# LangGraph Interruptible Checkpoints

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

## Best Practices for Interruptible Checkpoint Mastery

1. **Strategic Checkpoint Placement**: Place checkpoints before long-running operations, approval steps, and state transitions. Use automatic checkpoints for resilience and manual checkpoints for controlled pause points. Balance checkpoint frequency with overhead.

2. **State Versioning and Lineage**: Create immutable snapshots at each checkpoint. Maintain version graphs to track state evolution. This enables recovery from failures, rollback to previous states, and audit trails.

3. **Timeout and Auto-Resume Logic**: Define appropriate timeout durations for each checkpoint type. Implement auto-resume mechanisms for non-blocking checkpoints after timeouts. Require explicit approval for state-changing operations.

4. **Persistent Checkpoint Storage**: Use durable checkpoint backends (SQLite, PostgreSQL, cloud storage). Test recovery by simulating crashes and verifying state restoration. Include metadata for operational context.

5. **Monitoring and Alerting**: Track checkpoint durations, approval wait times, and timeout frequency. Alert on abnormally long pauses indicating bottlenecks. Log all checkpoint transitions for debugging complex workflow issues.
