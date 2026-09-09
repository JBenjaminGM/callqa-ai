"""
Datos de demostración.

Siembra un histórico de 90 días de llamadas ya procesadas, para que quien abra
la plataforma por primera vez vea un panel con contenido en vez de vacío.

Qué genera:
- ~70 llamadas repartidas en 90 días, con más volumen en días laborables.
- Transcripción real de cada llamada, con sus tiempos exactos, y el archivo de
  audio correspondiente (lo que se oye coincide con lo que se lee).
- Notas por dimensión escritas a mano en `demo_conversations.py`, con una
  variación pequeña por llamada para que las gráficas no salgan planas.
- Tendencias con intención: María mejora, Lucía empeora y Carlos se mantiene.
  Así el ranking, las alertas y la evolución temporal cuentan algo.

No llama a la IA: funciona sin clave y sin coste, y siempre produce lo mismo
(la semilla del azar es fija).

Uso:  SEED_DEMO=true python scripts/seed_demo.py
      o bien:      python scripts/seed_demo.py --force
"""

import os
import random
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import select  # noqa: E402

import demo_conversations as guiones  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.models.agent import Agent  # noqa: E402
from app.models.analysis import Analysis  # noqa: E402
from app.models.call import Call, CallStatus  # noqa: E402
from app.models.campaign import Campaign  # noqa: E402
from app.models.transcription import Transcription  # noqa: E402
from app.models.user import ROLE_JEFE, User  # noqa: E402
from app.services.conversation_metrics_service import (  # noqa: E402
    compute_conversation_metrics,
)
from app.services.storage_service import get_storage_provider  # noqa: E402
from app.utils.security import hash_password  # noqa: E402

# Cuenta de demostración pública. Su contraseña se publica a propósito en el
# README: es de solo lectura, así que compartirla no compromete nada. Solo
# existe si se pide el seed de demostración, nunca en un despliegue normal.
DEMO_EMAIL = "demo@callaibrate.com"
DEMO_PASSWORD = os.getenv("SEED_DEMO_PASSWORD", "CallAIbrate-Demo-2026")

DIAS_DE_HISTORIAL = 90
LLAMADAS_OBJETIVO = 70
CARPETA_AUDIO = Path(__file__).resolve().parent.parent / "demo_audio"

# Cómo evoluciona cada ejecutivo a lo largo de los 90 días. El número es la
# probabilidad de que la llamada sea la "buena" al principio y al final del
# periodo; entre medias se interpola. Es lo que hace que la evolución temporal
# y las alertas de tendencia tengan algo que contar.
TENDENCIAS = {
    "María González": {"inicio": 0.15, "fin": 0.95},   # mejora mucho con el coaching
    "Carlos Ruiz": {"inicio": 0.74, "fin": 0.70},      # estable
    "Lucía Fernández": {"inicio": 0.95, "fin": 0.20},  # se deteriora
}

# Guiones disponibles por ejecutivo: (el que cumple, el que falla).
GUIONES_POR_EJECUTIVO = {
    "María González": ("tarjetas_alta", "tarjetas_baja"),
    "Carlos Ruiz": ("prestamos_alta", "prestamos_baja"),
    "Lucía Fernández": ("seguros_alta", "seguros_baja"),
}


def crear_usuario_demo(db) -> None:
    """Crea (o repara) la cuenta de demostración de solo lectura."""
    demo = db.scalar(select(User).where(User.email == DEMO_EMAIL))
    if demo is None:
        db.add(
            User(
                email=DEMO_EMAIL,
                password_hash=hash_password(DEMO_PASSWORD),
                name="Invitado (demostración)",
                role=ROLE_JEFE,
                is_readonly=True,
            )
        )
        print(f"[demo] Cuenta de demostración creada: {DEMO_EMAIL} / {DEMO_PASSWORD}")
    elif not demo.is_readonly:
        # Nunca dejar la cuenta pública con permiso de escritura.
        demo.is_readonly = True
        print("[demo] La cuenta de demostración se ha vuelto a marcar como solo lectura.")
    db.commit()


def _quiere_sembrar() -> bool:
    """El seed de demostración solo corre si se pide explícitamente."""
    if "--force" in sys.argv:
        return True
    return os.getenv("SEED_DEMO", "").strip().lower() in {"1", "true", "yes", "si", "sí"}


def _dias_con_llamadas(rng: random.Random) -> list[date]:
    """
    Reparte las llamadas por días, con más volumen entre semana.

    Un histórico uniforme se ve artificial; uno con picos y valles se lee como
    actividad real.
    """
    hoy = date.today()
    dias: list[date] = []
    for atras in range(DIAS_DE_HISTORIAL):
        dia = hoy - timedelta(days=atras)
        if dia.weekday() >= 5:          # fin de semana: casi nada
            cuantas = rng.choices([0, 1], weights=[85, 15])[0]
        else:
            cuantas = rng.choices([0, 1, 2], weights=[25, 45, 30])[0]
        dias.extend([dia] * cuantas)
    rng.shuffle(dias)
    return dias[:LLAMADAS_OBJETIVO]


def _probabilidad_de_buena(ejecutivo: str, dia: date) -> float:
    """Interpola la tendencia del ejecutivo según lo reciente que sea el día."""
    t = TENDENCIAS[ejecutivo]
    antiguedad = (date.today() - dia).days
    avance = 1 - (antiguedad / DIAS_DE_HISTORIAL)   # 0 = lo más antiguo, 1 = hoy
    return t["inicio"] + (t["fin"] - t["inicio"]) * avance


def _notas_con_variacion(base: dict[str, int], rng: random.Random) -> dict[str, int]:
    """
    Aparta las notas del guion para que la distribución no salga bimodal.

    Con solo dos guiones por ejecutivo, los scores se agolpan en dos picos y la
    banda intermedia queda vacía, que es justo lo que delata unos datos
    inventados. Se aplica un desplazamiento común a toda la llamada —una llamada
    entera sale mejor o peor, no cada criterio por su cuenta— más un ruido
    pequeño por criterio.
    """
    # El +6 sube el conjunto lo justo para que las llamadas flojas caigan en la
    # banda intermedia en vez de amontonarse todas en rojo.
    desplazamiento = 6 + rng.gauss(0, 8)
    return {
        clave: max(15, min(100, round(valor + desplazamiento + rng.gauss(0, 3))))
        for clave, valor in base.items()
    }


def _score_global(notas: dict[str, int], pesos: dict[str, float]) -> int:
    total_peso = sum(pesos.get(k, 0) for k in notas) or 1
    acumulado = sum(nota * pesos.get(clave, 0) for clave, nota in notas.items())
    return int(round(acumulado / total_peso))


def sembrar() -> None:
    rng = random.Random(20260909)     # semilla fija: siempre el mismo resultado
    db = SessionLocal()
    almacen = get_storage_provider()

    try:
        crear_usuario_demo(db)

        if db.scalar(select(Call).limit(1)) is not None:
            print("[demo] Ya hay llamadas en la base de datos. No se toca nada.")
            return

        admin = db.scalar(select(User).order_by(User.id))
        if admin is None:
            print("[demo] No hay usuarios. Ejecuta antes scripts/seed_data.py.")
            return

        ejecutivos = {a.name: a for a in db.scalars(select(Agent))}
        campanas = {c.name: c for c in db.scalars(select(Campaign))}
        faltan = set(GUIONES_POR_EJECUTIVO) - set(ejecutivos)
        if faltan:
            print(f"[demo] Faltan ejecutivos: {', '.join(sorted(faltan))}. Ejecuta seed_data.py.")
            return

        # Los pesos de la rúbrica se leen de la base: si el jefe los cambió,
        # los scores de la demo siguen siendo coherentes con su configuración.
        from app.models.settings import RubricConfig
        pesos = {
            r.dimension_key: float(r.weight)
            for r in db.scalars(select(RubricConfig))
        }

        # El audio se copia una sola vez al almacenamiento y se reutiliza: son
        # seis grabaciones para setenta llamadas, y ocupan seis veces menos.
        audios_guardados: dict[str, str] = {}
        for clave, conv in guiones.CONVERSACIONES.items():
            origen = CARPETA_AUDIO / conv["audio"]
            if not origen.exists():
                print(f"[demo] Falta el audio {origen.name}. Se siembra sin audio.")
                continue
            audios_guardados[clave] = almacen.save(origen.read_bytes(), conv["audio"])

        creadas = 0
        for dia in _dias_con_llamadas(rng):
            ejecutivo_nombre = rng.choice(list(GUIONES_POR_EJECUTIVO))
            agente = ejecutivos[ejecutivo_nombre]
            buena, mala = GUIONES_POR_EJECUTIVO[ejecutivo_nombre]
            clave = buena if rng.random() < _probabilidad_de_buena(ejecutivo_nombre, dia) else mala
            conv = guiones.CONVERSACIONES[clave]

            segmentos = guiones.construir_segmentos(clave)
            duracion = guiones.duracion_total(clave)
            momento = datetime.combine(
                dia, time(hour=rng.randint(9, 18), minute=rng.randint(0, 59))
            )

            llamada = Call(
                uploaded_by=admin.id,
                agent_id=agente.id,
                audio_url=audios_guardados.get(clave, f"demo://{conv['audio']}"),
                audio_filename=f"{dia.isoformat()}_{conv['audio']}",
                duration_seconds=duracion,
                language="es",
                status=CallStatus.DONE,
                detected_agent_name=conv["ejecutivo"],
                call_date=dia,
                campaign_type=conv["campana"],
                campaign_id=campanas[conv["campana"]].id if conv["campana"] in campanas else None,
                responsible="Datos de demostración",
                created_at=momento,
                processed_at=momento + timedelta(minutes=2),
                conversation_metrics=compute_conversation_metrics(segmentos, duracion),
            )
            db.add(llamada)
            db.flush()

            db.add(
                Transcription(
                    call_id=llamada.id,
                    full_text=guiones.texto_completo(clave),
                    segments=segmentos,
                    language="es",
                )
            )

            notas = _notas_con_variacion(conv["scores"], rng)
            db.add(
                Analysis(
                    call_id=llamada.id,
                    global_score=_score_global(notas, pesos),
                    dimension_scores=notas,
                    recommendations=conv["recomendaciones"],
                    summary=conv["resumen"],
                    ai_provider="demo",
                    ai_model="datos-de-demostracion",
                    created_at=momento + timedelta(minutes=2),
                )
            )
            creadas += 1

        db.commit()
        print(f"[demo] {creadas} llamadas de demostración creadas en {DIAS_DE_HISTORIAL} días.")
        print("[demo] Tendencias: María mejora · Carlos estable · Lucía se deteriora.")
    finally:
        db.close()


if __name__ == "__main__":
    if not _quiere_sembrar():
        print(
            "[demo] Omitido. Para sembrar datos de demostración usa SEED_DEMO=true "
            "o el argumento --force."
        )
    else:
        sembrar()
