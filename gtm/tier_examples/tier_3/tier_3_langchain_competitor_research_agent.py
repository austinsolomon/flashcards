"""
GTM - Tier 3: Single-Purpose Agent - Competitor Research Agent

Use Case: Autonomously research competitors mentioned in sales calls or strategic docs,
gathering pricing, features, positioning, and ICP data to create actionable battlecards.

Tool Used: LangChain with multiple tools (web search, scraping, document analysis)
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests


# ============================================================================
# CUSTOM TOOLS
# ============================================================================

def search_web(query: str) -> str:
    """Search the web for information about competitors."""
    search = DuckDuckGoSearchRun()
    results = search.run(query)
    return results


def scrape_website(url: str) -> str:
    """Scrape and extract text content from a website."""
    try:
        loader = WebBaseLoader(url)
        documents = loader.load()

        # Split into chunks for better processing
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)

        # Return first 3 chunks (enough for pricing/features usually)
        return "\n\n".join([chunk.page_content for chunk in chunks[:3]])
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"


def extract_pricing_info(company_name: str, website_content: str) -> str:
    """
    Extract pricing information from website content using focused LLM call.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"""Extract pricing information for {company_name} from this content.

Content:
{website_content[:3000]}

Provide structured output:
- Pricing tiers (names and prices)
- Key features per tier
- Any free trial info
- Enterprise/custom pricing availability

If no pricing found, return "Pricing not publicly available"
"""

    response = llm.invoke(prompt)
    return response.content


def save_battlecard(company_name: str, data: Dict[str, Any]) -> str:
    """Save competitor battlecard to JSON file."""
    output_dir = "./battlecards"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{output_dir}/{company_name.lower().replace(' ', '_')}_battlecard.json"

    battlecard = {
        "company": company_name,
        "generated_at": datetime.now().isoformat(),
        **data
    }

    with open(filename, 'w') as f:
        json.dump(battlecard, f, indent=2)

    return f"Battlecard saved to {filename}"


# ============================================================================
# AGENT SETUP
# ============================================================================

def create_competitor_research_agent():
    """Create a LangChain agent with competitor research tools."""

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # Define tools
    tools = [
        Tool(
            name="search_web",
            func=search_web,
            description="Search the web for information. Use for finding competitor websites, news, reviews, comparisons."
        ),
        Tool(
            name="scrape_website",
            func=scrape_website,
            description="Extract text content from a URL. Use after finding competitor website to get detailed info."
        ),
        Tool(
            name="extract_pricing",
            func=extract_pricing_info,
            description="Extract structured pricing information from website content. Requires company_name and website_content as input."
        ),
        Tool(
            name="save_battlecard",
            func=save_battlecard,
            description="Save completed competitor analysis as a battlecard. Call this as the final step with all gathered data."
        )
    ]

    # Create agent prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a competitive intelligence analyst for a B2B SaaS company.

Your task is to research competitors and create comprehensive battlecards with:
1. Company overview and positioning
2. Target market / ICP (Ideal Customer Profile)
3. Pricing structure (all tiers if available)
4. Key features and differentiators
5. Strengths and weaknesses
6. Win/loss patterns (if found in reviews/comparisons)

Research process:
1. Search for the competitor's official website
2. Scrape their website to extract positioning, features, and pricing
3. Search for reviews (G2, Capterra, etc.) and comparison articles
4. Extract pricing details using the specialized tool
5. Compile all findings into a structured battlecard
6. Save the battlecard using the save_battlecard tool

Be thorough but efficient. Focus on actionable intelligence for sales teams."""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    # Create agent
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True
    )

    return agent_executor


# ============================================================================
# EXECUTION
# ============================================================================

def research_competitor(competitor_name: str) -> Dict[str, Any]:
    """
    Main function to research a competitor and generate battlecard.

    Args:
        competitor_name: Name of the competitor to research

    Returns:
        Dictionary containing research results and file path
    """
    print(f"\n{'='*60}")
    print(f"Starting competitor research for: {competitor_name}")
    print(f"{'='*60}\n")

    agent = create_competitor_research_agent()

    # Run the agent
    result = agent.invoke({
        "input": f"Research {competitor_name} and create a comprehensive battlecard. "
                f"Include: company overview, target market, pricing (all tiers), "
                f"key features, strengths/weaknesses, and any win/loss patterns from reviews."
    })

    print(f"\n{'='*60}")
    print("Research Complete!")
    print(f"{'='*60}\n")

    return result


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    How to Run:

    1. Install dependencies:
       pip install langchain langchain-openai langchain-community duckduckgo-search beautifulsoup4 lxml

    2. Set environment variable:
       export OPENAI_API_KEY='your-api-key-here'

    3. Run the script:
       python tier_3_langchain_competitor_research_agent.py

    Expected Output:
    - Autonomous web research (you'll see search queries, website scraping, analysis)
    - A JSON battlecard file saved to ./battlecards/
    - Console output showing agent's reasoning process
    """

    # Example: Research a competitor
    competitor = "HubSpot"  # Change to any B2B SaaS competitor

    result = research_competitor(competitor)

    print("\n" + "="*60)
    print("AGENT OUTPUT:")
    print("="*60)
    print(result['output'])

    # Example battlecard structure that would be created:
    example_battlecard = {
        "company": "HubSpot",
        "generated_at": "2025-01-15T10:30:00Z",
        "overview": {
            "tagline": "Inbound marketing, sales, and service software",
            "founded": "2006",
            "headquarters": "Cambridge, MA",
            "target_market": "SMB to Mid-Market",
            "positioning": "All-in-one CRM platform"
        },
        "icp": {
            "company_size": "10-1000 employees",
            "industries": ["Technology", "Services", "E-commerce"],
            "use_cases": ["Inbound marketing", "Sales automation", "Customer service"]
        },
        "pricing": {
            "tiers": [
                {"name": "Free", "price": "$0/mo", "features": ["Contact management", "Email marketing (2k sends)", "Forms", "Live chat"]},
                {"name": "Starter", "price": "$45/mo", "features": ["Everything in Free", "Email marketing (1k contacts)", "Simple automation", "Custom branding"]},
                {"name": "Professional", "price": "$800/mo", "features": ["Everything in Starter", "Marketing automation", "SEO tools", "Multi-language", "Phone support"]},
                {"name": "Enterprise", "price": "$3,200/mo", "features": ["Everything in Professional", "Advanced permissions", "Custom objects", "Predictive lead scoring"]}
            ],
            "free_trial": "14 days for paid tiers",
            "notes": "Prices increase based on contact count"
        },
        "key_features": [
            "Unified CRM database across marketing, sales, service",
            "Visual workflow builder for automation",
            "Content management system (CMS) included",
            "Extensive app marketplace",
            "Strong reporting and analytics"
        ],
        "strengths": [
            "Easy to use, especially for non-technical users",
            "Generous free tier for startups",
            "Strong inbound marketing tools",
            "Comprehensive documentation and training"
        ],
        "weaknesses": [
            "Can get expensive quickly as contacts grow",
            "Enterprise features locked behind highest tier",
            "Limited customization compared to Salesforce",
            "Some advanced features require professional services"
        ],
        "win_loss_patterns": {
            "win_against_us": ["Simpler setup", "Better for inbound marketing", "Lower entry price"],
            "lose_against_us": ["Our superior enterprise features", "Better API flexibility", "More cost-effective at scale"]
        },
        "sales_talking_points": [
            "While HubSpot has good inbound tools, we excel at [YOUR DIFFERENTIATOR]",
            "HubSpot pricing scales with contacts - ours is more predictable",
            "For enterprise needs, we offer [ENTERPRISE FEATURES] that HubSpot lacks"
        ]
    }

    print("\n" + "="*60)
    print("EXAMPLE BATTLECARD STRUCTURE:")
    print("="*60)
    print(json.dumps(example_battlecard, indent=2))

    """
    Tier Classification Reasoning:

    This is Tier 3 (Single-Purpose Agent) because:

    1. **Autonomous tool use**: Agent decides which tools to use and in what order
    2. **Multi-step reasoning**: Chains together search → scrape → analyze → save
    3. **Focused purpose**: Does one thing (competitor research) exceptionally well
    4. **No human intervention**: Runs completely autonomously once given competitor name
    5. **Tool selection logic**: Agent chooses to scrape pricing page vs homepage based on context
    6. **Self-contained**: Handles entire research workflow from search to output

    This differs from Tier 2 (context-aware workflow) because the agent makes autonomous
    decisions about which tools to use and how to combine information. It's not following
    a predetermined workflow - it adapts based on what it finds.

    This differs from Tier 4 (multi-agent) because it's a single agent, not multiple
    specialized agents collaborating. One agent, one purpose, autonomous execution.

    Cost: ~$0.15-0.30 per competitor researched (GPT-4 + web searches)
    Time: 2-4 minutes per competitor
    Output: Structured JSON battlecard ready for sales team
    """
