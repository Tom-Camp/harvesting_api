import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from zxcvbn import zxcvbn

from app.models.user import UserRole, UserStatus

_MIN_ZXCVBN_SCORE = 3


def _validate_password_strength(v: str) -> str:
    result = zxcvbn(v)
    if result["score"] < _MIN_ZXCVBN_SCORE:
        warning = result["feedback"].get("warning")
        suggestions = result["feedback"].get("suggestions", [])
        message = warning or (suggestions[0] if suggestions else "Password is too weak")
        raise ValueError(message)
    return v


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password_strength(v)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    picture: str | None = None


class SetRoleRequest(BaseModel):
    role: UserRole


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    first_name: str | None = None
    last_name: str | None = None
    picture: str | None = None
    status: UserStatus
    role: UserRole
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password_strength(v)
