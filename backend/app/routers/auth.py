"""Endpoints de autenticación."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.limiter import limiter
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserOut
from app.services.auth_service import authenticate_user
from app.utils.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_response(user: User) -> TokenResponse:
    """Construye la respuesta estándar con token JWT a partir de un usuario."""
    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expire_hours * 3600,
        user=UserOut.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/15minutes")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """
    Inicia sesión con email y contraseña.

    Rate limiting: máximo 5 intentos cada 15 minutos por IP (slowapi requiere
    que el parámetro `request` esté presente en la firma).
    """
    user = authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos.",
        )
    return _token_response(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(current_user: User = Depends(get_current_user)):
    """Renueva el token JWT del usuario autenticado."""
    return _token_response(current_user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: User = Depends(get_current_user)):
    """
    Cierra la sesión.

    Con JWT sin estado, el logout real lo hace el cliente descartando el
    token. Este endpoint existe por consistencia de la API.
    """
    return None


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    """Devuelve los datos del usuario autenticado."""
    return UserOut.model_validate(current_user)
