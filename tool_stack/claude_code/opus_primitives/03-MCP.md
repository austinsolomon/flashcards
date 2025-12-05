# Claude Code MCP Template
## Production-Ready Model Context Protocol Integration Skeleton

---

## WHAT IS MCP?

MCP (Model Context Protocol) is an **open standard for AI-tool integrations** that allows Claude Code to connect to external services, APIs, and databases as native tools. MCP servers handle authentication, rate limiting, and structured responses.

### Core Properties
- **Trigger:** Claude decides when to use MCP tools based on task requirements
- **Scope:** User (`--scope user`) or Project (`--scope project`)
- **Transport:** HTTP, SSE (deprecated), or Stdio (local processes)
- **State:** MCP servers maintain their own state (auth, sessions)

---

## WHEN TO USE MCP (vs. other primitives)

| Use MCP When | DON'T Use MCP When |
|--------------|-------------------|
| Integrating external APIs (CRM, enrichment, etc.) | Simple bash scripts suffice (use Tools) |
| Need persistent auth handling (OAuth, API keys) | One-off API calls (use bash + curl) |
| Want structured, typed responses | Task is purely local file manipulation |
| Service has existing MCP server | Building from scratch is faster than MCP |

### GTM Decision Examples
- ✅ Clay enrichment API → Use MCP (auth, rate limits, structured data)
- ✅ HubSpot CRM → Use MCP (OAuth, complex API surface)
- ✅ Gong call recordings → Use MCP (auth, pagination)
- ❌ Parse a local JSON file → Use bash/jq
- ❌ Send one-off webhook → Use curl in bash tool

---

## MCP ARCHITECTURE

```
┌─────────────────────────────────────────────────────┐
│                   Claude Code                        │
│                  (MCP Client)                        │
└────────────────────────┬────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Clay MCP    │  │ HubSpot MCP │  │ Gong MCP    │
│ Server      │  │ Server      │  │ Server      │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Clay API    │  │ HubSpot API │  │ Gong API    │
└─────────────┘  └─────────────┘  └─────────────┘
```

---

## TRANSPORT TYPES

### HTTP (Recommended for Remote)
```bash
# Basic
claude mcp add --transport http <name> <url>

# With auth
claude mcp add --transport http notion https://mcp.notion.com/mcp \
  --header "Authorization: Bearer $NOTION_TOKEN"
```

### Stdio (Local Processes)
```bash
# NPX-based server
claude mcp add --transport stdio clay \
  --env CLAY_API_KEY=$CLAY_API_KEY \
  -- npx -y @anthropic/mcp-server-clay

# Local script
claude mcp add --transport stdio custom-enrichment \
  -- python3 ./mcp-servers/enrichment.py
```

### SSE (Deprecated)
```bash
# Still supported but use HTTP when possible
claude mcp add --transport sse asana https://mcp.asana.com/sse
```

---

## CONFIGURATION METHODS

### Method 1: CLI (Recommended)
```bash
# Add server
claude mcp add <name> --scope user -- <command>

# Add with JSON config
claude mcp add-json hubspot '{
  "command": "npx",
  "args": ["-y", "@hubspot/mcp-server"],
  "env": {"HUBSPOT_API_KEY": "'$HUBSPOT_API_KEY'"}
}'

# List servers
claude mcp list

# Remove server
claude mcp remove <name>

# Test server
claude mcp get <name>
```

### Method 2: Config File
Location: `~/.claude/settings.json` or `.claude/settings.local.json`

```json
{
  "mcpServers": {
    "clay": {
      "command": "npx",
      "args": ["-y", "@clay/mcp-server"],
      "env": {
        "CLAY_API_KEY": "your-key-here"
      }
    },
    "hubspot": {
      "command": "npx",
      "args": ["-y", "@hubspot/mcp-server"],
      "env": {
        "HUBSPOT_API_KEY": "your-key-here"
      }
    }
  }
}
```

### Method 3: Project-Scoped (.mcp.json)
```json
{
  "mcpServers": {
    "project-specific": {
      "command": "python3",
      "args": ["./mcp-servers/custom.py"],
      "env": {}
    }
  }
}
```

---

## GTM MCP SETUP

### 1. Clay (Lead Enrichment)

```bash
# Install
claude mcp add --transport stdio clay \
  --scope user \
  --env CLAY_API_KEY=$CLAY_API_KEY \
  -- npx -y @clay/mcp-server-clay

# Usage in Claude Code
# "Enrich the lead alice@acme.com with Clay"
# Claude will call: mcp__clay__enrich_person
```

**Available Tools:**
- `mcp__clay__enrich_person` - Firmographic data from email
- `mcp__clay__enrich_company` - Company data from domain
- `mcp__clay__find_contacts` - Find contacts at company

---

### 2. HubSpot (CRM)

```bash
# Install
claude mcp add-json hubspot --scope user '{
  "command": "npx",
  "args": ["-y", "@hubspot/mcp-server"],
  "env": {
    "HUBSPOT_ACCESS_TOKEN": "'$HUBSPOT_ACCESS_TOKEN'"
  }
}'

# Usage in Claude Code
# "Create a contact for alice@acme.com in HubSpot"
# Claude will call: mcp__hubspot__create_contact
```

**Available Tools:**
- `mcp__hubspot__create_contact`
- `mcp__hubspot__update_contact`
- `mcp__hubspot__get_contact`
- `mcp__hubspot__create_deal`
- `mcp__hubspot__list_deals`

---

### 3. Gong (Conversation Intelligence)

```bash
# Install
claude mcp add-json gong --scope user '{
  "command": "npx",
  "args": ["-y", "@gong/mcp-server"],
  "env": {
    "GONG_ACCESS_KEY": "'$GONG_ACCESS_KEY'",
    "GONG_ACCESS_SECRET": "'$GONG_ACCESS_SECRET'"
  }
}'

# Usage in Claude Code
# "Find calls with Acme Corp from last month"
# Claude will call: mcp__gong__search_calls
```

**Available Tools:**
- `mcp__gong__search_calls`
- `mcp__gong__get_call_transcript`
- `mcp__gong__get_call_summary`

---

### 4. Slack (Team Communication)

```bash
# Install
claude mcp add-json slack --scope user '{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-slack"],
  "env": {
    "SLACK_BOT_TOKEN": "'$SLACK_BOT_TOKEN'"
  }
}'

# Usage in Claude Code
# "Post the lead summary to #inbound-leads"
# Claude will call: mcp__slack__post_message
```

---

### 5. GitHub (Code + Issues)

```bash
# Install
claude mcp add-json github --scope user '{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "'$GITHUB_TOKEN'"
  }
}'

# Usage in Claude Code
# "Create an issue for the lead qualification bug"
# Claude will call: mcp__github__create_issue
```

---

## CUSTOM MCP SERVER (Python)

For internal tools without existing MCP servers:

```python
#!/usr/bin/env python3
"""
Custom MCP Server for GTM Lead Scoring
Exposes internal ICP scoring as MCP tool
"""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json

server = Server("gtm-scoring")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="score_lead",
            description="Score a lead against ICP criteria",
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "Lead email"},
                    "company_data": {"type": "object", "description": "Enriched company data"}
                },
                "required": ["email", "company_data"]
            }
        ),
        Tool(
            name="get_icp_criteria",
            description="Get current ICP scoring criteria",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "score_lead":
        score = calculate_icp_score(arguments["company_data"])
        return [TextContent(
            type="text",
            text=json.dumps({
                "email": arguments["email"],
                "score": score,
                "tier": "A" if score > 80 else "B" if score > 50 else "C"
            })
        )]
    
    elif name == "get_icp_criteria":
        with open("./config/icp-criteria.json") as f:
            return [TextContent(type="text", text=f.read())]

def calculate_icp_score(data: dict) -> int:
    score = 0
    
    # Employee count scoring
    employees = data.get("employee_count", 0)
    if 50 <= employees <= 500:
        score += 25
    elif employees > 500:
        score += 15
    
    # Funding scoring
    funding = data.get("funding_stage", "")
    if funding in ["Series A", "Series B", "Series C"]:
        score += 25
    
    # Tech stack scoring
    tech_stack = data.get("tech_stack", [])
    target_tech = ["Salesforce", "HubSpot", "Segment", "Amplitude"]
    matches = len(set(tech_stack) & set(target_tech))
    score += matches * 10
    
    return min(score, 100)

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Installation:**
```bash
# Install MCP SDK
pip install mcp

# Register custom server
claude mcp add --transport stdio gtm-scoring \
  -- python3 ./mcp-servers/gtm-scoring.py
```

---

## TOKEN MANAGEMENT

MCP outputs can be large. Configure limits:

```bash
# Increase limit for large outputs
export MAX_MCP_OUTPUT_TOKENS=50000
claude
```

Default: 25,000 tokens. Warning at 10,000.

---

## BEST PRACTICES

### 1. User vs Project Scope
- **User (`--scope user`):** Personal API keys, global tools
- **Project (`--scope project`):** Team-shared configs, project-specific integrations

### 2. Secure API Keys
Never commit API keys. Use environment variables:
```bash
# In .bashrc or .zshrc
export CLAY_API_KEY="your-key"
export HUBSPOT_ACCESS_TOKEN="your-token"
```

### 3. Test Before Using
```bash
# Verify server is working
claude mcp get <name>

# Check available tools
# In Claude Code: "What MCP tools do you have access to?"
```

### 4. Rate Limit Awareness
MCP servers handle rate limits, but be mindful of:
- Parallel subagent calls hitting same API
- Batch operations that may trigger limits

### 5. Error Handling
MCP servers should return structured errors. Log failures for debugging.

---

## FILE STRUCTURE FOR THIS TEMPLATE

```
03-MCP/
├── README.md                          # This file
├── config/
│   ├── settings.json                  # User-level MCP config
│   └── .mcp.json                      # Project-level MCP config
├── mcp-servers/
│   ├── gtm-scoring.py                # Custom ICP scoring server
│   └── requirements.txt              # Python dependencies
└── examples/
    ├── setup-gtm-stack.sh            # Full GTM MCP setup script
    └── test-mcp-tools.md             # Testing guide
```

---

## INSTALLATION

```bash
# 1. Set environment variables
export CLAY_API_KEY="your-clay-key"
export HUBSPOT_ACCESS_TOKEN="your-hubspot-token"
export GONG_ACCESS_KEY="your-gong-key"
export GONG_ACCESS_SECRET="your-gong-secret"

# 2. Run setup script (or add individually)
./examples/setup-gtm-stack.sh

# 3. Verify
claude mcp list

# 4. Test in Claude Code
# "What MCP servers are connected?"
# "Enrich the lead test@example.com with Clay"
```

---

## TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| Server not connecting | Check `~/.claude/logs/mcp-server-*.log` |
| Auth failures | Verify env vars: `echo $CLAY_API_KEY` |
| Timeout errors | Increase timeout in settings |
| "Tool not found" | Run `claude mcp list` to verify registration |
