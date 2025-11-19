from sqlalchemy.orm import Session
from app.models.attachment_model import Attachment
from app.repository import attachment_repo


class NotFoundError(ValueError):
    pass


class ForbiddenError(ValueError):
    pass


class ConflictError(ValueError):
    pass


class AttachmentService:

    def __init__(self, db: Session):
        self.db = db

    def validate_and_get_attachment(self, att_id: int, user_id: int) -> Attachment:

        attachment = attachment_repo.get_attachment_by_id(self.db, att_id)

        if not attachment:
            raise NotFoundError(f"附件 {att_id} 未找到")

        if attachment.uploadedByUid != user_id:
            raise ForbiddenError(f"无权使用附件 {att_id}")

        if attachment.projectId is not None or attachment.registrationId is not None:
            raise ConflictError(f"附件 {att_id} 已被使用")

        return attachment