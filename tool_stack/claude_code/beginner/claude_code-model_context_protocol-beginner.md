# Model Context Protocol (MCP) in Claude Code

Model Context Protocol enables Claude Code to securely connect to external systems and data sources. MCP servers act as bridges, allowing Claude to access databases, APIs, file systems, and custom tools seamlessly during conversations.

## Beginner Example

**Concept:** Basic MCP server connection

```bash
# SIMPLE USE CASE
# You want Claude to access your local database directly

# Standard HTTP API (LESS EFFICIENT FOR CLAUDE CODE)
# Need to manually fetch data, parse JSON, handle pagination

# MCP APPROACH (MORE POWERFUL)
# Setup an MCP server that wraps database access
# Claude can call database queries directly with type safety
```

```json
{
  "mcp_servers": {
    "my_database": {
      "command": "node",
      "args": ["./mcp_servers/database.js"]
    }
  }
}
```

## Best Practices

1. **Define clear resource types** - Structure MCP resources by domain (jira://issues, slack://channels) not by endpoint
2. **Implement proper error handling** - MCP servers should validate input and return meaningful error messages
3. **Use tool schemas effectively** - Detailed input/output schemas with descriptions help Claude understand capabilities
4. **Cache expensive operations** - Database queries and API calls should be cached at the MCP server level
5. **Version your MCP servers** - Track changes to tool signatures and resource structures across versions
