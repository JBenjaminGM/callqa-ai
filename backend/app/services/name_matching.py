"""
Emparejamiento difuso de nombres de ejecutivos.

La IA detecta el nombre del ejecutivo en la transcripción, pero ese nombre
puede venir con errores ("Juan Perz" en lugar de "Juan Pérez"), sin tildes
o con mayúsculas distintas. Este módulo normaliza y compara nombres para
decidir si el nombre detectado corresponde a un ejecutivo ya registrado.
"""

import unicodedata
from difflib import SequenceMatcher

# Umbral de similitud (0-1) a partir del cual dos nombres se consideran
# la misma persona. 0.82 tolera erratas pequeñas sin emparejar de más.
MATCH_THRESHOLD = 0.82


def normalize_name(name: str) -> str:
    """
    Normaliza un nombre para comparar: minúsculas, sin tildes ni espacios extra.

    Ej: "  Juan  PÉREZ " -> "juan perez"
    """
    if not name:
        return ""
    # Elimina las marcas diacríticas (tildes, diéresis).
    nfkd = unicodedata.normalize("NFKD", name)
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c))
    # Minúsculas y espacios colapsados.
    return " ".join(sin_tildes.lower().split())


def name_similarity(a: str, b: str) -> float:
    """Devuelve la similitud (0-1) entre dos nombres ya normalizados."""
    return SequenceMatcher(None, a, b).ratio()


def find_matching_agent(detected_name: str, agents: list) -> tuple[object | None, float]:
    """
    Busca el ejecutivo registrado que mejor coincide con el nombre detectado.

    `agents` es una lista de objetos con atributo `name`.
    Devuelve (agente, similitud). Si ninguno supera el umbral, devuelve (None, mejor_similitud).
    """
    if not detected_name:
        return None, 0.0

    target = normalize_name(detected_name)
    best_agent = None
    best_score = 0.0

    for agent in agents:
        score = name_similarity(target, normalize_name(agent.name))
        if score > best_score:
            best_score = score
            best_agent = agent

    if best_score >= MATCH_THRESHOLD:
        return best_agent, best_score
    return None, best_score
