# Voice in Claude Code

Voice input enables hands-free interaction with Claude Code using natural speech. It's particularly useful for developers working on hardware setup, complex debugging sessions, or multi-step processes where typing would be cumbersome.

## Intermediate Example

**Concept:** Complex debugging workflow with voice navigation

```
Scenario: Debugging a production issue while doing on-site hardware setup

Voice Session:
User: "Claude, can you help me debug the database connection timeout?"

Claude: "I'll help. Let me check the error logs and recent deployments."
[Claude reads logs autonomously]

Claude: "I found the issue - connection pool is exhausted. It started
happening after the deployment 2 hours ago. Should I check the deployment
changes or the database metrics first?"

User: "Check the metrics first"

Claude: "Looking at PostgreSQL connection usage... it shows 450 active
connections, up from the usual 50. The new version has 3x more aggressive
connection creation. I found the problematic code change in the database
service. Should I generate a quick fix?"

User: "Yes, and tell me the estimated impact"

Claude: "Implementing the fix now... [edits file] Done. This change will:
- Reduce connection pool size from 500 to 50
- Add connection timeout of 5 seconds
- Preserve backward compatibility

Tests are running... [waits 30 seconds]... All tests pass.
Ready to deploy?"

User: "Deploy it"

[Claude safely deploys and monitors metrics]
```

## Best Practices

1. **Use voice for navigation and decisions** - Verbal input is great for answering questions and making choices, less ideal for code entry
2. **Ensure Claude autonomy in voice mode** - Don't require confirmation for every step; agent should execute confidently between checkpoints
3. **Provide clear context upfront** - Voice sessions work best when you establish context at the beginning rather than gradually
4. **Use voice for status updates** - Have Claude summarize progress periodically rather than waiting for you to ask
5. **Implement safety checkpoints** - For critical operations (deployments, deletions), still require explicit approval even in voice mode
