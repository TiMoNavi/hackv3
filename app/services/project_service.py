from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import User, Project, Attachment
from app.schemas import ProjectIn
from app.repository import project_repo, attachment_repo
from typing import List

from app.services.attachment_service import AttachmentService, NotFoundError, ForbiddenError, ConflictError


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.attachment_service = AttachmentService(db)

    def create_project(self, data: ProjectIn, user: User) -> Project:
        try:
            new_project = project_repo.create_project(self.db, data, user.uid)
            self.db.flush()

            if data.attachment_ids:
                for att_id in data.attachment_ids:
                    attachment = self.attachment_service.validate_and_get_attachment(
                        att_id=att_id,
                        user_id=user.uid
                    )

                    attachment_repo.link_attachment_to_project(self.db, attachment, new_project.projectId)

            self.db.commit()
            self.db.refresh(new_project)
            return new_project

        except (NotFoundError, ForbiddenError, ConflictError) as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"创建项目失败: {str(e)}")

    def get_my_projects(self, user: User) -> List[Project]:
        return project_repo.get_projects_by_uid(self.db, user.uid)

    def get_project_details(self, project_id: int) -> Project:
        project = project_repo.get_project_by_id(self.db, project_id)
        if not project:
            raise NotFoundError("项目不存在")  # 使用集中的异常
        return project