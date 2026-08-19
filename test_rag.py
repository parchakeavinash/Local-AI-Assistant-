
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.rag.ingestion import ingest_document
from app.rag.retriever import retrieve, assemble_context
from app.rag.vectorstore import get_stats

PDF_PATH = Path("data/raw/How-to-have-a-remember-who-the-fuck-you-are-day-starter-pack.pdf")

print("=" * 60)
print("  STEP 1: INGEST PDF")
print("=" * 60)

result = ingest_document(PDF_PATH, force_reindex=False)
print(f"\nResult : {result['status']}")
print(f"Chunks : {result['chunks_stored']}")
print(f"Message: {result['message']}")

print("\n" + "=" * 60)
print("  STEP 2: CHECK VECTOR STORE")
print("=" * 60)
stats = get_stats()
print(f"Total chunks     : {stats['total_chunks']}")
print(f"Total documents  : {stats['total_documents']}")
for src, count in stats["sources"].items():
    print(f"  - {src}: {count} chunks")

print("\n" + "=" * 60)
print("  STEP 3: RETRIEVE")
print("=" * 60)

test_questions = [
    "What is this document about?",
    "What are the main ideas?",
    "How do you remember who you are?",
]

for question in test_questions:
    print(f"\nQ: {question}")
    chunks = retrieve(question, k=3)
    if chunks:
        print(f"  Top match ({chunks[0].similarity_score:.0%} relevant):")
        print(f"  {chunks[0].content[:200]}...")
    else:
        print("  No results found.")

print("\n[DONE] RAG pipeline working end to end.")
