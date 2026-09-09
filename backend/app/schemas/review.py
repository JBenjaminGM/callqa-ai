"""Schemas de la revisión humana y del panel de calibración."""

from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.analysis import TranscriptionOut


class ReviewIn(BaseModel):
    """Puntuación humana que se envía al guardar una revisión."""

    # {dimension_key: score 0-100}. Debe traer al menos una dimensión.
    dimension_scores: dict[str, int] = Field(min_length=1)
    comment: str | None = None
    # True si se puntuó sin ver la nota de la IA (sesión de calibración).
    blind: bool = False

    @field_validator("dimension_scores")
    @classmethod
    def _rango(cls, v: dict[str, int]) -> dict[str, int]:
        """Cada score debe estar entre 0 y 100."""
        for key, score in v.items():
            if not 0 <= score <= 100:
                raise ValueError(
                    f"El score de «{key}» debe estar entre 0 y 100 (llegó {score})."
                )
        return v


class ReviewOut(BaseModel):
    """Una revisión humana, con la nota de la IA al lado para compararlas."""

    id: int
    call_id: int
    reviewer_id: int | None = None
    reviewer_name: str | None = None
    global_score: int
    dimension_scores: dict[str, int]
    comment: str | None = None
    blind: bool
    created_at: datetime
    updated_at: datetime | None = None
    # --- La nota de la IA, para la comparación. Null si la llamada no la tiene. ---
    ai_global_score: int | None = None
    ai_dimension_scores: dict[str, int] | None = None
    # Diferencia humano − IA en el global y por dimensión.
    global_delta: int | None = None
    dimension_deltas: dict[str, int] | None = None

    model_config = {"from_attributes": True}


class CalibrationCallOut(BaseModel):
    """Una llamada pendiente de calibrar, en el listado de la cola."""

    id: int
    agent_name: str | None = None
    campaign: str | None = None
    call_date: date | None = None
    duration_seconds: int | None = None
    created_at: datetime


class BlindCallOut(BaseModel):
    """
    Una llamada para puntuar **a ciegas**.

    No incluye el análisis de la IA a propósito: si el score viajara al
    navegador, la sesión dejaría de ser ciega aunque la interfaz lo ocultara.
    """

    id: int
    agent_name: str | None = None
    campaign: str | None = None
    call_date: date | None = None
    duration_seconds: int | None = None
    audio_filename: str | None = None
    transcription: TranscriptionOut | None = None


class DimensionAgreement(BaseModel):
    """Acuerdo IA-humano en una dimensión concreta."""

    dimension_key: str
    dimension_name: str
    count: int
    human_avg: float | None = None
    ai_avg: float | None = None
    # Sesgo (humano − IA): negativo significa que la IA puntúa más alto.
    bias: float | None = None
    # Desviación media absoluta: cuánto se separan, sin cancelarse entre sí.
    mean_abs_diff: float = 0.0
    agreement_pct: float | None = None


class AgreementOut(BaseModel):
    """Panel de acuerdo entre la IA y las revisiones humanas."""

    reviews_count: int
    blind_only: bool
    tolerance: int
    human_avg: float | None = None
    ai_avg: float | None = None
    bias: float | None = None
    mean_abs_diff: float = 0.0
    agreement_pct: float | None = None
    dimensions: list[DimensionAgreement] = []
    worst_dimension: str | None = None
