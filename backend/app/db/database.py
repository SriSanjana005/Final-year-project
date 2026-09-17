from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Engine configuration (fallbacks or sqlite in-memory for testing if mysql not connected yet)
try:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    with engine.connect() as conn:
        pass
except Exception:
    engine = create_engine("sqlite:///./fallback_test.db", connect_args={"check_same_thread": False})


from sqlalchemy import text

def ensure_schema_migrations(engine_obj):
    """Dynamically adds missing is_test_data columns if database already exists."""
    try:
        with engine_obj.begin() as conn:
            for table in ["users", "learning_histories", "quiz_attempts", "recommendations"]:
                try:
                    info = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
                    col_names = [col[1] for col in info]
                    if col_names and "is_test_data" not in col_names:
                        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN is_test_data BOOLEAN DEFAULT 0 NOT NULL"))
                except Exception:
                    try:
                        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN is_test_data BOOLEAN DEFAULT FALSE NOT NULL"))
                    except Exception:
                        pass
    except Exception as e:
        print(f"Schema migration notice: {e}")

try:
    ensure_schema_migrations(engine)
except Exception:
    pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
