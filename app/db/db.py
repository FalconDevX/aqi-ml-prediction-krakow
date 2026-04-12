from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import Config
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends

engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# will check if we can connecto to the db
SessionDependency = Annotated[Session, Depends(get_db)]