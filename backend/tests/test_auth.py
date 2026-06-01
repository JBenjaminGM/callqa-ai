"""Tests del módulo de autenticación."""


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
