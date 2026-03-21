from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import Config  

DATABASE_URL = Config.get_database_url()

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=1800
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    """
    Get a database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """
    Test the database connection
    """
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        print("DB OK:", result[0])
    except Exception as e:
        print("DB ERROR:", e)
    finally:
        db.close()

test_connection()
        