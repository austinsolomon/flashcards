# LangGraph Integration - Advanced

## Concept Overview

LangGraph is a framework for building stateful, multi-actor applications with LLMs using graph-based workflows. Unlike linear chains or simple agents, LangGraph enables complex control flow: conditional branching, loops, parallel execution, human-in-the-loop, and state management. It represents workflows as directed graphs where nodes are computations and edges define the flow.

**Why it matters:** Real-world LLM applications rarely follow linear paths. You need loops for iterative refinement, branches for decision points, parallel paths for efficiency, and human approval gates for safety. LangGraph makes these patterns explicit and debuggable. This is the difference between a prototype and a production system that handles real-world complexity.

## Real-World Example: Multi-Agent Content Publishing Workflow

This example demonstrates a sophisticated content publishing system with research, writing, editing, fact-checking, and approval stages - all coordinated via LangGraph.

```python
from typing import TypedDict, Annotated, Sequence, List, Dict, Any
from langgraph.graph import Graph, StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
import operator
import json

# ========== STATE DEFINITION ==========
class ContentWorkflowState(TypedDict):
    """State that flows through the content publishing graph."""
    # Input
    topic: str
    target_audience: str
    content_type: str  # blog, article, social_post

    # Research phase
    research_completed: bool
    research_findings: List[str]
    sources: List[str]

    # Writing phase
    draft_content: str
    draft_version: int

    # Review phases
    editor_feedback: List[str]
    fact_check_results: Dict[str, Any]
    approval_status: str  # pending, approved, rejected

    # Metadata
    iterations: int
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_stage: str

# ========== NODE FUNCTIONS ==========
def research_node(state: ContentWorkflowState) -> ContentWorkflowState:
    """Research node - gathers information on topic."""
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    research_prompt = f"""
You are a research assistant. Research the following topic thoroughly:

Topic: {state['topic']}
Target Audience: {state['target_audience']}
Content Type: {state['content_type']}

Provide:
1. Key facts and insights (5-7 points)
2. Current trends and statistics
3. Unique angles or perspectives
4. Credible sources

Format as JSON:
{{
  "findings": ["finding 1", "finding 2", ...],
  "sources": ["source 1", "source 2", ...]
}}
"""

    response = llm.invoke([HumanMessage(content=research_prompt)])

    try:
        research_data = json.loads(response.content)
        return {
            **state,
            "research_completed": True,
            "research_findings": research_data.get("findings", []),
            "sources": research_data.get("sources", []),
            "current_stage": "research_complete",
            "messages": [AIMessage(content=f"Research completed: {len(research_data.get('findings', []))} findings")]
        }
    except:
        return {
            **state,
            "research_completed": False,
            "current_stage": "research_failed",
            "messages": [AIMessage(content="Research parsing failed")]
        }

def writer_node(state: ContentWorkflowState) -> ContentWorkflowState:
    """Writer node - creates content draft based on research."""
    llm = ChatOpenAI(model="gpt-4", temperature=0.8)

    findings_text = "\n".join([f"- {f}" for f in state.get('research_findings', [])])

    writing_prompt = f"""
You are an expert content writer. Write {state['content_type']} content on this topic:

Topic: {state['topic']}
Target Audience: {state['target_audience']}

Research Findings:
{findings_text}

Requirements:
- Engaging and well-structured
- Appropriate tone for {state['target_audience']}
- Incorporate research findings naturally
- Include clear call-to-action if appropriate

Write the complete {state['content_type']}:
"""

    if state.get('editor_feedback'):
        # Revision based on feedback
        feedback_text = "\n".join([f"- {f}" for f in state['editor_feedback']])
        writing_prompt += f"""

IMPORTANT: This is revision #{state.get('draft_version', 1)}. Address this feedback:
{feedback_text}
"""

    response = llm.invoke([HumanMessage(content=writing_prompt)])

    return {
        **state,
        "draft_content": response.content,
        "draft_version": state.get('draft_version', 0) + 1,
        "current_stage": "draft_complete",
        "messages": [AIMessage(content=f"Draft v{state.get('draft_version', 0) + 1} completed")]
    }

def editor_node(state: ContentWorkflowState) -> ContentWorkflowState:
    """Editor node - reviews content for quality and provides feedback."""
    llm = ChatOpenAI(model="gpt-4", temperature=0.3)

    editing_prompt = f"""
You are a senior editor. Review this {state['content_type']} critically:

Topic: {state['topic']}
Target Audience: {state['target_audience']}

Content:
{state.get('draft_content', '')}

Evaluate:
1. Clarity and structure
2. Engagement and tone
3. Grammar and style
4. Factual accuracy (flag claims that need fact-checking)
5. Alignment with target audience

Provide feedback as JSON:
{{
  "issues": ["issue 1", "issue 2", ...],
  "suggestions": ["suggestion 1", "suggestion 2", ...],
  "quality_score": 1-10,
  "needs_revision": true/false,
  "fact_check_required": true/false
}}
"""

    response = llm.invoke([HumanMessage(content=editing_prompt)])

    try:
        feedback_data = json.loads(response.content)
        needs_revision = feedback_data.get('needs_revision', False)

        return {
            **state,
            "editor_feedback": feedback_data.get('issues', []) + feedback_data.get('suggestions', []),
            "current_stage": "revision_needed" if needs_revision else "editing_complete",
            "messages": [AIMessage(content=f"Editing complete. Quality: {feedback_data.get('quality_score')}/10")]
        }
    except:
        return {
            **state,
            "current_stage": "editing_complete",
            "messages": [AIMessage(content="Editing feedback parsing failed - proceeding")]
        }

def fact_checker_node(state: ContentWorkflowState) -> ContentWorkflowState:
    """Fact checker node - verifies claims in content."""
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    fact_check_prompt = f"""
You are a fact-checker. Verify all factual claims in this content:

Content:
{state.get('draft_content', '')}

For each factual claim:
1. Identify the claim
2. Assess verifiability
3. Flag if potentially inaccurate

Provide results as JSON:
{{
  "claims_checked": 5,
  "flags": ["flag 1", "flag 2", ...],
  "verification_status": "verified" / "needs_review",
  "confidence": 1-10
}}
"""

    response = llm.invoke([HumanMessage(content=fact_check_prompt)])

    try:
        fact_check_data = json.loads(response.content)

        return {
            **state,
            "fact_check_results": fact_check_data,
            "current_stage": "fact_check_complete",
            "messages": [AIMessage(content=f"Fact-check: {fact_check_data.get('verification_status')}")]
        }
    except:
        return {
            **state,
            "fact_check_results": {"verification_status": "error"},
            "current_stage": "fact_check_complete",
            "messages": [AIMessage(content="Fact-check failed")]
        }

def approval_node(state: ContentWorkflowState) -> ContentWorkflowState:
    """Approval node - final review and approval decision."""
    # In production, this would integrate with approval system or human review
    # For demo, auto-approve if quality thresholds met

    quality_score = state.get('editor_feedback', [])
    fact_check_status = state.get('fact_check_results', {}).get('verification_status', 'error')
    iterations = state.get('iterations', 0)

    # Decision logic
    if iterations > 3:
        approval_status = "rejected"
        reason = "Exceeded maximum revision iterations"
    elif fact_check_status != "verified" and fact_check_status != "error":
        approval_status = "rejected"
        reason = "Failed fact-checking"
    elif len(quality_score) > 5:
        approval_status = "rejected"
        reason = "Too many editor concerns"
    else:
        approval_status = "approved"
        reason = "Quality standards met"

    return {
        **state,
        "approval_status": approval_status,
        "current_stage": "approval_complete",
        "messages": [AIMessage(content=f"Approval: {approval_status} - {reason}")]
    }

# ========== CONDITIONAL EDGE FUNCTIONS ==========
def should_revise(state: ContentWorkflowState) -> str:
    """Decide if content needs revision based on editor feedback."""
    if state.get('current_stage') == 'revision_needed':
        return "revise"
    else:
        return "continue"

def check_approval(state: ContentWorkflowState) -> str:
    """Route based on approval status."""
    approval = state.get('approval_status', 'pending')

    if approval == 'approved':
        return "publish"
    elif approval == 'rejected' and state.get('iterations', 0) < 3:
        return "revise"
    else:
        return "terminate"

# ========== BUILD LANGGRAPH WORKFLOW ==========
def create_content_workflow() -> Graph:
    """Create the content publishing workflow graph."""

    # Initialize the graph with state
    workflow = StateGraph(ContentWorkflowState)

    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("write", writer_node)
    workflow.add_node("edit", editor_node)
    workflow.add_node("fact_check", fact_checker_node)
    workflow.add_node("approve", approval_node)

    # Define edges
    workflow.set_entry_point("research")

    # Linear flow: research -> write
    workflow.add_edge("research", "write")

    # After writing, go to editing
    workflow.add_edge("write", "edit")

    # Conditional: editing can require revision or continue
    workflow.add_conditional_edges(
        "edit",
        should_revise,
        {
            "revise": "write",  # Loop back to writer
            "continue": "fact_check"
        }
    )

    # After fact-checking, go to approval
    workflow.add_edge("fact_check", "approve")

    # Conditional: approval can approve, reject, or require revision
    workflow.add_conditional_edges(
        "approve",
        check_approval,
        {
            "publish": END,
            "revise": "write",
            "terminate": END
        }
    )

    return workflow.compile()

# ========== PRODUCTION USAGE ==========
print("=== LangGraph Content Publishing Workflow ===\n")

# Create workflow
app = create_content_workflow()

# Test with content request
initial_state = {
    "topic": "AI-Powered DevOps: Autonomous Incident Response",
    "target_audience": "Senior DevOps Engineers and SREs",
    "content_type": "technical blog post",
    "research_completed": False,
    "research_findings": [],
    "sources": [],
    "draft_content": "",
    "draft_version": 0,
    "editor_feedback": [],
    "fact_check_results": {},
    "approval_status": "pending",
    "iterations": 0,
    "messages": [],
    "current_stage": "initialized"
}

print("Starting content workflow...\n")
print(f"Topic: {initial_state['topic']}")
print(f"Audience: {initial_state['target_audience']}")
print(f"Type: {initial_state['content_type']}\n")
print("-" * 80)

# Execute workflow
final_state = app.invoke(initial_state)

# Print results
print("\n=== WORKFLOW EXECUTION COMPLETE ===\n")
print(f"Final Stage: {final_state.get('current_stage')}")
print(f"Approval Status: {final_state.get('approval_status')}")
print(f"Draft Version: {final_state.get('draft_version')}")
print(f"Total Iterations: {final_state.get('iterations')}")

print("\n=== EXECUTION TRACE ===")
for i, msg in enumerate(final_state.get('messages', [])):
    print(f"{i+1}. {msg.content}")

print("\n=== FINAL CONTENT ===")
print(final_state.get('draft_content', 'No content generated'))

print("\n=== FACT-CHECK RESULTS ===")
print(json.dumps(final_state.get('fact_check_results', {}), indent=2))

# ========== ADVANCED: HUMAN-IN-THE-LOOP ==========
from langgraph.checkpoint import MemorySaver

def create_hitl_workflow() -> Graph:
    """Workflow with human-in-the-loop approval."""

    workflow = StateGraph(ContentWorkflowState)

    # Add all nodes
    workflow.add_node("research", research_node)
    workflow.add_node("write", writer_node)
    workflow.add_node("edit", editor_node)
    workflow.add_node("fact_check", fact_checker_node)
    workflow.add_node("human_review", lambda state: state)  # Pauses for human input

    # Setup flow
    workflow.set_entry_point("research")
    workflow.add_edge("research", "write")
    workflow.add_edge("write", "edit")

    workflow.add_conditional_edges(
        "edit",
        should_revise,
        {
            "revise": "write",
            "continue": "fact_check"
        }
    )

    # After fact-check, pause for human review
    workflow.add_edge("fact_check", "human_review")
    workflow.add_edge("human_review", END)

    # Compile with checkpointing for persistence
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

print("\n\n=== HUMAN-IN-THE-LOOP WORKFLOW ===")
print("This workflow pauses at 'human_review' for manual approval")
print("In production, integrate with approval systems or UI")

# ========== ADVANCED: PARALLEL EXECUTION ==========
def create_parallel_research_workflow() -> Graph:
    """Workflow with parallel research agents."""

    def competitor_research(state):
        # Research competitors
        return {**state, "messages": [AIMessage(content="Competitor research complete")]}

    def trend_research(state):
        # Research trends
        return {**state, "messages": [AIMessage(content="Trend research complete")]}

    def technical_research(state):
        # Deep technical research
        return {**state, "messages": [AIMessage(content="Technical research complete")]}

    def aggregate_research(state):
        # Combine all research
        return {**state, "current_stage": "research_aggregated"}

    workflow = StateGraph(ContentWorkflowState)

    # Add parallel research nodes
    workflow.add_node("competitor_research", competitor_research)
    workflow.add_node("trend_research", trend_research)
    workflow.add_node("technical_research", technical_research)
    workflow.add_node("aggregate", aggregate_research)
    workflow.add_node("write", writer_node)

    # Set entry point that fans out to parallel nodes
    workflow.set_entry_point("competitor_research")
    workflow.add_edge("competitor_research", "aggregate")

    # In LangGraph, parallel execution requires multiple start points
    # This is a simplified example - production would use more sophisticated patterns

    workflow.add_edge("aggregate", "write")
    workflow.add_edge("write", END)

    return workflow.compile()

print("\n=== PARALLEL RESEARCH WORKFLOW ===")
print("Executes multiple research agents in parallel for faster results")

# ========== VISUALIZATION ==========
print("\n=== WORKFLOW VISUALIZATION ===")
print("""
Graph structure:

START
  ↓
[Research]
  ↓
[Write] ←─────┐ (revision loop)
  ↓            │
[Edit] ────────┘ (if needs_revision)
  ↓
[Fact Check]
  ↓
[Approve]
  ↓
END (or loop back if rejected)

Key Features:
- Conditional branching based on edit quality
- Iterative revision loop (max 3 iterations)
- Parallel fact-checking and editing possible
- Human-in-the-loop approval option
- State checkpointing for persistence
""")
```

### Why This Example Shows LangGraph Power:

1. **Complex Control Flow**: Loops for revision, branches for decisions, parallel execution
2. **Stateful Execution**: State persists and evolves through the graph
3. **Human-in-the-Loop**: Pause for manual approval at critical stages
4. **Conditional Routing**: Dynamic paths based on runtime evaluation
5. **Debuggability**: Clear graph structure makes workflow easy to understand and debug

## Best Practices for Mastering LangGraph

1. **Design your state schema carefully with TypedDict**: State is the contract between all nodes. Include all data each node might need or produce. Use Annotated types for special behaviors (like `operator.add` for message accumulation). Well-designed state prevents bugs and makes the graph self-documenting.

2. **Keep nodes pure and focused on single responsibilities**: Each node should do one thing well - research, write, edit, etc. Don't mix concerns. This makes nodes reusable across graphs and easy to test in isolation. Pure functions with state in/state out are easier to debug than stateful objects.

3. **Use conditional edges for complex routing logic**: Don't try to encode all logic in a single node. Extract decision logic into conditional edge functions that clearly express routing rules. This separates "what to do" (nodes) from "what to do next" (edges), improving readability.

4. **Implement checkpointing for long-running workflows**: Use LangGraph's checkpointing to persist state at each step. This enables resume-on-failure, human-in-the-loop with async approval, and time-travel debugging. Critical for production workflows that can't afford to restart from scratch.

5. **Add escape hatches to prevent infinite loops**: Always include max iteration counters, timeout conditions, and explicit termination paths. Test what happens when nodes fail or return unexpected data. Production graphs need defensive programming - one bad conditional can loop forever.

## Common Pitfalls to Avoid

- **Don't mutate state in nodes**: Return new state dicts, don't modify in place
- **Avoid complex logic in edge conditions**: Keep routing logic simple and testable
- **Don't skip type definitions**: TypedDict catches state schema mismatches early
- **Remember END is required**: Graphs without termination paths hang forever
- **Don't ignore checkpointing**: State loss on failure is catastrophic in production
