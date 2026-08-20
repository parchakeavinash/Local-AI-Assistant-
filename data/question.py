CRAG — 17 Questions
Factual Recall — 5
What problem in conventional Retrieval-Augmented Generation (RAG) is CRAG specifically designed to address?
What are the three confidence-based actions used by the CRAG retrieval evaluator?
What model is used to initialize the retrieval evaluator in CRAG, and approximately how many parameters does the evaluator have?
What happens to retrieved documents when the retrieval evaluator classifies the retrieval as Incorrect?
What are the four datasets used to evaluate CRAG, and which evaluation metric is used for the Biography dataset?
Conceptual Understanding — 5
Why does CRAG introduce a retrieval evaluator before allowing the generator to use retrieved documents?
Explain the difference between the Correct, Incorrect, and Ambiguous actions in CRAG and why the Ambiguous action is necessary.
How does CRAG's decompose-then-recompose knowledge refinement process improve the quality of retrieved knowledge?
Why does CRAG use web search when the retrieved documents are judged to be Incorrect?
Why can the accuracy of the retrieval evaluator have a significant effect on the overall performance of CRAG?
Application — 5
Suppose a query retrieves ten documents and every document receives a relevance score below the lower threshold. What should CRAG do next, and why?
Suppose the retrieval evaluator is moderately confident that some retrieved knowledge is useful but cannot determine whether the retrieval is clearly correct or incorrect. Which action should CRAG take, and what knowledge should be provided to the generator?
Suppose a retrieved document is highly relevant but contains several unrelated paragraphs. How would CRAG's knowledge-refinement stage process this document?
If a CRAG system needs information that is missing from its static knowledge corpus, how can its web-search mechanism compensate for this limitation?
If removing the Ambiguous action causes performance to decrease, what does this suggest about the role of confidence uncertainty in CRAG?
Out-of-Context — 2
What programming language was used to implement the first production version of ChatGPT?
What was CRAG's exact electricity consumption in kilowatt-hours during all of its experiments?
2. Docling Technical Report — 17 Questions
Factual Recall — 5
What is Docling, and under what license is it released?
Which two specialized models are central to Docling's document-understanding pipeline?
What output formats can Docling generate from PDF documents?
Which OCR library does the initial version of Docling use, and what resolution does it use for the page image sent to OCR?
What are the two PDF backends evaluated in Docling's performance experiments?
Conceptual Understanding — 5
Why is converting PDFs into machine-processable formats difficult according to the Docling report?
Explain the sequence of the main stages in Docling's document-processing pipeline, from PDF parsing to final document assembly.
Why does Docling need both the textual content with geometric coordinates and a rendered image of each PDF page?
Why is table structure recognition treated separately from ordinary text extraction in Docling?
Why does Docling preserve information such as reading order, figures, tables, references, and metadata instead of simply extracting plain text?
Application — 5
You have a scanned PDF containing no machine-readable text. Which Docling capability would you enable, and why?
You need to process a large collection of PDFs as quickly as possible. Which Docling processing mode would be more appropriate: batch or interactive, and why?
You have a PDF containing complex financial tables. How would Docling's TableFormer-based processing help compared with simply extracting the text from the PDF?
You need to run Docling in a very low-resource environment where memory usage is important. Which PDF backend does the report recommend considering, and what trade-off should you expect?
Suppose you need a customized document-processing pipeline that replaces one of Docling's default models. How can Docling's architecture support this requirement?
Out-of-Context — 2
What is the current market capitalization of IBM?
What was the exact number of downloads Docling received from PyPI during 2025?
3. SELF-RAG — 16 Questions
Factual Recall — 5
What does SELF-RAG stand for, and what are its two main goals?
What are the roles of the Retrieve, ISREL, ISSUP, and ISUSE reflection mechanisms?
How does SELF-RAG differ from conventional RAG in deciding when to retrieve information?
What model is used as the initial generator/critic model in the training setup described in the paper?
How is the critic model trained to predict reflection tokens?
Conceptual Understanding — 5
Why does SELF-RAG use reflection tokens instead of simply retrieving a fixed number of passages for every question?
How does SELF-RAG determine whether a retrieved passage is relevant to the question?
What is the difference between evaluating whether a passage is relevant and evaluating whether it supports the generated answer?
How do reflection tokens make SELF-RAG's behavior more controllable at inference time?
Why does SELF-RAG aim to improve both the factuality of generated answers and their attribution to retrieved evidence?
Application — 4
Suppose SELF-RAG is answering a question and determines that external information is unnecessary. What should happen instead of automatically retrieving passages?
Suppose SELF-RAG retrieves three passages, but only one is relevant to the question. How should the reflection mechanism affect the use of those passages?
Suppose a retrieved passage is relevant to the question but does not support the model's generated claim. Which aspect of SELF-RAG's reflection mechanism should detect this problem?
If you wanted an LLM to retrieve information only when it would improve an answer and then critique its own generated response, why would SELF-RAG be more suitable than conventional RAG?
Out-of-Context — 2
What is the exact inference latency of SELF-RAG on every NVIDIA GPU model currently available?
What is the current number of parameters in GPT-5.6 Luna?