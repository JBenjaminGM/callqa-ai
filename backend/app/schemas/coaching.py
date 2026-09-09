"""Schemas del cierre del ciclo: acuse de recibo y a quién escuchar hoy."""

from datetime import date, datetime

from pydantic import BaseModel, Field


class AcknowledgementIn(BaseModel):
    """Lo que el asesor envía al responder a una evaluación."""

    comment: str | None = None
    # True si además pide que un jefe revise la nota.
    review_requested: bool = False


class ManagerReplyIn(BaseModel):
    """Respuesta del jefe a una petición de revisión."""

    reply: str = Field(min_length=1)


class AcknowledgementOut(BaseModel):
    """El acuse de recibo de una llamada, con la respuesta del jefe si la hay."""

    id: int
    call_id: int
    user_id: int | None = None
    user_name: str | None = None
    comment: str | None = None
    review_requested: bool
    manager_reply: str | None = None
    replied_by_name: str | None = None
    replied_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
    # True mientras el asesor pidió revisión y nadie ha contestado.
    pending_review: bool = False

    model_config = {"from_attributes": True}


class ListenSuggestionOut(BaseModel):
    """Una llamada que merece escucharse, con el motivo por el que sale."""

    call_id: int
    agent_id: int | None = None
    agent_name: str | None = None
    campaign: str | None = None
    score: int | None = None
    call_date: date | None = None
    # review_requested | red_unreviewed | below_own_average | never_reviewed_agent
    reason: str
    priority: str
    title: str
    description: str


class PendingCallOut(BaseModel):
    """Una llamada evaluada de la que el asesor todavía no ha acusado recibo."""

    call_id: int
    global_score: int
    call_date: date | None = None
    campaign: str | None = None
    created_at: datetime
