from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, constr
from .attachment_schema import AttachmentOut


class RegistrationIn(BaseModel):
    note: Optional[constr(max_length=1000)] = None
    attachment_ids: Optional[List[int]] = None


class RegistrationOut(BaseModel):
    uid: int
    registrationId: int
    note: Optional[str]
    createdAt: datetime
    status: str = 'pending'

    attachments: List[AttachmentOut] = []

    class Config:
        from_attributes = True
