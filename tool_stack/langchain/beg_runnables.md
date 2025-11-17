# Runnables - Beginner

## Concept Overview

Runnables are the fundamental building blocks of LangChain. Every component that can be invoked (LLMs, prompts, retrievers, custom functions) implements the `Runnable` interface. This provides a unified API with standard methods: `invoke()`, `batch()`, `stream()`, and their async variants.

**Why it matters:** Understanding Runnables means you can create custom components that integrate seamlessly with LangChain's ecosystem. You get automatic support for batching, streaming, async execution, and composition without writing boilerplate code.

## Real-World Example: Custom Content Moderation Pipeline

This example shows how to build a sophisticated content moderation system using custom Runnables that can be composed with LLMs and other components.

```python
from langchain_core.runnables import RunnableLambda, RunnableParallel, Runnable
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import Dict, List, Any
import re
from datetime import datetime

# Custom Runnable for PII detection
class PIIDetector(Runnable):
    """Detects and masks personally identifiable information."""

    def __init__(self):
        self.patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        }

    def invoke(self, input: Dict[str, Any], config=None) -> Dict[str, Any]:
        text = input.get("text", "")
        detected_pii = []
        masked_text = text

        for pii_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                detected_pii.append({
                    "type": pii_type,
                    "count": len(matches),
                    "examples": matches[:2]  # Only log first 2 for security
                })
                # Mask the PII
                masked_text = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", masked_text)

        return {
            **input,
            "text": masked_text,
            "original_text": text,
            "pii_detected": detected_pii,
            "has_pii": len(detected_pii) > 0
        }

# Custom Runnable for profanity scoring
class ProfanityScorer(Runnable):
    """Scores text for profanity and toxic language."""

    def __init__(self):
        # In production, use a proper library like 'better-profanity' or API
        self.toxic_words = {"damn", "hell", "stupid", "hate", "kill", "death"}

    def invoke(self, input: Dict[str, Any], config=None) -> Dict[str, Any]:
        text = input.get("text", "").lower()
        words = set(text.split())

        toxic_matches = words & self.toxic_words
        toxicity_score = len(toxic_matches) / max(len(words), 1) * 100

        return {
            **input,
            "toxicity_score": round(toxicity_score, 2),
            "toxic_words_found": list(toxic_matches),
            "is_toxic": toxicity_score > 5.0
        }

# Custom Runnable for AI content analysis
class AIContentAnalyzer(Runnable):
    """Uses LLM to analyze content for policy violations."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.prompt = ChatPromptTemplate.from_template("""
Analyze this content for policy violations. Check for:
- Spam or promotional content
- Misinformation or false claims
- Harassment or bullying
- Inappropriate content for general audience

Content: {text}

Respond in JSON format:
{{
  "is_compliant": true/false,
  "violations": ["list of specific violations"],
  "severity": "low/medium/high",
  "recommendation": "approve/flag/reject"
}}
""")
        self.parser = JsonOutputParser()

    def invoke(self, input: Dict[str, Any], config=None) -> Dict[str, Any]:
        chain = self.prompt | self.llm | self.parser
        analysis = chain.invoke({"text": input.get("text", "")})

        return {
            **input,
            "ai_analysis": analysis
        }

# Custom Runnable for final decision aggregation
class ModerationDecision(Runnable):
    """Aggregates all moderation signals into a final decision."""

    def invoke(self, input: Dict[str, Any], config=None) -> Dict[str, Any]:
        # Decision logic
        if input.get("has_pii"):
            decision = "reject"
            reason = "Contains PII that must be removed"
        elif input.get("is_toxic"):
            decision = "flag"
            reason = f"High toxicity score: {input.get('toxicity_score')}%"
        elif not input.get("ai_analysis", {}).get("is_compliant", True):
            ai_rec = input.get("ai_analysis", {}).get("recommendation", "flag")
            decision = ai_rec
            reason = f"AI detected violations: {input.get('ai_analysis', {}).get('violations', [])}"
        else:
            decision = "approve"
            reason = "All checks passed"

        return {
            **input,
            "moderation_decision": decision,
            "decision_reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "reviewed_by": "automated_system"
        }

# Compose everything into a moderation pipeline
moderation_pipeline = (
    # Stage 1: Parallel detection
    RunnableParallel({
        "pii_check": PIIDetector(),
        "profanity_check": ProfanityScorer(),
        "original": RunnableLambda(lambda x: x)
    })
    # Stage 2: Merge results
    | RunnableLambda(lambda x: {
        **x["original"],
        **x["pii_check"],
        **x["profanity_check"]
    })
    # Stage 3: AI analysis on masked text
    | AIContentAnalyzer()
    # Stage 4: Final decision
    | ModerationDecision()
)

# Test with real-world content
test_content = """
Hey everyone! I found this amazing deal! Contact me at john.doe@email.com
or call 555-123-4567 to get started. This is not a scam, I promise!
You'd be stupid to miss out on this opportunity!
"""

result = moderation_pipeline.invoke({"text": test_content})

print(f"Decision: {result['moderation_decision']}")
print(f"Reason: {result['decision_reason']}")
print(f"\nPII Detected: {result['pii_detected']}")
print(f"Toxicity Score: {result['toxicity_score']}%")
print(f"AI Analysis: {result['ai_analysis']}")
```

### Batch Processing Example:

```python
# Process multiple pieces of content efficiently
test_batch = [
    {"text": "This is a normal, appropriate comment."},
    {"text": "Email me at secret@company.com for insider info!"},
    {"text": "I hate this product, it's garbage and stupid!"},
]

# Batch processing runs in parallel automatically
results = moderation_pipeline.batch(test_batch)

for i, result in enumerate(results):
    print(f"\nContent {i+1}: {result['moderation_decision']}")
    print(f"Reason: {result['decision_reason']}")
```

### Why This Example Shows Runnable's Power:

1. **Custom Logic Integration**: Your own Python classes become first-class LangChain components
2. **Automatic Batching**: The `.batch()` method works out of the box for parallel processing
3. **Composability**: Custom Runnables combine seamlessly with LLMs, prompts, and parsers
4. **Unified Interface**: Everything uses the same `invoke()`, `batch()`, `stream()` API
5. **Config Propagation**: Configuration (timeouts, callbacks, tags) flows through the entire chain

## Best Practices for Mastering Runnables

1. **Always extend the Runnable base class for custom components**: This ensures your components get all the standard methods (`batch`, `stream`, `ainvoke`) automatically. Implement just `invoke()` and the rest comes free.

2. **Design Runnables to be stateless and pure**: Each invocation should be independent. Store configuration in `__init__`, but don't maintain state between invocations. This enables safe parallel execution and caching.

3. **Use RunnableLambda for simple transformations**: When you need a quick function in a chain, wrap it with `RunnableLambda`. But for complex logic or reusable components, create a proper Runnable class for better maintainability.

4. **Pass through input data with spread operators**: Use `{**input, new_key: new_value}` to preserve all upstream data while adding new fields. This makes chains composable and prevents data loss between steps.

5. **Leverage RunnableParallel for I/O-bound operations**: Any time you have multiple independent API calls, database queries, or LLM invocations, wrap them in `RunnableParallel` to execute concurrently and dramatically reduce total latency.

## Common Pitfalls to Avoid

- **Don't block in Runnables**: Avoid blocking operations; use async variants (`ainvoke`) for I/O operations
- **Avoid mutable shared state**: Never use class variables that change; it breaks parallelization
- **Don't swallow errors**: Let exceptions propagate or handle them explicitly with try/except
- **Remember the config parameter**: Always accept `config` in `invoke()` even if unused; it's required for callbacks and other features
