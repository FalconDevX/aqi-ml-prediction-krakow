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


async def get_current_and_history_data_from_station(station_id: int):
    """
    Get current and history raw data from a given station
    """
    async with httpx.AsyncClient() as client:
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

    data = response.json()

    # current
    curr = data["current"]

    curr_station_data = {
        "stationId": station_id,
        "fromDateTime": curr.get("fromDateTime"),
        "tillDateTime": curr.get("tillDateTime"),
        "values": curr.get("values"),
        "indexes": curr.get("indexes"),
    }

    # history

    history_station_data = []

    history_station_data.extend([
        {
            "fromDateTime": h["fromDateTime"],
            "tillDateTime": h["tillDateTime"],
            "values": h["values"],
            "indexes": h["indexes"],
        }
        for h in data["history"]
    ])

    return curr_station_data, history_station_data


async def save_all_data_stations_24h():
    """
    Save all current and history data from all stations for the last 24 hours to a file
    """

    stations_ids = get_all_stations_ids()

    # gather current and history data from all stations
    stations_data = await asyncio.gather(
        *[get_current_and_history_data_from_station(id) for id in stations_ids]
    )

    with jsonlines.open("stations_current_data.jsonl", mode="w") as file:
        for station_curr, _ in stations_data:
            print("Saving current data for station: ", station_curr["stationId"])
            file.write(station_curr)

    with jsonlines.open("stations_hisotry_data.jsonl", mode="w") as file:
        for station_curr, station_history in stations_data:
            print("Saving history data for station: ", station_curr["stationId"])
            file.write({
                "stationId": station_curr["stationId"],
                "history": station_history
            })
       
station_history_data = asyncio.run(save_all_data_stations_24h())
