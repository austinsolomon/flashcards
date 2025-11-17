# Voice in Claude Code

Voice input enables hands-free interaction with Claude Code using natural speech. It's particularly useful for developers working on hardware setup, complex debugging sessions, or multi-step processes where typing would be cumbersome.

## Beginner Example

**Concept:** Basic voice commands for simple tasks

```
Voice Input:
\"Claude, what files changed in my last commit?\"

Claude Code processes:
1. Recognizes voice command
2. Executes: git diff HEAD~1 --name-only
3. Returns file list to user
4. User can follow up with voice or text
```

## Intermediate Example

**Concept:** Complex debugging workflow with voice navigation

```
Scenario: Debugging a production issue while doing on-site hardware setup

Voice Session:
User: \"Claude, can you help me debug the database connection timeout?\"

Claude: \"I'll help. Let me check the error logs and recent deployments.\"
[Claude reads logs autonomously]

Claude: \"I found the issue - connection pool is exhausted. It started
happening after the deployment 2 hours ago. Should I check the deployment
changes or the database metrics first?\"

User: \"Check the metrics first\"

Claude: \"Looking at PostgreSQL connection usage... it shows 450 active
connections, up from the usual 50. The new version has 3x more aggressive
connection creation. I found the problematic code change in the database
service. Should I generate a quick fix?\"

User: \"Yes, and tell me the estimated impact\"

Claude: \"Implementing the fix now... [edits file] Done. This change will:
- Reduce connection pool size from 500 to 50
- Add connection timeout of 5 seconds
- Preserve backward compatibility

Tests are running... [waits 30 seconds]... All tests pass.
Ready to deploy?\"

User: \"Deploy it\"

[Claude safely deploys and monitors metrics]
```

## Advanced Example

**Concept:** Voice-driven autonomous debugging and optimization session

```
Scenario: Complex performance optimization with voice oversight

User (via voice, hands occupied with hardware):
\"Claude, we have a performance issue. Our API is timing out on
the /search endpoint. I'm in the middle of network setup, so I need
you to be very autonomous. Here's what I know: p99 latency went
from 200ms to 2000ms after we deployed the new search indexing system
last night.\"

Claude (autonomous reasoning with voice):
[Fetches metrics, logs, and recent changes]

\"I'm analyzing this. The search endpoint depends on Elasticsearch.
Let me check the query performance.\"

[Runs trace analysis autonomously]

\"Found it - the new indexing system is issuing 50+ queries per
request instead of 1-2. This is an N+1 problem introduced in the
new search module.

Here's my plan without waiting for approval:
1. Implement query batching (estimated 20ms savings)
2. Add caching layer for common searches (50-100ms savings)
3. Update Elasticsearch query to use aggregations (100-200ms savings)

Should I proceed with all three or start conservatively with just #1?\"

User: \"Do all three, but be careful with caching\"

Claude (executing autonomously):
[Makes all changes with extensive testing]

\"Changes complete. Running integration tests...
[waits for tests]

Results:
- p99 latency: now 180ms (10x improvement)
- Error rate: 0.00% (no regressions)
- Memory usage: +5% (acceptable)
- Cache hit rate on 1000 test requests: 67%

Ready to deploy to staging for 10 minutes of production-like load testing?\"

User: \"Yes, deploy and monitor for 10 minutes\"

[Claude deploys, monitors metrics in real-time via voice]

Claude: \"Staging metrics look excellent. Deploying to production
with canary (5% traffic initially)...\"

[Continues autonomous monitoring with periodic voice updates]

Claude: \"Canary at 5% for 2 minutes - no issues. Scaling to 25%...
All good. Scaling to 100%...

Final metrics:
- p99 latency: 185ms (meets SLA)
- Error rate: 0.002% (acceptable)
- Cache efficiency: 62%

Deployment successful. Would you like me to document this optimization
for future reference?\"

User: \"Yes, and update the README performance section\"

Claude: [Creates optimization documentation autonomously]
```

## Best Practices

1. **Use voice for navigation and decisions** - Verbal input is great for answering questions and making choices, less ideal for code entry
2. **Ensure Claude autonomy in voice mode** - Don't require confirmation for every step; agent should execute confidently between checkpoints
3. **Provide clear context upfront** - Voice sessions work best when you establish context at the beginning rather than gradually
4. **Use voice for status updates** - Have Claude summarize progress periodically rather than waiting for you to ask
5. **Implement safety checkpoints** - For critical operations (deployments, deletions), still require explicit approval even in voice mode
