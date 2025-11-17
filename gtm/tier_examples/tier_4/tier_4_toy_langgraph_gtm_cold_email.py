#!/usr/bin/env python3
"""
GTM - Tier 4 - Multi-Agent Cold Email Generator (LangGraph)

TIER 4 CHARACTERISTICS:
- Multiple specialized agents coordinating
- ResearchAgent → WriterAgent workflow
- State management between agents
- Agents can request additional data from each other
- LangGraph orchestrates agent communication

What It Does:
Creates personalized cold emails by coordinating two agents:
1. ResearchAgent: Gathers prospect and company information
2. WriterAgent: Crafts personalized email based on research

Tier Contrast:
- Tier 3: Single agent with tools
- Tier 4: Multiple agents with coordination and state sharing
- Tier 5: Claude Code orchestrates agents + human review + send
"""

import os
import sys
from typing import TypedDict, List, Annotated
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

load_dotenv()


# ============================================================================
# TIER 4 CHARACTERISTIC: Shared State Between Agents
# ============================================================================

class EmailGenerationState(TypedDict):
    """
    Shared state that flows between agents

    TIER 4: State management is key - agents build on each other's work
    """
    # Input
    prospect_name: str
    company_name: str
    product_pitch: str

    # ResearchAgent outputs
    research_complete: bool
    company_info: str
    prospect_info: str
    buying_signals: List[str]

    # WriterAgent outputs
    email_draft: str
    subject_line: str

    # Workflow control
    current_agent: str
    messages: List


# ============================================================================
# TIER 4 CHARACTERISTIC: Specialized Agent 1 - ResearchAgent
# ============================================================================

def research_agent(state: EmailGenerationState) -> EmailGenerationState:
    """
    ResearchAgent: Gathers prospect and company information

    TIER 4: Specialized agent focused only on research
    """
    print(f"\n{'='*60}")
    print(f"🔍 RESEARCH AGENT: Gathering information")
    print(f"{'='*60}\n")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Research company (simulated - in production, would call real tools)
    company_research_prompt = f"""
    Research {state['company_name']} and provide:
    1. What they do (industry/product)
    2. Recent news or developments
    3. Company size and stage
    4. Tech stack (if software company)

    Provide concise, factual research.
    """

    company_info = llm.invoke([
        SystemMessage(content="You are a B2B research specialist."),
        HumanMessage(content=company_research_prompt)
    ]).content

    # Research prospect (simulated)
    prospect_research_prompt = f"""
    Research {state['prospect_name']} at {state['company_name']} and provide:
    1. Their likely role/title
    2. What they probably care about (based on role)
    3. Potential pain points they face
    4. Best way to approach them

    Be realistic and professional.
    """

    prospect_info = llm.invoke([
        SystemMessage(content="You are a B2B research specialist."),
        HumanMessage(content=prospect_research_prompt)
    ]).content

    # Identify buying signals
    buying_signals = [
        f"{state['company_name']} is likely scaling their operations",
        "Company may need better workflow automation",
        f"{state['prospect_name']} is likely responsible for tool selection"
    ]

    print(f"✅ Research complete for {state['company_name']}")
    print(f"📊 Company Info: {company_info[:100]}...")
    print(f"👤 Prospect Info: {prospect_info[:100]}...")
    print(f"🎯 Buying Signals: {len(buying_signals)} identified\n")

    # Update state for next agent
    state["research_complete"] = True
    state["company_info"] = company_info
    state["prospect_info"] = prospect_info
    state["buying_signals"] = buying_signals
    state["current_agent"] = "writer"

    return state


# ============================================================================
# TIER 4 CHARACTERISTIC: Specialized Agent 2 - WriterAgent
# ============================================================================

def writer_agent(state: EmailGenerationState) -> EmailGenerationState:
    """
    WriterAgent: Crafts personalized email based on research

    TIER 4: Specialized agent focused only on writing, builds on ResearchAgent's work
    """
    print(f"\n{'='*60}")
    print(f"✍️  WRITER AGENT: Crafting personalized email")
    print(f"{'='*60}\n")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)  # Higher temp for creativity

    # Craft email using research
    writing_prompt = f"""
    Write a personalized cold email to {state['prospect_name']} at {state['company_name']}.

    RESEARCH CONTEXT:
    Company: {state['company_info']}
    Prospect: {state['prospect_info']}
    Buying Signals: {', '.join(state['buying_signals'])}

    PRODUCT PITCH:
    {state['product_pitch']}

    REQUIREMENTS:
    - Personalized subject line (reference their company/situation)
    - Brief opening that shows you researched them
    - Clear value proposition relevant to their pain points
    - Soft call-to-action
    - Professional but conversational tone
    - Keep under 150 words

    Format:
    SUBJECT: [subject line]

    EMAIL:
    [email body]
    """

    email_draft = llm.invoke([
        SystemMessage(content="You are an expert B2B cold email copywriter."),
        HumanMessage(content=writing_prompt)
    ]).content

    # Parse subject and body
    if "SUBJECT:" in email_draft and "EMAIL:" in email_draft:
        parts = email_draft.split("EMAIL:")
        subject_line = parts[0].replace("SUBJECT:", "").strip()
        email_body = parts[1].strip()
    else:
        subject_line = f"Quick question about {state['company_name']}'s workflow"
        email_body = email_draft

    print(f"✅ Email drafted")
    print(f"📧 Subject: {subject_line}")
    print(f"📝 Email length: {len(email_body.split())} words\n")

    # Update state
    state["subject_line"] = subject_line
    state["email_draft"] = email_body
    state["current_agent"] = "complete"

    return state


# ============================================================================
# TIER 4 CHARACTERISTIC: LangGraph Workflow Definition
# ============================================================================

def create_email_generation_workflow():
    """
    Create LangGraph workflow with multi-agent coordination

    TIER 4: Explicit workflow with state passing between agents
    """
    # Create graph
    workflow = StateGraph(EmailGenerationState)

    # Add agents as nodes
    workflow.add_node("research", research_agent)
    workflow.add_node("writer", writer_agent)

    # Define workflow edges
    workflow.set_entry_point("research")
    workflow.add_edge("research", "writer")  # ResearchAgent → WriterAgent
    workflow.add_edge("writer", END)

    # Compile graph
    app = workflow.compile()

    return app


# ============================================================================
# Main Function
# ============================================================================

def generate_cold_email(prospect_name: str, company_name: str, product_pitch: str):
    """
    Generate personalized cold email using multi-agent workflow

    TIER 4 CHARACTERISTIC: Multiple agents coordinate to complete task
    """
    print(f"\n{'='*60}")
    print(f"🎯 TIER 4 MULTI-AGENT: Generating cold email")
    print(f"Target: {prospect_name} at {company_name}")
    print(f"{'='*60}\n")

    # Create workflow
    app = create_email_generation_workflow()

    # Initial state
    initial_state = {
        "prospect_name": prospect_name,
        "company_name": company_name,
        "product_pitch": product_pitch,
        "research_complete": False,
        "company_info": "",
        "prospect_info": "",
        "buying_signals": [],
        "email_draft": "",
        "subject_line": "",
        "current_agent": "research",
        "messages": []
    }

    # Run workflow
    try:
        final_state = app.invoke(initial_state)

        print(f"\n{'='*60}")
        print(f"✅ MULTI-AGENT WORKFLOW COMPLETE")
        print(f"{'='*60}\n")

        # Display results
        print("="*60)
        print("FINAL EMAIL")
        print("="*60)
        print(f"\nSubject: {final_state['subject_line']}\n")
        print(final_state['email_draft'])
        print("\n" + "="*60)

        return {
            "success": True,
            "subject": final_state['subject_line'],
            "email": final_state['email_draft'],
            "research": {
                "company": final_state['company_info'],
                "prospect": final_state['prospect_info'],
                "signals": final_state['buying_signals']
            }
        }

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return {"success": False, "error": str(e)}


# ============================================================================
# Example Usage
# ============================================================================

def main():
    """Example usage of Tier 4 multi-agent system"""

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found")
        sys.exit(1)

    # Example 1: SaaS cold email
    result = generate_cold_email(
        prospect_name="Sarah Chen",
        company_name="Acme Corp",
        product_pitch="We provide an analytics and integration platform that helps SaaS companies "
                      "connect their entire tool stack and gain insights across all systems."
    )

    if result["success"]:
        print("\n✅ Cold email generated successfully")

    # Show tier characteristics
    print("\n" + "="*60)
    print("🎓 WHY THIS IS TIER 4:")
    print("="*60)
    print("""
    1. Multiple Specialized Agents:
       - ResearchAgent: Gathers company/prospect data
       - WriterAgent: Crafts personalized email

    2. Agent Coordination:
       - ResearchAgent output → WriterAgent input
       - State management between agents
       - Sequential workflow orchestration

    3. Separation of Concerns:
       - Research logic separate from writing logic
       - Each agent has single responsibility
       - Can extend with more agents (ReviewAgent, SendAgent, etc.)

    4. LangGraph Orchestration:
       - Explicit workflow definition
       - State passing between nodes
       - Clear agent dependencies

    Contrast with other tiers:
    - Tier 3: Single agent with tools (no coordination)
    - Tier 4: Multiple agents with coordination
    - Tier 5: Claude Code orchestrates agents + human + systems
    - Tier 6: Autonomous learning and improvement
    """)


if __name__ == "__main__":
    main()
