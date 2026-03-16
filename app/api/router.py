from fastapi import APIRouter
from app.api.stations import router as stations_router

router = APIRouter()

router.include_router(stations_router, prefix="/stations", tags=["stations"])