from datetime import datetime, timedelta, timezone
from typing import Optional, TypedDict

from fastapi import Depends, Header, HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models import User

ALGORITHM = "HS256"

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenPayload(TypedDict, total=False):
    sub: str
    exp: int
    iat: int
    typ: str  # "access" | "refresh"
    aud: str


def create_token(
    subject: str,
    *,
    minutes: int,
    kind: str = "access",
    audience: str = "event-frontend",
) -> str:
    now = datetime.now(timezone.utc)
    payload: TokenPayload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
        "typ": kind,
        "aud": audience,
    }
    return jwt.encode(payload, settings.SECURITY_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.SECURITY_KEY, algorithms=[ALGORITHM], options={"verify_aud": False})
        # Audience check left to caller if needed
        return payload  # type: ignore[return-value]
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效或过期的令牌") from e


def bearer_token_from_header(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少 Authorization 头")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authorization 格式应为 Bearer <token>")
    return parts[1]


def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> User:
    token = bearer_token_from_header(authorization)
    payload = decode_token(token)
    if payload.get("typ") != "access":
        raise HTTPException(status_code=401, detail="令牌类型错误")
    user_id = payload.get("sub")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


def _truncate_for_bcrypt(raw: str) -> bytes:
    # bcrypt 只接受前 72 个字节，这里对 utf-8 编码后的字节流截断，避免 ValueError

    b = raw.encode("utf-8")
    if len(b) > 72:
        b = b[:70]
    return b


def hash_password(raw: str) -> str:
    return pwd_ctx.hash(_truncate_for_bcrypt(raw))


def verify_password(raw: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    try:
        return pwd_ctx.verify(_truncate_for_bcrypt(raw), hashed)
    except Exception:
        return False