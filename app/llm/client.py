from __future__ import annotations

import json
import re
import time
import ollama
import psutil

from pydantic import BaseModel, ValidationError
from typing import Type, TypeVar

T = TypeVar("T", bound=BaseModel)

from app.config import OLLAMA_BASE_URL,DEFAULT_MODEL,EMBEDDING_MODEL



def _get_client()->ollama.Client:
    """
    Returns a configured Ollama client pointed at our local server.
    Called internally by generate() and embed().
    """
    return ollama.Client(host=OLLAMA_BASE_URL)


def generate(
    prompt: str,
    model: str = DEFAULT_MODEL,
    system_prompt : str | None=None
)->tuple[str,float]:
    """
    Send a prompt to an Ollama model and return the response text.

    Args:
        prompt       : The user's question or instruction.
        model        : Which Ollama model to use (default from config).
        system_prompt: Optional system-level instruction for the model.

    Returns:
        A tuple of (response_text, latency_ms).
        - response_text : The raw text the model produced.
        - latency_ms    : How long the call took in milliseconds.

    Raises:
        ollama.ResponseError : If Ollama returns an API error.
        ConnectionError      : If Ollama is not running on localhost.

    Example:
        text, ms = generate("What is the capital of France?")
        print(text)   # "The capital of France is Paris."
        print(ms)     # 843.2
    """

    client = _get_client()


    messages: list[dict] = []
    if system_prompt:
        messages.append({'role':'system','content':system_prompt})
        
    messages.append({'role':'user','content':prompt})


    # measure latency
    start=time.perf_counter()
    
    try:
        response = client.chat(model=model,messages= messages)

    except ollama.ResponseError as e:
        raise ollama.ResponseError(
            f"Ollama API error for model '{model}': {e}"
        ) from e
    except Exception as e:
        raise ConnectionError(
            f"Could not connect to Ollama at {OLLAMA_BASE_URL}. "
            f"Is Ollama running? Error: {e}"
        ) from e

    end = time.perf_counter()
    latency_ms = (end-start) * 1000


    raw_text = response['message']['content'].strip()
    return raw_text,latency_ms  
    

def embed(text:str)->list[float]:

    """
    Convert text into a numerical embedding vector using nomic-embed-text.

    The vector captures the *meaning* of the text. Similar texts will
    have vectors that are close together in space — this is how ChromaDB
    finds relevant chunks when you search.
    
    Args:
        text : The string to embed (a document chunk or a user query).

    Returns:
        A list of floats representing the embedding vector.
        (nomic-embed-text produces 768-dimensional vectors)

    Example:
        vector = embed("Backpropagation uses the chain rule.")
        print(len(vector))   # 768
        print(vector[:3])    # [-0.021, 0.134, -0.056, ...]
    """

    client = _get_client()

    try:
        response = client.embeddings(
            model=EMBEDDING_MODEL,
            prompt=text
        )
        
    except Exception as e:
        raise ConnectionError(
            f"Could not connect to Ollama at {OLLAMA_BASE_URL}. "
            f"Is Ollama running? Error: {e}"
        ) from e

    return response.embedding


# extract JSON from raw LLM output

def extract_json(raw_text: str) -> str:
    """
    Pull out the JSON object from the model's raw response.

    Models sometimes wrap JSON in markdown fences like:
      ```json
      { ... }
      ```
    """
    # strip markdown code fences first
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()

    # find a raw JSON object { ... }
    brace_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if brace_match:
        return brace_match.group(0).strip()

    return raw_text.strip()
    

def query_structured(
    prompt: str,
    schema: Type[T],
    model: str = DEFAULT_MODEL,
    system_prompt: str | None = None,
    max_retries: int = 3,
) -> tuple[T, float, float, int]:
    """
    Call the LLM and enforce that it returns a valid Pydantic model.

    This is the production-grade pattern:
    - Call the LLM with the prompt
    - Extract JSON from the response
    - Validate it against the schema
    - If invalid → inject the error back into the prompt and retry
    - Repeat up to max_retries times
    - If still failing → raise an exception

    Args:
        prompt      : The user/RAG prompt to send.
        schema      : The Pydantic model class the response must conform to.
        model       : Ollama model to use.
        system_prompt : System instruction (uses SYSTEM_PROMPT from prompts.py if None).
        max_retries : How many times to retry on bad output. Default 3.

    Returns:
        Tuple of (parsed_model, latency_ms, ram_used_mb, retries_used)
        - parsed_model : Validated Pydantic instance (e.g. AnswerResponse)
        - latency_ms   : Total wall-clock time for all LLM calls combined (ms)
        - ram_used_mb  : RAM delta consumed during this call (MB)
        - retries_used : How many retries were needed (0 = first try worked)

    Raises:
        RuntimeError : If the model fails to produce valid JSON after all retries.

    Example:
        from app.model.schema import AnswerResponse
        result, ms, ram, retries = query_structured(prompt, AnswerResponse)
        print(result.answer, result.confidence)
    """
    from app.llm.prompts import build_correction_prompt, SYSTEM_PROMPT

    if system_prompt is None:
        system_prompt = SYSTEM_PROMPT

    # Measure RAM before the call
    process = psutil.Process()
    ram_before_mb = process.memory_info().rss / (1024 * 1024)

    total_latency_ms = 0.0
    current_prompt = prompt
    last_error = ""
    last_response = ""

    for attempt in range(max_retries):

        # On retry: inject the previous error into the prompt
        if attempt > 0:
            current_prompt = build_correction_prompt(
                original_prompt=prompt,
                validation_error=last_error,
                bad_response=last_response,
            )
            print(f"  [Retry {attempt}/{max_retries - 1}] Correcting invalid output...")

        # Call the LLM
        raw_text, latency_ms = generate(
            prompt=current_prompt,
            model=model,
            system_prompt=system_prompt,
        )
        total_latency_ms += latency_ms

        # Extract JSON from the response
        json_str = extract_json(raw_text)
        last_response = raw_text

        # Validate against the Pydantic schema
        try:
            parsed = schema.model_validate_json(json_str)

            # Success — measure RAM delta and return
            ram_after_mb = process.memory_info().rss / (1024 * 1024)
            ram_used_mb = max(0.0, ram_after_mb - ram_before_mb)

            return parsed, total_latency_ms, ram_used_mb, attempt

        except (ValidationError, json.JSONDecodeError, Exception) as e:
            last_error = str(e)
            print(f"  [Attempt {attempt + 1}] Validation failed: {last_error[:120]}")

    # All retries exhausted
    raise RuntimeError(
        f"Model '{model}' failed to produce valid {schema.__name__} "
        f"after {max_retries} attempts.\n"
        f"Last error : {last_error}\n"
        f"Last output: {last_response[:300]}"
    )
