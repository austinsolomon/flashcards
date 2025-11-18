# Context Engineering in Claude Code

Context engineering is strategically selecting and organizing information provided to Claude to maximize its ability to understand your problem. The right context dramatically improves accuracy, relevance, and solution quality.

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

## Best Practices

1. **Provide codebase structure** - Include relevant file paths and directory organization so Claude understands relationships
2. **Include system metrics and baselines** - Show before/after comparisons and current performance data
3. **Add Git history context** - What changed recently that could be related?
4. **Specify versions and dependencies** - Breaking changes often happen in minor version updates
5. **Include error messages and logs** - Raw error output and stack traces are crucial context that prevents guessing
