from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from app.core.config import settings
from app.core.security import verify_password, hash_password, create_token
from app.core.mail import send_verification_code
from app.models import User
from app.repository import user_repo, vcode_repo
from app.utils.uid import generate_uid
from app.schemas import RegisterIn, LoginIn, ResetPasswordIn, TokenPair


# 定义服务层特定的异常
class AuthError(ValueError):
    pass


class ConflictError(ValueError):
    pass


class ForbiddenError(ValueError):
    pass


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def _handle_db_exception(self, e: Exception):
        self.db.rollback()
        if isinstance(e, (ValueError, ConflictError, ForbiddenError)):
            raise e
        raise HTTPException(status_code=500, detail=f"数据库操作失败: {str(e)}")

    def send_verification_code(self, email: str, vcode_type: str, background: BackgroundTasks):
        if vcode_type == "register":
            if user_repo.get_user_by_email(self.db, email):
                raise ConflictError("该邮箱已被注册")
        elif vcode_type == "reset":
            if not user_repo.get_user_by_email(self.db, email):
                return settings.VERIFICATION_CODE_EXPIRE_MINUTES * 60

        now = datetime.utcnow()
        ttl_minutes = settings.VERIFICATION_CODE_EXPIRE_MINUTES
        min_interval = settings.VERIFICATION_CODE_MIN_INTERVAL_SECONDS

        vc = vcode_repo.get_code(self.db, email, vcode_type)
        last = vc.last_send_at if vc else None

        if last and (now - last).total_seconds() < min_interval:
            raise ForbiddenError("请勿频繁发送验证码")  # 429

        code = f"{random.randint(100000, 999999)}"
        expires_at = now + timedelta(minutes=ttl_minutes)

        try:
            vcode_repo.create_or_update_code(self.db, vc, email, vcode_type, code, expires_at, now)
            self.db.commit()
        except Exception as e:
            self._handle_db_exception(e)

        background.add_task(send_verification_code, email, code)
        return ttl_minutes * 60

    def register_user(self, data: RegisterIn) -> User:
        now = datetime.utcnow()
        vc = vcode_repo.get_code(self.db, data.email, "register")

        if not vc or vc.code != data.verification_code or (vc.expires_at < now):
            raise AuthError("验证码错误或已过期")

        if user_repo.get_user_by_username_or_email(self.db, data.username, data.email):
            raise ConflictError("用户名或邮箱已存在")

        uid = generate_uid(self.db, int(now.timestamp()), "your_salt_here")

        try:
            user = user_repo.create_user(self.db, data, uid, now)
            vcode_repo.delete_code(self.db, vc)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self._handle_db_exception(e)

    def login(self, data: LoginIn) -> TokenPair:
        if not data.username and not data.email:
            raise ValueError("必须提供用户名或邮箱")

        u = user_repo.get_user_by_username_or_email(self.db, data.username, data.email)

        if not u or not verify_password(data.password, u.passwordHash):
            raise AuthError("用户名/邮箱或密码错误")

        sub = str(u.uid)
        access = create_token(sub, minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES, kind="access")
        refresh = create_token(sub, minutes=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60, kind="refresh")
        return TokenPair(access_token=access, refresh_token=refresh)

    def reset_password(self, data: ResetPasswordIn):
        now = datetime.utcnow()
        vc = vcode_repo.get_code(self.db, data.email, "reset")
        if not vc or vc.code != data.verification_code or (vc.expires_at < now):
            raise AuthError("验证码错误或已过期")

        user = user_repo.get_user_by_email(self.db, data.email)
        if not user:
            raise AuthError("用户不存在")  # 404

        try:
            user.passwordHash = hash_password(data.new_password)
            user.updatedAt = now
            vcode_repo.delete_code(self.db, vc)
            self.db.commit()
        except Exception as e:
            self._handle_db_exception(e)