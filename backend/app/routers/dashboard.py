"""Endpoints del dashboard: KPIs agregados del equipo y por ejecutivo."""

from collections import defaultdict
from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_manager
from app.models.agent import Agent
from app.models.analysis import Analysis
from app.models.call import Call, CallStatus
from app.models.user import User
from app.schemas.dashboard import (
    AgentDashboardOut,
    AgentScore,
    CallsByDay,
    DashboardSummaryOut,
    ScoreBucket,
    TimelinePoint,
)
from app.services.name_matching import normalize_name

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Días asociados a cada valor del parámetro `period`.
PERIOD_DAYS = {"7d": 7, "30d": 30, "90d": 90}


def _period_start(period: str) -> datetime:
    """Devuelve la fecha de inicio del periodo solicitado."""
    days = PERIOD_DAYS.get(period, 30)
    return datetime.utcnow() - timedelta(days=days)


def _done_analyses(
    db: Session,
    start: datetime,
    end: datetime | None = None,
    agent_id: int | None = None,
    campaign: str | None = None,
):
    """Devuelve las filas (Call, Analysis) DONE dentro de la ventana y los filtros."""
    query = (
        select(Call, Analysis)
        .join(Analysis, Analysis.call_id == Call.id)
        .where(Call.status == CallStatus.DONE, Call.created_at >= start)
    )
    if end is not None:
        query = query.where(Call.created_at <= end)
    if agent_id is not None:
        query = query.where(Call.agent_id == agent_id)
    if campaign:
        query = query.where(Call.campaign_type == campaign)
    return db.execute(query).all()


@router.get("/summary", response_model=DashboardSummaryOut)
def dashboard_summary(
    period: str = Query(default="30d", pattern="^(7d|30d|90d)$"),
    campaign: str | None = Query(default=None),
    agent_id: int | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    """KPIs agregados del equipo, con filtros de campaña, ejecutivo y rango de fechas."""
    # Ventana temporal: el rango de fechas tiene prioridad sobre el periodo rápido.
    end = datetime.combine(date_to, time.max) if date_to else datetime.utcnow()
    if date_from:
        start = datetime.combine(date_from, time.min)
    elif date_to:
        start = end - timedelta(days=PERIOD_DAYS.get(period, 30))
    else:
        start = _period_start(period)

    rows = _done_analyses(db, start, end=end, agent_id=agent_id, campaign=campaign)

    total_calls = len(rows)
    scores = [a.global_score for _, a in rows]
    average_score = round(sum(scores) / total_calls, 1) if total_calls else 0.0

    # Tendencia: compara la primera mitad de la ventana con la segunda.
    mid = start + (end - start) / 2
    first_half = [a.global_score for c, a in rows if c.created_at < mid]
    second_half = [a.global_score for c, a in rows if c.created_at >= mid]
    if first_half and second_half:
        delta = (sum(second_half) / len(second_half)) - (
            sum(first_half) / len(first_half)
        )
        score_trend = f"{'+' if delta >= 0 else ''}{delta:.1f}"
    else:
        score_trend = "+0.0"

    # Llamadas por día.
    by_day_count: dict[str, int] = defaultdict(int)
    by_day_scores: dict[str, list[int]] = defaultdict(list)
    for call, analysis in rows:
        day = call.created_at.strftime("%Y-%m-%d")
        by_day_count[day] += 1
        by_day_scores[day].append(analysis.global_score)
    calls_by_day = [
        CallsByDay(
            date=day,
            count=by_day_count[day],
            avg_score=round(sum(by_day_scores[day]) / len(by_day_scores[day]), 1),
        )
        for day in sorted(by_day_count)
    ]

    # Distribución de scores en 3 tramos (regla RN-03).
    buckets = {"0-59": 0, "60-79": 0, "80-100": 0}
    for score in scores:
        if score < 60:
            buckets["0-59"] += 1
        elif score < 80:
            buckets["60-79"] += 1
        else:
            buckets["80-100"] += 1
    score_distribution = [ScoreBucket(range=r, count=c) for r, c in buckets.items()]

    # Ranking de ejecutivos (reporte NPS). Las llamadas asignadas a un
    # ejecutivo registrado se agrupan por su id; las que solo tienen nombre
    # detectado por la IA se agrupan por ese nombre (normalizado).
    by_key: dict[str, list[int]] = defaultdict(list)
    key_meta: dict[str, dict] = {}
    for call, analysis in rows:
        if call.agent_id is not None:
            key = f"a:{call.agent_id}"
            if key not in key_meta:
                agent = db.get(Agent, call.agent_id)
                key_meta[key] = {
                    "agent_id": call.agent_id,
                    "name": agent.name if agent else f"Ejecutivo {call.agent_id}",
                    "registered": True,
                }
        elif call.detected_agent_name:
            key = f"d:{normalize_name(call.detected_agent_name)}"
            if key not in key_meta:
                key_meta[key] = {
                    "agent_id": None,
                    "name": call.detected_agent_name,
                    "registered": False,
                }
        else:
            key = "d:sin-identificar"
            key_meta.setdefault(
                key,
                {"agent_id": None, "name": "Sin identificar", "registered": False},
            )
        by_key[key].append(analysis.global_score)

    agent_avgs: list[AgentScore] = []
    for key, scores_list in by_key.items():
        meta = key_meta[key]
        agent_avgs.append(
            AgentScore(
                agent_id=meta["agent_id"],
                name=meta["name"],
                registered=meta["registered"],
                total_calls=len(scores_list),
                avg_score=round(sum(scores_list) / len(scores_list), 1),
            )
        )
    agent_avgs.sort(key=lambda a: a.avg_score, reverse=True)

    return DashboardSummaryOut(
        total_calls=total_calls,
        average_score=average_score,
        score_trend=score_trend,
        calls_by_day=calls_by_day,
        score_distribution=score_distribution,
        top_performers=agent_avgs[:5],
        improvement_opportunities=list(reversed(agent_avgs[-5:])),
    )


@router.get("/campaigns", response_model=list[str])
def list_campaigns(
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    """Lista las campañas distintas presentes en las llamadas (para los filtros)."""
    rows = db.scalars(
        select(Call.campaign_type)
        .where(Call.campaign_type.is_not(None), Call.campaign_type != "")
        .distinct()
        .order_by(Call.campaign_type)
    ).all()
    return list(rows)


@router.get("/agents/{agent_id}", response_model=AgentDashboardOut)
def agent_dashboard(
    agent_id: int,
    period: str = Query(default="30d", pattern="^(7d|30d|90d)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Performance detallado de un ejecutivo: dimensiones, tendencia y comparativa."""
    if not current_user.is_manager and current_user.agent_id != agent_id:
        raise HTTPException(status_code=403, detail="No autorizado para ver este ejecutivo.")
    agent = db.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Ejecutivo no encontrado.")

    since = _period_start(period)
    agent_rows = _done_analyses(db, since, agent_id=agent_id)
    team_rows = _done_analyses(db, since)

    total_calls = len(agent_rows)
    scores = [a.global_score for _, a in agent_rows]
    average_score = round(sum(scores) / total_calls, 1) if total_calls else 0.0

    def _dimension_averages(rows) -> dict[str, float]:
        """Promedia cada dimensión a partir de una lista de (Call, Analysis)."""
        sums: dict[str, float] = defaultdict(float)
        counts: dict[str, int] = defaultdict(int)
        for _, analysis in rows:
            for key, score in (analysis.dimension_scores or {}).items():
                sums[key] += score
                counts[key] += 1
        return {k: round(sums[k] / counts[k], 1) for k in sums}

    dimension_averages = _dimension_averages(agent_rows)
    team_dimension_averages = _dimension_averages(team_rows)

    # Fortalezas y áreas de mejora: top 3 y bottom 3 dimensiones.
    ordered = sorted(dimension_averages.items(), key=lambda kv: kv[1], reverse=True)
    strengths = [k for k, _ in ordered[:3]]
    improvement_areas = [k for k, _ in ordered[-3:]] if len(ordered) >= 3 else []

    # Tendencia temporal: score promedio por día.
    by_day: dict[str, list[int]] = defaultdict(list)
    for call, analysis in agent_rows:
        by_day[call.created_at.strftime("%Y-%m-%d")].append(analysis.global_score)
    timeline = [
        TimelinePoint(date=day, avg_score=round(sum(v) / len(v), 1))
        for day, v in sorted(by_day.items())
    ]

    # Tendencia (mismo cálculo que el resumen del equipo).
    mid = since + (datetime.utcnow() - since) / 2
    first = [a.global_score for c, a in agent_rows if c.created_at < mid]
    second = [a.global_score for c, a in agent_rows if c.created_at >= mid]
    if first and second:
        delta = (sum(second) / len(second)) - (sum(first) / len(first))
        score_trend = f"{'+' if delta >= 0 else ''}{delta:.1f}"
    else:
        score_trend = "+0.0"

    return AgentDashboardOut(
        agent={"id": agent.id, "name": agent.name, "campaign": agent.campaign},
        total_calls=total_calls,
        average_score=average_score,
        score_trend=score_trend,
        dimension_averages=dimension_averages,
        team_dimension_averages=team_dimension_averages,
        strengths=strengths,
        improvement_areas=improvement_areas,
        timeline=timeline,
    )
