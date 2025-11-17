# Context Engineering in Claude Code

Context engineering is strategically selecting and organizing information provided to Claude to maximize its ability to understand your problem. The right context dramatically improves accuracy, relevance, and solution quality.

## Beginner Example

**Concept:** Providing relevant code and file structure

```
# POOR CONTEXT
The authentication isn't working. Here's some code:
[random code snippet]

# BETTER CONTEXT
I'm building a multi-tenant SaaS app. Here's the architecture:
- Frontend: React with Redux (auth state in Redux)
- Backend: Node.js/Express with JWT tokens
- Auth flow: User logs in → gets JWT → stores in localStorage

Here's my login component:
[component code]

Here's my API middleware:
[middleware code]

The issue: Users can log in, but after refreshing the page, they're logged out.
```

## Intermediate Example

**Concept:** Providing codebase structure, recent changes, and dependency versions

```javascript
// Real scenario: Debugging a performance issue in a data pipeline

// EFFECTIVE CONTEXT STRUCTURE
Project: Real-time analytics dashboard
Tech Stack:
- Node.js 18.x
- PostgreSQL 14
- Redis 7.0
- Bull job queue 4.10
- TypeScript 5.0

Recent changes (last 2 weeks):
- Upgraded Bull from 3.x to 4.10
- Added Redis caching layer
- Refactored database queries

Relevant file structure:
```
src/
├── jobs/
│   ├── analytics-processor.ts (processes raw events)
│   └── aggregation-job.ts (60-second aggregations)
├── services/
│   ├── cache.service.ts
│   └── db.service.ts
└── controllers/
    └── dashboard.controller.ts
```

Problem: Aggregation jobs take 15+ seconds instead of <2 seconds before the upgrade.

Here's the job implementation:
[code]

Here's the cache implementation:
[code]

What changed in Bull 4.10 that could cause this slowdown?
```

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
