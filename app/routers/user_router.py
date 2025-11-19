from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User
from app.core.security import get_current_user
from app.core.response import ok, err
from app.schemas import UpdateProfile, MeProfile
from app.services.user_service import UserService, ConflictError

router = APIRouter(prefix="/user", tags=["user"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    profile_data = MeProfile.model_validate(current_user).model_dump()
    return ok(profile_data)


@router.put("/profile")
def update_profile(
    profile: UpdateProfile, 
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        updated_user = user_service.update_profile(current_user, profile)
        profile_data = MeProfile.model_validate(updated_user).model_dump()
        return ok(profile_data)
    except ConflictError as e:
        return err(str(e), code=40902, status_code=status.HTTP_409_CONFLICT)