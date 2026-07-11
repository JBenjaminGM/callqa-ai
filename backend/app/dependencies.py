"""
Dependencias reutilizables de FastAPI.

La principal es `get_current_user`, que valida el JWT del header
Authorization y devuelve el usuario autenticado.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token

# Esquema de autenticación tipo "Bearer <token>".
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Valida el token JWT y devuelve el usuario autenticado.

    Lanza 401 si el token falta, es inválido o el usuario ya no existe.
    """
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado. Inicie sesión para continuar.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise error

    payload = decode_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        raise error

    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError):
        raise error

    user = db.get(User, user_id)
    if user is None:
        raise error

    return user


def require_manager(current_user: User = Depends(get_current_user)) -> User:
    """Exige rol de gestión (admin o jefe). Lanza 403 para asesores."""
    if not current_user.is_manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acción reservada a jefes de área o administradores.",
        )
    return current_user
