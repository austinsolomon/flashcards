# LangGraph Memory & State Reducers: Beginner to Advanced

## Concept Overview

State reducers define how state updates are merged into existing state. Instead of replacing fields, reducers combine old and new values intelligently. This is critical for managing growing state (like conversation history), implementing memory management patterns, and preventing state bloat in long-running workflows. Reducers enable append-only semantics, deduplication, summarization, and other transformations.

---

## Beginner Level: Simple List Appending with Operator.Add

A basic example using the standard `operator.add` reducer for message accumulation.

```python
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from typing import Annotated
import operator

class SimpleMessageState(BaseModel):
    messages: Annotated[list[str], operator.add]
    count: int = 0

def create_simple_message_workflow():
    """Create workflow with simple message reducer."""

    def add_message_1(state: SimpleMessageState):
        """Add first message."""
        return {
            "messages": ["Message 1: Processing started"],
            "count": 1
        }

    def add_message_2(state: SimpleMessageState):
        """Add second message."""
        return {
            "messages": ["Message 2: Data validated"],
            "count": state.count + 1
        }

    def add_message_3(state: SimpleMessageState):
        """Add third message."""
        return {
            "messages": ["Message 3: Operation completed"],
            "count": state.count + 1
        }

    # Build workflow
    workflow = StateGraph(SimpleMessageState)
    workflow.add_node("step1", add_message_1)
    workflow.add_node("step2", add_message_2)
    workflow.add_node("step3", add_message_3)

    workflow.add_edge(START, "step1")
    workflow.add_edge("step1", "step2")
    workflow.add_edge("step2", "step3")
    workflow.add_edge("step3", END)

    return workflow.compile()

# Usage
workflow = create_simple_message_workflow()
result = workflow.invoke(SimpleMessageState(messages=[]))
print(f"Total messages: {len(result.messages)}")
print("Messages:", result.messages)
```

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

## Advanced Level: Sophisticated Memory Management with Summarization and Pruning

A production system with advanced memory management, automatic summarization, and intelligent state pruning.

```python
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from typing import Annotated, Optional, Callable, Any
from datetime import datetime, timedelta
from enum import Enum
import operator
import json
from abc import ABC, abstractmethod

class MemoryType(str, Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    SEMANTIC = "semantic"

class MemoryItem(BaseModel):
    """Individual memory item."""
    item_id: str
    memory_type: MemoryType
    content: str
    timestamp: str
    relevance_score: float = 1.0
    access_count: int = 0
    last_accessed: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

class MemorySummary(BaseModel):
    """Condensed memory summary."""
    summary_id: str
    original_items: list[str]  # IDs of items summarized
    summary_text: str
    created_at: str
    representative_score: float

class AdvancedMemoryState(BaseModel):
    """State with sophisticated memory management."""
    session_id: str
    short_term_memory: Annotated[list[MemoryItem], operator.add]
    long_term_memory: Annotated[list[MemoryItem], operator.add]
    summaries: Annotated[list[MemorySummary], operator.add]
    memory_stats: dict = Field(default_factory=dict)
    memory_pressure: float = 0.0  # 0-1 indicating memory usage

class MemoryReducer(ABC):
    """Base class for memory reduction strategies."""
    @abstractmethod
    def reduce(
        self,
        existing_memories: list[MemoryItem],
        new_memories: list[MemoryItem],
        max_items: int
    ) -> tuple[list[MemoryItem], Optional[MemorySummary]]:
        """Reduce memories to fit constraints."""
        pass

class SummarizationReducer(MemoryReducer):
    """Reduces memory by summarizing old items."""
    def reduce(
        self,
        existing_memories: list[MemoryItem],
        new_memories: list[MemoryItem],
        max_items: int
    ) -> tuple[list[MemoryItem], Optional[MemorySummary]]:
        """Summarize old memories when limit exceeded."""
        combined = existing_memories + new_memories

        if len(combined) <= max_items:
            return combined, None

        # Summarize oldest items
        items_to_summarize = combined[:len(combined) - max_items]
        items_to_keep = combined[len(combined) - max_items:]

        # Create summary
        summary_text = f"Summarized {len(items_to_summarize)} items"
        summary = MemorySummary(
            summary_id=f"sum_{datetime.now().timestamp()}",
            original_items=[item.item_id for item in items_to_summarize],
            summary_text=summary_text,
            created_at=datetime.now().isoformat(),
            representative_score=0.85
        )

        return items_to_keep, summary

class RelevancePruner(MemoryReducer):
    """Prunes low-relevance items."""
    def reduce(
        self,
        existing_memories: list[MemoryItem],
        new_memories: list[MemoryItem],
        max_items: int
    ) -> tuple[list[MemoryItem], Optional[MemorySummary]]:
        """Keep only high-relevance items."""
        combined = existing_memories + new_memories

        # Sort by relevance
        sorted_memories = sorted(
            combined,
            key=lambda x: x.relevance_score,
            reverse=True
        )

        # Keep top items
        return sorted_memories[:max_items], None

class MemoryManager:
    """Manages memory lifecycle and reduction."""
    def __init__(self, max_short_term: int = 50, max_long_term: int = 200):
        self.max_short_term = max_short_term
        self.max_long_term = max_long_term
        self.short_term_reducer = SummarizationReducer()
        self.long_term_reducer = RelevancePruner()

    def compute_memory_pressure(
        self,
        short_term_count: int,
        long_term_count: int
    ) -> float:
        """Compute memory pressure (0-1)."""
        short_term_usage = short_term_count / self.max_short_term
        long_term_usage = long_term_count / self.max_long_term
        return (short_term_usage * 0.6 + long_term_usage * 0.4)

    def process_short_term_memory(
        self,
        state: AdvancedMemoryState,
        new_items: list[MemoryItem]
    ) -> tuple[list[MemoryItem], Optional[MemorySummary]]:
        """Process short-term memory with reduction."""
        reduced, summary = self.short_term_reducer.reduce(
            state.short_term_memory,
            new_items,
            self.max_short_term
        )

        # Move summarized items to long-term
        if summary:
            # Create long-term representation
            long_term_item = MemoryItem(
                item_id=summary.summary_id,
                memory_type=MemoryType.LONG_TERM,
                content=summary.summary_text,
                timestamp=summary.created_at,
                relevance_score=summary.representative_score,
                metadata={"is_summary": True}
            )
            return reduced, summary, long_term_item

        return reduced, None, None

def create_advanced_memory_system():
    """Create system with sophisticated memory management."""
    memory_manager = MemoryManager(
        max_short_term=50,
        max_long_term=200
    )

    def add_memory(state: AdvancedMemoryState):
        """Add new memories and manage constraints."""
        # Simulate new memory items
        new_items = [
            MemoryItem(
                item_id=f"mem_{datetime.now().timestamp()}",
                memory_type=MemoryType.SHORT_TERM,
                content="New observation",
                timestamp=datetime.now().isoformat(),
                relevance_score=0.9
            )
        ]

        # Process short-term memory
        reduced_short, summary, long_term_item = memory_manager.process_short_term_memory(
            state,
            new_items
        )

        updates = {
            "short_term_memory": reduced_short
        }

        if summary:
            updates["summaries"] = [summary]
            if long_term_item:
                updates["long_term_memory"] = [long_term_item]

        # Compute memory pressure
        memory_pressure = memory_manager.compute_memory_pressure(
            len(reduced_short),
            len(state.long_term_memory)
        )
        updates["memory_pressure"] = memory_pressure

        return updates

    def consolidate_memory(state: AdvancedMemoryState):
        """Consolidate and optimize memory."""
        # Move low-relevance short-term to long-term
        threshold = 0.5
        keep_short = [m for m in state.short_term_memory if m.relevance_score >= threshold]
        archive_to_long = [m for m in state.short_term_memory if m.relevance_score < threshold]

        return {
            "short_term_memory": keep_short,
            "long_term_memory": archive_to_long,
            "memory_stats": {
                "short_term_count": len(keep_short),
                "long_term_count": len(state.long_term_memory) + len(archive_to_long),
                "consolidation_timestamp": datetime.now().isoformat()
            }
        }

    # Build workflow
    workflow = StateGraph(AdvancedMemoryState)
    workflow.add_node("add", add_memory)
    workflow.add_node("consolidate", consolidate_memory)

    workflow.add_edge(START, "add")
    workflow.add_conditional_edges(
        "add",
        lambda s: "consolidate" if s.memory_pressure > 0.8 else "end",
        {"consolidate": "consolidate", "end": END}
    )
    workflow.add_edge("consolidate", END)

    return workflow.compile()

# Usage
workflow = create_advanced_memory_system()
initial_state = AdvancedMemoryState(
    session_id="session_001",
    short_term_memory=[],
    long_term_memory=[],
    summaries=[]
)
result = workflow.invoke(initial_state)
print(f"Final memory state: ST={len(result.short_term_memory)}, LT={len(result.long_term_memory)}")
```

---

## Best Practices for Memory & State Reducers Mastery

1. **Choose Appropriate Reducers**: Use `operator.add` for simple accumulation. Define custom reducers for deduplication, filtering, or summarization. Match reducer semantics to domain semantics (e.g., append for history, max for scores).

2. **Implement Bounded Memory**: Set maximum limits on state field sizes. When limits approached, trigger reduction strategies (summarization, pruning, archival). Monitor memory pressure and act before hitting hard limits.

3. **Dual-Memory Architectures**: Implement short-term (working) memory for immediate context and long-term memory for reference. Automatically promote important short-term items to long-term. This balances responsiveness with retention.

4. **Intelligent Summarization**: When reducing memories, create summaries capturing key information. Track summary quality metrics. Use summaries as compressed representations while retaining full originals separately for verification.

5. **Track Memory Metadata**: Record relevance scores, access patterns, age, and semantic similarity. Use this to inform reduction decisions. Prefer keeping high-relevance, frequently-accessed, recent items while pruning low-value older items.
