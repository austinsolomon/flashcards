# LangGraph Dynamic Routing via Conditional Edges

## Concept Overview

Conditional edges enable dynamic routing through a graph based on state. Rather than fixed paths, edges can route to different nodes based on computed conditions. This pattern is foundational for building adaptive workflows that respond to data, making decisions at runtime about which processing path to take. Mastering conditional edges unlocks sophisticated routing logic from simple branching to complex multi-criteria decision trees.

---

## Intermediate Level: Multi-Criteria Routing with Complex Decision Logic

A sophisticated router that uses multiple factors for intelligent routing.

```python
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from typing import Literal, Annotated
from datetime import datetime
from enum import Enum
import operator

class RequestType(str, Enum):
    TECHNICAL = "technical"
    BILLING = "billing"
    GENERAL = "general"

class RequestRoute(str, Enum):
    TECHNICAL_SUPPORT = "technical_support"
    BILLING_SUPPORT = "billing_support"
    GENERAL_SUPPORT = "general_support"
    ESCALATION = "escalation"
    FEEDBACK = "feedback"

class RoutingDecision(BaseModel):
    """Decision data for routing."""
    request_type: RequestType
    priority: int  # 1-5
    sentiment: str  # positive, neutral, negative
    requires_escalation: bool
    recommended_route: RequestRoute

class MultiCriteriaRoutingState(BaseModel):
    """State for multi-criteria routing."""
    request_id: str
    user_message: str
    user_history: dict = Field(default_factory=dict)
    routing_decision: RoutingDecision
    routing_history: Annotated[list[str], operator.add]
    final_handler: str

def create_multi_criteria_router():
    """Create router with multi-criteria decision logic."""

    def analyze_request(state: MultiCriteriaRoutingState):
        """Analyze request and classify."""
        text = state.user_message.lower()

        # Determine type
        if any(word in text for word in ["error", "bug", "crash", "technical"]):
            request_type = RequestType.TECHNICAL
        elif any(word in text for word in ["payment", "refund", "invoice", "billing"]):
            request_type = RequestType.BILLING
        else:
            request_type = RequestType.GENERAL

        # Determine priority (1-5)
        priority = 3  # default
        if any(word in text for word in ["urgent", "critical", "blocking"]):
            priority = 5
        elif any(word in text for word in ["soon", "asap"]):
            priority = 4
        elif any(word in text for word in ["eventually", "later"]):
            priority = 1

        # Determine sentiment
        if any(word in text for word in ["thank", "great", "excellent"]):
            sentiment = "positive"
        elif any(word in text for word in ["bad", "terrible", "angry"]):
            sentiment = "negative"
        else:
            sentiment = "neutral"

        # Check if escalation needed
        escalation_needed = (
            priority >= 5 or
            (sentiment == "negative" and priority >= 3) or
            state.user_history.get("previous_complaints", 0) >= 2
        )

        # Determine route
        if escalation_needed:
            route = RequestRoute.ESCALATION
        elif request_type == RequestType.TECHNICAL:
            route = RequestRoute.TECHNICAL_SUPPORT
        elif request_type == RequestType.BILLING:
            route = RequestRoute.BILLING_SUPPORT
        else:
            route = RequestRoute.GENERAL_SUPPORT

        decision = RoutingDecision(
            request_type=request_type,
            priority=priority,
            sentiment=sentiment,
            requires_escalation=escalation_needed,
            recommended_route=route
        )

        return {
            "routing_decision": decision,
            "routing_history": [f"Analyzed: routed to {route.value}"]
        }

    def technical_support_handler(state: MultiCriteriaRoutingState):
        """Handle technical support."""
        return {
            "final_handler": "technical_support_team",
            "routing_history": state.routing_history + ["Assigned to: Technical Support"]
        }

    def billing_support_handler(state: MultiCriteriaRoutingState):
        """Handle billing support."""
        return {
            "final_handler": "billing_support_team",
            "routing_history": state.routing_history + ["Assigned to: Billing Support"]
        }

    def general_support_handler(state: MultiCriteriaRoutingState):
        """Handle general support."""
        return {
            "final_handler": "general_support_team",
            "routing_history": state.routing_history + ["Assigned to: General Support"]
        }

    def escalation_handler(state: MultiCriteriaRoutingState):
        """Handle escalation."""
        return {
            "final_handler": "escalation_manager",
            "routing_history": state.routing_history + ["Escalated to: Manager"]
        }

    def feedback_handler(state: MultiCriteriaRoutingState):
        """Handle feedback."""
        return {
            "final_handler": "feedback_team",
            "routing_history": state.routing_history + ["Routed to: Feedback Team"]
        }

    # Build workflow
    workflow = StateGraph(MultiCriteriaRoutingState)
    workflow.add_node("analyze", analyze_request)
    workflow.add_node("technical", technical_support_handler)
    workflow.add_node("billing", billing_support_handler)
    workflow.add_node("general", general_support_handler)
    workflow.add_node("escalation", escalation_handler)
    workflow.add_node("feedback", feedback_handler)

    workflow.add_edge(START, "analyze")

    # Complex conditional routing
    def route_decision(state: MultiCriteriaRoutingState) -> str:
        """Determine next node based on decision."""
        decision = state.routing_decision
        return decision.recommended_route.value

    workflow.add_conditional_edges(
        "analyze",
        route_decision,
        {
            "technical_support": "technical",
            "billing_support": "billing",
            "general_support": "general",
            "escalation": "escalation",
            "feedback": "feedback"
        }
    )

    for handler in ["technical", "billing", "general", "escalation", "feedback"]:
        workflow.add_edge(handler, END)

    return workflow.compile()

# Usage
router = create_multi_criteria_router()
state = MultiCriteriaRoutingState(
    request_id="req_001",
    user_message="I have a critical billing error - been overcharged for months!",
    user_history={"previous_complaints": 1},
    routing_decision=RoutingDecision(
        request_type=RequestType.BILLING,
        priority=5,
        sentiment="negative",
        requires_escalation=True,
        recommended_route=RequestRoute.ESCALATION
    ),
    routing_history=[]
)
result = router.invoke(state)
print(f"Handler: {result.final_handler}")
```

---

## Best Practices for Dynamic Routing Mastery

1. **Explicit Routing Function**: Define a pure function that maps state to next node name. This makes routing logic testable, debuggable, and easy to understand. Avoid complex conditional expressions in `add_conditional_edges`.

2. **Route Score Ranking**: Compute scores for all possible routes rather than making binary decisions. Track top-N alternatives for fallback or comparison. This enables debugging when the primary route fails.

3. **Load-Aware Routing**: Monitor queue depths and handler capacity. Route requests to less-loaded handlers when multiple options exist. Balance latency (shortest queue) with quality (best resolution rates).

4. **Learned Weights and Optimization**: Track which routes perform well for different request types. Periodically update routing weights based on success rates and customer satisfaction. Use A/B testing for routing algorithm changes.

5. **Observability and Fallback**: Log all routing decisions with scores and reasoning. Include alternate routes in state. If primary handler fails, automatically retry with alternate route rather than full failure.
