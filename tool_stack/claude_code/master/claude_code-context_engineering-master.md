# Context Engineering in Claude Code

Context engineering is strategically selecting and organizing information provided to Claude to maximize its ability to understand your problem. The right context dramatically improves accuracy, relevance, and solution quality.

## Advanced Example

**Concept:** Providing Git history, system metrics, and comparative baseline

```javascript
// Real scenario: Optimizing a complex microservice architecture

const contextStructure = {
  project: "Payment Processing System",
  scale: "10M+ transactions/day",

  // Git history for context
  recentCommits: [
    "Migration from RabbitMQ to Apache Kafka (3 weeks ago)",
    "Added distributed tracing with Jaeger (2 weeks ago)",
    "Upgraded Postgres: 12 → 14 (1 week ago)"
  ],

  // System metrics showing degradation
  metrics: {
    p99Latency: {
      beforeKafka: "150ms",
      afterKafka: "450ms",
      currentTrend: "increasing"
    },
    errorRate: {
      baseline: "0.01%",
      current: "0.03%",
      affectedService: "payment-processor"
    }
  },

  // Comparative context
  workingVersion: {
    rabbitmqConfig: "link to v1.2.3 config",
    performance: "metrics from that version"
  },

  // Relevant dependencies
  dependencies: {
    kafka: "3.2.0",
    jaeger: "0.1.39",
    postgres: "14.5"
  },

  // Detailed file structure with key functions
  codeContext: `
  src/services/payment-processor.ts (main processing loop)
  src/kafka/producer.ts (Kafka integration)
  src/tracing/jaeger.ts (distributed tracing)
  src/db/queries.sql (critical queries)
  `
};

// Request:
// "We're seeing 3x latency increase and 3x error rate increase since Kafka migration.
// Tracing shows 70% of time is in Kafka operations. Here are the implementations...
// What's the most likely bottleneck?"
```

## Best Practices

1. **Provide codebase structure** - Include relevant file paths and directory organization so Claude understands relationships
2. **Include system metrics and baselines** - Show before/after comparisons and current performance data
3. **Add Git history context** - What changed recently that could be related?
4. **Specify versions and dependencies** - Breaking changes often happen in minor version updates
5. **Include error messages and logs** - Raw error output and stack traces are crucial context that prevents guessing
