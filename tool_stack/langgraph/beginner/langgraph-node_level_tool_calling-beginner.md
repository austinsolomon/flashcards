# LangGraph Node-Level Tool Calling

## Concept Overview

Node-level tool calling in LangGraph allows individual graph nodes to invoke tools directly without waiting for LLM decisions. This pattern enables deterministic tool invocation, parallel tool execution, and decouples tool logic from LLM reasoning. It's essential for building efficient workflows where some decisions don't require AI reasoning but still need access to tools and data sources.

---

## Beginner Level: Simple Node-Based Tool Invocation

A data pipeline that fetches and processes data using tools called directly by nodes.

```python
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from typing import Annotated
import operator

class DataPipelineState(BaseModel):
    user_id: str
    raw_data: dict
    processed_data: dict
    error: str = ""

# Define tools
def fetch_user_data(user_id: str) -> dict:
    """Fetch user data from database."""
    return {
        "id": user_id,
        "name": "John Doe",
        "email": "john@example.com",
        "created_at": "2024-01-15"
    }

def enrich_user_data(user_data: dict) -> dict:
    """Add computed fields to user data."""
    return {
        **user_data,
        "account_age_days": 300,
        "status": "active"
    }

def validate_data(data: dict) -> bool:
    """Validate data integrity."""
    required_fields = ["id", "name", "email"]
    return all(field in data for field in required_fields)

def create_simple_pipeline():
    """Create a simple data processing pipeline."""

    def fetch_node(state: DataPipelineState):
        """Fetch raw data."""
        raw_data = fetch_user_data(state.user_id)
        return {"raw_data": raw_data}

    def enrich_node(state: DataPipelineState):
        """Enrich the data."""
        enriched = enrich_user_data(state.raw_data)
        return {"processed_data": enriched}

    def validate_node(state: DataPipelineState):
        """Validate processed data."""
        is_valid = validate_data(state.processed_data)
        if not is_valid:
            return {"error": "Data validation failed"}
        return {"error": ""}

    # Build workflow
    workflow = StateGraph(DataPipelineState)
    workflow.add_node("fetch", fetch_node)
    workflow.add_node("enrich", enrich_node)
    workflow.add_node("validate", validate_node)

    workflow.add_edge(START, "fetch")
    workflow.add_edge("fetch", "enrich")
    workflow.add_edge("enrich", "validate")
    workflow.add_edge("validate", END)

    return workflow.compile()

# Usage
pipeline = create_simple_pipeline()
result = pipeline.invoke(DataPipelineState(user_id="user_123", raw_data={}, processed_data={}))
print(result.processed_data)
```

---

## Best Practices for Node-Level Tool Calling Mastery

1. **Decouple Tool Logic from LLM Reasoning**: Use node-level tools for deterministic, data-fetching, or transformation operations. Reserve LLM nodes for decisions requiring reasoning. This separation improves performance and reduces hallucinations.

2. **Implement Intelligent Caching**: Cache tool results by hashing inputs with output signatures. Check cache before invoking tools to reduce redundant calls. Include metadata (cache hit rate, age) in state for optimization decisions.

3. **Model Tool Dependencies Explicitly**: Use topological sorting and dependency graphs to plan tool execution order. Identify parallelizable tools and execute them concurrently. This maximizes efficiency and reduces total execution time.

4. **Quality Gates and Thresholds**: Define quality criteria for tool outputs and validate before using results. Route to fallback tools or handlers when quality thresholds aren't met, preventing garbage-in-garbage-out cascades.

5. **Instrument and Monitor Invocations**: Log all tool invocations with timestamps, inputs, outputs, and durations. Use this data to identify bottlenecks, debug issues, and optimize routing decisions over time.
