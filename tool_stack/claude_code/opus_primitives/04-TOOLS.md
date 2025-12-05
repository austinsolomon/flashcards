# Claude Code TOOLS Template
## Production-Ready Atomic Operations Reference

---

## WHAT ARE TOOLS?

Tools are **atomic, stateless operations** that Claude Code can execute. They are the fundamental building blocks—discrete actions like reading a file, running a bash command, or making an API call.

### Core Properties
- **Trigger:** Claude decides when to invoke based on task requirements
- **Scope:** Built into Claude Code (no configuration needed)
- **State:** Stateless—each call is independent
- **Granularity:** Single operation (read ONE file, run ONE command)

---

## WHEN TO USE TOOLS (vs. other primitives)

| Use Tools When | DON'T Use Tools When |
|----------------|---------------------|
| Need a single discrete operation | Need multi-step reasoning (use Subagents) |
| Action is stateless | Need persistent auth (use MCP) |
| Built-in tools suffice | Need human-initiated shortcut (use Commands) |
| Direct file/bash operations | Need event-triggered automation (use Hooks) |

### GTM Decision Examples
- ✅ `Read` → Load ICP criteria from JSON file
- ✅ `Bash(curl)` → One-off API call to enrichment service
- ✅ `Write` → Save lead data to output file
- ❌ Complex enrichment workflow → Use Subagent with MCP
- ❌ Auto-format on every save → Use Hook instead

---

## BUILT-IN TOOLS REFERENCE

### File Operations

| Tool | Description | Example |
|------|-------------|---------|
| `Read` | Read file contents | Read `./config/icp-criteria.json` |
| `Write` | Create/overwrite file | Write lead data to `./output/lead.json` |
| `Edit` | Modify existing file | Update specific section of file |
| `MultiEdit` | Multiple edits in one file | Batch updates |
| `Glob` | Find files by pattern | `./leads/**/*.json` |
| `Grep` | Search file contents | Find all files containing "acme" |

### Execution

| Tool | Description | Example |
|------|-------------|---------|
| `Bash` | Run shell commands | `curl`, `jq`, `git`, etc. |
| `Task` | Spawn subagent | Delegate to specialized agent |

### Navigation

| Tool | Description | Example |
|------|-------------|---------|
| `LS` | List directory contents | Show files in `./inbox/` |
| `View` | Preview file/directory | Quick look at structure |

---

## PERMISSION CONFIGURATION

Tools can be allowed/denied in `settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Grep",
      "Glob",
      "Bash(git *)",
      "Bash(curl:*)",
      "Bash(jq:*)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Write(./production.*)",
      "Bash(rm -rf:*)"
    ]
  }
}
```

### Permission Patterns

| Pattern | Matches |
|---------|---------|
| `Read` | All read operations |
| `Read(./config/*)` | Reads in config directory |
| `Bash(git *)` | All git commands |
| `Bash(curl:*)` | All curl commands |
| `Bash(npm run lint)` | Exact command only |

---

## GTM TOOL USAGE PATTERNS

### Pattern 1: Read → Process → Write

```markdown
# Workflow: Load criteria, score lead, save result

1. Read ICP criteria:
   Read `./config/icp-criteria.json`

2. Read lead data:
   Read `./inbox/leads/alice@acme.json`

3. Process (Claude reasoning):
   Apply scoring logic from criteria to lead

4. Write result:
   Write scored lead to `./output/scored/alice@acme.json`
```

### Pattern 2: Bash for Quick API Calls

```bash
# One-off enrichment (when MCP is overkill)
curl -s "https://api.clay.com/v1/enrich?email=alice@acme.com" \
  -H "Authorization: Bearer $CLAY_API_KEY" | jq .

# Parse and extract
curl -s ... | jq '.company.employee_count'
```

### Pattern 3: Glob + Grep for Discovery

```bash
# Find all high-value leads
Glob: ./output/scored/*.json
Grep: "tier.*A" in matched files

# Find leads mentioning competitor
Grep: "competitor_name" in ./inbox/leads/**/*.json
```

### Pattern 4: Edit for Incremental Updates

```markdown
# Update specific field in existing file
Edit `./output/scored/alice@acme.json`:
  - Change "status": "pending" → "status": "contacted"
  - Add "contacted_at": "2024-01-15T10:00:00Z"
```

---

## TOOL CONSTRAINTS IN COMMANDS/SUBAGENTS

### Whitelisting (Recommended)
```yaml
---
allowed-tools: Read, Grep, Glob
---
# This command can ONLY read, search, never write
```

### Blacklisting
```yaml
---
denied-tools: Write, Edit, Bash
---
# This command can do anything EXCEPT these
```

### Specific Bash Commands
```yaml
---
allowed-tools: Read, Bash(git status), Bash(git log:*)
---
# Only git status and git log commands allowed
```

---

## TOOL COMPOSITION PATTERNS

### Sequential (Most Common)
```
Read → Process → Write
```
Each tool call is independent, Claude orchestrates sequence.

### Parallel (Via Subagents)
```
                 ┌─→ Subagent 1 (Read + Process)
Main Agent ──────┼─→ Subagent 2 (Read + Process)
                 └─→ Subagent 3 (Read + Process)
                              ↓
                     Aggregate Results
```
Tools within subagents run serially; subagents run in parallel.

### Conditional
```
Read config
  ↓
If condition A → Bash(command A)
If condition B → Write(file B)
```
Claude decides which tool based on context.

---

## BEST PRACTICES

### 1. Prefer Read Over Bash(cat)
```markdown
# Good
Read `./data/leads.json`

# Avoid
Bash: cat ./data/leads.json
```
`Read` is safer, faster, and better integrated.

### 2. Use Glob Before Read
```markdown
# Find first, then read specific files
Glob: ./inbox/*.json
# Returns: lead1.json, lead2.json, lead3.json

Read: ./inbox/lead1.json
# Now read specific file
```

### 3. Atomic Writes
Write complete files, don't partially update:
```markdown
# Good: Write complete updated content
Write `./output/lead.json`:
  {"email": "...", "score": 85, "status": "scored"}

# Avoid: Multiple partial writes
```

### 4. Bash for Pipelines
When you need multiple operations, use bash pipes:
```bash
# Single tool call with complex operation
cat ./leads/*.json | jq -s '.' | jq 'map(select(.score > 80))'
```

### 5. Fail Fast with Bash
Check command success before proceeding:
```bash
# Include error handling
curl -sf "https://api..." || echo "API call failed"
```

---

## TOOL SECURITY

### Never Allow
```json
{
  "permissions": {
    "deny": [
      "Bash(rm -rf:*)",
      "Bash(curl * | sh)",
      "Read(./.env*)",
      "Write(/etc/*)",
      "Bash(chmod 777:*)"
    ]
  }
}
```

### GTM-Specific Restrictions
```json
{
  "permissions": {
    "deny": [
      "Read(./customer-data/pii/*)",
      "Write(./production-exports/*)",
      "Bash(aws s3:*)"
    ]
  }
}
```

---

## TOOLS vs OTHER PRIMITIVES

| Aspect | Tools | Commands | Hooks | MCP |
|--------|-------|----------|-------|-----|
| Trigger | Claude decides | User invokes | System event | Claude decides |
| Scope | Built-in | Markdown files | JSON config | Server config |
| State | Stateless | Stateless | Stateless | Server-managed |
| Auth | None (bash handles) | None | None | Server-managed |
| Use case | Single ops | Repeatable prompts | Deterministic automation | External services |

---

## FILE STRUCTURE FOR THIS TEMPLATE

```
04-TOOLS/
├── README.md                          # This file
├── settings/
│   ├── permissions-readonly.json      # Read-only tool set
│   ├── permissions-gtm-safe.json      # GTM with safety rails
│   └── permissions-full.json          # Full access (dev only)
└── examples/
    ├── read-process-write.md          # Sequential pattern
    ├── discovery-workflow.md          # Glob + Grep pattern
    └── bash-pipelines.md              # Complex bash operations
```

---

## CONFIGURATION

Tools are built-in; configuration is about permissions.

**For GTM (Safe Default):**
```json
{
  "permissions": {
    "allow": [
      "Read",
      "Write(./output/**)",
      "Write(./logs/**)",
      "Grep",
      "Glob",
      "Bash(curl:*)",
      "Bash(jq:*)",
      "Bash(git *)"
    ],
    "deny": [
      "Read(./.env*)",
      "Read(./secrets/**)",
      "Write(./config/**)",
      "Bash(rm:*)",
      "Bash(aws:*)",
      "Bash(gcloud:*)"
    ]
  }
}
```

---

## KEY INSIGHT

Tools are the **atoms**. Everything else is **molecules**:
- Commands = Tool instructions in markdown
- Hooks = Tool triggers on events  
- MCP = External tool wrappers
- Subagents = Tool execution in parallel contexts

Master tools first—they're the foundation of everything Claude Code does.
