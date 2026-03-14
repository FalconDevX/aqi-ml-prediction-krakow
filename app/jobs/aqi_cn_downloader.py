import requests
from app.config import Config


class AQICNClient:

    def get_station_feed(self, station_id: int):
        url = f"{Config.AQICN_BASE_URL}/feed/@{station_id}/"
        params = {
            "token": Config.TOKEN
        }

        response = requests.get(url, params=params)
        return response.json()


aqi_cn_client = AQICNClient()

print(aqi_cn_client.get_station_feed(450))