from fastapi import APIRouter
from app.db.db import SessionDependency
from app.db.models import stations_model, measurements_model
from app.db.models import stations, measurements
from fastapi import HTTPException
from typing import List
from datetime import datetime
from datetime import timedelta
from app.db.models import measurements
from fastapi.responses import FileResponse
from pathlib import Path
import csv

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
    existing_station = db.query(stations).filter(stations.station_id == payload.station_id).first()
    if existing_station:
        raise HTTPException(status_code=409, detail="Station with this station_id already exists")

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
##### IMPORTANT: ENDPOINT PATH CHANGED
@router.get("/measurements/history/days/{station_id}/{days}", response_model=list[measurements_model])
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

@router.get("/measurements/history/hours/{station_id}/{hours}", response_model=list[measurements_model])
async def get_measurements_history_hours(station_id: int, hours: int, db: SessionDependency):
    date = datetime.now() - timedelta(hours=hours)

    measurement_rows = (
        db.query(measurements)
        .filter(
            measurements.station_id == station_id,
            measurements.timestamp >= date
        )
        .all()
    )

    return [measurements_model.model_validate(m) for m in measurement_rows]

@router.get("/measurements/last/{station_id}", response_model=measurements_model)
async def get_last_measurement(station_id: int, db: SessionDependency):
    measurement = db.query(measurements).filter(measurements.station_id == station_id).order_by(measurements.timestamp.desc()).first()
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    return measurements_model.model_validate(measurement)

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
            continue
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


@router.get("/measurements/last24h/{station_id}/csv")
async def export_measurements_last24h_csv(station_id: int, db: SessionDependency):
    cutoff = datetime.now() - timedelta(hours=24)

    station = db.query(stations).filter(stations.station_id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    measurement_rows = (
        db.query(measurements)
        .filter(
            measurements.station_id == station_id,
            measurements.timestamp >= cutoff,
        )
        .order_by(measurements.timestamp.asc())
        .all()
    )

    if not measurement_rows:
        raise HTTPException(status_code=404, detail="No measurements found in last 24h")

    base_dir = Path(__file__).resolve().parent.parent.parent
    export_dir = base_dir / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"measurements_{station_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    file_path = export_dir / file_name

    fieldnames = [
        "station_id",
        "timestamp",
        "pm1",
        "pm25",
        "pm10",
        "temperature",
        "humidity",
        "pressure",
        "co",
        "o3",
        "so2",
        "no2",
        "no",
        "caqi",
    ]

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for m in measurement_rows:
            writer.writerow(
                {
                    "station_id": m.station_id,
                    "timestamp": m.timestamp.isoformat() if m.timestamp else None,
                    "pm1": m.pm1,
                    "pm25": m.pm25,
                    "pm10": m.pm10,
                    "temperature": m.temperature,
                    "humidity": m.humidity,
                    "pressure": m.pressure,
                    "co": m.co,
                    "o3": m.o3,
                    "so2": m.so2,
                    "no2": m.no2,
                    "no": m.no,
                    "caqi": m.caqi,
                }
            )

    return FileResponse(path=str(file_path), media_type="text/csv", filename=file_name)
