import asyncio
import jsonlines
from datetime import datetime
from pathlib import Path

import httpx

from app.config import Config
from app.exceptions import ExternalAPIError
from app.utils import get_all_stations_ids

headers = {"apikey": Config.AIRLY_API_KEY}

BASE_DIR = Path(__file__).resolve().parent.parent.parent / "stations_data"
BASE_DIR.mkdir(exist_ok=True)
(BASE_DIR / "current").mkdir(exist_ok=True)
(BASE_DIR / "history").mkdir(exist_ok=True)


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
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ExternalAPIError(
                message=f"API error for station {station_id}: {e!s}",
                status_code=e.response.status_code,
                url=str(e.request.url),
            ) from e

        data = response.json()

    curr = data["current"]

    curr_station_data = {
        "stationId": station_id,
        "fromDateTime": curr.get("fromDateTime"),
        "tillDateTime": curr.get("tillDateTime"),
        "values": curr.get("values"),
        "indexes": curr.get("indexes"),
    }

    history_station_data = [
        {
            "fromDateTime": h["fromDateTime"],
            "tillDateTime": h["tillDateTime"],
            "values": h["values"],
            "indexes": h["indexes"],
        }
        for h in data["history"]
    ]

    return curr_station_data, history_station_data


async def get_current_data_from_station(station_id: int):
    curr, _ = await get_current_and_history_data_from_station(station_id)
    return curr


async def save_all_data_stations_24h():
    """
    Save all current and history data from all stations for the last 24 hours to a file
    """
    stations_ids = get_all_stations_ids()

    stations_results = await asyncio.gather(
        *[get_current_and_history_data_from_station(id) for id in stations_ids],
        return_exceptions=True,
    )

    date_str = datetime.now().strftime("%Y-%m-%d-%H-%M")
    current_path = BASE_DIR /"current"/ f"{date_str}_stations_current_data.jsonl"
    history_path = BASE_DIR / "history" / f"{date_str}_stations_history_data.jsonl"

    with jsonlines.open(current_path, mode="w") as file:
        for item in stations_results:
            if isinstance(item, Exception):
                print("Skipping station due to error: ", item)
                continue
            station_curr, _ = item
            print("Saving current data for station: ", station_curr["stationId"])
            file.write(station_curr)

    with jsonlines.open(history_path, mode="w") as file:
        for item in stations_results:
            if isinstance(item, Exception):
                continue
            station_curr, station_history = item
            print("Saving history data for station: ", station_curr["stationId"])
            file.write(
                {
                    "stationId": station_curr["stationId"],
                    "history": station_history,
                }
            )

# if __name__ == "__main__":
#     asyncio.run(save_all_data_stations_24h())