# LangGraph Streaming & Partial State Updates

## Concept Overview

Streaming and partial state updates enable real-time feedback and efficient state mutations without processing entire state objects. This pattern is critical for building responsive UIs, handling large states, and optimizing bandwidth. Instead of returning complete state snapshots, nodes emit only changed fields, allowing incremental updates to propagate to clients immediately.

---

## Intermediate Level: Partial State Updates with Incremental Changes

A streaming system that emits partial updates as individual fields change.

```python
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from typing import Annotated, Optional, Any
import operator
from datetime import datetime

class ProgressUpdate(BaseModel):
    """Partial state update."""
    field: str
    value: Any
    timestamp: str
    progress_percent: int

class StreamingProcessState(BaseModel):
    """State with streaming updates."""
    task_id: str
    input_data: str
    processing_steps: list[str] = Field(default_factory=list)
    progress_updates: Annotated[list[ProgressUpdate], operator.add]
    extracted_features: dict = Field(default_factory=dict)
    analysis_results: Optional[str] = None
    current_step: str = "idle"
    completion_percent: int = 0

def create_streaming_updates_workflow():
    """Create workflow with partial state streaming."""

    def preprocess_step(state: StreamingProcessState):
        """Preprocessing with streaming updates."""
        updates = []

        # Update 1: Started preprocessing
        updates.append(ProgressUpdate(
            field="current_step",
            value="preprocessing",
            timestamp=datetime.now().isoformat(),
            progress_percent=10
        ))

        # Update 2: Parsing data
        updates.append(ProgressUpdate(
            field="current_step",
            value="parsing_input",
            timestamp=datetime.now().isoformat(),
            progress_percent=20
        ))

        # Update 3: Finished preprocessing
        updates.append(ProgressUpdate(
            field="current_step",
            value="preprocessing_complete",
            timestamp=datetime.now().isoformat(),
            progress_percent=30
        ))

        return {
            "progress_updates": updates,
            "processing_steps": ["preprocessing"],
            "completion_percent": 30,
            "current_step": "preprocessing_complete"
        }

    def feature_extraction_step(state: StreamingProcessState):
        """Feature extraction with partial updates."""
        updates = []
        features = {}

        # Stream feature extractions
        for i, feature in enumerate(["feature_1", "feature_2", "feature_3"]):
            features[feature] = f"value_{i}"
            progress = 30 + ((i + 1) / 3 * 25)

            updates.append(ProgressUpdate(
                field="extracted_features",
                value={feature: f"value_{i}"},
                timestamp=datetime.now().isoformat(),
                progress_percent=int(progress)
            ))

        return {
            "progress_updates": updates,
            "extracted_features": features,
            "processing_steps": state.processing_steps + ["feature_extraction"],
            "completion_percent": 55
        }

    def analysis_step(state: StreamingProcessState):
        """Analysis with streaming updates."""
        updates = []

        analysis_stages = [
            ("correlation_analysis", 60),
            ("statistical_summary", 75),
            ("insight_generation", 90),
            ("report_compilation", 100)
        ]

        for stage, progress in analysis_stages:
            updates.append(ProgressUpdate(
                field="analysis_results",
                value=f"Completed {stage}",
                timestamp=datetime.now().isoformat(),
                progress_percent=progress
            ))

        return {
            "progress_updates": updates,
            "analysis_results": "Analysis complete",
            "processing_steps": state.processing_steps + ["analysis"],
            "completion_percent": 100,
            "current_step": "complete"
        }

    # Build workflow
    workflow = StateGraph(StreamingProcessState)
    workflow.add_node("preprocess", preprocess_step)
    workflow.add_node("extract", feature_extraction_step)
    workflow.add_node("analyze", analysis_step)

    workflow.add_edge(START, "preprocess")
    workflow.add_edge("preprocess", "extract")
    workflow.add_edge("extract", "analyze")
    workflow.add_edge("analyze", END)

    return workflow.compile()

# Usage
workflow = create_streaming_updates_workflow()
state = StreamingProcessState(
    task_id="task_001",
    input_data="sample data",
    progress_updates=[]
)
result = workflow.invoke(state)

# Print progress updates as they were streamed
for update in result.progress_updates:
    print(f"[{update.progress_percent}%] {update.field}: {update.value}")
```

---

## Best Practices for Streaming & Partial State Updates Mastery

1. **Diff-Based Updates**: Compute and transmit only state changes, not complete state objects. Use JSON-path notation to identify changed fields. This dramatically reduces bandwidth and latency in high-frequency update scenarios.

2. **Client Subscription Filtering**: Let clients specify which state paths they care about. Filter diffs server-side before streaming. This reduces unnecessary updates and improves client performance.

3. **Buffering and Batching**: Don't stream every atomic change individually. Buffer diffs and batch them into coherent update packets. Balance between latency (smaller batches) and efficiency (larger batches).

4. **State Hash Tracking**: Compute hashes of full state snapshots. Use hashes to detect when client state diverges from server. Enable client-side caching and efficient resync mechanisms.

5. **Progressive Streaming Feedback**: For long-running operations, emit progress updates as partial state changes. Show intermediate results, progress percentages, and incremental improvements in real-time rather than waiting for completion.
