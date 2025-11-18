# LangGraph Node-Level Tool Calling

## Concept Overview

Node-level tool calling in LangGraph allows individual graph nodes to invoke tools directly without waiting for LLM decisions. This pattern enables deterministic tool invocation, parallel tool execution, and decouples tool logic from LLM reasoning. It's essential for building efficient workflows where some decisions don't require AI reasoning but still need access to tools and data sources.

---

## Intermediate Level: Parallel Tool Invocation with Error Recovery

A sophisticated data processing system that invokes multiple tools in parallel with error handling and retry logic.

```python
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from typing import Annotated, Optional
import operator
from datetime import datetime
import asyncio
from enum import Enum

class DataSourceType(str, Enum):
    DATABASE = "database"
    API = "api"
    CACHE = "cache"
    FILE = "file"

class ToolResult(BaseModel):
    """Result from tool invocation."""
    source: DataSourceType
    data: dict
    retrieved_at: str
    status: str  # "success" or "failed"
    error_message: Optional[str] = None
    retry_count: int = 0

class DataEnrichmentState(BaseModel):
    """State for parallel data enrichment."""
    record_id: str
    sources: list[DataSourceType] = Field(default_factory=list)
    tool_results: Annotated[dict[str, ToolResult], operator.add]
    merged_data: dict = Field(default_factory=dict)
    execution_time_ms: int = 0
    status: str = "pending"

class ToolRegistry:
    """Registry for managing tools with caching."""
    def __init__(self):
        self.cache = {}

    async def fetch_from_database(self, record_id: str) -> ToolResult:
        """Fetch from database with caching."""
        cache_key = f"db_{record_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # Simulate DB fetch
            data = {
                "id": record_id,
                "name": "Product X",
                "price": 99.99,
                "stock": 150
            }
            result = ToolResult(
                source=DataSourceType.DATABASE,
                data=data,
                retrieved_at=datetime.now().isoformat(),
                status="success"
            )
            self.cache[cache_key] = result
            return result
        except Exception as e:
            return ToolResult(
                source=DataSourceType.DATABASE,
                data={},
                retrieved_at=datetime.now().isoformat(),
                status="failed",
                error_message=str(e)
            )

    async def fetch_from_api(self, record_id: str) -> ToolResult:
        """Fetch from external API."""
        try:
            # Simulate API call
            data = {
                "reviews": 4.5,
                "review_count": 250,
                "trending": True
            }
            return ToolResult(
                source=DataSourceType.API,
                data=data,
                retrieved_at=datetime.now().isoformat(),
                status="success"
            )
        except Exception as e:
            return ToolResult(
                source=DataSourceType.API,
                data={},
                retrieved_at=datetime.now().isoformat(),
                status="failed",
                error_message=str(e)
            )

    async def fetch_from_cache(self, record_id: str) -> ToolResult:
        """Check cache for recent data."""
        try:
            cached_data = self.cache.get(f"cache_{record_id}")
            if cached_data:
                return ToolResult(
                    source=DataSourceType.CACHE,
                    data=cached_data,
                    retrieved_at=datetime.now().isoformat(),
                    status="success"
                )
            return ToolResult(
                source=DataSourceType.CACHE,
                data={},
                retrieved_at=datetime.now().isoformat(),
                status="success"
            )
        except Exception as e:
            return ToolResult(
                source=DataSourceType.CACHE,
                data={},
                retrieved_at=datetime.now().isoformat(),
                status="failed",
                error_message=str(e)
            )

def create_parallel_enrichment_pipeline():
    """Create pipeline with parallel tool invocation."""
    registry = ToolRegistry()

    async def parallel_fetch_node(state: DataEnrichmentState):
        """Fetch from multiple sources in parallel."""
        tasks = []

        if DataSourceType.DATABASE in state.sources:
            tasks.append(("db", registry.fetch_from_database(state.record_id)))
        if DataSourceType.API in state.sources:
            tasks.append(("api", registry.fetch_from_api(state.record_id)))
        if DataSourceType.CACHE in state.sources:
            tasks.append(("cache", registry.fetch_from_cache(state.record_id)))

        results = {}
        for name, task in tasks:
            results[name] = await task

        return {"tool_results": results}

    def merge_results_node(state: DataEnrichmentState):
        """Merge results from multiple sources."""
        merged = {}
        for source_name, result in state.tool_results.items():
            if result.status == "success":
                merged.update(result.data)

        return {
            "merged_data": merged,
            "status": "completed"
        }

    def handle_failures_node(state: DataEnrichmentState):
        """Handle any failed tool invocations."""
        failed_sources = [
            name for name, result in state.tool_results.items()
            if result.status == "failed"
        ]
        if failed_sources:
            print(f"Warning: Failed to fetch from {failed_sources}")
        return state

    # Build workflow
    workflow = StateGraph(DataEnrichmentState)
    workflow.add_node("fetch", parallel_fetch_node)
    workflow.add_node("merge", merge_results_node)
    workflow.add_node("handle_failures", handle_failures_node)

    workflow.add_edge(START, "fetch")
    workflow.add_conditional_edges(
        "fetch",
        lambda s: "handle_failures" if any(r.status == "failed" for r in s.tool_results.values()) else "merge",
        {"handle_failures": "handle_failures", "merge": "merge"}
    )
    workflow.add_edge("handle_failures", "merge")
    workflow.add_edge("merge", END)

    return workflow.compile()

# Usage (requires asyncio context)
async def main():
    pipeline = create_parallel_enrichment_pipeline()
    initial_state = DataEnrichmentState(
        record_id="prod_001",
        sources=[DataSourceType.DATABASE, DataSourceType.API, DataSourceType.CACHE],
        tool_results={}
    )
    # result = await asyncio.to_thread(pipeline.invoke, initial_state)
    # return result
```

---

## Best Practices for Node-Level Tool Calling Mastery

1. **Decouple Tool Logic from LLM Reasoning**: Use node-level tools for deterministic, data-fetching, or transformation operations. Reserve LLM nodes for decisions requiring reasoning. This separation improves performance and reduces hallucinations.

2. **Implement Intelligent Caching**: Cache tool results by hashing inputs with output signatures. Check cache before invoking tools to reduce redundant calls. Include metadata (cache hit rate, age) in state for optimization decisions.

3. **Model Tool Dependencies Explicitly**: Use topological sorting and dependency graphs to plan tool execution order. Identify parallelizable tools and execute them concurrently. This maximizes efficiency and reduces total execution time.

4. **Quality Gates and Thresholds**: Define quality criteria for tool outputs and validate before using results. Route to fallback tools or handlers when quality thresholds aren't met, preventing garbage-in-garbage-out cascades.

5. **Instrument and Monitor Invocations**: Log all tool invocations with timestamps, inputs, outputs, and durations. Use this data to identify bottlenecks, debug issues, and optimize routing decisions over time.
