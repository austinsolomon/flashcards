# Claude Code COMMANDS Template
## Production-Ready Slash Command Skeleton

---

## WHAT ARE COMMANDS?

Slash commands are **user-invoked shortcuts** that bundle prompts, context, and tool constraints into a repeatable unit. They are markdown files that Claude Code executes when a user types `/command-name`.

### Core Properties
- **Trigger:** Human-initiated via `/command-name [arguments]`
- **Scope:** Project (`.claude/commands/`) or User (`~/.claude/commands/`)
- **State:** Stateless—each invocation is fresh
- **Format:** Markdown with optional YAML frontmatter

---

## WHEN TO USE COMMANDS (vs. other primitives)

| Use Commands When | DON'T Use Commands When |
|-------------------|-------------------------|
| Task is human-initiated | Task should trigger automatically (use Hooks) |
| Action is repeatable with variations | Action requires persistent state across calls (use Subagents) |
| You want discoverability via `/help` | You need external API integration (use MCP) |
| Team needs standardized playbooks | Task requires parallel execution (use Subagents) |

### GTM Decision Examples
- ✅ `/enrich-lead alice@acme.com` — Human triggers, repeatable, needs arguments
- ✅ `/score-account` — Rep wants ICP score on demand
- ❌ Auto-validate new leads from webhook — Use Hook instead
- ❌ Research 10 accounts in parallel — Use Subagents instead

---

## TEMPLATE STRUCTURE

```
.claude/
└── commands/
    ├── gtm/                          # Namespace subdirectory
    │   ├── enrich-lead.md            # → /enrich-lead
    │   ├── score-account.md          # → /score-account
    │   └── generate-outbound.md      # → /generate-outbound
    └── ops/
        └── sync-crm.md               # → /sync-crm
```

**Naming Convention:** `kebab-case.md` → `/kebab-case`

---

## FRONTMATTER REFERENCE

```yaml
---
# REQUIRED
description: "One-line description shown in /help"

# OPTIONAL - Tool Constraints
allowed-tools: Read, Grep, Bash(git *)    # Whitelist specific tools
denied-tools: Write                        # Blacklist specific tools

# OPTIONAL - Model Override
model: claude-sonnet-4-20250514           # Override default model

# OPTIONAL - Argument Hints
argument-hint: <email> [--force]          # Shown in /help

# OPTIONAL - Disable Model Invocation
disable-model-invocation: true            # Prevent auto-triggering by Claude
---
```

---

## GTM COMMAND TEMPLATE

```markdown
---
description: "Enrich a lead with firmographic data and score against ICP"
allowed-tools: Read, Bash(curl:*), Bash(jq:*)
argument-hint: <email>
---

# Lead Enrichment & ICP Scoring

## Input
Lead email: $ARGUMENTS

## Workflow

### 1. Validate Email
- Verify email format is valid
- Check not in blocklist at `./data/blocklist.txt`

### 2. Enrich via Clay API
Execute the following to get firmographic data:
```bash
curl -s "https://api.clay.com/v1/enrich?email=$ARGUMENTS" \
  -H "Authorization: Bearer $CLAY_API_KEY" | jq .
```

### 3. Score Against ICP
Read ICP criteria from `./config/icp-criteria.json` and score:
- Employee count: 50-500 = +20pts, 500+ = +10pts
- Tech stack match: Each match = +15pts
- Funding stage: Series A+ = +25pts

### 4. Output
Create enrichment report at `./output/leads/{email}.json` with:
- Raw enrichment data
- ICP score (0-100)
- Recommended next action

## Success Criteria
- Lead data saved to `./output/leads/`
- Score logged to stdout
- If score > 80, flag as "High Priority"
```

---

## DYNAMIC ARGUMENTS

| Placeholder | Behavior |
|-------------|----------|
| `$ARGUMENTS` | Captures everything after command name |
| `!command` | Interpolates shell command output into prompt |

### Examples
```markdown
# $ARGUMENTS example
Lead email: $ARGUMENTS
# Usage: /enrich-lead alice@acme.com → Lead email: alice@acme.com

# Shell interpolation example
Current git branch: !`git branch --show-current`
Recent commits:
!`git log --oneline -5`
```

---

## TOOL PERMISSION PATTERNS

```yaml
# Read-only analysis
allowed-tools: Read, Grep, Glob

# Git operations only
allowed-tools: Bash(git *)

# Specific external calls
allowed-tools: Bash(curl:*), Bash(jq:*)

# Everything except writes
denied-tools: Write, Edit
```

---

## BEST PRACTICES

### 1. Single Responsibility
Each command does ONE thing well. Chain commands for complex workflows.

### 2. Explicit Outputs
Always specify WHERE outputs should go and WHAT format they should be in.

### 3. Fail Fast
Include validation steps early in the workflow.

### 4. Idempotency
Commands should be safe to run multiple times with same inputs.

### 5. Documentation in Command
The command file IS the documentation—write it for humans AND Claude.

---

## FILE STRUCTURE FOR THIS TEMPLATE

```
01-COMMANDS/
├── README.md                     # This file
├── templates/
│   ├── basic-command.md          # Minimal starting point
│   ├── gtm-enrich-lead.md        # GTM: Lead enrichment
│   ├── gtm-score-account.md      # GTM: Account scoring
│   └── gtm-generate-sequence.md  # GTM: Outbound sequence
└── examples/
    └── production-commands/      # Real-world examples
```

---

## INSTALLATION

```bash
# Create project commands directory
mkdir -p .claude/commands/gtm

# Copy template
cp templates/gtm-enrich-lead.md .claude/commands/gtm/enrich-lead.md

# Test
# In Claude Code, type: /enrich-lead test@example.com
```
