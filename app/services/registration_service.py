from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import User, Registration
from app.schemas import RegistrationIn
from app.repository import registration_repo, attachment_repo

from app.services.attachment_service import AttachmentService, NotFoundError, ForbiddenError, ConflictError


class RegistrationService:
    def __init__(self, db: Session):
        self.db = db
        self.attachment_service = AttachmentService(db)

    def create_registration(self, data: RegistrationIn, user: User) -> Registration:
        if registration_repo.get_registration_by_uid(self.db, user.uid):
            raise ConflictError("该用户已提交报名")

        try:
            new_reg = registration_repo.create_registration(self.db, data, user.uid)
            self.db.flush()

            if data.attachment_ids:
                for att_id in data.attachment_ids:
                    attachment = self.attachment_service.validate_and_get_attachment(
                        att_id=att_id,
                        user_id=user.uid
                    )

                    attachment_repo.link_attachment_to_registration(self.db, attachment, new_reg.registrationId)

            self.db.commit()
            self.db.refresh(new_reg)
            return new_reg
        except (NotFoundError, ForbiddenError, ConflictError) as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"报名失败: {str(e)}")

    def get_status(self, user: User) -> Registration:
        reg = registration_repo.get_registration_by_uid(self.db, user.uid, eager_load=True)
        if not reg:
            raise NotFoundError("尚未提交报名")
        return reg
