"""Prompt de análisis de llamadas en español."""


def build_analysis_prompt(segments: list[dict], rubric: list[dict]) -> str:
    """
    Construye el prompt que se envía al LLM para analizar una llamada.

    `segments` es la lista de segmentos de la transcripción (cada uno con 'text',
    ya enmascarado). Se numeran para que el modelo atribuya el hablante de cada
    segmento por su CONTENIDO (no por el orden ni las pausas), corrigiendo así la
    diarización. `rubric` describe las dimensiones a evaluar.
    """
    rubric_lines = []
    for i, dim in enumerate(rubric, start=1):
        desc = dim.get("description") or ""
        rubric_lines.append(
            f"{i}. {dim['dimension_name'].upper()} (clave: {dim['dimension_key']}): {desc}"
        )
    rubric_block = "\n".join(rubric_lines)

    transcript = "\n".join(
        f"[{i}] {seg.get('text', '')}" for i, seg in enumerate(segments)
    )
    n = len(segments)

    return f"""Eres un experto en Quality Assurance de call centers bancarios. Vas a evaluar la siguiente llamada entre un EJECUTIVO del banco y un CLIENTE.

TRANSCRIPCIÓN (cada línea es un segmento numerado [i]):
{transcript}

RÚBRICA DE EVALUACIÓN (score 0-100 cada dimensión):

{rubric_block}

Guía de cada dimensión:
1. SALUDO Y PROTOCOLO: ¿Saludó correctamente? ¿Se identificó? ¿Mencionó la grabación? ¿Cerró adecuadamente?
2. ASERTIVIDAD Y TONO: ¿Empático, claro, paciente? ¿Tono profesional? ¿Escuchó activamente?
3. MENCIÓN DE PROMOCIONES/PRODUCTOS: ¿Mencionó productos relevantes? ¿Explicó beneficios correctamente?
4. CUMPLIMIENTO NORMATIVO: ¿Mencionó disclaimers? ¿Protegió datos sensibles? ¿Pidió consentimiento?
5. RESOLUCIÓN: ¿Resolvió el motivo de la llamada? ¿Ofreció soluciones concretas?
6. MANEJO DE OBJECIONES: ¿Manejó bien las dudas/objeciones del cliente?
7. SENTIMIENTO DEL CLIENTE: ¿El cliente quedó satisfecho? (Inferir del tono, palabras, despedida)

INSTRUCCIONES:
- Sé objetivo y basa cada score en evidencia concreta de la transcripción.
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
- Genera 3-5 recomendaciones accionables priorizadas (high/medium/low).
- El resumen debe ser de 2-3 frases.
- IDENTIFICA EL NOMBRE DEL EJECUTIVO: al inicio el ejecutivo casi siempre se
  presenta ("Le atiende Juan Pérez", "Mi nombre es..."). Extrae ese nombre en
  "detected_agent_name"; si no estás seguro, usa null.

Responde EXCLUSIVAMENTE con un JSON válido con esta estructura exacta:

{{
  "detected_agent_name": "<nombre del ejecutivo o null>",
  "diarization": ["agent o customer, un elemento por segmento, {n} en total"],
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
