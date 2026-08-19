# RAG Pipeline — Test Run Report

**Date:** 2026-08-19  
**PDF Tested:** `How-to-have-a-remember-who-the-fuck-you-are-day-starter-pack.pdf`  
**Status:** PASSED

---

## Ingestion Results

| Metric | Value |
|--------|-------|
| Pages extracted | 8 |
| Characters extracted | 14,390 |
| Chunks created | 33 |
| Chunk size | 500 chars |
| Chunk overlap | 50 chars |
| Embedding model | `nomic-embed-text` (via Ollama) |
| Storage | ChromaDB (local, persistent) |
| Final status | `indexed` ✓ |

**Pipeline steps all passed:**
- `[1/4]` PDF loaded and text extracted — ✓  
- `[2/4]` Text split into 33 chunks — ✓  
- `[3/4]` 33 chunks embedded via Ollama — ✓  
- `[4/4]` Stored in ChromaDB — ✓  

---

## Vector Store State (after ingestion)

| Metric | Value |
|--------|-------|
| Total chunks in DB | 33 |
| Total documents | 1 |
| Source | `How-to-have-a-remember-who-the-fuck-you-are-day-starter-pack.pdf` |

---

## Retrieval Results

| Question | Top Match Relevance | Retrieved From |
|----------|-------------------|----------------|
| "What is this document about?" | **74%** | Page 3 |
| "What are the main ideas?" | **73%** | Page 6 |
| "How do you remember who you are?" | **88%** | Inline chunk |

### Sample Retrieved Chunks

**Q: "What is this document about?" → 74% match**
> *[Page 3] — "Prepare for peace. What I mean by this is spend time thinking what you might need to do so that you can completely enjoy this time, without worrying about other people or things..."*

**Q: "How do you remember who you are?" → 88% match**
> *"But then you'll go back to your current reality. And you may feel a bit deflated. And the energy you created from your 'Remember who the fuck you are!' day, may dwindle. This is OK!..."*

---

## Observations

- **Retrieval quality is good** — 88% similarity on a direct-intent question shows the embeddings are capturing meaning accurately.
- **74–73% on broader questions** is expected — vague questions return lower similarity but still return relevant content.
- The `[Page N]` prefix added during ingestion allows page-level citation in future answers.
- ChromaDB persisted the index to disk — re-running will skip ingestion (already indexed).

---

## What's Next

- [ ] **Layer 5** — Structured output: make the LLM answer in validated JSON (`AnswerResponse` schema)
- [ ] **Layer 5** — Retry logic: re-prompt on malformed JSON output
- [ ] **Layer 6** — Benchmark harness: run 3 models × 30+ questions, collect latency + RAM metrics
