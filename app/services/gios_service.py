import requests
import json

GIOS_GET_STATIONS_URL = "https://api.gios.gov.pl/pjp-api/v1/rest/metadata/stations"

def get_stations():
    params = {
        "page": 0,
        "size": 500,
        "filter[miejscowosc]": "Kraków"
    }

    response = requests.get(GIOS_GET_STATIONS_URL, params=params)
    data = response.json()

    stations = []
    with open("stations.json", "w", encoding="utf-8") as f:
        for station in data["Lista metadanych stacji pomiarowych"]:
            station_data = {
                "Nr": station["Nr"],
                "Kod stacji": station["Kod stacji"],
                "Nazwa stacji": station["Nazwa stacji"],
                "Adres": station["Adres"],
                "WGS84 φ N": station["WGS84 φ N"],
                "WGS84 λ E": station["WGS84 λ E"]
            }
            stations.append(station_data)
        
        json.dump(stations, f, indent=4, ensure_ascii=False)

    return data

get_stations()