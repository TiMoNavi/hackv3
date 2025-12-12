from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.models import User
from app.repository import attachment_repo
from app.core.config import settings
import os, uuid, mimetypes
import magic
from app.models.attachment_model import Attachment

SAFE_MIMES = {"image/jpeg", "image/png", "image/gif", "image/webp", "application/pdf"}


def guess_mime(filename: str, header_bytes: bytes) -> str:
    mime = mimetypes.guess_type(filename)[0]
    if not mime:
        try:
            detected = magic.from_buffer(header_bytes, mime=True)
            if detected:
                mime = detected
        except Exception:
            mime = None
    if not mime and header_bytes.startswith(b'%PDF-'):
        mime = "application/pdf"
    return mime or "application/octet-stream"


def build_public_url(sub_folder: str, filename: str) -> str:
    base = settings.PUBLIC_BASE_URL.rstrip("/") if settings.PUBLIC_BASE_URL else ""
    if base:
        return f"{base}/{sub_folder}/{filename}"
    return f"/static/{sub_folder}/{filename}"


class UploadService:
    def __init__(self, db: Session):
        self.db = db

    async def save_file(self, file: UploadFile, context: str, user: User) -> (Attachment, int):
        context_map = {"registration": "报名", "project": "项目"}
        context_zh = context_map.get(context)
        folder_name = f"{user.uid}_{context_zh}"
        target_dir = os.path.join(settings.UPLOAD_DIR, folder_name)

        data = await file.read()
        size = len(data)
        if size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="文件过大")

        original_filename = file.filename or "upload.bin"
        mime = guess_mime(original_filename, data[:4096])
        if mime not in SAFE_MIMES:
            raise HTTPException(status_code=400, detail="不支持的文件类型")

        ext_map = {
            'image/jpeg': '.jpg', 'image/png': '.png', 'image/gif': '.gif',
            'image/webp': '.webp', 'application/pdf': '.pdf'
        }
        ext = ext_map.get(mime, "")
        os.makedirs(target_dir, exist_ok=True)
        key = uuid.uuid4().hex + ext
        path = os.path.join(target_dir, key)
        url = build_public_url(folder_name, key)

        try:
            new_attachment = attachment_repo.create_attachment(self.db, user.uid, url, key, original_filename, mime)
            with open(path, "wb") as f:
                f.write(data)

            self.db.commit()
            self.db.refresh(new_attachment)
            return new_attachment, size
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"数据库错误: {str(e)}")
