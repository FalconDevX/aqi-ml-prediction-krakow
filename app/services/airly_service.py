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

    save_file_to_local_dir(response, __file__, "station_data.json")
    return response

get_current_data_from_station(17)