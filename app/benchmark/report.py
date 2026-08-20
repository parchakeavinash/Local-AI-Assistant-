"""
app/benchmark/report.py
=======================
Auto-generate a Markdown comparison table from benchmark results.

Called automatically by runner.py after every run.
"""

from __future__ import annotations

from collections import defaultdict
from app.model.schema import BenchmarkResult


def generate_report(results: list[BenchmarkResult]) -> str:
    """
    Generate a full Markdown benchmark report from a list of BenchmarkResult.

    Sections:
      1. Overall summary table (one row per model)
      2. Per-category breakdown table
      3. Retry analysis (which models needed corrections)
      4. Notable failures

    Args:
        results : All BenchmarkResult objects from a benchmark run.

    Returns:
        A Markdown string ready to write to a .md file or print.
    """
    if not results:
        return "# Benchmark Report\n\nNo results to report."

    # Group results by model
    by_model: dict[str, list[BenchmarkResult]] = defaultdict(list)
    for r in results:
        by_model[r.model_name].append(r)

    lines = []
    lines.append("# Benchmark Report — Local LLM Comparison\n")
    lines.append(f"**Models tested:** {', '.join(f'`{m}`' for m in by_model)}")
    lines.append(f"**Total questions:** {len(set(r.question_id for r in results))}")
    lines.append(f"**Total runs:** {len(results)}\n")

    # ── Section 1: Overall Summary Table ──────────────────────────────────────
    lines.append("## Overall Summary\n")
    lines.append("| Model | Avg Latency | Avg RAM | Success Rate | Avg Confidence | Total Retries |")
    lines.append("|-------|------------|---------|--------------|----------------|---------------|")

    for model, res in by_model.items():
        successful   = [r for r in res if r.success]
        avg_latency  = sum(r.latency_ms   for r in successful) / len(successful) if successful else 0
        avg_ram      = sum(r.ram_used_mb  for r in successful) / len(successful) if successful else 0
        avg_conf     = sum(r.confidence   for r in successful) / len(successful) if successful else 0
        success_rate = len(successful) / len(res) * 100
        total_retry  = sum(r.retries for r in res)

        lines.append(
            f"| `{model}` | {avg_latency:.0f} ms | {avg_ram:.1f} MB | "
            f"{success_rate:.0f}% | {avg_conf:.0%} | {total_retry} |"
        )

    # ── Section 2: Per-Category Breakdown ─────────────────────────────────────
    lines.append("\n## Performance by Question Category\n")
    categories = sorted(set(r.category for r in results))

    lines.append("| Model | " + " | ".join(f"{c.replace('_',' ').title()} Avg Conf" for c in categories) + " |")
    lines.append("|-------|" + "|".join("---" for _ in categories) + "|")

    for model, res in by_model.items():
        row = [f"`{model}`"]
        for cat in categories:
            cat_res = [r for r in res if r.category == cat and r.success]
            if cat_res:
                avg = sum(r.confidence for r in cat_res) / len(cat_res)
                row.append(f"{avg:.0%}")
            else:
                row.append("N/A")
        lines.append("| " + " | ".join(row) + " |")

    # ── Section 3: Retry Analysis ─────────────────────────────────────────────
    lines.append("\n## Retry Analysis\n")
    lines.append("*(Retries > 0 means the model returned invalid JSON on the first attempt)*\n")
    lines.append("| Model | Runs needing retry | Max retries in one run | Failed completely |")
    lines.append("|-------|-------------------|------------------------|-------------------|")

    for model, res in by_model.items():
        needed_retry   = sum(1 for r in res if r.retries > 0)
        max_retry      = max(r.retries for r in res)
        failed         = sum(1 for r in res if not r.success)
        lines.append(f"| `{model}` | {needed_retry} | {max_retry} | {failed} |")

    # ── Section 4: Out-of-Context Hallucination Check ─────────────────────────
    lines.append("\n## Hallucination Check (Out-of-Context Questions)\n")
    lines.append("*These questions have no answer in the documents. The model should say 'I don't know' with confidence ~0.*\n")
    lines.append("| Model | Correct Refusals | Hallucinated | Avg Confidence on OOC |")
    lines.append("|-------|-----------------|--------------|------------------------|")

    for model, res in by_model.items():
        ooc = [r for r in res if r.category == "out_of_context"]
        refusals      = sum(1 for r in ooc if r.confidence < 0.3)
        hallucinated  = sum(1 for r in ooc if r.confidence >= 0.3)
        avg_ooc_conf  = sum(r.confidence for r in ooc) / len(ooc) if ooc else 0
        lines.append(f"| `{model}` | {refusals}/{len(ooc)} | {hallucinated}/{len(ooc)} | {avg_ooc_conf:.0%} |")

    # ── Section 5: Key Observations ───────────────────────────────────────────
    lines.append("\n## Key Observations\n")
    lines.append("*(Fill this in after reviewing results)*\n")
    lines.append("- **Fastest model:** _TBD_")
    lines.append("- **Most accurate:** _TBD_")
    lines.append("- **Best at refusing out-of-context:** _TBD_")
    lines.append("- **Most retries needed:** _TBD_")
    lines.append("- **Engineering decision:** _TBD_\n")

    return "\n".join(lines)
