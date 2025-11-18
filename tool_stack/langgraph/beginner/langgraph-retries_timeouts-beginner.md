# LangGraph Retries & Timeouts at Node Level

## Concept Overview

Retries and timeouts at the node level enable building resilient workflows that gracefully handle transient failures and slow operations. Rather than having entire workflows fail on a single slow or failing node, node-level retry logic with exponential backoff and timeout handling enables graceful degradation. This pattern is critical for production systems where external service failures, network issues, or resource constraints are inevitable.

---

## Beginner Level: Basic Retry Logic

A simple node that retries failed operations.

```python
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from typing import Optional
import time

class RetryState(BaseModel):
    user_id: str
    attempt_count: int = 0
    max_retries: int = 3
    data: str = ""
    error: Optional[str] = None

def create_simple_retry_workflow():
    """Create workflow with basic retry logic."""

    def fetch_data_with_retry(state: RetryState):
        """Fetch data with retry logic."""
        attempt = state.attempt_count + 1

        # Simulate flaky operation (fails first 2 times)
        if attempt < 2:
            return {
                "attempt_count": attempt,
                "error": f"Attempt {attempt} failed - will retry"
            }

        # Success on third attempt
        return {
            "data": f"Data for {state.user_id}",
            "error": None,
            "attempt_count": attempt
        }

    def should_retry(state: RetryState) -> str:
        """Determine if we should retry."""
        if state.error and state.attempt_count < state.max_retries:
            return "retry"
        elif state.error:
            return "fail"
        return "success"

    # Build workflow
    workflow = StateGraph(RetryState)
    workflow.add_node("fetch", fetch_data_with_retry)

    workflow.add_edge(START, "fetch")
    workflow.add_conditional_edges(
        "fetch",
        should_retry,
        {
            "retry": "fetch",
            "success": END,
            "fail": END
        }
    )

    return workflow.compile()

# Usage
workflow = create_simple_retry_workflow()
result = workflow.invoke(RetryState(user_id="user_001"))
print(f"Success after {result.attempt_count} attempts: {result.data}")
```

---

## Best Practices for Retries & Timeouts Mastery

1. **Exponential Backoff with Jitter**: Use exponential backoff to avoid overwhelming recovering services. Add random jitter to prevent thundering herd when multiple clients retry simultaneously. Cap maximum wait time to prevent excessive delays.

2. **Circuit Breaker Pattern**: Monitor failure rates and open the circuit when error rate exceeds threshold. This prevents wasting resources on requests that will fail. Implement half-open state for testing recovery.

3. **Timeout Boundaries**: Set timeouts at node level based on SLA requirements. Distinguish between different timeout types: connect timeouts (shorter), read timeouts (medium), total operation timeouts (longer). Fail fast rather than hanging indefinitely.

4. **Adaptive Retry Strategies**: Track service health metrics and adjust retry behavior dynamically. Increase backoff when service is unhealthy. Reduce retries for idempotent operations but avoid retries for non-idempotent operations unless necessary.

5. **Observability and Metrics**: Log all retry attempts with attempt number, wait time, and result. Track circuit breaker state transitions. Monitor error rates and response times by service. Use this data to tune timeouts and retry policies.
