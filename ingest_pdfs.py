import sys
sys.path.insert(0, '.')
from app.rag.ingestion import ingest_all
from app.rag.vectorstore import get_stats

ingest_all()
stats = get_stats()
total_chunks = stats["total_chunks"]
total_docs = stats["total_documents"]
print(f"DONE: {total_chunks} chunks from {total_docs} documents")
for src, count in stats["sources"].items():
    print(f"  - {src}: {count} chunks")
