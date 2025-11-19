import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, constr


class PublicUser(BaseModel):
    uid: int
    username: str
    avatarUrl: Optional[str] = None
    bio: Optional[str] = None
    createdAt: datetime

    class Config:
        from_attributes = True


class MeProfile(BaseModel):
    uid: int
    username: str
    email: str
    avatarUrl: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class UpdateProfile(BaseModel):
    name: Optional[constr(min_length=2, max_length=50)] = Field(None, description="Display name (maps to username)")
    bio: Optional[constr(max_length=500)] = None
    phone: Optional[constr(pattern=r'^[0-9+\-\s()]{7,20}$')] = None
    avatarUrl: Optional[constr(max_length=500)] = None
