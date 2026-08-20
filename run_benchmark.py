"""
run_benchmark.py
================
Entry point. Run the full benchmark from here.

Usage:
  uv run run_benchmark.py                    # all models, all 50 questions
  uv run run_benchmark.py --models phi3:3.8b # single model only
  uv run run_benchmark.py --quick            # 5 questions per model (dev test)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.rag.ingestion import ingest_all
from app.rag.vectorstore import get_stats
from app.benchmark.runner import run_benchmark
from app.config import BENCHMARK_MODELS
from data.questions import QUESTIONS

# ── Parse simple CLI args ─────────────────────────────────────────────────────
args = sys.argv[1:]
quick_mode = "--quick" in args
custom_models = None

for arg in args:
    if arg.startswith("--models="):
        custom_models = arg.split("=", 1)[1].split(",")

models_to_run = custom_models or BENCHMARK_MODELS
questions_to_run = QUESTIONS[:5] if quick_mode else QUESTIONS

# ── Step 1: Ensure PDFs are ingested ─────────────────────────────────────────
print("=" * 65)
print("  STEP 1 — Check / Ingest PDFs")
print("=" * 65)
stats = get_stats()
if stats["total_chunks"] == 0:
    print("Vector store is empty. Ingesting all PDFs now...")
    ingest_all()
else:
    print(f"Vector store ready: {stats['total_chunks']} chunks from {stats['total_documents']} doc(s)")
    for src, count in stats["sources"].items():
        print(f"  - {src}: {count} chunks")

# ── Step 2: Run benchmark ─────────────────────────────────────────────────────
print()
if quick_mode:
    print(f"[QUICK MODE] Running first {len(questions_to_run)} questions only.")

results = run_benchmark(
    models=models_to_run,
    questions=questions_to_run,
)

print(f"\nDone. {len(results)} results recorded.")
