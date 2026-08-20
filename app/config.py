from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

# notes/docs
DATA_RAW_DIR = ROOT_DIR/"data"/"raw"

CHROMA_DB_DIR  = ROOT_DIR/"data"/"chroma_db"

# CSV/JSON/ report /
BENCHMARK_RESULT_DIR = ROOT_DIR/'benchmark_result'

# make sure to exit this when config is imported
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
BENCHMARK_RESULT_DIR.mkdir(parents=True, exist_ok=True)


# ollama setting

MODEL_LLAMA ='llama3.2:3b'
MODEL_MISTRAL='mistral:7b'
MODEL_PHI3='phi3:3.8b'

EMBEDDING_MODEL='nomic-embed-text:latest'

DEFAULT_MODEL = MODEL_PHI3

# OLLAMA_BASE_URL='http://[IP_ADDRESS]'

BENCHMARK_MODELS = [MODEL_LLAMA, MODEL_MISTRAL, MODEL_PHI3]

# RAG SETTINGS

CHUNK_SIZE = 500

CHUNK_OVERLAP = 50

TOP_K = 5

# name of the chromadb
CHROMA_COLLECTION_NAME ='Study_notes'



# llm call settings

MAX_RETRIES = 3

OLLAMA_BASE_URL ="http://localhost:11434"


BENCHMARK_QUESTION_COUNT = 50

# if __name__ == "__main__":
#     print("=== Config Check ===")
#     print(f"Project root  : {ROOT_DIR}")
#     print(f"Raw data dir  : {DATA_RAW_DIR}  (exists: {DATA_RAW_DIR.exists()})")
#     print(f"ChromaDB dir  : {CHROMA_DB_DIR}  (exists: {CHROMA_DB_DIR.exists()})")
#     print(f"Benchmark dir : {BENCHMARK_RESULT_DIR}  (exists: {BENCHMARK_RESULT_DIR.exists()})")
#     print(f"Default model : {DEFAULT_MODEL}")
#     print(f"Embed model   : {EMBEDDING_MODEL}")
#     print(f"Chunk size    : {CHUNK_SIZE}  |  Overlap: {CHUNK_OVERLAP}  |  Top-K: {TOP_K}")
#     print(f"Max retries   : {MAX_RETRIES}")
#     print("[OK] Config loaded successfully.")
