"""Modelo de campaña con su nota de producto (oferta que el ejecutivo debe presentar)."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.settings import JSONType


class Campaign(Base):
    """
    Una campaña comercial y su **nota de producto**.

    La nota de producto es la plantilla de referencia que describe la oferta que
    el ejecutivo DEBE presentar. La IA la usa al evaluar cada llamada asignada a
    la campaña para comprobar si se ofreció el producto correcto y en las
    condiciones correctas.
    """

    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)

    # --- Nota de producto (estructura completa) ---
    product_service: Mapped[str | None] = mapped_column(String(200), nullable=True)
    offer_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    key_benefits: Mapped[list | None] = mapped_column(JSONType, nullable=True, default=list)
    pricing_conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    customer_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    mandatory_phrases: Mapped[list | None] = mapped_column(JSONType, nullable=True, default=list)
    prohibited_claims: Mapped[list | None] = mapped_column(JSONType, nullable=True, default=list)
    target_audience: Mapped[str | None] = mapped_column(String(300), nullable=True)
    additional_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Origen / metadatos ---
    # source: "form" (rellenada a mano/IA) | "pdf" (extraída de un PDF) | "migrated".
    source: Mapped[str] = mapped_column(String(20), default="form")
    source_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    calls: Mapped[list["Call"]] = relationship(back_populates="campaign")  # noqa: F821
