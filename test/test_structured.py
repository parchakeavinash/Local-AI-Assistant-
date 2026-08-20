"""
test_structured.py
==================
end-to-end test.

Tests the full pipeline:
  Question -> Retrieve context -> Build prompt -> LLM -> Validate JSON -> AnswerResponse

Run: uv run test_structured.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.llm.client import query_structured
from app.llm.prompts import build_rag_prompt
from app.model.schema import AnswerResponse
from app.rag.retriever import retrieve_with_context
from app.config import DEFAULT_MODEL

# ── Test questions (based on the indexed PDF) ─────────────────────────────────
QUESTIONS = [
    "What is this document about?",
    "How do you prepare for a 'remember who you are' day?",
    "What should you do if you feel deflated after the day?",
]

print("=" * 60)
print(f"  Layer 5 Test — Structured Output + Retry")
print(f"  Model: {DEFAULT_MODEL}")
print("=" * 60)

for i, question in enumerate(QUESTIONS, 1):
    print(f"\n[Q{i}] {question}")
    print("-" * 50)

    # Step 1: Retrieve relevant context from ChromaDB
    chunks, context = retrieve_with_context(question, k=4)
    print(f"  Retrieved {len(chunks)} chunks (top: {chunks[0].similarity_score:.0%} match)" if chunks else "  No chunks found.")

    # Step 2: Build the RAG prompt
    prompt = build_rag_prompt(context=context, question=question)

    # Step 3: Call LLM with structured output enforcement
    try:
        result, latency_ms, ram_mb, retries = query_structured(
            prompt=prompt,
            schema=AnswerResponse,
            model=DEFAULT_MODEL,
        )

        # Step 4: Print the validated result
        print(f"  Answer     : {result.answer}")
        print(f"  Confidence : {result.confidence:.0%}")
        print(f"  Sources    : {len(result.sources)} chunk(s)")
        print(f"  Latency    : {latency_ms:.0f} ms")
        print(f"  RAM used   : {ram_mb:.1f} MB")
        print(f"  Retries    : {retries}")

        if result.reasoning:
            print(f"  Reasoning  : {result.reasoning[:120]}...")

    except RuntimeError as e:
        print(f"  [FAILED] {e}")

print("\n" + "=" * 60)
print("  Layer 5 test complete.")
print("=" * 60)
