from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from app.db.db import Base
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

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
    pm1: Optional[float] = None
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    no2: Optional[float] = None
    no: Optional[float] = None
    co: Optional[float] = None
    o3: Optional[float] = None
    so2: Optional[float] = None
    caqi: Optional[int] = None