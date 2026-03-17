from operator import ge
import requests
from app.config import Config
from app.utils import save_file_to_local_dir
import json
import httpx
import asyncio
from fastapi import HTTPException
from app.exceptions import ExternalAPIError

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
                    "standardType": "WHO"
                }
            )
            response.raise_for_status()

        except httpx.HTTPStatusError as e:
            raise ExternalAPIError(
                message=e.response.json()["message"],
                status_code=e.response.status_code,
                url=str(e.request.url)
            )
        
        except httpx.RequestError as e:
            raise ExternalAPIError(
                message="Network error while contacting Airly API",
                status_code=503,
                url=str(e.request.url)
            )

    try:
        data = response.json()
    except Exception:
        raise ExternalAPIError(
            message="Invalid JSON response from Airly API",
            status_code=502,
            url=Config.AIRLY_MEASURMENTS_LOCATION
        )

    if "current" not in data:
        raise ExternalAPIError(
            message="Incorrect Airly response",
            status_code=502,
            url=Config.AIRLY_MEASURMENTS_LOCATION
        )

    station_data = {}

    for air_index in data["current"].get("values", []):
        station_data[air_index["name"]] = air_index["value"]

    station_data["CAQI"] = data["current"].get("indexes", [])

    return station_data

# async def get_current_caqi_hex_color(station_id: int):
#     """
#     Get the hex color code for a given CAQI value
#     """

#     async with httpx.AsyncClient() as client:
#         response = await client.get(
#             Config.AIRLY_MEASURMENTS_LOCATION,
#             headers=headers,
#             params={
#                 "indexType": "AIRLY_CAQI",
#                 "locationId": station_id,
#                 "standardType": "WHO"
#             }
#         )

#     response.raise_for_status()
#     response = response.json()

#     color = response["current"]["indexes"][0]["color"]

#     return color
