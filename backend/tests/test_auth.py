"""Tests del módulo de autenticación."""

import pytest

from app.config import settings
from app.main import DEFAULT_JWT_SECRET, verify_production_secrets


def test_login_success(client, admin_user):
    """Login con credenciales correctas devuelve un token JWT."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "Admin123!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "admin@test.com"


def test_login_wrong_password(client, admin_user):
    """Login con contraseña incorrecta devuelve 401."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "incorrecta"},
    )
    assert response.status_code == 401


def test_login_unknown_email(client):
    """Login con un email inexistente devuelve 401."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nadie@test.com", "password": "Admin123!"},
    )
    assert response.status_code == 401


def test_me_requires_auth(client):
    """El endpoint /auth/me sin token devuelve 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_with_token(client, auth_headers):
    """El endpoint /auth/me con token válido devuelve el usuario."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "admin@test.com"


def test_prototype_header_present(client):
    """Todas las respuestas incluyen el header de aviso de prototipo."""
    response = client.get("/")
    assert response.headers.get("X-Prototype-Notice") is not None


def test_produccion_rechaza_el_jwt_secret_de_ejemplo(monkeypatch):
    """Arrancar en producción con el JWT_SECRET de ejemplo debe abortar."""
    monkeypatch.setattr(settings, "app_env", "production")
    monkeypatch.setattr(settings, "jwt_secret", DEFAULT_JWT_SECRET)
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        verify_production_secrets()


def test_produccion_acepta_un_jwt_secret_propio(monkeypatch):
    """Con un secreto propio, el arranque en producción no se bloquea."""
    monkeypatch.setattr(settings, "app_env", "production")
    monkeypatch.setattr(settings, "jwt_secret", "un-secreto-largo-y-aleatorio-de-verdad")
    verify_production_secrets()


def test_desarrollo_tolera_el_jwt_secret_de_ejemplo(monkeypatch):
    """Fuera de producción el valor de ejemplo es aceptable y no bloquea."""
    monkeypatch.setattr(settings, "app_env", "development")
    monkeypatch.setattr(settings, "jwt_secret", DEFAULT_JWT_SECRET)
    verify_production_secrets()
