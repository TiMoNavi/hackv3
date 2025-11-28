from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, constr
from .attachment_schema import AttachmentOut


class RegistrationIn(BaseModel):
    note: constr(max_length=100000)
    attachment_ids: Optional[List[int]] = None


class RegistrationOut(BaseModel):
    uid: int
    registrationId: int
    note: str
    createdAt: datetime
    status: str = 'pending'

    attachments: List[AttachmentOut] = []

    class Config:
        from_attributes = True
