"""Schemas del dashboard y reportes agregados."""

from pydantic import BaseModel


class CallsByDay(BaseModel):
    """Conteo y score medio de llamadas en un día."""

    date: str
    count: int
    avg_score: float | None = None


class ScoreBucket(BaseModel):
    """Un tramo de la distribución de scores."""

    range: str
    count: int


class AgentScore(BaseModel):
    """
    Score promedio de un ejecutivo en el ranking del reporte NPS.

    agent_id es None cuando el ejecutivo fue detectado por la IA pero aún
    no está registrado en el sistema.
    """

    agent_id: int | None = None
    name: str
    avg_score: float
    total_calls: int = 0
    registered: bool = True


class DashboardSummaryOut(BaseModel):
    """KPIs agregados del equipo para el dashboard principal."""

    total_calls: int
    average_score: float
    score_trend: str
    calls_by_day: list[CallsByDay]
    score_distribution: list[ScoreBucket]
    top_performers: list[AgentScore]
    improvement_opportunities: list[AgentScore]


class TimelinePoint(BaseModel):
    """Un punto de la evolución temporal de un ejecutivo."""

    date: str
    avg_score: float


class AgentDashboardOut(BaseModel):
    """Performance detallado de un ejecutivo."""

    agent: dict
    total_calls: int
    average_score: float
    score_trend: str
    dimension_averages: dict[str, float]
    team_dimension_averages: dict[str, float]
    strengths: list[str]
    improvement_areas: list[str]
    timeline: list[TimelinePoint]
