"""Clase base declarativa para todos los modelos ORM (SQLAlchemy 2.0)."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base común de la que heredan todas las tablas del sistema."""

    pass
