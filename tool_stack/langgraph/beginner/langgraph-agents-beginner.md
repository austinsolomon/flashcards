# LangGraph Agents

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

## Best Practices for Agent Mastery

1. **Implement Iteration Limits**: Always set `max_iterations` or message count limits to prevent infinite loops. Use state counters to track agent decisions and force termination when thresholds are exceeded.

2. **Tool Error Handling**: Wrap tool execution in try-catch blocks and return informative error messages that the LLM can learn from, allowing graceful degradation rather than agent failure.

3. **State Management Discipline**: Use clear, immutable state structures with typed fields. Leverage `add_messages` reducer for conversation history to prevent memory bloat while preserving context.

4. **Memory and Learning**: Persist agent decisions and metrics outside the main state loop. Use this to inform future routing decisions and identify performance patterns across multiple agent invocations.

5. **Specialized Agents over Generalists**: For complex systems, route tasks to specialized agents with domain-specific prompts and tools rather than using one LLM for all decisions. This improves accuracy and enables easier debugging.
