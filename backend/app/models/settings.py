"""Modelos de configuración: rúbrica de evaluación y settings globales."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RubricConfig(Base):
    """Una dimensión de la rúbrica de evaluación con su peso porcentual."""

    __tablename__ = "rubric_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    dimension_key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    dimension_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # weight: peso porcentual; la suma de todas las dimensiones debe ser 100.00
    weight: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    display_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class AppSettings(Base):
    """Pares clave-valor para configuración global (idioma, proveedor IA, etc.)."""

    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
