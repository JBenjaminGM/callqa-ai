"""
Configuración compartida de los tests.

Usa una base de datos SQLite en memoria y sustituye la dependencia get_db
para no necesitar PostgreSQL durante los tests.
"""

import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import get_db
from app.limiter import limiter
from app.main import app
from app.models import Base, RubricConfig, User
from app.utils.security import hash_password

# Almacenamiento de audios en una carpeta temporal durante los tests.
settings.storage_path = tempfile.mkdtemp(prefix="callqa_test_")

# Se desactiva el rate limiting en los tests: el cliente de pruebas usa
# siempre la misma IP y dispararía el límite de /auth/login entre tests.
limiter.enabled = False

# Motor SQLite en memoria, compartido entre conexiones (StaticPool).
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _setup_database():
    """Crea las tablas antes de cada test y las elimina al terminar."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Entrega una sesión de base de datos para usar en los tests."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def _override_get_db():
    """Versión de get_db que usa la base de datos de tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Cliente HTTP de pruebas con la dependencia de BD sustituida."""
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session):
    """Crea un usuario administrador de prueba."""
    user = User(
        email="admin@test.com",
        password_hash=hash_password("Admin123!"),
        name="Admin Test",
        role="supervisor",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def seed_rubric(db_session):
    """Carga las 7 dimensiones de la rúbrica para los tests que las necesiten."""
    dims = [
        ("greeting", "Saludo", 14.28, 1),
        ("assertiveness", "Asertividad", 14.28, 2),
        ("promotions", "Promociones", 14.28, 3),
        ("compliance", "Cumplimiento", 14.28, 4),
        ("resolution", "Resolución", 14.28, 5),
        ("objections", "Objeciones", 14.28, 6),
        ("sentiment", "Sentimiento", 14.32, 7),
    ]
    for key, name, weight, order in dims:
        db_session.add(
            RubricConfig(
                dimension_key=key,
                dimension_name=name,
                weight=weight,
                display_order=order,
            )
        )
    db_session.commit()


@pytest.fixture
def auth_headers(client, admin_user):
    """Devuelve las cabeceras Authorization con un token válido del admin."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "Admin123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
