"""Schemas de autenticación."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Credenciales enviadas al endpoint de login."""

    email: EmailStr
    password: str = Field(min_length=1)


class UserOut(BaseModel):
    """Datos públicos de un usuario."""

    id: int
    name: str
    email: EmailStr
    role: str
    last_login: datetime | None = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Respuesta del login: token JWT + datos del usuario."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut
