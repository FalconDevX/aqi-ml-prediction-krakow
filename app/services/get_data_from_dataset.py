import os
from tarfile import data_filter
import kagglehub
import pandas as pd
from pathlib import Path

from pandas.core.indexing import pd_array

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_FROM_KAGGLE_FOLDER = BASE_DIR / "data_from_kaggle"

def download_data_from_dataset():
    # temp directory under current working di
    if not DATA_FROM_KAGGLE_FOLDER.exists():
        DATA_FROM_KAGGLE_FOLDER.mkdir(parents=True, exist_ok=True)
    os.environ["KAGGLEHUB_CACHE"] = str(DATA_FROM_KAGGLE_FOLDER)
    path = kagglehub.dataset_download(
        "wisekinder/poland-air-quality-monitoring-dataset-2017-2023"
    )
    return path

def extract_data_from_dataset(year:int, param:str):
    #im sure theres better way to mark the path but i dontthink its important now
    station = "MpKrakBujaka"
    if param == "CO":
        station = "MpKrakBulwar" #exception for CO there is no CO sensor on Bujaka
    data = pd.read_csv(DATA_FROM_KAGGLE_FOLDER/f"datasets/wisekinder/poland-air-quality-monitoring-dataset-2017-2023/versions/14/{year}/{year}_{param}_1g.csv")
    if param == "PM25": #only for this one it is fuking different
        param = "PM2.5"
        station = "MpKrakBulwar"
    data = data[["Time",f"{station}-{param}-1g"]]
    #print(data.head())
    return data

def extract_all_data_from_dataset():
    years = [2017, 2018, 2019, 2020, 2021, 2022, 2023]
    data = pd.DataFrame()
    params = ["SO2", "NO2", "CO", "O3", "PM10", "PM25"]
    for year in years:
        for param in params:
            os.makedirs(f"data/{year}", exist_ok=True)
            data = extract_data_from_dataset(year, param)
            data.to_csv(f"data/{year}/{year}_{param}.csv", index=False)
            #return data

#path = download_data_from_dataset()
#print(path)
extract_all_data_from_dataset()