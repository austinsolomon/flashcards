# LangGraph Streaming & Partial State Updates

## Concept Overview

Streaming and partial state updates enable real-time feedback and efficient state mutations without processing entire state objects. This pattern is critical for building responsive UIs, handling large states, and optimizing bandwidth. Instead of returning complete state snapshots, nodes emit only changed fields, allowing incremental updates to propagate to clients immediately.

---

## Beginner Level: Simple Streaming Output

A basic streaming example that outputs data as it's generated.

```python
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from typing import Iterator

class StreamingState(BaseModel):
    query: str
    response: str

def create_basic_streaming_workflow():
    """Create workflow with streaming output."""
    llm = ChatOpenAI(model="gpt-4")

    def stream_response(state: StreamingState):
        """Generate streaming response."""
        response = ""
        for chunk in llm.stream([HumanMessage(content=state.query)]):
            if chunk.content:
                response += chunk.content
                print(chunk.content, end="", flush=True)  # Stream to console
        return {"response": response}

    # Build workflow
    workflow = StateGraph(StreamingState)
    workflow.add_node("stream", stream_response)
    workflow.add_edge(START, "stream")
    workflow.add_edge("stream", END)

    return workflow.compile()

# Usage
workflow = create_basic_streaming_workflow()
state = StreamingState(
    query="Explain quantum computing in 3 sentences",
    response=""
)
result = workflow.invoke(state)
```

---

## Best Practices for Streaming & Partial State Updates Mastery

1. **Diff-Based Updates**: Compute and transmit only state changes, not complete state objects. Use JSON-path notation to identify changed fields. This dramatically reduces bandwidth and latency in high-frequency update scenarios.

2. **Client Subscription Filtering**: Let clients specify which state paths they care about. Filter diffs server-side before streaming. This reduces unnecessary updates and improves client performance.

3. **Buffering and Batching**: Don't stream every atomic change individually. Buffer diffs and batch them into coherent update packets. Balance between latency (smaller batches) and efficiency (larger batches).

4. **State Hash Tracking**: Compute hashes of full state snapshots. Use hashes to detect when client state diverges from server. Enable client-side caching and efficient resync mechanisms.

5. **Progressive Streaming Feedback**: For long-running operations, emit progress updates as partial state changes. Show intermediate results, progress percentages, and incremental improvements in real-time rather than waiting for completion.
