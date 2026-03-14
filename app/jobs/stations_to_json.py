import requests
import json
from app.config import Config

url = f"{Config.AQICN_BASE_URL}/search/"
params = {
    "token": Config.TOKEN,
    "keyword": "Kraków"
}

response = requests.get(url, params=params).json()

stations = [
    {
        "id": s["uid"],
        "name": s["station"]["name"]
    }
    for s in response["data"]
]

with open("stations.json", "w", encoding="utf-8") as f:
    json.dump(stations, f, indent=4, ensure_ascii=False)