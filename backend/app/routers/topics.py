from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter(prefix="/topics", tags=["Topics"])

@router.get("")
def get_topics(db: Session = Depends(get_db)):
    return [
        {"id": 1, "title": "Mathematics - Addition & Subtraction", "category": "Math", "icon": "calculator"},
        {"id": 2, "title": "Reading Comprehension", "category": "English", "icon": "book-open"},
        {"id": 3, "title": "Visual Pattern Recognition", "category": "Logic", "icon": "shapes"}
    ]
