from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import User, Registration, Project, Attachment


class StatsService:
    def __init__(self, db: Session):
        self.db = db

    def get_counts(self) -> dict:
        users = self.db.query(func.count(User.uid)).scalar() or 0
        registrations = self.db.query(func.count(Registration.registrationId)).scalar() or 0
        projects = self.db.query(func.count(Project.projectId)).scalar() or 0
        attachments = self.db.query(func.count(Attachment.id)).scalar() or 0
        return {
            "users": users,
            "registrations": registrations,
            "projects": projects,
            "attachments": attachments,
        }
