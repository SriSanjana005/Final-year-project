from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.user import User
from app.models.parent import ParentProfile
from app.models.child import ChildProfile
from app.models.parent_child import ParentChild
from app.schemas.user_profile import ParentChildCreate, ParentChildResponse
from app.core.dependencies import require_role

router = APIRouter(prefix="/parent-child", tags=["Parent-Child Mappings"])

# GET /api/parent-child (Admin only)
@router.get("", response_model=List[ParentChildResponse])
def get_all_parent_child_mappings(db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin"]))):
    return db.query(ParentChild).all()

# POST /api/parent-child (Admin only)
@router.post("", response_model=ParentChildResponse, status_code=status.HTTP_201_CREATED)
def create_parent_child_mapping(
    payload: ParentChildCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    parent = db.query(ParentProfile).filter(ParentProfile.id == payload.parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent profile not found")

    child = db.query(ChildProfile).filter(ChildProfile.id == payload.child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child profile not found")

    existing = db.query(ParentChild).filter(
        ParentChild.parent_id == payload.parent_id,
        ParentChild.child_id == payload.child_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Parent-Child mapping already exists")

    mapping = ParentChild(
        parent_id=payload.parent_id,
        child_id=payload.child_id,
        relationship_type=payload.relationship_type
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping

# DELETE /api/parent-child/{mapping_id} (Admin only)
@router.delete("/{mapping_id}", status_code=status.HTTP_200_OK)
def delete_parent_child_mapping(
    mapping_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    mapping = db.query(ParentChild).filter(ParentChild.id == mapping_id).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")

    db.delete(mapping)
    db.commit()
    return {"message": "Parent-Child mapping deleted successfully"}
