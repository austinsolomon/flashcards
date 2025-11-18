# LangGraph Dynamic Routing via Conditional Edges

## Concept Overview

Conditional edges enable dynamic routing through a graph based on state. Rather than fixed paths, edges can route to different nodes based on computed conditions. This pattern is foundational for building adaptive workflows that respond to data, making decisions at runtime about which processing path to take. Mastering conditional edges unlocks sophisticated routing logic from simple branching to complex multi-criteria decision trees.

---

## Beginner Level: Simple Conditional Routing

A basic workflow that branches based on a single condition.

```python
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from typing import Literal

class RoutingState(BaseModel):
    user_input: str
    classification: Literal["urgent", "normal", "low"] = "normal"
    result: str

def create_simple_router():
    """Create workflow with simple conditional routing."""

    def classify_input(state: RoutingState):
        """Classify input urgency."""
        keywords_urgent = ["urgent", "critical", "asap"]
        keywords_low = ["later", "when possible", "eventually"]

        text = state.user_input.lower()

        if any(word in text for word in keywords_urgent):
            classification = "urgent"
        elif any(word in text for word in keywords_low):
            classification = "low"
        else:
            classification = "normal"

        return {"classification": classification}

    def handle_urgent(state: RoutingState):
        """Handle urgent requests immediately."""
        return {"result": f"URGENT: {state.user_input} - Processing immediately"}

    def handle_normal(state: RoutingState):
        """Handle normal requests."""
        return {"result": f"NORMAL: {state.user_input} - Queued for processing"}

    def handle_low(state: RoutingState):
        """Handle low-priority requests."""
        return {"result": f"LOW: {state.user_input} - Scheduled for later"}

    # Build workflow
    workflow = StateGraph(RoutingState)
    workflow.add_node("classify", classify_input)
    workflow.add_node("urgent", handle_urgent)
    workflow.add_node("normal", handle_normal)
    workflow.add_node("low", handle_low)

    workflow.add_edge(START, "classify")

    # Simple conditional routing
    workflow.add_conditional_edges(
        "classify",
        lambda state: state.classification,
        {
            "urgent": "urgent",
            "normal": "normal",
            "low": "low"
        }
    )

    workflow.add_edge("urgent", END)
    workflow.add_edge("normal", END)
    workflow.add_edge("low", END)

    return workflow.compile()

# Usage
router = create_simple_router()
result = router.invoke(RoutingState(user_input="Please handle this urgently!"))
print(result.result)
```

---

## Best Practices for Dynamic Routing Mastery

1. **Explicit Routing Function**: Define a pure function that maps state to next node name. This makes routing logic testable, debuggable, and easy to understand. Avoid complex conditional expressions in `add_conditional_edges`.

2. **Route Score Ranking**: Compute scores for all possible routes rather than making binary decisions. Track top-N alternatives for fallback or comparison. This enables debugging when the primary route fails.

3. **Load-Aware Routing**: Monitor queue depths and handler capacity. Route requests to less-loaded handlers when multiple options exist. Balance latency (shortest queue) with quality (best resolution rates).

4. **Learned Weights and Optimization**: Track which routes perform well for different request types. Periodically update routing weights based on success rates and customer satisfaction. Use A/B testing for routing algorithm changes.

5. **Observability and Fallback**: Log all routing decisions with scores and reasoning. Include alternate routes in state. If primary handler fails, automatically retry with alternate route rather than full failure.
