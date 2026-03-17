from fastapi import APIRouter
from app.services.airly_service import get_current_data_from_station

router = APIRouter()

@router.get("/current/{station_id}")
async def get_curr_station_data(station_id: int):
    return await get_current_data_from_station(station_id)

# @router.get("/current/color/{station_id}")
# async def get_curr_caqi_hex_color(station_id: int):
#     return await get_current_caqi_hex_color(station_id)