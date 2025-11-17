# LangGraph Agents: Beginner to Advanced

## Concept Overview

An agent in LangGraph is an autonomous system that uses an LLM to decide what actions to take, based on the current state and available tools. Unlike a simple prompt-response system, agents use a loop where the LLM observes, decides, and acts iteratively until reaching a goal. This pattern is foundational for building sophisticated AI systems that handle complex, multi-step reasoning.

---

## Beginner Level: Basic Agent Loop

A simple agent that responds to user queries and uses a calculator tool.

```python
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import Annotated
import operator

# Define the state
class AgentState(BaseModel):
    messages: Annotated[list[BaseMessage], operator.add]

# Define a simple calculator tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

tools = [add, multiply]

# Create the agent
def create_basic_agent():
    llm = ChatOpenAI(model="gpt-4")

    def should_continue(state: AgentState) -> str:
        messages = state.messages
        last_message = messages[-1]
        # If model called a tool, continue; otherwise end
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "continue"
        return "end"

    def call_model(state: AgentState):
        messages = state.messages
        response = llm.invoke(messages)
        return {"messages": [response]}

    def execute_tool(state: AgentState, name: str, arguments: dict):
        if name == "add":
            result = add(**arguments)
        elif name == "multiply":
            result = multiply(**arguments)
        return result

    # Build graph
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("action", execute_tool)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {"continue": "action", "end": END}
    )
    workflow.add_edge("action", "agent")

    return workflow.compile()

# Usage
agent = create_basic_agent()
result = agent.invoke({"messages": [HumanMessage(content="What is 5 + 3?")]})
```

---

## Intermediate Level: Multi-Tool Research Agent

A more sophisticated agent that researches topics using multiple tools with error handling and context management.

```python
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import Annotated
import operator
import json
from datetime import datetime

class ResearchAgentState(BaseModel):
    messages: Annotated[list[BaseMessage], operator.add]
    research_topic: str
    findings: list[str]
    max_iterations: int
    iteration_count: int

# Simulated tools for research
def search_academic_papers(query: str, limit: int = 5) -> dict:
    """Search academic papers (simulated)."""
    return {
        "papers": [
            {"title": f"Study on {query}", "year": 2023, "citations": 150},
            {"title": f"Advanced {query} techniques", "year": 2024, "citations": 42}
        ],
        "search_time": datetime.now().isoformat()
    }

def fetch_recent_news(topic: str) -> list:
    """Fetch recent news articles (simulated)."""
    return [
        {"headline": f"Breaking: New discovery in {topic}", "date": "2024-11-15"},
        {"headline": f"Industry update on {topic}", "date": "2024-11-14"}
    ]

def synthesize_findings(papers: list, news: list) -> str:
    """Synthesize research findings."""
    return f"Synthesized {len(papers)} papers and {len(news)} news items for comprehensive overview"

# Tool registry
TOOLS = {
    "search_papers": search_academic_papers,
    "fetch_news": fetch_recent_news,
    "synthesize": synthesize_findings
}

def create_research_agent():
    llm = ChatOpenAI(model="gpt-4")

    def should_continue(state: ResearchAgentState) -> str:
        """Determine if agent should continue or stop."""
        if state.iteration_count >= state.max_iterations:
            return "end"

        last_message = state.messages[-1]
        if isinstance(last_message, AIMessage) and not hasattr(last_message, 'tool_calls'):
            return "end"

        return "continue"

    def call_research_model(state: ResearchAgentState):
        """Call the model with conversation history and findings."""
        response = llm.invoke(state.messages)
        return {
            "messages": [response],
            "iteration_count": state.iteration_count + 1
        }

    def execute_research_tool(state: ResearchAgentState, tool_name: str, tool_input: dict):
        """Execute research tools and return results."""
        if tool_name not in TOOLS:
            return {
                "messages": [ToolMessage(
                    content=f"Tool {tool_name} not found",
                    tool_call_id="error"
                )]
            }

        try:
            result = TOOLS[tool_name](**tool_input)
            state.findings.append(json.dumps(result))

            return {
                "messages": [ToolMessage(
                    content=json.dumps(result),
                    tool_call_id="research_tool"
                )],
                "findings": state.findings
            }
        except Exception as e:
            return {
                "messages": [ToolMessage(
                    content=f"Error executing {tool_name}: {str(e)}",
                    tool_call_id="error"
                )]
            }

    # Build graph
    workflow = StateGraph(ResearchAgentState)
    workflow.add_node("researcher", call_research_model)
    workflow.add_node("tool_executor", execute_research_tool)

    workflow.add_edge(START, "researcher")
    workflow.add_conditional_edges(
        "researcher",
        should_continue,
        {"continue": "tool_executor", "end": END}
    )
    workflow.add_edge("tool_executor", "researcher")

    return workflow.compile()

# Usage
agent = create_research_agent()
initial_state = ResearchAgentState(
    messages=[HumanMessage(content="Research the latest advances in quantum computing")],
    research_topic="quantum computing",
    findings=[],
    max_iterations=5,
    iteration_count=0
)
result = agent.invoke(initial_state)
print(f"Research findings: {result.findings}")
```

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
