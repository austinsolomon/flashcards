# LangGraph Multi-Agent Orchestration Patterns

## Concept Overview

Multi-agent orchestration enables coordinating multiple specialized AI agents to solve complex problems through collaboration. Rather than a single monolithic agent, orchestration patterns use specialized agents (each expert in a domain) that communicate, delegate work, and combine results. This pattern is essential for tackling problems requiring diverse expertise, enabling parallelization, and improving reliability through redundancy.

---

## Intermediate Level: Collaborative Multi-Agent with Message Passing

A sophisticated system where multiple agents collaborate through message passing and shared state.

```python
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from datetime import datetime
from enum import Enum
import operator

class MessageType(str, Enum):
    QUERY = "query"
    RESPONSE = "response"
    REQUEST = "request"
    CONFIRMATION = "confirmation"

class AgentMessage(BaseModel):
    """Message between agents."""
    sender: str
    receiver: str
    message_type: MessageType
    content: str
    timestamp: str
    requires_response: bool = False

class CollaborativeState(BaseModel):
    """State for multi-agent collaboration."""
    task_id: str
    task_description: str
    active_agents: list[str]
    messages: Annotated[list[AgentMessage], operator.add]
    agent_outputs: dict[str, str] = Field(default_factory=dict)
    consensus: Optional[str] = None
    workflow_status: str = "in_progress"

def create_collaborative_workflow():
    """Create workflow with collaborative agents."""

    def researcher_agent(state: CollaborativeState):
        """Researches and gathers information."""
        message = AgentMessage(
            sender="researcher",
            receiver="synthesizer",
            message_type=MessageType.RESPONSE,
            content="Research complete: Found 5 relevant sources",
            timestamp=datetime.now().isoformat(),
            requires_response=False
        )

        return {
            "messages": [message],
            "agent_outputs": {"researcher": "Research findings compiled"}
        }

    def validator_agent(state: CollaborativeState):
        """Validates findings and approaches."""
        message = AgentMessage(
            sender="validator",
            receiver="synthesizer",
            message_type=MessageType.RESPONSE,
            content="Validation complete: All sources are credible",
            timestamp=datetime.now().isoformat(),
            requires_response=False
        )

        return {
            "messages": [message],
            "agent_outputs": {"validator": "Validation passed"}
        }

    def synthesizer_agent(state: CollaborativeState):
        """Synthesizes outputs from other agents."""
        # Check for research and validation
        has_research = any(m.sender == "researcher" for m in state.messages)
        has_validation = any(m.sender == "validator" for m in state.messages)

        if has_research and has_validation:
            synthesis = "Synthesized final report incorporating research and validation"
            status = "completed"
        else:
            synthesis = "Waiting for other agents"
            status = "in_progress"

        return {
            "agent_outputs": {"synthesizer": synthesis},
            "workflow_status": status,
            "consensus": synthesis
        }

    # Build workflow
    workflow = StateGraph(CollaborativeState)
    workflow.add_node("research", researcher_agent)
    workflow.add_node("validate", validator_agent)
    workflow.add_node("synthesize", synthesizer_agent)

    workflow.add_edge(START, "research")
    workflow.add_edge(START, "validate")
    workflow.add_edge("research", "synthesize")
    workflow.add_edge("validate", "synthesize")
    workflow.add_edge("synthesize", END)

    return workflow.compile()

# Usage
workflow = create_collaborative_workflow()
result = workflow.invoke(CollaborativeState(
    task_id="task_001",
    task_description="Analyze market trends",
    active_agents=["researcher", "validator", "synthesizer"],
    messages=[]
))
print(f"Consensus: {result.consensus}")
```

---

## Best Practices for Multi-Agent Orchestration Mastery

1. **Team Formation Strategy**: Match agent specializations to task requirements. Prefer specialized generalists over generalists. Assign lead agents for complex tasks. Track agent performance and prefer agents with proven success on similar tasks.

2. **Message Protocol and Communication**: Define clear message types (query, response, request, confirmation) and enforce protocol. Use timestamps and message IDs for tracking. Implement timeout mechanisms for hung agents.

3. **Delegation and Subtask Decomposition**: Decompose complex tasks into subtasks aligned with agent specializations. Assign subtasks to most capable agents. Track dependencies between subtasks to enable parallelization where possible.

4. **Consensus and Conflict Resolution**: Weight agent decisions by confidence scores and expertise relevance. Implement voting or weighted averaging for consensus. Escalate deadlocked decisions to supervisory agents or humans.

5. **Performance Tracking and Optimization**: Monitor agent performance metrics (success rate, average response time, quality scores). Use this data to improve team formation. Remove unreliable agents and promote high performers. Continuously fine-tune task-to-agent assignments.
