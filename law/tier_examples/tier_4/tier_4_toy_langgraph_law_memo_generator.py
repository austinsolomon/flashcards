#!/usr/bin/env python3
"""
Law - Tier 4 - Multi-Agent Legal Memo Generator (LangGraph)

## What Is Available Today

**Current Legal Memo Writing**:
- Attorney researches cases (2-4 hours)
- Attorney outlines memo (30-60 min)
- Attorney writes full memo (2-6 hours)
- Senior attorney reviews (1-2 hours)
- Total: 6-13 hours @ $200-600/hour = $1,200-7,800 per memo

**AI Tools Available (2025)**:
- **Harvey AI** ($enterprise): Draft generation for big law
- **CaseText CoCounsel** ($500/month): Research assistance
- **Manual ChatGPT/Claude**: Some attorneys use (ethics concerns)

## How AI Could Improve It

**Tier 4 (Available Today - Multi-Agent)**:
- **ResearchAgent**: Finds relevant cases (1-2 min)
- **OutlineAgent**: Creates memo structure (30 sec)
- **DraftAgent**: Writes full memo (2-3 min)
- **CitationAgent**: Validates all citations (1 min)
- Total: ~5 minutes AI time + 30-60 min attorney review/editing
- Cost: $2-5 (AI) + $100-300 (attorney time) = $102-305
- **Savings: 85-95%**

**Why Multi-Agent (Tier 4)**:
- Specialization: Each agent focuses on one task
- Quality: Separate citation validation catches errors
- Coordination: Agents pass state (research → outline → draft)

---

TIER 4 CHARACTERISTICS:
- Multiple specialized agents (not single agent like Tier 3)
- Agent coordination via LangGraph state
- Sequential workflow: ResearchAgent → OutlineAgent → DraftAgent
- Each agent has distinct responsibility
"""

import os
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# TIER 4: Define Shared State (flows between agents)
# ============================================================================

class MemoState(TypedDict):
    """Shared state that flows between agents"""
    legal_question: str
    research_findings: List[dict]
    outline: str
    draft_memo: str
    validated_citations: List[str]
    status: str


# ============================================================================
# TIER 4 AGENTS: Each agent is a specialized function
# ============================================================================

def research_agent(state: MemoState) -> MemoState:
    """
    Agent 1: Research relevant case law

    In production: Would use LangChain agent with tools (web search, citation lookup)
    This example: Simulated research
    """
    print("\n🔍 RESEARCH AGENT: Finding relevant case law...")

    question = state["legal_question"]

    # Simulated research (in production, would call research tools)
    if "summary judgment" in question.lower():
        findings = [
            {
                "case": "Celotex Corp. v. Catrett, 477 U.S. 317 (1986)",
                "holding": "Moving party must show absence of genuine issue of material fact",
                "relevance": "Standard for summary judgment"
            },
            {
                "case": "Anderson v. Liberty Lobby, Inc., 477 U.S. 242 (1986)",
                "holding": "Nonmoving party must show sufficient evidence for reasonable jury",
                "relevance": "Burden on nonmoving party"
            }
        ]
    else:
        findings = [
            {"case": "Relevant case 1", "holding": "Example holding", "relevance": "On point"},
            {"case": "Relevant case 2", "holding": "Example holding", "relevance": "Persuasive"}
        ]

    print(f"   Found {len(findings)} relevant cases")

    return {
        **state,
        "research_findings": findings,
        "status": "research_complete"
    }


def outline_agent(state: MemoState) -> MemoState:
    """
    Agent 2: Create memo outline based on research

    Uses LLM to structure findings into logical outline
    """
    print("\n📝 OUTLINE AGENT: Creating memo structure...")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Build outline prompt
    research_summary = "\n".join([
        f"- {f['case']}: {f['holding']}"
        for f in state["research_findings"]
    ])

    prompt = f"""You are a legal memo outline generator. Create a structured outline for a legal memo.

Question: {state['legal_question']}

Research Findings:
{research_summary}

Create an outline with sections:
I. Question Presented
II. Brief Answer
III. Facts (if applicable)
IV. Analysis
V. Conclusion

Format as clear outline with headings."""

    response = llm.invoke([HumanMessage(content=prompt)])
    outline = response.content

    print(f"   Generated outline with {len(outline.split('\\n'))} sections")

    return {
        **state,
        "outline": outline,
        "status": "outline_complete"
    }


def draft_agent(state: MemoState) -> MemoState:
    """
    Agent 3: Write full memo based on outline and research

    Uses LLM to expand outline into complete memo
    """
    print("\n✍️ DRAFT AGENT: Writing full memo...")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Build drafting prompt
    research_detail = "\n\n".join([
        f"**{f['case']}**\nHolding: {f['holding']}\nRelevance: {f['relevance']}"
        for f in state["research_findings"]
    ])

    prompt = f"""You are a legal memo writer. Write a complete legal memo following this outline.

OUTLINE:
{state['outline']}

RESEARCH FINDINGS:
{research_detail}

ORIGINAL QUESTION:
{state['legal_question']}

Write a professional legal memo with:
- Clear headings matching outline
- Well-reasoned analysis citing cases
- Proper legal citation format
- Professional tone appropriate for attorney audience

IMPORTANT: Include [ATTORNEY REVIEW REQUIRED] disclaimer at top."""

    response = llm.invoke([HumanMessage(content=prompt)])
    memo = response.content

    print(f"   Generated memo: {len(memo)} characters")

    return {
        **state,
        "draft_memo": memo,
        "status": "draft_complete"
    }


def citation_agent(state: MemoState) -> MemoState:
    """
    Agent 4: Validate all citations in memo

    Extracts citations and checks they're properly formatted
    """
    print("\n📚 CITATION AGENT: Validating citations...")

    memo = state["draft_memo"]

    # Extract citations (simplified - would use regex or NER in production)
    import re
    citations = re.findall(r'\d+ U\.S\. \d+|\d+ F\.\d+d \d+', memo)

    print(f"   Found {len(citations)} citations to validate")

    # In production, would validate each citation via Shepard's/KeyCite
    validated = [f"{cite} - [VERIFY VIA WESTLAW/LEXIS]" for cite in citations]

    return {
        **state,
        "validated_citations": validated,
        "status": "complete"
    }


# ============================================================================
# TIER 4: LangGraph Workflow - Coordinates Agents
# ============================================================================

def create_memo_workflow():
    """Create multi-agent workflow graph"""

    workflow = StateGraph(MemoState)

    # Add agent nodes
    workflow.add_node("research", research_agent)
    workflow.add_node("outline", outline_agent)
    workflow.add_node("draft", draft_agent)
    workflow.add_node("citation", citation_agent)

    # Define sequential flow: research → outline → draft → citation
    workflow.set_entry_point("research")
    workflow.add_edge("research", "outline")
    workflow.add_edge("outline", "draft")
    workflow.add_edge("draft", "citation")
    workflow.add_edge("citation", END)

    return workflow.compile()


def generate_legal_memo(question: str) -> dict:
    """
    Main function: Generate legal memo using multi-agent system

    TIER 4 KEY: Multiple specialized agents coordinate via shared state
    """
    print(f"\n{'='*70}")
    print(f"⚖️ TIER 4 MULTI-AGENT MEMO GENERATOR")
    print(f"{'='*70}\n")
    print(f"Question: {question}\n")

    # Initialize state
    initial_state = {
        "legal_question": question,
        "research_findings": [],
        "outline": "",
        "draft_memo": "",
        "validated_citations": [],
        "status": "initialized"
    }

    # Run multi-agent workflow
    app = create_memo_workflow()
    final_state = app.invoke(initial_state)

    print(f"\n{'='*70}")
    print(f"✅ MEMO GENERATION COMPLETE")
    print(f"{'='*70}\n")

    return final_state


# ============================================================================
# Example Usage
# ============================================================================

def main():
    """Example: Generate legal memo using multi-agent system"""

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in .env")
        return

    # Example question
    question = """
    Is summary judgment appropriate when the plaintiff has presented expert testimony
    supporting their claim, but the defendant argues the expert's methodology is flawed?
    """

    result = generate_legal_memo(question.strip())

    # Display results
    print("\n" + "="*70)
    print("📋 GENERATED LEGAL MEMO")
    print("="*70)
    print(result["draft_memo"])

    print("\n" + "="*70)
    print("📚 CITATIONS TO VERIFY")
    print("="*70)
    for cite in result["validated_citations"]:
        print(f"  • {cite}")

    # Show tier characteristics
    print("\n" + "="*70)
    print("🎓 WHY THIS IS TIER 4")
    print("="*70)
    print("""
    Multi-Agent Coordination:
    1. ResearchAgent: Finds relevant cases
    2. OutlineAgent: Structures findings
    3. DraftAgent: Writes full memo
    4. CitationAgent: Validates citations

    State Management:
    - Shared state flows between agents
    - Each agent enriches state with its output
    - Sequential workflow ensures proper dependencies

    Contrast with other tiers:
    - Tier 3: Single agent does all tasks (less specialized)
    - Tier 4 ← : Multiple agents coordinate via LangGraph
    - Tier 5: + Human attorney review before finalization
    - Tier 6: + Learning from attorney edits to improve

    Current vs. Experimental:
    ✅ Available Today:
    - Multi-agent memo generation (this example)
    - Citation extraction and basic validation
    - Cost: ~$2-5 per memo (vs $1,200-7,800 manual)

    ⚠️ Partially Experimental:
    - Automatic citation Shepardizing (requires paid APIs)
    - Jurisdiction-specific legal analysis
    - Complex multi-issue memo generation

    ❌ Not Yet Viable:
    - Fully autonomous memo (no attorney review)
    - Court-admissible AI-generated legal analysis
    - Malpractice liability protection for AI drafts

    Ethics Compliance (2025):
    - MUST include attorney review step (Tier 5)
    - AI output is DRAFT, not work product
    - Attorney responsible for all citations
    - Recommended: Disclose AI assistance to client
    """)


if __name__ == "__main__":
    main()
