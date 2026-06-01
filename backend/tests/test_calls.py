"""Tests de subida de llamadas, cálculo de score y enmascaramiento."""

import io
from types import SimpleNamespace

from app.services.analysis_service import calculate_global_score
from app.services.masking_service import mask_sensitive_data
from app.services.name_matching import find_matching_agent, normalize_name
from app.services.transcription_service import add_speaker_diarization


# ---------------------------------------------------------------
# Cálculo del score global
# ---------------------------------------------------------------
def test_calculate_global_score_equal_weights():
    """Con pesos iguales, el score global es el promedio de las dimensiones."""
    scores = {"a": 80, "b": 60, "c": 100}
    rubric = {"a": 33.34, "b": 33.33, "c": 33.33}
    result = calculate_global_score(scores, rubric)
    assert 79 <= result <= 81  # ~80


def test_calculate_global_score_weighted():
    """El peso de cada dimensión influye en el score global."""
    scores = {"a": 100, "b": 0}
    rubric = {"a": 90.0, "b": 10.0}
    assert calculate_global_score(scores, rubric) == 90


def test_calculate_global_score_clamped():
    """El score global nunca supera 100 ni baja de 0."""
    scores = {"a": 100}
    rubric = {"a": 100.0}
    assert calculate_global_score(scores, rubric) == 100


# ---------------------------------------------------------------
# Enmascaramiento de datos sensibles
# ---------------------------------------------------------------
def test_mask_card_number():
    """Un número de tarjeta se reemplaza por [TARJETA]."""
    text = "Mi tarjeta es 4532015112830366 gracias"
    masked = mask_sensitive_data(text)
    assert "4532015112830366" not in masked
    assert "[TARJETA]" in masked


def test_mask_dni():
    """Un DNI peruano de 8 dígitos se reemplaza por [DNI]."""
    masked = mask_sensitive_data("Mi DNI es 12345678")
    assert "12345678" not in masked
    assert "[DNI]" in masked


def test_mask_keeps_normal_text():
    """El texto sin datos sensibles no se modifica."""
    text = "Buenos días, ¿en qué le puedo ayudar?"
    assert mask_sensitive_data(text) == text


# ---------------------------------------------------------------
# Diarización por pausas (heurística de fallback)
# ---------------------------------------------------------------
def test_diarization_first_speaker_is_agent():
    """El primer segmento siempre se asigna al ejecutivo (agent)."""
    segments = [{"start": 0.0, "end": 2.0, "text": "Hola"}]
    result = add_speaker_diarization(segments)
    assert result[0]["speaker"] == "agent"


def test_diarization_switches_on_long_pause():
    """Una pausa larga cambia el hablante."""
    segments = [
        {"start": 0.0, "end": 2.0, "text": "Hola"},
        {"start": 5.0, "end": 7.0, "text": "Buenos días"},  # pausa de 3s
    ]
    result = add_speaker_diarization(segments)
    assert result[0]["speaker"] == "agent"
    assert result[1]["speaker"] == "customer"


# ---------------------------------------------------------------
# Subida de llamada (servicios externos mockeados)
# ---------------------------------------------------------------
def test_upload_call(client, auth_headers, monkeypatch):
    """Subir un audio crea la llamada SIN ejecutivo asignado (lo detecta la IA)."""
    # Mockea el encolado de Celery para no necesitar Redis en los tests.
    calls_encolados = []
    monkeypatch.setattr(
        "app.routers.calls.process_call.delay",
        lambda call_id: calls_encolados.append(call_id),
    )

    dummy_audio = io.BytesIO(b"contenido de audio de prueba")
    response = client.post(
        "/api/v1/calls",
        headers=auth_headers,
        files={"audio": ("prueba.mp3", dummy_audio, "audio/mpeg")},
        data={"campaign": "Tarjetas Premium", "comment": "Lote de prueba"},
    )
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "QUEUED"
    assert body["agent_id"] is None
    assert len(calls_encolados) == 1


def test_upload_batch(client, auth_headers, monkeypatch):
    """La subida en lote crea una llamada por archivo."""
    monkeypatch.setattr(
        "app.routers.calls.process_call.delay", lambda call_id: None
    )
    response = client.post(
        "/api/v1/calls/batch",
        headers=auth_headers,
        files=[
            ("audios", ("a.mp3", io.BytesIO(b"audio uno"), "audio/mpeg")),
            ("audios", ("b.mp3", io.BytesIO(b"audio dos"), "audio/mpeg")),
        ],
        data={"campaign": "Préstamos", "responsible": "Jefe QA"},
    )
    assert response.status_code == 202
    body = response.json()
    assert body["count"] == 2
    assert len(body["created_ids"]) == 2


def test_upload_call_invalid_format(client, auth_headers, monkeypatch):
    """Subir un archivo con formato no soportado devuelve 400."""
    monkeypatch.setattr(
        "app.routers.calls.process_call.delay", lambda call_id: None
    )
    response = client.post(
        "/api/v1/calls",
        headers=auth_headers,
        files={"audio": ("documento.txt", io.BytesIO(b"texto"), "text/plain")},
        data={"campaign": "Préstamos"},
    )
    assert response.status_code == 400


# ---------------------------------------------------------------
# Emparejamiento difuso de nombres de ejecutivos
# ---------------------------------------------------------------
def test_normalize_name_quita_tildes():
    """La normalización quita tildes y pasa a minúsculas."""
    assert normalize_name("  Juan  PÉREZ ") == "juan perez"


def test_match_con_errata():
    """Un nombre con errata ('Juan Perz') empareja con 'Juan Pérez'."""
    agents = [SimpleNamespace(name="Juan Pérez"), SimpleNamespace(name="Ana Torres")]
    match, score = find_matching_agent("Juan Perz", agents)
    assert match is not None
    assert match.name == "Juan Pérez"
    assert score >= 0.82


def test_match_sin_coincidencia():
    """Un nombre totalmente distinto no empareja con ningún ejecutivo."""
    agents = [SimpleNamespace(name="Juan Pérez")]
    match, _ = find_matching_agent("Roberto Salas", agents)
    assert match is None


def test_list_calls_empty(client, auth_headers):
    """El listado de llamadas vacío devuelve total 0."""
    response = client.get("/api/v1/calls", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 0


# ---------------------------------------------------------------
# Enmascaramiento endurecido (formatos reales de transcripción de voz)
# ---------------------------------------------------------------
def test_mask_card_with_dashes():
    """Tarjeta con guiones (como la formatea Whisper) -> [TARJETA]."""
    masked = mask_sensitive_data("es 4532-0151-1283-0366 gracias")
    assert "4532" not in masked
    assert "[TARJETA]" in masked


def test_mask_card_with_spaces():
    """Tarjeta en grupos de 4 separados por espacios -> [TARJETA]."""
    masked = mask_sensitive_data("es 4532 0151 1283 0366 gracias")
    assert "0366" not in masked
    assert "[TARJETA]" in masked


def test_mask_spoken_number_words():
    """Un número dictado en palabras (>=7 seguidas) -> [NUMERO]."""
    text = "es cuatro cinco tres dos cero uno cinco uno uno dos ocho tres"
    masked = mask_sensitive_data(text)
    assert "[NUMERO]" in masked
    assert "cuatro cinco" not in masked


def test_mask_does_not_touch_few_number_words():
    """Pocas palabras-número en lenguaje normal NO se enmascaran."""
    text = "tengo dos hijos y tres mascotas"
    assert mask_sensitive_data(text) == text


# ---------------------------------------------------------------
# Idempotencia del pipeline: reintentar no debe romper por UNIQUE(call_id)
# ---------------------------------------------------------------
def test_pipeline_retry_is_idempotent(monkeypatch):
    """Reprocesar una llamada borra los resultados previos y termina en DONE."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    import app.tasks.call_tasks as ct
    from app.models import Analysis, Base, Call, CallStatus, RubricConfig, Transcription, User

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    TS = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    class _Storage:
        def load(self, url):
            return b"x"

        def save(self, content, filename):
            return "f"

        def delete(self, url):
            pass

    class _Trans:
        async def transcribe(self, path, language):
            return {
                "text": "Le atiende Ana.",
                "segments": [{"start": 0.0, "end": 1.0, "text": "Le atiende Ana."}],
            }

    class _An:
        async def analyze(self, prompt):
            return {
                "detected_agent_name": "Ana",
                "dimension_scores": {"greeting": 80},
                "summary": "ok",
                "recommendations": [],
                "ai_model": "x",
                "tokens_used": 1,
            }

    monkeypatch.setattr(ct, "SessionLocal", TS)
    monkeypatch.setattr(ct, "get_storage_provider", lambda: _Storage())
    monkeypatch.setattr(ct, "get_transcription_provider", lambda: _Trans())
    monkeypatch.setattr(ct, "get_analysis_provider", lambda: _An())

    s = TS()
    s.add(User(email="u@u.com", password_hash="x", name="U", role="supervisor"))
    s.flush()
    s.add(RubricConfig(dimension_key="greeting", dimension_name="Saludo", weight=100.0, display_order=1))
    call = Call(uploaded_by=1, audio_url="f", audio_filename="a.mp3", language="es", status=CallStatus.QUEUED)
    s.add(call)
    s.commit()
    call_id = call.id
    s.close()

    ct.process_call(call_id)  # primer procesamiento
    ct.process_call(call_id)  # reintento: NO debe romper

    chk = TS()
    reloaded = chk.get(Call, call_id)
    n_trans = chk.query(Transcription).filter_by(call_id=call_id).count()
    n_analysis = chk.query(Analysis).filter_by(call_id=call_id).count()
    chk.close()

    assert reloaded.status == CallStatus.DONE
    assert n_trans == 1
    assert n_analysis == 1
