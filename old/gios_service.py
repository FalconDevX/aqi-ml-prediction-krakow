import requests
import json
import csv
from pathlib import Path

GIOS_GET_STATIONS_URL = "https://api.gios.gov.pl/pjp-api/v1/rest/metadata/stations"

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_FOLDER = BASE_DIR / "data"


def get_stations():
    params = {
        "page": 0,
        "size": 500,
        "filter[miejscowosc]": "Kraków",
    }

    response = requests.get(GIOS_GET_STATIONS_URL, params=params)
    data = response.json()

    DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    stations = []
    with open(DATA_FOLDER / "stations.json", "w", encoding="utf-8") as f:
        for station in data["Lista metadanych stacji pomiarowych"]:
            station_data = {
                "Nr": station["Nr"],
                "Kod stacji": station["Kod stacji"],
                "Nazwa stacji": station["Nazwa stacji"],
                "Adres": station["Adres"],
                "WGS84 φ N": station["WGS84 φ N"],
                "WGS84 λ E": station["WGS84 λ E"],
            }
            stations.append(station_data)

        json.dump(stations, f, indent=4, ensure_ascii=False)

    return stations


def save_stations_to_csv(stations):
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)
    with open(DATA_FOLDER / "stations.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["Nr", "Kod stacji", "Nazwa stacji", "Adres", "WGS84 φ N", "WGS84 λ E"]
        )
        for station in stations:
            writer.writerow(
                [
                    station["Nr"],
                    station["Kod stacji"],
                    station["Nazwa stacji"],
                    station["Adres"],
                    station["WGS84 φ N"],
                    station["WGS84 λ E"],
                ]
            )


get_stations()
save_stations_to_csv(get_stations())