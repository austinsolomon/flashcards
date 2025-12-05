# Legal Research Summarizer

**Tier**: 2 (Context-Aware AI)
**Category**: Recurring Development

## Purpose

Summarizes legal research materials (cases, statutes, articles) using Claude. Extracts key holdings, reasoning, and actionable insights.

## What It Does

- Summarizes court opinions and decisions
- Extracts key holdings and reasoning
- Identifies relevant precedents
- Generates case briefs automatically
- Synthesizes multiple sources
- Creates research memos

## Usage

```bash
# Summarize single case
python research_summarizer.py --case "123 F.3d 456"

# Generate case brief
python research_summarizer.py --case mobley_v_workday.pdf --brief

# Synthesize multiple cases on topic
python research_summarizer.py --topic "AI discrimination" --cases cases/ --memo

# Summarize statute
python research_summarizer.py --statute "42 USC 2000e" --annotate
```

## Example Output

```markdown
# Case Brief: Mobley v. Workday, Inc.

**Citation:** No. 3:23-cv-00770 (N.D. Cal. 2023)

**Facts:** Applicant used Workday's AI screening tool; rejected without
human review; alleged algorithmic bias based on race and disability.

**Issue:** Can employer be liable under Title VII/ADA for AI tool bias?

**Holding:** Yes, may be liable. "Employer cannot outsource discrimination."

**Reasoning:**
- AI tool decisions trigger traditional discrimination framework
- Employer responsible even if vendor-provided AI
- ADA reasonable accommodation applies to AI-driven decisions

**Significance:** Establishes employer liability for AI discrimination.

**Application:** Direct precedent for AI hiring discrimination cases.
```

## Files

- `research_summarizer.py` - Main summarization engine
- `case_brief_template.md` - Brief format
- `synthesis_agent.py` - Multi-source analysis
- `statute_annotator.py` - Statute summaries
