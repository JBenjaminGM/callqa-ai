"""Tests de roles, autorización y scoping (admin/jefe vs asesor)."""

from app.models.agent import Agent
from app.models.call import Call, CallStatus


# ---------------------------------------------------------------
# /auth/me expone rol y vínculo
# ---------------------------------------------------------------
def test_me_includes_role_and_agent(client, asesor_headers, asesor_user, sample_agent):
    me = client.get("/api/v1/auth/me", headers=asesor_headers).json()
    assert me["role"] == "asesor"
    assert me["agent_id"] == sample_agent.id


# ---------------------------------------------------------------
# El asesor NO puede acceder a funciones de gestión
# ---------------------------------------------------------------
def test_asesor_cannot_create_agent(client, asesor_headers):
    r = client.post("/api/v1/agents", headers=asesor_headers, json={"name": "X"})
    assert r.status_code == 403


def test_asesor_cannot_access_dashboard_summary(client, asesor_headers):
    assert client.get("/api/v1/dashboard/summary", headers=asesor_headers).status_code == 403


def test_asesor_cannot_upload_call(client, asesor_headers):
    import io

    r = client.post(
        "/api/v1/calls",
        headers=asesor_headers,
        files={"audio": ("a.mp3", io.BytesIO(b"x"), "audio/mpeg")},
    )
    assert r.status_code == 403


def test_manager_can_access_dashboard_summary(client, auth_headers):
    assert client.get("/api/v1/dashboard/summary", headers=auth_headers).status_code == 200


# ---------------------------------------------------------------
# Scoping: el asesor solo ve SUS datos
# ---------------------------------------------------------------
def test_asesor_lists_only_own_agent(client, auth_headers, asesor_headers, sample_agent):
    client.post("/api/v1/agents", headers=auth_headers, json={"name": "Otro Ejecutivo"})
    agents = client.get("/api/v1/agents", headers=asesor_headers).json()
    assert len(agents) == 1
    assert agents[0]["id"] == sample_agent.id


def test_asesor_cannot_view_other_agent(client, auth_headers, asesor_headers, sample_agent):
    other = client.post(
        "/api/v1/agents", headers=auth_headers, json={"name": "Ajeno"}
    ).json()
    assert client.get(f"/api/v1/agents/{other['id']}", headers=asesor_headers).status_code == 403
    # Su propia ficha sí
    assert (
        client.get(f"/api/v1/agents/{sample_agent.id}", headers=asesor_headers).status_code
        == 200
    )


def test_asesor_cannot_view_other_agent_dashboard(
    client, auth_headers, asesor_headers, sample_agent
):
    other = client.post(
        "/api/v1/agents", headers=auth_headers, json={"name": "Ajeno2"}
    ).json()
    assert (
        client.get(f"/api/v1/dashboard/agents/{other['id']}", headers=asesor_headers).status_code
        == 403
    )
    assert (
        client.get(
            f"/api/v1/dashboard/agents/{sample_agent.id}", headers=asesor_headers
        ).status_code
        == 200
    )


def test_asesor_sees_only_own_calls(
    client, asesor_headers, asesor_user, sample_agent, admin_user, db_session
):
    other = Agent(name="Otro", email="otro@test.com")
    db_session.add(other)
    db_session.commit()
    db_session.add(
        Call(uploaded_by=admin_user.id, audio_url="a", agent_id=sample_agent.id, status=CallStatus.DONE)
    )
    db_session.add(
        Call(uploaded_by=admin_user.id, audio_url="b", agent_id=other.id, status=CallStatus.DONE)
    )
    db_session.commit()

    body = client.get("/api/v1/calls", headers=asesor_headers).json()
    assert body["total"] == 1
    assert body["items"][0]["agent"]["id"] == sample_agent.id


# ---------------------------------------------------------------
# Creación de la cuenta de acceso del asesor
# ---------------------------------------------------------------
def test_create_agent_login(client, auth_headers, asesor_headers):
    agent = client.post(
        "/api/v1/agents", headers=auth_headers, json={"name": "Nuevo Asesor"}
    ).json()

    r = client.post(
        f"/api/v1/agents/{agent['id']}/login",
        headers=auth_headers,
        json={"email": "nuevo@test.com", "password": "Password123", "name": "Nuevo"},
    )
    assert r.status_code == 201
    assert r.json()["role"] == "asesor"
    assert r.json()["agent_id"] == agent["id"]

    # Ese ejecutivo ya tiene cuenta -> 400
    dup = client.post(
        f"/api/v1/agents/{agent['id']}/login",
        headers=auth_headers,
        json={"email": "otro2@test.com", "password": "Password123"},
    )
    assert dup.status_code == 400

    # Un asesor no puede crear cuentas
    forbidden = client.post(
        f"/api/v1/agents/{agent['id']}/login",
        headers=asesor_headers,
        json={"email": "z@test.com", "password": "Password123"},
    )
    assert forbidden.status_code == 403


# ---------------------------------------------------------------
# Umbrales de QA configurables
# ---------------------------------------------------------------
def test_qa_thresholds_default_and_update(client, auth_headers, asesor_headers):
    s = client.get("/api/v1/config/settings", headers=auth_headers).json()
    assert s["qa_target_score"] == 90
    assert s["qa_red_call_threshold"] == 60

    upd = client.put(
        "/api/v1/config/settings", headers=auth_headers, json={"qa_target_score": 85}
    )
    assert upd.status_code == 200
    assert upd.json()["qa_target_score"] == 85

    # El asesor no puede cambiar settings
    forbidden = client.put(
        "/api/v1/config/settings", headers=asesor_headers, json={"qa_target_score": 70}
    )
    assert forbidden.status_code == 403
