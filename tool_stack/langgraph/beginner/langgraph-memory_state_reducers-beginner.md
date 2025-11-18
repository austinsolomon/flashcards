# LangGraph Memory & State Reducers

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

## Best Practices for Memory & State Reducers Mastery

1. **Choose Appropriate Reducers**: Use `operator.add` for simple accumulation. Define custom reducers for deduplication, filtering, or summarization. Match reducer semantics to domain semantics (e.g., append for history, max for scores).

2. **Implement Bounded Memory**: Set maximum limits on state field sizes. When limits approached, trigger reduction strategies (summarization, pruning, archival). Monitor memory pressure and act before hitting hard limits.

3. **Dual-Memory Architectures**: Implement short-term (working) memory for immediate context and long-term memory for reference. Automatically promote important short-term items to long-term. This balances responsiveness with retention.

4. **Intelligent Summarization**: When reducing memories, create summaries capturing key information. Track summary quality metrics. Use summaries as compressed representations while retaining full originals separately for verification.

5. **Track Memory Metadata**: Record relevance scores, access patterns, age, and semantic similarity. Use this to inform reduction decisions. Prefer keeping high-relevance, frequently-accessed, recent items while pruning low-value older items.
