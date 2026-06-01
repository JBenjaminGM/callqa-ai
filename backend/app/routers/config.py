"""Endpoints de configuración: rúbrica de evaluación y settings globales."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.settings import AppSettings, RubricConfig
from app.models.user import User
from app.schemas.config import (
    RubricDimensionOut,
    RubricUpdateRequest,
    SettingsOut,
    SettingsUpdate,
)

router = APIRouter(prefix="/config", tags=["config"])

# Claves de settings gestionadas y sus valores por defecto.
SETTINGS_DEFAULTS = {
    "default_language": "es",
    "ai_provider": "claude",
    "whisper_provider": "groq",
}


@router.get("/rubric", response_model=list[RubricDimensionOut])
def get_rubric(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Devuelve las 7 dimensiones de la rúbrica con sus pesos."""
    rows = db.scalars(
        select(RubricConfig).order_by(RubricConfig.display_order)
    ).all()
    return rows


@router.put("/rubric", response_model=list[RubricDimensionOut])
def update_rubric(
    payload: RubricUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Actualiza los pesos (y descripciones) de la rúbrica. La suma debe ser 100%."""
    for dim in payload.dimensions:
        row = db.scalar(
            select(RubricConfig).where(RubricConfig.dimension_key == dim.dimension_key)
        )
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dimensión desconocida: {dim.dimension_key}",
            )
        row.weight = dim.weight
        if dim.description is not None:
            row.description = dim.description

    db.commit()
    return db.scalars(
        select(RubricConfig).order_by(RubricConfig.display_order)
    ).all()


@router.get("/settings", response_model=SettingsOut)
def get_settings_endpoint(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Devuelve los settings globales actuales."""
    rows = {s.key: s.value for s in db.scalars(select(AppSettings)).all()}
    return SettingsOut(
        default_language=rows.get("default_language", SETTINGS_DEFAULTS["default_language"]),
        ai_provider=rows.get("ai_provider", SETTINGS_DEFAULTS["ai_provider"]),
        whisper_provider=rows.get("whisper_provider", SETTINGS_DEFAULTS["whisper_provider"]),
    )


@router.put("/settings", response_model=SettingsOut)
def update_settings_endpoint(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Actualiza uno o varios settings globales."""
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in changes.items():
        row = db.get(AppSettings, key)
        if row is None:
            db.add(AppSettings(key=key, value=value))
        else:
            row.value = value
    db.commit()
    return get_settings_endpoint(db=db, _=None)  # type: ignore[arg-type]
