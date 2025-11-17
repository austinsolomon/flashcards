#!/usr/bin/env python3
"""
BR2 - Tier 3 - Note Connection Finder Agent (LangChain)

TIER 3 CHARACTERISTICS:
- Single agent with semantic search capabilities
- Tools for vector search, concept extraction, graph analysis
- Autonomous linking based on conceptual relationships
- Builds knowledge graph connections

What It Does:
Given a new note, finds related notes in your Obsidian vault using
semantic similarity, concept matching, and context analysis. Automatically
creates bidirectional links to build your knowledge graph.
"""

import os
import json
from typing import List, Dict
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_community.vectorstores import Chroma

load_dotenv()

# ============================================================================
# TIER 3 TOOLS: Knowledge Graph Tools
# ============================================================================

# Initialize embeddings
embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

def obsidian_semantic_search(query: str, vault_path: str = "/vault") -> str:
    """
    Search Obsidian vault using semantic similarity

    Production: Use vector DB (Chroma, Pinecone, or Weaviate)
    with embeddings of all notes
    """

    # Simulated search results
    results = [
        {
            "note_title": "Automation Architecture Overview",
            "similarity": 0.92,
            "excerpt": "Multi-tier automation framework from simple workflows to autonomous agents...",
            "path": "/vault/Projects/Automation/architecture.md"
        },
        {
            "note_title": "LangChain Agent Patterns",
            "similarity": 0.87,
            "excerpt": "Tool-calling agents can autonomously decide which tools to use...",
            "path": "/vault/Resources/Technical/langchain_patterns.md"
        },
        {
            "note_title": "Knowledge Management Systems",
            "similarity": 0.81,
            "excerpt": "PARA method organizes notes into Projects, Areas, Resources, Archive...",
            "path": "/vault/Areas/PKM/knowledge_systems.md"
        }
    ]

    return json.dumps(results)


def concept_extractor(note_content: str) -> str:
    """Extract key concepts from note content"""

    # Production: Use NER, topic modeling, or LLM extraction
    # Simulated concept extraction
    concepts = {
        "main_topics": ["automation", "agent systems", "knowledge management"],
        "entities": ["LangChain", "n8n", "Obsidian"],
        "key_phrases": ["tier architecture", "procedural generation", "semantic linking"],
        "question_marks": ["How to scale agent systems?", "When to use Tier 4 vs Tier 5?"]
    }

    return json.dumps(concepts)


def backlink_analyzer(note_path: str, vault_path: str = "/vault") -> str:
    """
    Analyze existing backlinks to suggest new connections

    Production: Parse all .md files to find existing [[wikilinks]]
    """

    # Simulated backlink analysis
    analysis = {
        "existing_backlinks": [
            {"from": "/vault/Projects/GTM_Automation.md", "context": "Discusses tier architecture"},
            {"from": "/vault/Resources/Tools/n8n.md", "context": "References workflow patterns"}
        ],
        "suggested_links": [
            {
                "note": "/vault/Areas/Learning/AI_Agents.md",
                "reason": "Related discussion of agent architectures",
                "confidence": 0.85
            },
            {
                "note": "/vault/Projects/UE5_Pipeline.md",
                "reason": "Similar automation patterns in different domain",
                "confidence": 0.72
            }
        ],
        "orphan_notes": []  # Notes with no links (should be connected)
    }

    return json.dumps(analysis)


def link_validator(proposed_links: str) -> str:
    """Validate that proposed links make semantic sense"""

    try:
        links = json.loads(proposed_links)

        validated = []
        for link in links:
            # Check confidence threshold
            if link.get("confidence", 0) > 0.7:
                validated.append({
                    "target": link["target"],
                    "reason": link["reason"],
                    "link_type": link.get("type", "related"),
                    "validated": True
                })

        return json.dumps({"validated_links": validated})

    except Exception as e:
        return json.dumps({"error": str(e)})


# ============================================================================
# TIER 3 AGENT
# ============================================================================

tools = [
    Tool(
        name="obsidian_semantic_search",
        description="Search vault for semantically similar notes. Input: search query based on note content",
        func=lambda x: obsidian_semantic_search(x, os.getenv("OBSIDIAN_VAULT_PATH", "/vault"))
    ),
    Tool(
        name="concept_extractor",
        description="Extract key concepts, entities, and topics from note content. Input: note text",
        func=concept_extractor
    ),
    Tool(
        name="backlink_analyzer",
        description="Analyze existing backlinks and suggest new connections. Input: note file path",
        func=lambda x: backlink_analyzer(x, os.getenv("OBSIDIAN_VAULT_PATH", "/vault"))
    ),
    Tool(
        name="link_validator",
        description="Validate proposed links for relevance. Input: JSON array of proposed links",
        func=link_validator
    )
]

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a knowledge graph curator for a personal knowledge management system.

Your job: Find semantically related notes and create meaningful connections.

PROCESS:
1. Extract key concepts from the new note
2. Search vault for semantically similar notes
3. Analyze existing backlink patterns
4. Propose new bidirectional links with reasoning
5. Validate links to ensure quality

OUTPUT: List of notes to link with [[wikilink]] syntax and placement context."""),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])


def create_connection_finder_agent():
    """Create note connection finder agent"""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    agent = create_openai_tools_agent(llm, tools, agent_prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=10)


def find_note_connections(note_path: str, note_content: str) -> Dict:
    """
    Main function: Find connections for a note

    Returns:
        {
            "suggested_links": [
                {
                    "target_note": "path/to/note.md",
                    "link_text": "[[Note Title]]",
                    "insert_after": "paragraph discussing X",
                    "reason": "Both discuss automation patterns",
                    "confidence": 0.89
                }
            ]
        }
    """
    agent = create_connection_finder_agent()

    query = f"Find related notes to connect with this new note:\n\nPath: {note_path}\n\nContent:\n{note_content[:1000]}"

    result = agent.invoke({"input": query})

    # Parse agent output
    # Production: Extract structured linking recommendations

    return {
        "note_path": note_path,
        "connections_found": True,
        "suggested_links": [
            {
                "target_note": "/vault/Projects/Automation_Architecture.md",
                "link_text": "[[Automation Architecture]]",
                "insert_after": "discussing tier systems",
                "reason": "Related architectural concepts",
                "confidence": 0.92
            }
        ],
        "agent_reasoning": result["output"]
    }


# FastAPI endpoint for production deployment
if __name__ == "__main__":
    result = find_note_connections(
        "/vault/00_Inbox/new_note_20251117.md",
        "Thinking about how to scale agent systems for production use..."
    )

    print(json.dumps(result, indent=2))
