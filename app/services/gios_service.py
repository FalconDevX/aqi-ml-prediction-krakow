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

    # with open("stations.json", "w", encoding="utf-8") as f:
    #     json.dump(data, f, indent=4, ensure_ascii=False)

    return data
get_stations()