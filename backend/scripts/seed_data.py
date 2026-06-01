"""
Script de datos iniciales (seed).

Crea, de forma idempotente (no duplica si ya existen):
- Un usuario administrador.
- Las 7 dimensiones de la rúbrica de evaluación.
- Los settings globales por defecto.
- 3 ejecutivos de ejemplo.

Uso:  python scripts/seed_data.py
"""

import sys
from datetime import date
from pathlib import Path

# Permite ejecutar el script directamente (añade la raíz del proyecto al path).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.models.agent import Agent  # noqa: E402
from app.models.settings import AppSettings, RubricConfig  # noqa: E402
from app.models.user import User  # noqa: E402
from app.utils.security import hash_password  # noqa: E402

# Credenciales del usuario admin de demo.
ADMIN_EMAIL = "admin@callqa.com"
ADMIN_PASSWORD = "Admin123!"

# Las 7 dimensiones de la rúbrica (regla de negocio RN-01).
RUBRIC = [
    ("greeting", "Saludo y protocolo de apertura/cierre", 14.28, 1),
    ("assertiveness", "Asertividad y tono", 14.28, 2),
    ("promotions", "Mención correcta de promociones/productos", 14.28, 3),
    ("compliance", "Cumplimiento normativo", 14.28, 4),
    ("resolution", "Resolución efectiva del motivo", 14.28, 5),
    ("objections", "Manejo de objeciones", 14.28, 6),
    ("sentiment", "Detección de sentimiento del cliente", 14.32, 7),
]

# Subcriterios (subcategorías) por defecto de cada dimensión. Cada uno se puede
# activar/desactivar desde Configuración; la IA solo evalúa los activos.
CRITERIA = {
    "greeting": ["Saludo inicial", "Identificación del ejecutivo y banco", "Aviso de grabación", "Despedida y cierre"],
    "assertiveness": ["Empatía", "Claridad al explicar", "Paciencia", "Escucha activa", "Tono profesional"],
    "promotions": ["Menciona productos relevantes", "Explica beneficios", "Condiciones claras y completas"],
    "compliance": ["Disclaimers obligatorios", "Protección de datos sensibles", "Solicitud de consentimiento"],
    "resolution": ["Atiende el motivo de la llamada", "Ofrece solución concreta", "Confirma la resolución"],
    "objections": ["Identifica la objeción", "Responde con argumentos", "Persuasión profesional"],
    "sentiment": ["Satisfacción percibida", "Tono emocional del cliente", "Cierre en positivo"],
}

SETTINGS = {
    "default_language": "es",
    "ai_provider": "groq",
    "whisper_provider": "groq",
}

AGENTS = [
    ("María González", "maria@banco.com", "Tarjetas Premium", date(2024, 1, 15)),
    ("Carlos Ruiz", "carlos@banco.com", "Préstamos", date(2024, 3, 1)),
    ("Lucía Fernández", "lucia@banco.com", "Seguros", date(2023, 11, 20)),
]


def seed() -> None:
    """Inserta los datos iniciales si aún no existen."""
    db = SessionLocal()
    try:
        # --- Usuario admin ---
        if db.scalar(select(User).where(User.email == ADMIN_EMAIL)) is None:
            db.add(
                User(
                    email=ADMIN_EMAIL,
                    password_hash=hash_password(ADMIN_PASSWORD),
                    name="Administrador",
                    role="supervisor",
                )
            )
            print(f"[seed] Usuario admin creado: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        else:
            print("[seed] El usuario admin ya existía.")

        # --- Rúbrica ---
        for key, name, weight, order in RUBRIC:
            default_criteria = [{"name": c, "enabled": True} for c in CRITERIA.get(key, [])]
            existing = db.scalar(
                select(RubricConfig).where(RubricConfig.dimension_key == key)
            )
            if existing is None:
                db.add(
                    RubricConfig(
                        dimension_key=key,
                        dimension_name=name,
                        weight=weight,
                        display_order=order,
                        criteria=default_criteria,
                    )
                )
            elif not existing.criteria:
                # Backfill: si la dimensión ya existía sin subcriterios, los añade.
                existing.criteria = default_criteria
        print("[seed] Rúbrica de 7 dimensiones verificada.")

        # --- Settings globales ---
        for key, value in SETTINGS.items():
            if db.get(AppSettings, key) is None:
                db.add(AppSettings(key=key, value=value))
        print("[seed] Settings globales verificados.")

        # --- Ejecutivos de ejemplo ---
        for name, email, campaign, start in AGENTS:
            if db.scalar(select(Agent).where(Agent.email == email)) is None:
                db.add(
                    Agent(name=name, email=email, campaign=campaign, start_date=start)
                )
        print("[seed] Ejecutivos de ejemplo verificados.")

        db.commit()
        print("[seed] Datos iniciales cargados correctamente.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
