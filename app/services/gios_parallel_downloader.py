from concurrent.futures import ThreadPoolExecutor
from gios_aqi_downloader import save_filtered_pages

years = [2020, 2021, 2022, 2023, 2024, 2025, 2026]

def download_year(year):
    save_filtered_pages(year, "PM10")

with ThreadPoolExecutor(max_workers=8) as executor:
    executor.map(download_year, years)

