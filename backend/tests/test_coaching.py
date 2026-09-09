"""
Tests del cierre del ciclo: acuse de recibo del asesor y a quién escuchar hoy.

Lo que se protege:

- que el acuse lo firme **quien recibió la evaluación**, no un jefe por él;
- que reabrir una petición no la deje contestada de antes;
- que «a quién escuchar hoy» no repita la misma llamada con varios motivos.
"""

from datetime import date, datetime, timedelta

from app.models.acknowledgement import Acknowledgement
from app.models.analysis import Analysis
from app.models.call import Call, CallStatus
from app.models.review import Review
from app.models.settings import AppSettings


def _done_call(db, uploaded_by, *, score, agent_id=None, days_ago=1, campaign=None):
    """Crea una llamada procesada con su análisis."""
    momento = datetime.now() - timedelta(days=days_ago)
    call = Call(
        uploaded_by=uploaded_by,
        audio_url="x",
        status=CallStatus.DONE,
        agent_id=agent_id,
        call_date=(date.today() - timedelta(days=days_ago)),
        campaign_type=campaign,
        created_at=momento,
        duration_seconds=90,
    )
    db.add(call)
    db.flush()
    db.add(
        Analysis(
            call_id=call.id,
            global_score=score,
            dimension_scores={"greeting": score},
            recommendations=[],
            created_at=momento,
        )
    )
    db.commit()
    return call


# ===============================================================
# Acuse de recibo
# ===============================================================
def test_el_asesor_acusa_recibo_de_su_evaluacion(
    client, db_session, admin_user, asesor_headers, sample_agent
):
    call = _done_call(db_session, admin_user.id, score=72, agent_id=sample_agent.id)

    r = client.put(
        f"/api/v1/calls/{call.id}/acknowledgement",
        json={"comment": "Recibido. El cliente colgó antes del cierre."},
        headers=asesor_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["user_name"] == "Asesor Demo"
    assert body["review_requested"] is False
    assert body["pending_review"] is False

    detail = client.get(f"/api/v1/calls/{call.id}", headers=asesor_headers).json()
    assert detail["acknowledgement"]["comment"].startswith("Recibido.")


def test_el_asesor_no_puede_acusar_recibo_de_una_llamada_ajena(
    client, db_session, admin_user, asesor_headers
):
    ajena = _done_call(db_session, admin_user.id, score=72, agent_id=None)
    r = client.put(
        f"/api/v1/calls/{ajena.id}/acknowledgement",
        json={"comment": "No es mía."},
        headers=asesor_headers,
    )
    assert r.status_code == 403


def test_el_jefe_no_puede_acusar_recibo_en_nombre_del_asesor(
    client, db_session, admin_user, auth_headers, sample_agent
):
    """Un acuse de recibo firmado por otro no significa nada."""
    call = _done_call(db_session, admin_user.id, score=72, agent_id=sample_agent.id)
    r = client.put(
        f"/api/v1/calls/{call.id}/acknowledgement",
        json={"comment": "Dado por leído."},
        headers=auth_headers,
    )
    assert r.status_code == 403


def test_peticion_de_revision_y_respuesta_del_jefe(
    client, db_session, admin_user, auth_headers, asesor_headers, sample_agent
):
    call = _done_call(db_session, admin_user.id, score=55, agent_id=sample_agent.id)

    pedida = client.put(
        f"/api/v1/calls/{call.id}/acknowledgement",
        json={"comment": "El cliente ya era cliente, no aplicaba el guion.", "review_requested": True},
        headers=asesor_headers,
    ).json()
    assert pedida["pending_review"] is True

    # Al jefe le aparece como pendiente.
    pendientes = client.get("/api/v1/coaching/pending", headers=auth_headers).json()
    assert [p["call_id"] for p in pendientes] == [call.id]

    contestada = client.post(
        f"/api/v1/calls/{call.id}/acknowledgement/reply",
        json={"reply": "Revisado: tienes razón, ajusto la nota."},
        headers=auth_headers,
    ).json()
    assert contestada["manager_reply"].startswith("Revisado")
    assert contestada["replied_by_name"] == "Admin Test"
    assert contestada["pending_review"] is False

    assert client.get("/api/v1/coaching/pending", headers=auth_headers).json() == []


def test_reabrir_la_peticion_descarta_la_respuesta_anterior(
    client, db_session, admin_user, auth_headers, asesor_headers, sample_agent
):
    """
    Si el asesor vuelve a pedir revisión, la conversación se reanuda. Dejar la
    respuesta vieja la haría pasar por contestada sin que nadie haya leído lo
    nuevo.
    """
    call = _done_call(db_session, admin_user.id, score=55, agent_id=sample_agent.id)
    client.put(
        f"/api/v1/calls/{call.id}/acknowledgement",
        json={"comment": "No estoy de acuerdo.", "review_requested": True},
        headers=asesor_headers,
    )
    client.post(
        f"/api/v1/calls/{call.id}/acknowledgement/reply",
        json={"reply": "Lo mantengo."},
        headers=auth_headers,
    )
    # El asesor lo acepta y retira la petición...
    client.put(
        f"/api/v1/calls/{call.id}/acknowledgement",
        json={"comment": "Entendido.", "review_requested": False},
        headers=asesor_headers,
    )
    # ...y más tarde vuelve a pedirla con un argumento nuevo.
    reabierta = client.put(
        f"/api/v1/calls/{call.id}/acknowledgement",
        json={"comment": "Encontré la grabación completa.", "review_requested": True},
        headers=asesor_headers,
    ).json()

    assert reabierta["manager_reply"] is None
    assert reabierta["replied_at"] is None
    assert reabierta["pending_review"] is True


def test_no_se_puede_acusar_recibo_sin_evaluacion(
    client, db_session, admin_user, asesor_headers, sample_agent
):
    call = Call(
        uploaded_by=admin_user.id,
        audio_url="x",
        status=CallStatus.QUEUED,
        agent_id=sample_agent.id,
    )
    db_session.add(call)
    db_session.commit()

    r = client.put(
        f"/api/v1/calls/{call.id}/acknowledgement",
        json={"comment": "Hola."},
        headers=asesor_headers,
    )
    assert r.status_code == 409


def test_mis_pendientes_solo_lista_lo_no_acusado(
    client, db_session, admin_user, asesor_headers, sample_agent
):
    acusada = _done_call(db_session, admin_user.id, score=80, agent_id=sample_agent.id)
    pendiente = _done_call(db_session, admin_user.id, score=70, agent_id=sample_agent.id)
    client.put(
        f"/api/v1/calls/{acusada.id}/acknowledgement",
        json={"comment": "Visto."},
        headers=asesor_headers,
    )

    ids = [
        c["call_id"]
        for c in client.get("/api/v1/coaching/my-pending", headers=asesor_headers).json()
    ]
    assert ids == [pendiente.id]


# ===============================================================
# A quién escuchar hoy
# ===============================================================
def test_la_peticion_de_revision_encabeza_la_lista(
    client, db_session, admin_user, auth_headers, asesor_headers, sample_agent
):
    # Una roja sin escuchar, que ya sería motivo de sobra...
    _done_call(db_session, admin_user.id, score=35, agent_id=sample_agent.id)
    # ...y una con petición abierta, que va por delante: hay alguien esperando.
    pedida = _done_call(db_session, admin_user.id, score=68, agent_id=sample_agent.id)
    client.put(
        f"/api/v1/calls/{pedida.id}/acknowledgement",
        json={"comment": "La objeción sí la rebatí, minuto 3.", "review_requested": True},
        headers=asesor_headers,
    )

    lista = client.get("/api/v1/coaching/who-to-listen", headers=auth_headers).json()
    assert lista[0]["call_id"] == pedida.id
    assert lista[0]["reason"] == "review_requested"
    assert lista[0]["description"].startswith("La objeción")


def test_una_llamada_aparece_una_sola_vez(
    client, db_session, admin_user, auth_headers, asesor_headers, sample_agent
):
    """
    La misma llamada puede cumplir tres motivos a la vez. Repetirla tres veces
    convertiría la lista en ruido: sale con el motivo más fuerte y ya.
    """
    for _ in range(4):
        _done_call(db_session, admin_user.id, score=90, agent_id=sample_agent.id)
    mala = _done_call(db_session, admin_user.id, score=30, agent_id=sample_agent.id)
    client.put(
        f"/api/v1/calls/{mala.id}/acknowledgement",
        json={"comment": "Pido revisión.", "review_requested": True},
        headers=asesor_headers,
    )

    lista = client.get("/api/v1/coaching/who-to-listen", headers=auth_headers).json()
    ids = [s["call_id"] for s in lista]
    assert ids.count(mala.id) == 1
    assert lista[0]["reason"] == "review_requested"


def test_la_banda_roja_ya_escuchada_no_se_propone(
    client, db_session, admin_user, auth_headers
):
    """Si alguien ya la revisó, proponerla otra vez es hacer trabajo repetido."""
    escuchada = _done_call(db_session, admin_user.id, score=30)
    db_session.add(
        Review(
            call_id=escuchada.id,
            reviewer_id=admin_user.id,
            global_score=35,
            dimension_scores={"greeting": 35},
        )
    )
    db_session.commit()

    lista = client.get("/api/v1/coaching/who-to-listen", headers=auth_headers).json()
    motivos = {
        s["call_id"]: s["reason"] for s in lista if s["call_id"] == escuchada.id
    }
    assert motivos.get(escuchada.id) != "red_unreviewed"


def test_detecta_la_llamada_muy_por_debajo_de_la_media_del_asesor(
    client, db_session, admin_user, auth_headers, sample_agent
):
    for _ in range(4):
        _done_call(db_session, admin_user.id, score=92, agent_id=sample_agent.id)
    floja = _done_call(db_session, admin_user.id, score=70, agent_id=sample_agent.id)

    lista = client.get("/api/v1/coaching/who-to-listen", headers=auth_headers).json()
    por_id = {s["call_id"]: s for s in lista}
    assert por_id[floja.id]["reason"] == "below_own_average"
    assert "por debajo de su media" in por_id[floja.id]["title"]


def test_señala_al_asesor_del_que_nadie_ha_escuchado_nada(
    client, db_session, admin_user, auth_headers, sample_agent
):
    """No es una alarma, es cobertura: nadie sabe cómo está trabajando."""
    for score in (88, 90, 91):
        _done_call(db_session, admin_user.id, score=score, agent_id=sample_agent.id)

    lista = client.get("/api/v1/coaching/who-to-listen", headers=auth_headers).json()
    motivos = [s["reason"] for s in lista]
    assert "never_reviewed_agent" in motivos


def test_sin_llamadas_no_hay_sugerencias(client, auth_headers):
    assert client.get("/api/v1/coaching/who-to-listen", headers=auth_headers).json() == []


def test_el_asesor_no_ve_a_quien_escuchar_hoy(client, asesor_headers):
    r = client.get("/api/v1/coaching/who-to-listen", headers=asesor_headers)
    assert r.status_code == 403
