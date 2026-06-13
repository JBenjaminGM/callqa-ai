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
from app.models.campaign import Campaign  # noqa: E402
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

# Campañas de ejemplo con su nota de producto (la oferta que el ejecutivo debe
# presentar). Coinciden con las campañas de los ejecutivos demo.
CAMPAIGNS = [
    {
        "name": "Tarjetas Premium",
        "product_service": "Tarjeta de crédito Premium",
        "offer_description": (
            "Tarjeta de crédito Premium sin cuota de mantenimiento el primer año, "
            "con beneficios exclusivos de viajes y compras."
        ),
        "key_benefits": [
            "Sin cuota de mantenimiento el primer año",
            "2% de cashback en todas las compras",
            "Acceso a salas VIP de aeropuerto",
            "Seguro de viaje incluido",
        ],
        "pricing_conditions": (
            "TEA desde 39.9%. Cuota de mantenimiento de S/ 25 al mes a partir del "
            "segundo año. Línea de crédito sujeta a evaluación."
        ),
        "customer_requirements": "Ingresos mínimos de S/ 3,000 mensuales y buen historial crediticio.",
        "mandatory_phrases": [
            "Informar la Tasa Efectiva Anual (TEA)",
            "Mencionar que la aprobación está sujeta a evaluación crediticia",
        ],
        "prohibited_claims": [
            "No afirmar que la tarjeta es gratuita de por vida",
            "No garantizar la aprobación inmediata",
        ],
        "target_audience": "Clientes con ingresos medios-altos y buen perfil crediticio.",
    },
    {
        "name": "Préstamos",
        "product_service": "Préstamo personal de libre disponibilidad",
        "offer_description": (
            "Préstamo personal con desembolso rápido y cuotas fijas mensuales."
        ),
        "key_benefits": [
            "Desembolso en 24 horas",
            "Cuotas fijas mensuales",
            "Sin penalidad por pago anticipado",
        ],
        "pricing_conditions": "TEA desde 29.9% según perfil. Plazos de 6 a 48 meses.",
        "customer_requirements": "Antigüedad laboral mínima de 6 meses e ingresos demostrables.",
        "mandatory_phrases": [
            "Informar la TEA y el monto total a pagar",
            "Indicar el número de cuotas y su importe",
        ],
        "prohibited_claims": ["No prometer tasas que no estén aprobadas"],
        "target_audience": "Clientes dependientes o independientes con ingresos demostrables.",
    },
    {
        "name": "Seguros",
        "product_service": "Seguro de protección financiera",
        "offer_description": (
            "Seguro de protección financiera que cubre al titular ante imprevistos "
            "como desempleo o incapacidad."
        ),
        "key_benefits": [
            "Cobertura ante desempleo o incapacidad",
            "Primas accesibles",
            "Activación inmediata",
        ],
        "pricing_conditions": "Prima mensual desde S/ 15 según la cobertura elegida.",
        "customer_requirements": "Ser titular de un producto del banco.",
        "mandatory_phrases": [
            "Explicar las exclusiones de la cobertura",
            "Mencionar el periodo de carencia",
        ],
        "prohibited_claims": ["No afirmar que cubre cualquier situación sin excepciones"],
        "target_audience": "Clientes con productos activos que buscan protección financiera.",
    },
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

        # --- Campañas de ejemplo con su nota de producto ---
        for camp in CAMPAIGNS:
            existing = db.scalar(select(Campaign).where(Campaign.name == camp["name"]))
            if existing is None:
                db.add(Campaign(**camp))
            elif not existing.offer_description:
                # La campaña ya existía pero sin nota (p.ej. creada por el backfill
                # de la migración): se rellenan SOLO sus campos vacíos.
                for key, value in camp.items():
                    if key != "name" and not getattr(existing, key, None):
                        setattr(existing, key, value)
        print("[seed] Campañas de ejemplo verificadas.")

        db.commit()
        print("[seed] Datos iniciales cargados correctamente.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
