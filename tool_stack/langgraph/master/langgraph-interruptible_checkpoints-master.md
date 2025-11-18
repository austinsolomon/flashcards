# LangGraph Interruptible Checkpoints

## Concept Overview

Interruptible checkpoints enable pausing graph execution at specific nodes, persisting state, and resuming later with new input. This is critical for building long-running workflows, human-in-the-loop systems, and applications requiring durability. Checkpoints allow workflows to survive crashes, enable external interventions, and decouple workflow stages across time and services.

---

## Advanced Level: Multi-Stage Checkpoint System with State Versioning

A sophisticated system managing complex workflows with multiple checkpoints, state versioning, and recovery.

```python
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from pydantic import BaseModel, Field
from typing import Annotated, Optional, Literal, Any
from datetime import datetime, timedelta
from enum import Enum
import operator
import asyncio
import uuid
import json

class CheckpointType(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SAFETY = "safety"

class StateVersion(BaseModel):
    """Immutable snapshot of state at checkpoint."""
    version_id: str
    timestamp: str
    checkpoint_type: CheckpointType
    state_hash: str
    state_data: dict
    prev_version_id: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

class CheckpointMetadata(BaseModel):
    """Metadata for checkpoint management."""
    checkpoint_id: str
    created_at: str
    node_name: str
    reason: str
    state_version_id: str
    timeout_seconds: Optional[int] = None
    requires_approval: bool = False

class AdvancedCheckpointState(BaseModel):
    """State with checkpoint management."""
    workflow_id: str
    current_node: str
    messages: Annotated[list[dict], add_messages] = Field(default_factory=list)
    state_versions: Annotated[list[StateVersion], operator.add]
    checkpoints: Annotated[list[CheckpointMetadata], operator.add]
    current_version_id: str
    data: dict = Field(default_factory=dict)
    recovery_metadata: dict = Field(default_factory=dict)

class CheckpointManager:
    """Manages checkpoint lifecycle and state versioning."""
    def __init__(self):
        self.checkpointer = SqliteSaver.from_conn_string(":memory:")
        self.version_graph = {}
        self.timeout_jobs = {}

    def create_state_version(
        self,
        state: AdvancedCheckpointState,
        checkpoint_type: CheckpointType
    ) -> StateVersion:
        """Create immutable state snapshot."""
        version_id = str(uuid.uuid4())
        state_hash = hash(json.dumps(state.data, sort_keys=True, default=str))

        version = StateVersion(
            version_id=version_id,
            timestamp=datetime.now().isoformat(),
            checkpoint_type=checkpoint_type,
            state_hash=str(state_hash),
            state_data=state.data.copy(),
            prev_version_id=state.current_version_id if state.current_version_id else None
        )

        # Build version graph
        if version.prev_version_id:
            self.version_graph[version.prev_version_id] = version_id

        return version

    def create_checkpoint(
        self,
        state: AdvancedCheckpointState,
        node_name: str,
        reason: str,
        requires_approval: bool = False,
        timeout_seconds: Optional[int] = None
    ) -> CheckpointMetadata:
        """Create checkpoint with metadata."""
        checkpoint = CheckpointMetadata(
            checkpoint_id=str(uuid.uuid4()),
            created_at=datetime.now().isoformat(),
            node_name=node_name,
            reason=reason,
            state_version_id=state.current_version_id,
            timeout_seconds=timeout_seconds,
            requires_approval=requires_approval
        )

        # Set timeout job if specified
        if timeout_seconds:
            job_id = str(uuid.uuid4())
            self.timeout_jobs[job_id] = {
                "checkpoint_id": checkpoint.checkpoint_id,
                "timeout_at": datetime.now() + timedelta(seconds=timeout_seconds),
                "action": "auto_resume"
            }

        return checkpoint

    async def can_resume(
        self,
        checkpoint_metadata: CheckpointMetadata
    ) -> tuple[bool, Optional[str]]:
        """Check if checkpoint can be resumed."""
        # Check timeout
        if checkpoint_metadata.timeout_seconds:
            job = next(
                (j for j in self.timeout_jobs.values()
                 if j["checkpoint_id"] == checkpoint_metadata.checkpoint_id),
                None
            )
            if job and datetime.now() > job["timeout_at"]:
                return True, "Timeout reached, auto-resuming"

        # Check approval requirement
        if checkpoint_metadata.requires_approval:
            return False, "Awaiting approval"

        return True, None

    def get_version_ancestry(self, version_id: str) -> list[str]:
        """Get all ancestor versions of a version."""
        ancestry = [version_id]
        current = version_id

        while current in self.version_graph:
            current = self.version_graph[current]
            ancestry.append(current)

        return ancestry

def create_advanced_checkpoint_system():
    """Create advanced checkpoint workflow."""
    manager = CheckpointManager()

    async def processing_node_1(state: AdvancedCheckpointState):
        """First processing stage with checkpoint."""
        state.data["stage1_output"] = "processed_batch_1"
        state.current_node = "processing_1"

        version = manager.create_state_version(state, CheckpointType.AUTOMATIC)
        checkpoint = manager.create_checkpoint(
            state,
            node_name="processing_1",
            reason="Intermediate data checkpoint",
            timeout_seconds=3600
        )

        return {
            "state_versions": [version],
            "checkpoints": [checkpoint],
            "current_version_id": version.version_id,
            "messages": [{"event": "stage1_completed", "timestamp": datetime.now().isoformat()}]
        }

    async def validation_node(state: AdvancedCheckpointState):
        """Validation requiring approval."""
        state.current_node = "validation"

        version = manager.create_state_version(state, CheckpointType.SAFETY)
        checkpoint = manager.create_checkpoint(
            state,
            node_name="validation",
            reason="Quality validation checkpoint",
            requires_approval=True,
            timeout_seconds=7200
        )

        return {
            "state_versions": [version],
            "checkpoints": [checkpoint],
            "current_version_id": version.version_id,
            "messages": [{"event": "validation_ready", "timestamp": datetime.now().isoformat()}]
        }

    async def processing_node_2(state: AdvancedCheckpointState):
        """Second processing stage."""
        state.data["stage2_output"] = "processed_batch_2"
        state.current_node = "processing_2"

        version = manager.create_state_version(state, CheckpointType.AUTOMATIC)

        return {
            "state_versions": [version],
            "current_version_id": version.version_id,
            "data": state.data,
            "messages": [{"event": "stage2_completed", "timestamp": datetime.now().isoformat()}]
        }

    async def recovery_check(state: AdvancedCheckpointState):
        """Check if recovery is needed and available."""
        if state.recovery_metadata.get("recovery_needed"):
            ancestry = manager.get_version_ancestry(state.current_version_id)
            return {
                "recovery_metadata": {
                    "recovery_needed": False,
                    "recovered_from": ancestry[0] if ancestry else None,
                    "recovery_timestamp": datetime.now().isoformat()
                }
            }
        return state

    # Build workflow
    workflow = StateGraph(AdvancedCheckpointState)
    workflow.add_node("process_1", processing_node_1)
    workflow.add_node("validate", validation_node)
    workflow.add_node("process_2", processing_node_2)
    workflow.add_node("recover", recovery_check)

    workflow.add_edge(START, "process_1")
    workflow.add_edge("process_1", "validate")
    workflow.add_edge("validate", "process_2")
    workflow.add_edge("process_2", "recover")
    workflow.add_edge("recover", END)

    return workflow.compile(checkpointer=manager.checkpointer)

# Usage
async def main():
    system = create_advanced_checkpoint_system()
    initial_state = AdvancedCheckpointState(
        workflow_id=str(uuid.uuid4()),
        current_node="start",
        state_versions=[],
        checkpoints=[],
        current_version_id="v0",
        data={}
    )

    config = {"configurable": {"thread_id": "workflow_001"}}
    # result = await asyncio.to_thread(system.invoke, initial_state, config)
```

---

## Best Practices for Interruptible Checkpoint Mastery

1. **Strategic Checkpoint Placement**: Place checkpoints before long-running operations, approval steps, and state transitions. Use automatic checkpoints for resilience and manual checkpoints for controlled pause points. Balance checkpoint frequency with overhead.

2. **State Versioning and Lineage**: Create immutable snapshots at each checkpoint. Maintain version graphs to track state evolution. This enables recovery from failures, rollback to previous states, and audit trails.

3. **Timeout and Auto-Resume Logic**: Define appropriate timeout durations for each checkpoint type. Implement auto-resume mechanisms for non-blocking checkpoints after timeouts. Require explicit approval for state-changing operations.

4. **Persistent Checkpoint Storage**: Use durable checkpoint backends (SQLite, PostgreSQL, cloud storage). Test recovery by simulating crashes and verifying state restoration. Include metadata for operational context.

5. **Monitoring and Alerting**: Track checkpoint durations, approval wait times, and timeout frequency. Alert on abnormally long pauses indicating bottlenecks. Log all checkpoint transitions for debugging complex workflow issues.
