# 🤖 Local AI Assistant — Implementation Plan

> **Goal**: Build a production-grade, fully offline AI assistant with RAG (Retrieval-Augmented Generation), structured output via Pydantic, and a rigorous model benchmarking system — all running on your local machine via Ollama.

---

## 📌 Project Philosophy

This is not a toy project. Every design decision mimics what you'd find in a real production ML/AI system:
- **Retry logic** when model outputs malformed JSON
- **Pydantic schemas** to validate every model response
- **Benchmark harness** to make data-driven model selection
- **Separation of concerns** across well-defined modules

---

## 🗺️ Phases Overview

| Phase | Name | Deliverable |
|-------|------|-------------|
| 1 | Environment Setup | Working Ollama + Python env + models pulled |
| 2 | Core RAG Pipeline | Document ingestion → chunking → embedding → retrieval |
| 3 | Structured Output Layer | Pydantic schemas + retry logic |
| 4 | Benchmarking Harness | 30–40 Q&A runs across 3 models with metrics |
| 5 | CLI / UI Interface | Interactive assistant interface |
| 6 | Documentation & Polish | README, benchmark table, architecture diagram |

---

## 🔧 Phase 1 — Environment Setup

### 1.1 Install Ollama
```bash
# Windows
winget install Ollama.Ollama
# OR download from https://ollama.com
```

### 1.2 Pull the 3 Benchmark Models
```bash
ollama pull llama3.2        # Meta's LLaMA 3.2 (3B or 8B)
ollama pull mistral         # Mistral 7B
ollama pull phi3            # Microsoft Phi-3 Mini (3.8B) — fast & lightweight
```

### 1.3 Python Environment
```bash
python -m venv .venv
.venv\Scripts\activate
pip install ollama chromadb pydantic langchain-community sentence-transformers rich click pytest
```

### 1.4 Project Scaffold
```
OfflineAiAsistant/
├── app/
│   ├── __init__.py
│   ├── config.py          # Model names, paths, settings
│   ├── models/            # Pydantic schemas
│   ├── rag/               # Document pipeline
│   ├── llm/               # Ollama client + retry logic
│   ├── benchmark/         # Benchmarking harness
│   └── cli/               # User interface
├── data/
│   ├── raw/               # Upload your notes here
│   └── chroma_db/         # Persisted vector store
├── benchmark_results/     # JSON + CSV output from runs
├── tests/
├── requirements.txt
└── README.md
```

---

## 🔧 Phase 2 — Core RAG Pipeline

### 2.1 Document Ingestion (`app/rag/ingestion.py`)
- Accept: `.pdf`, `.txt`, `.md`, `.docx`
- Use `langchain_community` document loaders
- Chunk text using **RecursiveCharacterTextSplitter** (chunk_size=500, overlap=50)

### 2.2 Embedding & Vector Store (`app/rag/vectorstore.py`)
- Embedding model: **`nomic-embed-text`** (runs via Ollama, fully local)
- Vector DB: **ChromaDB** (persistent, local)
- Store chunks with metadata (source file, page number, chunk index)

### 2.3 Retrieval (`app/rag/retriever.py`)
- Top-k similarity search (default k=5)
- Return retrieved chunks + similarity scores
- Assemble context string for the LLM prompt

### 2.4 Prompt Template (`app/llm/prompts.py`)
```
System: You are a study assistant. Answer ONLY from the provided context.
         If you cannot find the answer, say "I don't know based on the notes."
         Always respond in valid JSON matching the required schema.

Context: {retrieved_chunks}

Question: {user_question}
```

---

## 🔧 Phase 3 — Structured Output & Retry Logic

### 3.1 Pydantic Schemas (`app/models/schemas.py`)
```python
from pydantic import BaseModel, Field
from typing import Optional, List

class AnswerResponse(BaseModel):
    answer: str = Field(..., description="Direct answer to the question")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence 0-1")
    sources: List[str] = Field(default_factory=list, description="Source chunks referenced")
    reasoning: Optional[str] = Field(None, description="Step-by-step reasoning")

class BenchmarkResult(BaseModel):
    model_name: str
    question_id: int
    question: str
    answer: str
    latency_ms: float
    ram_used_mb: float
    confidence: float
    retries: int
    success: bool
```

### 3.2 Retry Logic (`app/llm/client.py`)
```python
def query_with_retry(model, prompt, schema, max_retries=3):
    for attempt in range(max_retries):
        raw = ollama_generate(model, prompt)
        try:
            parsed = schema.model_validate_json(extract_json(raw))
            return parsed, attempt
        except ValidationError as e:
            # Append error feedback to prompt and retry
            prompt += f"\n[CORRECTION]: Your last response was invalid: {e}. Fix it."
    raise MaxRetriesExceeded(f"Model failed after {max_retries} attempts")
```

**Key behaviours:**
- Extract JSON from markdown code fences (` ```json ... ``` `)
- Append validation errors as correction hints on retry
- Track `retries` count per query for benchmarking

---

## 🔧 Phase 4 — Benchmarking Harness

### 4.1 Question Bank (`benchmark/questions.py`)
- 35 questions across 5 categories:
  - **Factual recall** (10 Qs) — "What is X?"
  - **Conceptual understanding** (10 Qs) — "Explain Y in simple terms"
  - **Application** (5 Qs) — "How would you apply Z?"
  - **Multi-hop reasoning** (5 Qs) — questions requiring connecting two facts
  - **Out-of-context** (5 Qs) — questions NOT in notes (tests hallucination)

### 4.2 Metrics Collected Per Query
| Metric | How Measured |
|--------|-------------|
| **Latency (ms)** | `time.perf_counter()` around LLM call |
| **RAM Usage (MB)** | `psutil.Process().memory_info().rss` before/after |
| **Retries** | Counter in retry loop |
| **Success Rate** | % of queries that parse successfully |
| **Answer Quality** | Manual rating 1–5 OR automated ROUGE score |

### 4.3 Benchmark Runner (`benchmark/runner.py`)
```python
for model in ["llama3.2", "mistral", "phi3"]:
    for question in QUESTION_BANK:
        result = run_single_benchmark(model, question)
        results.append(result)

# Save to CSV + JSON
save_results(results, "benchmark_results/run_001.csv")
```

### 4.4 Results Visualization (`benchmark/report.py`)
- Auto-generate a **Markdown comparison table**
- Bar charts using `matplotlib` for latency and RAM
- Export as `benchmark_report.md` ready to paste into your README

---

## 🔧 Phase 5 — Interface

### 5.1 CLI (Primary — `app/cli/main.py`)
Using the `rich` + `click` libraries:
```
$ python -m app.cli.main

╔══════════════════════════════╗
║   📚 Offline AI Study Buddy  ║
╚══════════════════════════════╝
Active Model: mistral
Loaded Notes: semester_notes.pdf (42 chunks)

> ask: What is gradient descent?
> upload: notes.pdf
> benchmark: run
> switch-model: llama3.2
> exit
```

### 5.2 Optional Web UI (Stretch Goal)
- Minimal **FastAPI** backend + HTML/JS frontend
- Drag-and-drop file upload
- Chat-style interface with source citations

---

## 🔧 Phase 6 — Documentation & Polish

### 6.1 README.md Must Include
- [ ] Project description & motivation
- [ ] Setup instructions (step by step)
- [ ] Architecture diagram (Mermaid or image)
- [ ] Benchmark comparison table
- [ ] Sample Q&A screenshots
- [ ] Lessons learned / engineering decisions

### 6.2 Benchmark Comparison Table Template
| Model | Avg Latency | Peak RAM | Success Rate | Avg Confidence | Best For |
|-------|-------------|----------|--------------|----------------|----------|
| LLaMA 3.2 | _ms | _MB | _% | _ | |
| Mistral 7B | _ms | _MB | _% | _ | |
| Phi-3 Mini | _ms | _MB | _% | _ | |

---

## ✅ Step-by-Step Build Order (Your Checklist)

- [ ] **Week 1**: Env setup + Ollama running + basic `ollama.generate()` call works
- [ ] **Week 1**: Define all Pydantic schemas
- [ ] **Week 2**: Document ingestion pipeline (PDF → chunks → ChromaDB)
- [ ] **Week 2**: Retrieval working end-to-end (query → context → answer)
- [ ] **Week 3**: Retry logic + structured output fully tested
- [ ] **Week 3**: Benchmark question bank created (35 questions)
- [ ] **Week 4**: Benchmark runner complete, all 3 models tested
- [ ] **Week 4**: CLI polished, README written, benchmark table filled

---

## 🚨 Production Patterns to Highlight in Interviews

1. **Schema-first design** — Define outputs before writing logic
2. **Retry with feedback injection** — Not just blind retries, but error-guided correction
3. **Separation of concerns** — RAG pipeline is independent of the LLM client
4. **Observability** — Every query logs latency, RAM, and retries
5. **Data-driven decisions** — Model choice backed by benchmark numbers, not gut feel
6. **Graceful degradation** — "I don't know" is a valid, handled response
