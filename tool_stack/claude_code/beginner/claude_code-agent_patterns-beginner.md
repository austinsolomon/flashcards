# Agent Patterns in Claude Code

Agent patterns are proven architectural approaches for structuring autonomous agents to solve complex problems. Different patterns excel at different scenarios, and understanding which pattern to use significantly impacts agent effectiveness.

## Beginner Example

**Concept:** Reactive Pattern (simple stimulus-response)

```
Pattern: Reactive Agent

Structure:
User Request → Analyze → Select Tool → Execute → Return Result

Example: Code Format Checker
1. User: "Check if my code is properly formatted"
2. Agent: Read file
3. Agent: Run linter
4. Agent: Return results

Characteristics:
- Simple and direct
- Good for single-step tasks
- Fast execution
- Limited reasoning
```

## Best Practices

1. **Match pattern to problem type** - Use reactive for simple tasks, loop for iterative problems, tree search for complex decisions
2. **Define clear termination conditions** - Know when to stop exploring and commit to a decision
3. **Implement pruning** - Cut off branches that clearly won't lead to good solutions to save time
4. **Provide early feedback** - For complex searches, show intermediate results so humans can redirect if needed
5. **Combine patterns** - Start simple (reactive), escalate to loop if needed, use tree search only for critical decisions
