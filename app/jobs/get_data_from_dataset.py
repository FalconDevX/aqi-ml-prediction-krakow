import os
from pathlib import Path

try:
    import kagglehub
    import pandas as pd
except ImportError as e:
    raise SystemExit(
        "This job needs optional deps: pip install kagglehub pandas"
    ) from e

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_FROM_KAGGLE_FOLDER = BASE_DIR / "data_from_kaggle"

def download_data_from_dataset():
    if not DATA_FROM_KAGGLE_FOLDER.exists():
        DATA_FROM_KAGGLE_FOLDER.mkdir(parents=True, exist_ok=True)
    os.environ["KAGGLEHUB_CACHE"] = str(DATA_FROM_KAGGLE_FOLDER)
    path = kagglehub.dataset_download(
        "wisekinder/poland-air-quality-monitoring-dataset-2017-2023"
    )
    print("REAL PATH:", path)
    return path

def extract_data_from_dataset(base_path: str | Path, year: int, param: str) -> pd.DataFrame:
    station = "MpKrakBujaka"
    if param == "CO":
        station = "MpKrakBulwar"  # exception for CO: no CO sensor on Bujaka

    file_path = Path(base_path) / f"{year}/{year}_{param}_1g.csv"
    print("TRYING:", file_path)
    data = pd.read_csv(file_path)

    if param == "PM25":
        param = "PM2.5"
        station = "MpKrakBulwar"

    data = data[["Time", f"{station}-{param}-1g"]]
    return data

def extract_all_data_from_dataset():
    base_path = download_data_from_dataset()
    years = [2017, 2018, 2019, 2020, 2021, 2022, 2023]
    params = ["SO2", "NO2", "CO", "O3", "PM10", "PM25"]
    for year in years:
        for param in params:
            os.makedirs(f"data/{year}", exist_ok=True)
            data = extract_data_from_dataset(base_path, year, param)
            data.to_csv(f"data/{year}/{year}_{param}.csv", index=False)


if __name__ == "__main__":
    extract_all_data_from_dataset()