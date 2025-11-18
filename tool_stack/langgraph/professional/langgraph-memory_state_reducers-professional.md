# LangGraph Memory & State Reducers

## Concept Overview

State reducers define how state updates are merged into existing state. Instead of replacing fields, reducers combine old and new values intelligently. This is critical for managing growing state (like conversation history), implementing memory management patterns, and preventing state bloat in long-running workflows. Reducers enable append-only semantics, deduplication, summarization, and other transformations.

---

## Intermediate Level: Custom Reducers with Deduplication and Filtering

A sophisticated state management system with custom reducers for intelligent merging.

```python
from langgraph.graph import StateGraph, START, END, add_messages
from pydantic import BaseModel, Field
from typing import Annotated, Any, Callable
from datetime import datetime
import operator

class Event(BaseModel):
    """Timestamped event in the system."""
    event_id: str
    event_type: str
    timestamp: str
    data: dict
    priority: int = 0

class DeduplicatedState(BaseModel):
    """State with deduplication logic."""
    workflow_id: str
    # Standard message reducer
    messages: Annotated[list[str], add_messages] = Field(default_factory=list)
    # Custom reducer for deduplication
    events: Annotated[list[Event], lambda items, new_items: (
        items + [
            item for item in new_items
            if not any(item.event_id == existing.event_id for existing in items)
        ]
    )] = Field(default_factory=list)
    # Count with max reducer
    processed_count: Annotated[int, max] = 0

def create_custom_reducer_workflow():
    """Create workflow with custom reducers."""

    def add_events_batch_1(state: DeduplicatedState):
        """Add first batch of events."""
        events = [
            Event(
                event_id="evt_001",
                event_type="data_received",
                timestamp=datetime.now().isoformat(),
                data={"items": 10},
                priority=1
            ),
            Event(
                event_id="evt_002",
                event_type="validation_started",
                timestamp=datetime.now().isoformat(),
                data={"rules": 5},
                priority=1
            )
        ]
        return {
            "events": events,
            "messages": ["Batch 1: 2 events added"]
        }

    def add_events_batch_2(state: DeduplicatedState):
        """Add second batch (with duplicate)."""
        events = [
            Event(
                event_id="evt_001",  # Duplicate - will be filtered
                event_type="data_received",
                timestamp=datetime.now().isoformat(),
                data={"items": 10},
                priority=1
            ),
            Event(
                event_id="evt_003",
                event_type="validation_complete",
                timestamp=datetime.now().isoformat(),
                data={"passed": True},
                priority=1
            )
        ]
        return {
            "events": events,
            "messages": ["Batch 2: 2 events processed (1 duplicate filtered)"],
            "processed_count": state.processed_count + 1
        }

    def add_events_batch_3(state: DeduplicatedState):
        """Add third batch."""
        events = [
            Event(
                event_id="evt_004",
                event_type="processing_complete",
                timestamp=datetime.now().isoformat(),
                data={"result": "success"},
                priority=2
            )
        ]
        return {
            "events": events,
            "messages": ["Batch 3: 1 high-priority event added"],
            "processed_count": state.processed_count + 1
        }

    # Build workflow
    workflow = StateGraph(DeduplicatedState)
    workflow.add_node("batch1", add_events_batch_1)
    workflow.add_node("batch2", add_events_batch_2)
    workflow.add_node("batch3", add_events_batch_3)

    workflow.add_edge(START, "batch1")
    workflow.add_edge("batch1", "batch2")
    workflow.add_edge("batch2", "batch3")
    workflow.add_edge("batch3", END)

    return workflow.compile()

# Usage
workflow = create_custom_reducer_workflow()
result = workflow.invoke(DeduplicatedState(workflow_id="wf_001"))
print(f"Unique events: {len(result.events)}")
print(f"Messages: {result.messages}")
print(f"Event IDs: {[e.event_id for e in result.events]}")
```

---

## Best Practices for Memory & State Reducers Mastery

1. **Choose Appropriate Reducers**: Use `operator.add` for simple accumulation. Define custom reducers for deduplication, filtering, or summarization. Match reducer semantics to domain semantics (e.g., append for history, max for scores).

2. **Implement Bounded Memory**: Set maximum limits on state field sizes. When limits approached, trigger reduction strategies (summarization, pruning, archival). Monitor memory pressure and act before hitting hard limits.

3. **Dual-Memory Architectures**: Implement short-term (working) memory for immediate context and long-term memory for reference. Automatically promote important short-term items to long-term. This balances responsiveness with retention.

4. **Intelligent Summarization**: When reducing memories, create summaries capturing key information. Track summary quality metrics. Use summaries as compressed representations while retaining full originals separately for verification.

5. **Track Memory Metadata**: Record relevance scores, access patterns, age, and semantic similarity. Use this to inform reduction decisions. Prefer keeping high-relevance, frequently-accessed, recent items while pruning low-value older items.
