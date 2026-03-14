import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TOKEN = os.getenv("TOKEN")
    AQICN_BASE_URL = "https://api.waqi.info"