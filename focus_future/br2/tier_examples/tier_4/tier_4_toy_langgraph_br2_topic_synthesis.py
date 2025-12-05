#!/usr/bin/env python3
"""
BR2 - Tier 4 - Multi-Agent Topic Synthesis (LangGraph)

TIER 4: ResearchAgent → SynthesisAgent coordination
- ResearchAgent: Gathers related notes on topic
- SynthesisAgent: Synthesizes into comprehensive summary note
"""

import os
import sys
from typing import TypedDict, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END

load_dotenv()


class TopicSynthesisState(TypedDict):
    """Shared state between agents"""
    topic: str
    vault_path: str

    # ResearchAgent outputs
    research_complete: bool
    related_notes: List[str]
    key_concepts: List[str]
    connections: List[str]

    # SynthesisAgent outputs
    synthesis_complete: bool
    summary_note: str
    recommended_links: List[str]

    current_agent: str


def research_agent(state: TopicSynthesisState) -> TopicSynthesisState:
    """
    ResearchAgent: Finds all related notes on topic

    TIER 4: Specialized agent for research
    """
    print(f"\n🔍 RESEARCH AGENT: Gathering notes on '{state['topic']}'")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    research_prompt = f"""
    Research the topic: {state['topic']}

    Find:
    1. Related notes that should be included
    2. Key concepts to cover
    3. Connections between ideas

    Provide a research summary.
    """

    response = llm.invoke([
        SystemMessage(content="You are a knowledge researcher finding connections in a note vault."),
        HumanMessage(content=research_prompt)
    ]).content

    # Simulated research results
    related_notes = [
        "PARA Method Overview.md",
        "Zettelkasten Principles.md",
        "Building a Second Brain.md",
        "Progressive Summarization.md"
    ]

    key_concepts = [
        "Organize notes by actionability",
        "Atomic note principle",
        "Progressive refinement",
        "Bi-directional linking"
    ]

    connections = [
        "PARA and Zettelkasten complement each other",
        "Progressive summarization enables retrieval",
        "Second Brain requires consistent review"
    ]

    print(f"✅ Found {len(related_notes)} related notes")
    print(f"📊 Identified {len(key_concepts)} key concepts\n")

    state["research_complete"] = True
    state["related_notes"] = related_notes
    state["key_concepts"] = key_concepts
    state["connections"] = connections
    state["current_agent"] = "synthesis"

    return state


def synthesis_agent(state: TopicSynthesisState) -> TopicSynthesisState:
    """
    SynthesisAgent: Creates comprehensive summary note

    TIER 4: Specialized agent for synthesis
    """
    print(f"\n✍️  SYNTHESIS AGENT: Creating summary note")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    synthesis_prompt = f"""
    Create a comprehensive summary note on: {state['topic']}

    Based on research:
    Related Notes: {', '.join(state['related_notes'])}
    Key Concepts: {', '.join(state['key_concepts'])}
    Connections: {', '.join(state['connections'])}

    Create a well-structured Markdown note that:
    1. Synthesizes key ideas from all sources
    2. Shows connections between concepts
    3. Includes [[wikilinks]] to related notes
    4. Provides actionable takeaways

    Format as Obsidian note.
    """

    summary_note = llm.invoke([
        SystemMessage(content="You are a knowledge synthesis expert creating comprehensive notes."),
        HumanMessage(content=synthesis_prompt)
    ]).content

    recommended_links = state['related_notes']

    print(f"✅ Summary note created")
    print(f"🔗 {len(recommended_links)} links recommended\n")

    state["synthesis_complete"] = True
    state["summary_note"] = summary_note
    state["recommended_links"] = recommended_links
    state["current_agent"] = "complete"

    return state


def create_synthesis_workflow():
    """Create LangGraph workflow for topic synthesis"""
    workflow = StateGraph(TopicSynthesisState)

    workflow.add_node("research", research_agent)
    workflow.add_node("synthesis", synthesis_agent)

    workflow.set_entry_point("research")
    workflow.add_edge("research", "synthesis")
    workflow.add_edge("synthesis", END)

    return workflow.compile()


def synthesize_topic(topic: str, vault_path: str = "./vault"):
    """Synthesize comprehensive note on topic"""
    print(f"\n{'='*60}")
    print(f"🎯 TIER 4 MULTI-AGENT: Topic Synthesis")
    print(f"Topic: {topic}")
    print(f"{'='*60}\n")

    app = create_synthesis_workflow()

    initial_state = {
        "topic": topic,
        "vault_path": vault_path,
        "research_complete": False,
        "related_notes": [],
        "key_concepts": [],
        "connections": [],
        "synthesis_complete": False,
        "summary_note": "",
        "recommended_links": [],
        "current_agent": "research"
    }

    final_state = app.invoke(initial_state)

    print(f"\n{'='*60}")
    print(f"SYNTHESIZED NOTE")
    print(f"{'='*60}\n")
    print(final_state['summary_note'])
    print(f"\n{'='*60}\n")

    return final_state


def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found")
        sys.exit(1)

    synthesize_topic("Personal Knowledge Management Systems")

    print("\n🎓 WHY THIS IS TIER 4:")
    print("""
    - ResearchAgent → SynthesisAgent coordination
    - Research findings feed into synthesis
    - State management between agents
    - Specialized responsibilities
    """)


if __name__ == "__main__":
    main()
