from __future__ import annotations

import time
import ollama

# from app.config import OLLAMA_BASE_URL,DEFAULT_MODEL,EMBEDDING_MODEL
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


# if __name__ == "__main__":

    # print(f"Testing generate() with model: {DEFAULT_MODEL}")
    # print("Prompt: 'Say hello in exactly one sentence.'\n")

    # try:
    #     text, ms = generate(
    #         prompt="Say hello in exactly one sentence.",
    #         system_prompt="You are a helpful assistant. Always reply briefly.",
    #     )
    #     print(f"Response : {text.strip()}")
    #     print(f"Latency  : {ms:.1f} ms")
    #     print("[OK] generate() works!\n")
    # except ConnectionError as e:
    #     print(f"[ERROR] Connection failed: {e}")
    #     print("-> Make sure Ollama is running: open a terminal and run 'ollama serve'")
    #     exit(1)

    # # testing embeding model
    # print(f"Testing embed() with model: {EMBEDDING_MODEL}")
    # print("Text: 'Machine learning is a subset of AI.'\n")

    # try:
    #     vector = embed("Machine learning is a subset of AI.")
    #     print(f"Vector dimensions : {len(vector)}")
    #     print(f"First 5 values    : {[round(v, 4) for v in vector[:5]]}")
    #     print("[OK] embed() works!\n")
    # except Exception as e:
    #     print(f"[ERROR] Embedding failed: {e}")
    #     print(f"-> Make sure nomic-embed-text is pulled: ollama pull {EMBEDDING_MODEL}")

    # print("=== All tests done ===")
