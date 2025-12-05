# Claude Code HOOKS Template
## Production-Ready Event-Triggered Automation Skeleton

---

## WHAT ARE HOOKS?

Hooks are **event-triggered shell commands** that execute automatically at specific points in Claude Code's lifecycle. They provide **deterministic automation** without relying on Claude's discretion.

### Core Properties
- **Trigger:** System events (PreToolUse, PostToolUse, etc.)
- **Execution:** Shell commands or Python scripts
- **Scope:** User (`~/.claude/settings.json`) or Project (`.claude/settings.json`)
- **Control:** Can block, modify, or log tool calls

---

## WHEN TO USE HOOKS (vs. other primitives)

| Use Hooks When | DON'T Use Hooks When |
|----------------|----------------------|
| Action must happen EVERY time (deterministic) | Action should only happen sometimes (use Claude's judgment) |
| Response to system events | Response to user input (use Commands) |
| Pre/post processing of tool calls | Complex multi-step reasoning (use Subagents) |
| Validation, logging, formatting | External API calls (use MCP) |

### GTM Decision Examples
- ✅ Auto-validate leads before any write operation
- ✅ Log all CRM API calls for compliance
- ✅ Format markdown after any file edit
- ❌ Decide whether to escalate a lead (requires reasoning)
- ❌ Generate personalized email copy (requires creativity)

---

## HOOK LIFECYCLE EVENTS

| Event | Fires When | Common Use Cases |
|-------|------------|------------------|
| `PreToolUse` | Before any tool executes | Block dangerous ops, validate inputs, modify parameters |
| `PostToolUse` | After tool completes successfully | Format files, log operations, trigger notifications |
| `UserPromptSubmit` | User submits a prompt | Validate prompts, inject context, block patterns |
| `Notification` | Claude sends a notification | Custom alerts, Slack/email integration |
| `Stop` | Main agent finishes responding | Summarize session, cleanup, metrics |
| `SubagentStop` | Subagent finishes | Aggregate results, chain to next agent |
| `PreCompact` | Before context compaction | Backup transcripts |
| `SessionStart` | New session begins | Load project context, set environment |
| `SessionEnd` | Session terminates | Cleanup, final logging |

---

## CONFIGURATION STRUCTURE

Hooks are configured in `settings.json`:

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",
        "hooks": [
          {
            "type": "command",
            "command": "your-shell-command",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Matcher Patterns
| Pattern | Matches |
|---------|---------|
| `"Bash"` | Exactly the Bash tool |
| `"Edit\|Write"` | Edit OR Write tools |
| `"mcp__clay__*"` | All Clay MCP tools |
| `"*"` or `""` | ALL tools |

---

## INPUT/OUTPUT PROTOCOL

### Input (via stdin)
Hooks receive JSON with event context:

```json
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../session.jsonl",
  "cwd": "/path/to/project",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "curl https://api.clay.com/...",
    "description": "Enriching lead data"
  }
}
```

### Output (via stdout)
Hooks can control Claude's behavior:

```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow",
    "permissionDecisionReason": "Command validated successfully"
  }
}
```

### Permission Decisions (PreToolUse)
| Decision | Effect |
|----------|--------|
| `"allow"` | Bypass permission system, execute immediately |
| `"deny"` | Block tool call, show reason to Claude |
| `"ask"` | Prompt user for confirmation |

### Blocking Execution
```json
{
  "continue": false,
  "stopReason": "Blocked: sensitive file access detected"
}
```

---

## GTM HOOK TEMPLATES

### 1. Lead Validation (PreToolUse)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/validate-lead.py"
          }
        ]
      }
    ]
  }
}
```

**validate-lead.py:**
```python
#!/usr/bin/env python3
"""
Pre-write validation for lead data.
Blocks writes to leads/ directory if email is invalid or in blocklist.
"""
import json
import sys
import re

def main():
    # Read hook input from stdin
    data = json.load(sys.stdin)
    
    file_path = data.get("tool_input", {}).get("file_path", "")
    content = data.get("tool_input", {}).get("content", "")
    
    # Only validate writes to leads directory
    if "/leads/" not in file_path:
        # Allow all other writes
        print(json.dumps({"hookSpecificOutput": {"permissionDecision": "allow"}}))
        return
    
    # Extract email from content
    email_match = re.search(r'"email":\s*"([^"]+)"', content)
    if not email_match:
        print(json.dumps({
            "hookSpecificOutput": {
                "permissionDecision": "deny",
                "permissionDecisionReason": "Lead data must contain valid email field"
            }
        }))
        return
    
    email = email_match.group(1)
    
    # Validate email format
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        print(json.dumps({
            "hookSpecificOutput": {
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Invalid email format: {email}"
            }
        }))
        return
    
    # Check blocklist
    try:
        with open(f"{data['cwd']}/data/blocklist.txt") as f:
            blocklist = [line.strip().lower() for line in f]
        
        domain = email.split("@")[1].lower()
        if domain in blocklist:
            print(json.dumps({
                "hookSpecificOutput": {
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Domain {domain} is blocklisted"
                }
            }))
            return
    except FileNotFoundError:
        pass  # No blocklist, continue
    
    # All validations passed
    print(json.dumps({
        "hookSpecificOutput": {
            "permissionDecision": "allow",
            "permissionDecisionReason": f"Lead validation passed for {email}"
        }
    }))

if __name__ == "__main__":
    main()
```

---

### 2. CRM API Logging (PostToolUse)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "mcp__hubspot__*",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/log-crm-call.sh"
          }
        ]
      }
    ]
  }
}
```

**log-crm-call.sh:**
```bash
#!/bin/bash
# Log all HubSpot API calls for compliance and debugging

LOG_DIR="${CLAUDE_PROJECT_DIR}/logs/crm"
mkdir -p "$LOG_DIR"

# Read JSON from stdin
INPUT=$(cat)

# Extract relevant fields
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id')

# Create log entry
LOG_ENTRY=$(jq -n \
  --arg ts "$TIMESTAMP" \
  --arg tool "$TOOL_NAME" \
  --arg session "$SESSION_ID" \
  --argjson input "$(echo "$INPUT" | jq '.tool_input')" \
  --argjson response "$(echo "$INPUT" | jq '.tool_response')" \
  '{timestamp: $ts, tool: $tool, session: $session, input: $input, response: $response}')

# Append to daily log file
DATE=$(date +"%Y-%m-%d")
echo "$LOG_ENTRY" >> "${LOG_DIR}/${DATE}-hubspot.jsonl"

# Output nothing to allow normal processing
echo "{}"
```

---

### 3. Session Context Loading (SessionStart)

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/load-gtm-context.sh"
          }
        ]
      }
    ]
  }
}
```

**load-gtm-context.sh:**
```bash
#!/bin/bash
# Load GTM context at session start

echo "=== GTM Session Initialized ===" >&2

# Load environment
if [ -f "${CLAUDE_PROJECT_DIR}/.env.gtm" ]; then
    export $(cat "${CLAUDE_PROJECT_DIR}/.env.gtm" | xargs)
fi

# Show current pipeline status
PENDING_LEADS=$(find "${CLAUDE_PROJECT_DIR}/inbox/leads" -name "*.json" 2>/dev/null | wc -l)
PROCESSED_TODAY=$(find "${CLAUDE_PROJECT_DIR}/output/leads" -mtime 0 -name "*.json" 2>/dev/null | wc -l)

# Provide context to Claude via additionalContext
jq -n \
  --arg pending "$PENDING_LEADS" \
  --arg processed "$PROCESSED_TODAY" \
  '{
    hookSpecificOutput: {
      additionalContext: "GTM Context: \($pending) leads pending, \($processed) processed today. ICP criteria at ./config/icp-criteria.json"
    }
  }'
```

---

### 4. Protect Sensitive Files (PreToolUse)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|Read",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -c \"import json, sys; data=json.load(sys.stdin); path=data.get('tool_input',{}).get('file_path',''); sys.exit(0) if not any(p in path for p in ['.env', 'secrets/', 'credentials']) else print(json.dumps({'hookSpecificOutput':{'permissionDecision':'deny','permissionDecisionReason':'Access to sensitive files blocked'}}))\""
          }
        ]
      }
    ]
  }
}
```

---

## ENVIRONMENT VARIABLES

| Variable | Description |
|----------|-------------|
| `$CLAUDE_PROJECT_DIR` | Root directory of current project |
| `$CLAUDE_SESSION_ID` | Current session identifier |

---

## BEST PRACTICES

### 1. Use Absolute Paths
Hooks run from various contexts. Always use `$CLAUDE_PROJECT_DIR` for paths.

### 2. Fast Execution
Hooks block Claude's execution. Keep them under 1 second when possible.

### 3. Graceful Failures
Exit code 0 = success. Non-zero exits may halt Claude's operation.

### 4. JSON Output
Always output valid JSON. Malformed output causes undefined behavior.

### 5. Logging to stderr
Use `>&2` for debug output. stdout is parsed as hook response.

### 6. Targeted Matchers
Avoid `"*"` matchers unless truly needed. Specific matchers = faster execution.

---

## FILE STRUCTURE FOR THIS TEMPLATE

```
02-HOOKS/
├── README.md                           # This file
├── settings.json                       # Example settings configuration
└── hooks/
    ├── validate-lead.py               # PreToolUse: Lead validation
    ├── log-crm-call.sh                # PostToolUse: CRM logging
    ├── load-gtm-context.sh            # SessionStart: Context loading
    └── protect-sensitive.py           # PreToolUse: File protection
```

---

## INSTALLATION

```bash
# Create hooks directory
mkdir -p .claude/hooks

# Copy hook scripts
cp hooks/*.py hooks/*.sh .claude/hooks/
chmod +x .claude/hooks/*

# Add to settings.json (merge with existing)
# See settings.json template in this directory

# Test by triggering a tool call in Claude Code
```

---

## DEBUGGING

1. **Check logs:** `~/.claude/logs/hooks.log`
2. **Test manually:** `echo '{"tool_name":"Bash"}' | python3 .claude/hooks/your-hook.py`
3. **Verbose mode:** Add `set -x` to bash hooks or print to stderr in Python
