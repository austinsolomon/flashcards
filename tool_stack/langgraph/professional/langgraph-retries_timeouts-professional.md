# LangGraph Retries & Timeouts at Node Level

## Concept Overview

Retries and timeouts at the node level enable building resilient workflows that gracefully handle transient failures and slow operations. Rather than having entire workflows fail on a single slow or failing node, node-level retry logic with exponential backoff and timeout handling enables graceful degradation. This pattern is critical for production systems where external service failures, network issues, or resource constraints are inevitable.

---

## Intermediate Level: Exponential Backoff with Timeout

A sophisticated retry system with exponential backoff and timeout handling.

```python
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime, timedelta
from enum import Enum
import time
import math

class RetryStrategy(str, Enum):
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIBONACCI = "fibonacci"

class RetryMetrics(BaseModel):
    """Metrics for retry operations."""
    attempt_number: int
    wait_time_ms: int
    total_elapsed_ms: int
    status: Literal["pending", "waiting", "executing", "success", "failed"]

class ResilientOperationState(BaseModel):
    """State for resilient operations with retry/timeout."""
    operation_id: str
    max_retries: int = 3
    timeout_seconds: int = 30
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    base_wait_ms: int = 100
    max_wait_ms: int = 5000

    current_attempt: int = 0
    start_time: Optional[str] = None
    last_attempt_time: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    retry_metrics: list[RetryMetrics] = Field(default_factory=list)

def calculate_backoff(
    attempt: int,
    base_wait_ms: int,
    max_wait_ms: int,
    strategy: RetryStrategy
) -> int:
    """Calculate wait time for retry based on strategy."""
    if strategy == RetryStrategy.EXPONENTIAL:
        wait = base_wait_ms * (2 ** (attempt - 1))
    elif strategy == RetryStrategy.LINEAR:
        wait = base_wait_ms * attempt
    else:  # FIBONACCI
        fib = [1, 1]
        for _ in range(attempt - 2):
            fib.append(fib[-1] + fib[-2])
        wait = base_wait_ms * fib[min(attempt - 1, len(fib) - 1)]

    return min(wait, max_wait_ms)

def create_resilient_operation_workflow():
    """Create workflow with exponential backoff and timeout."""

    def execute_operation(state: ResilientOperationState):
        """Execute operation with timeout check."""
        current_attempt = state.current_attempt + 1
        start = datetime.now()

        # Check if timeout exceeded
        if state.start_time:
            elapsed = (start - datetime.fromisoformat(state.start_time)).total_seconds()
            if elapsed > state.timeout_seconds:
                return {
                    "error": f"Timeout exceeded after {elapsed:.1f}s",
                    "current_attempt": current_attempt
                }

        # Simulate flaky operation
        if current_attempt <= 2:
            return {
                "error": f"Operation failed on attempt {current_attempt}",
                "current_attempt": current_attempt,
                "last_attempt_time": start.isoformat()
            }

        # Success
        return {
            "result": f"Operation completed successfully",
            "error": None,
            "current_attempt": current_attempt,
            "last_attempt_time": start.isoformat()
        }

    def calculate_wait_and_retry(state: ResilientOperationState):
        """Calculate wait time and determine if should retry."""
        if state.error is None:
            return "success"

        if state.current_attempt >= state.max_retries:
            return "max_retries_exceeded"

        # Calculate backoff
        backoff_ms = calculate_backoff(
            state.current_attempt,
            state.base_wait_ms,
            state.max_wait_ms,
            state.retry_strategy
        )

        # Log metric
        metric = RetryMetrics(
            attempt_number=state.current_attempt,
            wait_time_ms=backoff_ms,
            total_elapsed_ms=0,
            status="waiting"
        )

        # Simulate wait
        time.sleep(backoff_ms / 1000.0)

        return "retry"

    def initialize(state: ResilientOperationState):
        """Initialize operation."""
        return {"start_time": datetime.now().isoformat()}

    # Build workflow
    workflow = StateGraph(ResilientOperationState)
    workflow.add_node("init", initialize)
    workflow.add_node("execute", execute_operation)
    workflow.add_node("wait_and_check", calculate_wait_and_retry)

    workflow.add_edge(START, "init")
    workflow.add_edge("init", "execute")

    workflow.add_conditional_edges(
        "wait_and_check",
        lambda s: "init" if calculate_wait_and_retry(s) == "retry" else calculate_wait_and_retry(s),
        {
            "init": "execute",
            "success": END,
            "max_retries_exceeded": END
        }
    )

    workflow.add_conditional_edges(
        "execute",
        lambda s: "wait_and_check",
        {"wait_and_check": "wait_and_check"}
    )

    return workflow.compile()

# Usage
workflow = create_resilient_operation_workflow()
result = workflow.invoke(ResilientOperationState(operation_id="op_001"))
print(f"Completed: {result.result}, Attempts: {result.current_attempt}")
```

---

## Best Practices for Retries & Timeouts Mastery

1. **Exponential Backoff with Jitter**: Use exponential backoff to avoid overwhelming recovering services. Add random jitter to prevent thundering herd when multiple clients retry simultaneously. Cap maximum wait time to prevent excessive delays.

2. **Circuit Breaker Pattern**: Monitor failure rates and open the circuit when error rate exceeds threshold. This prevents wasting resources on requests that will fail. Implement half-open state for testing recovery.

3. **Timeout Boundaries**: Set timeouts at node level based on SLA requirements. Distinguish between different timeout types: connect timeouts (shorter), read timeouts (medium), total operation timeouts (longer). Fail fast rather than hanging indefinitely.

4. **Adaptive Retry Strategies**: Track service health metrics and adjust retry behavior dynamically. Increase backoff when service is unhealthy. Reduce retries for idempotent operations but avoid retries for non-idempotent operations unless necessary.

5. **Observability and Metrics**: Log all retry attempts with attempt number, wait time, and result. Track circuit breaker state transitions. Monitor error rates and response times by service. Use this data to tune timeouts and retry policies.
