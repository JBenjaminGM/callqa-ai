"""
Modelos ORM de CallQA AI.

Se importan todos aquí para que Alembic los detecte automáticamente
a través de Base.metadata.
"""

from app.models.base import Base
from app.models.user import User
from app.models.agent import Agent
from app.models.call import Call, CallStatus
from app.models.transcription import Transcription
from app.models.analysis import Analysis
from app.models.settings import AppSettings, RubricConfig

__all__ = [
    "Base",
    "User",
    "Agent",
    "Call",
    "CallStatus",
    "Transcription",
    "Analysis",
    "AppSettings",
    "RubricConfig",
]
