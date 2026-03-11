import requests
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

session = requests.Session()

URL = "https://api.gios.gov.pl/pjp-api/v1/rest/archivalData/getDataForAllStationsByYearAndVoivodeship"

DATA_FOLDER = None

with open(f"./data/stations.json", "r", encoding="utf-8") as f:
    stations_list = json.load(f)

station_names = {s["Nazwa stacji"] for s in stations_list}
station_codes = {s["Kod stacji"] for s in stations_list}

def save_filtered_pages(year, aqi_param):
    """
    Saves all api pages for a given year and aqi parameter.
    """    

    global DATA_FOLDER
    DATA_FOLDER = f"./data/{aqi_param}"

    os.makedirs(DATA_FOLDER, exist_ok=True)

    file_path = f"{DATA_FOLDER}/all_pages.json"

    if os.path.exists(file_path):

        print("Loading cached pages...")

        with open(file_path, "r", encoding="utf-8") as f:
            all_pages = json.load(f)

    else:

        params = {
            "page": 0,
            "size": 500,
            "year": str(year),
            "voivodeship": "MAŁOPOLSKIE",
            "pollution": str(aqi_param)
        }

        response = session.get(URL, params=params)
        data = response.json()

        total_pages = data["totalPages"]

        results = {}

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(download_page, i, params): i
                for i in range(total_pages)
            }

            for future in as_completed(futures):
                page = futures[future]
                results[page] = future.result()

        all_pages = []

        for page in sorted(results):
            all_pages.extend(results[page])

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(all_pages, f)

    filter_stations(all_pages, year)

def download_page(page, params):
    """
    Downloads a single page from the API with retry logic.
    """

    p = params.copy()
    p["page"] = page

    for attempt in range(5):

        try:
            response = session.get(URL, params=p, timeout=30)

            response.raise_for_status()

            data = response.json()

            data = data["Lista archiwalnych wyników pomiarów"]

            print(f"\033[92mDownloaded page {page}\033[0m - year: {params['year']}, param: {params['pollution']}")

            return data

        except requests.exceptions.RequestException as e:

            print(f"\033[91mError page {page}, attempt {attempt}: {e}\033[0m")

            time.sleep(2)

    print(f"\033[91mFailed page {page}\033[0m")
    return []

def filter_stations(stations, year):
    """
    Filters stations by their code and save only from Krakow stations list
    """
    stations_to_save = []

    skipped_stations = set()

    curr_station_code = None

    for station in stations:
        if cut_String(station["Kod stanowiska"]) in station_codes:
            curr_station_code = station["Kod stanowiska"]
            break

    for station in stations:
        if cut_String(station["Kod stanowiska"]) in station_codes and station["Kod stanowiska"] == curr_station_code:
            stations_to_save.append(station) #adds a record, not just a station so its a lot of them
        elif cut_String(station["Kod stanowiska"]) in station_codes and station["Kod stanowiska"] != curr_station_code:
            save_filtered_stations(stations_to_save, curr_station_code, year)
            stations_to_save = [] #resets after saving all records to a dedicated station file
            curr_station_code = station["Kod stanowiska"] 
            stations_to_save.append(station)
        elif cut_String(station["Kod stanowiska"]) not in station_codes:
            #print(f"Station {station['Nazwa stacji']} not found in stations list") #debug purposes
            skipped_stations.add(station["Nazwa stacji"])

    print(f"Skipped stations: {skipped_stations}") #debug purposes

    save_filtered_stations(stations_to_save, curr_station_code, year)

    return stations_to_save

def cut_String(string):
    return string.split("-")[0]

def save_filtered_stations(filtered_stations, station_code, year):
    if not os.path.exists(f"{DATA_FOLDER}/{station_code}"):
        os.makedirs(f"{DATA_FOLDER}/{station_code}")

    with open(f"{DATA_FOLDER}/{station_code}/data_{year}.json", "w", encoding="utf-8") as f:
        json.dump(filtered_stations, f, indent=4, ensure_ascii=False)

save_filtered_pages(2024, "PM10")

# for year in years:
#     save_pages(year, "PM10")
