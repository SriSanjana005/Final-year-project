import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.db.seed_test_data import seed_test_data, clear_test_data
from backend.app.db.database import SessionLocal

if __name__ == "__main__":
    db = SessionLocal()
    try:
        if "--clear" in sys.argv:
            clear_test_data(db)
        else:
            seed_test_data(db)
    finally:
        db.close()
