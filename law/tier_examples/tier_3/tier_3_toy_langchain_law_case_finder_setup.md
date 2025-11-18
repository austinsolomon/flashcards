# Law - Tier 3 - Legal Research Agent Setup

## Installation

```bash
cd law/tier_examples/tier_3/
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.template .env
# Edit .env with your OPENAI_API_KEY
python tier_3_toy_langchain_law_case_finder.py
```

## What You'll See

The agent will:
1. Search for relevant case law
2. Validate citations are still good law
3. Look up statute text
4. Generate a research memo

## Why Tier 3

- **Single agent** with multiple tools (not Tier 4 multi-agent)
- **Autonomous decisions** about which tools to use
- **Real tool calling** (not just ONE LLM call like Tier 2)

## Next Steps

- Tier 4: Multi-agent system (ResearchAgent → CitationAgent → MemoAgent)
- Tier 5: Human attorney reviews AI memo before using in brief
