from __future__ import annotations

import hashlib
from pathlib import Path

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import CHUNK_SIZE, CHUNK_OVERLAP, DATA_RAW_DIR
from app.llm.client import embed
from app.rag.vectorstore import add_chunks, delete_source, list_sources, get_stats


# ── Step 1: Load PDF ──────────────────────────────────────────────────────────

def load_pdf(path: Path) -> str:
    """Extract all text from a PDF file, page by page."""
    reader = PdfReader(str(path))
    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pages.append(f"[Page {i + 1}]\n{text.strip()}")

    if not pages:
        raise ValueError("No text could be extracted from the PDF.")

    full_text = "\n\n".join(pages)
    print(f"  Extracted {len(reader.pages)} pages, {len(full_text):,} characters")
    return full_text   # fixed: was missing `return`


# ── Step 2: Split text into chunks ────────────────────────────────────────────

def chunk_text(raw_text: str, source_file: str) -> list[dict]:
    """Split the full PDF text into smaller overlapping chunks."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ".", " "]
    )

    raw_chunks = splitter.split_text(raw_text)

    chunks = []
    for i, text in enumerate(raw_chunks):
        if text.strip():
            chunks.append({
                "content":      text.strip(),
                "source_file":  source_file,
                "chunk_index":  i,
            })

    print(f"  Created {len(chunks)} chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    return chunks


# ── Step 3: Unique ID per chunk ───────────────────────────────────────────────

def unique_chunk_id(source_file: str, chunk_index: int, content: str) -> str:
    """Stable unique ID — same content always gets the same ID, no duplicates."""
    content_hash = hashlib.md5(content.encode()).hexdigest()[:6]
    safe_name = source_file.replace(" ", "_")[:20]
    return f"{safe_name}_chunk_{chunk_index}_{content_hash}"


# ── Main: ingest_document() ───────────────────────────────────────────────────

def ingest_document(file_path: Path, force_reindex: bool = False) -> dict:
    """
    Full pipeline: load PDF -> chunk -> embed -> store in ChromaDB.
    Returns a result dict with status and chunk count.
    """
    print(f"\n--- Ingesting: {file_path.name} ---")

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix.lower() != ".pdf":
        raise ValueError(f"Only PDF files supported. Got: {file_path.suffix}")

    # skip if already indexed
    already_indexed = list_sources()
    if not force_reindex and file_path.name in already_indexed:   # fixed: was `path.name`
        chunk_count = already_indexed[file_path.name]
        print(f"  Already indexed ({chunk_count} chunks). Skipping.")
        return {
            "file": file_path.name,
            "status": "skipped",
            "chunks_stored": chunk_count,
            "message": f"Already indexed ({chunk_count} chunks). Use force_reindex=True to redo."
        }

    # remove old chunks if force re-indexing
    if force_reindex and file_path.name in already_indexed:
        removed = delete_source(file_path.name)    # fixed: delete_source returns int not dict
        print(f"  Removed {removed} old chunks.")

    # Step 1: Load
    print(f"[1/4] Loading PDF...")
    try:
        raw_text = load_pdf(file_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load PDF: {e}")

    # Step 2: Chunk
    print(f"[2/4] Chunking text...")
    try:
        chunks = chunk_text(raw_text, file_path.name)
    except Exception as e:
        raise RuntimeError(f"Failed to chunk text: {e}")

    # Step 3: Embed
    print(f"[3/4] Embedding {len(chunks)} chunks via Ollama...")
    texts     = [c["content"]     for c in chunks]
    metadatas = [{"source_file": c["source_file"], "chunk_index": c["chunk_index"]} for c in chunks]
    ids       = [unique_chunk_id(c["source_file"], c["chunk_index"], c["content"]) for c in chunks]

    embeddings = []                          # fixed: was `embedding = []` then `embeddings.append()`
    for i, text in enumerate(texts):
        vec = embed(text)
        embeddings.append(vec)
        if (i + 1) % 10 == 0 or (i + 1) == len(texts):
            print(f"   Embedded {i + 1}/{len(texts)}")

    # Step 4: Store
    print(f"[4/4] Storing in ChromaDB...")
    stored = add_chunks(chunks=texts, embeddings=embeddings, ids=ids, metadatas=metadatas)

    return {
        "file": file_path.name,
        "status": "indexed",
        "chunks_stored": stored,
        "message": f"Successfully indexed {stored} chunks from {file_path.name}"
    }


# ── Ingest all PDFs in data/raw/ ──────────────────────────────────────────────

def ingest_all(force_reindex: bool = False) -> list[dict]:
    """Find and ingest all .pdf files in data/raw/ folder."""

    pdf_files = sorted(DATA_RAW_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in: {DATA_RAW_DIR}")
        print(f"Drop your PDFs into: {DATA_RAW_DIR}")
        return []

    print(f"Found {len(pdf_files)} PDF file(s):")
    for f in pdf_files:
        print(f"  - {f.name}")

    results = []
    for pdf in pdf_files:
        print(f"\n{'=' * 50}")
        result = ingest_document(pdf, force_reindex)
        print(f"Result: {result['message']}")   # fixed: was `result[message]` (missing quotes)
        results.append(result)

    # summary
    print(f"\n{'=' * 50}")
    print("INGESTION SUMMARY:")
    stats = get_stats()
    print(f"  Total chunks in DB : {stats['total_chunks']}")
    print(f"  Documents indexed  : {stats['total_documents']}")
    for src, count in stats["sources"].items():
        print(f"    - {src}: {count} chunks")

    return results          # fixed: was indented inside the for loop


# ── Utility functions ─────────────────────────────────────────────────────────

def list_documents() -> dict:
    """Return all documents currently in the RAG system."""
    return list_sources()   # fixed: was `list_ources()` (typo)


def remove_document(filename: str) -> int:
    """Remove a document and all its chunks from the RAG system."""
    print(f"\nRemoving: {filename}")
    removed = delete_source(filename)
    if removed:
        print(f"Removed {removed} chunks from {filename}.")
    else:
        print(f"Document '{filename}' not found or no chunks to remove.")
    return removed
