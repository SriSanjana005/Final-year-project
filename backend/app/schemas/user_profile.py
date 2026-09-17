from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChildProfileCreate(BaseModel):
    date_of_birth: Optional[str] = None
    learning_level: str = "beginner"
    learning_requirements: Optional[str] = None

class ChildProfileResponse(BaseModel):
    id: int
    user_id: int
    date_of_birth: Optional[str] = None
    learning_level: str
    learning_requirements: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True

class ParentProfileCreate(BaseModel):
    phone: Optional[str] = None

class ParentProfileResponse(BaseModel):
    id: int
    user_id: int
    phone: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True

class ParentChildCreate(BaseModel):
    parent_id: int
    child_id: int
    relationship_type: str = "Parent"

class ParentChildResponse(BaseModel):
    id: int
    parent_id: int
    child_id: int
    relationship_type: str
    created_at: datetime
    parent: Optional[ParentProfileResponse] = None
    child: Optional[ChildProfileResponse] = None

    class Config:
        from_attributes = True

class AdminMetricsResponse(BaseModel):
    total_users: int
    total_children: int
    total_parents: int
    total_mappings: int
