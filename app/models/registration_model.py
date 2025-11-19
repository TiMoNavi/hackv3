from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class Registration(Base):
    __tablename__ = "registrations"

    registrationId = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, ForeignKey("users.uid"), nullable=False, index=True)
    note = Column(String(1000), nullable=True)
    createdAt = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)
    status = Column(String(16), nullable=False, default="pending", server_default="pending")

    user = relationship("User", back_populates="registrations")

    attachments = relationship("Attachment", back_populates="registration", cascade="all, delete-orphan")
