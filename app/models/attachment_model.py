from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, autoincrement=True)

    uploadedByUid = Column(Integer, ForeignKey("users.uid"), nullable=False, index=True)
    projectId = Column(Integer, ForeignKey("projects.projectId"), nullable=True, index=True)
    registrationId = Column(Integer, ForeignKey("registrations.registrationId"), nullable=True, index=True)

    # 文件元数据
    url = Column(String(500), nullable=False)
    key = Column(String(255), nullable=False)
    originalFilename = Column(String(255), nullable=True)
    mimeType = Column(String(100), nullable=True)

    createdAt = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)

    uploader = relationship("User")
    project = relationship("Project", back_populates="attachments")
    registration = relationship("Registration", back_populates="attachments")
