# LangGraph Dynamic Routing via Conditional Edges

## Concept Overview

Conditional edges enable dynamic routing through a graph based on state. Rather than fixed paths, edges can route to different nodes based on computed conditions. This pattern is foundational for building adaptive workflows that respond to data, making decisions at runtime about which processing path to take. Mastering conditional edges unlocks sophisticated routing logic from simple branching to complex multi-criteria decision trees.

---

## Advanced Level: Adaptive Routing with Machine Learning and Dynamic Weights

A sophisticated router using learned weights, context-aware decisions, and continuous optimization.

```python
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from typing import Literal, Annotated, Optional, Any
from datetime import datetime
from enum import Enum
import operator
import json

class RouteMetrics(BaseModel):
    """Performance metrics for a route."""
    route_name: str
    avg_resolution_time: float
    success_rate: float
    customer_satisfaction: float
    cost_per_request: float
    current_load: int
    capacity: int

class RoutingWeight(BaseModel):
    """Learned weights for routing decisions."""
    request_type: float
    priority: float
    sentiment: float
    user_history: float
    queue_length: float
    resolution_performance: float
    timestamp_updated: str

class AdvancedRoutingDecision(BaseModel):
    """Advanced routing decision with confidence."""
    primary_route: str
    alternate_routes: list[str]
    route_scores: dict[str, float]
    confidence_score: float
    reasoning: str
    optimization_applied: str

class AdaptiveRoutingState(BaseModel):
    """State for adaptive routing system."""
    request_id: str
    request_data: dict
    route_metrics: dict[str, RouteMetrics]
    routing_weights: RoutingWeight
    routing_decision: Optional[AdvancedRoutingDecision] = None
    historical_decisions: Annotated[list[dict], operator.add]
    optimization_logs: Annotated[list[str], operator.add]
    final_route: str

class AdvancedRouter:
    """Router with ML-based decision making."""
    def __init__(self):
        self.route_metrics = {}
        self.decision_history = []

    def compute_route_score(
        self,
        request_features: dict,
        weights: RoutingWeight,
        route_metrics: dict[str, RouteMetrics]
    ) -> dict[str, float]:
        """Compute scores for each route using weighted features."""
        scores = {}

        # Define possible routes and their base suitability
        routes = ["technical", "billing", "general", "escalation"]

        for route in routes:
            score = 0.0

            # Factor 1: Request type match
            type_match = 1.0 if request_features.get("type_match") else 0.5
            score += type_match * weights.request_type

            # Factor 2: Priority handling
            priority = request_features.get("priority", 3) / 5.0
            score += priority * weights.priority

            # Factor 3: Sentiment match
            sentiment_score = {"positive": 1.0, "neutral": 0.7, "negative": 0.5}.get(
                request_features.get("sentiment"), 0.7
            )
            score += sentiment_score * weights.sentiment

            # Factor 4: Historical performance
            metrics = route_metrics.get(route)
            if metrics:
                resolution_score = (
                    metrics.success_rate * 0.6 +
                    (1 - metrics.avg_resolution_time / 3600) * 0.4
                )
                score += resolution_score * weights.resolution_performance

                # Factor 5: Load balancing
                load_factor = 1.0 - (metrics.current_load / metrics.capacity)
                score += load_factor * 0.5

            scores[route] = score

        return scores

    async def select_optimal_route(
        self,
        state: AdaptiveRoutingState
    ) -> tuple[str, AdvancedRoutingDecision]:
        """Select optimal route considering all factors."""
        request_features = {
            "priority": state.request_data.get("priority", 3),
            "sentiment": state.request_data.get("sentiment", "neutral"),
            "type_match": state.request_data.get("type_match", False)
        }

        route_scores = self.compute_route_score(
            request_features,
            state.routing_weights,
            state.route_metrics
        )

        # Sort routes by score
        sorted_routes = sorted(
            route_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        primary_route = sorted_routes[0][0]
        alternate_routes = [r[0] for r in sorted_routes[1:3]]

        # Calculate confidence
        primary_score = route_scores[primary_route]
        confidence = min(primary_score / 10.0, 1.0)

        # Generate reasoning
        reasoning = f"Routed to {primary_route} (score: {primary_score:.2f}) based on priority and performance metrics"

        decision = AdvancedRoutingDecision(
            primary_route=primary_route,
            alternate_routes=alternate_routes,
            route_scores=route_scores,
            confidence_score=confidence,
            reasoning=reasoning,
            optimization_applied="weighted_scoring"
        )

        return primary_route, decision

def create_adaptive_routing_system():
    """Create adaptive routing system with ML."""
    router = AdvancedRouter()

    async def analyze_and_route(state: AdaptiveRoutingState):
        """Analyze request and make intelligent routing decision."""
        primary_route, decision = await router.select_optimal_route(state)

        log_entry = f"Routing to {primary_route} with confidence {decision.confidence_score:.2%}"

        return {
            "routing_decision": decision,
            "final_route": primary_route,
            "optimization_logs": [log_entry]
        }

    def adaptive_handler(state: AdaptiveRoutingState):
        """Route to selected handler dynamically."""
        return {
            "historical_decisions": [{
                "route": state.final_route,
                "timestamp": datetime.now().isoformat(),
                "confidence": state.routing_decision.confidence_score if state.routing_decision else 0
            }]
        }

    # Build workflow
    workflow = StateGraph(AdaptiveRoutingState)
    workflow.add_node("analyze", analyze_and_route)
    workflow.add_node("route", adaptive_handler)

    workflow.add_edge(START, "analyze")
    workflow.add_edge("analyze", "route")
    workflow.add_edge("route", END)

    return workflow.compile()

# Usage
async def main():
    system = create_adaptive_routing_system()

    route_metrics = {
        "technical": RouteMetrics(
            route_name="technical",
            avg_resolution_time=300,
            success_rate=0.92,
            customer_satisfaction=4.3,
            cost_per_request=15.0,
            current_load=8,
            capacity=12
        ),
        "billing": RouteMetrics(
            route_name="billing",
            avg_resolution_time=180,
            success_rate=0.88,
            customer_satisfaction=3.9,
            cost_per_request=10.0,
            current_load=5,
            capacity=10
        )
    }

    initial_state = AdaptiveRoutingState(
        request_id="req_001",
        request_data={"priority": 4, "sentiment": "negative", "type_match": True},
        route_metrics=route_metrics,
        routing_weights=RoutingWeight(
            request_type=0.25,
            priority=0.25,
            sentiment=0.15,
            user_history=0.10,
            queue_length=0.15,
            resolution_performance=0.10,
            timestamp_updated=datetime.now().isoformat()
        ),
        historical_decisions=[],
        optimization_logs=[],
        final_route=""
    )
    # result = await asyncio.to_thread(system.invoke, initial_state)
```

---

## Best Practices for Dynamic Routing Mastery

1. **Explicit Routing Function**: Define a pure function that maps state to next node name. This makes routing logic testable, debuggable, and easy to understand. Avoid complex conditional expressions in `add_conditional_edges`.

2. **Route Score Ranking**: Compute scores for all possible routes rather than making binary decisions. Track top-N alternatives for fallback or comparison. This enables debugging when the primary route fails.

3. **Load-Aware Routing**: Monitor queue depths and handler capacity. Route requests to less-loaded handlers when multiple options exist. Balance latency (shortest queue) with quality (best resolution rates).

4. **Learned Weights and Optimization**: Track which routes perform well for different request types. Periodically update routing weights based on success rates and customer satisfaction. Use A/B testing for routing algorithm changes.

5. **Observability and Fallback**: Log all routing decisions with scores and reasoning. Include alternate routes in state. If primary handler fails, automatically retry with alternate route rather than full failure.
