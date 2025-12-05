# Claude Code SKILLS Template
## Production-Ready Documented Workflow Instructions

---

## WHAT ARE SKILLS?

Skills are **documented workflow instructions** stored as markdown files that encode institutional knowledge, methodologies, and multi-step processes. They provide Claude with "how to think" about complex tasks.

### Core Properties
- **Trigger:** Claude reads when task matches skill domain OR user explicitly invokes
- **Scope:** Project (`/skills/`) or available via CLAUDE.md reference
- **State:** Stateless—instructions only, execution uses other primitives
- **Format:** Markdown with structured methodology

---

## WHEN TO USE SKILLS (vs. other primitives)

| Use Skills When | DON'T Use Skills When |
|-----------------|----------------------|
| Complex multi-step methodology | Single atomic operation (use Tools) |
| Business logic that evolves | Static, unchanging process (use Hooks) |
| Non-engineers need to update | Requires external API (use MCP) |
| Consistency across agents/commands | User-initiated shortcut (use Commands) |

### GTM Decision Examples
- ✅ ICP scoring methodology → Skill (complex logic, RevOps updates it)
- ✅ Outbound sequence framework → Skill (template + personalization rules)
- ✅ Lead qualification playbook → Skill (decision tree for routing)
- ❌ "Enrich this lead" → Command (user-initiated)
- ❌ Auto-format files → Hook (deterministic, every time)

---

## SKILL STRUCTURE

```
project/
├── skills/
│   └── gtm/
│       ├── SKILL.md                 # Skill manifest (optional)
│       ├── icp-scoring.md           # ICP scoring methodology
│       ├── outbound-sequence.md     # Sequence generation framework
│       └── lead-qualification.md    # Qualification playbook
└── CLAUDE.md                        # References skills
```

### SKILL.md Manifest (Optional)
```markdown
---
name: gtm-skills
description: "Go-to-market playbooks and methodologies"
version: 1.2.0
---

# GTM Skills

This directory contains sales and marketing methodologies.

## Available Skills
- **icp-scoring.md** - Score leads against Ideal Customer Profile
- **outbound-sequence.md** - Generate personalized outbound sequences
- **lead-qualification.md** - Qualify and route inbound leads
```

---

## GTM SKILL TEMPLATES

### 1. ICP Scoring Methodology

**File:** `skills/gtm/icp-scoring.md`

```markdown
# ICP Scoring Methodology

## Overview
This skill defines how to score leads against our Ideal Customer Profile.
Last updated: 2024-Q1 by RevOps.

## Input Requirements
- Company data (employee count, industry, tech stack, funding)
- Contact data (title, seniority)

## Scoring Criteria

### Firmographic Fit (Max 40 points)

#### Employee Count
| Range | Points | Rationale |
|-------|--------|-----------|
| 50-200 | 25 | Sweet spot: need our solution, can afford it |
| 201-500 | 20 | Good fit but longer sales cycle |
| 501-1000 | 15 | Enterprise, requires different motion |
| <50 | 5 | Too early, limited budget |
| >1000 | 10 | Enterprise only via partnerships |

#### Industry Vertical
| Industry | Points | Rationale |
|----------|--------|-----------|
| SaaS / Software | 15 | Core ICP, fastest adoption |
| FinTech | 15 | High ACV, compliance-driven |
| E-commerce | 10 | Good fit, seasonal buying |
| Healthcare | 5 | Long cycle, heavy compliance |
| Other | 0 | Case-by-case evaluation |

### Technology Fit (Max 30 points)

#### Tech Stack Signals
Award 10 points for EACH match (max 30):
- Salesforce → Indicates CRM maturity
- HubSpot → Marketing automation in place
- Segment → Data infrastructure ready
- Amplitude → Analytics sophistication
- Slack → Modern collaboration stack

### Buying Signals (Max 30 points)

#### Funding Stage
| Stage | Points |
|-------|--------|
| Series B+ | 15 |
| Series A | 10 |
| Seed | 5 |
| Bootstrapped | 0 |

#### Contact Seniority
| Level | Points |
|-------|--------|
| C-Level / VP | 15 |
| Director | 10 |
| Manager | 5 |
| IC | 0 |

## Score Interpretation

| Score | Tier | Action |
|-------|------|--------|
| 80-100 | A | Priority: SDR outreach within 24h, deep research |
| 60-79 | B | Standard: SDR outreach within 48h |
| 40-59 | C | Nurture: Add to marketing sequences |
| 0-39 | D | Disqualify: No active pursuit |

## Edge Cases

### Override to Tier A
Regardless of score, upgrade to Tier A if:
- Company is a known logo target (see `targets.json`)
- Contact was referred by existing customer
- Company appeared in recent funding news

### Override to Tier D
Regardless of score, downgrade to Tier D if:
- Domain is in blocklist (`blocklist.txt`)
- Company is a direct competitor
- Contact is from personal email domain

## Output Format

```json
{
  "email": "contact@company.com",
  "score": 75,
  "tier": "B",
  "breakdown": {
    "firmographic": 25,
    "technology": 20,
    "buying_signals": 30
  },
  "flags": ["series_b", "uses_salesforce"],
  "next_action": "SDR outreach within 48h"
}
```

## Changelog
- 2024-Q1: Added tech stack scoring for Segment/Amplitude
- 2023-Q4: Adjusted employee count sweet spot from 100-500 to 50-200
- 2023-Q3: Initial version
```

---

### 2. Outbound Sequence Framework

**File:** `skills/gtm/outbound-sequence.md`

```markdown
# Outbound Sequence Generation Framework

## Overview
Generate personalized multi-touch outbound sequences based on prospect data.

## Input Requirements
- Prospect data (name, title, company, industry)
- Company research (recent news, tech stack, challenges)
- Trigger event (if any)

## Sequence Structure

### Touch Cadence
| Day | Channel | Type |
|-----|---------|------|
| 0 | Email | Value-first intro |
| 2 | LinkedIn | Connection request + note |
| 4 | Email | Follow-up with insight |
| 7 | Phone | Discovery attempt |
| 10 | Email | Case study/social proof |
| 14 | LinkedIn | Engage with content |
| 17 | Email | Breakup/last chance |

## Email Templates

### Email 1: Value-First Intro

**Subject Line Formulas:**
- `{trigger_event} + {company}` → "Congrats on the Series B, {Company}"
- `{mutual_connection}` → "{Name} suggested I reach out"
- `{relevant_insight}` → "Noticed {Company} is expanding into {market}"

**Body Structure:**
```
[Personalized opener - 1 sentence referencing trigger/research]

[Value proposition - 2 sentences max, focused on their problem]

[Social proof - 1 sentence, similar company result]

[Soft CTA - question, not a meeting request]

[Signature]
```

**Example:**
```
Saw {Company} just closed a Series B - congrats! Scaling the GTM 
team is usually next.

We help companies like yours automate lead enrichment and scoring 
so SDRs focus on high-value conversations instead of data entry.

{Similar_Company} cut their lead response time by 60% in 30 days.

Curious - how are you thinking about scaling outbound with the 
new funding?

{Signature}
```

### Email 2: Follow-up with Insight

**Subject Line:** RE: [previous subject] (no change)

**Body Structure:**
```
[Quick reference to previous email]

[New insight specific to their business]

[Reframe value prop with new angle]

[Stronger CTA - specific ask]
```

### Email 3: Case Study / Social Proof

**Subject Line:** "How {Similar_Company} [achieved result]"

**Body Structure:**
```
[Acknowledge no response - no guilt]

[Lead with specific, relevant case study]

[Quantified results]

[One-liner connecting to their situation]

[Clear next step CTA]
```

### Email 4: Breakup

**Subject Line:** "Closing the loop"

**Body Structure:**
```
[Acknowledge timing may be off]

[Leave door open - one sentence]

[Offer alternative (content, intro, etc.)]

[Sign off warmly]
```

## Personalization Rules

### Must Have
- [ ] First name (never "Hi there")
- [ ] Company name (never generic)
- [ ] Industry-specific language
- [ ] One specific research point (news, tech stack, hiring)

### Nice to Have
- [ ] Mutual connection reference
- [ ] Trigger event (funding, hiring, expansion)
- [ ] Competitor mention (if relevant)
- [ ] Personalized PS line

### Never Do
- ❌ Fake personalization ("I noticed your LinkedIn profile...")
- ❌ Lying about mutual connections
- ❌ Criticizing competitor by name
- ❌ Multiple CTAs in one email
- ❌ Attachments in first email

## Output Format

```json
{
  "prospect": "alice@acme.com",
  "sequence": [
    {
      "day": 0,
      "channel": "email",
      "subject": "Congrats on the Series B, Acme",
      "body": "...",
      "personalization_elements": ["funding_trigger", "industry_specific"]
    },
    ...
  ],
  "personalization_score": 85,
  "notes": "Strong trigger event (Series B). Recommend LinkedIn warm-up first."
}
```
```

---

### 3. Lead Qualification Playbook

**File:** `skills/gtm/lead-qualification.md`

```markdown
# Lead Qualification Playbook

## Overview
Decision tree for qualifying and routing inbound leads.

## Qualification Criteria (BANT+)

### Budget
| Signal | Qualification |
|--------|---------------|
| Stated budget range | Direct → Score accordingly |
| Company size proxy | 50-500 employees = likely budget |
| Funding stage | Series A+ = likely budget |
| No signal | Neutral → Continue qualification |

### Authority
| Title | Authority Level |
|-------|-----------------|
| C-Suite, VP | High → Priority routing |
| Director | Medium → Standard routing |
| Manager | Low → Nurture first |
| IC, Student | Disqualify → Marketing nurture |

### Need
| Signal | Interpretation |
|--------|----------------|
| Specific use case mentioned | High intent |
| "Evaluating options" | Active buyer |
| "Just researching" | Early stage |
| Demo request | Highest intent |

### Timeline
| Signal | Urgency |
|--------|---------|
| "This quarter" | Hot |
| "This year" | Warm |
| "Eventually" | Cold |
| "Just exploring" | Nurture |

### Plus: Fit
Cross-reference with ICP scoring skill.

## Routing Decision Tree

```
START
  │
  ├─ Is email domain personal (gmail, yahoo, etc.)?
  │   ├─ YES → ROUTE: Marketing nurture
  │   └─ NO → Continue
  │
  ├─ Is domain in blocklist?
  │   ├─ YES → ROUTE: Disqualify
  │   └─ NO → Continue
  │
  ├─ Is company in target account list?
  │   ├─ YES → ROUTE: Named AE (priority)
  │   └─ NO → Continue
  │
  ├─ ICP Score ≥ 80?
  │   ├─ YES → ROUTE: SDR (priority)
  │   └─ NO → Continue
  │
  ├─ ICP Score ≥ 50?
  │   ├─ YES → ROUTE: SDR (standard)
  │   └─ NO → Continue
  │
  └─ ICP Score < 50
      └─ ROUTE: Marketing nurture
```

## Routing Destinations

| Route | Owner | SLA | Action |
|-------|-------|-----|--------|
| Named AE (priority) | Account Executive | 2h | Immediate outreach |
| SDR (priority) | SDR | 4h | Research + outreach |
| SDR (standard) | SDR Pool | 24h | Standard cadence |
| Marketing nurture | Automated | N/A | Add to drip campaign |
| Disqualify | None | N/A | Log reason, no action |

## Output Format

```json
{
  "lead_email": "alice@acme.com",
  "qualification": {
    "budget": "likely",
    "authority": "high",
    "need": "specific_use_case",
    "timeline": "this_quarter",
    "fit_score": 85
  },
  "route": "SDR (priority)",
  "owner": "sdr-pool",
  "sla_hours": 4,
  "notes": "Series B company, VP title, demo request - hot lead"
}
```
```

---

## REFERENCING SKILLS IN CLAUDE.md

```markdown
# CLAUDE.md

## Project Context
This is the GTM Engineering system for lead processing.

## Available Skills
When working on lead-related tasks, reference these methodologies:

- **ICP Scoring**: `skills/gtm/icp-scoring.md`
  Use when scoring any lead against our Ideal Customer Profile.

- **Outbound Sequences**: `skills/gtm/outbound-sequence.md`
  Use when generating personalized outbound email sequences.

- **Lead Qualification**: `skills/gtm/lead-qualification.md`
  Use when routing inbound leads to appropriate owners.

## How to Use Skills
1. Read the relevant skill file completely
2. Follow the methodology step-by-step
3. Output in the specified format
4. Flag any edge cases for human review
```

---

## BEST PRACTICES

### 1. Version Control
Include changelog in each skill. Track who updated and when.

### 2. Structured Outputs
Always define exact JSON output format for downstream processing.

### 3. Edge Cases
Document exceptions explicitly. "If X, then do Y instead."

### 4. Cross-References
Link related skills: "For scoring, see `icp-scoring.md`"

### 5. Human Override Points
Mark where human judgment is required: "Flag for review if..."

---

## FILE STRUCTURE FOR THIS TEMPLATE

```
05-SKILLS/
├── README.md                          # This file
├── skills/
│   └── gtm/
│       ├── SKILL.md                   # Manifest
│       ├── icp-scoring.md             # Scoring methodology
│       ├── outbound-sequence.md       # Sequence framework
│       └── lead-qualification.md      # Qualification playbook
└── CLAUDE.md.example                  # Example CLAUDE.md references
```

---

## INSTALLATION

```bash
# Create skills directory
mkdir -p skills/gtm

# Copy skill files
cp skills/gtm/*.md ./skills/gtm/

# Update CLAUDE.md to reference skills
# See CLAUDE.md.example

# Test
# In Claude Code: "Score the lead alice@acme.com using our ICP criteria"
```
