"""Modelo de revisión humana de una nota (calibración)."""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    false as sa_false,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

# Tipo JSON portable: JSONB en PostgreSQL, JSON genérico en otras BD (tests SQLite).
JSONType = JSON().with_variant(JSONB(), "postgresql")


class Review(Base):
    """
    Puntuación humana de una llamada, guardada **junto a** la de la IA.

    La nota de la IA (`Analysis`) nunca se sobrescribe: son dos registros
    independientes sobre la misma llamada. Eso es lo que permite medir el
    acuerdo entre ambas, que es de lo que trata calibrar.

    Hay como mucho una revisión vigente por llamada (`call_id` es único): si
    el jefe corrige dos veces, la segunda actualiza la primera y queda
    constancia en `updated_at`.
    """

    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint(
            "global_score >= 0 AND global_score <= 100", name="ck_review_global_score"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[int] = mapped_column(
        ForeignKey("calls.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    # Quién revisó. Se conserva la llamada aunque se borre el usuario.
    reviewer_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Score global ponderado con la rúbrica vigente al guardar la revisión.
    global_score: Mapped[int] = mapped_column(Integer, nullable=False)
    # dimension_scores: {greeting: 85, assertiveness: 72, ...}
    dimension_scores: Mapped[dict] = mapped_column(JSONType, nullable=False)
    # Motivo de la corrección: por qué el humano puntúa distinto que la IA.
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    # True cuando se puntuó en una sesión de calibración a ciegas (sin ver la
    # nota de la IA). Solo esas revisiones son comparables sin sesgo de anclaje.
    blind: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=sa_false(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    call: Mapped["Call"] = relationship(back_populates="review")  # noqa: F821
    reviewer: Mapped["User | None"] = relationship()  # noqa: F821
