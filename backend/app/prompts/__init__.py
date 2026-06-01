"""
Prompts para los modelos de lenguaje.

`get_analysis_prompt` selecciona el prompt según el idioma configurado.
"""

from app.prompts.analysis_en import build_analysis_prompt as _build_en
from app.prompts.analysis_es import build_analysis_prompt as _build_es


def get_analysis_prompt(segments: list[dict], rubric: list[dict], language: str) -> str:
    """Devuelve el prompt de análisis en el idioma indicado (es por defecto).

    `segments` es la lista de segmentos (con 'text' ya enmascarado).
    """
    if language.lower().startswith("en"):
        return _build_en(segments, rubric)
    return _build_es(segments, rubric)
