from __future__ import annotations

from app.config import TOP_K
from app.llm.client import embed
from app.model.schema import DocumentChunk
from app.rag.vectorstore import search, get_stats


def retrieve(question: str, k: int = TOP_K) -> list[DocumentChunk]:   # fixed: was `retriver`, wrong signature `k = int = TOP_K`
    """
    Find the k most relevant document chunks for a user's question.
    Process: Embed question -> search ChromaDB -> return list of DocumentChunks.
    """
    stats = get_stats()

    if stats["total_chunks"] == 0:
        print("[WARNING] Vector store is empty. Please ingest documents first.")
        return []

    try:
        question_embedding = embed(question)
    except Exception as e:
        print(f"[ERROR] Embedding failed: {e}")
        return []

    if not question_embedding:
        print("[WARNING] Embedding returned empty.")
        return []

    # search chromadb
    chunks = search(question_embedding, k)

    if not chunks:
        print("[WARNING] No relevant chunks found.")
        return []

    return chunks


def assemble_context(chunks: list[DocumentChunk]) -> str:
    """Format retrieved chunks into a clean context block for the LLM."""
    if not chunks:
        return "No relevant context found in the uploaded documents."

    parts = []
    for chunk in chunks:
        relevance_pct = int(chunk.similarity_score * 100)
        header = f"[Source: {chunk.source_file} | Relevance: {relevance_pct}%]"
        parts.append(f"{header}\n{chunk.content}")

    return "\n\n".join(parts)


def retrieve_with_context(question: str, k: int = TOP_K) -> tuple[list[DocumentChunk], str]:  # fixed: was `retriver_with_context`, called `retrieve()` not defined
    """
    Combine retrieve + assemble_context in one call.
    Returns (chunks, context_string).
    """
    chunks = retrieve(question, k)      # fixed: was calling `retrieve(question)` before it was defined
    context = assemble_context(chunks)
    return chunks, context