# Voice in Claude Code

Voice input enables hands-free interaction with Claude Code using natural speech. It's particularly useful for developers working on hardware setup, complex debugging sessions, or multi-step processes where typing would be cumbersome.

## Beginner Example

**Concept:** Basic voice commands for simple tasks

```
Voice Input:
"Claude, what files changed in my last commit?"

Claude Code processes:
1. Recognizes voice command
2. Executes: git diff HEAD~1 --name-only
3. Returns file list to user
4. User can follow up with voice or text
```

## Best Practices

1. **Use voice for navigation and decisions** - Verbal input is great for answering questions and making choices, less ideal for code entry
2. **Ensure Claude autonomy in voice mode** - Don't require confirmation for every step; agent should execute confidently between checkpoints
3. **Provide clear context upfront** - Voice sessions work best when you establish context at the beginning rather than gradually
4. **Use voice for status updates** - Have Claude summarize progress periodically rather than waiting for you to ask
5. **Implement safety checkpoints** - For critical operations (deployments, deletions), still require explicit approval even in voice mode
