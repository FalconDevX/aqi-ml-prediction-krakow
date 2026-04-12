import json
from pathlib import Path

# Repo root (app/utils.py -> app -> project root); works regardless of CWD (cron, IDE, etc.)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def save_file_to_local_dir(data, caller_file, filename):
    """
    Save data to a local file under project ``data/``.

    Args:
        data: data to save
        caller_file: kept for call-site compatibility (path does not depend on it)
        filename: name of the file to save
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DATA_DIR / str(filename)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_all_stations_ids():
    """
    Returns list of all stations ids
    """
    stations_ids = []

    path = DATA_DIR / "all_airly_stations.json"
    with open(path, "r", encoding="utf-8") as f:
        stations = json.load(f)

    for station in stations:
        stations_ids.append(station["id"])

    return stations_ids
