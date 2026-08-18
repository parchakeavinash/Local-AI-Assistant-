                 INGESTION
PDF
 ↓
Extract text
 ↓
Create chunks
 ↓
Create embeddings
 ↓
┌─────────────────────┐
│      ChromaDB       │
│                     │
│ text                │
│ embedding           │
│ metadata            │
│ ID                  │
└─────────────────────┘
          ↑
          │
       SEARCH
          │
User question
 ↓
Create query embedding
 ↓
Search ChromaDB
 ↓
Most relevant chunks
 ↓
LLM
 ↓
Answer