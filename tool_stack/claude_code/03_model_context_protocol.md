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

## Advanced Example

**Concept:** Multi-source context aggregation with custom MCP server

```javascript
// Real scenario: Company-wide knowledge system integrating multiple data sources

// composite-knowledge-mcp-server.js
class CompositeKnowledgeMCP extends MCPServer {
  async initialize() {
    // Connect to multiple sources
    this.confluence = new ConfluenceAPI();
    this.slack = new SlackAPI();
    this.github = new GitHubAPI();
    this.datadog = new DatadogAPI();
  }

  async registerResources() {
    // Resource: Full company context
    this.resources.register({
      uri: "company://full-context",
      name: "Complete Company Knowledge"
    }, async (params) => {
      const context = {
        // Architecture docs from Confluence
        architecture: await this.confluence.search({
          space: "ARCH",
          query: params.topic
        }),

        // Recent Slack discussions
        discussions: await this.slack.search({
          query: params.topic,
          timeRange: "7d"
        }),

        // Code references from GitHub
        codeExamples: await this.github.search({
          query: params.topic,
          language: params.language
        }),

        // Current system metrics
        metrics: await this.datadog.getMetrics({
          service: params.service,
          timeRange: "24h"
        })
      };

      return context;
    });

    // Tool: Autonomous decision making with full context
    this.tools.register({
      name: "make_architectural_decision",
      description: "Make architecture decision with full company context"
    }, async (input) => {
      const fullContext = await this.getFullContext(input.domain);

      return {
        decision: this.analyzeWithContext(input.proposal, fullContext),
        rationale: fullContext.discussions,
        precedents: fullContext.codeExamples,
        impact: this.predictImpact(input.proposal, fullContext.metrics)
      };
    });
  }
}

// Usage in Claude Code:
// "Should we migrate our auth system from JWT to OAuth2?
// Give me full architectural context from our docs, recent discussions, and code examples"
// MCP automatically aggregates all information
```

## Best Practices

1. **Define clear resource types** - Structure MCP resources by domain (jira://issues, slack://channels) not by endpoint
2. **Implement proper error handling** - MCP servers should validate input and return meaningful error messages
3. **Use tool schemas effectively** - Detailed input/output schemas with descriptions help Claude understand capabilities
4. **Cache expensive operations** - Database queries and API calls should be cached at the MCP server level
5. **Version your MCP servers** - Track changes to tool signatures and resource structures across versions
