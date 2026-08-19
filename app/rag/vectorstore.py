from __future__ import annotations

import chromadb
from chromadb.config import Settings

from app.config import CHROMA_DB_DIR, CHROMA_COLLECTION_NAME
from app.model.schema import DocumentChunk


# connect with chromadb and get the collection
def get_collection() -> chromadb.Collection:
    """Get or create ChromaDB collection."""

    client = chromadb.PersistentClient(
        path=str(CHROMA_DB_DIR),
        settings=Settings(anonymized_telemetry=False)
    )

    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    return collection


# add chunks to the collection
def add_chunks(
    chunks: list[str],
    embeddings: list[list[float]],
    ids: list[str],
    metadatas: list[dict],          # fixed: was `metadata` (singular) — must match call in ingestion.py
) -> int:
    """Add embedding vectors to the ChromaDB collection. Returns count stored."""

    if not chunks:
        return 0

    collection = get_collection()

    # upsert = insert if not exists, update if it does → no duplicates
    collection.upsert(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    return len(chunks)


def search(query_embedding: list[float], k: int = 5) -> list[DocumentChunk]:
    """Retrieve top-k relevant chunks for a query embedding using cosine similarity."""

    collection = get_collection()   # fixed: was using `collection` before defining it

    # empty db check
    if collection.count() == 0:
        return []

    result = collection.query(
        query_embeddings=[query_embedding],      # fixed: was `query_embedding` (wrong param name)
        n_results=min(k, collection.count()),    # fixed: was `n_result` (wrong param name)
        include=["documents", "metadatas", "distances"]
    )

    chunks: list[DocumentChunk] = []

    documents = result.get("documents")[0]
    metadatas = result.get("metadatas")[0]
    distances = result.get("distances")[0]
    ids       = result.get("ids")[0]

    for doc, meta, dist, chunk_id in zip(documents, metadatas, distances, ids):
        # cosine distance 0 = identical → similarity = 1.0
        similarity = 1.0 - (dist / 2.0)
        chunks.append(DocumentChunk(
            chunk_id=chunk_id,
            content=doc,
            source_file=meta.get("source_file", "Unknown file"),
            chunk_index=int(meta.get("chunk_index", 0)),
            similarity_score=round(similarity, 4)
        ))

    return chunks


def delete_source(source_file: str) -> int:
    """Delete all stored chunks that came from a specific file."""
    collection = get_collection()

    results = collection.get(
        where={"source_file": source_file},
        include=["metadatas"],
    )
    ids_to_delete = results["ids"]

    if not ids_to_delete:
        return 0

    collection.delete(ids=ids_to_delete)
    return len(ids_to_delete)


# show all unique source files that have been indexed
def list_sources() -> dict[str, int]:
    collection = get_collection()

    if collection.count() == 0:
        return {}

    results = collection.get(include=["metadatas"])

    counts: dict[str, int] = {}
    for meta in results.get("metadatas", []):
        src = meta.get("source_file", "unknown")
        counts[src] = counts.get(src, 0) + 1

    return counts


def get_stats() -> dict:
    """Returns a summary of the vector store state."""
    collection = get_collection()
    sources = list_sources()
    return {
        "total_chunks": collection.count(),
        "total_documents": len(sources),
        "sources": sources,
    }
