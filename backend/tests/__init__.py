"""
Paquete de tests.

Se importa antes que `conftest.py`, así que es el sitio correcto para fijar el
entorno ANTES de que `app.config` construya los Settings: los tests corren como
entorno de test, no de producción, y con un JWT_SECRET propio. Sin esto, el
guardarraíl de `app.main` abortaría el arranque en una máquina sin `.env`.
"""

import os

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("JWT_SECRET", "clave-solo-para-tests-no-usar-en-produccion")
