"""Tests del módulo de gestión de ejecutivos."""


def test_create_agent(client, auth_headers):
    """Se puede crear un ejecutivo y aparece en el listado."""
    response = client.post(
        "/api/v1/agents",
        headers=auth_headers,
        json={"name": "Pedro Test", "email": "pedro@test.com"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Pedro Test"
    assert body["active"] is True


def test_list_agents(client, auth_headers):
    """El listado devuelve los ejecutivos creados."""
    client.post(
        "/api/v1/agents",
        headers=auth_headers,
        json={"name": "Ana Test", "email": "ana@test.com"},
    )
    response = client.get("/api/v1/agents", headers=auth_headers)
    assert response.status_code == 200
    assert any(a["name"] == "Ana Test" for a in response.json())


def test_create_agent_duplicate_email(client, auth_headers):
    """Crear dos ejecutivos con el mismo email devuelve 400."""
    payload = {"name": "Dup Uno", "email": "dup@test.com"}
    client.post("/api/v1/agents", headers=auth_headers, json=payload)
    response = client.post(
        "/api/v1/agents",
        headers=auth_headers,
        json={"name": "Dup Dos", "email": "dup@test.com"},
    )
    assert response.status_code == 400


def test_update_agent(client, auth_headers):
    """Se pueden actualizar los datos de un ejecutivo."""
    created = client.post(
        "/api/v1/agents",
        headers=auth_headers,
        json={"name": "Editar Test"},
    ).json()
    response = client.put(
        f"/api/v1/agents/{created['id']}",
        headers=auth_headers,
        json={"campaign": "Nueva Campaña"},
    )
    assert response.status_code == 200
    assert response.json()["campaign"] == "Nueva Campaña"


def test_deactivate_agent(client, auth_headers):
    """Desactivar un ejecutivo lo marca como inactivo (soft delete)."""
    created = client.post(
        "/api/v1/agents",
        headers=auth_headers,
        json={"name": "Baja Test"},
    ).json()
    response = client.delete(
        f"/api/v1/agents/{created['id']}", headers=auth_headers
    )
    assert response.status_code == 204

    detail = client.get(
        f"/api/v1/agents/{created['id']}", headers=auth_headers
    ).json()
    assert detail["active"] is False


def test_agents_require_auth(client):
    """Los endpoints de ejecutivos requieren autenticación."""
    assert client.get("/api/v1/agents").status_code == 401
