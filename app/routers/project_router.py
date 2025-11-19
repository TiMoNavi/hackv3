from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.core.response import ok, err
from app.models import User
from app.schemas import ProjectIn, ProjectOut
from app.services.project_service import ProjectService, NotFoundError, ForbiddenError, ConflictError
from typing import List

router = APIRouter(prefix="/project", tags=["project"])


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


@router.post("")
def create_project(
    data: ProjectIn,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    try:
        new_project = project_service.create_project(data, current_user)
        return ok(ProjectOut.model_validate(new_project).model_dump())
    except (NotFoundError, ForbiddenError, ConflictError) as e:
        return err(str(e), code=40004, status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/my")
def list_my_projects(
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    projects = project_service.get_my_projects(current_user)
    return ok([ProjectOut.model_validate(p).model_dump() for p in projects])


@router.get("/{projectId}")
def get_project_detail(
    projectId: int,
    project_service: ProjectService = Depends(get_project_service)
):
    try:
        project = project_service.get_project_details(projectId)
        return ok(ProjectOut.model_validate(project).model_dump())
    except NotFoundError as e:
        return err(str(e), code=40401, status_code=status.HTTP_404_NOT_FOUND)