from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.session import Base


class Project(Base):
    __tablename__ = "projects"

    projectId = Column(Integer, primary_key=True, autoincrement=True, index=True)
    uid = Column(Integer, ForeignKey("users.uid"), nullable=False, index=True)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    repoUrl = Column(String(500), nullable=True)
    demoUrl = Column(String(500), nullable=True)
    createdAt = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)
    updatedAt = Column(
        DateTime,
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
        nullable=False
    )

    user = relationship("User", back_populates="projects")

    attachments = relationship("Attachment", back_populates="project", cascade="all, delete-orphan")
    __table_args__ = (Index("ix_project_user_created", "uid", "createdAt"),)

