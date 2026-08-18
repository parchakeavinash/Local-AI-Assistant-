import ollama     

response = ollama.generate(
    model = 'phi3:3.8b',
    prompt = 'what is agentic memory in one sentence..'
)

print(response["response"])