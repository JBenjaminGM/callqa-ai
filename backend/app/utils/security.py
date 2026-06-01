"""
Utilidades de seguridad: hashing de contraseñas y tokens JWT.

- Las contraseñas se almacenan hasheadas con bcrypt (nunca en texto plano).
- Las sesiones se gestionan con JWT firmados con HS256.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Contexto de hashing. cost factor 12 según los requerimientos de seguridad.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(password: str) -> str:
    """Devuelve el hash bcrypt de una contraseña en texto plano."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Comprueba si una contraseña coincide con su hash almacenado."""
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(subject: str | int, extra: dict | None = None) -> str:
    """
    Genera un JWT firmado.

    `subject` se guarda en el claim 'sub' (normalmente el id del usuario).
    El token expira tras JWT_EXPIRE_HOURS horas.
    """
    now = datetime.now(timezone.utc)
    payload: dict = {
        "sub": str(subject),
        "iat": now,
        "exp": now + timedelta(hours=settings.jwt_expire_hours),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    """Decodifica y valida un JWT. Devuelve el payload o None si es inválido/expirado."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
