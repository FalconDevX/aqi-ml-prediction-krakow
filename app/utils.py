import json
from pathlib import Path


def save_file_to_local_dir(data, caller_file, filename):
    """
    Save data to a local file

    Args:
        data: data to save
        caller_file: file where the function is called
        filename: name of the file to save
    """
    curr_dir = Path(caller_file).parent

    file_path = curr_dir / str(filename)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_all_stations_ids():
    """
    Returns list of all stations ids
    """
    stations_ids = []

    with open("data/all_airly_stations.json", "r", encoding="utf-8") as f:
        stations = json.load(f)

    for station in stations:
        stations_ids.append(station["id"])

    return stations_ids
