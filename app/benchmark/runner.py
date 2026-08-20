"""
app/benchmark/runner.py
=======================
Layer 6 — Benchmark Harness.

Runs every question × every model and records:
  - latency_ms   : wall-clock time for the full LLM call
  - ram_used_mb  : RAM delta before/after
  - retries      : how many correction attempts were needed
  - confidence   : model's self-reported confidence (0.0–1.0)
  - success      : whether valid structured output was produced
  - answer       : the model's actual answer text

Output: benchmark_results/run_TIMESTAMP.csv  +  run_TIMESTAMP.json
"""

from __future__ import annotations

import csv
import json
import time
from datetime import datetime
from pathlib import Path

from app.benchmark.report import generate_report
from app.config import BENCHMARK_MODELS, BENCHMARK_RESULT_DIR, MAX_RETRIES
from app.llm.client import query_structured
from app.llm.prompts import build_rag_prompt
from app.model.schema import AnswerResponse, BenchmarkResult
from app.rag.retriever import retrieve_with_context
from data.questions import QUESTIONS


# ─────────────────────────────────────────────────────────────────────────────
# Core: run one question through one model
# ─────────────────────────────────────────────────────────────────────────────

def run_single(model: str, question: dict) -> BenchmarkResult:
    """
    Run one question through one model and return a BenchmarkResult.

    Steps:
      1. Retrieve top-k chunks from ChromaDB for this question
      2. Assemble context string
      3. Build RAG prompt
      4. Call query_structured() — includes retry logic + RAM/latency measurement
      5. Package everything into a BenchmarkResult

    Args:
        model    : Ollama model name (e.g. "phi3:3.8b")
        question : Dict from data/questions.py with id, question, category, source_pdf

    Returns:
        BenchmarkResult with all metrics filled in.
    """
    q_text = question["question"]
    q_id   = question["id"]
    q_cat  = question["category"]

    # Step 1 + 2: Retrieve and assemble context
    chunks, context = retrieve_with_context(q_text, k=5)

    # Step 3: Build prompt
    prompt = build_rag_prompt(context=context, question=q_text)

    # Step 4: Structured LLM call with retry
    try:
        result, latency_ms, ram_mb, retries = query_structured(
            prompt=prompt,
            schema=AnswerResponse,
            model=model,
            max_retries=MAX_RETRIES,
        )
        return BenchmarkResult(
            model_name=model,
            question_id=q_id,
            question=q_text,
            category=q_cat,
            answer=result.answer,
            confidence=result.confidence,
            latency_ms=round(latency_ms, 1),
            ram_used_mb=round(ram_mb, 2),
            retries=retries,
            success=True,
        )

    except RuntimeError as e:
        # Model failed even after all retries (bad JSON)
        return BenchmarkResult(
            model_name=model,
            question_id=q_id,
            question=q_text,
            category=q_cat,
            answer=f"FAILED: {str(e)[:200]}",
            confidence=0.0,
            latency_ms=0.0,
            ram_used_mb=0.0,
            retries=MAX_RETRIES,
            success=False,
        )

    except ConnectionError as e:
        # Ollama went down mid-run — mark as skipped, let the benchmark continue
        print(f"  [OLLAMA DOWN] Skipping Q{q_id}: {e}")
        return BenchmarkResult(
            model_name=model,
            question_id=q_id,
            question=q_text,
            category=q_cat,
            answer="SKIPPED: Ollama connection lost",
            confidence=0.0,
            latency_ms=0.0,
            ram_used_mb=0.0,
            retries=0,
            success=False,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Main: run_benchmark()
# ─────────────────────────────────────────────────────────────────────────────

def run_benchmark(
    models: list[str] | None = None,
    questions: list[dict] | None = None,
    run_name: str | None = None,
) -> list[BenchmarkResult]:
    """
    Run the full benchmark: every model × every question.

    Args:
        models    : List of Ollama model names. Defaults to BENCHMARK_MODELS from config.
        questions : List of question dicts. Defaults to all 50 in data/questions.py.
        run_name  : Optional label for this run (used in filenames).

    Returns:
        List of BenchmarkResult objects (one per model × question pair).
        Also saves CSV + JSON to benchmark_results/ automatically.
    """
    if models is None:
        models = BENCHMARK_MODELS
    if questions is None:
        questions = QUESTIONS

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_label = run_name or timestamp

    total = len(models) * len(questions)
    done  = 0
    all_results: list[BenchmarkResult] = []

    print("=" * 65)
    print(f"  BENCHMARK RUN : {run_label}")
    print(f"  Models        : {models}")
    print(f"  Questions     : {len(questions)}")
    print(f"  Total runs    : {total}")
    print("=" * 65)

    for model in models:
        print(f"\n{'=' * 65}")
        print(f"  Model: {model}")
        print(f"{'=' * 65}")

        for q in questions:
            done += 1
            print(f"\n  [{done}/{total}] Q{q['id']:02d} ({q['category']}) - {q['question'][:60]}...")

            result = run_single(model, q)
            all_results.append(result)

            # Live result
            status = "PASS" if result.success else "SKIP" if "SKIPPED" in result.answer else "FAIL"
            print(f"  [{status}] conf={result.confidence:.0%} | {result.latency_ms:.0f}ms | "
                  f"ram={result.ram_used_mb:.1f}MB | retries={result.retries}")

            # Auto-save partial results every 10 questions in case of crash
            if len(all_results) % 10 == 0:
                _save_results(all_results, f"{run_label}_partial")
                print(f"  [AUTO-SAVE] {len(all_results)} results saved.")

    # Save results
    csv_path, json_path = _save_results(all_results, run_label)
    print(f"\n{'=' * 65}")
    print(f"  Saved CSV  : {csv_path}")
    print(f"  Saved JSON : {json_path}")

    # Generate and print the comparison report
    report = generate_report(all_results)
    report_path = BENCHMARK_RESULT_DIR / f"report_{run_label}.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"  Saved report: {report_path}")
    print("=" * 65)
    print(report)

    return all_results


# ─────────────────────────────────────────────────────────────────────────────
# Save results to CSV + JSON
# ─────────────────────────────────────────────────────────────────────────────

def _save_results(results: list[BenchmarkResult], run_label: str) -> tuple[Path, Path]:
    """Save all BenchmarkResult objects to CSV and JSON files."""
    BENCHMARK_RESULT_DIR.mkdir(parents=True, exist_ok=True)

    csv_path  = BENCHMARK_RESULT_DIR / f"run_{run_label}.csv"
    json_path = BENCHMARK_RESULT_DIR / f"run_{run_label}.json"

    # CSV — one row per result
    fieldnames = list(BenchmarkResult.model_fields.keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r.model_dump())

    # JSON — full detail
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([r.model_dump() for r in results], f, indent=2, ensure_ascii=False)

    return csv_path, json_path
