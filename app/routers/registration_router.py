from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.core.response import ok, err
from app.models import User
from app.schemas import RegistrationIn, RegistrationOut
from app.services.registration_service import RegistrationService
from app.services.project_service import NotFoundError, ForbiddenError, ConflictError

router = APIRouter(prefix="/registration", tags=["registration"])


def get_reg_service(db: Session = Depends(get_db)) -> RegistrationService:
    return RegistrationService(db)


@router.post("")
def create_registration(
        data: RegistrationIn,
        current_user: User = Depends(get_current_user),
        reg_service: RegistrationService = Depends(get_reg_service)
):
    try:
        reg = reg_service.create_registration(data, current_user)
        return ok(RegistrationOut.model_validate(reg).model_dump())
    except ConflictError as e:
        return err(str(e), code=40903, status_code=status.HTTP_409_CONFLICT)
    except (NotFoundError, ForbiddenError) as e:
        return err(str(e), code=40005, status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/status")
def get_registration_status(
    current_user: User = Depends(get_current_user),
    reg_service: RegistrationService = Depends(get_reg_service)
):
    try:
        reg = reg_service.get_status(current_user)
        return ok(RegistrationOut.model_validate(reg).model_dump())
    except NotFoundError as e:
        return err(str(e), code=40402, status_code=status.HTTP_404_NOT_FOUND)