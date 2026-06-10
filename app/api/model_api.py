from fastapi import APIRouter, HTTPException
from app.api.postgre_api import get_measurements_history_hours
from app.db.db import SessionDependency
from pathlib import Path
from datetime import datetime, timedelta

router = APIRouter()

HISTORY_HOURS = 24
PREDICTION_HOURS = 65
DATA_FETCH_HOURS = HISTORY_HOURS + 24
MAX_INTERPOLATION_GAP_HOURS = 3
MAX_MISSING_RATIO = 0.2


async def get_data_from_API(station_id: int, hours: int, db: SessionDependency):
    data = await get_measurements_history_hours(station_id, hours, db)
    return data


def _prepare_hourly_history(measurements, attr_name: str, hours: int) -> tuple[list[float], datetime]:
    import pandas as pd

    points = [
        (m.timestamp, getattr(m, attr_name))
        for m in measurements
        if getattr(m, attr_name, None) is not None
    ]
    if not points:
        raise HTTPException(
            status_code=400,
            detail=f"No data available for parameter '{attr_name.upper()}'",
        )

    points.sort(key=lambda x: x[0])
    last_timestamp = points[-1][0]
    full_range = pd.date_range(end=last_timestamp, periods=hours, freq="1h")

    series = pd.Series({ts: value for ts, value in points})
    series = series[~series.index.duplicated(keep="last")].sort_index()
    series = series.reindex(full_range)

    missing_count = int(series.isna().sum())
    if missing_count / hours > MAX_MISSING_RATIO:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Too many gaps in measurement data: {missing_count} of {hours} hours missing "
                f"({missing_count / hours:.0%}). Prediction requires more complete hourly data."
            ),
        )

    interpolated = series.interpolate(method="time", limit=MAX_INTERPOLATION_GAP_HOURS)
    remaining = int(interpolated.isna().sum())
    if remaining > 0:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Gaps too long to interpolate: {remaining} hour(s) still missing "
                f"(max gap fill is {MAX_INTERPOLATION_GAP_HOURS}h). Prediction unavailable."
            ),
        )

    return interpolated.tolist(), last_timestamp


async def model_prediction(model_path: str, target_param: str, station_id: int, db: SessionDependency):
    import joblib
    import numpy as np
    import pandas as pd

    model_file = Path(model_path)
    if not model_file.exists():
        raise HTTPException(status_code=404, detail=f"Model '{model_path}' not found")

    model = joblib.load(model_file)

    data = await get_data_from_API(station_id, DATA_FETCH_HOURS, db)
    attr_name = target_param.lower()
    history, last_timestamp = _prepare_hourly_history(data, attr_name, HISTORY_HOURS)

    predictions = []
    for step in range(PREDICTION_HOURS):
        target_time = last_timestamp + timedelta(hours=step + 1)
        hour = target_time.hour
        month = target_time.month

        input_data = pd.DataFrame([{
            'hour': hour,
            'dayofweek': target_time.weekday(),
            'month': month,
            'dayofyear': target_time.timetuple().tm_yday,
            'hour_sin': np.sin(2 * np.pi * hour / 24),
            'hour_cos': np.cos(2 * np.pi * hour / 24),
            'month_sin': np.sin(2 * np.pi * month / 12),
            'month_cos': np.cos(2 * np.pi * month / 12),
            f'{target_param}_lag_1': history[-1],
            f'{target_param}_lag_2': history[-2],
            f'{target_param}_lag_3': history[-3],
            f'{target_param}_lag_24': history[-24],
            f'{target_param}_lag_48': history[-48],
        }])

        prediction = model.predict(input_data)[0]
        history.append(prediction)

        predictions.append({
            "timestamp": target_time.isoformat(),
            f"{target_param}": round(float(prediction), 2),
        })

    return predictions


@router.get("/prediction/{target_param}/{station_id}")
async def get_model_prediction(target_param: str, station_id: int, db: SessionDependency):
    target_param = target_param.upper()
    return await model_prediction(f"models/{target_param}_model.joblib", target_param, station_id, db)