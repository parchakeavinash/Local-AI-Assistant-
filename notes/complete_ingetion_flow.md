              data/raw/
                  │
          Find all .pdf files
                  │
                  ▼
       ┌─────────────────────┐
       │  ingest_all_pdfs()  │
       └──────────┬──────────┘
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
    PDF 1       PDF 2      PDF 3
       │          │          │
       ▼          ▼          ▼
 ingest_pdf  ingest_pdf  ingest_pdf
       │          │          │
       ▼          ▼          ▼
    chunks     chunks     chunks
       │          │          │
       ▼          ▼          ▼
  embeddings  embeddings  embeddings
       │          │          │
       └──────────┼──────────┘
                  ▼
             Vector DB
                  │
                  ▼
           get_stats()
                  │
                  ▼
          Ingestion Summary