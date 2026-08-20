# Benchmark Report — Local LLM Comparison

**Models tested:** `llama3.2:3b`, `mistral:7b`, `phi3:3.8b`
**Total questions:** 50
**Total runs:** 150

## Overall Summary

| Model | Avg Latency | Avg RAM | Success Rate | Avg Confidence | Total Retries |
|-------|------------|---------|--------------|----------------|---------------|
| `llama3.2:3b` | 17731 ms | 0.6 MB | 78% | 81% | 33 |
| `mistral:7b` | 51214 ms | 0.2 MB | 90% | 82% | 16 |
| `phi3:3.8b` | 27903 ms | 0.1 MB | 80% | 84% | 31 |

## Performance by Question Category

| Model | Application Avg Conf | Conceptual Avg Conf | Factual Avg Conf | Out Of Context Avg Conf |
|-------|---|---|---|---|
| `llama3.2:3b` | 82% | 90% | 92% | 0% |
| `mistral:7b` | 99% | 93% | 90% | 0% |
| `phi3:3.8b` | 89% | 98% | 100% | 17% |

## Retry Analysis

*(Retries > 0 means the model returned invalid JSON on the first attempt)*

| Model | Runs needing retry | Max retries in one run | Failed completely |
|-------|-------------------|------------------------|-------------------|
| `llama3.2:3b` | 11 | 3 | 11 |
| `mistral:7b` | 6 | 3 | 5 |
| `phi3:3.8b` | 11 | 3 | 10 |

## Hallucination Check (Out-of-Context Questions)

*These questions have no answer in the documents. The model should say 'I don't know' with confidence ~0.*

| Model | Correct Refusals | Hallucinated | Avg Confidence on OOC |
|-------|-----------------|--------------|------------------------|
| `llama3.2:3b` | 6/6 | 0/6 | 0% |
| `mistral:7b` | 6/6 | 0/6 | 0% |
| `phi3:3.8b` | 5/6 | 1/6 | 17% |

## Key Observations

*(Fill this in after reviewing results)*

- **Fastest model:** _TBD_
- **Most accurate:** _TBD_
- **Best at refusing out-of-context:** _TBD_
- **Most retries needed:** _TBD_
- **Engineering decision:** _TBD_
