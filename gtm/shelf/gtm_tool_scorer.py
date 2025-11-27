#!/usr/bin/env python3
"""
GTM Tool Scorer - "Choose Your Own Adventure" Backend
======================================================

This is the recommendation engine that powers a Tinder-style GTM automation
stack builder. Instead of scoring LEADS (traditional lead scoring), we're
scoring TOOLS based on:
  - User's existing stack (integrations)
  - User's current goal (step in the funnel)
  - User's skill level (complexity tolerance)

This is a RULES-BASED scoring system (Phase 1). See bottom of file for how
we'll evolve this into a Vector Database + Embeddings approach (Phase 2).
"""

from typing import List, Dict
from dataclasses import dataclass


# ============================================================================
# TOOL CLASS - Represents a SaaS Tool in our GTM Stack
# ============================================================================

@dataclass
class SaaS_Tool:
    """
    Represents a single SaaS tool in the GTM automation ecosystem.

    Attributes:
        name: Tool name (e.g., "Apollo", "Clay", "RB2B")
        category: Tool category (e.g., "Data Provider", "Enrichment", "Sequencer")
        integrations: List of tools/platforms it integrates with
        complexity_score: 1-10 scale
            1-3: SMB/No-Code (e.g., Zapier, basic integrations)
            4-7: Mid-Market (e.g., Clay, n8n, some API work)
            8-10: Enterprise/API-Heavy (e.g., custom HubSpot apps, LangChain)
        funnel_steps: Which steps this tool is designed for
            Common steps: "Find Accounts", "Find Leads", "Enrich Data",
                         "Score Fit", "Personalize Outreach", "Send Emails"
    """
    name: str
    category: str
    integrations: List[str]
    complexity_score: int  # 1-10
    funnel_steps: List[str]

    def __repr__(self):
        return f"<Tool: {self.name} | Category: {self.category} | Complexity: {self.complexity_score}/10>"


# ============================================================================
# SAMPLE TOOL DATABASE - Real tools from the "shelf" examples
# ============================================================================

TOOL_DATABASE = [
    # Account Finding Tools
    SaaS_Tool(
        name="Apollo",
        category="Data Provider",
        integrations=["HubSpot", "Salesforce", "Outreach"],
        complexity_score=4,
        funnel_steps=["Find Accounts", "Find Leads"]
    ),
    SaaS_Tool(
        name="Clay",
        category="Enrichment Orchestrator",
        integrations=["HubSpot", "Salesforce", "Attio", "Slack", "Smartlead"],
        complexity_score=6,
        funnel_steps=["Find Accounts", "Find Leads", "Enrich Data", "Score Fit", "Personalize Outreach"]
    ),
    SaaS_Tool(
        name="RB2B",
        category="Visitor Identification",
        integrations=["Clay", "Slack"],
        complexity_score=3,
        funnel_steps=["Find Accounts"]
    ),

    # Enrichment Tools
    SaaS_Tool(
        name="Attio",
        category="CRM",
        integrations=["Clay", "Zapier", "Webhooks"],
        complexity_score=5,
        funnel_steps=["Enrich Data", "Score Fit"]
    ),
    SaaS_Tool(
        name="Serper",
        category="Search API",
        integrations=["Clay", "n8n", "Make"],
        complexity_score=4,
        funnel_steps=["Enrich Data"]
    ),
    SaaS_Tool(
        name="Zenrows",
        category="Web Scraper",
        integrations=["Clay", "n8n"],
        complexity_score=7,
        funnel_steps=["Enrich Data", "Find Leads"]
    ),

    # Outreach Tools
    SaaS_Tool(
        name="Smartlead",
        category="Email Sequencer",
        integrations=["Clay", "Slack"],
        complexity_score=4,
        funnel_steps=["Send Emails"]
    ),
    SaaS_Tool(
        name="HubSpot",
        category="CRM & Automation",
        integrations=["Apollo", "Clay", "Salesforce"],
        complexity_score=6,
        funnel_steps=["Find Leads", "Enrich Data", "Score Fit", "Send Emails"]
    ),

    # Advanced/Custom Tools
    SaaS_Tool(
        name="WhoisXML API",
        category="DNS Lookup",
        integrations=["Clay", "n8n"],
        complexity_score=5,
        funnel_steps=["Enrich Data"]
    ),
    SaaS_Tool(
        name="OpenAI API",
        category="AI/LLM",
        integrations=["Clay", "LangChain", "n8n"],
        complexity_score=7,
        funnel_steps=["Score Fit", "Personalize Outreach"]
    ),
]


# ============================================================================
# SCORING LOGIC - The "Lead Scoring Model" but for Tools
# ============================================================================

def score_tool(user_stack: List[str], current_step: str, user_skill_level: int, tool: SaaS_Tool) -> Dict:
    """
    Calculate a "fit score" for a tool based on user context.

    This is analogous to Lead Scoring:
      - Lead Scoring: Score a PERSON based on their Job Title (attribute) + Email Clicks (behavior)
      - Tool Scoring: Score a TOOL based on User's Stack (attribute) + User's Goal (behavior/intent)

    Args:
        user_stack: List of tools the user already has (e.g., ["HubSpot", "Slack"])
        current_step: The funnel step they're trying to solve (e.g., "Find Accounts")
        user_skill_level: User's self-identified skill (1-10, same scale as complexity_score)
        tool: The SaaS_Tool to score

    Returns:
        Dict with 'score' (int) and 'reasons' (list of explanations)
    """
    score = 0
    reasons = []

    # ========================================
    # RULE 1: Integration Match (+10 points per shared tool)
    # ========================================
    # If the tool integrates with something the user already has, it's easier to adopt
    integration_matches = set(user_stack) & set(tool.integrations)
    if integration_matches:
        points = len(integration_matches) * 10
        score += points
        reasons.append(f"+{points} pts: Integrates with your existing stack ({', '.join(integration_matches)})")

    # ========================================
    # RULE 2: Funnel Step Fit (+20 points if perfect match)
    # ========================================
    # This is the most important: does the tool solve the current problem?
    if current_step in tool.funnel_steps:
        score += 20
        reasons.append(f"+20 pts: Built specifically for '{current_step}'")

    # ========================================
    # RULE 3: Complexity Match (+5 points if within 2 levels of user skill)
    # ========================================
    # If user is skill level 5, they can handle tools rated 3-7 without overwhelming them
    complexity_delta = abs(tool.complexity_score - user_skill_level)
    if complexity_delta <= 2:
        score += 5
        reasons.append(f"+5 pts: Complexity ({tool.complexity_score}/10) matches your skill level")
    elif complexity_delta > 4:
        # Penalty for tools that are way too complex or too simple
        penalty = -5
        score += penalty
        reasons.append(f"{penalty} pts: Complexity mismatch (tool is {tool.complexity_score}/10, you're {user_skill_level}/10)")

    # ========================================
    # RULE 4: Clay Bonus (Meta-Rule)
    # ========================================
    # Clay is the "orchestrator" - if user already has Clay, boost other tools that integrate with it
    if "Clay" in user_stack and "Clay" in tool.integrations and tool.name != "Clay":
        score += 8
        reasons.append("+8 pts: Works seamlessly with your Clay workspace")

    return {
        "tool": tool.name,
        "score": score,
        "reasons": reasons
    }


# ============================================================================
# RECOMMENDATION ENGINE - Rank tools for a given context
# ============================================================================

def recommend_tools(user_stack: List[str], current_step: str, user_skill_level: int, top_n: int = 3) -> List[Dict]:
    """
    Score all tools and return the top N recommendations.

    Args:
        user_stack: User's existing tools
        current_step: Current funnel step they need to solve
        user_skill_level: User's skill level (1-10)
        top_n: How many recommendations to return

    Returns:
        List of scored tools, sorted by score (highest first)
    """
    scored_tools = []

    for tool in TOOL_DATABASE:
        result = score_tool(user_stack, current_step, user_skill_level, tool)
        result["tool_obj"] = tool  # Include full object for display
        scored_tools.append(result)

    # Sort by score (descending) and return top N
    scored_tools.sort(key=lambda x: x["score"], reverse=True)
    return scored_tools[:top_n]


# ============================================================================
# CLI GAME SIMULATION - "Choose Your Own Adventure"
# ============================================================================

def display_tool_card(tool_result: Dict):
    """Pretty-print a tool recommendation like a Tinder card."""
    tool = tool_result["tool_obj"]
    score = tool_result["score"]
    reasons = tool_result["reasons"]

    print("\n" + "="*60)
    print(f"  🛠️  {tool.name}")
    print("="*60)
    print(f"Category:      {tool.category}")
    print(f"Complexity:    {tool.complexity_score}/10 {'🔥' * tool.complexity_score}")
    print(f"Integrations:  {', '.join(tool.integrations[:3])}{'...' if len(tool.integrations) > 3 else ''}")
    print(f"\n💯 FIT SCORE: {score} points")
    print("\nWhy this tool?")
    for reason in reasons:
        print(f"  • {reason}")
    print("="*60)


def run_game():
    """
    Simulate the "Choose Your Own Adventure" game.
    User progresses through funnel steps and gets tool recommendations.
    """
    print("\n🎮 Welcome to the GTM Stack Builder!")
    print("We'll help you build your automation stack step-by-step.\n")

    # Initialize user profile
    user_stack = []

    # Step 0: Get user skill level
    print("First, what's your technical skill level?")
    print("  1-3: I prefer no-code tools")
    print("  4-7: I can handle some API work and integrations")
    print("  8-10: I write custom code and build integrations from scratch")

    while True:
        try:
            skill = int(input("\nYour skill level (1-10): "))
            if 1 <= skill <= 10:
                break
            print("Please enter a number between 1 and 10.")
        except ValueError:
            print("Please enter a valid number.")

    print(f"\n✅ Got it! Skill level: {skill}/10\n")

    # Define the funnel journey
    funnel_journey = [
        {
            "step": "Find Accounts",
            "question": "Step 1: How do you want to find accounts that could buy from you?",
            "description": "This is about identifying COMPANIES (not people yet)."
        },
        {
            "step": "Find Leads",
            "question": "Step 2: Now that you have accounts, how do you find the RIGHT PEOPLE at those companies?",
            "description": "This is about finding contact info for decision-makers."
        },
        {
            "step": "Enrich Data",
            "question": "Step 3: You have contacts, but you need MORE DATA to personalize. How do you enrich?",
            "description": "This is about adding context (LinkedIn, tech stack, company news, etc.)."
        }
    ]

    # Walk through each step
    for journey_step in funnel_journey:
        step_name = journey_step["step"]
        question = journey_step["question"]
        description = journey_step["description"]

        print("\n" + "🎯 " + "="*58)
        print(f"  {question}")
        print("="*60)
        print(f"  {description}")
        print("="*60)

        # Get recommendations
        recommendations = recommend_tools(
            user_stack=user_stack,
            current_step=step_name,
            user_skill_level=skill,
            top_n=3
        )

        # Show top 3 recommendations
        print(f"\n📊 Top 3 Recommendations for '{step_name}':\n")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['tool']} (Score: {rec['score']} pts)")

        # Let user pick one
        print("\nWhich tool do you want to use? (Enter 1, 2, or 3)")
        while True:
            try:
                choice = int(input("Your choice: "))
                if 1 <= choice <= 3:
                    break
                print("Please enter 1, 2, or 3.")
            except ValueError:
                print("Please enter a valid number.")

        # Show full card for chosen tool
        chosen = recommendations[choice - 1]
        display_tool_card(chosen)

        # Add to user's stack
        chosen_tool_name = chosen["tool"]
        user_stack.append(chosen_tool_name)
        print(f"\n✅ Added {chosen_tool_name} to your stack!")
        print(f"📦 Your stack: {', '.join(user_stack)}")

        input("\nPress ENTER to continue to the next step...")

    # Final summary
    print("\n" + "🎉 " + "="*58)
    print("  Congratulations! You've built your GTM automation stack!")
    print("="*60)
    print(f"\n📦 Your Final Stack: {' → '.join(user_stack)}")
    print("\nNext steps:")
    print("  • Check out the /gtm/shelf/ directory for workflow examples")
    print("  • Start building integrations between these tools")
    print("  • Iterate and optimize based on results\n")


# ============================================================================
# FUTURE: Vector Database + Embeddings Approach
# ============================================================================
"""
PHASE 2: EVOLUTION TO VECTOR-BASED RECOMMENDATIONS
===================================================

The rules-based scoring above works for a "toy example," but it has limitations:
  1. Rigid Rules: Every new tool requires manual rule updates
  2. No Semantic Understanding: Can't match "I want to find CTO emails" to tools
  3. Doesn't Learn: No feedback loop to improve recommendations

HOW TO EVOLVE THIS WITH VECTOR DATABASES + EMBEDDINGS:
------------------------------------------------------

STEP 1: Vectorize Tool Descriptions
  - For each tool, create a rich text description:
    Example for Clay: "Clay is a data enrichment orchestrator that helps you
    find accounts, enrich leads, score fit, and personalize outreach. It integrates
    with HubSpot, Salesforce, and 50+ data providers. Ideal for mid-market teams
    who need flexible workflows without heavy coding."

  - Convert these descriptions to embeddings using OpenAI's text-embedding-3-small:
    ```python
    import openai
    embedding = openai.Embedding.create(
        input="Clay is a data enrichment...",
        model="text-embedding-3-small"
    )
    ```

STEP 2: Store in Vector Database
  - Use Pinecone, Weaviate, or PostgreSQL with pgvector
  - Schema:
    {
      "tool_id": "clay",
      "name": "Clay",
      "embedding": [0.023, -0.15, ...],  # 1536-dim vector
      "metadata": {
        "category": "Enrichment",
        "complexity": 6,
        "integrations": ["HubSpot", "Salesforce"]
      }
    }

STEP 3: Query with Natural Language
  - User says: "I need to find CTOs at companies using Google Workspace"
  - Convert query to embedding
  - Perform vector similarity search (cosine similarity)
  - Return top-k most semantically similar tools

STEP 4: Hybrid Scoring (Vector + Rules)
  - Combine semantic similarity (vector search) with rules-based scoring:
    final_score = (0.6 * vector_similarity) + (0.4 * rules_based_score)

  This gives you:
    • Semantic matching for complex/creative queries
    • Hard constraints from rules (e.g., "must integrate with HubSpot")

STEP 5: Feedback Loop (Learning)
  - Track user selections: "User chose Apollo over Clay for 'Find Accounts'"
  - Store as training data
  - Fine-tune embeddings or adjust rule weights over time
  - Example: If users with HubSpot always pick Apollo, increase its weight

EXAMPLE VECTOR QUERY CODE:
--------------------------
```python
import pinecone
import openai

# Initialize
pinecone.init(api_key="...")
index = pinecone.Index("gtm-tools")

# User query
query = "I want to find startup founders who recently got funding"
query_embedding = openai.Embedding.create(input=query, model="text-embedding-3-small")

# Vector search
results = index.query(
    vector=query_embedding["data"][0]["embedding"],
    top_k=5,
    include_metadata=True
)

# Combine with rules
for match in results["matches"]:
    tool = match["metadata"]
    vector_score = match["score"]  # Cosine similarity (0-1)
    rules_score = score_tool(user_stack, current_step, skill, tool) / 100  # Normalize to 0-1
    final_score = (0.6 * vector_score) + (0.4 * rules_score)
    print(f"{tool['name']}: {final_score}")
```

WHY THIS MATTERS:
-----------------
  • Rules-based is great for MVP and transparency (you can explain every score)
  • Vector-based scales to hundreds of tools and handles complex, natural queries
  • Hybrid approach gives you the best of both worlds

WHEN TO MAKE THE SWITCH:
------------------------
  • You have 50+ tools in the database (manual rules become unmanageable)
  • Users ask questions like "tools for ABM in healthcare" (semantic understanding needed)
  • You want to learn from user behavior (feedback loops require vectors)

For now, the rules-based system gets you 80% of the value with 20% of the complexity.
Ship this first. Iterate based on real user queries.
"""


# ============================================================================
# MAIN - Run the game
# ============================================================================

if __name__ == "__main__":
    # Uncomment to run the interactive game:
    run_game()

    # Or test scoring manually:
    # user_stack = ["HubSpot", "Slack"]
    # current_step = "Find Accounts"
    # skill_level = 5
    #
    # recommendations = recommend_tools(user_stack, current_step, skill_level, top_n=5)
    # for rec in recommendations:
    #     print(f"{rec['tool']}: {rec['score']} pts")
    #     for reason in rec['reasons']:
    #         print(f"  - {reason}")
    #     print()
