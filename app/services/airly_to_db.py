import json
import re
from datetime import datetime
from pathlib import Path

import httpx

from app.config import Config
from app.db.models import measurements_model
from app.services.airly_service import save_all_data_stations_24h

_DATA_BACKUP_DIR = Path(__file__).resolve().parent.parent.parent / "Data_Backup"
_BACKUP_FILENAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.json$")

_BULK_CHUNK_SIZE = 800
async def _post_measurements_bulk(url: str, payload: list[dict]) -> None:
    if not payload:
        return
    timeout = httpx.Timeout(connect=60.0, read=600.0, write=300.0, pool=60.0)
    n_chunks = (len(payload) + _BULK_CHUNK_SIZE - 1) // _BULK_CHUNK_SIZE
    created_total = 0
    async with httpx.AsyncClient(timeout=timeout) as client:
        for i in range(0, len(payload), _BULK_CHUNK_SIZE):
            chunk = payload[i : i + _BULK_CHUNK_SIZE]
            response = await client.post(url, json=chunk)
            response.raise_for_status()
            body = response.json()
            if isinstance(body, list):
                created_total += len(body)
    print(f"bulk: {created_total} records saved (new) in {n_chunks} requests, total {len(payload)} in payload")


def _latest_backup_json_in_data_backup() -> Path:
    directory = _DATA_BACKUP_DIR
    if not directory.is_dir():
        raise FileNotFoundError(f"No backup folder: {directory}")
    candidates = [
        p
        for p in directory.iterdir()
        if p.is_file() and _BACKUP_FILENAME_RE.match(p.name)
    ]
    if not candidates:
        raise FileNotFoundError(
            f"No backup files (*.json with name YYYY-MM-DD_HH-MM-SS.json) in {directory}"
        )
    return max(candidates, key=lambda p: p.name)


async def map_airly_results_to_db_models():
    stations_results = await save_all_data_stations_24h()
    measurements = []
    n_exceptions = 0
    n_ok_empty_history = 0
    for station_result in stations_results:
        if isinstance(station_result, Exception):
            n_exceptions += 1
            continue

        station_curr, station_history = station_result
        curr_station_id = station_curr["stationId"]
        if not station_history:
            n_ok_empty_history += 1
            continue

        for h in station_history:
            values = {v.get("name"): v.get("value") for v in (h.get("values") or []) if isinstance(v, dict)}
            indexes = {i.get("name"): i.get("value") for i in (h.get("indexes") or []) if isinstance(i, dict)}
            caqi_val = indexes.get("AIRLY_CAQI") or indexes.get("AIRLY")
            caqi_int = int(round(caqi_val)) if isinstance(caqi_val, (int, float)) else None
            temp_measurement = measurements_model(
                station_id=curr_station_id,
                timestamp=h["fromDateTime"],
                pm1=values.get("PM1"),
                pm25=values.get("PM25") or values.get("PM2.5"),
                pm10=values.get("PM10"),
                temperature=values.get("TEMPERATURE"),
                humidity=values.get("HUMIDITY"),
                pressure=values.get("PRESSURE"),
                co=values.get("CO"),
                o3=values.get("O3"),
                so2=values.get("SO2"),
                no2=values.get("NO2"),
                no=values.get("NO"),
                caqi=caqi_int,
            )
            measurements.append(temp_measurement)
    if not measurements:
        first_err = next((r for r in stations_results if isinstance(r, Exception)), None)
        raise ValueError(
            f"No measurements from Airly to map (stations in response: {len(stations_results)}, "
            f"errors: {n_exceptions}, stations with empty history: {n_ok_empty_history}). "
            f"First exception: {repr(first_err) if first_err else 'none'}. "
            "daily_airly_backup_json_and_db always fetches fresh data from API first — "
            "existing file in Data_Backup is not used in this step. "
            "To send only existing JSON to the database: save_measurements_from_json_to_db(path)."
        )
    return measurements


async def save_airly_measurements_to_json(file_path: str | Path | None = None) -> Path:
    measurements = await map_airly_results_to_db_models()
    if file_path is not None:
        path = Path(file_path)
    else:
        backup_dir = _DATA_BACKUP_DIR
        backup_dir.mkdir(parents=True, exist_ok=True)
        newest_ts: datetime = measurements[-1].timestamp
        name = newest_ts.strftime("%Y-%m-%d_%H-%M-%S") + ".json"
        path = backup_dir / name
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [m.model_dump(mode="json") for m in measurements]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


async def save_measurements_from_json_to_db(json_path: str | Path | None = None) -> None:
    path = Path(json_path) if json_path is not None else _latest_backup_json_in_data_backup()
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, list):
        raise ValueError("JSON must be a list of measurement objects")
    items = [measurements_model.model_validate(row) for row in raw]
    payload = [m.model_dump(mode="json") for m in items]
    URL = Config.POSTGRE_API_URL + "/measurements/bulk"
    await _post_measurements_bulk(URL, payload)


async def daily_airly_backup_json_and_db() -> Path:
    try:
        backup_path = await save_airly_measurements_to_json()
        print(f"New Backup: {backup_path}")
    except Exception as fetch_err:
        print(f"Fetching from Airly failed: {fetch_err}")
        backup_path = _latest_backup_json_in_data_backup()
        print(f"Using existing backup: {backup_path}")
    await save_measurements_from_json_to_db(backup_path)
    return backup_path


async def save_measurements_to_db():
    URL = Config.POSTGRE_API_URL + "/measurements/bulk"
    measurements = await map_airly_results_to_db_models()
    payload = [m.model_dump(mode="json") for m in measurements]
    await _post_measurements_bulk(URL, payload)


if __name__ == "__main__":
    import asyncio

    asyncio.run(save_measurements_from_json_to_db())