from app.services.airly_service import save_all_data_stations_24h
import asyncio
import datetime

if __name__ == "__main__":
    with open("app/jobs/save_all_data_all_stations.log", "a") as f:
        f.write(f"Starting save all data all stations at {datetime.now()}\n")
    try:
        asyncio.run(save_all_data_stations_24h())
        with open("app/jobs/save_all_data_all_stations.log", "a") as f:
            f.write(f"All data saved successfully at {datetime.now()}\n")
    except Exception as e:
        with open("app/jobs/save_all_data_all_stations.log", "a") as f:
            f.write(f"Error saving data: {e}\n")
        print(f"Error saving data: {e}")