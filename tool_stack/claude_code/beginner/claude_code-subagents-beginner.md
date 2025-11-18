# Subagents in Claude Code

Subagents are specialized agents launched to handle specific subtasks within a larger workflow. The main agent can orchestrate multiple subagents in parallel or sequence, enabling complex multi-domain problem solving with proper task decomposition.

## Beginner Example

**Concept:** One main agent launching a focused subagent

```
Main Task: Deploy a new feature and generate documentation

Main Agent Flow:
1. Review changes
2. Run tests
3. Launch Subagent: Document Generator
   → Subagent generates README updates
4. Deploy
5. Confirm completion
```

## Best Practices

1. **Decompose by expertise domain** - Launch subagents that represent specialized roles (frontend engineer, security specialist, etc.)
2. **Define clear dependencies** - Specify which subagents must complete before others start; run independent subagents in parallel
3. **Provide integration points** - Each subagent should understand how their output integrates with others
4. **Monitor and coordinate** - Main agent watches progress and handles conflicts between subagents
5. **Use subagents for scale** - Subagents excel at handling multiple complex subtasks faster than sequential processing
