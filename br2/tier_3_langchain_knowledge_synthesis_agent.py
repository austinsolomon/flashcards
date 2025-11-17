"""
BR2 - Tier 3: Single-Purpose Agent - Knowledge Synthesis Agent

Use Case: Given a research question or topic, autonomously search your Second Brain vault,
external sources, and synthesize a comprehensive permanent note with connections.

Tool Used: LangChain with RAG, web search, and note generation tools
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA


# ============================================================================
# CONFIGURATION
# ============================================================================

VAULT_PATH = os.path.expanduser("~/Library/Mobile Documents/iCloud~md~obsidian/Documents/MyVault")
VECTOR_DB_PATH = "./chroma_db"


# ============================================================================
# CUSTOM TOOLS
# ============================================================================

def search_vault(query: str) -> str:
    """
    Search the Obsidian vault using semantic search (RAG).
    """
    try:
        # Load or create vector database
        embeddings = OpenAIEmbeddings()

        if os.path.exists(VECTOR_DB_PATH):
            vectorstore = Chroma(
                persist_directory=VECTOR_DB_PATH,
                embedding_function=embeddings
            )
        else:
            # First time: index the vault
            print(f"Indexing vault at {VAULT_PATH}...")
            loader = DirectoryLoader(
                VAULT_PATH,
                glob="**/*.md",
                loader_cls=TextLoader,
                show_progress=True
            )
            documents = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)

            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=embeddings,
                persist_directory=VECTOR_DB_PATH
            )

        # Search
        docs = vectorstore.similarity_search(query, k=5)

        # Format results
        results = []
        for doc in docs:
            source = doc.metadata.get('source', 'unknown')
            # Extract note title from path
            note_name = Path(source).stem
            results.append(f"**{note_name}**:\n{doc.page_content}\n")

        return "\n\n---\n\n".join(results) if results else "No relevant notes found in vault."

    except Exception as e:
        return f"Error searching vault: {str(e)}"


def search_web_sources(query: str) -> str:
    """
    Search the web for external information to supplement vault knowledge.
    """
    search = DuckDuckGoSearchRun()
    results = search.run(f"{query} research article academic")
    return results


def extract_note_connections(topic: str, vault_content: str) -> List[str]:
    """
    Identify related concepts that should be linked to other notes.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"""Analyze this content about '{topic}' and identify concepts that likely have dedicated notes in a Second Brain vault.

Content:
{vault_content[:2000]}

Return a JSON array of concept names that should be wikilinked:
["concept1", "concept2", "concept3"]

Focus on:
- Proper nouns (people, places, theories)
- Technical terms
- Related frameworks or methodologies
- Cross-referenced topics
"""

    response = llm.invoke(prompt)

    try:
        import re
        json_match = re.search(r'\[.*\]', response.content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass

    return []


def generate_permanent_note(topic: str, synthesis_data: Dict[str, Any]) -> str:
    """
    Create a permanent note in Zettelkasten/PARA format.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

    prompt = f"""Create a comprehensive permanent note for a Second Brain on: {topic}

Source Material:
{json.dumps(synthesis_data, indent=2)}

Generate a well-structured permanent note following these principles:
1. Atomic: Focused on one core idea
2. Concept-oriented: Expresses a complete thought
3. Connected: References related concepts
4. In your own words: Synthesized, not copied

Structure:
- Clear title expressing the core concept
- Opening paragraph stating the main insight
- Detailed explanation with examples
- Connections to related concepts
- Questions for further exploration
- Sources cited

Format in Obsidian markdown with:
- YAML frontmatter (tags, date, note_type: permanent)
- Wikilinks [[Like This]] for connections
- Clear hierarchical sections
- Inline citations where appropriate
"""

    response = llm.invoke(prompt)
    return response.content


def save_permanent_note(filename: str, content: str) -> str:
    """
    Save the generated permanent note to the vault.
    """
    # Determine save location (Resources folder for permanent notes)
    save_dir = os.path.join(VAULT_PATH, "Resources", "Permanent Notes")
    os.makedirs(save_dir, exist_ok=True)

    filepath = os.path.join(save_dir, f"{filename}.md")

    with open(filepath, 'w') as f:
        f.write(content)

    return f"Permanent note saved to: {filepath}"


# ============================================================================
# AGENT SETUP
# ============================================================================

def create_knowledge_synthesis_agent():
    """Create an agent specialized in synthesizing knowledge from multiple sources."""

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    tools = [
        Tool(
            name="search_vault",
            func=search_vault,
            description="Search your Obsidian vault using semantic search. Returns relevant excerpts from existing notes. Use this first to find what you already know."
        ),
        Tool(
            name="search_web",
            func=search_web_sources,
            description="Search the web for external information. Use this to supplement gaps in vault knowledge or get fresh perspectives."
        ),
        Tool(
            name="extract_connections",
            func=extract_note_connections,
            description="Identify concepts in the content that should link to other notes. Provide topic and content as input."
        ),
        Tool(
            name="generate_note",
            func=generate_permanent_note,
            description="Generate a permanent note from synthesized research. Provide topic and all gathered data."
        ),
        Tool(
            name="save_note",
            func=save_permanent_note,
            description="Save the generated permanent note to the vault. Provide filename (without .md) and note content."
        )
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a knowledge synthesis agent for a Second Brain / Zettelkasten system.

Your task is to research a topic and create a high-quality permanent note following these principles:
- **Atomic**: One core idea per note
- **Concept-oriented**: Express a complete, standalone thought
- **Connected**: Link to related concepts in the vault
- **Synthesized**: Combine multiple sources into original understanding

Research process:
1. Search the vault to see what's already known about this topic
2. Identify gaps in current knowledge
3. Search external sources to fill gaps and add perspectives
4. Synthesize all information into a coherent understanding
5. Extract concepts that should link to other notes
6. Generate a permanent note in Zettelkasten format
7. Save to the Resources/Permanent Notes folder

Quality criteria for permanent notes:
- States a clear, specific insight (not just a topic)
- Written in your own words, not copied from sources
- Includes concrete examples or applications
- Makes connections to related concepts explicit
- Raises questions for further exploration
- Properly cites sources

The note should be immediately useful for future thinking and writing."""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=12,
        handle_parsing_errors=True
    )

    return agent_executor


# ============================================================================
# EXECUTION
# ============================================================================

def synthesize_knowledge(topic: str, specific_question: str = None) -> Dict[str, Any]:
    """
    Main function to research and synthesize knowledge into a permanent note.

    Args:
        topic: The topic or concept to research
        specific_question: Optional specific angle or question to explore

    Returns:
        Dictionary containing synthesis results and file path
    """
    print(f"\n{'='*60}")
    print(f"Synthesizing knowledge on: {topic}")
    if specific_question:
        print(f"Focus question: {specific_question}")
    print(f"{'='*60}\n")

    agent = create_knowledge_synthesis_agent()

    query = f"Research and create a permanent note on: {topic}"
    if specific_question:
        query += f"\n\nSpecific question to address: {specific_question}"

    query += "\n\nFollow the full research process: search vault, identify gaps, search external sources, synthesize, extract connections, generate note, and save."

    result = agent.invoke({"input": query})

    print(f"\n{'='*60}")
    print("Knowledge synthesis complete!")
    print(f"{'='*60}\n")

    return result


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    How to Run:

    1. Install dependencies:
       pip install langchain langchain-openai langchain-community duckduckgo-search chromadb tiktoken

    2. Set environment variable:
       export OPENAI_API_KEY='your-api-key-here'

    3. Update VAULT_PATH to point to your Obsidian vault

    4. Run the script:
       python tier_3_langchain_knowledge_synthesis_agent.py

    Expected Output:
    - Semantic search through your vault
    - Web research for additional context
    - A permanent note created and saved to your vault
    - Console showing agent's research and synthesis process
    """

    # Example: Synthesize knowledge on a topic
    topic = "Spaced Repetition for Skill Development"
    specific_question = "How can spaced repetition be applied to learning code patterns, not just facts?"

    result = synthesize_knowledge(topic, specific_question)

    print("\n" + "="*60)
    print("AGENT OUTPUT:")
    print("="*60)
    print(result['output'])

    # Example permanent note that would be created:
    example_note = """---
date: 2025-01-15
tags: [learning, spaced-repetition, deliberate-practice, coding]
note_type: permanent
related: [[Learning Techniques]], [[Deliberate Practice]], [[Code Patterns]]
---

# Spaced Repetition Extends Beyond Facts to Procedural Skills

The traditional view of spaced repetition confines it to declarative memory (facts, vocabulary, formulas). However, research in motor learning and expertise development shows that **spaced practice enhances procedural memory and skill acquisition** when structured appropriately.

## Core Insight

Spaced repetition for skills differs from factual memorization in three key ways:
1. **Active reconstruction**: Rather than passive recall, you must actively reproduce the skill from scratch
2. **Varied contexts**: Each repetition should vary the problem context to prevent rote pattern matching
3. **Increasing complexity**: Later repetitions should introduce variations and edge cases

## Application to Code Patterns

For learning design patterns and programming techniques:

**Instead of flashcards like:**
> Q: What is the Observer pattern?
> A: A behavioral pattern where objects subscribe to state changes...

**Use spaced coding challenges:**
> Week 1: Implement Observer pattern for a simple weather app
> Week 2: Extend it to handle multiple subscriber types with filtering
> Week 4: Refactor a legacy polling system to use Observer pattern
> Week 8: Compare Observer vs. Event Bus for your current project

Each iteration requires reconstructing the pattern from memory while applying it in increasingly complex contexts.

## Evidence and Sources

- [[Bjork 1994]] - Desirable difficulties and optimal learning
- [[Karpicke 2008]] - Retrieval practice produces more learning than elaborative studying
- Motor learning research shows spaced practice beats massed practice for skill retention (see [[Schmidt & Lee Motor Learning]])

## Connections

- Related to [[Deliberate Practice]] - both require effortful reconstruction
- Supports [[Learn by Building]] - each repetition is a small project
- Contrasts with [[Tutorial Hell]] - passive watching without retrieval

## Questions for Further Exploration

- What is the optimal spacing interval for procedural skills vs facts?
- How to balance exact repetition (for muscle memory) with variation (for transfer)?
- Can we apply this to learning AI/LLM tool use patterns?

## Implementation in My System

Create a separate Anki deck for "Code Pattern Practice" with:
- Challenge cards (not solution cards)
- Links to small, self-contained repos for each repetition
- Increasing complexity tags to schedule variants

---

*Sources: Bjork (1994), Karpicke (2008), Make It Stick (Brown et al.), personal experimentation*
"""

    print("\n" + "="*60)
    print("EXAMPLE PERMANENT NOTE:")
    print("="*60)
    print(example_note)

    """
    Tier Classification Reasoning:

    This is Tier 3 (Single-Purpose Agent) because:

    1. **Autonomous research workflow**: Searches vault → identifies gaps → searches web → synthesizes
    2. **Tool orchestration**: Decides which tools to use based on what it finds (or doesn't find)
    3. **RAG-based retrieval**: Uses semantic search, not simple keyword matching
    4. **Quality assessment**: Evaluates whether vault knowledge is sufficient or external search needed
    5. **Synthesis capability**: Combines multiple sources into original permanent note
    6. **Focused purpose**: Does one thing (knowledge synthesis) with deep capability

    This differs from Tier 2 (n8n + LLM) because:
    - Agent controls research flow dynamically
    - Makes autonomous decisions about when to search externally
    - RAG system provides semantic understanding of vault content
    - Creates genuinely new synthesized content, not just categorizing existing notes

    This differs from Tier 4 (multi-agent) because:
    - Single agent handles entire workflow
    - No separate researcher/writer/editor agents
    - Self-contained decision-making and execution

    Use Cases:
    - "Research and synthesize: Mental models for decision-making"
    - "Create permanent note on: Second-order thinking"
    - "Synthesize what I know about: Building AI agents + gaps to research"

    This is the "research assistant" tier - capable enough to produce publication-quality
    synthesis notes autonomously, but still focused on a single purpose.

    Cost: ~$0.30-0.60 per synthesis (GPT-4 + embeddings + web search)
    Time: 4-7 minutes per topic
    Output: Publication-ready permanent note with connections
    """
