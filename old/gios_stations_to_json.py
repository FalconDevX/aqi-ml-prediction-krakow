import requests
import json
from app.config import Config
from app.utils import save_file_to_local_dir

url = f"{Config.GIOS_METADATA_STATIONS}"
params = {
    "page":0,
    "size": 500,
    "filter[miejscowosc]": "Kraków"
}

response = requests.get(url, params=params).json()

stations = [
    {
        "id": station["Nr"],
        "station_id": station["Kod stacji"],
        "name": station["Nazwa stacji"]
    }
    for station in response["Lista metadanych stacji pomiarowych"] 
]

file_path = save_file_to_local_dir(__file__, "stations.json")

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(stations, f, indent=4, ensure_ascii=False)