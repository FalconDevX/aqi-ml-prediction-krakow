import os
from dotenv import load_dotenv
from configparser import ConfigParser

load_dotenv()

class Config:
    TOKEN = os.getenv("TOKEN")
    AQICN_BASE_URL = "https://api.waqi.info"
    GIOS_METADATA_STATIONS = "https://api.gios.gov.pl/pjp-api/v1/rest/metadata/stations"
    AIRLY_API_KEY = os.getenv("AIRLY_API_KEY")
    AIRLY_NEAREST_INSTALLATIONS = "https://airapi.airly.eu/v2/installations/nearest"
    AIRLY_MEASURMENTS_LOCATION = "https://airapi.airly.eu/v2/measurements/location"


    DATABASE_URL = os.getenv("DATABASE_URL")

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    @classmethod
    def get_database_url(cls):
        if cls.DATABASE_URL:
            return cls.DATABASE_URL
        return (
            f"postgresql+psycopg2://{cls.DB_USER}:"
            f"{cls.DB_PASSWORD}@{cls.DB_HOST}:"
            f"{cls.DB_PORT}/{cls.DB_NAME}"
        )

def config(filename='./app/database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    db = {}

    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in {filename}')

    return db
