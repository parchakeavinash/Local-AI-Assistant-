Layer 1: Config + Schemas       ← Define the "contract" first
Layer 2: Ollama client          ← Verify your AI connection works
Layer 3: Document pipeline      ← Get data into the system
Layer 4: Retrieval              ← Get relevant data back out
Layer 5: Retry + structured output ← Production hardening
Layer 6: Benchmark harness      ← The interview-ready piece
Layer 7: CLI                    ← Tie it all together


layer -1 

layer -2 
The rule: Write the simplest possible wrapper first — no retry, no validation. Just "send text → get text back". Verify it works. Then add retry logic.

Test it:

layer -3 :
document ingestion
.txt/ pdf /.md

layer -4 
retreiver

layer -5 
structure output. will enforce pydantic schema in response

layer - 6 benchmark harness
question.py
runner.py
report.py

The rule: Start with 5 questions and 2 models. Get the data pipeline (run → collect → save → report) working end-to-end. Then scale to 35 questions and 3 models.
