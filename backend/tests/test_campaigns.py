"""Tests del módulo de campañas y notas de producto."""

import io

import app.services.campaign_ai as campaign_ai
from app.prompts.analysis_es import build_analysis_prompt
from app.services.campaign_service import build_product_note_text


# ---------------------------------------------------------------
# CRUD de campañas
# ---------------------------------------------------------------
def test_create_campaign(client, auth_headers):
    """Se puede crear una campaña con su nota de producto."""
    response = client.post(
        "/api/v1/campaigns",
        headers=auth_headers,
        json={
            "name": "Tarjeta Oro",
            "product_service": "Tarjeta de crédito Oro",
            "offer_description": "Tarjeta sin cuota el primer año.",
            "key_benefits": ["Cashback 2%", "Sala VIP aeropuerto"],
            "mandatory_phrases": ["Debe informar la TEA"],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Tarjeta Oro"
    assert body["active"] is True
    assert body["key_benefits"] == ["Cashback 2%", "Sala VIP aeropuerto"]
    assert body["calls_count"] == 0


def test_list_campaigns(client, auth_headers):
    """El listado devuelve las campañas creadas."""
    client.post(
        "/api/v1/campaigns", headers=auth_headers, json={"name": "Seguros Vida"}
    )
    response = client.get("/api/v1/campaigns", headers=auth_headers)
    assert response.status_code == 200
    assert any(c["name"] == "Seguros Vida" for c in response.json())


def test_get_campaign(client, auth_headers):
    """Se puede consultar el detalle de una campaña."""
    created = client.post(
        "/api/v1/campaigns", headers=auth_headers, json={"name": "Préstamo Express"}
    ).json()
    response = client.get(
        f"/api/v1/campaigns/{created['id']}", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Préstamo Express"


def test_create_campaign_duplicate_name(client, auth_headers):
    """Crear dos campañas con el mismo nombre devuelve 400."""
    client.post("/api/v1/campaigns", headers=auth_headers, json={"name": "Duplicada"})
    response = client.post(
        "/api/v1/campaigns", headers=auth_headers, json={"name": "Duplicada"}
    )
    assert response.status_code == 400


def test_update_campaign(client, auth_headers):
    """Se pueden actualizar los datos de una campaña."""
    created = client.post(
        "/api/v1/campaigns", headers=auth_headers, json={"name": "Editar Camp"}
    ).json()
    response = client.put(
        f"/api/v1/campaigns/{created['id']}",
        headers=auth_headers,
        json={"offer_description": "Nueva oferta", "key_benefits": ["A", "B"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["offer_description"] == "Nueva oferta"
    assert body["key_benefits"] == ["A", "B"]


def test_deactivate_campaign(client, auth_headers):
    """Desactivar una campaña la marca como inactiva (soft delete)."""
    created = client.post(
        "/api/v1/campaigns", headers=auth_headers, json={"name": "Baja Camp"}
    ).json()
    response = client.delete(
        f"/api/v1/campaigns/{created['id']}", headers=auth_headers
    )
    assert response.status_code == 204
    detail = client.get(
        f"/api/v1/campaigns/{created['id']}", headers=auth_headers
    ).json()
    assert detail["active"] is False


def test_campaigns_require_auth(client):
    """Los endpoints de campañas requieren autenticación."""
    assert client.get("/api/v1/campaigns").status_code == 401


def test_list_campaign_with_null_lists(client, auth_headers, db_session):
    """Una campaña con listas en NULL (p.ej. migrada) se serializa como [] sin error."""
    from app.models.campaign import Campaign

    db_session.add(
        Campaign(
            name="Migrada X",
            source="migrated",
            key_benefits=None,
            mandatory_phrases=None,
            prohibited_claims=None,
        )
    )
    db_session.commit()

    resp = client.get("/api/v1/campaigns", headers=auth_headers)
    assert resp.status_code == 200
    item = next(c for c in resp.json() if c["name"] == "Migrada X")
    assert item["key_benefits"] == []
    assert item["mandatory_phrases"] == []
    assert item["prohibited_claims"] == []


# ---------------------------------------------------------------
# Extracción desde PDF (IA y lectura de PDF mockeadas)
# ---------------------------------------------------------------
def test_extract_campaign_from_pdf(client, auth_headers, monkeypatch):
    """Subir un PDF devuelve la nota estructurada y los campos que faltan."""
    monkeypatch.setattr(
        campaign_ai,
        "extract_text_from_pdf",
        lambda content: "Campaña Tarjeta Oro. Cashback 2%.",
    )
    monkeypatch.setattr(
        campaign_ai,
        "llm_json",
        lambda prompt: {
            "name": "Tarjeta Oro",
            "product_service": "Tarjeta de crédito",
            "offer_description": "Sin cuota el primer año.",
            "key_benefits": ["Cashback 2%"],
            "pricing_conditions": None,  # falta -> missing
            "mandatory_phrases": [],  # falta -> missing
        },
    )
    response = client.post(
        "/api/v1/campaigns/extract",
        headers=auth_headers,
        files={"file": ("nota.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["draft"]["name"] == "Tarjeta Oro"
    assert body["draft"]["key_benefits"] == ["Cashback 2%"]
    assert "pricing_conditions" in body["missing_fields"]
    assert "mandatory_phrases" in body["missing_fields"]
    assert body["warning"] is None


def test_extract_rejects_non_pdf(client, auth_headers):
    """Subir un archivo que no es PDF devuelve 400."""
    response = client.post(
        "/api/v1/campaigns/extract",
        headers=auth_headers,
        files={"file": ("nota.txt", io.BytesIO(b"texto"), "text/plain")},
    )
    assert response.status_code == 400


def test_extract_handles_unreadable_pdf(client, auth_headers, monkeypatch):
    """Un PDF sin texto legible devuelve un borrador vacío con aviso (cae al formulario)."""
    monkeypatch.setattr(campaign_ai, "extract_text_from_pdf", lambda content: "")
    response = client.post(
        "/api/v1/campaigns/extract",
        headers=auth_headers,
        files={"file": ("scan.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["warning"] is not None
    assert "name" in body["missing_fields"]


# ---------------------------------------------------------------
# Asistencia por IA del formulario
# ---------------------------------------------------------------
def test_assist_campaign(client, auth_headers, monkeypatch):
    """La asistencia por IA devuelve un borrador completado."""
    monkeypatch.setattr(
        campaign_ai,
        "llm_json",
        lambda prompt: {
            "name": "Crédito Hipotecario",
            "offer_description": "Crédito para vivienda a tasa fija.",
            "key_benefits": ["Tasa fija", "Hasta 30 años"],
        },
    )
    response = client.post(
        "/api/v1/campaigns/assist",
        headers=auth_headers,
        json={"description": "crédito hipotecario a tasa fija para vivienda"},
    )
    assert response.status_code == 200
    draft = response.json()["draft"]
    assert draft["offer_description"] == "Crédito para vivienda a tasa fija."
    assert draft["key_benefits"] == ["Tasa fija", "Hasta 30 años"]


# ---------------------------------------------------------------
# Inyección de la nota de producto en el prompt de análisis
# ---------------------------------------------------------------
def test_product_note_text_builder(db_session):
    """El texto de la nota de producto incluye los campos rellenados."""
    from app.models.campaign import Campaign

    campaign = Campaign(
        name="Tarjeta Oro",
        offer_description="Sin cuota el primer año.",
        key_benefits=["Cashback 2%", "Sala VIP"],
    )
    text = build_product_note_text(campaign)
    assert "Tarjeta Oro" in text
    assert "Cashback 2%" in text
    assert "Sala VIP" in text


def test_analysis_prompt_includes_product_note():
    """El prompt de análisis incluye la nota de producto cuando se proporciona."""
    rubric = [{"dimension_key": "promotions", "dimension_name": "Promociones", "criteria": []}]
    prompt = build_analysis_prompt(
        [{"text": "Hola"}], rubric, product_note="- Producto: Tarjeta Oro con cashback"
    )
    assert "NOTA DE PRODUCTO" in prompt
    assert "Tarjeta Oro con cashback" in prompt


def test_analysis_prompt_without_product_note():
    """Sin nota de producto, el prompt no incluye la sección (compatibilidad)."""
    rubric = [{"dimension_key": "greeting", "dimension_name": "Saludo", "criteria": []}]
    prompt = build_analysis_prompt([{"text": "Hola"}], rubric)
    assert "NOTA DE PRODUCTO" not in prompt


# ---------------------------------------------------------------
# Asignación de campaña a una llamada al subirla
# ---------------------------------------------------------------
def test_upload_call_with_campaign_id(client, auth_headers, monkeypatch):
    """Subir una llamada con campaign_id la enlaza y rellena campaign_type."""
    monkeypatch.setattr(
        "app.routers.calls.process_call.delay", lambda call_id: None
    )
    campaign = client.post(
        "/api/v1/campaigns", headers=auth_headers, json={"name": "Campaña Llamada"}
    ).json()

    upload = client.post(
        "/api/v1/calls",
        headers=auth_headers,
        files={"audio": ("c.mp3", io.BytesIO(b"audio"), "audio/mpeg")},
        data={"campaign_id": str(campaign["id"])},
    )
    assert upload.status_code == 202
    call_id = upload.json()["id"]

    detail = client.get(f"/api/v1/calls/{call_id}", headers=auth_headers).json()
    assert detail["campaign_type"] == "Campaña Llamada"
    assert detail["campaign"]["id"] == campaign["id"]


def test_upload_call_with_unknown_campaign_id(client, auth_headers, monkeypatch):
    """Subir una llamada con un campaign_id inexistente devuelve 400."""
    monkeypatch.setattr(
        "app.routers.calls.process_call.delay", lambda call_id: None
    )
    response = client.post(
        "/api/v1/calls",
        headers=auth_headers,
        files={"audio": ("c.mp3", io.BytesIO(b"audio"), "audio/mpeg")},
        data={"campaign_id": "99999"},
    )
    assert response.status_code == 400
