from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class AttachmentOut(BaseModel):
    id: int
    url: str
    originalFilename: Optional[str]
    mimeType: Optional[str]
    createdAt: datetime

    class Config:
        from_attributes = True
