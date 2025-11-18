# LangGraph Retries & Timeouts at Node Level

## Concept Overview

Retries and timeouts at the node level enable building resilient workflows that gracefully handle transient failures and slow operations. Rather than having entire workflows fail on a single slow or failing node, node-level retry logic with exponential backoff and timeout handling enables graceful degradation. This pattern is critical for production systems where external service failures, network issues, or resource constraints are inevitable.

---

## Advanced Level: Circuit Breaker with Adaptive Retry and Fallback

A production-grade system with circuit breaker pattern, adaptive retry strategies, and fallback paths.

```python
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from typing import Optional, Literal, Callable, Any
from datetime import datetime, timedelta
from enum import Enum
from collections import deque
import asyncio
import statistics

class CircuitState(str, Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class ServiceMetrics(BaseModel):
    """Metrics for a service."""
    service_name: str
    success_count: int = 0
    failure_count: int = 0
    timeout_count: int = 0
    avg_response_time_ms: float = 0.0
    last_error_time: Optional[str] = None
    circuit_state: CircuitState = CircuitState.CLOSED
    error_rate: float = 0.0

class RetryPolicy(BaseModel):
    """Adaptive retry policy."""
    max_retries: int = 3
    initial_backoff_ms: int = 100
    max_backoff_ms: int = 10000
    timeout_ms: int = 30000
    circuit_failure_threshold: float = 0.5
    circuit_success_threshold: int = 3
    adaptive: bool = True
    jitter_enabled: bool = True

class CircuitBreakerState(BaseModel):
    """State for circuit breaker pattern."""
    request_id: str
    service_name: str
    service_metrics: ServiceMetrics
    retry_policy: RetryPolicy
    current_attempt: int = 0
    circuit_open_until: Optional[str] = None

    result: Optional[Any] = None
    error: Optional[str] = None
    final_status: Literal["success", "failed", "circuit_open"] = "pending"
    execution_history: list[dict] = Field(default_factory=list)

class CircuitBreaker:
    """Implements circuit breaker pattern with adaptive retry."""
    def __init__(self):
        self.metrics = {}
        self.recent_failures = deque(maxlen=100)

    def update_metrics(
        self,
        service_name: str,
        success: bool,
        response_time_ms: float
    ) -> ServiceMetrics:
        """Update metrics and determine circuit state."""
        if service_name not in self.metrics:
            self.metrics[service_name] = ServiceMetrics(service_name=service_name)

        metrics = self.metrics[service_name]

        if success:
            metrics.success_count += 1
        else:
            metrics.failure_count += 1
            metrics.last_error_time = datetime.now().isoformat()
            self.recent_failures.append({
                "service": service_name,
                "time": datetime.now().isoformat()
            })

        # Calculate error rate
        total = metrics.success_count + metrics.failure_count
        metrics.error_rate = metrics.failure_count / total if total > 0 else 0.0

        # Update circuit state
        self._update_circuit_state(metrics)

        return metrics

    def _update_circuit_state(self, metrics: ServiceMetrics):
        """Update circuit breaker state based on error rate."""
        if metrics.error_rate > 0.5:
            metrics.circuit_state = CircuitState.OPEN
        elif metrics.error_rate > 0.2:
            metrics.circuit_state = CircuitState.HALF_OPEN
        else:
            metrics.circuit_state = CircuitState.CLOSED

    def should_reject(self, metrics: ServiceMetrics) -> bool:
        """Check if requests should be rejected due to circuit state."""
        return metrics.circuit_state == CircuitState.OPEN

    def get_adaptive_backoff(
        self,
        attempt: int,
        error_rate: float,
        base_wait_ms: int,
        max_wait_ms: int
    ) -> int:
        """Calculate adaptive backoff based on service health."""
        # Base exponential backoff
        exponential_wait = base_wait_ms * (2 ** (attempt - 1))

        # Adjust based on error rate
        if error_rate > 0.8:
            # Service is very unhealthy, longer backoff
            multiplier = 3.0
        elif error_rate > 0.5:
            multiplier = 2.0
        else:
            multiplier = 1.0

        wait = int(exponential_wait * multiplier)

        # Add jitter to prevent thundering herd
        import random
        jitter = random.uniform(0.8, 1.2)
        wait = int(wait * jitter)

        return min(wait, max_wait_ms)

def create_circuit_breaker_system():
    """Create system with circuit breaker and adaptive retry."""
    breaker = CircuitBreaker()

    async def check_circuit(state: CircuitBreakerState):
        """Check circuit breaker state."""
        if breaker.should_reject(state.service_metrics):
            return {
                "final_status": "circuit_open",
                "error": "Circuit breaker open - service unavailable"
            }
        return state

    async def execute_with_retry(state: CircuitBreakerState):
        """Execute operation with adaptive retry."""
        attempt = state.current_attempt + 1
        start = datetime.now()

        # Simulate operation (fails first 2 attempts)
        success = attempt > 2
        response_time_ms = (datetime.now() - start).total_seconds() * 1000

        # Update metrics
        updated_metrics = breaker.update_metrics(
            state.service_name,
            success,
            response_time_ms
        )

        if success:
            return {
                "result": "Operation succeeded",
                "error": None,
                "current_attempt": attempt,
                "service_metrics": updated_metrics,
                "final_status": "success",
                "execution_history": [
                    {"attempt": attempt, "success": True, "time_ms": response_time_ms}
                ]
            }
        else:
            return {
                "error": f"Attempt {attempt} failed",
                "current_attempt": attempt,
                "service_metrics": updated_metrics,
                "execution_history": [
                    {"attempt": attempt, "success": False, "time_ms": response_time_ms}
                ]
            }

    async def should_continue(state: CircuitBreakerState):
        """Determine if should retry."""
        if state.error is None:
            return "success"

        if state.current_attempt >= state.retry_policy.max_retries:
            return "max_retries"

        # Calculate adaptive backoff
        backoff_ms = breaker.get_adaptive_backoff(
            state.current_attempt,
            state.service_metrics.error_rate,
            state.retry_policy.initial_backoff_ms,
            state.retry_policy.max_backoff_ms
        )

        # Wait before retry
        await asyncio.sleep(backoff_ms / 1000.0)

        return "retry"

    # Build workflow
    workflow = StateGraph(CircuitBreakerState)
    workflow.add_node("check_circuit", check_circuit)
    workflow.add_node("execute", execute_with_retry)

    workflow.add_edge(START, "check_circuit")
    workflow.add_conditional_edges(
        "check_circuit",
        lambda s: "execute" if s.final_status == "pending" else "end",
        {"execute": "execute", "end": END}
    )
    workflow.add_edge("execute", END)

    return workflow.compile()

# Usage
async def main():
    system = create_circuit_breaker_system()

    initial_state = CircuitBreakerState(
        request_id="req_001",
        service_name="payment_service",
        service_metrics=ServiceMetrics(service_name="payment_service"),
        retry_policy=RetryPolicy(
            max_retries=3,
            adaptive=True,
            jitter_enabled=True
        )
    )
    # result = await asyncio.to_thread(system.invoke, initial_state)
```

---

## Best Practices for Retries & Timeouts Mastery

1. **Exponential Backoff with Jitter**: Use exponential backoff to avoid overwhelming recovering services. Add random jitter to prevent thundering herd when multiple clients retry simultaneously. Cap maximum wait time to prevent excessive delays.

2. **Circuit Breaker Pattern**: Monitor failure rates and open the circuit when error rate exceeds threshold. This prevents wasting resources on requests that will fail. Implement half-open state for testing recovery.

3. **Timeout Boundaries**: Set timeouts at node level based on SLA requirements. Distinguish between different timeout types: connect timeouts (shorter), read timeouts (medium), total operation timeouts (longer). Fail fast rather than hanging indefinitely.

4. **Adaptive Retry Strategies**: Track service health metrics and adjust retry behavior dynamically. Increase backoff when service is unhealthy. Reduce retries for idempotent operations but avoid retries for non-idempotent operations unless necessary.

5. **Observability and Metrics**: Log all retry attempts with attempt number, wait time, and result. Track circuit breaker state transitions. Monitor error rates and response times by service. Use this data to tune timeouts and retry policies.
