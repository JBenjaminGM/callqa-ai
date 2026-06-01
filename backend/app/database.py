"""
Configuración de la conexión a la base de datos con SQLAlchemy 2.0.

Expone:
- engine: motor de conexión a PostgreSQL.
- SessionLocal: fábrica de sesiones.
- get_db(): dependencia de FastAPI que entrega una sesión por petición.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

# pool_pre_ping evita errores por conexiones caídas (típico en hosting cloud).
engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependencia de FastAPI: entrega una sesión de BD y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
