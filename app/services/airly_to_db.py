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
    print(f"bulk: {created_total} rek. zapisanych (nowych) w {n_chunks} requestach, łącznie {len(payload)} w payloadzie")


def _latest_backup_json_in_data_backup() -> Path:
    directory = _DATA_BACKUP_DIR
    if not directory.is_dir():
        raise FileNotFoundError(f"Brak folderu kopii: {directory}")
    candidates = [
        p
        for p in directory.iterdir()
        if p.is_file() and _BACKUP_FILENAME_RE.match(p.name)
    ]
    if not candidates:
        raise FileNotFoundError(
            f"Brak plików kopii (*.json z nazwą YYYY-MM-DD_HH-MM-SS.json) w {directory}"
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
            f"Brak pomiarów z Airly do zmapowania (stacji w odpowiedzi: {len(stations_results)}, "
            f"błędów: {n_exceptions}, stacji z pustą historią: {n_ok_empty_history}). "
            f"Pierwszy wyjątek: {repr(first_err) if first_err else 'brak'}. "
            "daily_airly_backup_json_and_db zawsze najpierw pobiera świeże dane z API — "
            "istniejący plik w Data_Backup nie jest używany w tym kroku. "
            "Aby wysłać tylko istniejący JSON do bazy: save_measurements_from_json_to_db(ścieżka)."
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
        raise ValueError("JSON musi być listą obiektów pomiarów")
    items = [measurements_model.model_validate(row) for row in raw]
    payload = [m.model_dump(mode="json") for m in items]
    URL = Config.POSTGRE_API_URL + "/measurements/bulk"
    await _post_measurements_bulk(URL, payload)


async def daily_airly_backup_json_and_db() -> Path:
    backup_path = await save_airly_measurements_to_json()
    await save_measurements_from_json_to_db(backup_path)
    return backup_path


async def save_measurements_to_db():
    URL = Config.POSTGRE_API_URL + "/measurements/bulk"
    measurements = await map_airly_results_to_db_models()
    payload = [m.model_dump(mode="json") for m in measurements]
    await _post_measurements_bulk(URL, payload)


if __name__ == "__main__":
    import asyncio

    asyncio.run(daily_airly_backup_json_and_db())