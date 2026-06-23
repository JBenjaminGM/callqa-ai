"""
Comprobación determinista del cumplimiento de la NOTA DE PRODUCTO de una campaña.

Dada la transcripción diarizada de una llamada y la campaña asignada, comprueba:
- **Frases obligatorias**: si el ejecutivo cubrió (de forma aproximada) cada
  frase/idea que la campaña exige mencionar.
- **Afirmaciones prohibidas**: si el ejecutivo dijo algo que coincide con un
  claim prohibido por la campaña.

Es un emparejamiento **best-effort por palabras clave** (no garantía legal): las
frases obligatorias/prohibidas suelen ser instrucciones ("Informar la TEA"), no
literales, así que se comparan los tokens significativos contra lo que dijo el
AGENTE. Sirve para señalar riesgos al jefe y al asesor, no para sancionar.
Coste $0 (sin IA).
"""

from __future__ import annotations

import unicodedata

# Cobertura mínima de tokens para considerar una frase "cubierta"/"dicha".
MANDATORY_THRESHOLD = 0.6
PROHIBITED_THRESHOLD = 0.75
_EVIDENCE_MAX_CHARS = 200

# Palabras vacías en español que no aportan a la comparación por palabras clave.
_STOPWORDS = {
    "de", "la", "el", "los", "las", "un", "una", "unos", "unas", "y", "o", "que",
    "en", "del", "al", "se", "su", "sus", "por", "para", "con", "como", "es",
    "the", "a", "an", "of", "to", "and", "or",
}
# Prefijos de instrucción que se eliminan de los claims prohibidos para quedarnos
# con la afirmación en sí (lo que NO debe decirse).
_PROHIBITION_PREFIXES = (
    "no afirmar que", "no garantizar que", "no prometer que", "no mencionar que",
    "no decir que", "no asegurar que", "no afirmar", "no garantizar", "no prometer",
    "no mencionar", "no decir", "no asegurar", "evitar", "nunca", "no",
)


def _normalize(text: object) -> str:
    """Minúsculas y sin tildes para comparar de forma robusta."""
    nfkd = unicodedata.normalize("NFKD", str(text or ""))
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def _significant_tokens(phrase: str, *, strip_prohibition: bool = False) -> set[str]:
    """Tokens significativos de una frase (sin stopwords ni palabras muy cortas)."""
    norm = _normalize(phrase).strip()
    if strip_prohibition:
        for prefix in _PROHIBITION_PREFIXES:
            if norm.startswith(prefix + " "):
                norm = norm[len(prefix) + 1 :].strip()
                break
    cleaned = "".join(c if c.isalnum() or c.isspace() else " " for c in norm)
    return {
        tok
        for tok in cleaned.split()
        if len(tok) >= 4 and tok not in _STOPWORDS
    }


def _agent_text(segments: list[dict] | None, full_text: str | None) -> str:
    """Texto normalizado dicho por el AGENTE (cae al texto completo si no hay diarización)."""
    if segments:
        agent_segs = [
            s.get("text", "")
            for s in segments
            if str(s.get("speaker", "")).strip().lower().startswith("a")
        ]
        if agent_segs:
            return _normalize(" ".join(agent_segs))
    return _normalize(full_text)


def _best_evidence(tokens: set[str], segments: list[dict] | None) -> str | None:
    """Devuelve el segmento del agente que más tokens de la frase contiene."""
    if not segments or not tokens:
        return None
    best_text: str | None = None
    best_hits = 0
    for seg in segments:
        if not str(seg.get("speaker", "")).strip().lower().startswith("a"):
            continue
        seg_norm = _normalize(seg.get("text", ""))
        hits = sum(1 for tok in tokens if tok in seg_norm)
        if hits > best_hits:
            best_hits = hits
            best_text = str(seg.get("text", "")).strip()
    if best_text and len(best_text) > _EVIDENCE_MAX_CHARS:
        best_text = best_text[:_EVIDENCE_MAX_CHARS].rstrip() + "…"
    return best_text


def _coverage(tokens: set[str], agent_text: str) -> float:
    """Fracción (0-1) de los tokens de la frase presentes en el texto del agente."""
    if not tokens:
        return 0.0
    present = sum(1 for tok in tokens if tok in agent_text)
    return present / len(tokens)


def check_product_note_compliance(
    segments: list[dict] | None,
    full_text: str | None,
    mandatory_phrases: list[str] | None,
    prohibited_claims: list[str] | None,
) -> dict:
    """
    Comprueba la cobertura de frases obligatorias y los claims prohibidos.

    Devuelve un dict serializable:
      {
        has_note, mandatory_total, mandatory_covered_count, coverage_pct,
        mandatory_covered: [{phrase, evidence}],
        mandatory_missing: [phrase],
        prohibited_hits:   [{claim, evidence}],
      }
    """
    mandatory_phrases = [p for p in (mandatory_phrases or []) if str(p).strip()]
    prohibited_claims = [c for c in (prohibited_claims or []) if str(c).strip()]
    agent_text = _agent_text(segments, full_text)

    covered: list[dict] = []
    missing: list[str] = []
    for phrase in mandatory_phrases:
        tokens = _significant_tokens(phrase)
        if tokens and _coverage(tokens, agent_text) >= MANDATORY_THRESHOLD:
            covered.append({"phrase": phrase, "evidence": _best_evidence(tokens, segments)})
        else:
            missing.append(phrase)

    hits: list[dict] = []
    for claim in prohibited_claims:
        tokens = _significant_tokens(claim, strip_prohibition=True)
        if tokens and _coverage(tokens, agent_text) >= PROHIBITED_THRESHOLD:
            hits.append({"claim": claim, "evidence": _best_evidence(tokens, segments)})

    total = len(mandatory_phrases)
    return {
        "has_note": bool(mandatory_phrases or prohibited_claims),
        "mandatory_total": total,
        "mandatory_covered_count": len(covered),
        "coverage_pct": round(len(covered) / total * 100, 1) if total else None,
        "mandatory_covered": covered,
        "mandatory_missing": missing,
        "prohibited_hits": hits,
    }
