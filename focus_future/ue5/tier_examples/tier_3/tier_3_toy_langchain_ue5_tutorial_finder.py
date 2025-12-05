#!/usr/bin/env python3
"""
UE5 - Tier 3 - Tutorial & Documentation Finder (LangChain Agent)

TIER 3 CHARACTERISTICS:
- Single agent with tool calling capabilities
- Agent decides which tools to use and in what order
- Uses reasoning to find best learning resources
- Autonomous decision-making within a single task
- No multi-agent coordination (that's Tier 4)

What It Does:
Given a UE5 topic/feature, autonomously finds the best tutorials, documentation,
and learning resources by using web search, YouTube search, and official docs search.
The agent decides which resources are most helpful.

Tier Contrast:
- Tier 2: Would use ONE LLM call to categorize the request
- Tier 3: Agent uses MULTIPLE tools to find and evaluate resources
- Tier 4: Would have DiscoveryAgent → EvaluationAgent → CurationAgent
"""

import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool

load_dotenv()


# ============================================================================
# TIER 3 CHARACTERISTIC: Tool Definitions
# Agent has multiple search tools and decides which to use
# ============================================================================

def web_search_tool(query: str) -> str:
    """
    TIER 3 TOOL: General web search for UE5 tutorials

    In production: call Serper, Brave, Google Search API
    Toy example: simulated search results
    """
    print(f"🔍 [WEB_SEARCH] Searching for: {query}")

    # Simulated search results based on query
    if "niagara" in query.lower():
        return """
        Web Search Results:
        1. "Unreal Engine Niagara VFX Tutorial for Beginners" - UnrealSensei.com
           Comprehensive 2-hour tutorial covering Niagara particles from scratch

        2. "Advanced Niagara Techniques in UE5" - 80.lv Interview
           Industry experts share production-ready Niagara workflows

        3. "Niagara vs Cascade: When to Use Each" - Unreal Dev Community
           Guide on choosing between particle systems
        """
    elif "blueprint" in query.lower():
        return """
        Web Search Results:
        1. "Blueprint Visual Scripting Masterclass" - Udemy
           50+ hours of Blueprint training, 4.8★ rating

        2. "Blueprint Best Practices 2024" - Unreal Engine Forums
           Community-curated best practices and optimization tips

        3. "From Blueprint to C++: When to Make the Transition" - gamedev.net
           Guide on scaling from Blueprints to C++ code
        """
    else:
        return f"""
        Web Search Results for '{query}':
        1. Official Unreal Engine Documentation - docs.unrealengine.com
        2. Unreal Engine Community Forums - forums.unrealengine.com
        3. Unreal Slackers Discord - Large community of UE developers
        """


def youtube_search_tool(topic: str) -> str:
    """
    TIER 3 TOOL: YouTube tutorial search

    In production: call YouTube Data API
    Toy example: simulated video results
    """
    print(f"📺 [YOUTUBE_SEARCH] Searching YouTube for: {topic}")

    # Simulated YouTube results
    if "niagara" in topic.lower():
        return """
        YouTube Tutorial Results:

        1. "UE5 Niagara Tutorial - Create Realistic Fire Effect" - Unreal Sensei
           Views: 450K | Duration: 28:45 | Rating: 98% liked
           Level: Intermediate
           https://youtube.com/watch?v=example1

        2. "Complete Niagara VFX Course" - Ben Cloward
           Views: 1.2M | Duration: 2:15:30 | Rating: 99% liked
           Level: Beginner to Advanced
           https://youtube.com/watch?v=example2

        3. "Niagara Particle System From Scratch" - Ryan Laley
           Views: 280K | Duration: 45:20 | Rating: 97% liked
           Level: Beginner
           https://youtube.com/watch?v=example3
        """
    elif "blueprint" in topic.lower():
        return """
        YouTube Tutorial Results:

        1. "Blueprint Basics for Beginners" - Matt Aspland
           Views: 850K | Duration: 1:15:00 | Rating: 99% liked
           Level: Beginner

        2. "Advanced Blueprint Patterns" - Mathew Wadstein
           Views: 320K | Duration: 3:45:00 | Rating: 98% liked
           Level: Advanced

        3. "Blueprint Performance Optimization" - Tech Art Aid
           Views: 180K | Duration: 35:15 | Rating: 96% liked
           Level: Intermediate
        """
    else:
        return f"""
        YouTube Tutorial Results for '{topic}':
        1. "UE5 Tutorial Series" - Various creators
        2. "Unreal Engine Official Channel" - Epic Games tutorials
        3. "Community Tutorials" - Multiple sources
        """


def docs_search_tool(feature: str) -> str:
    """
    TIER 3 TOOL: Official Unreal Engine documentation search

    In production: scrape or query docs.unrealengine.com
    Toy example: simulated documentation links
    """
    print(f"📚 [DOCS_SEARCH] Searching UE5 docs for: {feature}")

    # Simulated documentation results
    return f"""
    Official Unreal Engine Documentation:

    1. {feature} Overview
       https://docs.unrealengine.com/5.3/en-US/{feature.lower()}/overview/
       Comprehensive overview of {feature} system architecture and concepts

    2. {feature} Quick Start Guide
       https://docs.unrealengine.com/5.3/en-US/{feature.lower()}/quick-start/
       Step-by-step guide to getting started with {feature}

    3. {feature} Best Practices
       https://docs.unrealengine.com/5.3/en-US/{feature.lower()}/best-practices/
       Recommended workflows and optimization techniques

    4. {feature} API Reference
       https://docs.unrealengine.com/5.3/en-US/{feature.lower()}/api-reference/
       Complete API documentation for C++ and Blueprint classes

    5. {feature} Troubleshooting Guide
       https://docs.unrealengine.com/5.3/en-US/{feature.lower()}/troubleshooting/
       Common issues and solutions
    """


# ============================================================================
# TIER 3 CHARACTERISTIC: Tool Setup for Agent
# ============================================================================

tools = [
    Tool(
        name="web_search",
        description="Search the web for UE5 tutorials, articles, and community resources. "
                    "Use this to find general learning resources and community discussions. "
                    "Input should be a search query about a UE5 topic.",
        func=web_search_tool
    ),
    Tool(
        name="youtube_search",
        description="Search YouTube for UE5 video tutorials. Returns video titles, views, "
                    "duration, and difficulty level. Use this to find visual learning resources. "
                    "Input should be a UE5 topic or feature name.",
        func=youtube_search_tool
    ),
    Tool(
        name="docs_search",
        description="Search official Unreal Engine documentation. Returns links to official "
                    "docs including overviews, quick starts, API references, and best practices. "
                    "Use this for authoritative technical information. Input should be a feature name.",
        func=docs_search_tool
    )
]


# ============================================================================
# TIER 3 CHARACTERISTIC: Agent Prompt
# Instructs agent to curate best learning resources
# ============================================================================

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a UE5 learning resource curator that helps developers find the best tutorials and documentation.

Your goal: Given a UE5 topic or feature, find and recommend the best learning resources.

TIER 3 REASONING APPROACH:
1. Understand what the user wants to learn
2. Search official docs for authoritative information
3. Find YouTube tutorials for visual learning
4. Search web for community resources and advanced techniques
5. Curate the best resources with clear recommendations

You have access to these tools:
- web_search: Find tutorials, articles, community discussions
- youtube_search: Find video tutorials with ratings and difficulty levels
- docs_search: Find official Unreal Engine documentation

Think step-by-step about what resources would be most helpful. When you have enough information, provide:
- Recommended learning path (beginner → intermediate → advanced)
- Best video tutorial with explanation why
- Key documentation links
- Community resources for deeper learning

Consider the user's likely skill level and provide appropriate resources."""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])


# ============================================================================
# TIER 3 CHARACTERISTIC: Agent Creation & Execution
# ============================================================================

def create_tutorial_finder_agent():
    """Create the LangChain agent for finding UE5 tutorials"""
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    agent = create_openai_tools_agent(llm, tools, agent_prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True
    )

    return agent_executor


def find_tutorials(topic: str, skill_level: str = "beginner") -> Dict[str, Any]:
    """
    Main function: Find best learning resources for a UE5 topic

    TIER 3 CHARACTERISTIC: Agent autonomously decides which resources to search
    """
    print(f"\n{'='*60}")
    print(f"📚 TIER 3 AGENT: Finding tutorials for '{topic}' ({skill_level} level)")
    print(f"{'='*60}\n")

    agent = create_tutorial_finder_agent()

    try:
        result = agent.invoke({
            "input": f"I want to learn about {topic} in Unreal Engine 5. "
                     f"My skill level is {skill_level}. Find me the best learning resources."
        })

        print(f"\n{'='*60}")
        print(f"✅ AGENT COMPLETE")
        print(f"{'='*60}\n")

        return {
            "success": True,
            "topic": topic,
            "skill_level": skill_level,
            "output": result["output"]
        }

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Example Usage
# ============================================================================

def main():
    """Example usage of the Tier 3 tutorial finder agent"""

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found")
        print("Please set it in your .env file")
        sys.exit(1)

    # Example 1: Niagara particle system
    print("\n" + "="*60)
    print("EXAMPLE 1: Learn Niagara VFX System")
    print("="*60)

    result1 = find_tutorials("Niagara particle systems", "beginner")

    if result1["success"]:
        print("\n📋 CURATED RESOURCES:")
        print(result1["output"])

    # Example 2: Blueprint scripting
    print("\n" + "="*60)
    print("EXAMPLE 2: Advanced Blueprint Patterns")
    print("="*60)

    result2 = find_tutorials("Blueprint visual scripting", "intermediate")

    if result2["success"]:
        print("\n📋 CURATED RESOURCES:")
        print(result2["output"])

    # Show tier characteristics
    print("\n" + "="*60)
    print("🎓 WHY THIS IS TIER 3:")
    print("="*60)
    print("""
    1. Single Agent: One agent curates all learning resources
    2. Multiple Tools: web_search, youtube_search, docs_search
    3. Autonomous Decisions: Agent chooses which sources to query
    4. Resource Evaluation: Agent evaluates quality and appropriateness
    5. Curated Recommendations: Synthesizes findings into learning path

    Contrast with other tiers:
    - Tier 2: Would use ONE AI call to suggest resources (no actual searching)
    - Tier 4: Would have DiscoveryAgent → EvaluationAgent → CurationAgent (multi-agent)
    - Tier 5: Would orchestrate: Agent finds → Human reviews → Add to curriculum
    - Tier 6: Would autonomously track user progress and adapt recommendations
    """)


if __name__ == "__main__":
    main()
