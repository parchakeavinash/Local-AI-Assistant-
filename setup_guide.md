# Setup Guide — Local AI Assistant (Offline RAG Benchmarking System)

> A local-first RAG (Retrieval-Augmented Generation) system that benchmarks open-source LLMs  
> running entirely on your machine — no API keys, no cloud, no cost.

---

## What This Project Does

This tool lets you:
1. **Ingest PDF documents** into a local vector database (ChromaDB)
2. **Ask questions** and retrieve answers from those documents using a local LLM
3. **Benchmark multiple models** (llama3.2, mistral, phi3) on a question bank and compare their performance across accuracy, latency, retry rate, and hallucination resistance

---

## Prerequisites

Before you begin, make sure you have the following installed:

| Tool | Version | Purpose |
|------|---------|---------|
| [Python](https://www.python.org/downloads/) | ≥ 3.12 | Runtime |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | latest | Fast Python package manager |
| [Ollama](https://ollama.com/download) | latest | Runs local LLMs |
| [Git](https://git-scm.com/downloads) | latest | Clone the repo |

> **Windows users:** All commands below are for PowerShell.

---

## Step 1 — Clone the Repository

```powershell
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

---

## Step 2 — Install Python Dependencies

This project uses `uv` for dependency management (much faster than pip).

```powershell
# Install uv if you haven't already
pip install uv

# Create virtual environment and install all dependencies
uv sync
```

This will create a `.venv` folder and install everything from `pyproject.toml`:
- `ollama` — Python client for Ollama API
- `chromadb` — Local vector database
- `langchain-community` — PDF loading + text chunking
- `pydantic` — Structured output schema validation
- `rich` + `click` — CLI interface
- `sentence-transformers` — Embedding support
- `pytest` — Testing

---

## Step 3 — Install Ollama Models

Start the Ollama server, then pull all required models:

```powershell
# In a DEDICATED terminal window — keep this open during the entire session
ollama serve
```

Then in a **new** terminal window:

```powershell
# Embedding model (required for ingestion + retrieval)
ollama pull nomic-embed-text

# LLMs for benchmarking
ollama pull phi3:3.8b
ollama pull llama3.2:3b
ollama pull mistral:7b
```

> **Note:** Total download size is approximately **8.9 GB**.  
> Make sure you have enough disk space before pulling all three models.

Verify they are ready:
```powershell
ollama list
```

Expected output:
```
NAME                       SIZE
nomic-embed-text:latest    274 MB
phi3:3.8b                  2.2 GB
llama3.2:3b                2.0 GB
mistral:7b                 4.4 GB
```

---

## Step 4 — Add Your PDF Files

Place your PDF documents inside the `data/raw/` folder:

```
data/
  raw/
    Crag.pdf
    docling-doc.pdf
    self_rag.pdf
```

> The benchmark question bank in `data/questions.py` is written for these 3 specific PDFs.  
> If you use your own PDFs, update `data/questions.py` accordingly.

---

## Step 5 — Ingest PDFs into ChromaDB

```powershell
# Make sure 'ollama serve' is running in another terminal first
$env:PYTHONIOENCODING='utf-8'
.venv\Scripts\python.exe ingest_pdfs.py
```

Expected output:
```
Found 3 PDF file(s)...

--- Ingesting: Crag.pdf ---
  Extracted X pages | Created ~144 chunks | Stored in ChromaDB

--- Ingesting: docling-doc.pdf ---
  Extracted X pages | Created ~120 chunks | Stored in ChromaDB

--- Ingesting: self_rag.pdf ---
  Extracted X pages | Created ~245 chunks | Stored in ChromaDB

DONE: 509 chunks from 3 documents
```

---

## Step 6 — Run a Quick Test (5 questions, 1 model)

Before running the full benchmark, verify the pipeline works end-to-end:

```powershell
$env:PYTHONIOENCODING='utf-8'
.venv\Scripts\python.exe run_benchmark.py --quick --models=phi3:3.8b
```

You should see 5 questions answered with `[PASS]` or `[FAIL]` status, latency, and confidence scores.

---

## Step 7 — Run the Full Benchmark

> **Warning:** This runs 150 LLM calls (50 questions × 3 models). Takes **45–90 minutes** depending on your hardware.

```powershell
$env:PYTHONIOENCODING='utf-8'
.venv\Scripts\python.exe run_benchmark.py
```

Results are saved automatically to `benchmark_result/`:
```
benchmark_result/
  run_TIMESTAMP.csv        ← all results as a spreadsheet
  run_TIMESTAMP.json       ← full detail with answers
  report_TIMESTAMP.md      ← comparison table (markdown)
```

To run only specific models:
```powershell
.venv\Scripts\python.exe run_benchmark.py --models=mistral:7b
.venv\Scripts\python.exe run_benchmark.py --models=phi3:3.8b,llama3.2:3b
```

---

## Step 8 — View the Report

Open the generated report in VS Code or any markdown viewer:
```powershell
code benchmark_result\report_TIMESTAMP.md
```

The report includes:
- **Overall summary** — success rate, latency, RAM, retries per model
- **Category breakdown** — factual / conceptual / application / out-of-context
- **Retry analysis** — how many questions needed error correction
- **Hallucination check** — did models say "I don't know" on unanswerable questions?

---

## Project Structure

```
OfflineAiAsistant/
│
├── app/
│   ├── config.py               ← Central config (paths, models, settings)
│   ├── model/
│   │   └── schema.py           ← Pydantic schemas (AnswerResponse, BenchmarkResult)
│   ├── llm/
│   │   ├── client.py           ← Ollama API + query_structured() with retry logic
│   │   └── prompts.py          ← System prompt + RAG prompt + correction prompt
│   ├── rag/
│   │   ├── ingestion.py        ← PDF → chunks → embeddings → ChromaDB
│   │   ├── retriever.py        ← Semantic search + context assembly
│   │   └── vectorstore.py      ← ChromaDB read/write/stats
│   └── benchmark/
│       ├── runner.py           ← Runs model × question loop, saves CSV/JSON
│       └── report.py           ← Generates markdown comparison table
│
├── data/
│   ├── raw/                    ← Drop your PDFs here
│   └── questions.py            ← 50-question bank (17 CRAG + 17 Docling + 16 SELF-RAG)
│
├── benchmark_result/           ← Auto-generated results (gitignored CSV/JSON)
│   └── *.md                    ← Benchmark reports (kept in git)
│
├── notes/
│   ├── benchmark_deep_analysis.md  ← Full analysis of 150-run results
│   └── structure.md                ← Project roadmap
│
├── test/
│   ├── test_rag.py             ← End-to-end ingestion + retrieval test
│   └── test_structured.py      ← Structured output + retry test
│
├── run_benchmark.py            ← Main entry point
├── ingest_pdfs.py              ← Re-ingest PDFs if ChromaDB is cleared
├── analyze_benchmark.py        ← Deep stats from benchmark JSON
├── pyproject.toml              ← Dependencies (managed by uv)
└── .python-version             ← Python version pin
```

---

## Common Issues & Fixes

### Ollama not responding / hanging

```powershell
# Always run Ollama in its OWN dedicated terminal window
ollama serve

# Pre-warm the model before benchmarking to keep it loaded in RAM
ollama run phi3:3.8b "ready"
```

### UnicodeEncodeError on Windows terminal

```powershell
# Set UTF-8 encoding before every python run
$env:PYTHONIOENCODING='utf-8'
```

Or add it permanently to your PowerShell profile:
```powershell
Add-Content $PROFILE '$env:PYTHONIOENCODING="utf-8"'
```

### ChromaDB already has old data

```powershell
# Clear the vector store and re-ingest
Remove-Item -Recurse -Force "data\chroma_db"
.venv\Scripts\python.exe ingest_pdfs.py
```

### Benchmark crashes mid-run

Results are auto-saved every 10 questions as `run_TIMESTAMP_partial.csv`.  
The run is designed to survive Ollama connection drops — skipped questions are logged as `SKIP`.

---

## Key Design Decisions

| Decision | Reason |
|----------|--------|
| **PDF-only ingestion** | Focused scope for benchmarking — one format, clean comparison |
| **nomic-embed-text** | Best open-source embedding model available via Ollama |
| **ChromaDB** | Zero-config, persistent, on-disk vector store — no server needed |
| **Pydantic validation** | Forces models to return structured, parseable output |
| **Retry with error injection** | Correction prompt includes the exact validation error so model knows what it got wrong |
| **uv over pip** | 10–100x faster dependency resolution |

---

## Benchmark Results (150-run summary)

| Model | Success Rate | Avg Latency | Retries | OOC Refusals |
|-------|-------------|-------------|---------|--------------|
| mistral:7b | **90%** | 51,214 ms | 16 | 6/6 |
| phi3:3.8b | 80% | 27,903 ms | 31 | 5/6 |
| llama3.2:3b | 78% | **17,731 ms** | 33 | 6/6 |

**Winner for accuracy:** `mistral:7b`  
**Winner for speed:** `llama3.2:3b`

Full analysis: [`notes/benchmark_deep_analysis.md`](notes/benchmark_deep_analysis.md)

---

## License

MIT — free to use, fork, and build on.
