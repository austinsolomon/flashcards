# LangGraph Agents

## Concept Overview

An agent in LangGraph is an autonomous system that uses an LLM to decide what actions to take, based on the current state and available tools. Unlike a simple prompt-response system, agents use a loop where the LLM observes, decides, and acts iteratively until reaching a goal. This pattern is foundational for building sophisticated AI systems that handle complex, multi-step reasoning.

---

## Advanced Level: Hierarchical Multi-Agent System with Specialization

An enterprise-grade system with specialized agents for different domains, dynamic routing, and sophisticated state management.

```python
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Annotated, Literal
import operator
from datetime import datetime
import asyncio

class AgentMemory(BaseModel):
    """Persistent memory for agent decision-making."""
    decisions: list[dict]
    performance_metrics: dict
    learned_patterns: list[str]

class HierarchicalAgentState(BaseModel):
    """State for multi-agent system."""
    messages: Annotated[list[BaseMessage], add_messages]
    current_agent: Literal["orchestrator", "analyst", "executor", "validator"]
    agent_memory: dict[str, AgentMemory]
    task_queue: list[dict]
    execution_context: dict
    request_id: str

class SpecializedAgent:
    """Base class for specialized agents."""
    def __init__(self, name: str, domain: str):
        self.name = name
        self.domain = domain
        self.llm = ChatOpenAI(model="gpt-4")
        self.memory = AgentMemory(
            decisions=[],
            performance_metrics={},
            learned_patterns=[]
        )

    async def process(self, state: HierarchicalAgentState) -> dict:
        """Process task with domain-specific logic."""
        raise NotImplementedError

class AnalystAgent(SpecializedAgent):
    """Analyzes requirements and data."""
    async def process(self, state: HierarchicalAgentState) -> dict:
        # Complex analysis logic
        analysis = await self.llm.ainvoke(state.messages)
        self.memory.decisions.append({
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis.content,
            "request_id": state.request_id
        })
        return {
            "messages": [analysis],
            "current_agent": "executor"
        }

class ExecutorAgent(SpecializedAgent):
    """Executes planned tasks."""
    async def process(self, state: HierarchicalAgentState) -> dict:
        # Complex execution logic with error handling
        task = state.task_queue[0] if state.task_queue else {}
        execution_result = await self.llm.ainvoke(
            state.messages + [HumanMessage(content=f"Execute: {task}")]
        )
        return {
            "messages": [execution_result],
            "current_agent": "validator",
            "task_queue": state.task_queue[1:]
        }

class ValidatorAgent(SpecializedAgent):
    """Validates results and ensures quality."""
    async def process(self, state: HierarchicalAgentState) -> dict:
        validation = await self.llm.ainvoke(
            state.messages + [HumanMessage(content="Validate the previous execution")]
        )
        return {
            "messages": [validation],
            "current_agent": "orchestrator"
        }

class OrchestratorAgent(SpecializedAgent):
    """Routes between specialized agents."""
    async def process(self, state: HierarchicalAgentState) -> dict:
        decision = await self.llm.ainvoke(state.messages)

        # Intelligent routing based on response
        if "analyze" in decision.content.lower():
            next_agent = "analyst"
        elif "execute" in decision.content.lower():
            next_agent = "executor"
        elif "validate" in decision.content.lower():
            next_agent = "validator"
        else:
            next_agent = "analyst"  # default

        return {
            "messages": [decision],
            "current_agent": next_agent
        }

def create_hierarchical_agent_system():
    """Create a hierarchical multi-agent system."""
    agents = {
        "orchestrator": OrchestratorAgent("orchestrator", "routing"),
        "analyst": AnalystAgent("analyst", "analysis"),
        "executor": ExecutorAgent("executor", "execution"),
        "validator": ValidatorAgent("validator", "validation")
    }

    async def route_to_agent(state: HierarchicalAgentState):
        """Route to the appropriate agent."""
        agent = agents.get(state.current_agent)
        if agent:
            return await agent.process(state)
        return {"current_agent": "orchestrator"}

    def should_continue(state: HierarchicalAgentState) -> str:
        """Determine if multi-agent loop should continue."""
        last_message = state.messages[-1]

        # Check for completion signals
        if isinstance(last_message, AIMessage):
            content = last_message.content.lower()
            if any(word in content for word in ["complete", "done", "finished"]):
                return "end"

        # Prevent infinite loops
        if len(state.messages) > 20:
            return "end"

        return "continue"

    # Build hierarchical workflow
    workflow = StateGraph(HierarchicalAgentState)

    for agent_name in ["orchestrator", "analyst", "executor", "validator"]:
        workflow.add_node(agent_name, route_to_agent)

    workflow.add_edge(START, "orchestrator")

    workflow.add_conditional_edges(
        "orchestrator",
        lambda state: state.current_agent,
        {
            "analyst": "analyst",
            "executor": "executor",
            "validator": "validator",
            "orchestrator": "orchestrator"
        }
    )

    for agent in ["analyst", "executor", "validator"]:
        workflow.add_edge(agent, "orchestrator")

    workflow.add_conditional_edges(
        "orchestrator",
        should_continue,
        {"continue": "orchestrator", "end": END}
    )

    return workflow.compile()

# Usage
async def main():
    system = create_hierarchical_agent_system()
    initial_state = HierarchicalAgentState(
        messages=[HumanMessage(content="Analyze market trends and provide recommendations")],
        current_agent="orchestrator",
        agent_memory={name: AgentMemory(decisions=[], performance_metrics={}, learned_patterns=[])
                     for name in ["orchestrator", "analyst", "executor", "validator"]},
        task_queue=[],
        execution_context={"market": "tech", "timeframe": "Q4 2024"},
        request_id="req_001"
    )

    result = await asyncio.to_thread(system.invoke, initial_state)
    return result

# Run: asyncio.run(main())
```

---

## Best Practices for Agent Mastery

1. **Implement Iteration Limits**: Always set `max_iterations` or message count limits to prevent infinite loops. Use state counters to track agent decisions and force termination when thresholds are exceeded.

2. **Tool Error Handling**: Wrap tool execution in try-catch blocks and return informative error messages that the LLM can learn from, allowing graceful degradation rather than agent failure.

3. **State Management Discipline**: Use clear, immutable state structures with typed fields. Leverage `add_messages` reducer for conversation history to prevent memory bloat while preserving context.

4. **Memory and Learning**: Persist agent decisions and metrics outside the main state loop. Use this to inform future routing decisions and identify performance patterns across multiple agent invocations.

5. **Specialized Agents over Generalists**: For complex systems, route tasks to specialized agents with domain-specific prompts and tools rather than using one LLM for all decisions. This improves accuracy and enables easier debugging.
