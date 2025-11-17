"""
UE5 - Tier 3: Single-Purpose Agent - Tutorial Finder and Curator

Use Case: Autonomously search for, evaluate, and curate UE5 tutorials based on
specific learning goals, ranking them by quality, recency, and relevance.

Tool Used: LangChain with web search, content scraping, and quality assessment tools
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import urlparse

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


# ============================================================================
# CUSTOM TOOLS
# ============================================================================

def search_ue5_tutorials(query: str) -> str:
    """
    Search for UE5 tutorials with quality indicators.
    """
    search = DuckDuckGoSearchRun()

    # Enhance query with UE5-specific terms and quality signals
    enhanced_query = f"Unreal Engine 5 {query} tutorial 2024 2025"

    results = search.run(enhanced_query)
    return results


def analyze_tutorial_page(url: str) -> str:
    """
    Scrape tutorial page and extract key information.
    """
    try:
        loader = WebBaseLoader(url)
        documents = loader.load()

        # Extract content
        content = documents[0].page_content if documents else ""

        # Limit content size for LLM processing
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_text(content)

        return chunks[0] if chunks else "Could not extract content"
    except Exception as e:
        return f"Error analyzing {url}: {str(e)}"


def rate_tutorial_quality(tutorial_data: str) -> Dict[str, Any]:
    """
    Use LLM to assess tutorial quality based on content analysis.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"""Analyze this tutorial content and rate its quality for learning Unreal Engine 5.

Tutorial Content:
{tutorial_data[:2000]}

Provide a JSON response with:
{{
  "quality_score": 1-10,
  "difficulty_level": "beginner|intermediate|advanced|expert",
  "estimated_duration": "time to complete (e.g., 30 min, 2 hours)",
  "prerequisites": ["list of required knowledge"],
  "key_topics_covered": ["specific topics"],
  "has_project_files": true/false,
  "has_video": true/false,
  "pros": ["strengths of this tutorial"],
  "cons": ["weaknesses or missing elements"],
  "recommended_for": "description of ideal learner"
}}
"""

    response = llm.invoke(prompt)

    # Parse JSON from response
    try:
        import re
        json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return {"error": "Could not parse quality assessment"}
    except:
        return {"error": "Could not parse quality assessment", "raw": response.content}


def check_tutorial_currency(url: str, content: str) -> Dict[str, Any]:
    """
    Check if tutorial is up-to-date for UE5.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"""Determine if this tutorial is current for Unreal Engine 5 (2024-2025).

URL: {url}
Content snippet: {content[:1000]}

Look for:
- Explicit version mentions (UE 5.3, 5.4, etc.)
- References to UE5-specific features (Lumen, Nanite, World Partition)
- Publication/update dates
- Screenshots/videos showing UE5 interface

Return JSON:
{{
  "is_current": true/false,
  "ue_version": "detected version",
  "last_updated": "estimated date if found",
  "currency_confidence": 0.0-1.0,
  "reasoning": "why you classified it this way"
}}
"""

    response = llm.invoke(prompt)

    try:
        import re
        json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass

    return {"is_current": False, "currency_confidence": 0.0}


def save_learning_path(topic: str, tutorials: List[Dict[str, Any]]) -> str:
    """
    Save curated tutorial list as a learning path.
    """
    output_dir = "./learning_paths"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{output_dir}/{topic.lower().replace(' ', '_')}_learning_path.json"

    learning_path = {
        "topic": topic,
        "generated_at": datetime.now().isoformat(),
        "tutorial_count": len(tutorials),
        "tutorials": tutorials,
        "recommended_order": "Tutorials are ordered from beginner to advanced",
        "estimated_total_time": "Sum of individual tutorial durations"
    }

    with open(filename, 'w') as f:
        json.dump(learning_path, f, indent=2)

    # Also create a markdown version for easy reading
    md_filename = filename.replace('.json', '.md')
    with open(md_filename, 'w') as f:
        f.write(f"# UE5 Learning Path: {topic}\n\n")
        f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d')}*\n\n")
        f.write(f"**Total Tutorials:** {len(tutorials)}\n\n")
        f.write("---\n\n")

        for i, tut in enumerate(tutorials, 1):
            f.write(f"## {i}. {tut.get('title', 'Untitled')}\n\n")
            f.write(f"**URL:** {tut.get('url', 'N/A')}\n\n")
            if 'quality_assessment' in tut:
                qa = tut['quality_assessment']
                f.write(f"**Quality Score:** {qa.get('quality_score', 'N/A')}/10\n\n")
                f.write(f"**Difficulty:** {qa.get('difficulty_level', 'N/A')}\n\n")
                f.write(f"**Duration:** {qa.get('estimated_duration', 'N/A')}\n\n")
                f.write(f"**Topics:** {', '.join(qa.get('key_topics_covered', []))}\n\n")
                if qa.get('prerequisites'):
                    f.write(f"**Prerequisites:** {', '.join(qa['prerequisites'])}\n\n")
            f.write("---\n\n")

    return f"Learning path saved to {filename} and {md_filename}"


# ============================================================================
# AGENT SETUP
# ============================================================================

def create_tutorial_finder_agent():
    """Create a LangChain agent specialized in finding and curating UE5 tutorials."""

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    tools = [
        Tool(
            name="search_ue5_tutorials",
            func=search_ue5_tutorials,
            description="Search for Unreal Engine 5 tutorials. Input should be the specific topic (e.g., 'Nanite terrain', 'Blueprint AI', 'procedural materials')"
        ),
        Tool(
            name="analyze_tutorial_page",
            func=analyze_tutorial_page,
            description="Extract and analyze content from a tutorial URL. Use this to get detailed information about a tutorial."
        ),
        Tool(
            name="rate_tutorial_quality",
            func=rate_tutorial_quality,
            description="Assess the quality of tutorial content. Provide the tutorial content as input."
        ),
        Tool(
            name="check_currency",
            func=check_tutorial_currency,
            description="Check if a tutorial is current for UE5. Provide URL and content snippet."
        ),
        Tool(
            name="save_learning_path",
            func=save_learning_path,
            description="Save the curated list of tutorials as a learning path. Provide topic and list of tutorial data."
        )
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a UE5 learning curator and expert researcher.

Your task is to find, analyze, and curate the best tutorials for specific UE5 topics.

Research process:
1. Search for tutorials on the requested topic using search_ue5_tutorials
2. For each promising result (aim for top 5-8):
   a. Analyze the tutorial page content
   b. Check if it's current for UE5 (2024-2025)
   c. Rate its quality based on content depth, clarity, and completeness
3. Filter out outdated or low-quality tutorials (quality score < 6 or not current)
4. Rank remaining tutorials by:
   - Quality score (primary)
   - Currency/recency
   - Difficulty level (beginner tutorials ranked higher for broad topics)
5. Save the final curated list as a learning path

Quality criteria:
- Clear explanations and step-by-step instructions
- UE5-specific features (Lumen, Nanite, Enhanced Input, etc.)
- Project files or downloadable examples
- Recent publication (2023-2025)
- Appropriate difficulty progression

Be selective - only include truly valuable tutorials."""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=15,
        handle_parsing_errors=True
    )

    return agent_executor


# ============================================================================
# EXECUTION
# ============================================================================

def find_tutorials(topic: str) -> Dict[str, Any]:
    """
    Main function to find and curate tutorials for a specific UE5 topic.

    Args:
        topic: The UE5 topic to find tutorials for (e.g., "Niagara VFX", "C++ gameplay")

    Returns:
        Dictionary containing curated tutorial list and file path
    """
    print(f"\n{'='*60}")
    print(f"Finding tutorials for: {topic}")
    print(f"{'='*60}\n")

    agent = create_tutorial_finder_agent()

    result = agent.invoke({
        "input": f"Find and curate the best tutorials for learning '{topic}' in Unreal Engine 5. "
                f"Search for multiple tutorials, analyze their quality, check if they're current for UE5, "
                f"and create a ranked learning path with the top 5-8 tutorials. "
                f"Filter out any tutorials older than UE5 or with quality scores below 6/10."
    })

    print(f"\n{'='*60}")
    print("Tutorial curation complete!")
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
       python tier_3_langchain_tutorial_finder_agent.py

    Expected Output:
    - Autonomous web research (searches, page analysis, quality ratings)
    - A JSON file with curated tutorials saved to ./learning_paths/
    - A markdown file with human-readable learning path
    - Console output showing agent's research process
    """

    # Example: Find tutorials on a specific UE5 topic
    topic = "Procedural Content Generation"  # Change to any UE5 topic

    result = find_tutorials(topic)

    print("\n" + "="*60)
    print("AGENT OUTPUT:")
    print("="*60)
    print(result['output'])

    # Example learning path structure that would be created:
    example_learning_path = {
        "topic": "Procedural Content Generation",
        "generated_at": "2025-01-15T11:00:00Z",
        "tutorial_count": 6,
        "tutorials": [
            {
                "title": "Procedural Generation Fundamentals in UE5",
                "url": "https://example.com/tutorial1",
                "source": "Unreal Sensei",
                "quality_assessment": {
                    "quality_score": 9,
                    "difficulty_level": "beginner",
                    "estimated_duration": "45 minutes",
                    "prerequisites": ["Basic UE5 navigation", "Blueprint basics"],
                    "key_topics_covered": ["PCG framework overview", "Simple scatter rules", "Biome generation"],
                    "has_project_files": True,
                    "has_video": True,
                    "pros": ["Clear explanations", "Project files included", "Covers UE5.3 PCG tools"],
                    "cons": ["Could go deeper on advanced techniques"],
                    "recommended_for": "Beginners wanting to understand PCG basics"
                },
                "currency_check": {
                    "is_current": True,
                    "ue_version": "5.3",
                    "last_updated": "2024-11",
                    "currency_confidence": 0.95
                }
            },
            {
                "title": "Advanced PCG: Creating Procedural Cities",
                "url": "https://example.com/tutorial2",
                "source": "Gorka Games",
                "quality_assessment": {
                    "quality_score": 10,
                    "difficulty_level": "advanced",
                    "estimated_duration": "3 hours",
                    "prerequisites": ["PCG framework knowledge", "Blueprint intermediate", "Understanding of transforms"],
                    "key_topics_covered": ["Grid-based generation", "Rule-based placement", "Performance optimization", "LOD integration"],
                    "has_project_files": True,
                    "has_video": True,
                    "pros": ["Extremely detailed", "Real-world production techniques", "Optimization covered"],
                    "cons": ["Long duration", "Requires solid foundation"],
                    "recommended_for": "Developers ready to build production-grade procedural systems"
                },
                "currency_check": {
                    "is_current": True,
                    "ue_version": "5.4",
                    "last_updated": "2024-12",
                    "currency_confidence": 0.98
                }
            }
        ],
        "recommended_order": "Tutorials ordered from beginner to advanced for progressive learning"
    }

    print("\n" + "="*60)
    print("EXAMPLE LEARNING PATH STRUCTURE:")
    print("="*60)
    print(json.dumps(example_learning_path, indent=2))

    """
    Tier Classification Reasoning:

    This is Tier 3 (Single-Purpose Agent) because:

    1. **Autonomous multi-step research**: Agent searches → analyzes → rates → ranks without human input
    2. **Tool selection based on context**: Decides which tutorials need quality analysis vs currency checks
    3. **Iterative refinement**: Can search multiple times with different queries if first results inadequate
    4. **Quality filtering**: Makes autonomous decisions about which tutorials to include/exclude
    5. **Focused expertise**: Single purpose (tutorial curation) but deep capability within that domain
    6. **Handles uncertainty**: Adapts when tutorials lack certain information or URLs fail to load

    This differs from Tier 2 (n8n + LLM) because:
    - Agent controls its own workflow, not following predetermined n8n steps
    - Makes decisions about which tools to use and when
    - Can iterate and backtrack if needed
    - Autonomous quality judgments, not just classification

    This differs from Tier 4 (multi-agent) because:
    - Single agent handles entire workflow
    - No specialization into separate researcher/analyst/curator agents
    - Self-contained decision-making

    Use Cases:
    - "Find tutorials on Niagara particle systems"
    - "Curate learning path for C++ gameplay programming"
    - "Best tutorials for procedural material creation"
    - "Learn UE5 Enhanced Input system"

    Cost: ~$0.20-0.40 per topic (GPT-4 + web searches)
    Time: 3-6 minutes per topic
    Output: Curated learning path with 5-8 quality tutorials
    """
