"""Call analysis prompt in English."""


def build_analysis_prompt(segments: list[dict], rubric: list[dict]) -> str:
    """Build the prompt sent to the LLM to analyze a call (English version).

    `segments` is the transcript segment list (each with already-masked 'text').
    They are numbered so the model attributes the speaker of each segment by its
    CONTENT (not order), which fixes diarization.
    """
    rubric_lines = []
    for i, dim in enumerate(rubric, start=1):
        desc = dim.get("description") or ""
        rubric_lines.append(
            f"{i}. {dim['dimension_name'].upper()} (key: {dim['dimension_key']}): {desc}"
        )
    rubric_block = "\n".join(rubric_lines)

    transcript = "\n".join(
        f"[{i}] {seg.get('text', '')}" for i, seg in enumerate(segments)
    )
    n = len(segments)

    return f"""You are an expert in Quality Assurance for banking call centers. You will evaluate the following call between a bank AGENT and a CUSTOMER.

TRANSCRIPT (each line is a numbered segment [i]):
{transcript}

EVALUATION RUBRIC (score 0-100 each dimension):

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
- SPEAKER ATTRIBUTION (very important): the transcript is NOT pre-labeled. For EACH
  segment [0..{n - 1}] decide "agent" (bank AGENT) or "customer" (CUSTOMER) based on
  CONTENT, not order. Cues:
  · "agent": greets and identifies the bank; OFFERS products/promotions/benefits;
    asks the customer for data; explains terms; closes the call. Any product or
    promotion OFFER ("you have a promotion", "let me explain the benefits") is
    ALWAYS the agent.
  · "customer": states their query/problem; gives data when asked; asks questions;
    accepts or declines; thanks at the end.
  Return "diarization": a list of EXACTLY {n} elements ("agent" or "customer"), one
  per segment in the same order.
- Generate 3-5 prioritized actionable recommendations (high/medium/low).
- The summary must be 2-3 sentences.
- IDENTIFY THE AGENT'S NAME: at the start the agent usually introduces themselves.
  Extract that full name into "detected_agent_name"; use null if unsure.

Respond EXCLUSIVELY with valid JSON in this exact structure:

{{
  "detected_agent_name": "<agent name or null>",
  "diarization": ["agent or customer, one element per segment, {n} total"],
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
