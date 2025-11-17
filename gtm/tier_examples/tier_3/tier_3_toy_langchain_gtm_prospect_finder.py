#!/usr/bin/env python3
"""
GTM - Tier 3 - Prospect Decision-Maker Finder (LangChain Agent)

TIER 3 CHARACTERISTICS:
- Single agent with tool calling capabilities
- Agent decides which tools to use and in what order
- Uses reasoning to combine information from multiple sources
- Autonomous decision-making within a single task
- No multi-agent coordination (that's Tier 4)

What It Does:
Given a company name, autonomously finds the key decision-maker for sales outreach
by using web search, LinkedIn lookup, and company research tools. The agent
decides which tools to use based on the available information.

Tier Contrast:
- Tier 2: Would use ONE LLM call with no tools
- Tier 3: Agent uses MULTIPLE tools autonomously
- Tier 4: Would have multiple agents coordinating (ResearchAgent → QualificationAgent)
"""

import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv

# LangChain imports
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_core.pydantic_v1 import BaseModel, Field

# Load environment variables
load_dotenv()


# ============================================================================
# TIER 3 CHARACTERISTIC: Tool Definitions
# Agent has multiple tools and decides which to use autonomously
# ============================================================================

def web_search_tool(query: str) -> str:
    """
    TIER 3 TOOL: Web search for company information

    In production, this would call a real search API (Serper, Brave, Google).
    For this toy example, we simulate responses.
    """
    print(f"🔍 [WEB_SEARCH] Searching for: {query}")

    # Simulated responses based on query content
    if "ceo" in query.lower() or "founder" in query.lower():
        return """
        Search Results:
        1. Acme Corp Leadership - Sarah Chen is the CEO and co-founder of Acme Corp
        2. LinkedIn - Sarah Chen - CEO at Acme Corp, Stanford MBA, 15+ years in enterprise SaaS
        3. About Us - Acme Corp was founded in 2018 by Sarah Chen and Michael Rodriguez
        """
    elif "decision maker" in query.lower() or "vp" in query.lower():
        return """
        Search Results:
        1. Acme Corp Announces VP of Sales - James Patterson joins as VP of Sales
        2. Leadership Team - James Patterson oversees all sales and revenue operations
        3. Press Release - Acme Corp names James Patterson as head of go-to-market strategy
        """
    else:
        return f"""
        Search Results for '{query}':
        1. Acme Corp - Enterprise software company specializing in workflow automation
        2. Acme Corp raised $50M Series B led by Sequoia Capital
        3. Acme Corp has 200+ employees across SF, NYC, and Austin
        """


def linkedin_lookup_tool(person_name: str, company_name: str) -> str:
    """
    TIER 3 TOOL: LinkedIn profile lookup

    In production, this would call LinkedIn Sales Navigator API or a scraping service.
    For this toy example, we simulate profile data.
    """
    print(f"👔 [LINKEDIN_LOOKUP] Looking up: {person_name} at {company_name}")

    # Simulated LinkedIn profile data
    profiles = {
        "sarah chen": {
            "name": "Sarah Chen",
            "title": "CEO & Co-Founder",
            "company": "Acme Corp",
            "location": "San Francisco, CA",
            "email_pattern": "sarah.chen@acmecorp.com",
            "bio": "Building the future of workflow automation. Stanford MBA. Former VP at Salesforce.",
            "connections": "5000+",
            "recent_activity": "Posted about Acme's new AI features 2 days ago"
        },
        "james patterson": {
            "name": "James Patterson",
            "title": "VP of Sales",
            "company": "Acme Corp",
            "location": "New York, NY",
            "email_pattern": "james.patterson@acmecorp.com",
            "bio": "Leading sales at Acme Corp. 10+ years in enterprise SaaS sales. Always open to partnerships.",
            "connections": "3500+",
            "recent_activity": "Shared article about B2B sales trends"
        }
    }

    # Lookup by name (case-insensitive)
    name_key = person_name.lower()
    if name_key in profiles:
        profile = profiles[name_key]
        return f"""
        LinkedIn Profile Found:
        Name: {profile['name']}
        Title: {profile['title']}
        Company: {profile['company']}
        Location: {profile['location']}
        Email Pattern: {profile['email_pattern']}
        Bio: {profile['bio']}
        Connections: {profile['connections']}
        Recent Activity: {profile['recent_activity']}
        """
    else:
        return f"No LinkedIn profile found for {person_name} at {company_name}"


def company_info_tool(company_name: str) -> str:
    """
    TIER 3 TOOL: Company information lookup (Clearbit, ZoomInfo, etc.)

    In production, this would call a company data API.
    For this toy example, we simulate company data.
    """
    print(f"🏢 [COMPANY_INFO] Looking up: {company_name}")

    # Simulated company data
    return f"""
    Company Profile: {company_name}

    Industry: Enterprise SaaS - Workflow Automation
    Size: 200-500 employees
    Founded: 2018
    Funding: $75M total (Series B)
    Revenue: $20M ARR (estimated)

    Key Decision Makers:
    - CEO: Sarah Chen (sarah.chen@acmecorp.com)
    - VP Sales: James Patterson (james.patterson@acmecorp.com)
    - VP Engineering: Michael Rodriguez (michael.rodriguez@acmecorp.com)

    Tech Stack: React, Python, AWS, Salesforce, HubSpot
    Recent News: Launched AI-powered workflow builder, expanding to EU market

    Buying Signals:
    - Recently posted job openings for "Integration Engineer"
    - CEO mentioned "looking for better analytics tools" on LinkedIn
    - Attended SaaStr conference last month
    """


# ============================================================================
# TIER 3 CHARACTERISTIC: Tool Setup for Agent
# ============================================================================

# Define tools that the agent can use
tools = [
    Tool(
        name="web_search",
        description="Search the web for information about a company, person, or topic. "
                    "Use this to find general information, news, or public data. "
                    "Input should be a search query string.",
        func=web_search_tool
    ),
    Tool(
        name="linkedin_lookup",
        description="Look up a person's LinkedIn profile given their name and company. "
                    "Returns profile information, title, email pattern, and recent activity. "
                    "Input should be in format: 'person_name, company_name'",
        func=lambda x: linkedin_lookup_tool(*[s.strip() for s in x.split(',')])
    ),
    Tool(
        name="company_info",
        description="Get detailed company information including size, funding, decision makers, "
                    "tech stack, and buying signals. Use this to understand the company before outreach. "
                    "Input should be the company name.",
        func=company_info_tool
    )
]


# ============================================================================
# TIER 3 CHARACTERISTIC: Agent Prompt
# Instructs agent to reason and choose tools autonomously
# ============================================================================

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a sales research agent that finds the best decision-maker to contact at a target company.

Your goal: Given a company name, find the key decision-maker for sales outreach and provide their contact information.

TIER 3 REASONING APPROACH:
1. First, get company overview to understand the business
2. Search for decision-makers (CEO, VP Sales, Head of Operations, etc.)
3. Look up the most relevant person on LinkedIn
4. Synthesize findings into a clear recommendation

You have access to these tools:
- web_search: Find general information about the company and decision-makers
- linkedin_lookup: Get detailed LinkedIn profile data
- company_info: Get company details, tech stack, and buying signals

Think step-by-step and use tools as needed. When you have enough information, provide:
- Name and title of the best person to contact
- Why they're the right decision-maker
- Their likely email address
- Key talking points for outreach

Be thorough but efficient. Don't use more tools than necessary."""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])


# ============================================================================
# TIER 3 CHARACTERISTIC: Agent Creation & Execution
# Single agent with autonomous tool selection
# ============================================================================

def create_prospect_finder_agent():
    """
    Create the LangChain agent with tools

    TIER 3: Single agent that autonomously uses multiple tools
    """
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Create agent
    agent = create_openai_tools_agent(llm, tools, agent_prompt)

    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,  # Show reasoning steps
        max_iterations=10,
        handle_parsing_errors=True
    )

    return agent_executor


def find_decision_maker(company_name: str) -> Dict[str, Any]:
    """
    Main function: Find the best decision-maker at a company

    TIER 3 CHARACTERISTIC: Agent autonomously decides which tools to use
    """
    print(f"\n{'='*60}")
    print(f"🎯 TIER 3 AGENT: Finding decision-maker at {company_name}")
    print(f"{'='*60}\n")

    # Create agent
    agent = create_prospect_finder_agent()

    # Run agent
    try:
        result = agent.invoke({
            "input": f"Find the best decision-maker to contact for a sales outreach at {company_name}. "
                     f"I want to pitch them on our analytics and integration platform."
        })

        print(f"\n{'='*60}")
        print(f"✅ AGENT COMPLETE")
        print(f"{'='*60}\n")

        return {
            "success": True,
            "company": company_name,
            "output": result["output"],
            "tool_calls": "See logs above for tool usage"
        }

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Example Usage & Error Handling
# ============================================================================

def main():
    """
    Example usage of the Tier 3 prospect finder agent
    """
    # Check environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        sys.exit(1)

    # Example 1: Find decision-maker at Acme Corp
    print("\n" + "="*60)
    print("EXAMPLE 1: Find decision-maker at Acme Corp")
    print("="*60)

    result1 = find_decision_maker("Acme Corp")

    if result1["success"]:
        print("\n📋 RESULT:")
        print(result1["output"])

    # Example 2: Another company
    print("\n" + "="*60)
    print("EXAMPLE 2: Find decision-maker at TechStart Inc")
    print("="*60)

    result2 = find_decision_maker("TechStart Inc")

    if result2["success"]:
        print("\n📋 RESULT:")
        print(result2["output"])

    # Show tier characteristics
    print("\n" + "="*60)
    print("🎓 WHY THIS IS TIER 3:")
    print("="*60)
    print("""
    1. Single Agent: One agent handles the entire task
    2. Multiple Tools: Agent has web_search, linkedin_lookup, company_info
    3. Autonomous Decisions: Agent chooses which tools to use and when
    4. Reasoning: Agent combines information from multiple sources
    5. Tool Chaining: Agent may use multiple tools in sequence

    Contrast with other tiers:
    - Tier 2: Would use ONE AI call, no tools
    - Tier 4: Would have multiple agents (ResearchAgent → QualificationAgent → WriterAgent)
    - Tier 5: Would orchestrate human handoff and CRM integration
    - Tier 6: Would autonomously learn and improve over time
    """)


if __name__ == "__main__":
    main()
