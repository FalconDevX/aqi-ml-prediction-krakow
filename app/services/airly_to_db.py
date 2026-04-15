from app.services.airly_service import save_all_data_stations_24h
from app.config import Config
from app.db.models import measurements_model
import json
import asyncio
import httpx

async def map_airly_results_to_db_models():
    stations_results = await save_all_data_stations_24h()
    curr_station_id = None
    measurements = [] 
    for station_result in stations_results:
        if isinstance(station_result, Exception):
            continue

        station_curr, station_history = station_result
        curr_station_id = station_curr["stationId"]


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
    return measurements

async def save_measurements_to_db():
    URL = Config.POSTGRE_API_URL + "/measurements/bulk"
    measurements = await map_airly_results_to_db_models()
    payload = [m.model_dump(mode="json") for m in measurements]
    async with httpx.AsyncClient() as client:
        response = await client.post(URL, json=payload)
        response.raise_for_status()
    print(response.json())

asyncio.run(save_measurements_to_db())