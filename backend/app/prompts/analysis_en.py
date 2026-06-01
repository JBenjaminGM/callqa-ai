"""Call analysis prompt in English."""


def build_analysis_prompt(transcription_text: str, rubric: list[dict]) -> str:
    """Build the prompt sent to the LLM to analyze a call (English version)."""
    rubric_lines = []
    for i, dim in enumerate(rubric, start=1):
        desc = dim.get("description") or ""
        rubric_lines.append(
            f"{i}. {dim['dimension_name'].upper()} (key: {dim['dimension_key']}): {desc}"
        )
    rubric_block = "\n".join(rubric_lines)

    return f"""You are an expert in Quality Assurance for banking call centers. You will evaluate the following call between a bank AGENT and a CUSTOMER.

CALL TRANSCRIPT:
{transcription_text}

EVALUATION RUBRIC (7 dimensions, score 0-100 each):

{rubric_block}

Dimension guide:
1. GREETING & PROTOCOL: Did the agent greet properly, identify themselves, mention the recording, and close appropriately?
2. ASSERTIVENESS & TONE: Empathetic, clear, patient? Professional tone? Active listening?
3. PROMOTIONS/PRODUCTS: Did the agent mention relevant products and explain benefits correctly?
4. COMPLIANCE: Disclaimers mentioned? Sensitive data protected? Consent requested?
5. RESOLUTION: Was the reason for the call resolved? Concrete solutions offered?
6. OBJECTION HANDLING: Were the customer's doubts/objections handled well?
7. CUSTOMER SENTIMENT: Was the customer satisfied? (Infer from tone, words, farewell)

INSTRUCTIONS:
- Be objective and base each score on concrete evidence from the transcript.
- Generate 3-5 prioritized actionable recommendations (high/medium/low).
- The summary must be 2-3 sentences.
- IDENTIFY THE AGENT'S NAME: at the start of the call the bank agent almost
  always introduces themselves ("My name is...", "You're speaking with...").
  Extract that full name into "detected_agent_name". Use null if unsure.

Respond EXCLUSIVELY with valid JSON in this exact structure:

{{
  "detected_agent_name": "<agent name or null>",
  "dimension_scores": {{
    "greeting": <int 0-100>,
    "assertiveness": <int 0-100>,
    "promotions": <int 0-100>,
    "compliance": <int 0-100>,
    "resolution": <int 0-100>,
    "objections": <int 0-100>,
    "sentiment": <int 0-100>
  }},
  "summary": "<executive summary of the call>",
  "recommendations": [
    {{
      "priority": "high|medium|low",
      "dimension": "<dimension_key>",
      "title": "<short title>",
      "description": "<specific actionable recommendation>"
    }}
  ]
}}
"""
