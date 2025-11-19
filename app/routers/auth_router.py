from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session
from app.core.response import ok, err
from app.db.session import get_db
from app.schemas import RegisterIn, LoginIn, SendCodeIn, ResetPasswordIn, TokenPair
from app.services.auth_service import AuthService, AuthError, ConflictError, ForbiddenError

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/send-verification-code")
def send_code_api(body: SendCodeIn, background: BackgroundTasks, auth_service: AuthService = Depends(get_auth_service)):
    try:
        expire_in = auth_service.send_verification_code(body.email, "register", background)
        return ok({"expire_in": expire_in}, "验证码已发送")
    except ConflictError as e:
        return err(str(e), code=40901, status_code=status.HTTP_409_CONFLICT)
    except ForbiddenError as e:
        return err(str(e), code=42901, status_code=status.HTTP_429_TOO_MANY_REQUESTS)
    except ValueError as e:
        return err(str(e), code=40001, status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/register")
def register_api(body: RegisterIn, auth_service: AuthService = Depends(get_auth_service)):
    try:
        user = auth_service.register_user(body)
        return ok({
            "uid": user.uid,
            "username": user.username,
            "email": user.email,
        }, "注册成功")
    except (AuthError, ConflictError) as e:
        return err(str(e), code=40002, status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/login")
def login_api(body: LoginIn, auth_service: AuthService = Depends(get_auth_service)):
    try:
        token_pair = auth_service.login(body)
        return ok(token_pair.model_dump(), "登录成功")
    except AuthError as e:
        return err(str(e), code=40101, status_code=status.HTTP_401_UNAUTHORIZED)
    except ValueError as e:
        return err(str(e), code=42201, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@router.post("/forgot-password/send-code")
def forgot_password_send_code(body: SendCodeIn, background: BackgroundTasks, auth_service: AuthService = Depends(get_auth_service)):
    try:
        expire_in = auth_service.send_verification_code(body.email, "reset", background)
        return ok({"expire_in": expire_in}, "验证码已发送")
    except ForbiddenError as e:
        return err(str(e), code=42901, status_code=status.HTTP_429_TOO_MANY_REQUESTS)


@router.post("/forgot-password/reset")
def reset_password(body: ResetPasswordIn, auth_service: AuthService = Depends(get_auth_service)):
    try:
        auth_service.reset_password(body)
        return ok(message="密码重置成功")
    except AuthError as e:
        return err(str(e), code=40003, status_code=status.HTTP_400_BAD_REQUEST)