# LangGraph Memory & State Reducers

## Concept Overview

State reducers define how state updates are merged into existing state. Instead of replacing fields, reducers combine old and new values intelligently. This is critical for managing growing state (like conversation history), implementing memory management patterns, and preventing state bloat in long-running workflows. Reducers enable append-only semantics, deduplication, summarization, and other transformations.

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
