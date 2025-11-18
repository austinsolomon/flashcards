# LangGraph Agents

## Concept Overview

An agent in LangGraph is an autonomous system that uses an LLM to decide what actions to take, based on the current state and available tools. Unlike a simple prompt-response system, agents use a loop where the LLM observes, decides, and acts iteratively until reaching a goal. This pattern is foundational for building sophisticated AI systems that handle complex, multi-step reasoning.

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

## Best Practices for Agent Mastery

1. **Implement Iteration Limits**: Always set `max_iterations` or message count limits to prevent infinite loops. Use state counters to track agent decisions and force termination when thresholds are exceeded.

2. **Tool Error Handling**: Wrap tool execution in try-catch blocks and return informative error messages that the LLM can learn from, allowing graceful degradation rather than agent failure.

3. **State Management Discipline**: Use clear, immutable state structures with typed fields. Leverage `add_messages` reducer for conversation history to prevent memory bloat while preserving context.

4. **Memory and Learning**: Persist agent decisions and metrics outside the main state loop. Use this to inform future routing decisions and identify performance patterns across multiple agent invocations.

5. **Specialized Agents over Generalists**: For complex systems, route tasks to specialized agents with domain-specific prompts and tools rather than using one LLM for all decisions. This improves accuracy and enables easier debugging.
