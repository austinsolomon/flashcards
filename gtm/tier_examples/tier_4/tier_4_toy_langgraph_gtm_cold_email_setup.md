# GTM - Tier 4 - Multi-Agent Cold Email Generator (LangGraph)

**What It Does**: Coordinates two specialized agents to create personalized cold emails. ResearchAgent gathers prospect/company data, then WriterAgent crafts the email using that research.

**Tier Characteristics**:
- **Multiple specialized agents**: ResearchAgent + WriterAgent
- **Agent coordination**: Sequential workflow with state passing
- **LangGraph orchestration**: Explicit graph defining agent flow
- **Separation of concerns**: Each agent has single responsibility
- **State management**: Shared state flows between agents

---

## Installation

```bash
cd gtm/tier_4/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
# Edit .env with OPENAI_API_KEY
python tier_4_toy_langgraph_gtm_cold_email.py
```

---

## Architecture

```
Input: Prospect Name + Company + Product Pitch
                    │
                    ▼
         ┌──────────────────────┐
         │  ResearchAgent       │ ← Agent 1: Gather data
         │  - Company research  │
         │  - Prospect research │
         │  - Buying signals    │
         └──────────┬───────────┘
                    │ State: research results
                    ▼
         ┌──────────────────────┐
         │  WriterAgent         │ ← Agent 2: Craft email
         │  - Use research      │
         │  - Personalize       │
         │  - Generate email    │
         └──────────┬───────────┘
                    │
                    ▼
         Output: Personalized Cold Email
```

**Key Tier 4 Element**: Agent coordination via shared state

---

## Why This Is Tier 4

**Tier 4 Characteristics**:
1. **Multi-Agent**: ResearchAgent → WriterAgent
2. **Coordination**: Sequential workflow with dependencies
3. **State Management**: Research results pass to writer
4. **Specialization**: Each agent focused on one task
5. **Orchestration**: LangGraph defines agent flow

**Contrast**:
- **Tier 3**: Single agent with tools (no multi-agent coordination)
- **Tier 4** ←: Multiple agents coordinating via LangGraph
- **Tier 5**: Claude Code orchestrates agents + human review + CRM integration
- **Tier 6**: Autonomous learning from email responses, continuous improvement

---

## Extending to More Agents

```python
# Add ReviewAgent
def review_agent(state):
    """Scores email quality, requests rewrites if needed"""
    ...

# Add SendAgent
def send_agent(state):
    """Sends email via API, tracks in CRM"""
    ...

# Update workflow
workflow.add_node("review", review_agent)
workflow.add_node("send", send_agent)
workflow.add_edge("writer", "review")
workflow.add_conditional_edges(
    "review",
    lambda x: "writer" if x["quality_score"] < 8 else "send"
)
```

---

## Next Steps: Moving to Tier 5

For **Tier 5** (Claude Code orchestration), you would add:
- Human-in-the-loop review
- CRM integration to log outreach
- Email sending via API
- A/B testing different email styles
- Calendar integration for follow-ups

See `tier_5_toy_claude_code_gtm_campaign_launch.py`.
