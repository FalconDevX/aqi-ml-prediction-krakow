import requests
import json
import os

URL = "https://api.gios.gov.pl/pjp-api/v1/rest/archivalData/getDataForAllStationsByYearAndVoivodeship"

DATA_FOLDER = "../data"

years = [2020, 2021, 2022, 2023, 2024, 2025, 2026]

def get_aqi_param_gois(years, aqi_param):
    
    for year in years:
        save_pages(year, aqi_param)

def save_pages(year, aqi_param):
    """
    Saves all api pages for a given year and aqi parameter.
    """

    file_folder = f"{DATA_FOLDER}/{aqi_param}"

    all_pages = []
    
    params = {
        "page": 0,
        "size": 500,
        "year": str(year),
        "voivodeship": "MAŁOPOLSKIE",
        "pollution": str(aqi_param)
    }

    response = requests.get(URL, params=params)

    data = response.json()

    total_pages = data["totalPages"]

    for i in range(total_pages):
        all_pages.append(download_page(i, params))

    if not os.path.exists(file_folder):
        os.makedirs(file_folder)

    with open(f"{file_folder}/data_{year}.json", "w", encoding="utf-8") as f:
        json.dump(all_pages, f, indent=4, ensure_ascii=False)


def download_page(page, params):
    """
    Downloads a single page from the api.
    """
    p = params.copy()
    p["page"] = page

    response = requests.get(URL, params=p)
    data = response.json()
    
    data = data["Lista archiwalnych wyników pomiarów"]

    print(f"\033[92mSaving page {page}\033[0m")

    return data

save_pages(2020, "PM10")
