# GTM - Tier 5 - Campaign Launch Orchestrator (Claude Code)

**What It Does**: Claude Code orchestrates complete campaign launch: AI research → AI email generation → Human approval → CRM integration → Email sending → Follow-up scheduling

**Tier 5 Characteristics**:
- **Orchestration**: Coordinates multiple AI agents, human review, and systems
- **Human-in-the-loop**: Requires approval before sending
- **System integration**: CRM, email, calendar
- **Multi-step workflow**: 7-step process with checkpoints
- **Error handling**: Can pause for human input

## Installation
```bash
cd gtm/tier_5/
pip install python-dotenv
python tier_5_toy_claude_code_gtm_campaign_launch.py
```

## Tier 5: Full Orchestration
- AI agents research and generate
- Human reviews and approves
- Systems execute (CRM, email, calendar)
- End-to-end campaign automation

**Contrast**: Tier 4 has AI agents only. Tier 5 orchestrates AI + human + systems. Tier 6 removes human requirement with autonomous learning.
