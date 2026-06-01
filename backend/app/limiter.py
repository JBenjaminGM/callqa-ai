"""
Rate limiter compartido (slowapi).

Se define en su propio módulo para que tanto `main.py` como los routers
puedan importarlo sin provocar importaciones circulares.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# La clave del límite es la IP del cliente.
limiter = Limiter(key_func=get_remote_address)
