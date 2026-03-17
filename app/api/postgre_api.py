from fastapi import APIRouter
from app.db.db import get_db, SessionDependency
from app.db.models import stations_model, measurements_model
from app.db.models import stations, measurements
from fastapi import Depends
from fastapi import HTTPException

postgre_api = APIRouter()

#will work on this file next

@postgre_api.get("/stations/{station_id}")
async def get_station(station_id: int, db: SessionDependency = Depends(get_db)):
    station = db.query(stations).filter(stations.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return stations_model.model_validate(station) 
