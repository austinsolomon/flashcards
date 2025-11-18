# LangGraph Interruptible Checkpoints

## Concept Overview

Interruptible checkpoints enable pausing graph execution at specific nodes, persisting state, and resuming later with new input. This is critical for building long-running workflows, human-in-the-loop systems, and applications requiring durability. Checkpoints allow workflows to survive crashes, enable external interventions, and decouple workflow stages across time and services.

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

## Best Practices for Interruptible Checkpoint Mastery

1. **Strategic Checkpoint Placement**: Place checkpoints before long-running operations, approval steps, and state transitions. Use automatic checkpoints for resilience and manual checkpoints for controlled pause points. Balance checkpoint frequency with overhead.

2. **State Versioning and Lineage**: Create immutable snapshots at each checkpoint. Maintain version graphs to track state evolution. This enables recovery from failures, rollback to previous states, and audit trails.

3. **Timeout and Auto-Resume Logic**: Define appropriate timeout durations for each checkpoint type. Implement auto-resume mechanisms for non-blocking checkpoints after timeouts. Require explicit approval for state-changing operations.

4. **Persistent Checkpoint Storage**: Use durable checkpoint backends (SQLite, PostgreSQL, cloud storage). Test recovery by simulating crashes and verifying state restoration. Include metadata for operational context.

5. **Monitoring and Alerting**: Track checkpoint durations, approval wait times, and timeout frequency. Alert on abnormally long pauses indicating bottlenecks. Log all checkpoint transitions for debugging complex workflow issues.
