"""
Enmascaramiento de datos sensibles.

Antes de enviar cualquier transcripción a un LLM externo, se ocultan
números de tarjeta, DNI peruano, CVV y teléfonos. Así la IA nunca
recibe datos personales en claro (requisito de seguridad RNF-07).
"""

import re

# Cada patrón: (regex compilada, texto de reemplazo).
PATTERNS: dict[str, tuple[re.Pattern, str]] = {
    "card": (re.compile(r"\b\d{13,19}\b"), "[TARJETA]"),
    "cvv": (re.compile(r"\bcvv\s*:?\s*\d{3,4}\b", re.IGNORECASE), "cvv: [CVV]"),
    "phone": (re.compile(r"\b9\d{8}\b"), "[TELEFONO]"),
    "dni_peru": (re.compile(r"\b\d{8}\b"), "[DNI]"),
}


def mask_sensitive_data(text: str) -> str:
    """
    Devuelve el texto con los datos sensibles enmascarados.

    El orden importa: primero tarjetas (13-19 dígitos) y teléfonos,
    luego DNI (8 dígitos), para no enmascarar de más.
    """
    if not text:
        return text
    for pattern, replacement in PATTERNS.values():
        text = pattern.sub(replacement, text)
    return text
