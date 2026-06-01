"""Schemas de configuración: rúbrica y settings globales."""

from pydantic import BaseModel, Field, model_validator


class RubricDimensionOut(BaseModel):
    """Una dimensión de la rúbrica."""

    dimension_key: str
    dimension_name: str
    description: str | None = None
    weight: float
    display_order: int | None = None

    model_config = {"from_attributes": True}


class RubricDimensionUpdate(BaseModel):
    """Datos editables de una dimensión de la rúbrica."""

    dimension_key: str
    weight: float = Field(ge=0, le=100)
    description: str | None = None


class RubricUpdateRequest(BaseModel):
    """Petición para actualizar toda la rúbrica. La suma de pesos debe ser 100."""

    dimensions: list[RubricDimensionUpdate]

    @model_validator(mode="after")
    def check_weights_sum_100(self) -> "RubricUpdateRequest":
        """Valida que los pesos sumen 100 (con tolerancia por redondeo)."""
        total = sum(d.weight for d in self.dimensions)
        if abs(total - 100.0) > 0.5:
            raise ValueError(
                f"La suma de los pesos debe ser 100%. Suma actual: {total:.2f}%."
            )
        return self


class SettingsOut(BaseModel):
    """Settings globales de la aplicación."""

    default_language: str
    ai_provider: str
    whisper_provider: str


class SettingsUpdate(BaseModel):
    """Campos de settings que se pueden actualizar."""

    default_language: str | None = None
    ai_provider: str | None = None
    whisper_provider: str | None = None
