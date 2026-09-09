"""
Endpoints del cierre del ciclo de coaching.

- `/calls/{id}/acknowledgement` — el asesor responde a la evaluación de su
  llamada y, si no está de acuerdo, pide revisión. El jefe contesta con
  `/reply`.
- `/coaching/pending` — las peticiones abiertas, para el jefe.
- `/coaching/my-pending` — lo que el asesor tiene por leer.
- `/coaching/who-to-listen` — qué llamada poner ahora y por qué.
"""

from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_manager
from app.models.acknowledgement import Acknowledgement
from app.models.call import Call
from app.models.user import User
from app.routers.config import read_qa_thresholds
from app.schemas.coaching import (
    AcknowledgementIn,
    AcknowledgementOut,
    ListenSuggestionOut,
    ManagerReplyIn,
    PendingCallOut,
)
from app.services import coaching_service, dashboard_service as ds

router = APIRouter(tags=["coaching"])


def _get_call(db: Session, call_id: int) -> Call:
    call = db.get(Call, call_id)
    if call is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Llamada no encontrada."
        )
    return call


def _ensure_can_view(current_user: User, call: Call) -> None:
    """Un asesor solo accede a sus propias llamadas; un manager a todas."""
    if not current_user.is_manager and call.agent_id != current_user.agent_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado para ver esta llamada.",
        )


def build_ack_out(ack: Acknowledgement) -> AcknowledgementOut:
    """Compone la respuesta añadiendo los nombres de las personas implicadas."""
    return AcknowledgementOut(
        id=ack.id,
        call_id=ack.call_id,
        user_id=ack.user_id,
        user_name=ack.user.name if ack.user else None,
        comment=ack.comment,
        review_requested=ack.review_requested,
        manager_reply=ack.manager_reply,
        replied_by_name=ack.replier.name if ack.replier else None,
        replied_at=ack.replied_at,
        created_at=ack.created_at,
        updated_at=ack.updated_at,
        pending_review=ack.pending_review,
    )


# ------------------------ Acuse de recibo del asesor ------------------------


@router.get("/calls/{call_id}/acknowledgement", response_model=AcknowledgementOut | None)
def get_acknowledgement(
    call_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Devuelve el acuse de recibo de la llamada, o `null` si no lo hay."""
    call = _get_call(db, call_id)
    _ensure_can_view(current_user, call)
    if call.acknowledgement is None:
        return None
    return build_ack_out(call.acknowledgement)


@router.put("/calls/{call_id}/acknowledgement", response_model=AcknowledgementOut)
def upsert_acknowledgement(
    call_id: int,
    payload: AcknowledgementIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    El asesor da por leída la evaluación y, si quiere, pide revisión.

    Lo firma **quien la recibió**, no un jefe en su nombre: un acuse de recibo
    ajeno no significaría nada. Por eso solo puede hacerlo el asesor asignado a
    la llamada.
    """
    call = _get_call(db, call_id)

    if call.agent_id is None or call.agent_id != current_user.agent_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el asesor evaluado puede responder a esta evaluación.",
        )
    if call.analysis is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta llamada todavía no tiene evaluación a la que responder.",
        )

    ack = call.acknowledgement
    if ack is None:
        ack = Acknowledgement(call_id=call.id)
        db.add(ack)

    ack.user_id = current_user.id
    ack.comment = payload.comment
    # Reabrir la petición borra la respuesta anterior: si el asesor vuelve a
    # pedir revisión, la conversación se reanuda y no queda cerrada de antes.
    if payload.review_requested and not ack.review_requested:
        ack.manager_reply = None
        ack.replied_by = None
        ack.replied_at = None
    ack.review_requested = payload.review_requested

    db.commit()
    db.refresh(ack)
    return build_ack_out(ack)


@router.post(
    "/calls/{call_id}/acknowledgement/reply", response_model=AcknowledgementOut
)
def reply_to_acknowledgement(
    call_id: int,
    payload: ManagerReplyIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """El jefe contesta a la petición de revisión y con eso la cierra."""
    call = _get_call(db, call_id)
    ack = call.acknowledgement
    if ack is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El asesor todavía no ha respondido a esta evaluación.",
        )

    ack.manager_reply = payload.reply
    ack.replied_by = current_user.id
    ack.replied_at = datetime.now()

    db.commit()
    db.refresh(ack)
    return build_ack_out(ack)


# ------------------------------- Listados ----------------------------------


@router.get("/coaching/pending", response_model=list[AcknowledgementOut])
def pending_requests(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    """Peticiones de revisión abiertas: alguien está esperando respuesta."""
    return [
        build_ack_out(a) for a in coaching_service.pending_review_requests(db, limit)
    ]


@router.get("/coaching/my-pending", response_model=list[PendingCallOut])
def my_pending(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Evaluaciones del asesor de las que aún no ha acusado recibo."""
    if current_user.agent_id is None:
        return []
    return [
        PendingCallOut(
            call_id=call.id,
            global_score=analysis.global_score,
            call_date=call.call_date,
            campaign=call.campaign_type,
            created_at=call.created_at,
        )
        for call, analysis in coaching_service.unacknowledged_for_agent(
            db, current_user.agent_id, limit
        )
    ]


@router.get("/coaching/who-to-listen", response_model=list[ListenSuggestionOut])
def who_to_listen(
    period: str = Query("30d", pattern="^(7d|30d|90d)$"),
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    _: User = Depends(require_manager),
):
    """Qué llamadas escuchar ahora y por qué. Es con lo que abre el panel."""
    start, end = ds.resolve_window(period, date_from, date_to)
    thresholds = read_qa_thresholds(db)
    return [
        ListenSuggestionOut(**s)
        for s in coaching_service.who_to_listen(db, start, end, thresholds, limit)
    ]
