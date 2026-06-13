"""Endpoints de gestión de campañas y notas de producto."""

import os

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.campaign import (
    CampaignAssistOut,
    CampaignAssistRequest,
    CampaignCreate,
    CampaignExtractOut,
    CampaignOut,
    CampaignUpdate,
)
from app.services import campaign_service

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

# Tamaño máximo de un PDF de nota de producto.
MAX_PDF_BYTES = 15 * 1024 * 1024


def _to_out(db: Session, campaign) -> CampaignOut:
    """Convierte un modelo Campaign a su schema de salida con el contador de llamadas."""
    out = CampaignOut.model_validate(campaign)
    out.calls_count = campaign_service.count_calls(db, campaign.id)
    return out


@router.get("", response_model=list[CampaignOut])
def list_campaigns(
    active: bool | None = Query(default=None),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Lista las campañas, con filtros opcionales por estado y nombre."""
    campaigns = campaign_service.list_campaigns(db, active=active, search=search)
    return [_to_out(db, c) for c in campaigns]


@router.post("", response_model=CampaignOut, status_code=status.HTTP_201_CREATED)
def create_campaign(
    payload: CampaignCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Crea una campaña con su nota de producto."""
    try:
        campaign = campaign_service.create_campaign(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return _to_out(db, campaign)


@router.post("/extract", response_model=CampaignExtractOut)
def extract_campaign_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Analiza un PDF de nota de producto y devuelve la nota estructurada.

    No persiste nada: el frontend revisa el borrador, completa los campos que
    falten (`missing_fields`) y luego llama a POST /campaigns para crearla.
    """
    content = file.file.read()
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser un PDF (.pdf).",
        )
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El PDF está vacío."
        )
    if len(content) > MAX_PDF_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El PDF supera el tamaño máximo de {MAX_PDF_BYTES // (1024 * 1024)} MB.",
        )

    draft, missing, warning = campaign_service.extract_from_pdf(
        content, settings.app_default_language
    )
    return CampaignExtractOut(
        draft=draft,
        missing_fields=missing,
        source_filename=file.filename,
        warning=warning,
    )


@router.post("/assist", response_model=CampaignAssistOut)
def assist_campaign(
    payload: CampaignAssistRequest,
    _: User = Depends(get_current_user),
):
    """Usa la IA para completar la nota de producto a partir de una descripción."""
    draft, warning = campaign_service.assist(
        payload.description, payload.current, settings.app_default_language
    )
    return CampaignAssistOut(draft=draft, warning=warning)


@router.get("/{campaign_id}", response_model=CampaignOut)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Devuelve el detalle de una campaña."""
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaña no encontrada.")
    return _to_out(db, campaign)


@router.put("/{campaign_id}", response_model=CampaignOut)
def update_campaign(
    campaign_id: int,
    payload: CampaignUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Actualiza una campaña y su nota de producto."""
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaña no encontrada.")
    try:
        campaign = campaign_service.update_campaign(db, campaign, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return _to_out(db, campaign)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Desactiva una campaña (soft delete)."""
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaña no encontrada.")
    campaign_service.deactivate_campaign(db, campaign)
    return None
