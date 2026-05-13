from fastapi import APIRouter, HTTPException
from app.api.postgre_api import get_measurements_history_hours
from app.db.db import SessionDependency
from app.db.models import measurements_model
from pathlib import Path
from datetime import timedelta

router = APIRouter()

HISTORY_HOURS = 48
PREDICTION_HOURS = 10


async def get_data_from_API(station_id: int, hours: int, db: SessionDependency):
    data = await get_measurements_history_hours(station_id, hours, db)
    return data


async def model_prediction(model_path: str, target_param: str, station_id: int, db: SessionDependency):
    import joblib
    import numpy as np
    import pandas as pd

    model_file = Path(model_path)
    if not model_file.exists():
        raise HTTPException(status_code=404, detail=f"Model '{model_path}' not found")

    model = joblib.load(model_file)

    data = await get_data_from_API(station_id, HISTORY_HOURS, db)

    attr_name = target_param.lower()
    data = [m for m in data if getattr(m, attr_name, None) is not None]
    data.sort(key=lambda m: m.timestamp)

    if len(data) < HISTORY_HOURS:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough data: need {HISTORY_HOURS} records, got {len(data)}",
        )

    history = [getattr(m, attr_name) for m in data[-HISTORY_HOURS:]]
    last_timestamp = data[-1].timestamp

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