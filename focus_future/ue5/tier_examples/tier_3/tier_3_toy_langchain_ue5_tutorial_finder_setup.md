# UE5 - Tier 3 - Tutorial & Documentation Finder (LangChain Agent)

**What It Does**: Given a UE5 topic, a LangChain agent autonomously finds the best tutorials, documentation, and learning resources by searching the web, YouTube, and official docs. The agent evaluates and curates the best learning path.

**Tier Characteristics**:
- **Single agent**: One agent curates all resources
- **Multiple tools**: web_search, youtube_search, docs_search
- **Autonomous search**: Agent decides which sources to query
- **Resource evaluation**: Assesses quality and appropriateness
- **Learning path curation**: Synthesizes findings into recommended order

---

## Installation & Usage

```bash
cd ue5/tier_3/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
# Edit .env with your OPENAI_API_KEY
python tier_3_toy_langchain_ue5_tutorial_finder.py
```

---

## Expected Output

```
============================================================
📚 TIER 3 AGENT: Finding tutorials for 'Niagara particle systems' (beginner level)
============================================================

> Entering new AgentExecutor chain...
I should start by checking official documentation for foundational knowledge.

Action: docs_search
Action Input: Niagara

📚 [DOCS_SEARCH] Searching UE5 docs for: Niagara

Observation: Official Unreal Engine Documentation with Quick Start Guide, API Reference...

Thought: Now let me find video tutorials for visual learning.

Action: youtube_search
Action Input: Niagara tutorial beginner

📺 [YOUTUBE_SEARCH] Searching YouTube for: Niagara tutorial beginner

Observation:
1. "UE5 Niagara Tutorial - Create Realistic Fire Effect" - Unreal Sensei (450K views)
2. "Complete Niagara VFX Course" - Ben Cloward (1.2M views, 99% liked)
3. "Niagara Particle System From Scratch" - Ryan Laley (280K views)

Thought: Excellent resources found. Let me also check for community resources.

Action: web_search
Action Input: UE5 Niagara best practices

🔍 [WEB_SEARCH] Searching for: UE5 Niagara best practices

Observation: Advanced Niagara Techniques, Industry expert workflows...

Thought: I have comprehensive resources. Let me curate the best learning path.

Final Answer:
**Recommended Learning Path for Niagara Particle Systems**

BEGINNER (Start here):
1. Official Quick Start Guide
   https://docs.unrealengine.com/5.3/en-US/niagara/quick-start/
   Start with this to understand core concepts

2. "Niagara Particle System From Scratch" - Ryan Laley
   https://youtube.com/watch?v=example3
   Duration: 45 minutes | Beginner-friendly
   Best video for absolute beginners - clear explanations, step-by-step

INTERMEDIATE (After basics):
3. "Complete Niagara VFX Course" - Ben Cloward
   https://youtube.com/watch?v=example2
   Duration: 2+ hours | Comprehensive deep dive
   1.2M views, 99% liked - highly recommended by community

ADVANCED (For production work):
4. "Advanced Niagara Techniques" - 80.lv Interview
   Industry experts share production workflows
   Learn optimization and real-world techniques

5. Official Best Practices Documentation
   https://docs.unrealengine.com/5.3/en-US/niagara/best-practices/
   Performance optimization and project-scale considerations

**Why This Path:**
- Start with official docs to avoid picking up bad habits
- Ryan Laley's tutorial is perfect for visual learners (clear, concise)
- Ben Cloward's course covers everything comprehensively
- Industry resources prepare you for production environments
```

---

## Why This Is Tier 3

**Tier 3 Characteristics**:
1. **Single Agent** handles entire curation task
2. **Multiple Tools** for different resource types
3. **Autonomous Search** - agent decides what to search
4. **Quality Evaluation** - agent assesses which resources are best
5. **Synthesis** - combines findings into coherent learning path

**Contrast**:
- **Tier 2**: ONE AI call returns generic tutorial suggestions (no actual searching)
- **Tier 3** ←: Single agent with tools, autonomously searches and curates
- **Tier 4**: Multiple agents (DiscoveryAgent → EvaluationAgent → CurationAgent)
- **Tier 5**: Claude Code orchestrates agent + human review + add to curriculum
- **Tier 6**: Autonomous system tracks user progress, adapts recommendations

---

## Customization

### Add Real APIs

```python
def youtube_search_tool(topic: str) -> str:
    import requests
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={
            "key": os.getenv("YOUTUBE_API_KEY"),
            "q": f"Unreal Engine 5 {topic} tutorial",
            "part": "snippet",
            "type": "video",
            "maxResults": 10
        }
    )
    return format_youtube_results(response.json())
```

### Add More Tools

```python
def reddit_search_tool(topic: str) -> str:
    """Search r/unrealengine for discussions"""
    ...

def discord_search_tool(topic: str) -> str:
    """Search Unreal Slackers Discord"""
    ...
```

---

## Next Steps: Moving to Tier 4

For **Tier 4** (multi-agent), you would create:
- **DiscoveryAgent**: Finds all possible resources
- **EvaluationAgent**: Scores resources by quality/relevance
- **CurationAgent**: Builds optimal learning path

Agents would coordinate via LangGraph.

See `tier_4_toy_langgraph_ue5_asset_validation.py` for multi-agent patterns.
