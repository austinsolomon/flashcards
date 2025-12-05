# Law - Tier 5 - Legal Brief Assistant Setup

## What This Does

Coordinates AI agents with human attorney oversight to generate legal briefs:

1. **AI** researches cases
2. **AI** creates outline
3. **👤 HUMAN** reviews and edits outline
4. **AI** writes full brief incorporating edits
5. **👤 HUMAN** reviews and edits brief
6. **AI** files to court ECF system
7. **AI** updates practice management software

## Installation

```bash
cd law/tier_examples/tier_5/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # (if different from tier 4)
python tier_5_toy_claude_code_law_brief_assistant.py
```

## Why Tier 5

- **Human-in-the-loop**: Attorney reviews at critical decision points
- **Multi-system integration**: Court ECF + practice management
- **Orchestration**: Coordinates agents, human, and external systems
- **Ethics compliant**: Attorney maintains oversight and responsibility

## Time Savings

- **Traditional**: 16-32 hours attorney time
- **Tier 5**: 3-5 hours attorney time (review/edit only)
- **Savings**: 70-85%

## Next Steps

- Tier 6: System learns from attorney edits to improve
