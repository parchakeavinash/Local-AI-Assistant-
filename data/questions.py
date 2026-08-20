"""
data/questions.py
=================
Question bank for benchmarking 3 local LLMs.

50 questions across 3 PDFs:
  - Crag.pdf          → 17 questions
  - docling-doc.pdf   → 17 questions
  - self_rag.pdf      → 16 questions

Categories:
  factual       - Direct recall from the document
  conceptual    - Requires understanding, not just copy-paste
  application   - Apply the concept to a new scenario
  out_of_context - NOT answerable from the doc (tests hallucination)
"""

QUESTIONS = [

    # ─────────────────────────────────────────────────────────────────────────
    # CRAG — 17 Questions
    # ─────────────────────────────────────────────────────────────────────────

    # Factual
    {
        "id": 0,
        "question": "What problem in conventional Retrieval-Augmented Generation (RAG) is CRAG specifically designed to address?",
        "category": "factual",
        "source_pdf": "Crag.pdf",
    },
    {
        "id": 1,
        "question": "What are the three confidence-based actions used by the CRAG retrieval evaluator?",
        "category": "factual",
        "source_pdf": "Crag.pdf",
    },
    {
        "id": 2,
        "question": "What model is used to initialize the retrieval evaluator in CRAG, and approximately how many parameters does the evaluator have?",
        "category": "factual",
        "source_pdf": "Crag.pdf",
    },
    {
        "id": 3,
        "question": "What happens to retrieved documents when the retrieval evaluator classifies the retrieval as Incorrect?",
        "category": "factual",
        "source_pdf": "Crag.pdf",
    },
    {
        "id": 4,
        "question": "What are the four datasets used to evaluate CRAG, and which evaluation metric is used for the Biography dataset?",
        "category": "factual",
        "source_pdf": "Crag.pdf",
    },

    # Conceptual
    {
        "id": 5,
        "question": "Why does CRAG introduce a retrieval evaluator before allowing the generator to use retrieved documents?",
        "category": "conceptual",
        "source_pdf": "Crag.pdf",
    },
    {
        "id": 6,
        "question": "Explain the difference between the Correct, Incorrect, and Ambiguous actions in CRAG and why the Ambiguous action is necessary.",
        "category": "conceptual",
        "source_pdf": "Crag.pdf",
    },
    {
        "id": 7,
        "question": "How does CRAG's decompose-then-recompose knowledge refinement process improve the quality of retrieved knowledge?",
        "category": "conceptual",
        "source_pdf": "Crag.pdf",
    },
    {
        "id": 8,
        "question": "Why does CRAG use web search when the retrieved documents are judged to be Incorrect?",
        "category": "conceptual",
        "source_pdf": "Crag.pdf",
    },
    {
        "id": 9,
        "question": "Why can the accuracy of the retrieval evaluator have a significant effect on the overall performance of CRAG?",
        "category": "conceptual",
        "source_pdf": "Crag.pdf",
    },

    # Application
    {
        "id": 10,
        "question": "Suppose a query retrieves ten documents and every document receives a relevance score below the lower threshold. What should CRAG do next, and why?",
        "category": "application",
        "source_pdf": "Crag.pdf",
    },
    {
        "id": 11,
        "question": "Suppose the retrieval evaluator is moderately confident that some retrieved knowledge is useful but cannot determine whether the retrieval is clearly correct or incorrect. Which action should CRAG take, and what knowledge should be provided to the generator?",
        "category": "application",
        "source_pdf": "Crag.pdf",
    },
    {
        "id": 12,
        "question": "Suppose a retrieved document is highly relevant but contains several unrelated paragraphs. How would CRAG's knowledge-refinement stage process this document?",
        "category": "application",
        "source_pdf": "Crag.pdf",
    },
    {
        "id": 13,
        "question": "If a CRAG system needs information that is missing from its static knowledge corpus, how can its web-search mechanism compensate for this limitation?",
        "category": "application",
        "source_pdf": "Crag.pdf",
    },
    {
        "id": 14,
        "question": "If removing the Ambiguous action causes performance to decrease, what does this suggest about the role of confidence uncertainty in CRAG?",
        "category": "application",
        "source_pdf": "Crag.pdf",
    },

    # Out-of-context (these should get confidence=0 / "I don't know")
    {
        "id": 15,
        "question": "What programming language was used to implement the first production version of ChatGPT?",
        "category": "out_of_context",
        "source_pdf": "Crag.pdf",
    },
    {
        "id": 16,
        "question": "What was CRAG's exact electricity consumption in kilowatt-hours during all of its experiments?",
        "category": "out_of_context",
        "source_pdf": "Crag.pdf",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # Docling Technical Report — 17 Questions
    # ─────────────────────────────────────────────────────────────────────────

    # Factual
    {
        "id": 17,
        "question": "What is Docling, and under what license is it released?",
        "category": "factual",
        "source_pdf": "docling-doc.pdf",
    },
    {
        "id": 18,
        "question": "Which two specialized models are central to Docling's document-understanding pipeline?",
        "category": "factual",
        "source_pdf": "docling-doc.pdf",
    },
    {
        "id": 19,
        "question": "What output formats can Docling generate from PDF documents?",
        "category": "factual",
        "source_pdf": "docling-doc.pdf",
    },
    {
        "id": 20,
        "question": "Which OCR library does the initial version of Docling use, and what resolution does it use for the page image sent to OCR?",
        "category": "factual",
        "source_pdf": "docling-doc.pdf",
    },
    {
        "id": 21,
        "question": "What are the two PDF backends evaluated in Docling's performance experiments?",
        "category": "factual",
        "source_pdf": "docling-doc.pdf",
    },

    # Conceptual
    {
        "id": 22,
        "question": "Why is converting PDFs into machine-processable formats difficult according to the Docling report?",
        "category": "conceptual",
        "source_pdf": "docling-doc.pdf",
    },
    {
        "id": 23,
        "question": "Explain the sequence of the main stages in Docling's document-processing pipeline, from PDF parsing to final document assembly.",
        "category": "conceptual",
        "source_pdf": "docling-doc.pdf",
    },
    {
        "id": 24,
        "question": "Why does Docling need both the textual content with geometric coordinates and a rendered image of each PDF page?",
        "category": "conceptual",
        "source_pdf": "docling-doc.pdf",
    },
    {
        "id": 25,
        "question": "Why is table structure recognition treated separately from ordinary text extraction in Docling?",
        "category": "conceptual",
        "source_pdf": "docling-doc.pdf",
    },
    {
        "id": 26,
        "question": "Why does Docling preserve information such as reading order, figures, tables, references, and metadata instead of simply extracting plain text?",
        "category": "conceptual",
        "source_pdf": "docling-doc.pdf",
    },

    # Application
    {
        "id": 27,
        "question": "You have a scanned PDF containing no machine-readable text. Which Docling capability would you enable, and why?",
        "category": "application",
        "source_pdf": "docling-doc.pdf",
    },
    {
        "id": 28,
        "question": "You need to process a large collection of PDFs as quickly as possible. Which Docling processing mode would be more appropriate: batch or interactive, and why?",
        "category": "application",
        "source_pdf": "docling-doc.pdf",
    },
    {
        "id": 29,
        "question": "You have a PDF containing complex financial tables. How would Docling's TableFormer-based processing help compared with simply extracting the text from the PDF?",
        "category": "application",
        "source_pdf": "docling-doc.pdf",
    },
    {
        "id": 30,
        "question": "You need to run Docling in a very low-resource environment where memory usage is important. Which PDF backend does the report recommend considering, and what trade-off should you expect?",
        "category": "application",
        "source_pdf": "docling-doc.pdf",
    },
    {
        "id": 31,
        "question": "Suppose you need a customized document-processing pipeline that replaces one of Docling's default models. How can Docling's architecture support this requirement?",
        "category": "application",
        "source_pdf": "docling-doc.pdf",
    },

    # Out-of-context
    {
        "id": 32,
        "question": "What is the current market capitalization of IBM?",
        "category": "out_of_context",
        "source_pdf": "docling-doc.pdf",
    },
    {
        "id": 33,
        "question": "What was the exact number of downloads Docling received from PyPI during 2025?",
        "category": "out_of_context",
        "source_pdf": "docling-doc.pdf",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # SELF-RAG — 16 Questions
    # ─────────────────────────────────────────────────────────────────────────

    # Factual
    {
        "id": 34,
        "question": "What does SELF-RAG stand for, and what are its two main goals?",
        "category": "factual",
        "source_pdf": "self_rag.pdf",
    },
    {
        "id": 35,
        "question": "What are the roles of the Retrieve, ISREL, ISSUP, and ISUSE reflection tokens in SELF-RAG?",
        "category": "factual",
        "source_pdf": "self_rag.pdf",
    },
    {
        "id": 36,
        "question": "How does SELF-RAG differ from conventional RAG in deciding when to retrieve information?",
        "category": "factual",
        "source_pdf": "self_rag.pdf",
    },
    {
        "id": 37,
        "question": "What model is used as the initial generator/critic model in the training setup described in the SELF-RAG paper?",
        "category": "factual",
        "source_pdf": "self_rag.pdf",
    },
    {
        "id": 38,
        "question": "How is the critic model trained to predict reflection tokens in SELF-RAG?",
        "category": "factual",
        "source_pdf": "self_rag.pdf",
    },

    # Conceptual
    {
        "id": 39,
        "question": "Why does SELF-RAG use reflection tokens instead of simply retrieving a fixed number of passages for every question?",
        "category": "conceptual",
        "source_pdf": "self_rag.pdf",
    },
    {
        "id": 40,
        "question": "How does SELF-RAG determine whether a retrieved passage is relevant to the question?",
        "category": "conceptual",
        "source_pdf": "self_rag.pdf",
    },
    {
        "id": 41,
        "question": "What is the difference between evaluating whether a passage is relevant and evaluating whether it supports the generated answer in SELF-RAG?",
        "category": "conceptual",
        "source_pdf": "self_rag.pdf",
    },
    {
        "id": 42,
        "question": "How do reflection tokens make SELF-RAG's behavior more controllable at inference time?",
        "category": "conceptual",
        "source_pdf": "self_rag.pdf",
    },
    {
        "id": 43,
        "question": "Why does SELF-RAG aim to improve both the factuality of generated answers and their attribution to retrieved evidence?",
        "category": "conceptual",
        "source_pdf": "self_rag.pdf",
    },

    # Application
    {
        "id": 44,
        "question": "Suppose SELF-RAG is answering a question and determines that external information is unnecessary. What should happen instead of automatically retrieving passages?",
        "category": "application",
        "source_pdf": "self_rag.pdf",
    },
    {
        "id": 45,
        "question": "Suppose SELF-RAG retrieves three passages, but only one is relevant to the question. How should the reflection mechanism affect the use of those passages?",
        "category": "application",
        "source_pdf": "self_rag.pdf",
    },
    {
        "id": 46,
        "question": "Suppose a retrieved passage is relevant to the question but does not support the model's generated claim. Which aspect of SELF-RAG's reflection mechanism should detect this problem?",
        "category": "application",
        "source_pdf": "self_rag.pdf",
    },
    {
        "id": 47,
        "question": "If you wanted an LLM to retrieve information only when it would improve an answer and then critique its own generated response, why would SELF-RAG be more suitable than conventional RAG?",
        "category": "application",
        "source_pdf": "self_rag.pdf",
    },

    # Out-of-context
    {
        "id": 48,
        "question": "What is the exact inference latency of SELF-RAG on every NVIDIA GPU model currently available?",
        "category": "out_of_context",
        "source_pdf": "self_rag.pdf",
    },
    {
        "id": 49,
        "question": "What is the current number of parameters in GPT-5.6 Luna?",
        "category": "out_of_context",
        "source_pdf": "self_rag.pdf",
    },
]


# ── Quick lookup helpers ───────────────────────────────────────────────────────

def get_by_category(category: str) -> list[dict]:
    """Return all questions of a given category."""
    return [q for q in QUESTIONS if q["category"] == category]

def get_by_pdf(pdf_name: str) -> list[dict]:
    """Return all questions for a specific PDF."""
    return [q for q in QUESTIONS if q["source_pdf"] == pdf_name]

def summary() -> None:
    """Print a breakdown of the question bank."""
    from collections import Counter
    cats = Counter(q["category"] for q in QUESTIONS)
    pdfs = Counter(q["source_pdf"] for q in QUESTIONS)
    print(f"Total questions : {len(QUESTIONS)}")
    print(f"By category     : {dict(cats)}")
    print(f"By PDF          : {dict(pdfs)}")


if __name__ == "__main__":
    summary()
