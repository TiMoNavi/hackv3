from sqlalchemy.orm import Session
from app.models.attachment_model import Attachment


def create_attachment(db: Session, user_id: int, url: str, key: str, filename: str, mime: str) -> Attachment:
    new_attachment = Attachment(
        uploadedByUid=user_id,
        projectId=None,
        registrationId=None,
        url=url,
        key=key,
        originalFilename=filename,
        mimeType=mime
    )
    db.add(new_attachment)
    return new_attachment


def get_attachment_by_id(db: Session, attachment_id: int) -> Attachment | None:
    return db.get(Attachment, attachment_id)


def link_attachment_to_project(db: Session, attachment: Attachment, project_id: int):
    attachment.projectId = project_id
    db.add(attachment)


def link_attachment_to_registration(db: Session, attachment: Attachment, registration_id: int):
    attachment.registrationId = registration_id
    db.add(attachment)