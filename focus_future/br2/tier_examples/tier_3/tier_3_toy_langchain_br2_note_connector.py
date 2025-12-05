#!/usr/bin/env python3
"""
BR2 - Tier 3 - Smart Note Connector (LangChain Agent)

TIER 3 CHARACTERISTICS:
- Single agent with tool calling capabilities
- Agent searches for related notes using multiple methods
- Autonomous decision-making about which connections to make
- Synthesizes connections into knowledge graph

What It Does:
Given a note or topic, finds related notes in your Obsidian vault using
semantic search, tag search, and content search. Creates bi-directional links.

Tier Contrast:
- Tier 2: Would use ONE AI call to suggest related topics
- Tier 3: Agent uses MULTIPLE tools to find actual related notes
- Tier 4: ResearchAgent → SynthesisAgent → LinkingAgent (multi-agent)
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
# ============================================================================

def obsidian_search_tool(query: str) -> str:
    """
    TIER 3 TOOL: Search Obsidian vault by content

    In production: call Obsidian Local REST API or Dataview plugin
    Toy example: simulated note search
    """
    print(f"📝 [OBSIDIAN_SEARCH] Searching vault for: {query}")

    # Simulated search results
    if "productivity" in query.lower():
        return """
        Found 5 notes matching 'productivity':

        1. "GTD System Implementation.md" (Projects/)
           Last modified: 2025-11-15
           Preview: "Getting Things Done methodology with weekly review process..."

        2. "Time Blocking Techniques.md" (Resources/productivity-tools/)
           Last modified: 2025-11-10
           Preview: "Deep work sessions using Pomodoro and time blocking..."

        3. "PARA Method Overview.md" (Areas/knowledge-management/)
           Last modified: 2025-11-12
           Preview: "Projects, Areas, Resources, Archives organizational framework..."

        4. "Weekly Review Template.md" (Projects/)
           Last modified: 2025-11-14
           Preview: "Review all projects, clear inbox, plan next week..."

        5. "Productivity Apps Comparison.md" (Resources/)
           Last modified: 2025-11-08
           Preview: "Comparison of Todoist, Things, OmniFocus for task management..."
        """
    elif "unreal" in query.lower() or "ue5" in query.lower():
        return """
        Found 3 notes matching 'unreal engine':

        1. "UE5 Learning Path.md" (Projects/game-dev/)
           Preview: "Comprehensive learning roadmap for Unreal Engine 5..."

        2. "Niagara VFX Notes.md" (Resources/game-dev/)
           Preview: "Notes from Niagara particle system tutorials..."

        3. "Blueprint Best Practices.md" (Resources/game-dev/)
           Preview: "Performance optimization tips for Blueprint scripts..."
        """
    else:
        return f"Found 0 notes matching '{query}'. Try different search terms."


def semantic_search_tool(concept: str) -> str:
    """
    TIER 3 TOOL: Semantic search using embeddings

    In production: use vector database (Pinecone, Weaviate, local embeddings)
    Toy example: simulated semantic matches
    """
    print(f"🧠 [SEMANTIC_SEARCH] Finding semantically similar notes to: {concept}")

    # Simulated semantic matches
    return f"""
    Semantically similar notes to '{concept}':

    1. [85% match] "Knowledge Management Systems.md"
       Why: Both discuss organizing and retrieving information effectively

    2. [78% match] "Building a Second Brain Overview.md"
       Why: Related concept of personal knowledge management (PKM)

    3. [72% match] "Zettelkasten Method.md"
       Why: Similar note-taking and linking methodology

    4. [65% match] "Progressive Summarization Technique.md"
       Why: Related information processing workflow

    5. [58% match] "Evergreen Notes Principles.md"
       Why: Shared emphasis on atomic, reusable knowledge units
    """


def tag_search_tool(tags: str) -> str:
    """
    TIER 3 TOOL: Search notes by tags

    In production: query Obsidian's tag index or Dataview
    Toy example: simulated tag results
    """
    print(f"🏷️  [TAG_SEARCH] Finding notes with tags: {tags}")

    tag_list = [t.strip() for t in tags.split(',')]

    # Simulated tag matches
    return f"""
    Notes tagged with {', '.join(tag_list)}:

    1. "Daily Note - 2025-11-15.md"
       Tags: #daily-note #productivity #review
       Preview: "Completed GTD weekly review, planned next week's priorities..."

    2. "PARA Setup Guide.md"
       Tags: #productivity #knowledge-management #obsidian
       Preview: "Step-by-step guide to implementing PARA in Obsidian..."

    3. "Atomic Habits Summary.md"
       Tags: #productivity #books #habits
       Preview: "Key takeaways from James Clear's Atomic Habits..."

    Found {len(tag_list) * 3} notes total across all tags.
    """


# ============================================================================
# TIER 3 CHARACTERISTIC: Tool Setup
# ============================================================================

tools = [
    Tool(
        name="obsidian_search",
        description="Search your Obsidian vault by content/keywords. Returns note titles, "
                    "paths, and previews. Use this to find notes about specific topics. "
                    "Input should be a search query.",
        func=obsidian_search_tool
    ),
    Tool(
        name="semantic_search",
        description="Find notes semantically similar to a concept using AI embeddings. "
                    "Returns similarity scores and reasons for matches. Use this to find "
                    "conceptually related notes even if they don't share exact keywords. "
                    "Input should be a concept or topic.",
        func=semantic_search_tool
    ),
    Tool(
        name="tag_search",
        description="Search notes by tags. Returns all notes with specified tags. "
                    "Use this to find notes in specific categories. "
                    "Input should be comma-separated tags (e.g., 'productivity,obsidian').",
        func=tag_search_tool
    )
]


# ============================================================================
# TIER 3 CHARACTERISTIC: Agent Prompt
# ============================================================================

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a knowledge connection agent that finds related notes in an Obsidian vault.

Your goal: Given a note or topic, find all relevant related notes and suggest bi-directional links.

TIER 3 REASONING APPROACH:
1. Understand the main topic/concept
2. Search for direct keyword matches
3. Find semantically similar notes
4. Look for notes with related tags
5. Synthesize findings into connection recommendations

You have access to these tools:
- obsidian_search: Keyword/content search
- semantic_search: Find conceptually similar notes
- tag_search: Find notes by category tags

Think step-by-step about what connections would be most valuable. When done, provide:
- List of related notes with brief explanations
- Suggested bi-directional links to create
- Why each connection strengthens the knowledge graph

Be thorough but focused on high-value connections."""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])


# ============================================================================
# TIER 3 CHARACTERISTIC: Agent Creation & Execution
# ============================================================================

def create_note_connector_agent():
    """Create the note connector agent"""
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


def find_related_notes(note_title: str, note_content: str = "") -> Dict[str, Any]:
    """
    Main function: Find related notes and suggest connections

    TIER 3 CHARACTERISTIC: Agent autonomously searches multiple ways
    """
    print(f"\n{'='*60}")
    print(f"🔗 TIER 3 AGENT: Finding connections for '{note_title}'")
    print(f"{'='*60}\n")

    agent = create_note_connector_agent()

    try:
        result = agent.invoke({
            "input": f"Find related notes and suggest connections for: '{note_title}'\n\n"
                     f"Note content: {note_content if note_content else 'Not provided - use title only'}"
        })

        print(f"\n{'='*60}")
        print(f"✅ AGENT COMPLETE")
        print(f"{'='*60}\n")

        return {
            "success": True,
            "note": note_title,
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
    """Example usage of the note connector agent"""

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found")
        sys.exit(1)

    # Example 1: Connect productivity note
    print("\n" + "="*60)
    print("EXAMPLE 1: Find connections for productivity note")
    print("="*60)

    result1 = find_related_notes(
        "Daily Review Process.md",
        "My daily review process includes inbox processing, task prioritization, and reflection."
    )

    if result1["success"]:
        print("\n🔗 SUGGESTED CONNECTIONS:")
        print(result1["output"])

    # Example 2: Connect UE5 learning note
    print("\n" + "="*60)
    print("EXAMPLE 2: Find connections for UE5 learning note")
    print("="*60)

    result2 = find_related_notes(
        "Unreal Engine 5 Niagara Tutorial Notes.md",
        "Learning Niagara particle systems for VFX effects in my game project."
    )

    if result2["success"]:
        print("\n🔗 SUGGESTED CONNECTIONS:")
        print(result2["output"])

    # Show tier characteristics
    print("\n" + "="*60)
    print("🎓 WHY THIS IS TIER 3:")
    print("="*60)
    print("""
    1. Single Agent: One agent finds all connections
    2. Multiple Tools: obsidian_search, semantic_search, tag_search
    3. Autonomous Search Strategy: Agent decides which tools to use
    4. Multi-Method Discovery: Combines keyword, semantic, and tag searches
    5. Synthesis: Combines findings into coherent connection recommendations

    Contrast with other tiers:
    - Tier 2: ONE AI call suggests related topics (no actual vault search)
    - Tier 3: Agent actively searches vault using multiple methods
    - Tier 4: ResearchAgent → SynthesisAgent → LinkingAgent (multi-agent workflow)
    - Tier 5: Claude Code orchestrates: Agent finds → Human reviews → Auto-links
    - Tier 6: Autonomous system learns connection patterns, improves over time
    """)


if __name__ == "__main__":
    main()
