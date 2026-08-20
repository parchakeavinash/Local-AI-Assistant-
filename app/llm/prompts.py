from __future__ import annotations

from app.model.schema import AnswerResponse


SYSTEM_PROMPT = """You are a precise study assistant. Your job is to answer questions using ONLY the provided context.

Rules:
1. Answer strictly from the context. Do NOT use outside knowledge.
2. If the answer is not in the context, set answer to "I couldn't find enough information in the provided notes." and confidence to 0.0.
3. You MUST respond with valid JSON only. No prose, no markdown, no explanation outside the JSON.
4. Your response must match this exact schema:

{
  "answer": "<your answer here>",
  "confidence": <float between 0.0 and 1.0>,
  "sources": ["<short quote from context that supports your answer>"],
  "reasoning": "<optional: your step-by-step thinking>"
}"""


def build_rag_prompt(context: str, question: str) -> str:
    """
    Build the user-facing prompt that combines retrieved context + question.


    Args:
        context  : The assembled context string from retriever.assemble_context()
        question : The user's original question.

    Returns:
        A formatted prompt string ready to send to generate().
    """
    return f"""CONTEXT (from uploaded documents):
{context}

QUESTION:
{question}

Respond ONLY with a JSON object matching the schema in your instructions."""


def build_correction_prompt(original_prompt: str, validation_error: str, bad_response: str) -> str:
    """
    Build a correction prompt when the model returns invalid JSON.

    Instead of starting over, we feed the error back to the model
    so it can fix its own output. This is the retry pattern.

    Args:
        original_prompt   : The original prompt that produced bad output.
        validation_error  : The Pydantic validation error message.
        bad_response      : What the model actually returned (the bad output).

    Returns:
        A new prompt that includes the error and asks for a fix.
    """
    return f"""{original_prompt}

---
YOUR PREVIOUS RESPONSE WAS INVALID:
{bad_response}

VALIDATION ERROR:
{validation_error}

Fix the errors and respond again with ONLY a valid JSON object matching the required schema.
Do not include any text outside the JSON."""


def get_schema_description() -> str:
    """
    Return a human-readable description of the AnswerResponse schema.
    Used in prompts to remind the model what fields are required.
    """
    schema = AnswerResponse.model_json_schema()
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    lines = ["Required JSON fields:"]
    for field, info in properties.items():
        req = "(required)" if field in required else "(optional)"
        desc = info.get("description", "")
        lines.append(f"  - {field} {req}: {desc}")

    return "\n".join(lines)
