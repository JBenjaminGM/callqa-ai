"""
Enmascaramiento de datos sensibles.

Antes de enviar una transcripción a un LLM externo se intentan ocultar números
de tarjeta, DNI, CVV y teléfonos. Cubre las tres formas en que aparecen en una
transcripción real de voz:
  - dígitos seguidos:            "4532015112830366"
  - dígitos con separadores:     "4532-0151-1283-0366" / "4532 0151 1283 0366"
  - dígitos DICTADOS en palabras: "cuatro cinco tres dos cero uno ..."

⚠️ LIMITACIÓN: es un filtro *best-effort*, NO una garantía de cumplimiento.
Puede no captar todos los formatos y puede sobre-enmascarar números legítimos
(importes, referencias). Además, el AUDIO original se envía íntegro al proveedor
de transcripción (Groq/Azure), por lo que el dato sensible sale del perímetro de
todas formas. La protección real exige transcripción on-premise/Azure y la
validación de DPO/CISO (ver docs/01_VISION_Y_CASOS_DE_USO.md, sección 7).
"""

import re

# Palabra de un solo dígito en español (para números dictados).
_DIGIT_WORD = r"(?:cero|uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve)"

# Lista ORDENADA de (regex, reemplazo). El orden importa: primero los números
# dictados en palabras y las tarjetas (las secuencias más largas), luego CVV,
# teléfono y, por último, DNI (8 dígitos).
PATTERNS: list[tuple[re.Pattern, str]] = [
    # Secuencia larga (>= 7) de dígitos DICTADOS como palabras -> tarjeta/DNI/tel.
    (
        re.compile(rf"\b(?:{_DIGIT_WORD}[\s,.;:-]+){{6,}}{_DIGIT_WORD}\b", re.IGNORECASE),
        "[NUMERO]",
    ),
    # Tarjeta: 13-19 dígitos, admitiendo espacios o guiones entre ellos.
    (re.compile(r"\b\d(?:[ \-]?\d){12,18}\b"), "[TARJETA]"),
    # CVV: 3-4 dígitos precedidos de "cvv" o "código (de seguridad)".
    (
        re.compile(
            r"\b(?:cvv|c[oó]digo(?:\s+de\s+seguridad)?)\s*:?\s*\d{3,4}\b",
            re.IGNORECASE,
        ),
        "[CVV]",
    ),
    # Teléfono móvil peruano: 9 dígitos que empiezan por 9.
    (re.compile(r"\b9\d{8}\b"), "[TELEFONO]"),
    # DNI peruano: 8 dígitos.
    (re.compile(r"\b\d{8}\b"), "[DNI]"),
]


def mask_sensitive_data(text: str) -> str:
    """Devuelve el texto con los datos sensibles enmascarados (best-effort)."""
    if not text:
        return text
    for pattern, replacement in PATTERNS:
        text = pattern.sub(replacement, text)
    return text
