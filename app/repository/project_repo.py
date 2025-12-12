from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from app.models import Project
from app.schemas import ProjectIn
from typing import List


def create_project(db: Session, data: ProjectIn, user_id: int) -> Project:

    p = Project(
        uid=user_id,
        title=data.title,
        description=data.description,
        repoUrl=data.repoUrl,
        demoUrl=data.demoUrl
    )
    db.add(p)
    return p


def get_project_by_id(db: Session, project_id: int) -> Project:

    return (
        db.query(Project)
        .options(joinedload(Project.attachments))
        .filter(Project.projectId == project_id)
        .first()
    )


def get_projects_by_uid(db: Session, user_id: int) -> List[Project]:

    return (
        db.query(Project)
        .filter(Project.uid == user_id)
        .options(joinedload(Project.attachments))
        .order_by(Project.createdAt.desc())
        .all()
    )


def update_project(db: Session, project: Project, *, title=None, description=None, repoUrl=None, demoUrl=None) -> Project:
    if title is not None:
        project.title = title
    if description is not None:
        project.description = description
    if repoUrl is not None:
        project.repoUrl = repoUrl
    if demoUrl is not None:
        project.demoUrl = demoUrl
    db.add(project)
    return project


def delete_project(db: Session, project: Project):
    db.delete(project)
