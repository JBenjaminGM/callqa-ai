"""Endpoints de gestión de ejecutivos (agents)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.agent import (
    AgentCreate,
    AgentCreatedOut,
    AgentDetailOut,
    AgentOut,
    AgentUpdate,
)
from app.services import agent_service

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentOut])
def list_agents(
    active: bool | None = Query(default=None),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Lista los ejecutivos, con filtros opcionales por estado y nombre."""
    return agent_service.list_agents(db, active=active, search=search)


@router.post("", response_model=AgentCreatedOut, status_code=status.HTTP_201_CREATED)
def create_agent(
    payload: AgentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Crea un nuevo ejecutivo.

    Si la IA ya había detectado su nombre en llamadas previas sin asignar,
    esas llamadas se le vinculan automáticamente (campo `linked_calls`).
    """
    try:
        agent, linked = agent_service.create_agent(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    result = AgentCreatedOut.model_validate(agent)
    result.linked_calls = linked
    return result


@router.get("/{agent_id}", response_model=AgentDetailOut)
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Devuelve el detalle de un ejecutivo con sus estadísticas."""
    agent = agent_service.get_agent(db, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Ejecutivo no encontrado.")

    total, avg = agent_service.get_agent_stats(db, agent_id)
    detail = AgentDetailOut.model_validate(agent)
    detail.total_calls = total
    detail.average_score = avg
    return detail


@router.put("/{agent_id}", response_model=AgentOut)
def update_agent(
    agent_id: int,
    payload: AgentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Actualiza los datos de un ejecutivo."""
    agent = agent_service.get_agent(db, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Ejecutivo no encontrado.")
    try:
        return agent_service.update_agent(db, agent, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Desactiva un ejecutivo (soft delete)."""
    agent = agent_service.get_agent(db, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Ejecutivo no encontrado.")
    agent_service.deactivate_agent(db, agent)
    return None
