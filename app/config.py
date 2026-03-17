import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TOKEN = os.getenv("TOKEN")
    AQICN_BASE_URL = "https://api.waqi.info"
    GIOS_METADATA_STATIONS = "https://api.gios.gov.pl/pjp-api/v1/rest/metadata/stations"
    AIRLY_API_KEY = os.getenv("AIRLY_API_KEY")
    AIRLY_NEAREST_INSTALLATIONS = "https://airapi.airly.eu/v2/installations/nearest"
    AIRLY_MEASURMENTS_LOCATION = "https://airapi.airly.eu/v2/measurements/location"
    DATABASE_URL = os.getenv("DATABASE_URL")