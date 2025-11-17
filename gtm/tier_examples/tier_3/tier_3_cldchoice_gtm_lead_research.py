#!/usr/bin/env python3
"""
GTM - Tier 3 - Prospect Research Agent (LangChain Production)

TIER 3 CHARACTERISTICS:
- Single agent with autonomous tool calling
- Multiple specialized tools (web search, LinkedIn, company enrichment)
- Agent decides which tools to use and in what order
- Structured output for downstream workflows
- Production-ready with error handling and logging

What It Does:
Given a company name and target role, autonomously researches the company,
finds the best decision-maker for outreach, gathers pain points and buying
signals, and returns structured data for personalized email generation.

Integration:
- Called by Tier 1 orchestration workflow via HTTP API
- Returns research data that feeds into Tier 2 email generation
- Part of complete lead research automation stack
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# LangChain imports
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_core.pydantic_v1 import BaseModel, Field

# FastAPI for production deployment
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel as PydanticBaseModel
import uvicorn

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Request/Response Models
# ============================================================================

class ResearchRequest(PydanticBaseModel):
    """API request model for research endpoint"""
    company_name: str = Field(..., description="Target company name")
    industry: Optional[str] = Field(None, description="Industry/vertical")
    target_role: str = Field("VP of Sales", description="Target role to find")
    research_depth: str = Field("standard", description="standard or deep")


class DecisionMaker(PydanticBaseModel):
    """Decision maker information"""
    name: str
    title: str
    email: str
    linkedin_url: Optional[str] = None


class CompanyInfo(PydanticBaseModel):
    """Company information"""
    size: str
    funding: str
    tech_stack: List[str]
    website: Optional[str] = None


class ResearchResponse(PydanticBaseModel):
    """API response model"""
    success: bool
    company_name: str
    decision_maker: Optional[DecisionMaker] = None
    company_info: Optional[CompanyInfo] = None
    pain_points: List[str] = []
    buying_signals: List[str] = []
    research_date: str
    error: Optional[str] = None


# ============================================================================
# TIER 3 CHARACTERISTIC: Tool Definitions
# ============================================================================

def web_search_tool(query: str) -> str:
    """
    TIER 3 TOOL: Web search for company and prospect information

    In production, integrate with:
    - Serper API (https://serper.dev)
    - Brave Search API
    - Google Custom Search API

    Returns search results for agent to analyze
    """
    logger.info(f"Web search: {query}")

    # PRODUCTION: Replace with real search API
    # Example with Serper:
    # import requests
    # response = requests.post('https://google.serper.dev/search',
    #     headers={'X-API-KEY': os.getenv('SERPER_API_KEY')},
    #     json={'q': query})
    # return response.json()['organic']

    # Simulated responses for demo
    query_lower = query.lower()

    if "ceo" in query_lower or "vp" in query_lower or "decision maker" in query_lower:
        return json.dumps([
            {
                "title": f"{query.split()[0]} Leadership Team",
                "snippet": "Sarah Chen serves as VP of Sales, leading the revenue organization. Previously led sales at Salesforce...",
                "link": "https://company.com/about/leadership"
            },
            {
                "title": "LinkedIn Profile - Sarah Chen",
                "snippet": "VP of Sales at Acme Corp. Expert in enterprise SaaS sales, team building, and revenue operations...",
                "link": "https://linkedin.com/in/sarah-chen-sales"
            }
        ])
    elif "funding" in query_lower or "series" in query_lower:
        return json.dumps([
            {
                "title": f"{query.split()[0]} Raises $50M Series B",
                "snippet": "Led by Sequoia Capital, the round will fuel product development and market expansion...",
                "link": "https://techcrunch.com/acme-series-b"
            }
        ])
    elif "tech stack" in query_lower or "uses" in query_lower:
        return json.dumps([
            {
                "title": f"{query.split()[0]} Tech Stack",
                "snippet": "Built on modern stack: React, Python, AWS, Salesforce, HubSpot, Slack, Segment...",
                "link": "https://stackshare.io/acme-corp"
            }
        ])
    else:
        return json.dumps([
            {
                "title": f"{query.split()[0]} - Company Overview",
                "snippet": "Enterprise SaaS company providing workflow automation. 200-500 employees, HQ in San Francisco...",
                "link": "https://company.com"
            }
        ])


def linkedin_profile_finder(person_name: str, company_name: str) -> str:
    """
    TIER 3 TOOL: Find LinkedIn profile for a person at a company

    In production, integrate with:
    - LinkedIn Sales Navigator API
    - Proxycurl API
    - Apollo.io API

    Returns profile data including email pattern
    """
    logger.info(f"LinkedIn lookup: {person_name} at {company_name}")

    # PRODUCTION: Replace with real LinkedIn API
    # Example with Proxycurl:
    # import requests
    # response = requests.get('https://nubela.co/proxycurl/api/v2/linkedin',
    #     params={'url': linkedin_url},
    #     headers={'Authorization': f'Bearer {os.getenv("PROXYCURL_API_KEY")}'})
    # return json.dumps(response.json())

    # Simulated response
    name_parts = person_name.lower().split()
    first_name = name_parts[0] if name_parts else "person"
    last_name = name_parts[-1] if len(name_parts) > 1 else "lastname"
    company_domain = company_name.lower().replace(" ", "").replace("corp", "").replace("inc", "") + ".com"

    return json.dumps({
        "name": person_name,
        "title": "VP of Sales & Revenue Operations",
        "company": company_name,
        "location": "San Francisco Bay Area",
        "email_pattern": f"{first_name}.{last_name}@{company_domain}",
        "linkedin_url": f"https://linkedin.com/in/{first_name}-{last_name}-sales",
        "experience": [
            {"company": company_name, "title": "VP of Sales", "duration": "2 years"},
            {"company": "Salesforce", "title": "Enterprise Sales Director", "duration": "4 years"}
        ],
        "education": ["Stanford MBA", "UC Berkeley BS"],
        "recent_posts": [
            "Excited to share that we're scaling our GTM motion - hiring 5 sales reps!",
            "Great discussion at SaaStr about building sales operations at scale"
        ]
    })


def company_enrichment_tool(company_name: str) -> str:
    """
    TIER 3 TOOL: Get detailed company information

    In production, integrate with:
    - Clearbit Enrichment API
    - ZoomInfo API
    - Apollo.io API

    Returns firmographic and technographic data
    """
    logger.info(f"Company enrichment: {company_name}")

    # PRODUCTION: Replace with real enrichment API
    # Example with Clearbit:
    # import requests
    # response = requests.get(f'https://company.clearbit.com/v2/companies/find',
    #     params={'domain': company_domain},
    #     headers={'Authorization': f'Bearer {os.getenv("CLEARBIT_API_KEY")}'})
    # return json.dumps(response.json())

    # Simulated response
    return json.dumps({
        "name": company_name,
        "domain": f"{company_name.lower().replace(' ', '')}.com",
        "size": "200-500 employees",
        "industry": "Enterprise SaaS - Workflow Automation",
        "founded": 2018,
        "funding": {
            "total": "$75M",
            "stage": "Series B",
            "investors": ["Sequoia Capital", "Accel Partners"]
        },
        "tech_stack": [
            "Salesforce", "HubSpot", "Outreach.io", "ZoomInfo",
            "Slack", "AWS", "React", "Python"
        ],
        "employee_count": 250,
        "revenue_estimated": "$20M ARR",
        "growth_rate": "200% YoY",
        "locations": ["San Francisco, CA", "New York, NY", "Austin, TX"],
        "recent_news": [
            "Launched AI-powered workflow builder",
            "Expanding to European market",
            "Raised $50M Series B"
        ],
        "job_postings": [
            {"title": "Sales Operations Manager", "posted": "5 days ago"},
            {"title": "Enterprise Account Executive", "posted": "12 days ago"},
            {"title": "Customer Success Manager", "posted": "18 days ago"}
        ]
    })


def pain_point_analyzer(company_info: str, industry: str) -> str:
    """
    TIER 3 TOOL: Analyze company data to identify likely pain points

    Uses heuristics and pattern matching to identify pain points
    based on company size, tech stack, and industry
    """
    logger.info(f"Analyzing pain points for {industry} company")

    try:
        info = json.loads(company_info)
        pain_points = []

        # Size-based pain points
        if info.get("employee_count", 0) > 200:
            pain_points.append("Managing data across disconnected systems as team scales")
            pain_points.append("Manual reporting and dashboard creation consuming significant time")

        # Tech stack analysis
        tech_stack = info.get("tech_stack", [])
        if len(tech_stack) > 5:
            pain_points.append(f"Tool sprawl - {len(tech_stack)} different systems requiring manual integration")

        if "Salesforce" in tech_stack and "HubSpot" in tech_stack:
            pain_points.append("Data sync challenges between Salesforce and HubSpot")

        # Growth indicators
        if info.get("growth_rate", "").find("200%") >= 0:
            pain_points.append("Rapid growth straining existing processes and systems")

        # Job postings analysis
        job_postings = info.get("job_postings", [])
        if any("Operations" in job.get("title", "") for job in job_postings):
            pain_points.append("Hiring for operations roles suggests process inefficiencies")

        return json.dumps(pain_points)

    except Exception as e:
        logger.error(f"Error analyzing pain points: {e}")
        return json.dumps([
            "Potential workflow automation needs",
            "Data integration challenges likely"
        ])


def buying_signal_detector(company_info: str, linkedin_data: str) -> str:
    """
    TIER 3 TOOL: Detect buying signals from company and prospect data

    Identifies indicators of purchase readiness
    """
    logger.info("Detecting buying signals")

    try:
        company = json.loads(company_info)
        linkedin = json.loads(linkedin_data)

        signals = []

        # Funding signals
        if company.get("funding", {}).get("stage") in ["Series B", "Series C"]:
            signals.append(f"Recently raised {company['funding']['total']} - in growth/investment mode")

        # Hiring signals
        job_postings = company.get("job_postings", [])
        if job_postings:
            signals.append(f"Actively hiring {len(job_postings)} roles - scaling operations")

        # Leadership activity
        recent_posts = linkedin.get("recent_posts", [])
        if recent_posts:
            for post in recent_posts[:2]:
                if any(word in post.lower() for word in ["scaling", "growing", "hiring", "expanding"]):
                    signals.append(f"Decision-maker posted about: '{post[:100]}...'")

        # Tech stack signals
        tech_stack = company.get("tech_stack", [])
        if any(competitor in tech_stack for competitor in ["Zapier", "Make", "Workato"]):
            signals.append("Currently using competitor solutions - potential to switch/upgrade")

        # News/PR signals
        recent_news = company.get("recent_news", [])
        if recent_news:
            signals.append(f"Recent company updates: {', '.join(recent_news[:2])}")

        # Event signals (from LinkedIn)
        posts_about_events = [p for p in recent_posts if any(event in p.lower() for event in ["conference", "summit", "event"])]
        if posts_about_events:
            signals.append("Decision-maker active at industry events - open to new solutions")

        return json.dumps(signals)

    except Exception as e:
        logger.error(f"Error detecting buying signals: {e}")
        return json.dumps(["Company shows growth indicators"])


# ============================================================================
# TIER 3 CHARACTERISTIC: Agent Setup
# ============================================================================

# Define tools for the agent
tools = [
    Tool(
        name="web_search",
        description="Search the web for information about companies, people, or topics. "
                    "Use this to find decision-makers, company news, funding, etc. "
                    "Input should be a search query string.",
        func=web_search_tool
    ),
    Tool(
        name="linkedin_profile_finder",
        description="Find a person's LinkedIn profile given their name and company. "
                    "Returns profile data, title, email pattern, and recent activity. "
                    "Input format: 'person_name, company_name'",
        func=lambda x: linkedin_profile_finder(*[s.strip() for s in x.split(',')])
    ),
    Tool(
        name="company_enrichment",
        description="Get detailed company information including size, funding, tech stack, "
                    "employees, recent news, and job postings. "
                    "Input should be the company name.",
        func=company_enrichment_tool
    ),
    Tool(
        name="pain_point_analyzer",
        description="Analyze company data to identify likely pain points and challenges. "
                    "Input should be company_info JSON from company_enrichment tool, and industry string, "
                    "separated by a pipe: 'company_info_json | industry'",
        func=lambda x: pain_point_analyzer(*[s.strip() for s in x.split('|')])
    ),
    Tool(
        name="buying_signal_detector",
        description="Detect buying signals from company and prospect data. "
                    "Input should be company_info JSON and linkedin_data JSON, separated by a pipe: "
                    "'company_info_json | linkedin_data_json'",
        func=lambda x: buying_signal_detector(*[s.strip() for s in x.split('|')])
    )
]


# Agent prompt
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert B2B sales research agent. Your job is to research a target company and find the best decision-maker for outreach.

RESEARCH PROCESS:
1. Use company_enrichment to get comprehensive company data
2. Use web_search to find decision-makers in the target role
3. Use linkedin_profile_finder to get detailed profile and email
4. Use pain_point_analyzer to identify challenges (pass company info and industry)
5. Use buying_signal_detector to identify purchase readiness (pass company info and linkedin data)

OUTPUT REQUIREMENTS:
When you have completed research, provide a structured summary in this EXACT JSON format:
```json
{
  "decision_maker": {
    "name": "Full Name",
    "title": "Exact Title",
    "email": "email@company.com",
    "linkedin_url": "https://linkedin.com/in/profile"
  },
  "company_info": {
    "size": "200-500 employees",
    "funding": "$50M Series B",
    "tech_stack": ["Tool1", "Tool2", "Tool3"],
    "website": "https://company.com"
  },
  "pain_points": [
    "Specific pain point 1",
    "Specific pain point 2"
  ],
  "buying_signals": [
    "Specific buying signal 1",
    "Specific buying signal 2"
  ]
}
```

Be thorough but efficient. Use only the tools needed to gather complete information."""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])


def create_research_agent():
    """Create the LangChain research agent"""
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    agent = create_openai_tools_agent(llm, tools, agent_prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=15,
        handle_parsing_errors=True,
        return_intermediate_steps=False
    )

    return agent_executor


def research_prospect(
    company_name: str,
    industry: Optional[str] = None,
    target_role: str = "VP of Sales",
    research_depth: str = "standard"
) -> ResearchResponse:
    """
    Main research function - calls Tier 3 agent

    Args:
        company_name: Target company name
        industry: Industry/vertical (helps with pain point analysis)
        target_role: Role to find (VP of Sales, Head of Marketing, etc.)
        research_depth: "standard" or "deep"

    Returns:
        ResearchResponse with structured data
    """
    logger.info(f"Starting research: {company_name}, role: {target_role}")

    try:
        # Create agent
        agent = create_research_agent()

        # Build research query
        query = f"Research {company_name}"
        if industry:
            query += f" (industry: {industry})"
        query += f". Find the {target_role} and gather decision-maker info, company details, pain points, and buying signals."

        # Run agent
        result = agent.invoke({"input": query})

        # Parse agent output
        output = result["output"]

        # Extract JSON from output
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', output, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1))
        else:
            # Try parsing the whole output as JSON
            data = json.loads(output)

        # Build response
        response = ResearchResponse(
            success=True,
            company_name=company_name,
            decision_maker=DecisionMaker(**data.get("decision_maker", {})) if data.get("decision_maker") else None,
            company_info=CompanyInfo(**data.get("company_info", {})) if data.get("company_info") else None,
            pain_points=data.get("pain_points", []),
            buying_signals=data.get("buying_signals", []),
            research_date=datetime.now().isoformat()
        )

        logger.info(f"Research completed successfully for {company_name}")
        return response

    except Exception as e:
        logger.error(f"Research failed for {company_name}: {str(e)}")
        return ResearchResponse(
            success=False,
            company_name=company_name,
            research_date=datetime.now().isoformat(),
            error=str(e)
        )


# ============================================================================
# FastAPI Application for Production Deployment
# ============================================================================

app = FastAPI(
    title="Tier 3 Prospect Research Agent API",
    description="Autonomous research agent for B2B lead intelligence",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/research", response_model=ResearchResponse)
async def research_endpoint(request: ResearchRequest):
    """
    Main research endpoint - called by Tier 1 orchestration workflow

    POST /research
    {
      "company_name": "Acme Corp",
      "industry": "Enterprise SaaS",
      "target_role": "VP of Sales",
      "research_depth": "standard"
    }
    """
    logger.info(f"API request: {request.company_name}")

    result = research_prospect(
        company_name=request.company_name,
        industry=request.industry,
        target_role=request.target_role,
        research_depth=request.research_depth
    )

    return result


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "tier3_research_agent",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# CLI for Testing
# ============================================================================

def main():
    """CLI for testing the agent"""
    import argparse

    parser = argparse.ArgumentParser(description="Prospect Research Agent")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--industry", help="Industry/vertical")
    parser.add_argument("--role", default="VP of Sales", help="Target role")
    parser.add_argument("--server", action="store_true", help="Run as API server")
    parser.add_argument("--port", type=int, default=8000, help="Server port")

    args = parser.parse_args()

    if args.server:
        logger.info(f"Starting API server on port {args.port}")
        uvicorn.run(app, host="0.0.0.0", port=args.port)
    else:
        # CLI mode
        result = research_prospect(
            company_name=args.company,
            industry=args.industry,
            target_role=args.role
        )

        print("\n" + "="*60)
        print("RESEARCH RESULTS")
        print("="*60)
        print(result.json(indent=2))


if __name__ == "__main__":
    main()
