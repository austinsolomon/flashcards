# LangGraph Interruptible Checkpoints: Beginner to Advanced

## Concept Overview

Interruptible checkpoints enable pausing graph execution at specific nodes, persisting state, and resuming later with new input. This is critical for building long-running workflows, human-in-the-loop systems, and applications requiring durability. Checkpoints allow workflows to survive crashes, enable external interventions, and decouple workflow stages across time and services.

---

## Beginner Level: Basic Checkpoint with Resume

A simple workflow that pauses and resumes at a checkpoint.

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel
from typing import Annotated
import operator

class CheckpointState(BaseModel):
    user_id: str
    step: int
    data: str
    status: str

def create_basic_checkpoint_workflow():
    """Create workflow with basic checkpoints."""
    checkpointer = MemorySaver()

    def step1_node(state: CheckpointState):
        """First processing step."""
        return {
            "data": f"processed_{state.user_id}",
            "step": 1
        }

    def step2_node(state: CheckpointState):
        """Second processing step (can be interrupted)."""
        return {
            "data": f"{state.data}_enriched",
            "step": 2,
            "status": "ready_for_approval"  # Checkpoint here
        }

    def step3_node(state: CheckpointState):
        """Final step after approval."""
        return {
            "data": f"{state.data}_finalized",
            "step": 3,
            "status": "completed"
        }

    # Build workflow
    workflow = StateGraph(CheckpointState)
    workflow.add_node("step1", step1_node)
    workflow.add_node("step2", step2_node)
    workflow.add_node("step3", step3_node)

    workflow.add_edge(START, "step1")
    workflow.add_edge("step1", "step2")
    workflow.add_edge("step2", "step3")
    workflow.add_edge("step3", END)

    return workflow.compile(checkpointer=checkpointer)

# Usage
workflow = create_basic_checkpoint_workflow()

# Initial run - stops at checkpoint
config = {"configurable": {"thread_id": "user_001"}}
state = CheckpointState(user_id="user_001", step=0, data="", status="")
result1 = workflow.invoke(state, config)
print(f"After step 2: {result1}")

# Resume from checkpoint with approval
result2 = workflow.invoke(None, config)  # None means continue from checkpoint
print(f"After step 3: {result2}")
```

---

## Intermediate Level: Checkpoint with Approval Workflow

A realistic approval workflow with checkpoint persistence and conditional resumption.

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from pydantic import BaseModel, Field
from typing import Annotated, Optional, Literal
from datetime import datetime
import operator
import json

class ApprovalRequest(BaseModel):
    """Request awaiting approval."""
    request_id: str
    requester: str
    amount: float
    description: str
    created_at: str

class ApprovalState(BaseModel):
    """State for approval workflow."""
    request: ApprovalRequest
    approval_status: Literal["pending", "approved", "rejected", "completed"]
    approver_comments: str = ""
    approval_timestamp: Optional[str] = None
    execution_log: Annotated[list[str], operator.add]

def create_approval_workflow():
    """Create workflow with approval checkpoints."""
    # Use SQLite for persistent checkpointing
    checkpointer = SqliteSaver.from_conn_string(":memory:")

    def validate_request_node(state: ApprovalState):
        """Validate incoming request."""
        is_valid = (
            state.request.amount > 0 and
            state.request.description and
            state.request.requester
        )

        log_entry = f"[{datetime.now().isoformat()}] Validation: {'PASSED' if is_valid else 'FAILED'}"

        if not is_valid:
            return {
                "approval_status": "rejected",
                "execution_log": [log_entry]
            }

        return {
            "approval_status": "pending",
            "execution_log": [log_entry]
        }

    def wait_for_approval_node(state: ApprovalState):
        """Pause and wait for manual approval."""
        # This node pauses execution at checkpoint
        log_entry = f"[{datetime.now().isoformat()}] Waiting for approval at checkpoint"
        return {"execution_log": [log_entry]}

    def process_approval_node(state: ApprovalState):
        """Process the approval decision."""
        if state.approval_status not in ["approved", "rejected"]:
            log_entry = f"[{datetime.now().isoformat()}] No approval decision received"
            return {"execution_log": [log_entry]}

        status = "completed" if state.approval_status == "approved" else "rejected"
        log_entry = f"[{datetime.now().isoformat()}] Processed: {state.approval_status}"

        if status == "completed":
            log_entry += " - Executing request"

        return {
            "approval_status": status,
            "approval_timestamp": datetime.now().isoformat(),
            "execution_log": [log_entry]
        }

    # Build workflow
    workflow = StateGraph(ApprovalState)
    workflow.add_node("validate", validate_request_node)
    workflow.add_node("wait_approval", wait_for_approval_node)
    workflow.add_node("process_approval", process_approval_node)

    workflow.add_edge(START, "validate")

    workflow.add_conditional_edges(
        "validate",
        lambda s: "wait_approval" if s.approval_status == "pending" else "process_approval",
        {"wait_approval": "wait_approval", "process_approval": "process_approval"}
    )

    workflow.add_edge("wait_approval", "process_approval")
    workflow.add_edge("process_approval", END)

    return workflow.compile(checkpointer=checkpointer)

# Usage
workflow = create_approval_workflow()

request = ApprovalRequest(
    request_id="req_001",
    requester="alice@company.com",
    amount=5000.0,
    description="Q4 marketing budget",
    created_at=datetime.now().isoformat()
)

config = {"configurable": {"thread_id": "approval_001"}}

# Step 1: Submit request (pauses at wait_approval checkpoint)
state = ApprovalState(
    request=request,
    approval_status="pending",
    execution_log=[]
)
result1 = workflow.invoke(state, config)
print(f"Status after submission: {result1.approval_status}")

# Step 2: Resume with approval decision
state_with_approval = ApprovalState(
    request=request,
    approval_status="approved",
    approver_comments="Looks good, proceeding.",
    execution_log=[]
)
result2 = workflow.invoke(state_with_approval, config)
print(f"Final status: {result2.approval_status}")
```

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
