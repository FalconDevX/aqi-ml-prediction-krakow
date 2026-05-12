from fastapi import APIRouter
from app.api.postgre_api import get_measurements_history_hours
from app.db.db import SessionDependency
from app.db.models import measurements_model
from pathlib import Path

router = APIRouter()

def get_data_from_API(station_id: int, hours: int, db: SessionDependency):
    data = get_measurements_history_hours(station_id, hours, db)
    return data

def model_prediction(model_path: str, target_param: str, station_id: int, db: SessionDependency):
    history_hours = 48
    predicted_hours = 10
    data = get_data_from_API(station_id, history_hours, db)
    #### MODEL LOGIC
    return predicted_measurements #list

@router.get("/prediction/{target_param}/{station_id}")
async def get_model_prediction(target_param: str, station_id: int, db: SessionDependency):
    return model_prediction(f"models/{target_param}_model.joblib", target_param, station_id, db)