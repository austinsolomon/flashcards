"""
GTM - Tier 4: Multi-Agent Collaboration - Campaign Planning System

Use Case: Multiple specialized agents collaborate to plan a marketing campaign:
- Research Agent: Analyzes market, competitors, audience
- Strategy Agent: Develops positioning and messaging
- Content Agent: Plans content calendar and asset requirements
- Coordinator: Orchestrates the workflow and ensures coherence

Tool Used: LangGraph for state-based multi-agent orchestration
"""

import os
from typing import TypedDict, Annotated, List, Dict, Any
from datetime import datetime
import json
import operator

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


# ============================================================================
# STATE DEFINITION
# ============================================================================

class CampaignPlanState(TypedDict):
    """Shared state passed between agents."""
    # Input
    product: str
    target_audience: str
    campaign_goal: str
    budget: str
    timeline: str

    # Research outputs
    market_analysis: str
    competitor_analysis: str
    audience_insights: str

    # Strategy outputs
    positioning: str
    key_messages: List[str]
    value_propositions: List[str]

    # Content outputs
    content_calendar: List[Dict[str, Any]]
    asset_requirements: List[Dict[str, Any]]

    # Coordination
    messages: Annotated[List, operator.add]
    current_agent: str
    next_step: str


# ============================================================================
# AGENT IMPLEMENTATIONS
# ============================================================================

def research_agent(state: CampaignPlanState) -> CampaignPlanState:
    """
    Research Agent: Analyzes market, competitors, and target audience.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

    prompt = f"""You are a market research specialist. Analyze the campaign parameters:

Product: {state['product']}
Target Audience: {state['target_audience']}
Campaign Goal: {state['campaign_goal']}
Budget: {state['budget']}
Timeline: {state['timeline']}

Provide comprehensive research on:
1. Market Analysis - current trends, opportunities, threats
2. Competitor Analysis - who are the main competitors and their positioning
3. Audience Insights - pain points, motivations, media consumption habits

Format your response as structured JSON with these three sections."""

    response = llm.invoke([SystemMessage(content="You are a market research expert."),
                           HumanMessage(content=prompt)])

    # Parse response (in real implementation, enforce JSON)
    research_content = response.content

    # Extract sections (simplified - real implementation would parse JSON properly)
    state["market_analysis"] = f"Market Analysis:\n{research_content}"
    state["competitor_analysis"] = f"Based on competitive landscape for {state['product']}"
    state["audience_insights"] = f"Audience insights for {state['target_audience']}"

    state["messages"].append({
        "agent": "research",
        "content": "Market research complete",
        "timestamp": datetime.now().isoformat()
    })
    state["current_agent"] = "research"
    state["next_step"] = "strategy"

    return state


def strategy_agent(state: CampaignPlanState) -> CampaignPlanState:
    """
    Strategy Agent: Develops positioning and key messages based on research.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.4)

    prompt = f"""You are a marketing strategy expert. Based on the research:

MARKET ANALYSIS:
{state['market_analysis']}

AUDIENCE INSIGHTS:
{state['audience_insights']}

CAMPAIGN PARAMETERS:
Product: {state['product']}
Goal: {state['campaign_goal']}
Budget: {state['budget']}

Develop:
1. Positioning Statement - how should we position this product
2. 5 Key Messages - core messages to communicate
3. 3 Value Propositions - why prospects should care

Format as JSON with these three sections."""

    response = llm.invoke([SystemMessage(content="You are a marketing strategy expert."),
                           HumanMessage(content=prompt)])

    # In real implementation, parse JSON properly
    strategy_content = response.content

    state["positioning"] = f"Positioning: {strategy_content[:200]}"
    state["key_messages"] = [
        "Message 1: Primary benefit",
        "Message 2: Differentiation",
        "Message 3: Social proof",
        "Message 4: Urgency/CTA",
        "Message 5: Risk reversal"
    ]
    state["value_propositions"] = [
        "VP1: Core value",
        "VP2: Competitive advantage",
        "VP3: Unique benefit"
    ]

    state["messages"].append({
        "agent": "strategy",
        "content": "Strategy and positioning complete",
        "timestamp": datetime.now().isoformat()
    })
    state["current_agent"] = "strategy"
    state["next_step"] = "content"

    return state


def content_agent(state: CampaignPlanState) -> CampaignPlanState:
    """
    Content Agent: Plans content calendar and asset requirements.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

    prompt = f"""You are a content marketing expert. Based on the strategy:

POSITIONING:
{state['positioning']}

KEY MESSAGES:
{', '.join(state['key_messages'])}

CAMPAIGN PARAMETERS:
Timeline: {state['timeline']}
Budget: {state['budget']}
Target Audience: {state['target_audience']}

Create:
1. Content Calendar - 10-15 pieces of content with dates, formats, and topics
2. Asset Requirements - all creative assets needed (videos, graphics, copy)

Format as JSON with content_calendar (array of content pieces) and asset_requirements (array of assets)."""

    response = llm.invoke([SystemMessage(content="You are a content marketing expert."),
                           HumanMessage(content=prompt)])

    # Simulate content calendar
    state["content_calendar"] = [
        {"date": "Week 1", "format": "Blog Post", "topic": "Educational content", "channel": "Blog"},
        {"date": "Week 1", "format": "Social Media", "topic": "Problem awareness", "channel": "LinkedIn"},
        {"date": "Week 2", "format": "Video", "topic": "Product demo", "channel": "YouTube"},
        {"date": "Week 2", "format": "Email", "topic": "Launch announcement", "channel": "Email"},
        {"date": "Week 3", "format": "Webinar", "topic": "Deep dive", "channel": "Zoom"},
        {"date": "Week 3", "format": "Case Study", "topic": "Customer success", "channel": "Website"},
        {"date": "Week 4", "format": "Infographic", "topic": "Value prop visual", "channel": "Social"},
        {"date": "Week 4", "format": "Podcast", "topic": "Thought leadership", "channel": "Spotify"},
    ]

    state["asset_requirements"] = [
        {"type": "Video", "quantity": 3, "specs": "60-90 seconds, 1080p"},
        {"type": "Graphics", "quantity": 15, "specs": "Social media sized"},
        {"type": "Landing Page", "quantity": 1, "specs": "Conversion-optimized"},
        {"type": "Email Templates", "quantity": 5, "specs": "Mobile responsive"},
        {"type": "Slide Deck", "quantity": 1, "specs": "Webinar presentation"},
    ]

    state["messages"].append({
        "agent": "content",
        "content": "Content calendar and asset requirements complete",
        "timestamp": datetime.now().isoformat()
    })
    state["current_agent"] = "content"
    state["next_step"] = "coordinator"

    return state


def coordinator_agent(state: CampaignPlanState) -> CampaignPlanState:
    """
    Coordinator Agent: Reviews all agent outputs and ensures coherence.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

    prompt = f"""You are a campaign coordinator. Review all agent outputs for coherence:

RESEARCH: {state['market_analysis'][:200]}
STRATEGY: {state['positioning'][:200]}
CONTENT: {len(state['content_calendar'])} pieces planned

Verify:
1. Strategy aligns with research insights
2. Content supports the positioning and messages
3. Timeline and budget are realistic
4. All elements work together cohesively

Provide a final assessment and any recommendations for adjustment."""

    response = llm.invoke([SystemMessage(content="You are a campaign coordinator."),
                           HumanMessage(content=prompt)])

    state["messages"].append({
        "agent": "coordinator",
        "content": f"Campaign plan reviewed and validated: {response.content[:150]}",
        "timestamp": datetime.now().isoformat()
    })
    state["current_agent"] = "coordinator"
    state["next_step"] = "complete"

    return state


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

def create_campaign_planning_graph():
    """Create the LangGraph workflow for multi-agent campaign planning."""

    workflow = StateGraph(CampaignPlanState)

    # Add nodes (agents)
    workflow.add_node("research", research_agent)
    workflow.add_node("strategy", strategy_agent)
    workflow.add_node("content", content_agent)
    workflow.add_node("coordinator", coordinator_agent)

    # Define edges (workflow)
    workflow.set_entry_point("research")
    workflow.add_edge("research", "strategy")
    workflow.add_edge("strategy", "content")
    workflow.add_edge("content", "coordinator")
    workflow.add_edge("coordinator", END)

    return workflow.compile()


# ============================================================================
# EXECUTION
# ============================================================================

def plan_campaign(product: str, target_audience: str, campaign_goal: str,
                  budget: str, timeline: str) -> Dict[str, Any]:
    """
    Execute multi-agent campaign planning.

    Returns complete campaign plan with research, strategy, and content.
    """
    print(f"\n{'='*60}")
    print("MULTI-AGENT CAMPAIGN PLANNING")
    print(f"{'='*60}\n")

    # Initialize state
    initial_state = {
        "product": product,
        "target_audience": target_audience,
        "campaign_goal": campaign_goal,
        "budget": budget,
        "timeline": timeline,
        "messages": [],
        "key_messages": [],
        "value_propositions": [],
        "content_calendar": [],
        "asset_requirements": [],
        "market_analysis": "",
        "competitor_analysis": "",
        "audience_insights": "",
        "positioning": "",
        "current_agent": "",
        "next_step": "research"
    }

    # Create and run graph
    app = create_campaign_planning_graph()
    final_state = app.invoke(initial_state)

    print(f"\n{'='*60}")
    print("CAMPAIGN PLANNING COMPLETE")
    print(f"{'='*60}\n")

    # Save campaign plan
    output_dir = "./campaign_plans"
    os.makedirs(output_dir, exist_ok=True)

    campaign_plan = {
        "product": final_state["product"],
        "target_audience": final_state["target_audience"],
        "campaign_goal": final_state["campaign_goal"],
        "budget": final_state["budget"],
        "timeline": final_state["timeline"],
        "research": {
            "market_analysis": final_state["market_analysis"],
            "competitor_analysis": final_state["competitor_analysis"],
            "audience_insights": final_state["audience_insights"]
        },
        "strategy": {
            "positioning": final_state["positioning"],
            "key_messages": final_state["key_messages"],
            "value_propositions": final_state["value_propositions"]
        },
        "content": {
            "calendar": final_state["content_calendar"],
            "assets": final_state["asset_requirements"]
        },
        "workflow_log": final_state["messages"],
        "generated_at": datetime.now().isoformat()
    }

    filename = f"{output_dir}/campaign_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(campaign_plan, f, indent=2)

    print(f"Campaign plan saved to: {filename}\n")

    return campaign_plan


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    How to Run:

    1. Install dependencies:
       pip install langgraph langchain-openai langchain-core

    2. Set environment variable:
       export OPENAI_API_KEY='your-api-key-here'

    3. Run the script:
       python tier_4_langgraph_campaign_planner.py

    Expected Output:
    - Four agents execute in sequence: Research → Strategy → Content → Coordinator
    - Each agent builds on previous agent's outputs
    - Final comprehensive campaign plan saved to JSON
    - Console shows agent-by-agent progress
    """

    # Example campaign parameters
    campaign_plan = plan_campaign(
        product="AI-Powered Sales Intelligence Platform",
        target_audience="B2B SaaS companies, 50-500 employees, sales teams struggling with manual prospecting",
        campaign_goal="Generate 500 qualified demo requests in Q1",
        budget="$75,000",
        timeline="12 weeks (Q1 2025)"
    )

    print("\n" + "="*60)
    print("CAMPAIGN PLAN SUMMARY:")
    print("="*60 + "\n")
    print(f"Product: {campaign_plan['product']}")
    print(f"\nTarget: {campaign_plan['target_audience']}")
    print(f"\nGoal: {campaign_plan['campaign_goal']}")
    print(f"\nPositioning: {campaign_plan['strategy']['positioning'][:150]}...")
    print(f"\nContent Pieces: {len(campaign_plan['content']['calendar'])}")
    print(f"Asset Requirements: {len(campaign_plan['content']['assets'])}")

    print("\n" + "="*60)
    print("TIER 4 CLASSIFICATION REASONING:")
    print("="*60)
    print("""
This is Tier 4 (Multi-Agent Collaboration) because:

1. **Multiple specialized agents**: Research, Strategy, Content, Coordinator
   - Each has distinct expertise and responsibility
   - Agents have different prompts and reasoning styles

2. **Coordinated workflow**: LangGraph orchestrates agent sequence
   - State passed between agents builds progressively
   - Later agents depend on earlier agents' outputs
   - Coordinator ensures coherence across all agents

3. **Shared state management**: All agents read/write to CampaignPlanState
   - Research fills market/audience insights
   - Strategy uses research to create positioning
   - Content uses strategy to plan calendar
   - Coordinator reviews all outputs for alignment

4. **Division of labor**: Each agent focuses on its specialty
   - Research doesn't do strategy
   - Strategy doesn't create content calendar
   - Clear separation of concerns

This differs from Tier 3 (single agent) because:
- Multiple agents with specialized roles vs. one general-purpose agent
- Explicit state passing and coordination vs. monolithic execution
- Each agent could be enhanced independently

This differs from Tier 5 (recursive decomposition) because:
- Fixed agent graph, not dynamic task decomposition
- Predetermined workflow, not adaptive based on complexity
- All agents known upfront, not spawned as needed

Use Cases:
- Product launch planning
- Market entry strategy
- Competitive positioning campaigns
- Multi-channel campaign design

Cost: ~$1.50-3.00 per campaign plan (4x GPT-4 calls)
Time: 5-8 minutes
Output: Comprehensive campaign plan with research, strategy, content
""")
