from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, constr
from .attachment_schema import AttachmentOut


class ProjectIn(BaseModel):
    title: constr(min_length=1, max_length=200)
    description: constr(min_length=1, max_length=5000)
    repoUrl: Optional[constr(max_length=500)] = None
    demoUrl: Optional[constr(max_length=500)] = None
    attachment_ids: Optional[List[int]] = None


class ProjectOut(BaseModel):
    projectId: int
    uid: int
    title: str
    description: str
    repoUrl: Optional[str]
    demoUrl: Optional[str]
    createdAt: datetime
    updatedAt: datetime

    attachments: List[AttachmentOut] = []

    class Config:
        from_attributes = True
