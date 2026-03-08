from fastapi import APIRouter, FastAPI
from app.services.gios_service import get_stations

app = FastAPI()
router = APIRouter()


@router.get("/gios/stations", tags=["gios"])
async def get_gios_stations():
    return get_stations()

app.include_router(router)