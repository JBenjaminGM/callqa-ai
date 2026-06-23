"""Tests de la Fase 2: métricas de conversación, compliance y analítica del dashboard."""

from app.models.agent import Agent
from app.models.analysis import Analysis
from app.models.call import Call, CallStatus
from app.models.campaign import Campaign
from app.models.transcription import Transcription
from app.services.compliance_service import check_product_note_compliance
from app.services.conversation_metrics_service import compute_conversation_metrics


# ---------------------------------------------------------------
# Helper: crea una llamada DONE con análisis y transcripción
# ---------------------------------------------------------------
def _done_call(
    db,
    uploaded_by,
    *,
    agent_id=None,
    campaign_type=None,
    campaign_id=None,
    score=85,
    dims=None,
    recs=None,
    segments=None,
    full_text="",
    detected=None,
    duration=120,
    conv=None,
):
    call = Call(
        uploaded_by=uploaded_by,
        audio_url="x",
        status=CallStatus.DONE,
        agent_id=agent_id,
        campaign_type=campaign_type,
        campaign_id=campaign_id,
        detected_agent_name=detected,
        duration_seconds=duration,
        conversation_metrics=conv,
    )
    db.add(call)
    db.flush()
    db.add(Transcription(call_id=call.id, full_text=full_text, segments=segments))
    db.add(
        Analysis(
            call_id=call.id,
            global_score=score,
            dimension_scores=dims or {"greeting": score},
            recommendations=recs or [],
        )
    )
    db.commit()
    return call


# ===============================================================
# Métricas de conversación (función pura, determinista)
# ===============================================================
def test_conversation_metrics_basic():
    segments = [
        {"start": 0.0, "end": 4.0, "speaker": "agent", "text": "hola buenas tardes le saluda Juan"},
        {"start": 4.0, "end": 6.0, "speaker": "customer", "text": "hola si"},
        {"start": 7.0, "end": 13.0, "speaker": "agent", "text": "le cuento sobre nuestra tarjeta premium con grandes beneficios hoy"},
    ]
    m = compute_conversation_metrics(segments, 13)
    assert m["agent_talk_seconds"] == 10.0
    assert m["customer_talk_seconds"] == 2.0
    assert m["talk_to_listen_ratio"] == 5.0
    assert m["agent_talk_pct"] == 83.3
    assert m["longest_agent_monologue_seconds"] == 6.0
    assert m["silence_seconds"] == 1.0
    assert m["turns"] == 3
    assert m["agent_words_per_minute"] is not None
    assert m["overall_words_per_minute"] is not None


def test_conversation_metrics_empty_returns_none():
    assert compute_conversation_metrics([], 0) is None
    assert compute_conversation_metrics(None, None) is None


def test_conversation_metrics_single_speaker_no_ratio():
    segments = [{"start": 0.0, "end": 5.0, "speaker": "agent", "text": "hola que tal"}]
    m = compute_conversation_metrics(segments, 5)
    # Sin cliente: no hay ratio hablar/escuchar.
    assert m["talk_to_listen_ratio"] is None
    assert m["turns"] == 1


# ===============================================================
# Compliance de la nota de producto
# ===============================================================
def test_compliance_detects_mandatory_and_prohibited():
    segments = [
        {"speaker": "agent", "text": "Le informo la tasa efectiva anual TEA de 39.9%."},
        {"speaker": "customer", "text": "ya entiendo"},
        {"speaker": "agent", "text": "Le garantizamos la aprobacion inmediata sin problemas."},
    ]
    report = check_product_note_compliance(
        segments,
        " ".join(s["text"] for s in segments),
        mandatory_phrases=["Informar la Tasa Efectiva Anual (TEA)"],
        prohibited_claims=["No garantizar la aprobación inmediata"],
    )
    assert report["mandatory_covered_count"] == 1
    assert report["mandatory_missing"] == []
    assert len(report["prohibited_hits"]) == 1
    assert report["prohibited_hits"][0]["evidence"]


def test_compliance_flags_missing_mandatory():
    segments = [{"speaker": "agent", "text": "hola buenos dias en que le ayudo"}]
    report = check_product_note_compliance(
        segments,
        "hola buenos dias",
        mandatory_phrases=["Informar la Tasa Efectiva Anual (TEA)"],
        prohibited_claims=[],
    )
    assert report["mandatory_covered_count"] == 0
    assert len(report["mandatory_missing"]) == 1
    assert report["coverage_pct"] == 0.0


def test_compliance_no_note():
    report = check_product_note_compliance([], "", [], [])
    assert report["has_note"] is False


# ===============================================================
# /dashboard/summary — campos nuevos de la Fase 2
# ===============================================================
def test_summary_phase2_fields(client, auth_headers, admin_user, db_session):
    _done_call(db_session, admin_user.id, score=90, dims={"greeting": 90, "sentiment": 88}, duration=100)
    _done_call(db_session, admin_user.id, score=40, dims={"greeting": 40, "sentiment": 30}, duration=200)

    body = client.get("/api/v1/dashboard/summary", headers=auth_headers).json()
    assert body["total_calls"] == 2
    assert "team_dimension_averages" in body
    assert body["team_dimension_averages"]["greeting"] == 65.0
    assert body["avg_duration_seconds"] == 150.0
    assert body["red_call_count"] == 1  # la de score 40 (< 60)


# ===============================================================
# /dashboard/by-campaign
# ===============================================================
def test_by_campaign_manager(client, auth_headers, admin_user, db_session):
    _done_call(db_session, admin_user.id, campaign_type="Tarjetas", score=80, dims={"sentiment": 70})
    _done_call(db_session, admin_user.id, campaign_type="Tarjetas", score=50, dims={"sentiment": 40})
    _done_call(db_session, admin_user.id, campaign_type="Préstamos", score=95, dims={"sentiment": 90})

    rows = client.get("/api/v1/dashboard/by-campaign", headers=auth_headers).json()
    by_name = {r["campaign"]: r for r in rows}
    assert by_name["Tarjetas"]["total_calls"] == 2
    assert by_name["Tarjetas"]["red_calls"] == 1
    assert by_name["Préstamos"]["avg_score"] == 95.0
    assert by_name["Tarjetas"]["sentiment"] is not None


def test_by_campaign_forbidden_for_asesor(client, asesor_headers):
    assert client.get("/api/v1/dashboard/by-campaign", headers=asesor_headers).status_code == 403


# ===============================================================
# /dashboard/alerts
# ===============================================================
def test_alerts_flags_red_call(client, auth_headers, admin_user, db_session, sample_agent):
    _done_call(db_session, admin_user.id, agent_id=sample_agent.id, score=35, campaign_type="Tarjetas")
    alerts = client.get("/api/v1/dashboard/alerts", headers=auth_headers).json()
    assert any(a["type"] == "red_call" for a in alerts)


def test_alerts_prohibited_claim(client, auth_headers, admin_user, db_session, sample_agent):
    campaign = Campaign(
        name="Camp Compliance",
        prohibited_claims=["No garantizar la aprobación inmediata"],
    )
    db_session.add(campaign)
    db_session.flush()
    _done_call(
        db_session,
        admin_user.id,
        agent_id=sample_agent.id,
        campaign_type="Camp Compliance",
        campaign_id=campaign.id,
        score=70,
        segments=[
            {"speaker": "agent", "text": "Le garantizamos la aprobacion inmediata."},
        ],
        full_text="Le garantizamos la aprobacion inmediata.",
    )
    alerts = client.get("/api/v1/dashboard/alerts", headers=auth_headers).json()
    assert any(a["type"] == "prohibited_claim" for a in alerts)


def test_alerts_forbidden_for_asesor(client, asesor_headers):
    assert client.get("/api/v1/dashboard/alerts", headers=asesor_headers).status_code == 403


# ===============================================================
# /dashboard/top-recommendations
# ===============================================================
def test_top_recommendations_aggregates(client, auth_headers, admin_user, db_session):
    rec = {"priority": "high", "dimension": "greeting", "title": "Mejorar el saludo", "description": "Saludar con nombre"}
    _done_call(db_session, admin_user.id, recs=[rec])
    _done_call(db_session, admin_user.id, recs=[rec])
    rows = client.get("/api/v1/dashboard/top-recommendations", headers=auth_headers).json()
    assert rows[0]["count"] == 2
    assert rows[0]["dimension"] == "greeting"


# ===============================================================
# /dashboard/agents/{id}/percentile — scoping y anonimato
# ===============================================================
def test_percentile_hidden_with_few_peers(client, asesor_headers, asesor_user, sample_agent, admin_user, db_session):
    _done_call(db_session, admin_user.id, agent_id=sample_agent.id, score=80)
    body = client.get(
        f"/api/v1/dashboard/agents/{sample_agent.id}/percentile", headers=asesor_headers
    ).json()
    # Solo 1 asesor con datos en la campaña -> oculto por anonimato.
    assert body["available"] is False


def test_percentile_available_with_enough_peers(client, asesor_headers, asesor_user, sample_agent, admin_user, db_session):
    # sample_agent (campaña "Tarjetas") + 4 colegas con datos = 5 peers (mínimo).
    _done_call(db_session, admin_user.id, agent_id=sample_agent.id, score=70)
    for i, sc in enumerate([60, 65, 90, 95]):
        peer = Agent(name=f"Colega {i}", email=f"colega{i}@t.com", campaign="Tarjetas")
        db_session.add(peer)
        db_session.flush()
        _done_call(db_session, admin_user.id, agent_id=peer.id, score=sc)

    body = client.get(
        f"/api/v1/dashboard/agents/{sample_agent.id}/percentile", headers=asesor_headers
    ).json()
    assert body["available"] is True
    assert body["peers_count"] == 5
    assert 0 <= body["percentile"] <= 100


def test_percentile_scoping_forbidden(client, asesor_headers, auth_headers):
    other = client.post("/api/v1/agents", headers=auth_headers, json={"name": "Ajeno P"}).json()
    assert (
        client.get(
            f"/api/v1/dashboard/agents/{other['id']}/percentile", headers=asesor_headers
        ).status_code
        == 403
    )


# ===============================================================
# /dashboard/agents/{id}/recommendations — scoping y contenido
# ===============================================================
def test_agent_recommendations_content_and_scoping(
    client, asesor_headers, auth_headers, asesor_user, sample_agent, admin_user, db_session
):
    rec = {"priority": "high", "dimension": "greeting", "title": "Saludar mejor", "description": "Usa el nombre"}
    _done_call(
        db_session,
        admin_user.id,
        agent_id=sample_agent.id,
        score=55,
        dims={"greeting": 50},
        recs=[rec],
        campaign_type="Tarjetas",
        segments=[{"speaker": "agent", "text": "buenas le atiendo de inmediato sin mas preambulos"}],
    )
    body = client.get(
        f"/api/v1/dashboard/agents/{sample_agent.id}/recommendations", headers=asesor_headers
    ).json()
    assert body["total_calls"] == 1
    assert body["recommendations"][0]["title"] == "Saludar mejor"
    assert body["recommendations"][0]["count"] == 1
    assert any(c["campaign"] == "Tarjetas" for c in body["by_campaign"])

    # Scoping: otro ejecutivo -> 403.
    other = client.post("/api/v1/agents", headers=auth_headers, json={"name": "Ajeno R"}).json()
    assert (
        client.get(
            f"/api/v1/dashboard/agents/{other['id']}/recommendations", headers=asesor_headers
        ).status_code
        == 403
    )
