#!/usr/bin/env python3
"""
Law - Tier 3 - Case Law Research Agent (LangChain)

## What Is Available Today (2025)

**Current Legal Research Process**:
- Attorneys search Westlaw/Lexis manually ($400-600/month/user)
- Keyword searches return 100s of cases, manual review required
- 2-6 hours per research memo for standard issues
- Expensive for small firms, solo practitioners

**Available AI Tools**:
- **CaseText CoCounsel** ($500/month): AI research assistant
- **Lexis+ AI** ($premium tier): Conversational case law search
- **Harvey AI** ($enterprise only): Legal research for big law

**The Gap**: Affordable AI research agents for small/mid firms

---

## How AI Could Improve It

**Tier 3 (Available Today - This Example)**:
- **Tool A**: LangChain agent with multiple search tools
- **Tool B**: Web search for free case law (Google Scholar, Justia, CourtListener)
- **Tool C**: Citation validation tool (check if case still good law)
- **Cost**: ~$0.50-2 per research query vs $50-200 attorney time

**Current Techniques (In Use)**:
1. **Semantic search**: Vector embeddings for case similarity (not just keywords)
2. **Citation graphs**: Find cases citing key precedents
3. **Multi-tool agents**: Web search + citation check + summarization

**Experimental Techniques**:
1. **Shepardizing via API**: Auto-check if case overruled (requires Lexis/Westlaw API $$$)
2. **Jurisdiction-aware search**: Prioritize binding precedent over persuasive
3. **Predictive case outcome**: ML models predict judge's ruling based on facts

---

TIER 3 CHARACTERISTICS:
- Single agent with multiple tools
- Agent decides which tools to use and when
- Autonomous decision-making within research task
- No multi-agent coordination (that's Tier 4)

What It Does:
Given a legal question, finds relevant case law using web search, validates citations,
and synthesizes research memo with holdings and recommendations.
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
# TIER 3 TOOLS: Legal Research Tools
# ============================================================================

def case_law_search(query: str) -> str:
    """
    TIER 3 TOOL: Search free case law databases

    In production: Query Google Scholar Cases, CourtListener API, or Justia
    This example: Simulated search results
    """
    print(f"🔍 [CASE_SEARCH] Searching case law for: {query}")

    # Simulated case law results based on query
    if "attorney fees" in query.lower() or "prevailing party" in query.lower():
        return """
        Case Law Search Results for '{query}':

        1. Hensley v. Eckerhart, 461 U.S. 424 (1983)
           Supreme Court | Cited by 15,234 cases
           Holding: Prevailing party may recover attorney's fees under 42 U.S.C. § 1988
           if they succeed on any significant issue in litigation that achieves some of the
           benefit the parties sought in bringing suit.
           Key Quote: "litigants in good faith may raise alternative legal grounds for a desired outcome"

        2. Buckhannon Board & Care Home, Inc. v. West Virginia Dept. of Health, 532 U.S. 598 (2001)
           Supreme Court | Cited by 8,942 cases
           Holding: Prevailing party status requires judicial imprimatur (court-ordered relief or
           consent decree), not just catalyst theory where defendant voluntarily changes conduct.

        3. Newman v. Piggie Park Enterprises, Inc., 390 U.S. 400 (1968)
           Supreme Court | Cited by 5,123 cases
           Holding: In civil rights cases, prevailing plaintiff "should ordinarily recover an
           attorney's fee unless special circumstances would render such an award unjust."
        """
    elif "motion to dismiss" in query.lower() or "12(b)(6)" in query.lower():
        return """
        Case Law Search Results for '{query}':

        1. Bell Atlantic Corp. v. Twombly, 550 U.S. 544 (2007)
           Supreme Court | Cited by 42,315 cases
           Holding: To survive motion to dismiss, complaint must contain sufficient factual matter,
           accepted as true, to state claim to relief that is plausible on its face.
           Overrules: Conley v. Gibson's "no set of facts" standard

        2. Ashcroft v. Iqbal, 556 U.S. 662 (2009)
           Supreme Court | Cited by 38,921 cases
           Holding: Plausibility standard requires more than sheer possibility that defendant acted
           unlawfully. Conclusory statements not entitled to assumption of truth.

        3. Johnson v. City of Shelby, Mississippi, 574 U.S. 10 (2014)
           Supreme Court | Cited by 2,845 cases
           Holding: Federal pleading rules do not require plaintiff to plead or prove correct legal
           theory for their claim. Notice pleading remains sufficient.
        """
    else:
        return f"""
        Case Law Search Results for '{query}':

        1. Relevant case found via Google Scholar
        2. See also CourtListener.com for free PACER alternatives
        3. Justia.com has annotated Supreme Court cases with summaries
        """


def shepardize_case(citation: str) -> str:
    """
    TIER 3 TOOL: Check if case is still good law

    In production: Query Shepard's Citations (Lexis) or KeyCite (West)
    This example: Simulated citation validation

    **Note**: This is EXPERIMENTAL - requires paid API access to Lexis/Westlaw
    """
    print(f"📚 [SHEPARDIZE] Validating citation: {citation}")

    # Simulated Shepardizing
    if "Twombly" in citation or "550 U.S. 544" in citation:
        return """
        Shepard's Report for Bell Atlantic v. Twombly, 550 U.S. 544 (2007):

        Status: ✅ GOOD LAW (Still binding)
        Positive Treatment: Followed by 42,315 cases
        Negative Treatment: None (not overruled, not questioned)

        Subsequent History:
        - Clarified by Ashcroft v. Iqbal, 556 U.S. 662 (2009)
        - Applied in thousands of federal cases since 2007

        Recent Citations (2024-2025):
        - Followed in Smith v. Tech Corp, 2024 WL 12345 (9th Cir. 2024)
        - Distinguished in Martinez v. City, 2025 WL 54321 (D. Mass. 2025)

        Recommendation: Safe to cite as binding precedent
        """
    else:
        return f"""
        Shepard's Report for {citation}:

        Status: ✅ GOOD LAW (preliminary check)

        Note: This is a simulated check. In production, use:
        - Lexis Shepard's Citations API (requires subscription)
        - Westlaw KeyCite API (requires subscription)
        - CourtListener citation network (free, but limited coverage)
        """


def statute_lookup(statute_citation: str) -> str:
    """
    TIER 3 TOOL: Look up federal/state statutes

    In production: Query Justia, Cornell LII, or state-specific statute databases
    This example: Simulated statute text
    """
    print(f"📖 [STATUTE] Looking up: {statute_citation}")

    if "1988" in statute_citation or "42 U.S.C. § 1988" in statute_citation:
        return """
        42 U.S.C. § 1988 - Proceedings in vindication of civil rights

        (b) Attorney's fees
        In any action or proceeding to enforce a provision of sections 1981, 1981a, 1982,
        1983, 1985, and 1986 of this title, title IX of Public Law 92-318, the Religious
        Freedom Restoration Act of 1993, the Religious Land Use and Institutionalized
        Persons Act of 2000, title VI of the Civil Rights Act of 1964, or section 13981
        of this title, the court, in its discretion, may allow the prevailing party, other
        than the United States, a reasonable attorney's fee as part of the costs, except
        that in any action brought against a judicial officer for an act or omission taken
        in such officer's judicial capacity such officer shall not be held liable for any
        costs, including attorney's fees, unless such action was clearly in excess of such
        officer's jurisdiction.

        Last amended: 2006
        Current as of: 2025
        """
    else:
        return f"Statute text for {statute_citation} would be retrieved from free legal databases."


# ============================================================================
# TIER 3 AGENT SETUP
# ============================================================================

tools = [
    Tool(
        name="case_law_search",
        description="Search for case law on a legal topic or issue. Returns case names, citations, "
                    "holdings, and key quotes. Use this to find relevant precedents. "
                    "Input should be a legal question or issue description.",
        func=case_law_search
    ),
    Tool(
        name="shepardize",
        description="Validate whether a case citation is still good law (not overruled or questioned). "
                    "Returns treatment history and current status. Use this after finding cases to "
                    "ensure they're still valid. Input should be a case citation (e.g., '550 U.S. 544').",
        func=shepardize_case
    ),
    Tool(
        name="statute_lookup",
        description="Look up the text of federal or state statutes. Returns full statute text and "
                    "amendment history. Use this to verify statutory language. "
                    "Input should be a statute citation (e.g., '42 U.S.C. § 1988').",
        func=statute_lookup
    )
]

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a legal research assistant helping attorneys find relevant case law and statutes.

Your goal: Answer legal research questions by finding authoritative precedents and validating they're still good law.

TIER 3 REASONING APPROACH:
1. Understand the legal question
2. Search for relevant case law using case_law_search
3. Validate key cases are still good law using shepardize
4. Look up relevant statutes if needed using statute_lookup
5. Synthesize findings into a clear research memo

Available tools:
- case_law_search: Find relevant cases
- shepardize: Validate case citations
- statute_lookup: Get statute text

When you have enough research, provide:
- Key cases with holdings
- Current status (still good law?)
- Relevant statutes
- Recommendation for attorney

IMPORTANT ETHICAL NOTES:
- Always recommend attorney independently verify citations
- Flag if cases are from non-binding jurisdictions
- Note any limitations in free research tools vs. paid (Westlaw/Lexis)"""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])


def create_legal_research_agent():
    """Create LangChain agent for legal research"""
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


def research_legal_question(question: str) -> Dict[str, Any]:
    """Main function: Research a legal question"""
    print(f"\n{'='*60}")
    print(f"⚖️ TIER 3 AGENT: Researching legal question")
    print(f"{'='*60}\n")
    print(f"Question: {question}\n")

    agent = create_legal_research_agent()

    try:
        result = agent.invoke({
            "input": question
        })

        print(f"\n{'='*60}")
        print(f"✅ RESEARCH COMPLETE")
        print(f"{'='*60}\n")

        return {
            "success": True,
            "question": question,
            "research_memo": result["output"]
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
    """Example usage of legal research agent"""

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found")
        print("Set it in .env file or environment")
        sys.exit(1)

    # Example 1: Attorney fee research
    print("\n" + "="*60)
    print("EXAMPLE 1: Attorney Fees Research")
    print("="*60)

    result1 = research_legal_question(
        "What is the standard for awarding attorney's fees to a prevailing party "
        "in a federal civil rights case under 42 U.S.C. § 1988?"
    )

    if result1["success"]:
        print("\n📋 RESEARCH MEMO:")
        print(result1["research_memo"])

    # Example 2: Motion to dismiss standard
    print("\n" + "="*60)
    print("EXAMPLE 2: Motion to Dismiss Standard")
    print("="*60)

    result2 = research_legal_question(
        "What is the current pleading standard for surviving a Rule 12(b)(6) motion "
        "to dismiss after Twombly and Iqbal?"
    )

    if result2["success"]:
        print("\n📋 RESEARCH MEMO:")
        print(result2["research_memo"])

    # Show tier comparison
    print("\n" + "="*60)
    print("🎓 WHY THIS IS TIER 3:")
    print("="*60)
    print("""
    ✅ Current Techniques (In Use Today):
    1. Single Agent: One research agent with multiple tools
    2. Tool Calling: Agent decides to search, validate, lookup statutes
    3. Free Data Sources: Google Scholar, CourtListener, Justia
    4. Autonomous Research: Agent determines research strategy

    ⚠️ Partially Experimental:
    1. Citation Validation: Shepardizing requires paid API (simulated here)
    2. Jurisdiction Filtering: Binding vs. persuasive precedent detection
    3. Research Quality: Free sources less comprehensive than Westlaw/Lexis

    ❌ Not Yet Viable:
    1. Court-Admissible Research: AI research memo not standalone legal advice
    2. Malpractice Protection: No case law establishing AI research liability limits
    3. Full Westlaw/Lexis Replacement: Free tools lack headnotes, annotations

    Contrast with other tiers:
    - Tier 2: ONE AI call to summarize cases (no actual searching)
    - Tier 3 ← : Agent with tools autonomously researches question
    - Tier 4: Multi-agent (ResearchAgent → ValidationAgent → MemoAgent)
    - Tier 5: Human attorney reviews AI memo → Edits → Adds to brief
    - Tier 6: System learns from firm's win/loss record, suggests winning arguments
    """)

    print("\n" + "="*60)
    print("💡 PRODUCTION DEPLOYMENT NOTES:")
    print("="*60)
    print("""
    To use in production:

    1. **Data Sources**:
       - Replace simulated tools with real API calls:
         - CourtListener API (free, federal courts): courtlistener.com/api/
         - Google Scholar Cases scraper (legal, but rate-limited)
         - Justia API (free tier available)

    2. **Citation Validation**:
       - Paid: Lexis Shepard's API or Westlaw KeyCite ($$$)
       - Free: CourtListener citation network (limited)
       - Hybrid: Free search + manual attorney verification

    3. **Ethics Compliance**:
       - Add disclaimer: "AI-assisted research, attorney must verify"
       - Log all research queries for audit trail
       - Never represent AI output as attorney work product without review
       - Check state bar ethics opinions on AI research (vary by jurisdiction)

    4. **Cost Comparison (2025)**:
       - Manual Westlaw research: $200-500/issue (attorney time + platform fees)
       - This AI agent: $0.50-2/issue (OpenAI API only)
       - Savings: 99%+ cost reduction for initial research pass
       - Caveat: Attorney still must review and validate

    5. **Limitations**:
       - Free sources lack West headnotes, Lexis summaries
       - No access to unpublished opinions (PACER only)
       - Citation validation less reliable than Shepard's/KeyCite
       - Best for: Initial research, straightforward questions
       - Not suitable for: Complex novel issues, high-stakes litigation
    """)


if __name__ == "__main__":
    main()
