#!/usr/bin/env python3
"""
GTM - Tier 3 - ICP-Based Account Hunter Agent (LangChain)

TIER 3 CHARACTERISTICS:
- Single agent with company search/enrichment tools
- Autonomous decision-making for ICP fit scoring
- Multi-criteria evaluation (firmographics + technographics)
- Structured output for downstream workflows

What It Does:
Given an Ideal Customer Profile (ICP), autonomously searches for companies
that match criteria, enriches with firmographic/technographic data, and
scores each prospect for sales outreach prioritization.
"""

import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool

load_dotenv()

# ============================================================================
# TIER 3 TOOLS: Company Discovery & Enrichment
# ============================================================================

def company_search_tool(criteria: str) -> str:
    """
    Search for companies matching ICP criteria

    Production: Integrate with:
    - Apollo.io Search API
    - ZoomInfo Company Search
    - LinkedIn Sales Navigator
    - Crunchbase API
    """
    # Simulated search results
    results = [
        {
            "company_name": "DataFlow Systems",
            "domain": "dataflowsystems.com",
            "industry": "Analytics SaaS",
            "employee_count": 350,
            "location": "San Francisco, CA",
            "founded": 2017
        },
        {
            "company_name": "CloudScale Inc",
            "domain": "cloudscale.io",
            "industry": "Infrastructure SaaS",
            "employee_count": 280,
            "location": "Austin, TX",
            "founded": 2019
        },
        {
            "company_name": "WorkflowPro",
            "domain": "workflowpro.com",
            "industry": "Workflow Automation",
            "employee_count": 420,
            "location": "New York, NY",
            "founded": 2016
        }
    ]

    return json.dumps(results)


def company_enrichment_tool(company_domain: str) -> str:
    """
    Enrich company with detailed firmographic/technographic data

    Production: Clearbit, ZoomInfo, BuiltWith
    """
    # Simulated enrichment data
    enrichment = {
        "company_name": company_domain.split('.')[0].title(),
        "employees": 350,
        "revenue_range": "$20M-$50M",
        "funding": {
            "total": "$45M",
            "stage": "Series B",
            "investors": ["Sequoia", "Accel"]
        },
        "tech_stack": [
            "Salesforce", "HubSpot", "AWS", "Python", "React",
            "Slack", "Zoom", "Notion"
        ],
        "growth_signals": {
            "headcount_growth_6mo": "+15%",
            "job_postings": 12,
            "recent_funding": True
        },
        "decision_makers": {
            "cto": "John Smith",
            "vp_engineering": "Sarah Johnson",
            "head_of_operations": "Mike Chen"
        }
    }

    return json.dumps(enrichment)


def technographic_analyzer(tech_stack: str) -> str:
    """
    Analyze tech stack for integration opportunities and fit

    Identifies:
    - Existing tools we integrate with
    - Gaps in their stack we fill
    - Competitor usage
    """
    try:
        stack = json.loads(tech_stack)

        analysis = {
            "integration_opportunities": [],
            "stack_gaps": [],
            "competitor_tools": [],
            "fit_score": 0
        }

        # Check for integration opportunities
        integrations = ["Salesforce", "HubSpot", "Slack", "AWS"]
        for tool in integrations:
            if tool in stack:
                analysis["integration_opportunities"].append(tool)
                analysis["fit_score"] += 20

        # Check for competitors
        competitors = ["Zapier", "Make", "Workato"]
        for comp in competitors:
            if comp in stack:
                analysis["competitor_tools"].append(comp)
                analysis["fit_score"] += 15  # Can position as upgrade

        # Identify gaps
        if "Salesforce" in stack and "HubSpot" in stack:
            analysis["stack_gaps"].append("No unified data integration platform")
            analysis["fit_score"] += 25

        return json.dumps(analysis)

    except Exception as e:
        return json.dumps({"error": str(e), "fit_score": 0})


def icp_fit_scorer(company_data: str, icp_criteria: str) -> str:
    """
    Score company against ICP criteria

    Returns: Comprehensive fit score with reasoning
    """
    try:
        company = json.loads(company_data)
        criteria = json.loads(icp_criteria)

        score = 0
        max_score = 100
        fit_reasons = []

        # Employee count fit
        emp_range = criteria.get("employee_range", [100, 1000])
        if emp_range[0] <= company.get("employees", 0) <= emp_range[1]:
            score += 20
            fit_reasons.append(f"Employee count ({company['employees']}) within target range")
        else:
            fit_reasons.append(f"Employee count ({company['employees']}) outside target range")

        # Revenue fit
        if criteria.get("revenue_min") and company.get("revenue_range"):
            score += 15
            fit_reasons.append("Revenue range matches ICP")

        # Industry fit
        target_industries = criteria.get("industries", [])
        if any(ind.lower() in str(company.get("industry", "")).lower() for ind in target_industries):
            score += 25
            fit_reasons.append(f"Industry match: {company.get('industry')}")

        # Tech stack fit (from analysis)
        tech_score = company.get("tech_fit_score", 0)
        score += min(tech_score, 40)
        if tech_score > 30:
            fit_reasons.append("Strong tech stack alignment")

        return json.dumps({
            "fit_score": score,
            "fit_level": "high" if score > 70 else ("medium" if score > 50 else "low"),
            "fit_reasons": fit_reasons,
            "recommended_action": "reach_out" if score > 60 else "nurture"
        })

    except Exception as e:
        return json.dumps({"error": str(e), "fit_score": 0})


# ============================================================================
# TIER 3 AGENT
# ============================================================================

tools = [
    Tool(
        name="company_search",
        description="Search for companies matching ICP criteria. Input: search criteria string (e.g., 'SaaS companies 200-500 employees')",
        func=company_search_tool
    ),
    Tool(
        name="company_enrichment",
        description="Enrich company with firmographic/technographic data. Input: company domain",
        func=company_enrichment_tool
    ),
    Tool(
        name="technographic_analyzer",
        description="Analyze tech stack for fit and opportunities. Input: JSON array of tech tools",
        func=technographic_analyzer
    ),
    Tool(
        name="icp_fit_scorer",
        description="Score company against ICP. Input: 'company_data_json | icp_criteria_json'",
        func=lambda x: icp_fit_scorer(*[s.strip() for s in x.split('|')])
    )
]

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an ICP-based account hunting specialist for B2B sales.

Your job: Find companies that match the Ideal Customer Profile and score them for outreach priority.

PROCESS:
1. Search for companies matching ICP criteria
2. Enrich each company with detailed data
3. Analyze tech stack for fit and opportunities
4. Score against ICP criteria
5. Provide prioritized list with reasoning

Focus on finding the BEST fit companies, not just volume."""),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])


def create_icp_hunter_agent():
    """Create ICP account hunting agent"""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    agent = create_openai_tools_agent(llm, tools, agent_prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=12)


def hunt_icp_accounts(icp_definition: Dict) -> List[Dict]:
    """
    Main function: Hunt for accounts matching ICP

    Args:
        icp_definition: {
            "industries": ["SaaS", "FinTech"],
            "employee_range": [200, 1000],
            "revenue_min": "$10M",
            "tech_requirements": ["Salesforce", "AWS"],
            "geography": ["US", "Canada"]
        }

    Returns:
        List of scored companies with fit reasoning
    """
    agent = create_icp_hunter_agent()

    query = f"""Find companies matching this ICP:
{json.dumps(icp_definition, indent=2)}

Search, enrich, analyze tech fit, and score each company. Return top 5 best fits."""

    result = agent.invoke({"input": query})

    # Production: Parse structured output
    return {
        "icp_hunt_complete": True,
        "accounts_found": 5,
        "agent_output": result["output"]
    }


# Example usage
if __name__ == "__main__":
    icp = {
        "industries": ["SaaS", "Analytics", "Workflow Automation"],
        "employee_range": [200, 1000],
        "revenue_range": "$10M-$100M",
        "tech_requirements": ["Salesforce OR HubSpot", "AWS OR GCP"],
        "funding_stage": ["Series A", "Series B", "Series C"],
        "geography": ["US", "Canada"]
    }

    results = hunt_icp_accounts(icp)
    print(json.dumps(results, indent=2))
