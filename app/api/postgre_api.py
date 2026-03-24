from fastapi import APIRouter
from app.db.db import SessionDependency
from app.db.models import stations_model, measurements_model
from app.db.models import stations, measurements
from fastapi import HTTPException

router = APIRouter()

#will work on this file next

@router.get("/stations/{station_id}")
async def get_station(station_id: int, db: SessionDependency):
    station = db.query(stations).filter(stations.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return stations_model.model_validate(station)


@router.post("/stations", response_model=stations_model, status_code=201)
async def create_station(payload: stations_model, db: SessionDependency):
    existing_station = db.query(stations).filter(stations.name == payload.name).first()
    if existing_station:
        raise HTTPException(status_code=409, detail="Station with this name already exists")

    new_station = stations( #converts pydantic model int o sqlalchemy model
        name=payload.name,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    db.add(new_station)
    db.commit()
    db.refresh(new_station)
    return new_station

@router.get("/measurements/{station_id}", response_model=list[measurements_model])
async def get_measurements(station_id: int, db: SessionDependency):
    measurements = db.query(measurements).filter(measurements.station_id == station_id).all()
    return [measurements_model.model_validate(m) for m in measurements]

@router.post("/measurements", response_model=measurements_model, status_code=201)
async def create_measurement(payload: measurements_model, db: SessionDependency):
    existing_measurement = db.query(measurements).filter(measurements.station_id == payload.station_id, measurements.timestamp == payload.timestamp).first()
    if existing_measurement:
        raise HTTPException(status_code=409, detail="Measurement with this station_id and timestamp already exists")

    new_measurement = measurements( #same conversion here
        station_id=payload.station_id,
        timestamp=payload.timestamp,
        pm10=payload.pm10,
        pm25=payload.pm25,
        co=payload.co,
        aqi=payload.aqi,
    )
    db.add(new_measurement)
    db.commit()
    db.refresh(new_measurement)
    return new_measurement