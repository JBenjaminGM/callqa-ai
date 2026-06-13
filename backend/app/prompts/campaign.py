"""Prompts para extraer y asistir notas de producto de campañas con el LLM."""

import json

from app.schemas.campaign import CAMPAIGN_FIELD_GUIDE


def _fields_guide() -> str:
    """Lista legible de los campos esperados y su significado."""
    return "\n".join(f'- "{key}": {desc}' for key, desc in CAMPAIGN_FIELD_GUIDE)


def _json_skeleton() -> str:
    """Esqueleto del JSON de salida con todas las claves esperadas."""
    from app.schemas.campaign import LIST_FIELDS

    parts = []
    for key, _ in CAMPAIGN_FIELD_GUIDE:
        placeholder = "[]" if key in LIST_FIELDS else "null"
        parts.append(f'  "{key}": {placeholder}')
    return "{\n" + ",\n".join(parts) + "\n}"


def build_extraction_prompt(document_text: str, language: str = "es") -> str:
    """Prompt para extraer la nota de producto estructurada desde el texto de un PDF."""
    return f"""Eres un asistente experto en campañas comerciales de banca. Te paso el
TEXTO de una nota de producto (la ficha de una oferta que un ejecutivo de call center
debe presentar a los clientes). Tu tarea es EXTRAER la información en un JSON estructurado.

TEXTO DE LA NOTA DE PRODUCTO:
\"\"\"
{document_text}
\"\"\"

Devuelve EXCLUSIVAMENTE un JSON válido con EXACTAMENTE estas claves:
{_fields_guide()}

Reglas:
- Usa el idioma del documento (por defecto español).
- Si un dato NO aparece en el texto, deja el valor en null (o en lista vacía [] para los campos de tipo lista). NO inventes datos.
- Los campos de tipo lista (key_benefits, mandatory_phrases, prohibited_claims) deben ser arrays de strings cortos.
- No añadas comentarios ni texto fuera del JSON.

Estructura de salida:
{_json_skeleton()}
"""


def build_assist_prompt(description: str, current: dict, language: str = "es") -> str:
    """Prompt para que la IA proponga/complete una nota de producto a partir de una descripción."""
    current_block = json.dumps(current or {}, ensure_ascii=False, indent=2)
    return f"""Eres un asistente experto en campañas comerciales de banca. Un responsable de
calidad quiere crear la NOTA DE PRODUCTO de una campaña (la ficha de la oferta que el
ejecutivo debe presentar). Te da una descripción y, opcionalmente, algunos campos ya
rellenados. Completa y mejora la nota de producto de forma profesional y realista.

DESCRIPCIÓN DE LA CAMPAÑA:
\"\"\"
{description}
\"\"\"

CAMPOS YA RELLENADOS (respétalos y mejóralos solo si aportas valor):
{current_block}

Devuelve EXCLUSIVAMENTE un JSON válido con EXACTAMENTE estas claves:
{_fields_guide()}

Reglas:
- Mantén la coherencia con la descripción dada; no contradigas los campos ya rellenados.
- Sé concreto y accionable: las frases obligatorias deben ser frases que el ejecutivo pueda decir literalmente.
- Los campos de tipo lista deben ser arrays de strings cortos.
- Si algún dato no se puede deducir razonablemente, déjalo en null (o []). No inventes cifras concretas (tasas, precios) si no se dan.
- No añadas texto fuera del JSON.

Estructura de salida:
{_json_skeleton()}
"""
