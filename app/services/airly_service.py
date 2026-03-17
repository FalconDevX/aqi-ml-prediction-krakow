from operator import ge
import requests
from app.config import Config
from app.utils import save_file_to_local_dir
import json
import httpx
import asyncio


headers = {"apikey": Config.AIRLY_API_KEY}

async def get_current_data_from_station(station_id: int):
    """
    Get data and time from a given station based on its id
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            Config.AIRLY_MEASURMENTS_LOCATION,
            headers=headers,
            params={
                "indexType": "AIRLY_CAQI",
                "locationId": station_id,
                "standardType": "WHO"
            }
        )

    response.raise_for_status()
    response = response.json()

    station_data = {}

    for air_index in response["current"]["values"]:
        station_data[air_index["name"]] = air_index["value"]

    station_data["CAQI"] = response["current"]["indexes"]

    return station_data

async def get_current_caqi_hex_color(station_id: int):
    """
    Get the hex color code for a given CAQI value
    """

    async with httpx.AsyncClient() as client:
        response = await client.get(
            Config.AIRLY_MEASURMENTS_LOCATION,
            headers=headers,
            params={
                "indexType": "AIRLY_CAQI",
                "locationId": station_id,
                "standardType": "WHO"
            }
        )

    response.raise_for_status()
    response = response.json()

    color = response["current"]["indexes"][0]["color"]

    return color

color = asyncio.run(get_current_caqi_hex_color(17))
print(color)