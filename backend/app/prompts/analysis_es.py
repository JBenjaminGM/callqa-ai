"""Prompt de análisis de llamadas en español (rúbrica dinámica con subcriterios)."""


def build_analysis_prompt(segments: list[dict], rubric: list[dict]) -> str:
    """
    Construye el prompt que se envía al LLM para analizar una llamada.

    `segments`: lista de segmentos (cada uno con 'text', ya enmascarado). Se numeran
    para que el modelo atribuya el hablante de cada uno por su CONTENIDO.
    `rubric`: lista de dimensiones {dimension_key, dimension_name, description,
    criteria:[{name, enabled}]}. Solo los subcriterios ACTIVOS se incluyen como guía,
    y la estructura de salida `dimension_scores` se genera con las claves reales.
    """
    rubric_lines = []
    for i, dim in enumerate(rubric, start=1):
        desc = dim.get("description") or ""
        line = f"{i}. {dim['dimension_name'].upper()} (clave: {dim['dimension_key']})"
        if desc:
            line += f": {desc}"
        enabled = [
            c.get("name")
            for c in (dim.get("criteria") or [])
            if c.get("enabled") and c.get("name")
        ]
        if enabled:
            line += "\n   Subcriterios a evaluar: " + "; ".join(enabled)
        rubric_lines.append(line)
    rubric_block = "\n".join(rubric_lines)

    transcript = "\n".join(
        f"[{i}] {seg.get('text', '')}" for i, seg in enumerate(segments)
    )
    n = len(segments)
    score_lines = ",\n".join(
        f'    "{dim["dimension_key"]}": <int 0-100>' for dim in rubric
    )

    return f"""Eres un experto en Quality Assurance de call centers bancarios. Vas a evaluar la siguiente llamada entre un EJECUTIVO del banco y un CLIENTE.

TRANSCRIPCIÓN (cada línea es un segmento numerado [i]):
{transcript}

RÚBRICA DE EVALUACIÓN (score 0-100 por dimensión):

{rubric_block}

INSTRUCCIONES:
- Evalúa CADA dimensión de la rúbrica de 0 a 100, teniendo en cuenta ÚNICAMENTE los
  subcriterios listados en ella. Basa cada score en evidencia concreta de la transcripción.
- ATRIBUCIÓN DE HABLANTE (muy importante): la transcripción NO indica quién habla.
  Para CADA segmento [0..{n - 1}] decide "agent" (EJECUTIVO del banco) o "customer"
  (CLIENTE) SEGÚN EL CONTENIDO, no por el orden. Pistas:
  · "agent": saluda e identifica al banco; OFRECE productos/promociones/beneficios;
    pide datos al cliente; explica condiciones; cierra la llamada. Toda OFERTA o
    descripción de un producto/promoción ("le ofrezco", "tiene una promoción",
    "le explico los beneficios") es SIEMPRE del ejecutivo.
  · "customer": plantea su consulta o problema; da sus datos cuando se los piden;
    pregunta dudas; acepta o rechaza; agradece al final.
  Devuelve "diarization": lista de EXACTAMENTE {n} elementos ("agent" o "customer"),
  uno por segmento y en el mismo orden.
- Genera 3-5 recomendaciones accionables priorizadas (high/medium/low). El campo
  "dimension" de cada recomendación debe ser una de las claves de la rúbrica.
- El resumen debe ser de 2-3 frases.
- IDENTIFICA EL NOMBRE DEL EJECUTIVO: al inicio el ejecutivo casi siempre se presenta
  ("Le atiende Juan Pérez", "Mi nombre es..."). Extrae ese nombre en
  "detected_agent_name"; si no estás seguro, usa null.

Responde EXCLUSIVAMENTE con un JSON válido con esta estructura exacta:

{{
  "detected_agent_name": "<nombre del ejecutivo o null>",
  "diarization": ["agent o customer, un elemento por segmento, {n} en total"],
  "dimension_scores": {{
{score_lines}
  }},
  "summary": "<resumen ejecutivo de la llamada>",
  "recommendations": [
    {{
      "priority": "high|medium|low",
      "dimension": "<dimension_key>",
      "title": "<título corto>",
      "description": "<recomendación específica accionable>"
    }}
  ]
}}
"""
