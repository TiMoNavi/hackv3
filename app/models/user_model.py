from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base


class User(Base):
    __tablename__ = "users"
    uid = Column(Integer, primary_key=True, index=True, nullable=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    passwordHash = Column(String(255), nullable=False)
    avatarUrl = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    phone = Column(String(32), nullable=True)
    isAdmin = Column(Boolean, default=False, nullable=False)

    createdAt = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)
    updatedAt = Column(
        DateTime,
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
        nullable=False
    )

    registrations = relationship("Registration", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
