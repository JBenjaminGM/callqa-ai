"""Schemas de llamadas (calls)."""

from datetime import date, datetime

from pydantic import BaseModel

from app.models.call import CallStatus
from app.schemas.analysis import AnalysisOut, TranscriptionOut


class AgentRef(BaseModel):
    """Referencia ligera a un ejecutivo dentro de una llamada."""

    id: int
    name: str
    campaign: str | None = None

    model_config = {"from_attributes": True}


class CallCreatedOut(BaseModel):
    """Respuesta tras subir una llamada (202 Accepted)."""

    id: int
    status: CallStatus
    agent_id: int | None = None
    estimated_completion_seconds: int = 180


class BatchCreatedOut(BaseModel):
    """Respuesta tras una subida en lote de llamadas."""

    created_ids: list[int]
    count: int


class AssignAgentRequest(BaseModel):
    """Petición para asignar (o reasignar) una llamada a un ejecutivo."""

    agent_id: int
    # Si es True, asigna también las demás llamadas sin asignar cuyo nombre
    # detectado coincida con el del ejecutivo.
    apply_to_same_name: bool = False


class CallStatusOut(BaseModel):
    """Estado del procesamiento de una llamada (para polling)."""

    id: int
    status: CallStatus
    progress_percent: int
    error_message: str | None = None


class CallListItem(BaseModel):
    """Una llamada tal como aparece en el listado paginado."""

    id: int
    # agent es None si la llamada aún no está asignada a un ejecutivo registrado.
    agent: AgentRef | None = None
    detected_agent_name: str | None = None
    call_date: date | None = None
    duration_seconds: int | None = None
    status: CallStatus
    global_score: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CallListOut(BaseModel):
    """Listado paginado de llamadas."""

    items: list[CallListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class CallDetailOut(BaseModel):
    """Detalle completo de una llamada: metadata + transcripción + análisis."""

    id: int
    agent: AgentRef | None = None
    detected_agent_name: str | None = None
    responsible: str | None = None
    audio_url: str
    audio_filename: str | None = None
    duration_seconds: int | None = None
    status: CallStatus
    language: str
    call_date: date | None = None
    campaign_type: str | None = None
    call_reason: str | None = None
    error_message: str | None = None
    created_at: datetime
    processed_at: datetime | None = None
    transcription: TranscriptionOut | None = None
    analysis: AnalysisOut | None = None

    model_config = {"from_attributes": True}
