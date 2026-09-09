"""Modelo del acuse de recibo del asesor sobre una evaluación."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    false as sa_false,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Acknowledgement(Base):
    """
    Lo que el asesor responde a la evaluación de una de sus llamadas.

    Sin esto la evaluación es un monólogo: el asesor ve su nota y no puede
    hacer nada con ella. Aquí puede dar por leída la evaluación, explicarse y
    —si no está de acuerdo— pedir que la revise su jefe, que contesta en el
    mismo sitio. Eso es lo que cierra el ciclo.

    Uno por llamada: si el asesor vuelve a escribir, actualiza el suyo.
    """

    __tablename__ = "acknowledgements"

    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[int] = mapped_column(
        ForeignKey("calls.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    # El asesor que acusa recibo.
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    # True si además pide que un jefe revise la nota.
    review_requested: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=sa_false(), nullable=False, index=True
    )
    # --- Respuesta del jefe. Mientras esté vacía, la petición sigue abierta. ---
    manager_reply: Mapped[str | None] = mapped_column(Text, nullable=True)
    replied_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    replied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    call: Mapped["Call"] = relationship(back_populates="acknowledgement")  # noqa: F821
    user: Mapped["User | None"] = relationship(foreign_keys=[user_id])  # noqa: F821
    replier: Mapped["User | None"] = relationship(foreign_keys=[replied_by])  # noqa: F821

    @property
    def pending_review(self) -> bool:
        """La petición de revisión sigue abierta si nadie ha contestado."""
        return self.review_requested and self.replied_at is None
