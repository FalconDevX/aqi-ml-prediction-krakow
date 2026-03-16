import requests
from urllib3 import request, response
from app.config import Config
from app.utils import save_file_to_local_dir
import json

headers = {"apikey": Config.AIRLY_API_KEY}

def get_current_data_from_station(station_id: int):
    """
    Get data and time from a given station based on its id
    """
    response = requests.get(
        Config.AIRLY_MEASURMENTS_LOCATION,
        headers = headers,
        params = {
            "indexType": "AIRLY_CAQI",
            "locationId": station_id,
            "standardType": "WHO"
        }
    ).json()

    file_path = save_file_to_local_dir(__file__, "station_data.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(response, f, indent=4, ensure_ascii=False)
