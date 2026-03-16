from concurrent.futures import ThreadPoolExecutor
from gios_aqi_downloader import save_filtered_pages

years = [2020]

aqi_params = ["PM10", "PM2.5", "SO2", "NO2", "CO", "O3", ]

def download_year(year, param):
    # print(f"Downloading {param} for {year}...")
    save_filtered_pages(year, param)

def download_all():
    tasks = [(year, param) for param in aqi_params for year in years]

    with ThreadPoolExecutor(max_workers=16) as executor:
        executor.map(lambda x: download_year(*x), tasks)

download_all()



