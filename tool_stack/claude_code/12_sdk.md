# SDK (Claude Code SDK) in Claude Code

The Claude Code SDK enables developers to build custom extensions, integrate with external systems, and create sophisticated automation workflows. It provides programmatic access to Claude's capabilities beyond the CLI interface.

## Beginner Example

**Concept:** Simple SDK usage to build a custom tool

```javascript
// Basic SDK setup
const ClaudeCodeSDK = require('@anthropic/claude-code-sdk');

const sdk = new ClaudeCodeSDK({
  apiKey: process.env.CLAUDE_API_KEY,
  projectPath: '/path/to/project'
});

// Simple custom tool
const myTool = {
  name: 'analyze_code_quality',
  description: 'Analyze code quality metrics',
  handler: async (filePath) => {
    const analysis = await sdk.tools.read(filePath);
    return {
      path: filePath,
      status: 'analyzed'
    };
  }
};

// Register and use
sdk.registerTool(myTool);
```

## Intermediate Example

**Concept:** Building a plugin that integrates external services

```javascript
// Real scenario: Build a Slack integration plugin for Claude Code

const ClaudeCodeSDK = require('@anthropic/claude-code-sdk');
const SlackAPI = require('@slack/web-api');

class SlackIntegrationPlugin {
  constructor(slackToken) {
    this.sdk = new ClaudeCodeSDK({
      apiKey: process.env.CLAUDE_API_KEY
    });
    this.slack = new SlackAPI.WebClient(slackToken);
  }

  async initialize() {
    // Register Slack-specific tools
    this.sdk.registerTool({
      name: 'notify_slack',
      description: 'Send message to Slack channel',
      parameters: {
        channel: { type: 'string', description: 'Slack channel ID' },
        message: { type: 'string', description: 'Message content' },
        blocks: { type: 'object', description: 'Slack block format (optional)' }
      },
      handler: async (params) => {
        return await this.slack.chat.postMessage({
          channel: params.channel,
          text: params.message,
          blocks: params.blocks
        });
      }
    });

    // Register tool to fetch PR reviews from Slack threads
    this.sdk.registerTool({
      name: 'get_slack_pr_feedback',
      description: 'Retrieve PR review feedback from Slack threads',
      parameters: {
        prNumber: { type: 'number' },
        threadTs: { type: 'string' }
      },
      handler: async (params) => {
        const replies = await this.slack.conversations.replies({
          channel: process.env.SLACK_PR_CHANNEL,
          ts: params.threadTs
        });
        return this.parseReviewFeedback(replies.messages);
      }
    });

    // Register context resource
    this.sdk.registerResource({
      uri: 'slack://recent_pr_reviews',
      description: 'Recent PR reviews from Slack',
      handler: async () => {
        const messages = await this.slack.conversations.history({
          channel: process.env.SLACK_PR_CHANNEL,
          limit: 10
        });
        return this.extractPRReviews(messages.messages);
      }
    });
  }

  async parseReviewFeedback(messages) {
    // Parse Slack reactions and comments into structured feedback
    return messages.map(msg => ({
      reviewer: msg.user,
      sentiment: this.analyzeSentiment(msg.text),
      feedback: msg.text,
      reactions: msg.reactions
    }));
  }

  async extractPRReviews(messages) {
    return messages
      .filter(msg => msg.text.includes('PR'))
      .map(msg => ({
        text: msg.text,
        ts: msg.ts,
        thread: msg.thread_ts
      }));
  }

  analyzeSentiment(text) {
    // Simple sentiment analysis
    if (text.match(/approve|looks good|👍/i)) return 'positive';
    if (text.match(/change|issue|problem|❌/i)) return 'negative';
    return 'neutral';
  }
}

// Usage
const plugin = new SlackIntegrationPlugin(process.env.SLACK_TOKEN);
await plugin.initialize();

// Claude Code can now use Slack tools directly:
// \"Post a summary of today's PRs to #engineering-reviews\"
```

## Advanced Example

**Concept:** Complex SDK-based system for intelligent automation orchestration

```javascript
// Real scenario: Enterprise-scale automation platform using Claude Code SDK

const ClaudeCodeSDK = require('@anthropic/claude-code-sdk');

class EnterpriseAutomationPlatform {
  constructor(config) {
    this.sdk = new ClaudeCodeSDK(config);
    this.agents = new Map();
    this.eventBus = new EventEmitter();
    this.metrics = {};
  }

  async setupCoreInfrastructure() {
    // Register authentication system
    this.registerAuthenticationTools();

    // Register multi-environment support
    this.registerEnvironmentTools();

    // Register audit and compliance tools
    this.registerAuditTools();

    // Register monitoring and alerting
    this.registerMonitoringTools();
  }

  registerAuthenticationTools() {
    // RBAC (Role-Based Access Control)
    this.sdk.registerTool({
      name: 'check_permission',
      description: 'Check if user has permission for action',
      parameters: {
        userId: { type: 'string' },
        action: { type: 'string' },
        resource: { type: 'string' }
      },
      handler: async (params) => {
        const user = await this.getUser(params.userId);
        return this.evaluatePermission(user, params.action, params.resource);
      }
    });

    // Audit log
    this.sdk.registerTool({
      name: 'audit_action',
      description: 'Log action to audit trail',
      parameters: {
        action: { type: 'string' },
        actor: { type: 'string' },
        resource: { type: 'string' },
        result: { type: 'string' }
      },
      handler: async (params) => {
        return await this.auditLog.write({
          timestamp: new Date(),
          ...params
        });
      }
    });
  }

  registerEnvironmentTools() {
    // Multi-environment support: dev, staging, production
    this.sdk.registerTool({
      name: 'deploy_to_environment',
      description: 'Deploy code to specified environment',
      parameters: {
        environment: {
          type: 'string',
          enum: ['dev', 'staging', 'production']
        },
        version: { type: 'string' },
        rollbackPlan: { type: 'object' }
      },
      handler: async (params) => {
        // Environment-specific logic
        const config = this.getEnvironmentConfig(params.environment);
        return await this.executeDeployment(params, config);
      }
    });
  }

  registerAuditTools() {
    // Compliance and audit tools
    this.sdk.registerTool({
      name: 'validate_compliance',
      description: 'Validate compliance with organizational policies',
      parameters: {
        checkType: {
          type: 'string',
          enum: ['security', 'data_residency', 'encryption', 'access_control']
        },
        target: { type: 'string' }
      },
      handler: async (params) => {
        const policy = this.getPolicyFor(params.checkType);
        return await policy.validate(params.target);
      }
    });
  }

  registerMonitoringTools() {
    // Real-time monitoring and alerting
    this.sdk.registerTool({
      name: 'setup_monitoring',
      description: 'Configure monitoring for critical operations',
      parameters: {
        metricName: { type: 'string' },
        threshold: { type: 'number' },
        alertChannel: { type: 'string' },
        escalationPolicy: { type: 'object' }
      },
      handler: async (params) => {
        const monitor = new Monitor(params);
        return await monitor.activate();
      }
    });
  }

  async createAutomationAgent(config) {
    // Create a specialized agent with access to platform capabilities
    const agent = await this.sdk.createAgent({
      name: config.name,
      role: config.role,
      permissions: config.permissions,
      tools: this.getToolsForRole(config.role),
      eventHandlers: {
        onSuccess: (result) => this.handleSuccess(config.name, result),
        onError: (error) => this.handleError(config.name, error),
        onRateLimit: (info) => this.handleRateLimit(config.name, info)
      }
    });

    this.agents.set(config.name, agent);
    return agent;
  }

  getToolsForRole(role) {
    // Role-based tool access
    const baseTools = ['read', 'bash'];
    const roleTools = {
      'developer': [...baseTools, 'edit', 'write', 'test'],
      'devops': [...baseTools, 'deploy_to_environment', 'scale_services'],
      'security': [...baseTools, 'validate_compliance', 'audit_action'],
      'analyst': [...baseTools, 'query_analytics', 'generate_reports']
    };
    return roleTools[role] || baseTools;
  }

  async executeWithGovernance(agentName, task) {
    const agent = this.agents.get(agentName);

    // Pre-execution: compliance check
    const complianceCheck = await this.validateCompliance(task);
    if (!complianceCheck.passed) {
      return {
        status: 'blocked',
        reason: complianceCheck.violations
      };
    }

    // Execute with monitoring
    const startTime = Date.now();
    try {
      const result = await agent.execute(task);

      // Post-execution: audit and metrics
      this.recordMetric({
        agent: agentName,
        task: task.type,
        duration: Date.now() - startTime,
        status: 'success'
      });

      await this.auditLog.write({
        action: 'agent_execution',
        agent: agentName,
        task: task.type,
        result: 'success',
        timestamp: new Date()
      });

      return result;
    } catch (error) {
      this.recordMetric({
        agent: agentName,
        task: task.type,
        duration: Date.now() - startTime,
        status: 'error',
        error: error.message
      });

      throw error;
    }
  }

  getMetrics() {
    return {
      totalExecutions: this.metrics.totalExecutions,
      successRate: this.metrics.successRate,
      averageExecutionTime: this.metrics.averageExecutionTime,
      agentPerformance: this.getAgentPerformance()
    };
  }
}

// Usage
const platform = new EnterpriseAutomationPlatform({
  apiKey: process.env.CLAUDE_API_KEY,
  environment: 'production'
});

await platform.setupCoreInfrastructure();

// Create specialized agents
await platform.createAutomationAgent({
  name: 'deployment_agent',
  role: 'devops',
  permissions: ['deploy', 'monitor', 'rollback']
});

// Execute with governance
const result = await platform.executeWithGovernance(
  'deployment_agent',
  {
    type: 'deploy_new_feature',
    version: 'v2.1.0',
    rolloutStage: 'canary'
  }
);
```

## Best Practices

1. **Implement proper error handling** - SDK calls can fail; always wrap in try/catch with meaningful error messages
2. **Use resource caching** - Cache SDK resources that don't change frequently to reduce API calls
3. **Register tools thoughtfully** - Every tool should have clear name, description, and input/output schemas
4. **Implement rate limit awareness** - Track SDK API usage and implement backoff strategies
5. **Version your API contracts** - As you extend the SDK, maintain backward compatibility with versioning
