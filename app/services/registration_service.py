from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import User, Registration
from app.schemas import RegistrationIn, AdminRegistrationCreate
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

    def get_all_registrations(self, status: str | None, page: int, page_size: int = 20):
        items, total = registration_repo.list_registrations(self.db, status, page, page_size)
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def audit_registration(self, registration_id: int, status: str) -> Registration:
        if status not in {"approved", "rejected", "pending"}:
            raise ValueError("非法审核状态")
        reg = registration_repo.get_registration_by_id(self.db, registration_id, eager_load=True)
        if not reg:
            raise NotFoundError("报名不存在")
        try:
            registration_repo.update_registration_status(self.db, reg, status)
            self.db.commit()
            self.db.refresh(reg)
            return reg
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"审核失败: {str(e)}")

    def delete_registration(self, registration_id: int):
        reg = registration_repo.get_registration_by_id(self.db, registration_id, eager_load=False)
        if not reg:
            raise NotFoundError("报名不存在")
        try:
            registration_repo.delete_registration(self.db, reg)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

    def update_registration_note(self, registration_id: int, note: str) -> Registration:
        reg = registration_repo.get_registration_by_id(self.db, registration_id, eager_load=True)
        if not reg:
            raise NotFoundError("报名不存在")
        reg.note = note
        try:
            self.db.add(reg)
            self.db.commit()
            self.db.refresh(reg)
            return reg
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")

    def admin_create_registration(self, data: AdminRegistrationCreate) -> Registration:
        # 管理员为指定 uid 创建报名，不限制“一个用户只能一条”的规则可根据业务调整
        try:
            new_reg = registration_repo.create_registration(self.db, RegistrationIn(note=data.note, attachment_ids=data.attachment_ids or []), data.uid)
            self.db.flush()
            if data.attachment_ids:
                for att_id in data.attachment_ids:
                    attachment = self.attachment_service.validate_and_get_attachment(att_id=att_id, user_id=data.uid)
                    attachment_repo.link_attachment_to_registration(self.db, attachment, new_reg.registrationId)
            self.db.commit()
            self.db.refresh(new_reg)
            return new_reg
        except (NotFoundError, ForbiddenError, ConflictError) as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"创建报名失败: {str(e)}")
