from pydantic import BaseModel, constr, EmailStr
from typing import Optional


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class RefreshIn(BaseModel):
    refresh_token: str


class RegisterIn(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=6, max_length=128)
    verification_code: constr(min_length=6, max_length=6)


class LoginIn(BaseModel):
    username: Optional[constr(min_length=3, max_length=50)] = None
    email: Optional[EmailStr] = None
    password: constr(min_length=6, max_length=128)


class SendCodeIn(BaseModel):
    email: EmailStr


class ResetPasswordIn(BaseModel):
    email: EmailStr
    verification_code: constr(min_length=6, max_length=6)
    new_password: constr(min_length=6, max_length=128)
