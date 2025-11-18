# Model Context Protocol (MCP) in Claude Code

Model Context Protocol enables Claude Code to securely connect to external systems and data sources. MCP servers act as bridges, allowing Claude to access databases, APIs, file systems, and custom tools seamlessly during conversations.

## Intermediate Example

**Concept:** Real-world MCP server for project management

```javascript
// Real scenario: Claude Code directly managing Jira tickets

// MCP Server Implementation (jira-mcp-server.js)
const MCPServer = require("@anthropic-sdk/mcp");

const server = new MCPServer();

// Resource: list all issues
server.resources.register({
  uri: "jira://issues",
  name: "Active Jira Issues",
  mimeType: "application/json"
}, async () => {
  return await jiraClient.issues.search({
    jql: "status != Closed AND assignee = currentUser()"
  });
});

// Tool: create issue
server.tools.register({
  name: "create_jira_issue",
  description: "Create a new Jira issue",
  inputSchema: {
    type: "object",
    properties: {
      title: { type: "string" },
      description: { type: "string" },
      priority: { type: "string", enum: ["Low", "Medium", "High", "Critical"] }
    },
    required: ["title", "priority"]
  }
}, async (input) => {
  return await jiraClient.issues.create({
    fields: {
      summary: input.title,
      description: input.description,
      priority: input.priority
    }
  });
});

// Usage in Claude Code:
// "Check my open Jira issues and create a new one for that API migration task"
// Claude can directly list issues and create new ones through MCP
```

## Best Practices

1. **Define clear resource types** - Structure MCP resources by domain (jira://issues, slack://channels) not by endpoint
2. **Implement proper error handling** - MCP servers should validate input and return meaningful error messages
3. **Use tool schemas effectively** - Detailed input/output schemas with descriptions help Claude understand capabilities
4. **Cache expensive operations** - Database queries and API calls should be cached at the MCP server level
5. **Version your MCP servers** - Track changes to tool signatures and resource structures across versions
