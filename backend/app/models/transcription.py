"""Modelo de transcripción de una llamada (relación 1:1 con Call)."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

# Tipo JSON portable: JSONB en PostgreSQL, JSON genérico en otras BD (tests con SQLite).
JSONType = JSON().with_variant(JSONB(), "postgresql")


class Transcription(Base):
    """Texto transcrito de una llamada, con segmentos y timestamps."""

    __tablename__ = "transcriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[int] = mapped_column(
        ForeignKey("calls.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    # segments: lista de objetos {start, end, speaker, text}
    segments: Mapped[list | None] = mapped_column(JSONType, nullable=True)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    call: Mapped["Call"] = relationship(back_populates="transcription")  # noqa: F821
