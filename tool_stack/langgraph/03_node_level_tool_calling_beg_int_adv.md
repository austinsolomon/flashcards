# LangGraph Node-Level Tool Calling: Beginner to Advanced

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

## Advanced Level: Conditional Tool Orchestration with Intelligent Routing

An enterprise system that intelligently routes to different tools based on data characteristics, maintains tool state, and handles complex dependencies.

```python
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from typing import Annotated, Optional, Callable, Any, Literal
from datetime import datetime
import operator
from enum import Enum
import hashlib
import json

class DataQuality(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"

class ToolInvocation(BaseModel):
    """Record of a tool invocation."""
    tool_name: str
    input: dict
    output: Any
    status: str
    duration_ms: int
    timestamp: str
    retry_count: int = 0

class ComputeNode(BaseModel):
    """Node in the computation graph."""
    name: str
    tool_name: str
    dependencies: list[str]
    cache_key: Optional[str] = None
    quality_threshold: DataQuality = DataQuality.MEDIUM

class AdvancedToolOrchestrationState(BaseModel):
    """State for advanced tool orchestration."""
    record_id: str
    input_data: dict
    compute_graph: list[ComputeNode]
    execution_plan: list[str] = Field(default_factory=list)
    tool_results: Annotated[dict[str, Any], operator.add]
    tool_invocations: Annotated[list[ToolInvocation], operator.add]
    data_quality_scores: dict[str, DataQuality] = Field(default_factory=dict)
    execution_status: str = "pending"
    optimization_metadata: dict = Field(default_factory=dict)

class IntelligentToolOrchestrator:
    """Orchestrates complex tool dependencies and routing."""
    def __init__(self):
        self.tool_registry: dict[str, Callable] = {}
        self.result_cache: dict[str, Any] = {}
        self.quality_estimator = self._build_quality_estimator()

    def _build_quality_estimator(self) -> Callable:
        """Build a function to estimate data quality."""
        def estimate_quality(data: dict) -> DataQuality:
            completeness = len(data) / 10  # Assume 10 fields is complete
            if completeness >= 0.8:
                return DataQuality.HIGH
            elif completeness >= 0.5:
                return DataQuality.MEDIUM
            return DataQuality.LOW
        return estimate_quality

    async def resolve_dependencies(
        self,
        state: AdvancedToolOrchestrationState
    ) -> list[str]:
        """Topologically sort compute nodes by dependencies."""
        graph = {node.name: node.dependencies for node in state.compute_graph}
        result = []
        visited = set()

        def visit(node_name: str):
            if node_name in visited:
                return
            visited.add(node_name)
            if node_name in graph:
                for dep in graph[node_name]:
                    visit(dep)
            result.append(node_name)

        for node in state.compute_graph:
            visit(node.name)

        return result

    def get_cache_key(self, tool_name: str, input_data: dict) -> str:
        """Generate cache key for tool result."""
        data_str = json.dumps(input_data, sort_keys=True)
        hash_obj = hashlib.sha256(f"{tool_name}:{data_str}".encode())
        return hash_obj.hexdigest()

    async def invoke_tool(
        self,
        tool_name: str,
        input_data: dict,
        quality_threshold: DataQuality
    ) -> ToolInvocation:
        """Invoke a tool with caching and quality checks."""
        cache_key = self.get_cache_key(tool_name, input_data)

        # Check cache
        if cache_key in self.result_cache:
            cached_result = self.result_cache[cache_key]
            return ToolInvocation(
                tool_name=tool_name,
                input=input_data,
                output=cached_result,
                status="success_cached",
                duration_ms=0,
                timestamp=datetime.now().isoformat()
            )

        # Simulate tool execution
        try:
            import time
            start = time.time()
            output = {"result": f"computed_{tool_name}", "timestamp": datetime.now().isoformat()}
            duration = int((time.time() - start) * 1000)

            # Estimate quality
            quality = self.quality_estimator(output)
            if quality.value < quality_threshold.value:
                raise ValueError(f"Quality {quality} below threshold {quality_threshold}")

            # Cache result
            self.result_cache[cache_key] = output

            return ToolInvocation(
                tool_name=tool_name,
                input=input_data,
                output=output,
                status="success",
                duration_ms=duration,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return ToolInvocation(
                tool_name=tool_name,
                input=input_data,
                output=None,
                status="failed",
                duration_ms=0,
                timestamp=datetime.now().isoformat(),
                retry_count=0
            )

def create_advanced_orchestration_system():
    """Create advanced tool orchestration system."""
    orchestrator = IntelligentToolOrchestrator()

    async def plan_execution(state: AdvancedToolOrchestrationState):
        """Plan execution order based on dependencies."""
        plan = await orchestrator.resolve_dependencies(state)
        return {
            "execution_plan": plan,
            "optimization_metadata": {
                "nodes_to_execute": len(plan),
                "plan_generated_at": datetime.now().isoformat()
            }
        }

    async def execute_tools(state: AdvancedToolOrchestrationState):
        """Execute tools according to plan."""
        results = {}
        invocations = []

        for node_name in state.execution_plan:
            node = next(n for n in state.compute_graph if n.name == node_name)

            # Gather dependency outputs
            dep_data = {dep: results.get(dep) for dep in node.dependencies}

            # Invoke tool
            invocation = await orchestrator.invoke_tool(
                node.tool_name,
                dep_data,
                node.quality_threshold
            )
            results[node_name] = invocation.output
            invocations.append(invocation)

        return {
            "tool_results": results,
            "tool_invocations": invocations
        }

    async def evaluate_quality(state: AdvancedToolOrchestrationState):
        """Evaluate overall data quality."""
        quality_scores = {}
        for result_name, result in state.tool_results.items():
            if result:
                quality_scores[result_name] = orchestrator.quality_estimator(result)
            else:
                quality_scores[result_name] = DataQuality.UNKNOWN

        return {
            "data_quality_scores": quality_scores,
            "execution_status": "completed"
        }

    # Build workflow
    workflow = StateGraph(AdvancedToolOrchestrationState)
    workflow.add_node("plan", plan_execution)
    workflow.add_node("execute", execute_tools)
    workflow.add_node("evaluate", evaluate_quality)

    workflow.add_edge(START, "plan")
    workflow.add_edge("plan", "execute")
    workflow.add_edge("execute", "evaluate")
    workflow.add_edge("evaluate", END)

    return workflow.compile()

# Usage
async def main():
    system = create_advanced_orchestration_system()

    compute_graph = [
        ComputeNode(
            name="fetch_user",
            tool_name="database_fetch",
            dependencies=[],
            quality_threshold=DataQuality.HIGH
        ),
        ComputeNode(
            name="fetch_purchase_history",
            tool_name="api_fetch",
            dependencies=["fetch_user"],
            quality_threshold=DataQuality.MEDIUM
        ),
        ComputeNode(
            name="predict_churn",
            tool_name="ml_model",
            dependencies=["fetch_purchase_history"],
            quality_threshold=DataQuality.MEDIUM
        ),
    ]

    initial_state = AdvancedToolOrchestrationState(
        record_id="user_001",
        input_data={"user_id": "user_001"},
        compute_graph=compute_graph,
        tool_results={}
    )
    # result = await asyncio.to_thread(system.invoke, initial_state)
```

---

## Best Practices for Node-Level Tool Calling Mastery

1. **Decouple Tool Logic from LLM Reasoning**: Use node-level tools for deterministic, data-fetching, or transformation operations. Reserve LLM nodes for decisions requiring reasoning. This separation improves performance and reduces hallucinations.

2. **Implement Intelligent Caching**: Cache tool results by hashing inputs with output signatures. Check cache before invoking tools to reduce redundant calls. Include metadata (cache hit rate, age) in state for optimization decisions.

3. **Model Tool Dependencies Explicitly**: Use topological sorting and dependency graphs to plan tool execution order. Identify parallelizable tools and execute them concurrently. This maximizes efficiency and reduces total execution time.

4. **Quality Gates and Thresholds**: Define quality criteria for tool outputs and validate before using results. Route to fallback tools or handlers when quality thresholds aren't met, preventing garbage-in-garbage-out cascades.

5. **Instrument and Monitor Invocations**: Log all tool invocations with timestamps, inputs, outputs, and durations. Use this data to identify bottlenecks, debug issues, and optimize routing decisions over time.
