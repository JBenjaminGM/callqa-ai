"""Schemas del análisis IA y la transcripción."""

from pydantic import BaseModel


class Recommendation(BaseModel):
    """Una recomendación accionable generada por la IA."""

    priority: str          # high | medium | low
    dimension: str
    title: str
    description: str


class TranscriptionSegment(BaseModel):
    """Un segmento de la transcripción con timestamps y hablante."""

    start: float
    end: float
    speaker: str           # agent | customer
    text: str


class TranscriptionOut(BaseModel):
    """Transcripción completa de una llamada."""

    full_text: str
    segments: list[TranscriptionSegment] = []
    language: str | None = None

    model_config = {"from_attributes": True}


class AnalysisOut(BaseModel):
    """Resultado del análisis IA de una llamada."""

    global_score: int
    dimension_scores: dict[str, int]
    recommendations: list[Recommendation] = []
    summary: str | None = None
    ai_provider: str | None = None
    ai_model: str | None = None
    team_average: dict[str, float] | None = None

    model_config = {"from_attributes": True}
