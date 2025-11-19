from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UpdateProfile
from app.repository import user_repo
from datetime import datetime
from fastapi import HTTPException


class ConflictError(ValueError):
    pass


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def update_profile(self, user: User, data: UpdateProfile) -> User:
        if data.name and data.name != user.username:
            if user_repo.get_user_by_username(self.db, data.name):
                raise ConflictError("该用户名已被占用")
            user.username = data.name

        if data.bio is not None:
            user.bio = data.bio
        if data.phone is not None:
            user.phone = data.phone
        if data.avatarUrl is not None:
            user.avatarUrl = data.avatarUrl

        user.updatedAt = datetime.utcnow()

        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ConflictError): raise e
            raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")