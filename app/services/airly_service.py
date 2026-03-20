from operator import ge
import requests
from app.config import Config
from app.utils import save_file_to_local_dir, get_all_stations_ids
import json
import httpx
import asyncio
from fastapi import HTTPException
from app.exceptions import ExternalAPIError
import asyncio
import jsonlines

headers = {"apikey": Config.AIRLY_API_KEY}


async def get_current_data_from_station(station_id: int):
    """
    Get data and time from a given station based on its id
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                Config.AIRLY_MEASURMENTS_LOCATION,
                headers=headers,
                params={
                    "indexType": "AIRLY_CAQI",
                    "locationId": station_id,
                    "standardType": "WHO",
                },
            )
            response.raise_for_status()

        except httpx.HTTPStatusError as e:
            raise ExternalAPIError(
                message=e.response.json()["message"],
                status_code=e.response.status_code,
                url=str(e.request.url),
            )

        except httpx.RequestError as e:
            raise ExternalAPIError(
                message="Network error while contacting Airly API",
                status_code=503,
                url=str(e.request.url),
            )

    try:
        data = response.json()
    except Exception:
        raise ExternalAPIError(
            message="Invalid JSON response from Airly API",
            status_code=502,
            url=Config.AIRLY_MEASURMENTS_LOCATION,
        )

    if "current" not in data:
        raise ExternalAPIError(
            message="Incorrect Airly response",
            status_code=502,
            url=Config.AIRLY_MEASURMENTS_LOCATION,
        )

    station_data = {}

    for air_index in data["current"].get("values", []):
        station_data[air_index["name"]] = air_index["value"]

    station_data["CAQI"] = data["current"].get("indexes", [])

    return station_data


def filter_current_stations(response):
    stations_current_data = []
    current = response["current"]
    filtered_current = {k: v for k, v in current.items() if k != "standards"}
    stations_current_data.append(filtered_current)


def get_all_data_stations_24h():
    stations_ids = get_all_stations_ids()

    stations_data = []
    stations_current_data = []
    station_history_data = []

    # gather raw stations data
    with jsonlines.open("all_stations_data.jsonl", mode="w") as file:
        for id in stations_ids:
            response = asyncio.run(get_current_data_from_station(id))
            stations_data.append(response)
            file.write(response)

    # filter stations
    for station_curr in stations_data:
        stations_current_data.append(filter_current_stations(station_curr))
