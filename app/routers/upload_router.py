from fastapi import APIRouter, UploadFile, File, Depends, Query
from sqlalchemy.orm import Session
from app.core.response import ok
from app.core.security import get_current_user
from app.db.session import get_db
from app.models import User
from typing import Literal
from app.services.upload_service import UploadService

router = APIRouter(prefix="/upload", tags=["upload"])


def get_upload_service(db: Session = Depends(get_db)) -> UploadService:
    return UploadService(db)


@router.post("/image")
async def upload_file(
        file: UploadFile = File(...),
        context: Literal["registration", "project"] = Query(...),
        current_user: User = Depends(get_current_user),
        upload_service: UploadService = Depends(get_upload_service)
):

    new_attachment, size = await upload_service.save_file(file, context, current_user)

    return ok({
        "attachment_id": new_attachment.id,
        "url": new_attachment.url,
        "size": size,
        "mime": new_attachment.mimeType,
        "key": new_attachment.key,
        "originalFilename": new_attachment.originalFilename
    })