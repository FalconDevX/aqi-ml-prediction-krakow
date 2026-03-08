from fastapi import APIRouter
from app.services.gios_service import get_stations

router = APIRouter()

@router.get("/gios/stations", tags=["gios"])
async def get_gios_stations():
    return get_stations()