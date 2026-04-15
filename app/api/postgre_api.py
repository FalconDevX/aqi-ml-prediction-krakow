from fastapi import APIRouter
from app.db.db import SessionDependency
from app.db.models import stations_model, measurements_model
from app.db.models import stations, measurements
from fastapi import HTTPException
from typing import List
from datetime import datetime
from datetime import timedelta
from app.db.models import measurements

router = APIRouter()

#will work on this file next

@router.get("/stations/{station_id}")
async def get_station(station_id: int, db: SessionDependency):
    station = db.query(stations).filter(stations.station_id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return stations_model.model_validate(station)


@router.post("/stations", response_model=stations_model, status_code=201)
async def create_station(payload: stations_model, db: SessionDependency):
    existing_station = db.query(stations).filter(stations.name == payload.name).first()
    if existing_station:
        raise HTTPException(status_code=409, detail="Station with this name already exists")

    new_station = stations( #converts pydantic model int o sqlalchemy model
        station_id=payload.station_id,
        name=payload.name,
    )
    db.add(new_station)
    db.commit()
    db.refresh(new_station)
    return new_station

########################################################

@router.get("/measurements/{station_id}", response_model=list[measurements_model])
async def get_measurements(station_id: int, db: SessionDependency):
    measurement_rows = (
        db.query(measurements)
        .filter(measurements.station_id == station_id)
        .all()
    )
    return [measurements_model.model_validate(m) for m in measurement_rows]

#get mesurements by date back to history np. 10, 20 last days
@router.get("/measurements/history/{station_id}/{days}", response_model=list[measurements_model])
async def get_measurements_history(station_id: int, days: int, db: SessionDependency):
    date = datetime.now() - timedelta(days=days)

    measurement_rows = (
        db.query(measurements)
        .filter(
            measurements.station_id == station_id,
            measurements.timestamp >= date
        )
        .all()
    )

    return [measurements_model.model_validate(m) for m in measurement_rows]

@router.post("/measurements", response_model=measurements_model, status_code=201)
async def create_measurement(payload: measurements_model, db: SessionDependency):
    existing_measurement = db.query(measurements).filter(measurements.station_id == payload.station_id, measurements.timestamp == payload.timestamp).first()
    if existing_measurement:
        raise HTTPException(status_code=409, detail="Measurement with this station_id and timestamp already exists")

    new_measurement = measurements( #same conversion here
        station_id=payload.station_id,
        timestamp=payload.timestamp,
        pm1=payload.pm1,
        pm10=payload.pm10,
        pm25=payload.pm25,
        no2=payload.no2,
        no=payload.no,
        co=payload.co,
        o3=payload.o3,
        so2=payload.so2,
        caqi=payload.caqi,
    )
    db.add(new_measurement)
    db.commit()
    db.refresh(new_measurement)
    return new_measurement

@router.post("/measurements/bulk", response_model=List[measurements_model], status_code=201)
async def create_measurements(payload: List[measurements_model], db: SessionDependency):
    created = []
    for item in payload:
        exists = (
            db.query(measurements)
            .filter(
                measurements.station_id == item.station_id,
                measurements.timestamp == item.timestamp,
            )
            .first()
        )
        if exists:
            raise HTTPException(
                status_code=409,
                detail=f"Duplicate measurement for station_id={item.station_id}, timestamp={item.timestamp}",
            )
        obj = measurements(
            station_id=item.station_id,
            timestamp=item.timestamp,
            pm1=item.pm1,
            pm10=item.pm10,
            pm25=item.pm25,
            no2=item.no2,
            no=item.no,
            co=item.co,
            o3=item.o3,
            so2=item.so2,
            caqi=item.caqi,
        )
        db.add(obj)
        created.append(obj)
    db.commit()
    for obj in created:
        db.refresh(obj)
    return created
