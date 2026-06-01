"""Prompt de análisis de llamadas en español."""


def build_analysis_prompt(transcription_text: str, rubric: list[dict]) -> str:
    """
    Construye el prompt que se envía al LLM para analizar una llamada.

    `rubric` es una lista de dicts con al menos dimension_key, dimension_name
    y, opcionalmente, description. Se incluye en el prompt para que el modelo
    conozca los criterios y pesos configurados por el supervisor.
    """
    rubric_lines = []
    for i, dim in enumerate(rubric, start=1):
        desc = dim.get("description") or ""
        rubric_lines.append(
            f"{i}. {dim['dimension_name'].upper()} (clave: {dim['dimension_key']}): {desc}"
        )
    rubric_block = "\n".join(rubric_lines)

    return f"""Eres un experto en Quality Assurance de call centers bancarios. Vas a evaluar la siguiente llamada entre un EJECUTIVO del banco y un CLIENTE.

TRANSCRIPCIÓN DE LA LLAMADA:
{transcription_text}

RÚBRICA DE EVALUACIÓN (7 dimensiones, score 0-100 cada una):

{rubric_block}

Guía de cada dimensión:
1. SALUDO Y PROTOCOLO: ¿Saludó correctamente? ¿Se identificó? ¿Mencionó la grabación? ¿Cerró adecuadamente?
2. ASERTIVIDAD Y TONO: ¿Empático, claro, paciente? ¿Tono profesional? ¿Escuchó activamente?
3. MENCIÓN DE PROMOCIONES/PRODUCTOS: ¿Mencionó productos relevantes? ¿Explicó beneficios correctamente?
4. CUMPLIMIENTO NORMATIVO: ¿Mencionó disclaimers? ¿Protegió datos sensibles? ¿Pidió consentimiento?
5. RESOLUCIÓN: ¿Resolvió el motivo de la llamada? ¿Ofreció soluciones concretas?
6. MANEJO DE OBJECIONES: ¿Manejó bien las dudas/objeciones del cliente? ¿Persuasión profesional?
7. SENTIMIENTO DEL CLIENTE: ¿El cliente quedó satisfecho? (Inferir del tono, palabras, despedida)

INSTRUCCIONES:
- Sé objetivo y basa cada score en evidencia concreta de la transcripción.
- Genera 3-5 recomendaciones accionables priorizadas (high/medium/low).
- El resumen debe ser de 2-3 frases.
- IDENTIFICA EL NOMBRE DEL EJECUTIVO: al inicio de la llamada el ejecutivo del
  banco casi siempre se presenta ("Le atiende Juan Pérez", "Mi nombre es...",
  "Habla con..."). Extrae ese nombre completo en "detected_agent_name". Si no
  logras identificarlo con seguridad, usa null.

Responde EXCLUSIVAMENTE con un JSON válido con esta estructura exacta:

{{
  "detected_agent_name": "<nombre del ejecutivo o null>",
  "dimension_scores": {{
    "greeting": <int 0-100>,
    "assertiveness": <int 0-100>,
    "promotions": <int 0-100>,
    "compliance": <int 0-100>,
    "resolution": <int 0-100>,
    "objections": <int 0-100>,
    "sentiment": <int 0-100>
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
