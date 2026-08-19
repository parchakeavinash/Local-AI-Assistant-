from __future__ import annotations

import hashlib
from pathlib import Path

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import CHUNK_SIZE, CHUNK_OVERLAP, DATA_RAW_DIR
from app.llm.client import embed

from app.rag.vectorstore import add_chunks, delete_source, list_sources, get_stats

# Step 1- Load PDF

def load_pdf(path: Path) -> str:
    """
    Extract all text from a PDF file, page by page.
    """
    reader = PdfReader(str(path))
    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pages.append(f"[Page {i + 1}]\n{text.strip()}")
    
    if not pages:
        raise ValueError("No text could be extracted from the PDF.")
    
    full_text = "\n\n".join(pages)
    print(f'Extracted {len(reader.pages)} pages, {len(full_text):,} characters')


def chunk_text(raw_text: str, source_file: str) -> list[dict]:
    """
     Split the full PDF text into smaller overlapping chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function = len,
        separators=["\n\n", "\n", ".", " "] 
    )

    raw_chunks = splitter.split_text(raw_text)
    print('raw chunks\n:',raw_chunks)

    chunks = []

    for i, text in enumerate(raw_chunks):
        if text.strip():
            chunks.append({
                'content':text.strip(),
                'source_file':source_file,
                'chunk_index': i,
            })

    print(f'created {len(chunks)} chunks (size= {CHUNK_SIZE}, overlap= {CHUNK_OVERLAP})')
    return chunks

# stable unique id for each chunk
def unique_chunk_id(source_file: str,chunk_index: int, content: str)->str:

    content_hash = hashlib.md5(content.encode()).hexdigest()[:6]
    safe_name = source_file.replace(" ", "_")
    return f"{source_file[:10]}_chunk_{chunk_index}"


def ingest_document(file_path: Path, force_reindex: bool =False) -> dict:
    """
    Add a PDF to the RAG system: load -> chunk -> embed -> index.
    Returns statistics about the ingestion.
    """
    
    print(f'\n🚀 Ingesting: {file_path.name}')
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if file_path.suffix.lower() != '.pdf':
        raise ValueError(f"Only PDF files supported. Got: {file_path.suffix}")

    # skip if already indexed
    already_indexed = list_sources()
    if not force_reindex and path.name in already_indexed:
        chunk_count = already_indexed[path.name]
        return {"file": path.name, "status": "skipped", "chunks_stored": chunk_count,
                "message": f"Already indexed ({chunk_count} chunks). Use force_reindex=True to redo."}
    
    # remove old chunks if re-indexing
    if force_reindex and path.name in already_indexed:
        removed = delete_source(path.name)
        print(f"⚠️ Removed {removed['deleted']} old chunks from {path.name}.")
    
    print(f"\n[1/4] Loading '{path.name}'...")
    try:
        raw_text = load_pdf(file_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load PDF: {str(e)}")
        print(f"Loaded {len(reader.pages)} pages, {len(raw_text):,} chars")
    
    # Chunk text
    print(f'[2/4] Chunking text...')
    try:
        chunks = chunk_text(raw_text,file_path.name)
    except Exception as e:
        raise RuntimeError(f"Failed to chunk text: {str(e)}")


    # embedding 
    print(f"[3/4] Embedding {len(chunks)} chunks via Ollama...")
    texts = [c['content'] for c in chunks]
    metadatas = [{'source_file':c['source_file'], 'chunk_index':c['chunk_index']} for c in chunks]
    ids = [unique_chunk_id(c['source_file'],c['chunk_index'],c['content']) for c in chunks]

    embedding = []
    for i, text in enumerate(texts):
        vec = embed(text)
        embeddings.append(vec)
        if (i+1) % 10 == 0 or (i+1) == len(texts):
            print(f"   - Embedded {i+1}/{len(texts)} chunks")

    # store in chromadb
    print(f"[4/4] Storing {len(chunks)} chunks in ChromaDB...")
    stored = add_chunks(chunks= texts, embeddings = embeddings, metadatas=metadatas, ids=ids)
    
    return {
        'file': path.name,
        'status':'indexed',
        'chunks_stored':stored,
        'message':f'sucessfully indexed {stored} chunks from {path.name}'
    }

    # index every pdf in the data/raw/folder

def ingest_all(force_reindex: bool = False)->list[dict]:

    """find and ingest all .pdf files in data/raw/ folder"""

    pdf_files = sorted(DATA_RAW_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in: {DATA_RAW_DIR}")
        print(f"Drop your PDFs into: {DATA_RAW_DIR}")
        return []

    print(f"Found {len(pdf_files)} PDF files.")
    for f in pdf_files:
        print(f' -{f.name}')

    results = []
    for pdf in pdf_files:
        print(f'\n{'='*50}')
        result = ingest_document(pdf,force_reindex)
        print(f'Result:{result[message]}')
        results.append(result)
        
    #summary
    print('ingestion Summary')
    stats = get_stats()
    print(f"  Total chunks in DB : {stats['total_chunks']}")
    print(f"  Documents indexed  : {stats['total_documents']}")
    for src, count in stats["sources"].items():
        print(f"    - {src}: {count} chunks")

        return results












    print(f'\n📊 Ingestion stats:')
    print(f"   - File:          {file_path.name}")
    print(f"   - Total pages:   {len(reader.pages) if 'reader' in locals() else 'unknown'}")
    print(f"   - Total chars:   {len(text):,}")
    print(f"   - Total chunks:  {len(chunks)}")
    print(f"   - Chunk size:    {CHUNK_SIZE} chars (avg)")
    print(f"   - Overlap:       {CHUNK_OVERLAP} chars")
    
    # Step 3 + 4 + 5 in one go
    print('\n🧠 Creating embeddings and adding to ChromaDB...')
    stats = add_chunks(chunks)
    
    print(f"\n✅ Done! Added {stats['added']} chunks.")
    return stats


# ==================== MANAGEMENT FUNCTIONS ====================

def list_documents() -> list[dict]:
    """Return all documents currently in the RAG system."""
    return list_sources()


def remove_document(filename: str) -> dict:
    """Remove a document and all its chunks from the RAG system."""
    print(f'\n🗑️ Removing: {filename}')
    result = delete_source(filename)
    if result:
        print(f"✅ Removed {result['deleted']} chunks from {filename}.")
    else:
        print(f"⚠️ Document '{filename}' not found or no chunks to remove.")
    return result


def get_statistics() -> dict:
    """Return current RAG system statistics."""
    stats = get_stats()
    print('\n📊 System Statistics:')
    print(f"   - Total chunks:     {stats['total_chunks']}")
    print(f"   - Total documents:    {stats['total_documents']}")
    print(f"   - Embedding model:    {EMBEDDING_MODEL}")
    print(f"   - ChromaDB path:    {CHROMA_DB_DIR}")
    return stats
