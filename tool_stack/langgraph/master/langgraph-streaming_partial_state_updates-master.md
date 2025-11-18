# LangGraph Streaming & Partial State Updates

## Concept Overview

Streaming and partial state updates enable real-time feedback and efficient state mutations without processing entire state objects. This pattern is critical for building responsive UIs, handling large states, and optimizing bandwidth. Instead of returning complete state snapshots, nodes emit only changed fields, allowing incremental updates to propagate to clients immediately.

---

## Advanced Level: Real-Time Streaming with Diff-Based Updates

A sophisticated streaming system that efficiently transmits only state diffs to clients.

```python
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from typing import Annotated, Optional, Any, Callable
from datetime import datetime
from enum import Enum
import operator
import json
import difflib
import hashlib

class UpdateType(str, Enum):
    ADD = "add"
    UPDATE = "update"
    DELETE = "delete"
    REPLACE = "replace"

class StateDiff(BaseModel):
    """Efficient state change representation."""
    update_type: UpdateType
    path: str  # JSON path to changed field
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    timestamp: str
    change_hash: str

class ClientSession(BaseModel):
    """Tracks client subscription and state."""
    client_id: str
    last_state_hash: str
    subscribed_paths: list[str]  # Fields client cares about
    buffer: Annotated[list[StateDiff], operator.add]

class StreamingDiffState(BaseModel):
    """State optimized for diff-based streaming."""
    workflow_id: str
    data: dict = Field(default_factory=dict)
    state_hash: str = ""
    state_history: Annotated[list[dict], operator.add]
    client_sessions: dict[str, ClientSession] = Field(default_factory=dict)
    pending_diffs: Annotated[list[StateDiff], operator.add]
    metrics: dict = Field(default_factory=dict)

class StreamingDiffManager:
    """Manages efficient state diffing and streaming."""
    def __init__(self):
        self.previous_state = {}

    def compute_state_hash(self, state_data: dict) -> str:
        """Compute hash of state for change detection."""
        state_str = json.dumps(state_data, sort_keys=True, default=str)
        return hashlib.sha256(state_str.encode()).hexdigest()

    def compute_diffs(
        self,
        old_state: dict,
        new_state: dict
    ) -> list[StateDiff]:
        """Compute minimal diffs between states."""
        diffs = []

        # Find added/updated keys
        for key, new_value in new_state.items():
            old_value = old_state.get(key)

            if key not in old_state:
                # New field
                diff = StateDiff(
                    update_type=UpdateType.ADD,
                    path=f"/{key}",
                    new_value=new_value,
                    timestamp=datetime.now().isoformat(),
                    change_hash=""
                )
            elif old_value != new_value:
                # Updated field
                diff = StateDiff(
                    update_type=UpdateType.UPDATE,
                    path=f"/{key}",
                    old_value=old_value,
                    new_value=new_value,
                    timestamp=datetime.now().isoformat(),
                    change_hash=""
                )
            else:
                continue

            # Compute change hash
            change_str = json.dumps({
                "path": diff.path,
                "new_value": diff.new_value
            }, sort_keys=True, default=str)
            diff.change_hash = hashlib.sha256(change_str.encode()).hexdigest()
            diffs.append(diff)

        # Find deleted keys
        for key in old_state:
            if key not in new_state:
                diff = StateDiff(
                    update_type=UpdateType.DELETE,
                    path=f"/{key}",
                    old_value=old_state[key],
                    timestamp=datetime.now().isoformat(),
                    change_hash=hashlib.sha256(f"delete_{key}".encode()).hexdigest()
                )
                diffs.append(diff)

        return diffs

    def filter_diffs_for_client(
        self,
        diffs: list[StateDiff],
        subscribed_paths: list[str]
    ) -> list[StateDiff]:
        """Filter diffs to only subscribed paths."""
        if not subscribed_paths:
            return diffs

        filtered = []
        for diff in diffs:
            if any(diff.path.startswith(p) for p in subscribed_paths):
                filtered.append(diff)

        return filtered

def create_streaming_diff_system():
    """Create streaming system with diff-based updates."""
    diff_manager = StreamingDiffManager()

    def process_batch_with_streaming(state: StreamingDiffState):
        """Process data and emit diffs."""
        old_state = state.data.copy()
        old_hash = state.state_hash

        # Simulate processing
        new_data = state.data.copy()
        new_data["processed"] = True
        new_data["timestamp"] = datetime.now().isoformat()
        new_data["count"] = new_data.get("count", 0) + 1

        # Compute diffs
        diffs = diff_manager.compute_diffs(old_state, new_data)

        # Update state hash
        new_hash = diff_manager.compute_state_hash(new_data)

        # For each client, filter relevant diffs
        client_buffers = {}
        for client_id, session in state.client_sessions.items():
            filtered_diffs = diff_manager.filter_diffs_for_client(
                diffs,
                session.subscribed_paths
            )
            if filtered_diffs:
                # Create updated session with new diffs
                updated_session = ClientSession(
                    client_id=client_id,
                    last_state_hash=new_hash,
                    subscribed_paths=session.subscribed_paths,
                    buffer=filtered_diffs
                )
                client_buffers[client_id] = updated_session

        return {
            "data": new_data,
            "state_hash": new_hash,
            "pending_diffs": diffs,
            "state_history": [{"hash": old_hash, "timestamp": datetime.now().isoformat()}]
        }

    def stream_to_clients(state: StreamingDiffState):
        """Stream diffs to subscribed clients."""
        # Simulate streaming diffs to multiple clients
        metrics = {
            "diffs_sent": len(state.pending_diffs),
            "clients_updated": len(state.client_sessions),
            "bytes_transmitted": sum(
                len(json.dumps(d.dict()))
                for d in state.pending_diffs
            ),
            "timestamp": datetime.now().isoformat()
        }

        return {"metrics": metrics}

    # Build workflow
    workflow = StateGraph(StreamingDiffState)
    workflow.add_node("process", process_batch_with_streaming)
    workflow.add_node("stream", stream_to_clients)

    workflow.add_edge(START, "process")
    workflow.add_edge("process", "stream")
    workflow.add_edge("stream", END)

    return workflow.compile()

# Usage
workflow = create_streaming_diff_system()
initial_state = StreamingDiffState(
    workflow_id="stream_001",
    data={"items": [], "status": "idle"},
    state_hash="initial_hash",
    client_sessions={
        "client_1": ClientSession(
            client_id="client_1",
            last_state_hash="initial_hash",
            subscribed_paths=["/processed", "/count"],
            buffer=[]
        )
    },
    pending_diffs=[]
)
result = workflow.invoke(initial_state)
print(f"Metrics: {result.metrics}")
```

---

## Best Practices for Streaming & Partial State Updates Mastery

1. **Diff-Based Updates**: Compute and transmit only state changes, not complete state objects. Use JSON-path notation to identify changed fields. This dramatically reduces bandwidth and latency in high-frequency update scenarios.

2. **Client Subscription Filtering**: Let clients specify which state paths they care about. Filter diffs server-side before streaming. This reduces unnecessary updates and improves client performance.

3. **Buffering and Batching**: Don't stream every atomic change individually. Buffer diffs and batch them into coherent update packets. Balance between latency (smaller batches) and efficiency (larger batches).

4. **State Hash Tracking**: Compute hashes of full state snapshots. Use hashes to detect when client state diverges from server. Enable client-side caching and efficient resync mechanisms.

5. **Progressive Streaming Feedback**: For long-running operations, emit progress updates as partial state changes. Show intermediate results, progress percentages, and incremental improvements in real-time rather than waiting for completion.
