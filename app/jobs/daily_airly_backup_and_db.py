"""
Codzienny job: Airly (24h) -> plik JSON w Data_Backup -> zapis do bazy.

Uruchamianie co 24h na serwerze (przykład crona, z katalogu projektu):
    0 3 * * * cd /sciezka/do/aqi-ml-prediction-krakow && /sciezka/do/venv/bin/python -m app.jobs.daily_airly_backup_and_db
"""
import asyncio
from datetime import datetime
from pathlib import Path

from app.services.airly_to_db import daily_airly_backup_json_and_db

LOG_PATH = Path(__file__).resolve().parent / "daily_airly_backup_and_db.log"


if __name__ == "__main__":
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"START {datetime.now()}\n")
    try:
        backup_path = asyncio.run(daily_airly_backup_json_and_db())
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"OK {datetime.now()} backup={backup_path}\n")
    except Exception as e:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"ERROR {datetime.now()} {e!r}\n")
        print(f"Error: {e}")
        raise
