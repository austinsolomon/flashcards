# Callbacks, Tracing, and Observability - Advanced

## Concept Overview

Callbacks are hooks that execute at key points in LangChain execution (LLM start/end, chain start/end, tool usage, errors). They enable logging, monitoring, cost tracking, and debugging. Combined with tracing platforms (LangSmith, LangFuse), callbacks provide full observability into complex LLM applications - every token, every decision, every error, with latency and cost metrics.

**Why it matters:** You can't debug what you can't see. LLM applications are non-deterministic and complex - without proper observability, you're flying blind. Production systems need real-time monitoring, error alerting, cost tracking, and execution traces for debugging. The difference between "it works on my machine" and a production system is observability.

## Real-World Example: Production-Grade RAG System with Full Observability

This example demonstrates a comprehensive observability setup for a RAG system with custom callbacks, cost tracking, performance monitoring, and integration with external observability platforms.

```python
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from typing import Dict, Any, List, Optional
from datetime import datetime
import time
import json
import logging
from collections import defaultdict

# ========== CUSTOM CALLBACKS FOR MONITORING ==========

class CostTrackingCallback(BaseCallbackHandler):
    """Track token usage and estimated costs across all LLM calls."""

    # Pricing as of 2024 (per 1K tokens)
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "text-embedding-3-large": {"input": 0.00013, "output": 0.0}
    }

    def __init__(self):
        self.total_tokens = 0
        self.total_cost = 0.0
        self.call_counts = defaultdict(int)
        self.model_usage = defaultdict(lambda: {"input": 0, "output": 0, "cost": 0.0})

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """Called when LLM starts."""
        model = kwargs.get('invocation_params', {}).get('model_name', 'unknown')
        self.call_counts[model] += 1

    def on_llm_end(self, response, **kwargs) -> None:
        """Called when LLM ends - track tokens and cost."""
        try:
            # Extract token usage
            llm_output = response.llm_output or {}
            token_usage = llm_output.get('token_usage', {})
            model_name = llm_output.get('model_name', 'unknown')

            input_tokens = token_usage.get('prompt_tokens', 0)
            output_tokens = token_usage.get('completion_tokens', 0)
            total = token_usage.get('total_tokens', 0)

            # Update tracking
            self.total_tokens += total
            self.model_usage[model_name]['input'] += input_tokens
            self.model_usage[model_name]['output'] += output_tokens

            # Calculate cost
            if model_name in self.PRICING:
                pricing = self.PRICING[model_name]
                cost = (input_tokens / 1000 * pricing['input']) + \
                       (output_tokens / 1000 * pricing['output'])
                self.model_usage[model_name]['cost'] += cost
                self.total_cost += cost

        except Exception as e:
            logging.error(f"Cost tracking error: {e}")

    def get_summary(self) -> Dict[str, Any]:
        """Get cost and usage summary."""
        return {
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost, 4),
            "model_breakdown": dict(self.model_usage),
            "call_counts": dict(self.call_counts)
        }

class PerformanceTrackingCallback(BaseCallbackHandler):
    """Track latency and performance metrics."""

    def __init__(self):
        self.chain_timings = []
        self.llm_timings = []
        self.retrieval_timings = []
        self.start_times = {}

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        """Track chain start time."""
        run_id = kwargs.get('run_id')
        self.start_times[f"chain_{run_id}"] = time.time()

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        """Calculate chain duration."""
        run_id = kwargs.get('run_id')
        start_key = f"chain_{run_id}"

        if start_key in self.start_times:
            duration = time.time() - self.start_times[start_key]
            self.chain_timings.append({
                "duration_ms": round(duration * 1000, 2),
                "timestamp": datetime.now().isoformat()
            })
            del self.start_times[start_key]

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """Track LLM start time."""
        run_id = kwargs.get('run_id')
        self.start_times[f"llm_{run_id}"] = time.time()

    def on_llm_end(self, response, **kwargs) -> None:
        """Calculate LLM duration."""
        run_id = kwargs.get('run_id')
        start_key = f"llm_{run_id}"

        if start_key in self.start_times:
            duration = time.time() - self.start_times[start_key]
            self.llm_timings.append({
                "duration_ms": round(duration * 1000, 2),
                "timestamp": datetime.now().isoformat()
            })
            del self.start_times[start_key]

    def on_retriever_start(self, serialized: Dict[str, Any], query: str, **kwargs) -> None:
        """Track retriever start time."""
        run_id = kwargs.get('run_id')
        self.start_times[f"retriever_{run_id}"] = time.time()

    def on_retriever_end(self, documents, **kwargs) -> None:
        """Calculate retrieval duration."""
        run_id = kwargs.get('run_id')
        start_key = f"retriever_{run_id}"

        if start_key in self.start_times:
            duration = time.time() - self.start_times[start_key]
            self.retrieval_timings.append({
                "duration_ms": round(duration * 1000, 2),
                "num_docs": len(documents),
                "timestamp": datetime.now().isoformat()
            })
            del self.start_times[start_key]

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        return {
            "chain_stats": self._calculate_stats(self.chain_timings),
            "llm_stats": self._calculate_stats(self.llm_timings),
            "retrieval_stats": self._calculate_stats(self.retrieval_timings)
        }

    def _calculate_stats(self, timings: List[Dict]) -> Dict:
        """Calculate statistical summary."""
        if not timings:
            return {"count": 0}

        durations = [t['duration_ms'] for t in timings]
        return {
            "count": len(durations),
            "avg_ms": round(sum(durations) / len(durations), 2),
            "min_ms": min(durations),
            "max_ms": max(durations),
            "total_ms": round(sum(durations), 2)
        }

class ErrorTrackingCallback(BaseCallbackHandler):
    """Track and log errors for debugging and alerting."""

    def __init__(self):
        self.errors = []
        self.error_counts = defaultdict(int)

    def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Log LLM errors."""
        error_info = {
            "type": "llm_error",
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": datetime.now().isoformat()
        }
        self.errors.append(error_info)
        self.error_counts['llm'] += 1
        logging.error(f"LLM Error: {error}")

    def on_chain_error(self, error: Exception, **kwargs) -> None:
        """Log chain errors."""
        error_info = {
            "type": "chain_error",
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": datetime.now().isoformat()
        }
        self.errors.append(error_info)
        self.error_counts['chain'] += 1
        logging.error(f"Chain Error: {error}")

    def on_tool_error(self, error: Exception, **kwargs) -> None:
        """Log tool errors."""
        error_info = {
            "type": "tool_error",
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": datetime.now().isoformat()
        }
        self.errors.append(error_info)
        self.error_counts['tool'] += 1
        logging.error(f"Tool Error: {error}")

    def get_summary(self) -> Dict[str, Any]:
        """Get error summary."""
        return {
            "total_errors": len(self.errors),
            "error_breakdown": dict(self.error_counts),
            "recent_errors": self.errors[-5:]  # Last 5 errors
        }

class DetailedTracingCallback(BaseCallbackHandler):
    """Comprehensive tracing for debugging - logs everything."""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.trace = []

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        """Log chain start."""
        self.trace.append({
            "event": "chain_start",
            "name": serialized.get('name', 'unknown'),
            "inputs": inputs,
            "timestamp": datetime.now().isoformat()
        })
        if self.verbose:
            print(f"\n🔗 Chain Start: {serialized.get('name', 'unknown')}")
            print(f"   Inputs: {json.dumps(inputs, indent=2)[:200]}...")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        """Log chain end."""
        self.trace.append({
            "event": "chain_end",
            "outputs": outputs,
            "timestamp": datetime.now().isoformat()
        })
        if self.verbose:
            print(f"✅ Chain End")
            print(f"   Outputs: {json.dumps(outputs, indent=2)[:200]}...")

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """Log LLM start."""
        model = kwargs.get('invocation_params', {}).get('model_name', 'unknown')
        self.trace.append({
            "event": "llm_start",
            "model": model,
            "prompt_preview": prompts[0][:100] if prompts else "",
            "timestamp": datetime.now().isoformat()
        })
        if self.verbose:
            print(f"\n🤖 LLM Start: {model}")
            print(f"   Prompt: {prompts[0][:150]}..." if prompts else "")

    def on_llm_end(self, response, **kwargs) -> None:
        """Log LLM end."""
        try:
            output = response.generations[0][0].text if response.generations else "No output"
            self.trace.append({
                "event": "llm_end",
                "output_preview": output[:100],
                "timestamp": datetime.now().isoformat()
            })
            if self.verbose:
                print(f"✅ LLM End")
                print(f"   Response: {output[:150]}...")
        except:
            pass

    def on_retriever_start(self, serialized: Dict[str, Any], query: str, **kwargs) -> None:
        """Log retrieval start."""
        self.trace.append({
            "event": "retrieval_start",
            "query": query,
            "timestamp": datetime.now().isoformat()
        })
        if self.verbose:
            print(f"\n🔍 Retrieval Start")
            print(f"   Query: {query}")

    def on_retriever_end(self, documents, **kwargs) -> None:
        """Log retrieval end."""
        self.trace.append({
            "event": "retrieval_end",
            "num_docs": len(documents),
            "timestamp": datetime.now().isoformat()
        })
        if self.verbose:
            print(f"✅ Retrieval End: {len(documents)} documents")

    def get_trace(self) -> List[Dict]:
        """Get full execution trace."""
        return self.trace

# ========== PRODUCTION RAG WITH OBSERVABILITY ==========

class ObservableRAGSystem:
    """RAG system with comprehensive observability."""

    def __init__(self):
        # Initialize callbacks
        self.cost_tracker = CostTrackingCallback()
        self.perf_tracker = PerformanceTrackingCallback()
        self.error_tracker = ErrorTrackingCallback()
        self.trace_callback = DetailedTracingCallback(verbose=True)

        # Create callback manager
        self.callback_manager = CallbackManager([
            self.cost_tracker,
            self.perf_tracker,
            self.error_tracker,
            self.trace_callback
        ])

        # Initialize components with callbacks
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            callbacks=[self.cost_tracker, self.perf_tracker, self.error_tracker]
        )

        self.embeddings = OpenAIEmbeddings(
            callbacks=[self.cost_tracker, self.perf_tracker]
        )

        # Setup vector store (using sample data)
        self.vectorstore = Chroma.from_texts(
            texts=[
                "LangChain is a framework for developing applications powered by language models.",
                "Callbacks in LangChain enable monitoring, logging, and debugging of LLM applications.",
                "Vector stores enable semantic search by storing and retrieving embeddings.",
                "RAG (Retrieval-Augmented Generation) combines retrieval with generation for better answers."
            ],
            embedding=self.embeddings
        )

        # Create RAG chain
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 2}
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.retriever,
            return_source_documents=True,
            callbacks=[self.cost_tracker, self.perf_tracker, self.error_tracker, self.trace_callback]
        )

    def query(self, question: str) -> Dict[str, Any]:
        """Execute query with full observability."""
        print("=" * 80)
        print(f"QUERY: {question}")
        print("=" * 80)

        start_time = time.time()

        try:
            result = self.qa_chain.invoke({"query": question})

            duration = time.time() - start_time

            return {
                "success": True,
                "answer": result['result'],
                "source_documents": [doc.page_content for doc in result.get('source_documents', [])],
                "duration_ms": round(duration * 1000, 2)
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "duration_ms": round(duration * 1000, 2)
            }

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        return {
            "cost_metrics": self.cost_tracker.get_summary(),
            "performance_metrics": self.perf_tracker.get_summary(),
            "error_metrics": self.error_tracker.get_summary(),
            "execution_trace": self.trace_callback.get_trace()
        }

# ========== USAGE EXAMPLE ==========
print("\n=== Observable RAG System Demo ===\n")

rag_system = ObservableRAGSystem()

# Execute multiple queries
queries = [
    "What is LangChain?",
    "How do callbacks work in LangChain?",
    "What is RAG and why is it useful?"
]

results = []
for query in queries:
    result = rag_system.query(query)
    results.append(result)

    print(f"\n{'=' * 80}")
    print(f"Answer: {result.get('answer', 'Error')}")
    print(f"Duration: {result.get('duration_ms')}ms")
    print(f"{'=' * 80}\n")

# Print comprehensive metrics
print("\n" + "=" * 80)
print("=== COMPREHENSIVE METRICS SUMMARY ===")
print("=" * 80)

metrics = rag_system.get_metrics_summary()

print("\n📊 COST METRICS:")
print(json.dumps(metrics['cost_metrics'], indent=2))

print("\n⚡ PERFORMANCE METRICS:")
print(json.dumps(metrics['performance_metrics'], indent=2))

print("\n❌ ERROR METRICS:")
print(json.dumps(metrics['error_metrics'], indent=2))

print("\n🔍 EXECUTION TRACE:")
print(f"Total events: {len(metrics['execution_trace'])}")
print("Recent events:")
for event in metrics['execution_trace'][-5:]:
    print(f"  - {event['event']} at {event['timestamp']}")

# ========== INTEGRATION WITH EXTERNAL PLATFORMS ==========
class LangSmithCallback(BaseCallbackHandler):
    """Mock integration with LangSmith tracing platform."""

    def __init__(self, project_name: str, api_key: str):
        self.project_name = project_name
        self.api_key = api_key
        self.traces = []

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        """Send trace to LangSmith."""
        # In production: POST to LangSmith API
        trace_data = {
            "project": self.project_name,
            "run_id": kwargs.get('run_id'),
            "event": "chain_start",
            "data": inputs
        }
        self.traces.append(trace_data)
        # self._send_to_langsmith(trace_data)

    def _send_to_langsmith(self, data: Dict):
        """Send data to LangSmith API."""
        # Implementation: HTTP POST to LangSmith
        pass

print("\n=== EXTERNAL PLATFORM INTEGRATION ===")
print("Production systems integrate with:")
print("  - LangSmith: https://smith.langchain.com")
print("  - LangFuse: https://langfuse.com")
print("  - Datadog/New Relic: Custom callback handlers")
print("  - Prometheus: Metrics export")
```

### Why This Example Shows Observability Power:

1. **Multi-Dimensional Tracking**: Cost, performance, errors, and execution traces
2. **Production-Ready Metrics**: Real pricing, statistical analysis, error categorization
3. **Debugging Support**: Full execution traces with timestamps and intermediate values
4. **External Integration**: Ready for LangSmith, LangFuse, APM tools
5. **Real-Time Monitoring**: Immediate visibility into system behavior

## Best Practices for Mastering Callbacks and Observability

1. **Implement cost tracking from day one**: Don't wait until you get a surprise $10K bill. Track every token with model-specific pricing. Log costs per user, per session, per feature. Set alerts at $100, $500, $1K daily spend thresholds. Cost overruns are the #1 LLM production incident.

2. **Use separate callbacks for different concerns**: Don't build one mega-callback. Create focused callbacks: CostCallback, PerformanceCallback, ErrorCallback, DebugCallback. Enable/disable independently in different environments (verbose debugging in dev, cost+error in prod).

3. **Always track both success and failure paths**: Most callbacks only log successes. Critical production systems need error callbacks (`on_llm_error`, `on_chain_error`, `on_tool_error`). Errors are your most valuable debugging signal - log them with full context (inputs, intermediate state, error type).

4. **Integrate with your existing observability stack**: Don't build a new monitoring system. Write callbacks that export to Datadog, New Relic, Prometheus, CloudWatch - whatever you already use. Unified monitoring is 10x more valuable than LLM-specific dashboards.

5. **Use trace IDs to correlate events across distributed systems**: Pass trace/request IDs through callbacks and attach to all logs, metrics, and external API calls. When debugging a production issue, you need to correlate LLM calls with DB queries, API calls, and user actions. Structured logging with trace IDs makes this possible.

## Common Pitfalls to Avoid

- **Don't ignore callback exceptions**: Wrap callback code in try/except or failures cascade
- **Avoid blocking I/O in callbacks**: Callbacks run synchronously; async operations block the chain
- **Don't log sensitive data**: PII, API keys, and passwords can appear in prompts/outputs
- **Remember callback overhead**: Excessive logging degrades performance
- **Don't skip cost tracking**: Token costs compound quickly at scale
