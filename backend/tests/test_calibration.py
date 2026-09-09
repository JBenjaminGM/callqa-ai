"""
Tests de la calibración: revisión humana de una nota y acuerdo IA-humano.

Lo que se protege aquí, por orden de importancia:

- que revisar **no borre** la nota de la IA;
- que la sesión a ciegas no filtre el score de la IA al cliente;
- que el informe de acuerdo distinga sesgo de desviación media.
"""

from datetime import date, datetime, timedelta

from app.models.analysis import Analysis
from app.models.call import Call, CallStatus
from app.models.settings import RubricConfig
from app.models.transcription import Transcription
from app.services.review_service import compute_global_score


def _rubric(db, pesos: dict[str, float]) -> None:
    """Deja la rúbrica con exactamente estas dimensiones y pesos."""
    for i, (key, weight) in enumerate(pesos.items()):
        db.add(
            RubricConfig(
                dimension_key=key,
                dimension_name=key.replace("_", " ").capitalize(),
                weight=weight,
                display_order=i,
            )
        )
    db.commit()


def _done_call(db, uploaded_by, *, dims, score, days_ago=1, campaign=None, agent_id=None):
    """Crea una llamada procesada con su análisis IA y una transcripción."""
    call = Call(
        uploaded_by=uploaded_by,
        audio_url="x",
        status=CallStatus.DONE,
        call_date=date.today() - timedelta(days=days_ago),
        created_at=datetime.now() - timedelta(days=days_ago),
        campaign_type=campaign,
        agent_id=agent_id,
        duration_seconds=90,
    )
    db.add(call)
    db.flush()
    db.add(
        Transcription(
            call_id=call.id,
            full_text="hola buenas tardes",
            segments=[
                {"start": 0.0, "end": 2.0, "speaker": "agent", "text": "hola buenas tardes"}
            ],
        )
    )
    db.add(
        Analysis(call_id=call.id, global_score=score, dimension_scores=dims, recommendations=[])
    )
    db.commit()
    return call


# ===============================================================
# Score global ponderado (función pura)
# ===============================================================
def test_global_ponderado_usa_los_pesos():
    pesos = {"saludo": 70.0, "cierre": 30.0}
    assert compute_global_score({"saludo": 100, "cierre": 0}, pesos) == 70


def test_global_renormaliza_si_faltan_pesos():
    """
    La rúbrica cambió después del análisis: la mitad de las dimensiones ya no
    tiene peso. El global debe salir de las que sí lo tienen, no hundirse.
    """
    pesos = {"saludo": 50.0}
    assert compute_global_score({"saludo": 80, "dimension_retirada": 20}, pesos) == 80


def test_global_sin_pesos_cae_a_la_media():
    assert compute_global_score({"a": 90, "b": 70}, {}) == 80


def test_global_sin_dimensiones_es_cero():
    assert compute_global_score({}, {"saludo": 100.0}) == 0


# ===============================================================
# Revisión de una nota
# ===============================================================
def test_revisar_no_pisa_la_nota_de_la_ia(client, db_session, admin_user, auth_headers):
    _rubric(db_session, {"saludo": 50.0, "cierre": 50.0})
    call = _done_call(db_session, admin_user.id, dims={"saludo": 90, "cierre": 90}, score=90)

    r = client.put(
        f"/api/v1/calls/{call.id}/review",
        json={
            "dimension_scores": {"saludo": 60, "cierre": 40},
            "comment": "No confirmó el importe de la cuota.",
        },
        headers=auth_headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["global_score"] == 50
    assert body["ai_global_score"] == 90
    assert body["global_delta"] == -40
    assert body["dimension_deltas"] == {"saludo": -30, "cierre": -50}
    assert body["reviewer_name"] == "Admin Test"

    # La nota de la IA sigue en su sitio, sin tocar.
    detail = client.get(f"/api/v1/calls/{call.id}", headers=auth_headers).json()
    assert detail["analysis"]["global_score"] == 90
    assert detail["analysis"]["dimension_scores"] == {"saludo": 90, "cierre": 90}
    assert detail["review"]["global_score"] == 50
    assert detail["review"]["comment"] == "No confirmó el importe de la cuota."


def test_revisar_dos_veces_actualiza_la_misma_revision(
    client, db_session, admin_user, auth_headers
):
    _rubric(db_session, {"saludo": 100.0})
    call = _done_call(db_session, admin_user.id, dims={"saludo": 80}, score=80)

    primera = client.put(
        f"/api/v1/calls/{call.id}/review",
        json={"dimension_scores": {"saludo": 50}},
        headers=auth_headers,
    ).json()
    segunda = client.put(
        f"/api/v1/calls/{call.id}/review",
        json={"dimension_scores": {"saludo": 70}, "comment": "Reconsiderado."},
        headers=auth_headers,
    ).json()

    assert primera["id"] == segunda["id"]
    assert segunda["global_score"] == 70
    assert segunda["comment"] == "Reconsiderado."


def test_no_se_puede_revisar_una_llamada_sin_analisis(
    client, db_session, admin_user, auth_headers
):
    call = Call(uploaded_by=admin_user.id, audio_url="x", status=CallStatus.QUEUED)
    db_session.add(call)
    db_session.commit()

    r = client.put(
        f"/api/v1/calls/{call.id}/review",
        json={"dimension_scores": {"saludo": 50}},
        headers=auth_headers,
    )
    assert r.status_code == 409


def test_scores_fuera_de_rango_se_rechazan(client, db_session, admin_user, auth_headers):
    _rubric(db_session, {"saludo": 100.0})
    call = _done_call(db_session, admin_user.id, dims={"saludo": 80}, score=80)

    r = client.put(
        f"/api/v1/calls/{call.id}/review",
        json={"dimension_scores": {"saludo": 120}},
        headers=auth_headers,
    )
    assert r.status_code == 422


def test_borrar_la_revision_deja_intacta_la_de_la_ia(
    client, db_session, admin_user, auth_headers
):
    _rubric(db_session, {"saludo": 100.0})
    call = _done_call(db_session, admin_user.id, dims={"saludo": 80}, score=80)
    client.put(
        f"/api/v1/calls/{call.id}/review",
        json={"dimension_scores": {"saludo": 40}},
        headers=auth_headers,
    )

    assert client.delete(f"/api/v1/calls/{call.id}/review", headers=auth_headers).status_code == 204

    detail = client.get(f"/api/v1/calls/{call.id}", headers=auth_headers).json()
    assert detail["review"] is None
    assert detail["analysis"]["global_score"] == 80


def test_el_asesor_no_puede_revisar(client, db_session, admin_user, asesor_headers):
    _rubric(db_session, {"saludo": 100.0})
    call = _done_call(db_session, admin_user.id, dims={"saludo": 80}, score=80)

    r = client.put(
        f"/api/v1/calls/{call.id}/review",
        json={"dimension_scores": {"saludo": 40}},
        headers=asesor_headers,
    )
    assert r.status_code == 403


def test_el_asesor_ve_la_revision_de_su_propia_llamada(
    client, db_session, admin_user, auth_headers, asesor_headers, asesor_user, sample_agent
):
    _rubric(db_session, {"saludo": 100.0})
    call = _done_call(
        db_session, admin_user.id, dims={"saludo": 80}, score=80, agent_id=sample_agent.id
    )
    client.put(
        f"/api/v1/calls/{call.id}/review",
        json={"dimension_scores": {"saludo": 60}, "comment": "Faltó despedida."},
        headers=auth_headers,
    )

    r = client.get(f"/api/v1/calls/{call.id}/review", headers=asesor_headers)
    assert r.status_code == 200
    assert r.json()["comment"] == "Faltó despedida."


# ===============================================================
# Sesión a ciegas
# ===============================================================
def test_la_cola_solo_trae_llamadas_sin_revisar(
    client, db_session, admin_user, auth_headers
):
    _rubric(db_session, {"saludo": 100.0})
    revisada = _done_call(db_session, admin_user.id, dims={"saludo": 80}, score=80)
    pendiente = _done_call(db_session, admin_user.id, dims={"saludo": 70}, score=70)
    client.put(
        f"/api/v1/calls/{revisada.id}/review",
        json={"dimension_scores": {"saludo": 75}},
        headers=auth_headers,
    )

    ids = [c["id"] for c in client.get("/api/v1/calibration/queue", headers=auth_headers).json()]
    assert pendiente.id in ids
    assert revisada.id not in ids


def test_la_llamada_a_ciegas_no_filtra_el_score_de_la_ia(
    client, db_session, admin_user, auth_headers
):
    """
    El requisito real de una sesión ciega: el score no puede llegar al cliente.
    Ocultarlo solo en la interfaz no serviría de nada.
    """
    _rubric(db_session, {"saludo": 100.0})
    call = _done_call(db_session, admin_user.id, dims={"saludo": 93}, score=93)

    r = client.get(f"/api/v1/calibration/calls/{call.id}", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert "analysis" not in body
    assert "93" not in r.text
    # Pero sí trae lo que hace falta para poder puntuar.
    assert body["transcription"]["full_text"] == "hola buenas tardes"


def test_a_ciegas_rechaza_una_llamada_sin_procesar(
    client, db_session, admin_user, auth_headers
):
    call = Call(uploaded_by=admin_user.id, audio_url="x", status=CallStatus.ANALYZING)
    db_session.add(call)
    db_session.commit()

    r = client.get(f"/api/v1/calibration/calls/{call.id}", headers=auth_headers)
    assert r.status_code == 409


# ===============================================================
# Panel de acuerdo
# ===============================================================
def test_acuerdo_separa_sesgo_de_desviacion_media(
    client, db_session, admin_user, auth_headers
):
    """
    Dos dimensiones diseñadas para contar historias opuestas:

    - `saludo`: el humano puntúa +20 en una llamada y −20 en la otra. El sesgo
      se cancela (0), pero la desviación media es 20: está mal calibrada.
    - `cierre`: coincide en las dos. Ni sesgo ni desviación.
    """
    _rubric(db_session, {"saludo": 50.0, "cierre": 50.0})
    a = _done_call(db_session, admin_user.id, dims={"saludo": 50, "cierre": 60}, score=55)
    b = _done_call(db_session, admin_user.id, dims={"saludo": 50, "cierre": 60}, score=55)

    client.put(
        f"/api/v1/calls/{a.id}/review",
        json={"dimension_scores": {"saludo": 70, "cierre": 60}, "blind": True},
        headers=auth_headers,
    )
    client.put(
        f"/api/v1/calls/{b.id}/review",
        json={"dimension_scores": {"saludo": 30, "cierre": 60}, "blind": True},
        headers=auth_headers,
    )

    data = client.get(
        "/api/v1/calibration/agreement", params={"period": "30d"}, headers=auth_headers
    ).json()

    assert data["reviews_count"] == 2
    por_clave = {d["dimension_key"]: d for d in data["dimensions"]}

    assert por_clave["saludo"]["bias"] == 0.0
    assert por_clave["saludo"]["mean_abs_diff"] == 20.0
    assert por_clave["saludo"]["agreement_pct"] == 0.0

    assert por_clave["cierre"]["mean_abs_diff"] == 0.0
    assert por_clave["cierre"]["agreement_pct"] == 100.0

    # La peor calibrada encabeza la lista: es la que hay que reescribir.
    assert data["dimensions"][0]["dimension_key"] == "saludo"
    assert data["worst_dimension"] == "saludo"


def test_acuerdo_puede_limitarse_a_las_revisiones_a_ciegas(
    client, db_session, admin_user, auth_headers
):
    _rubric(db_session, {"saludo": 100.0})
    ciega = _done_call(db_session, admin_user.id, dims={"saludo": 80}, score=80)
    con_vista = _done_call(db_session, admin_user.id, dims={"saludo": 80}, score=80)

    client.put(
        f"/api/v1/calls/{ciega.id}/review",
        json={"dimension_scores": {"saludo": 40}, "blind": True},
        headers=auth_headers,
    )
    client.put(
        f"/api/v1/calls/{con_vista.id}/review",
        json={"dimension_scores": {"saludo": 80}, "blind": False},
        headers=auth_headers,
    )

    todas = client.get("/api/v1/calibration/agreement", headers=auth_headers).json()
    solo_ciegas = client.get(
        "/api/v1/calibration/agreement",
        params={"blind_only": True},
        headers=auth_headers,
    ).json()

    assert todas["reviews_count"] == 2
    assert solo_ciegas["reviews_count"] == 1
    assert solo_ciegas["mean_abs_diff"] == 40.0


def test_acuerdo_sin_revisiones_no_revienta(client, auth_headers):
    data = client.get("/api/v1/calibration/agreement", headers=auth_headers).json()
    assert data["reviews_count"] == 0
    assert data["dimensions"] == []
    assert data["worst_dimension"] is None


def test_el_asesor_no_ve_el_panel_de_acuerdo(client, asesor_headers):
    r = client.get("/api/v1/calibration/agreement", headers=asesor_headers)
    assert r.status_code == 403
