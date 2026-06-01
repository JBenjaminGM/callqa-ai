"""Validación de archivos de audio subidos."""

import os

from app.config import settings

# Formatos de audio soportados (regla de negocio RN-05).
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}


def get_extension(filename: str) -> str:
    """Devuelve la extensión del archivo en minúsculas (incluyendo el punto)."""
    return os.path.splitext(filename or "")[1].lower()


def validate_audio_file(filename: str, size_bytes: int) -> None:
    """
    Valida formato y tamaño de un audio.

    Lanza ValueError con un mensaje claro en español si el archivo no es válido.
    """
    ext = get_extension(filename)
    if ext not in ALLOWED_EXTENSIONS:
        permitidos = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValueError(
            f"Formato de audio no soportado ('{ext or 'sin extensión'}'). "
            f"Formatos permitidos: {permitidos}."
        )

    if size_bytes > settings.max_audio_size_bytes:
        raise ValueError(
            f"El archivo es demasiado grande ({size_bytes / 1_048_576:.1f} MB). "
            f"El tamaño máximo permitido es {settings.app_max_audio_size_mb} MB."
        )

    if size_bytes == 0:
        raise ValueError("El archivo de audio está vacío.")
