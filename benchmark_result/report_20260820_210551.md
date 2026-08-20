# Benchmark Report — Local LLM Comparison

**Models tested:** `phi3:3.8b`
**Total questions:** 5
**Total runs:** 5

## Overall Summary

| Model | Avg Latency | Avg RAM | Success Rate | Avg Confidence | Total Retries |
|-------|------------|---------|--------------|----------------|---------------|
| `phi3:3.8b` | 29935 ms | 0.0 MB | 20% | 100% | 0 |

## Performance by Question Category

| Model | Factual Avg Conf |
|-------|---|
| `phi3:3.8b` | 100% |

## Retry Analysis

*(Retries > 0 means the model returned invalid JSON on the first attempt)*

| Model | Runs needing retry | Max retries in one run | Failed completely |
|-------|-------------------|------------------------|-------------------|
| `phi3:3.8b` | 0 | 0 | 4 |

## Hallucination Check (Out-of-Context Questions)

*These questions have no answer in the documents. The model should say 'I don't know' with confidence ≈ 0.*

| Model | Correct Refusals | Hallucinated | Avg Confidence on OOC |
|-------|-----------------|--------------|------------------------|
| `phi3:3.8b` | 0/0 | 0/0 | 0% |

## Key Observations

*(Fill this in after reviewing results)*

- **Fastest model:** _TBD_
- **Most accurate:** _TBD_
- **Best at refusing out-of-context:** _TBD_
- **Most retries needed:** _TBD_
- **Engineering decision:** _TBD_
