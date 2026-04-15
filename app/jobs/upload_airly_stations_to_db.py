import json
import os
import httpx

def upload_airly_stations_to_db():
    with open("app/services/all_airly_stations.json", "r") as f:
        airly_stations = json.load(f)
        counter = 0
    for station in airly_stations:
        station_id = station["id"]
        name = station["name"]

        url = os.getenv("POSTGRE_API_URL")
        url = "http://localhost:8000/postgre" ## normally it shouldnt be like this but i want to add them once 
                                                ## manually and i cant run single file on uvicorn or somethin
        response = httpx.post(url + "/stations", json={"station_id": station_id, "name": name})
        if response.status_code == 201:
            print(f"Station {name} uploaded successfully")
            counter += 1
        else:
            print(f"Failed to upload station {name}")
    print(f"Uploaded {counter} stations")
upload_airly_stations_to_db()