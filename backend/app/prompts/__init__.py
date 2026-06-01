"""
Prompts para los modelos de lenguaje.

`get_analysis_prompt` selecciona el prompt según el idioma configurado.
"""

from app.prompts.analysis_en import build_analysis_prompt as _build_en
from app.prompts.analysis_es import build_analysis_prompt as _build_es


def get_analysis_prompt(transcription_text: str, rubric: list[dict], language: str) -> str:
    """Devuelve el prompt de análisis en el idioma indicado (es por defecto)."""
    if language.lower().startswith("en"):
        return _build_en(transcription_text, rubric)
    return _build_es(transcription_text, rubric)
