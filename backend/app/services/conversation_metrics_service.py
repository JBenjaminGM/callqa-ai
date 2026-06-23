"""
Métricas de conversación derivadas de los segmentos de la transcripción.

Todo se calcula de forma DETERMINISTA en Python a partir de
`Transcription.segments` = [{start, end, speaker, text}] — sin llamadas a la IA,
coste $0. Se persisten en `Call.conversation_metrics` durante el pipeline y, para
llamadas antiguas sin el campo, se recalculan al vuelo desde la transcripción.

Métricas expuestas:
- talk-to-listen ratio (agente vs cliente) y % de tiempo de cada hablante,
- % de silencio / dead-air dentro de la conversación,
- monólogo más largo del agente (segundos que retiene el turno seguido),
- palabras por minuto (del agente y global),
- turnos por minuto (cambios de hablante).
"""

from __future__ import annotations


def _is_agent(speaker: object) -> bool:
    """True si la etiqueta de hablante corresponde al ejecutivo ('agent')."""
    return str(speaker or "").strip().lower().startswith("a")


def _word_count(text: object) -> int:
    """Número de palabras de un texto (separadas por espacios)."""
    return len(str(text or "").split())


def compute_conversation_metrics(
    segments: list[dict] | None, duration_seconds: int | float | None = None
) -> dict | None:
    """
    Calcula las métricas de conversación a partir de los segmentos diarizados.

    Devuelve un diccionario serializable a JSON, o ``None`` si no hay segmentos
    con tiempos utilizables (no se puede medir nada fiable).
    """
    if not segments:
        return None

    # Normaliza y ordena por tiempo de inicio; descarta segmentos sin tiempos.
    clean: list[dict] = []
    for seg in segments:
        try:
            start = float(seg.get("start"))
            end = float(seg.get("end"))
        except (TypeError, ValueError):
            continue
        if end < start:
            start, end = end, start
        clean.append(
            {
                "start": start,
                "end": end,
                "is_agent": _is_agent(seg.get("speaker")),
                "words": _word_count(seg.get("text")),
            }
        )
    if not clean:
        return None
    clean.sort(key=lambda s: s["start"])

    first_start = clean[0]["start"]
    last_end = max(s["end"] for s in clean)
    # Ventana de conversación: desde el primer hasta el último segmento. Es la
    # base más honesta para silencio/ritmo (excluye silencios de cabecera/cola).
    span = max(last_end - first_start, 0.0)
    if duration_seconds:
        span = max(span, float(duration_seconds))

    agent_talk = sum(s["end"] - s["start"] for s in clean if s["is_agent"])
    customer_talk = sum(s["end"] - s["start"] for s in clean if not s["is_agent"])
    total_speech = agent_talk + customer_talk

    agent_words = sum(s["words"] for s in clean if s["is_agent"])
    total_words = sum(s["words"] for s in clean)

    # --- Silencio / dead-air: huecos entre segmentos consecutivos ---
    # (no se solapan; si dos segmentos se pisan, el hueco es 0).
    silence = 0.0
    prev_end = clean[0]["end"]
    for seg in clean[1:]:
        gap = seg["start"] - prev_end
        if gap > 0:
            silence += gap
        prev_end = max(prev_end, seg["end"])

    # --- Monólogo más largo del agente (racha contigua sin que hable el cliente) ---
    longest_monologue = 0.0
    run_start: float | None = None
    run_end: float | None = None
    for seg in clean:
        if seg["is_agent"]:
            if run_start is None:
                run_start, run_end = seg["start"], seg["end"]
            else:
                run_end = max(run_end or seg["end"], seg["end"])
        else:
            if run_start is not None and run_end is not None:
                longest_monologue = max(longest_monologue, run_end - run_start)
            run_start = run_end = None
    if run_start is not None and run_end is not None:
        longest_monologue = max(longest_monologue, run_end - run_start)

    # --- Turnos: cambios de hablante (incluye el primer turno) ---
    turns = 1
    for i in range(1, len(clean)):
        if clean[i]["is_agent"] != clean[i - 1]["is_agent"]:
            turns += 1

    minutes = span / 60.0 if span > 0 else 0.0
    agent_minutes = agent_talk / 60.0 if agent_talk > 0 else 0.0

    def _pct(part: float, whole: float) -> float:
        return round(part / whole * 100, 1) if whole > 0 else 0.0

    return {
        "duration_seconds": round(span, 1),
        "agent_talk_seconds": round(agent_talk, 1),
        "customer_talk_seconds": round(customer_talk, 1),
        "total_speech_seconds": round(total_speech, 1),
        "agent_talk_pct": _pct(agent_talk, total_speech),
        "customer_talk_pct": _pct(customer_talk, total_speech),
        # Ratio hablar/escuchar del agente: >1 habla más que el cliente.
        "talk_to_listen_ratio": (
            round(agent_talk / customer_talk, 2) if customer_talk > 0 else None
        ),
        "silence_seconds": round(silence, 1),
        "silence_pct": _pct(silence, span),
        "longest_agent_monologue_seconds": round(longest_monologue, 1),
        "agent_words_per_minute": (
            round(agent_words / agent_minutes) if agent_minutes > 0 else None
        ),
        "overall_words_per_minute": (
            round(total_words / minutes) if minutes > 0 else None
        ),
        "turns": turns,
        "turns_per_minute": round(turns / minutes, 1) if minutes > 0 else None,
        "segments_count": len(clean),
    }
