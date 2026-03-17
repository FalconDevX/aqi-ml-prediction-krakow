import requests
import json
from app.config import Config
from app.utils import save_file_to_local_dir
import httpx

def get_all_stations():
    response = requests.get(
        Config.AIRLY_NEAREST_INSTALLATIONS,
        headers={"apikey": Config.AIRLY_API_KEY},
        params={
            "lat": 50.049683,
            "lng": 19.944544,
            "maxDistanceKM": 50,
            "maxResults": 1000
        }
    )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise Exception(f"Too many requests: {e.response.status_code}")
            
    data = response.json()
    

    stations = [
        {
            "id": station["locationId"],
            "name": station["address"]["displayAddress2"],
            "lat": station["location"]["latitude"],
            "long": station["location"]["longitude"]
        }
        for station in data
        if station["address"]["city"] == "Kraków"
    ]

    for station in stations:
        if station["name"] is None:
            station["name"] = "Kraków"

    file_path = save_file_to_local_dir(__file__, "all_airly_stations.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(stations, f, indent=4, ensure_ascii=False)

#get_all_stations()