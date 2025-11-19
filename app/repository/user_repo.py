from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import User
from app.schemas import RegisterIn
from app.core.security import hash_password
from datetime import datetime


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_username_or_email(db: Session, username: str, email: str) -> User | None:
    return db.query(User).filter(
        or_(User.username == username, User.email == email)
    ).first()


def create_user(db: Session, data: RegisterIn, uid: int, now: datetime) -> User:
    u = User(
        username=data.username.strip(),
        email=data.email.strip().lower(),
        uid=uid,
        createdAt=now,
        updatedAt=now,
        passwordHash=hash_password(data.password)
    )
    db.add(u)
    return u