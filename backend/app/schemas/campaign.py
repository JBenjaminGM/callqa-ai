"""Schemas de campañas y su nota de producto."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

# Guía de campos de la nota de producto: clave -> descripción para el LLM.
# El orden define también el orden de presentación en el formulario.
CAMPAIGN_FIELD_GUIDE: list[tuple[str, str]] = [
    ("name", "nombre corto de la campaña"),
    ("product_service", "producto o servicio principal que se ofrece"),
    ("offer_description", "descripción de la oferta: en qué consiste y qué se le propone al cliente"),
    ("key_benefits", "lista de beneficios clave para el cliente (array de strings)"),
    ("pricing_conditions", "precio, tasas, comisiones, plazos y condiciones económicas"),
    ("customer_requirements", "requisitos que debe cumplir el cliente para acceder a la oferta"),
    ("mandatory_phrases", "lista de frases o partes del script que el ejecutivo DEBE mencionar sí o sí (array de strings)"),
    ("prohibited_claims", "lista de afirmaciones prohibidas o restricciones legales que el ejecutivo NO debe decir (array de strings)"),
    ("target_audience", "público objetivo al que va dirigida la campaña"),
    ("additional_notes", "cualquier otra información relevante de la oferta"),
]

# Campos cuyo valor es una lista de strings.
LIST_FIELDS = {"key_benefits", "mandatory_phrases", "prohibited_claims"}

# Campos que se consideran imprescindibles para que la nota esté "completa".
# Si tras leer un PDF alguno falta, el formulario lo pedirá explícitamente.
CORE_FIELDS = [
    "name",
    "product_service",
    "offer_description",
    "key_benefits",
    "pricing_conditions",
    "mandatory_phrases",
]


class CampaignDraft(BaseModel):
    """Borrador de nota de producto (todos los campos opcionales).

    Se usa como salida de la extracción desde PDF y de la asistencia por IA: la
    IA rellena lo que encuentra y deja en null/[] lo que no.
    """

    name: str | None = None
    product_service: str | None = None
    offer_description: str | None = None
    key_benefits: list[str] | None = None
    pricing_conditions: str | None = None
    customer_requirements: str | None = None
    mandatory_phrases: list[str] | None = None
    prohibited_claims: list[str] | None = None
    target_audience: str | None = None
    additional_notes: str | None = None


class CampaignBase(BaseModel):
    """Campos comunes de una campaña."""

    name: str = Field(min_length=1, max_length=150)
    product_service: str | None = Field(default=None, max_length=200)
    offer_description: str | None = None
    key_benefits: list[str] = Field(default_factory=list)
    pricing_conditions: str | None = None
    customer_requirements: str | None = None
    mandatory_phrases: list[str] = Field(default_factory=list)
    prohibited_claims: list[str] = Field(default_factory=list)
    target_audience: str | None = Field(default=None, max_length=300)
    additional_notes: str | None = None

    @field_validator(
        "key_benefits", "mandatory_phrases", "prohibited_claims", mode="before"
    )
    @classmethod
    def _none_to_list(cls, v):
        """Las filas migradas pueden tener NULL en las listas: se normalizan a []."""
        return v or []


class CampaignCreate(CampaignBase):
    """Datos para crear una campaña."""

    source: str = "form"
    source_filename: str | None = None


class CampaignUpdate(BaseModel):
    """Datos para actualizar una campaña (todos los campos opcionales)."""

    name: str | None = Field(default=None, min_length=1, max_length=150)
    product_service: str | None = Field(default=None, max_length=200)
    offer_description: str | None = None
    key_benefits: list[str] | None = None
    pricing_conditions: str | None = None
    customer_requirements: str | None = None
    mandatory_phrases: list[str] | None = None
    prohibited_claims: list[str] | None = None
    target_audience: str | None = Field(default=None, max_length=300)
    additional_notes: str | None = None
    active: bool | None = None


class CampaignOut(CampaignBase):
    """Representación de una campaña en las respuestas."""

    id: int
    source: str
    source_filename: str | None = None
    active: bool
    created_at: datetime
    calls_count: int = 0

    model_config = {"from_attributes": True}


class CampaignExtractOut(BaseModel):
    """Resultado de analizar un PDF de nota de producto."""

    draft: CampaignDraft
    # Campos imprescindibles que la IA no logró encontrar en el documento.
    missing_fields: list[str] = Field(default_factory=list)
    source_filename: str | None = None
    # Aviso cuando la extracción no pudo completarse (se cae al formulario manual).
    warning: str | None = None


class CampaignAssistRequest(BaseModel):
    """Petición para que la IA ayude a completar una nota de producto."""

    description: str = Field(min_length=1)
    current: CampaignDraft | None = None


class CampaignAssistOut(BaseModel):
    """Sugerencia de la IA para completar la nota de producto."""

    draft: CampaignDraft
    warning: str | None = None
