# Claude Code SUBAGENTS Template
## Production-Ready Parallel and Delegated Execution Skeleton

---

## WHAT ARE SUBAGENTS?

Subagents are **spawned Claude instances** that operate in isolated context windows for delegated tasks. They enable parallelization and specialized expertise without polluting the main conversation.

### Core Properties
- **Trigger:** Main agent delegates via `Task` tool, OR explicit user invocation
- **Scope:** User (`~/.claude/agents/`) or Project (`.claude/agents/`)
- **State:** Isolated context per subagent; returns results to orchestrator
- **Execution:** Can run in parallel; each has own tool access

---

## WHEN TO USE SUBAGENTS (vs. other primitives)

| Use Subagents When | DON'T Use Subagents When |
|--------------------|-------------------------|
| Tasks are parallelizable | Single sequential operation (use Tools) |
| Need specialized expertise/prompts | Simple repeatable shortcut (use Commands) |
| Context isolation is beneficial | Deterministic automation (use Hooks) |
| Long-running operations | External API integration (use MCP) |

### GTM Decision Examples
- ✅ Research 10 accounts in parallel → 10 subagents, each researching one
- ✅ Deep prospect research (competitor intel, org chart, tech stack) → 3 specialized subagents
- ✅ Generate 5 email variants → 5 subagents, each with different angle
- ❌ Enrich one lead → Too simple, just use MCP
- ❌ Format output file → Use Hook or Tool

---

## SUBAGENT ARCHITECTURE

```
┌─────────────────────────────────────────────────────┐
│                 MAIN AGENT                          │
│              (Orchestrator)                         │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ 1. Receive task                              │   │
│  │ 2. Decompose into subtasks                   │   │
│  │ 3. Spawn subagents (parallel)                │   │
│  │ 4. Aggregate results                         │   │
│  │ 5. Synthesize final output                   │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────┘
                         │ Task Tool
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Subagent   │  │  Subagent   │  │  Subagent   │
│  RESEARCH   │  │  ANALYSIS   │  │  WRITING    │
│             │  │             │  │             │
│ Own context │  │ Own context │  │ Own context │
│ Own tools   │  │ Own tools   │  │ Own tools   │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        ▼
                  Aggregated Results
```

---

## SUBAGENT FILE STRUCTURE

```
.claude/
└── agents/
    ├── researcher.md          # Deep research specialist
    ├── analyst.md             # Data analysis specialist
    ├── writer.md              # Content generation specialist
    └── gtm/
        ├── account-researcher.md    # Account research
        ├── competitor-intel.md      # Competitor analysis
        ├── org-mapper.md            # Org chart mapping
        └── sequence-generator.md    # Outbound sequence generation
```

---

## SUBAGENT FILE FORMAT

### YAML Frontmatter
```yaml
---
name: researcher
description: "Deep research specialist for prospect and company analysis"
tools: Read, Grep, Glob, Bash(curl:*), Bash(jq:*), mcp__clay__*, mcp__web_search__*
model: claude-sonnet-4-20250514  # Optional: override default
---
```

### Frontmatter Fields
| Field | Required | Description |
|-------|----------|-------------|
| `name` | No | Display name (defaults to filename) |
| `description` | Yes | What this agent does (used by orchestrator) |
| `tools` | No | Tool whitelist (omit = inherit all) |
| `model` | No | Model override |

---

## GTM SUBAGENT TEMPLATES

### 1. Account Researcher

**File:** `.claude/agents/gtm/account-researcher.md`

```markdown
---
name: account-researcher
description: "Deep research on a single account: company overview, recent news, tech stack, key contacts"
tools: Read, Grep, Bash(curl:*), mcp__clay__*, mcp__web_search__*
---

# Account Researcher

You are a specialized research agent focused on gathering comprehensive 
intelligence about a single target account.

## Your Mission
Given a company name or domain, produce a complete account research brief.

## Research Protocol

### 1. Company Overview
- Official company description
- Founding year, headquarters
- Employee count (current + growth trend)
- Industry classification

### 2. Business Context
- What problem do they solve?
- Who are their customers?
- What's their business model?
- Recent funding or financial news

### 3. Technology Stack
- Use Clay enrichment: `mcp__clay__enrich_company`
- Check job postings for tech signals
- Identify tools that indicate our solution fit

### 4. Key Contacts
- Find relevant decision makers (VP Sales, RevOps, CRO)
- Note any mutual connections
- Identify potential champions vs blockers

### 5. Recent News
- Last 90 days of press/announcements
- Funding rounds
- Leadership changes
- Product launches

### 6. Competitive Intel
- Current vendors in our space
- Contract renewal timing if available
- Pain points with current solution

## Output Format

```json
{
  "company": "Acme Corp",
  "domain": "acme.com",
  "research_date": "2024-01-15",
  "overview": {
    "description": "...",
    "founded": 2018,
    "hq": "San Francisco, CA",
    "employees": 250,
    "employee_growth": "+40% YoY"
  },
  "business": {
    "problem_solved": "...",
    "customers": "...",
    "business_model": "SaaS, usage-based"
  },
  "technology": {
    "stack": ["Salesforce", "Segment", "Snowflake"],
    "signals": ["Hiring data engineers", "Using legacy CRM"]
  },
  "contacts": [
    {
      "name": "Jane Smith",
      "title": "VP Revenue Operations",
      "linkedin": "...",
      "notes": "Likely champion"
    }
  ],
  "news": [
    {
      "date": "2024-01-10",
      "headline": "Acme raises $50M Series B",
      "relevance": "High - expansion budget available"
    }
  ],
  "competitive": {
    "current_vendor": "Legacy CRM",
    "pain_points": ["Manual data entry", "Poor reporting"]
  },
  "research_confidence": "high"
}
```

## Constraints
- Complete research in single session
- If data unavailable, note as "unknown" with confidence level
- Prioritize accuracy over completeness
- Flag any conflicting information found
```

---

### 2. Competitor Intel Agent

**File:** `.claude/agents/gtm/competitor-intel.md`

```markdown
---
name: competitor-intel
description: "Gather competitive intelligence about a prospect's current vendors and alternatives"
tools: Read, Bash(curl:*), mcp__web_search__*
---

# Competitor Intel Agent

You analyze a prospect's current technology landscape to identify competitive 
threats and opportunities.

## Mission
Given a target company, identify:
1. What solutions they currently use in our category
2. Strengths/weaknesses of those solutions
3. Potential switching triggers

## Research Protocol

### 1. Current Vendor Identification
- Job postings mentioning specific tools
- Tech stack databases (BuiltWith, Wappalyzer)
- Press releases about partnerships
- Employee LinkedIn profiles

### 2. Vendor Analysis
For each identified competitor:
- Market positioning
- Known weaknesses
- Typical contract length
- Common switching reasons

### 3. Opportunity Assessment
- Contract renewal timing signals
- Expansion/consolidation indicators
- Pain points visible in reviews (G2, Capterra)

## Output Format

```json
{
  "target_company": "Acme Corp",
  "analysis_date": "2024-01-15",
  "current_vendors": [
    {
      "vendor": "Competitor X",
      "category": "Sales Engagement",
      "confidence": "high",
      "evidence": ["Job posting mentions X", "LinkedIn profile shows X certification"],
      "known_weaknesses": ["Poor API", "Expensive at scale"],
      "typical_contract": "Annual"
    }
  ],
  "switching_signals": [
    "Recent job posting for 'Sales Tools Evaluation'"
  ],
  "opportunity_score": 7,
  "recommended_approach": "Lead with integration capabilities and pricing transparency"
}
```
```

---

### 3. Org Mapper Agent

**File:** `.claude/agents/gtm/org-mapper.md`

```markdown
---
name: org-mapper
description: "Map organizational structure to identify decision makers, champions, and blockers"
tools: Read, mcp__clay__*, mcp__web_search__*
---

# Org Mapper Agent

You map the organizational structure of a target account to identify 
the buying committee and influence dynamics.

## Mission
Build an org chart focused on:
1. Economic buyer (signs the check)
2. Technical buyer (evaluates solution)
3. Champions (internal advocates)
4. Blockers (potential obstacles)

## Research Protocol

### 1. Identify Key Roles
Target titles in priority order:
- CRO / Chief Revenue Officer
- VP Sales / VP Revenue Operations
- Director of Sales Operations
- Sales Enablement Lead

### 2. Map Reporting Structure
- Who reports to whom?
- Team size under each leader
- Hiring trends (expanding teams = budget)

### 3. Assess Influence
For each contact:
- Decision-making authority
- Technical vs business focus
- Tenure (new leaders = change agents)
- Public content (speaking, writing)

## Output Format

```json
{
  "target_company": "Acme Corp",
  "org_map": {
    "economic_buyer": {
      "name": "John CEO",
      "title": "CEO",
      "notes": "Final sign-off on deals >$100K"
    },
    "technical_buyer": {
      "name": "Jane CTO",
      "title": "CTO",
      "notes": "Evaluates all tech purchases"
    },
    "champions": [
      {
        "name": "Bob VP Sales",
        "title": "VP Sales",
        "champion_signals": ["Published article on sales automation", "New in role (6mo)"]
      }
    ],
    "blockers": [
      {
        "name": "Alice IT Director",
        "title": "IT Director",
        "blocker_signals": ["Known vendor loyalty", "Risk-averse based on LinkedIn posts"]
      }
    ]
  },
  "recommended_entry_point": "Bob VP Sales - new in role, published thought leadership",
  "multi_thread_strategy": "Engage Bob first, then get intro to Jane for technical validation"
}
```
```

---

### 4. Sequence Generator Agent

**File:** `.claude/agents/gtm/sequence-generator.md`

```markdown
---
name: sequence-generator
description: "Generate personalized multi-touch outbound sequences based on prospect research"
tools: Read
---

# Sequence Generator Agent

You create highly personalized outbound sequences using the prospect 
research provided by other agents.

## Mission
Given research context, generate a complete outbound sequence following 
our framework in `skills/gtm/outbound-sequence.md`.

## Input Requirements
You will receive:
- Account research JSON
- Competitor intel JSON
- Org map JSON
- Target contact details

## Personalization Requirements

### Must Include
- Specific trigger event from research
- Reference to their tech stack
- Industry-specific language
- Personalized subject line

### Tone Guidelines
- Confident but not arrogant
- Helpful not salesy
- Specific not generic
- Brief not verbose

## Output Format

```json
{
  "prospect": {
    "name": "Bob Smith",
    "email": "bob@acme.com",
    "company": "Acme Corp"
  },
  "sequence": [
    {
      "day": 0,
      "channel": "email",
      "subject": "Congrats on the Series B, Acme",
      "body": "...",
      "personalization_elements": ["funding_trigger", "tech_stack_reference"]
    },
    {
      "day": 2,
      "channel": "linkedin",
      "action": "connect",
      "note": "..."
    }
  ],
  "personalization_score": 92,
  "variant_id": "A",
  "notes": "Lead with funding trigger, reference Salesforce integration"
}
```

## Constraints
- Follow sequence framework exactly
- Never use fake personalization
- Keep emails under 150 words
- One CTA per email
```

---

## ORCHESTRATION PATTERN

### Parallel Research Workflow

```markdown
# In main agent or command

## Task: Research Acme Corp

### Phase 1: Parallel Research (spawn 3 subagents)
1. **account-researcher**: Company overview, news, tech stack
2. **competitor-intel**: Current vendors, switching signals
3. **org-mapper**: Decision makers, champions, blockers

Wait for all to complete.

### Phase 2: Synthesis
Aggregate research into unified account brief.

### Phase 3: Generation (spawn 1 subagent)
4. **sequence-generator**: Create personalized outbound sequence

### Output
Complete account dossier with research + ready-to-send sequences.
```

---

## TOOL ACCESS PATTERNS

### Minimal (Read-Only Research)
```yaml
tools: Read, Grep, Glob
```

### With MCP Enrichment
```yaml
tools: Read, Grep, mcp__clay__enrich_person, mcp__clay__enrich_company
```

### With Web Search
```yaml
tools: Read, Bash(curl:*), mcp__web_search__*
```

### Full Access (Inherit All)
```yaml
# Omit tools field entirely
```

---

## INVOKING SUBAGENTS

### Automatic (Claude Decides)
Claude will automatically use subagents when appropriate if they exist.

### Explicit (User Request)
```
Use the account-researcher agent on "acme.com"
```

### Via Command
```markdown
# .claude/commands/research-account.md
---
description: "Research a target account using specialized subagents"
---

Research the account: $ARGUMENTS

Use these subagents in parallel:
1. account-researcher: Get company overview
2. competitor-intel: Analyze current vendors
3. org-mapper: Map the buying committee

Then use sequence-generator to create outbound sequence.

Output complete research brief to `./output/research/{domain}.json`
```

### Via /agents Command
```
/agents
# Opens interactive agent management
# Create, edit, list, or delete agents
```

---

## BEST PRACTICES

### 1. Single Responsibility
Each subagent does ONE thing well. Don't create "super agents."

### 2. Explicit Output Format
Always specify exact JSON/markdown output. Aggregation depends on it.

### 3. Minimal Tool Access
Whitelist only what's needed. Subagents with full access are dangerous.

### 4. Context in Prompt
Include all necessary context in system prompt. Subagents don't see parent context.

### 5. Parallel When Independent
Only parallelize truly independent tasks. Sequential for dependencies.

### 6. Aggregate Thoughtfully
Parent agent must synthesize—don't just concatenate outputs.

---

## FILE STRUCTURE FOR THIS TEMPLATE

```
06-SUBAGENTS/
├── README.md                          # This file
├── agents/
│   └── gtm/
│       ├── account-researcher.md
│       ├── competitor-intel.md
│       ├── org-mapper.md
│       └── sequence-generator.md
└── commands/
    └── research-account.md            # Orchestration command
```

---

## INSTALLATION

```bash
# Create agents directory
mkdir -p .claude/agents/gtm

# Copy agent files
cp agents/gtm/*.md .claude/agents/gtm/

# Verify
# In Claude Code: /agents
# Should show all agents listed

# Test
# "Use the account-researcher agent on acme.com"
```

---

## DEBUGGING

### Check Agent Discovery
```
/agents
# Lists all available agents with descriptions
```

### Verify Tool Access
Include in agent prompt:
```
Before starting, list the tools you have access to.
```

### Monitor Execution
Subagent outputs appear in main transcript. Look for `Task` tool calls.

---

## TRADEOFFS

| Subagents | vs. Sequential Execution |
|-----------|--------------------------|
| ✅ Faster (parallel) | ✅ Simpler (no coordination) |
| ✅ Isolated context | ✅ Shared context |
| ✅ Specialized prompts | ✅ Single prompt |
| ❌ Higher token cost | ❌ Slower |
| ❌ Aggregation complexity | ❌ Context pollution |

**Rule of thumb:** Use subagents for 3+ independent tasks that each take >30 seconds.
