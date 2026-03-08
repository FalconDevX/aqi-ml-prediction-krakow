from fastapi import FastAPI
from app.api.router import router
from app.services.gios_service import get_stations


app = FastAPI()

app.include_router(router)

