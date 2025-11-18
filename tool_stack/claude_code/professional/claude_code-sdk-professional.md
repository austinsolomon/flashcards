# SDK (Claude Code SDK) in Claude Code

The Claude Code SDK enables developers to build custom extensions, integrate with external systems, and create sophisticated automation workflows. It provides programmatic access to Claude's capabilities beyond the CLI interface.

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
// "Post a summary of today's PRs to #engineering-reviews"
```

## Best Practices

1. **Implement proper error handling** - SDK calls can fail; always wrap in try/catch with meaningful error messages
2. **Use resource caching** - Cache SDK resources that don't change frequently to reduce API calls
3. **Register tools thoughtfully** - Every tool should have clear name, description, and input/output schemas
4. **Implement rate limit awareness** - Track SDK API usage and implement backoff strategies
5. **Version your API contracts** - As you extend the SDK, maintain backward compatibility with versioning
