from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Engine configuration (fallbacks or sqlite in-memory for testing if mysql not connected yet)
try:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
except Exception:
    # fallback engine placeholder
    engine = create_engine("sqlite:///./fallback_test.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
