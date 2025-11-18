# LangGraph Multi-Agent Orchestration Patterns

## Concept Overview

Multi-agent orchestration enables coordinating multiple specialized AI agents to solve complex problems through collaboration. Rather than a single monolithic agent, orchestration patterns use specialized agents (each expert in a domain) that communicate, delegate work, and combine results. This pattern is essential for tackling problems requiring diverse expertise, enabling parallelization, and improving reliability through redundancy.

---

## Advanced Level: Hierarchical Multi-Agent System with Dynamic Team Formation

A production-grade system with agent specialization, team formation, task delegation, and consensus mechanisms.

```python
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Annotated, Optional, Literal, Any
from datetime import datetime
from enum import Enum
import operator
import uuid
import json

class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    SPECIALIST = "specialist"
    VALIDATOR = "validator"
    SYNTHESIZER = "synthesizer"

class SpecializationArea(str, Enum):
    TECHNICAL = "technical"
    BUSINESS = "business"
    DATA = "data"
    CREATIVE = "creative"
    SECURITY = "security"

class AgentProfile(BaseModel):
    """Profile of an agent in the system."""
    agent_id: str
    role: AgentRole
    specializations: list[SpecializationArea]
    confidence_score: float
    is_available: bool = True
    current_task_id: Optional[str] = None
    performance_history: list[float] = Field(default_factory=list)

class TaskRequest(BaseModel):
    """Request for task execution."""
    task_id: str
    description: str
    required_specializations: list[SpecializationArea]
    priority: int
    deadline: Optional[str] = None
    required_agents: int = 1

class AgentDecision(BaseModel):
    """Decision made by an agent."""
    agent_id: str
    task_id: str
    decision: str
    confidence: float
    reasoning: str
    timestamp: str

class HierarchicalMultiAgentState(BaseModel):
    """State for hierarchical multi-agent system."""
    workflow_id: str
    task_request: TaskRequest
    agent_registry: dict[str, AgentProfile]
    selected_team: list[str] = Field(default_factory=list)

    task_assignments: dict[str, list[str]] = Field(default_factory=dict)
    agent_decisions: Annotated[list[AgentDecision], add_messages]
    consensus_decision: Optional[str] = None
    final_result: Optional[str] = None
    workflow_status: str = "planning"

class AgentPool:
    """Manages pool of agents and team formation."""
    def __init__(self):
        self.agents = {}
        self.llm = ChatOpenAI(model="gpt-4")

    def register_agent(self, profile: AgentProfile):
        """Register an agent in the pool."""
        self.agents[profile.agent_id] = profile

    def find_suitable_agents(
        self,
        required_specializations: list[SpecializationArea],
        required_count: int
    ) -> list[str]:
        """Find agents matching specialization requirements."""
        suitable = []

        for agent_id, profile in self.agents.items():
            if not profile.is_available:
                continue

            # Check specialization match
            matching_specs = len(
                set(profile.specializations) & set(required_specializations)
            )

            if matching_specs >= len(required_specializations) / 2:
                suitable.append((agent_id, profile.confidence_score))

        # Sort by confidence and return top matches
        suitable.sort(key=lambda x: x[1], reverse=True)
        return [agent_id for agent_id, _ in suitable[:required_count]]

    def assign_tasks(
        self,
        team: list[str],
        task_request: TaskRequest
    ) -> dict[str, list[str]]:
        """Assign task components to team members."""
        assignments = {}

        # Distribute work across team
        for agent_id in team:
            assignments[agent_id] = [f"Subtask of {task_request.task_id}"]

        return assignments

class ConsensusEngine:
    """Implements consensus mechanism across agents."""
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo")

    async def reach_consensus(
        self,
        decisions: list[AgentDecision]
    ) -> str:
        """Combine multiple agent decisions into consensus."""
        if not decisions:
            return "No decisions available"

        if len(decisions) == 1:
            return decisions[0].decision

        # Weighted consensus based on confidence
        total_confidence = sum(d.confidence for d in decisions)
        weights = [d.confidence / total_confidence for d in decisions]

        # Simple majority-based consensus
        decision_counts = {}
        for decision, weight in zip(decisions, weights):
            decision_counts[decision.decision] = decision_counts.get(decision.decision, 0) + weight

        consensus = max(decision_counts, key=decision_counts.get)
        return consensus

def create_hierarchical_multi_agent_system():
    """Create hierarchical multi-agent orchestration system."""
    agent_pool = AgentPool()
    consensus_engine = ConsensusEngine()

    # Register agents
    agent_profiles = [
        AgentProfile(
            agent_id="tech_001",
            role=AgentRole.SPECIALIST,
            specializations=[SpecializationArea.TECHNICAL],
            confidence_score=0.95
        ),
        AgentProfile(
            agent_id="biz_001",
            role=AgentRole.SPECIALIST,
            specializations=[SpecializationArea.BUSINESS],
            confidence_score=0.88
        ),
        AgentProfile(
            agent_id="data_001",
            role=AgentRole.SPECIALIST,
            specializations=[SpecializationArea.DATA],
            confidence_score=0.92
        ),
        AgentProfile(
            agent_id="validator_001",
            role=AgentRole.VALIDATOR,
            specializations=[SpecializationArea.TECHNICAL, SpecializationArea.DATA],
            confidence_score=0.90
        )
    ]

    for profile in agent_profiles:
        agent_pool.register_agent(profile)

    def form_team(state: HierarchicalMultiAgentState):
        """Orchestrator selects and forms optimal team."""
        selected = agent_pool.find_suitable_agents(
            state.task_request.required_specializations,
            state.task_request.required_agents
        )

        assignments = agent_pool.assign_tasks(selected, state.task_request)

        return {
            "selected_team": selected,
            "task_assignments": assignments,
            "workflow_status": "team_formed"
        }

    def execute_specialist_task(state: HierarchicalMultiAgentState):
        """Specialists execute assigned tasks."""
        decisions = []

        for agent_id in state.selected_team:
            decision = AgentDecision(
                agent_id=agent_id,
                task_id=state.task_request.task_id,
                decision=f"Completed by {agent_id}",
                confidence=0.85,
                reasoning="Task execution successful",
                timestamp=datetime.now().isoformat()
            )
            decisions.append(decision)

        return {
            "agent_decisions": decisions,
            "workflow_status": "decisions_made"
        }

    async def reach_consensus_step(state: HierarchicalMultiAgentState):
        """Consensus engine combines decisions."""
        consensus = await consensus_engine.reach_consensus(state.agent_decisions)

        return {
            "consensus_decision": consensus,
            "workflow_status": "consensus_reached"
        }

    def synthesize_result(state: HierarchicalMultiAgentState):
        """Synthesizer creates final result."""
        result = f"Final result: {state.consensus_decision}"

        return {
            "final_result": result,
            "workflow_status": "completed"
        }

    # Build workflow
    workflow = StateGraph(HierarchicalMultiAgentState)
    workflow.add_node("form_team", form_team)
    workflow.add_node("execute", execute_specialist_task)
    workflow.add_node("consensus", reach_consensus_step)
    workflow.add_node("synthesize", synthesize_result)

    workflow.add_edge(START, "form_team")
    workflow.add_edge("form_team", "execute")
    workflow.add_edge("execute", "consensus")
    workflow.add_edge("consensus", "synthesize")
    workflow.add_edge("synthesize", END)

    return workflow.compile()

# Usage
async def main():
    system = create_hierarchical_multi_agent_system()

    initial_state = HierarchicalMultiAgentState(
        workflow_id=str(uuid.uuid4()),
        task_request=TaskRequest(
            task_id="task_001",
            description="Design and validate a data pipeline architecture",
            required_specializations=[
                SpecializationArea.TECHNICAL,
                SpecializationArea.DATA
            ],
            priority=5,
            required_agents=3
        ),
        agent_registry={},
        agent_decisions=[]
    )

    # result = await asyncio.to_thread(system.invoke, initial_state)
```

---

## Best Practices for Multi-Agent Orchestration Mastery

1. **Team Formation Strategy**: Match agent specializations to task requirements. Prefer specialized generalists over generalists. Assign lead agents for complex tasks. Track agent performance and prefer agents with proven success on similar tasks.

2. **Message Protocol and Communication**: Define clear message types (query, response, request, confirmation) and enforce protocol. Use timestamps and message IDs for tracking. Implement timeout mechanisms for hung agents.

3. **Delegation and Subtask Decomposition**: Decompose complex tasks into subtasks aligned with agent specializations. Assign subtasks to most capable agents. Track dependencies between subtasks to enable parallelization where possible.

4. **Consensus and Conflict Resolution**: Weight agent decisions by confidence scores and expertise relevance. Implement voting or weighted averaging for consensus. Escalate deadlocked decisions to supervisory agents or humans.

5. **Performance Tracking and Optimization**: Monitor agent performance metrics (success rate, average response time, quality scores). Use this data to improve team formation. Remove unreliable agents and promote high performers. Continuously fine-tune task-to-agent assignments.
