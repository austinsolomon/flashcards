# Law - Tier 4 - Multi-Agent Legal Memo Generator Setup

## Installation

```bash
cd law/tier_examples/tier_4/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
# Edit .env with OPENAI_API_KEY
python tier_4_toy_langgraph_law_memo_generator.py
```

## Architecture

```
ResearchAgent → OutlineAgent → DraftAgent → CitationAgent
     |              |              |              |
     v              v              v              v
  (finds cases) (structures) (writes memo) (validates)
```

## Why Tier 4

- **Multi-agent**: 4 specialized agents vs single agent (Tier 3)
- **Coordination**: LangGraph manages state flow
- **Separation**: Each agent has one job (research, outline, draft, cite)

## Next Steps

- Tier 5: Add human attorney review before finalizing
- Tier 6: System learns from attorney edits to improve drafts
