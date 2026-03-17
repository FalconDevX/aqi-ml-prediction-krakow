from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from app.db.db import Base
from pydantic import BaseModel, ConfigDict
from datetime import datetime


# sqlalchemy models for our postgres database
class stations(Base):
    __tablename__ = "stations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)

class measurements(Base):
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True)
    station_id = Column(Integer, ForeignKey("stations.id"))
    timestamp = Column(DateTime)
    pm25 = Column(Float)
    pm10 = Column(Float)
    co = Column(Float)
    aqi = Column(Integer)


# pydantic models for data validation if we need it XD (and also guy in tutorial was using them)
class stations_model(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    latitude: float
    longitude: float

class measurements_model(BaseModel):
    model_config = ConfigDict(from_attributes=True) # some pydantic magic to convert the sqlalchemy model to a pydantic model
    
    id: int
    station_id: int
    timestamp: datetime
    pm25: float
    pm10: float
    co: float
    aqi: int