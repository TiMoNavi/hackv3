from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import VerificationCode
from datetime import datetime


def get_code(db: Session, email: str, vcode_type: str) -> VerificationCode | None:

    return db.execute(
        select(VerificationCode).where(
            VerificationCode.email == email,
            VerificationCode.type == vcode_type
        )
    ).scalar_one_or_none()


def create_or_update_code(
        db: Session, vc: VerificationCode | None,
        email: str, vcode_type: str,
        code: str, expires_at: datetime,
        now: datetime
) -> VerificationCode:

    if not vc:
        vc = VerificationCode(
            email=email,
            code=code,
            expires_at=expires_at,
            last_send_at=now,
            type=vcode_type
        )
        db.add(vc)
    else:
        vc.code = code
        vc.expires_at = expires_at
        vc.last_send_at = now
    return vc


def delete_code(db: Session, vc: VerificationCode):

    db.delete(vc)