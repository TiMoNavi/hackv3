from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_admin
from app.core.response import ok
from app.db.session import get_db
from app.models import User
from app.services.stats_service import StatsService
from app.services.registration_service import RegistrationService
from app.services.user_service import UserService
from app.core.response import err
from fastapi import status, Query
from app.schemas import RegistrationOut, PublicUser, ProjectOut, ProjectUpdate, AdminRegistrationCreate
from app.repository import registration_repo
from app.repository import project_repo

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/ping")
def admin_ping(current_admin: User = Depends(get_current_admin)):
    return ok({"pong": True})


def get_stats_service(db: Session = Depends(get_db)) -> StatsService:
    return StatsService(db)


@router.get("/stats")
def get_stats(current_admin: User = Depends(get_current_admin), stats: StatsService = Depends(get_stats_service)):
    return ok(stats.get_counts())


def get_reg_service(db: Session = Depends(get_db)) -> RegistrationService:
    return RegistrationService(db)


@router.get("/registrations")
def list_registrations(
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    current_admin: User = Depends(get_current_admin),
    reg_service: RegistrationService = Depends(get_reg_service)
):
    data = reg_service.get_all_registrations(status, page)
    data["items"] = [RegistrationOut.model_validate(r).model_dump() for r in data["items"]]
    return ok(data)


@router.get("/registrations/{registrationId}")
def get_registration_detail(
    registrationId: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    r = registration_repo.get_registration_by_id(db, registrationId, eager_load=True)
    if not r:
        return err("报名不存在", code=40403, status_code=status.HTTP_404_NOT_FOUND)
    return ok(RegistrationOut.model_validate(r).model_dump())


@router.put("/registrations/{registrationId}/audit")
def audit_registration(
    registrationId: int,
    status_: str = Query(..., alias="status"),
    current_admin: User = Depends(get_current_admin),
    reg_service: RegistrationService = Depends(get_reg_service)
):
    try:
        r = reg_service.audit_registration(registrationId, status_)
        return ok(RegistrationOut.model_validate(r).model_dump())
    except ValueError as e:
        return err(str(e), code=40007, status_code=status.HTTP_400_BAD_REQUEST)


@router.delete("/registrations/{registrationId}")
def delete_registration(
    registrationId: int,
    current_admin: User = Depends(get_current_admin),
    reg_service: RegistrationService = Depends(get_reg_service)
):
    try:
        reg_service.delete_registration(registrationId)
        return ok({"deleted": True})
    except NotFoundError as e:
        return err(str(e), code=40403, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return err(str(e), code=50006, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.put("/registrations/{registrationId}")
def update_registration(
    registrationId: int,
    note: str = Query(..., min_length=1, max_length=100000),
    current_admin: User = Depends(get_current_admin),
    reg_service: RegistrationService = Depends(get_reg_service)
):
    try:
        r = reg_service.update_registration_note(registrationId, note)
        return ok(RegistrationOut.model_validate(r).model_dump())
    except NotFoundError as e:
        return err(str(e), code=40403, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return err(str(e), code=50006, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/registrations")
def admin_create_registration(
    body: AdminRegistrationCreate,
    current_admin: User = Depends(get_current_admin),
    reg_service: RegistrationService = Depends(get_reg_service)
):
    try:
        r = reg_service.admin_create_registration(body)
        return ok(RegistrationOut.model_validate(r).model_dump())
    except (ForbiddenError, ConflictError, NotFoundError) as e:
        return err(str(e), code=40008, status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return err(str(e), code=50006, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


@router.get("/users")
def list_users(
    page: int = Query(1, ge=1),
    current_admin: User = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service)
):
    data = user_service.get_all_users(page)
    data["items"] = [PublicUser.model_validate(u).model_dump() for u in data["items"]]
    return ok(data)


# ---- Admin Project CRUD ----

@router.get("/projects")
def admin_list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    q = db.query(project_repo.Project)
    total = q.count()
    items = (
        q.order_by(project_repo.Project.createdAt.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return ok({
        "items": [ProjectOut.model_validate(p).model_dump() for p in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/projects/{projectId}")
def admin_get_project(projectId: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    p = project_repo.get_project_by_id(db, projectId)
    if not p:
        return err("项目不存在", code=40404, status_code=status.HTTP_404_NOT_FOUND)
    return ok(ProjectOut.model_validate(p).model_dump())


@router.put("/projects/{projectId}")
def admin_update_project(
    projectId: int,
    body: ProjectUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    p = project_repo.get_project_by_id(db, projectId)
    if not p:
        return err("项目不存在", code=40404, status_code=status.HTTP_404_NOT_FOUND)
    try:
        project_repo.update_project(db, p, title=body.title, description=body.description, repoUrl=body.repoUrl, demoUrl=body.demoUrl)
        db.commit()
        db.refresh(p)
        return ok(ProjectOut.model_validate(p).model_dump())
    except Exception as e:
        db.rollback()
        return err(f"更新失败: {e}", code=50004, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.delete("/projects/{projectId}")
def admin_delete_project(projectId: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    p = project_repo.get_project_by_id(db, projectId)
    if not p:
        return err("项目不存在", code=40404, status_code=status.HTTP_404_NOT_FOUND)
    try:
        project_repo.delete_project(db, p)
        db.commit()
        return ok({"deleted": True})
    except Exception as e:
        db.rollback()
        return err(f"删除失败: {e}", code=50005, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
