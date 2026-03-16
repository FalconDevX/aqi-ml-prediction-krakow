from fastapi import APIRouter
from app.services.airly_service import get_current_data_from_station

router = APIRouter()

@router.get("/get_curr_station_data")
def get_curr_station_data():
    return get_current_data_from_station()
