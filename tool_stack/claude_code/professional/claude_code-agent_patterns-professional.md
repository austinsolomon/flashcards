# Agent Patterns in Claude Code

Agent patterns are proven architectural approaches for structuring autonomous agents to solve complex problems. Different patterns excel at different scenarios, and understanding which pattern to use significantly impacts agent effectiveness.

## Intermediate Example

**Concept:** Loop Pattern (iterative refinement)

```javascript
// Real scenario: Automated bug fixing

const BugFixerAgent = {
  name: "Bug Fixer",
  pattern: "Loop Pattern",

  algorithm: `
Initialize:
  - Read error message
  - Analyze stack trace

Loop (max 5 iterations):
  1. Identify root cause
  2. Generate potential fixes
  3. Implement most likely fix
  4. Run tests
  5. Evaluate results:
     - If tests pass: EXIT (success)
     - If tests fail differently: CONTINUE (new issue)
     - If same error: Try next fix (continue loop)
     - If max iterations: ESCALATE (couldn't fix)

Output:
  - Fixed code
  - Explanation of fix
  - Test results
  `,

  example: `
User: "Fix this TypeError: Cannot read property 'name' of undefined"

Iteration 1:
- Root cause: Missing null check
- Fix: Add || {} operator
- Test: Still fails
- Decision: Problem deeper

Iteration 2:
- Root cause: API call not awaited
- Fix: Add await to API call
- Test: PASS!
- Decision: Done

Output: Fixed code + explanation of root issue
  `,

  characteristics: {
    goodFor: "Fixing bugs, optimization, incremental improvements",
    advantages: "Can recover from wrong approaches, learns as it goes",
    limitations: "Can get stuck in loops, may need human guidance"
  }
};
```

## Best Practices

1. **Match pattern to problem type** - Use reactive for simple tasks, loop for iterative problems, tree search for complex decisions
2. **Define clear termination conditions** - Know when to stop exploring and commit to a decision
3. **Implement pruning** - Cut off branches that clearly won't lead to good solutions to save time
4. **Provide early feedback** - For complex searches, show intermediate results so humans can redirect if needed
5. **Combine patterns** - Start simple (reactive), escalate to loop if needed, use tree search only for critical decisions
