# Claude Code Primitives: Master Decision Tree
## The Complete Reference for Choosing the Right Primitive

---

## THE DECISION FLOWCHART

```
START: You have a task
         │
         ▼
┌────────────────────────┐
│ Is it triggered by a   │
│ HUMAN typing a command?│
└──────────┬─────────────┘
           │
     ┌─────┴─────┐
     │           │
    YES          NO
     │           │
     ▼           ▼
┌─────────┐  ┌────────────────────────┐
│ COMMAND │  │ Is it triggered by a   │
│         │  │ SYSTEM EVENT?          │
└─────────┘  └──────────┬─────────────┘
                        │
                  ┌─────┴─────┐
                  │           │
                 YES          NO
                  │           │
                  ▼           ▼
             ┌─────────┐  ┌────────────────────────┐
             │  HOOK   │  │ Does it require        │
             │         │  │ EXTERNAL API access?   │
             └─────────┘  └──────────┬─────────────┘
                                     │
                               ┌─────┴─────┐
                               │           │
                              YES          NO
                               │           │
                               ▼           ▼
                          ┌─────────┐  ┌────────────────────────┐
                          │   MCP   │  │ Is it a SINGLE atomic  │
                          │         │  │ operation?             │
                          └─────────┘  └──────────┬─────────────┘
                                                  │
                                            ┌─────┴─────┐
                                            │           │
                                           YES          NO
                                            │           │
                                            ▼           ▼
                                       ┌─────────┐  ┌────────────────────────┐
                                       │  TOOL   │  │ Is it a METHODOLOGY    │
                                       │         │  │ or PROCESS?            │
                                       └─────────┘  └──────────┬─────────────┘
                                                               │
                                                         ┌─────┴─────┐
                                                         │           │
                                                        YES          NO
                                                         │           │
                                                         ▼           ▼
                                                    ┌─────────┐  ┌───────────┐
                                                    │  SKILL  │  │ SUBAGENT  │
                                                    │         │  │ (parallel │
                                                    └─────────┘  │  or long) │
                                                                 └───────────┘
```

---

## QUICK REFERENCE MATRIX

| Primitive | Trigger | State | Config Location | Best For |
|-----------|---------|-------|-----------------|----------|
| **Command** | User types `/command` | Stateless | `.claude/commands/*.md` | Repeatable user-initiated tasks |
| **Hook** | System event | Stateless | `settings.json` | Deterministic automation |
| **MCP** | Claude decides | Server-managed | `settings.json` or `.mcp.json` | External API integration |
| **Tool** | Claude decides | Stateless | Built-in | Single atomic operations |
| **Skill** | Claude reads when relevant | Stateless | `skills/*.md` | Documented methodologies |
| **Subagent** | Delegation via Task | Isolated context | `.claude/agents/*.md` | Parallel/specialized work |

---

## THE PRIMITIVE HIERARCHY

```
                    ┌───────────────────┐
                    │     PLUGINS       │  ← Bundles of everything
                    │ (meta-container)  │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   COMMANDS    │     │     HOOKS     │     │  SUBAGENTS    │
│ (user-invoked)│     │(event-triggered)    │ (delegated)   │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
            ┌───────────────┐   ┌───────────────┐
            │    SKILLS     │   │      MCP      │
            │ (methodology) │   │ (external)    │
            └───────┬───────┘   └───────┬───────┘
                    │                   │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │      TOOLS        │  ← Atomic operations
                    │  (Read, Write,    │
                    │   Bash, etc.)     │
                    └───────────────────┘
```

---

## GTM DECISION SCENARIOS

### Scenario 1: "Enrich this lead"
```
User types command → COMMAND
Calls Clay API → MCP
Writes result → TOOL (Write)
```
**Answer: Command + MCP + Tool**

### Scenario 2: "Auto-validate all leads before saving"
```
Every time Write is called → HOOK (PreToolUse)
Check email format → Shell script
Block if invalid → Hook output
```
**Answer: Hook**

### Scenario 3: "Score leads using our ICP criteria"
```
Complex multi-factor logic → SKILL (icp-scoring.md)
Needs external enrichment → MCP (Clay)
Writes scored output → TOOL (Write)
```
**Answer: Skill + MCP + Tool**

### Scenario 4: "Research 10 target accounts"
```
10 independent tasks → SUBAGENTS (parallel)
Each researches one account → Subagent with MCP
Aggregate results → Main agent
```
**Answer: 10 Subagents**

### Scenario 5: "Log all CRM API calls"
```
After every HubSpot call → HOOK (PostToolUse)
Append to log file → Shell command
```
**Answer: Hook**

### Scenario 6: "Generate outbound sequence for this prospect"
```
User initiates → COMMAND
Follow sequence methodology → SKILL
Generate personalized content → Subagent (for quality)
```
**Answer: Command + Skill + Subagent**

---

## ANTI-PATTERNS (What NOT to Do)

### ❌ Hook for Complex Reasoning
```
# BAD: Hook trying to score leads
PostToolUse hook → python script that scores

# GOOD: Skill with methodology
Skill defines scoring → Claude reasons
```
**Why:** Hooks are for deterministic automation, not reasoning.

### ❌ Subagent for Simple Tasks
```
# BAD: Subagent to read one file
Spawn subagent → read file → return

# GOOD: Direct tool
Read tool directly
```
**Why:** Subagent overhead isn't worth it for simple ops.

### ❌ MCP for One-Off Calls
```
# BAD: MCP server for single curl
Full MCP setup → one API call

# GOOD: Bash with curl
Bash(curl) → direct API call
```
**Why:** MCP setup cost only pays off with repeated use.

### ❌ Command for Automatic Tasks
```
# BAD: Command that must run every time
/format-file after every edit

# GOOD: Hook
PostToolUse hook → auto-format
```
**Why:** Commands require human invocation.

### ❌ Skill Without Structure
```
# BAD: Skill that's just prose
"Score leads by looking at company size..."

# GOOD: Skill with clear structure
Tables, decision trees, output format
```
**Why:** Skills must be precise enough for consistent execution.

---

## COMPOSITION PATTERNS

### Pattern 1: Command → Skill → MCP → Tool
**Use case:** User-initiated task with methodology and external data
```
/score-lead alice@acme.com
     │
     ▼
Read skill: icp-scoring.md
     │
     ▼
MCP: Clay enrichment
     │
     ▼
Tool: Write scored result
```

### Pattern 2: Hook → Tool → Notification
**Use case:** Automatic validation with alerting
```
PreToolUse (Write)
     │
     ▼
Validation script
     │
     ├── Pass → Allow write
     └── Fail → Block + Slack alert
```

### Pattern 3: Command → Parallel Subagents → Aggregate
**Use case:** Parallel research with synthesis
```
/research-account acme.com
     │
     ▼
Spawn 3 subagents (parallel)
  ├── Account research
  ├── Competitor intel
  └── Org mapping
     │
     ▼
Aggregate in main agent
     │
     ▼
Output unified brief
```

### Pattern 4: MCP → Skill → Subagent
**Use case:** External data informs methodology for specialized work
```
MCP: Get enrichment data
     │
     ▼
Apply Skill: Determine approach
     │
     ▼
Subagent: Execute specialized task
```

---

## COST/BENEFIT ANALYSIS

| Primitive | Setup Cost | Execution Cost | Maintenance | Parallelization |
|-----------|------------|----------------|-------------|-----------------|
| Tool | None | Low | None | No |
| Command | Low (1 file) | Low | Low | No |
| Hook | Medium (JSON + script) | Very Low | Medium | No |
| Skill | Medium (1 file) | Low | Medium | No |
| MCP | High (server setup) | Medium | High | Via subagents |
| Subagent | Medium (1 file) | High (tokens) | Medium | Yes |

---

## TEMPLATE FILES SUMMARY

```
claude-code-primitives-templates/
├── 01-COMMANDS/
│   └── README.md           # Slash command templates
├── 02-HOOKS/
│   └── README.md           # Event automation templates
├── 03-MCP/
│   └── README.md           # External integration templates
├── 04-TOOLS/
│   └── README.md           # Atomic operations reference
├── 05-SKILLS/
│   └── README.md           # Methodology documentation templates
├── 06-SUBAGENTS/
│   └── README.md           # Parallel execution templates
└── 00-DECISION-TREE/
    └── README.md           # This file
```

---

## THE GOLDEN RULE

> **Start with the simplest primitive that solves the problem.**
> 
> Tool → Command → Hook → Skill → MCP → Subagent
> 
> Only move up the complexity ladder when the simpler option is insufficient.

---

## NEXT STEPS

1. **Identify your first use case** in GTM
2. **Walk through the decision tree** above
3. **Copy the relevant template** from the corresponding directory
4. **Customize for your specific needs**
5. **Test in Claude Code**
6. **Iterate based on results**

Start small. One command. One hook. One skill. Build mastery through incremental complexity.
