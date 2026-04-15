from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from app.db.db import Base
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# sqlalchemy models for our postgres database
class stations(Base):
    __tablename__ = "stations"
    id = Column(Integer, primary_key=True)
    station_id = Column(Integer, unique=True, nullable=False)
    name = Column(String)

class measurements(Base):
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True)
    station_id = Column(Integer, ForeignKey("stations.station_id"), nullable=False)
    timestamp = Column(DateTime)
    pm1 = Column(Float)
    pm25 = Column(Float)
    pm10 = Column(Float)
    temperature = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    co = Column(Float)
    o3 = Column(Float)
    so2 = Column(Float)
    no2 = Column(Float)
    no = Column(Float)
    caqi = Column(Integer)

# pydantic models for data validation if we need it XD (and also guy in tutorial was using them)
class stations_model(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    #id: int #id is primary key wit auto increment so we dont give it
    station_id: int
    name: str

class measurements_model(BaseModel):
    model_config = ConfigDict(from_attributes=True) # some pydantic magic to convert the sqlalchemy model to a pydantic model
    
    #id: int
    station_id: int
    timestamp: datetime
    pm1: float | None = None
    pm25: float | None = None
    pm10: float | None = None
    temperature: float | None = None
    humidity: float | None = None
    pressure: float | None = None
    no2: float | None = None
    no: float | None = None
    co: float | None = None
    o3: float | None = None
    so2: float | None = None
    caqi: int | None = None

