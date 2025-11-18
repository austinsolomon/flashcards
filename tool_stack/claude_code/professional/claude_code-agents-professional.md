# Agents in Claude Code

Agents are autonomous systems that can perform complex, multi-step tasks with minimal human intervention. They leverage Claude's reasoning to break down problems, execute tools, and adapt based on results—without requiring explicit step-by-step instructions for each decision.

## Intermediate Example

**Concept:** Multi-file refactoring agent with decision-making

```javascript
// Real scenario: Migrate legacy code from JavaScript to TypeScript

const migrationAgent = {
  goal: "Convert src/legacy to TypeScript",

  thinking: `
An autonomous migration agent that:
1. Identifies all .js files in src/legacy
2. Analyzes each file for type patterns
3. Creates corresponding .ts files with proper types
4. Updates all import statements across the codebase
5. Runs tests to ensure nothing broke
6. Reports migration summary
  `,

  toolsAvailable: [
    "Glob",      // Find all .js files
    "Read",      // Read legacy code
    "Edit",      // Add type annotations
    "Bash",      // Run tests and type checking
    "Grep"       // Find all imports
  ],

  criticalDecisions: [
    "Should this use 'any' or proper types?",
    "Which imports need to be updated?",
    "Is test coverage adequate after migration?",
    "Should we run migrations in batches or all at once?"
  ],

  // Agent autonomously makes these decisions based on code analysis
};

// Agent executes intelligently:
// - Reads files to understand patterns
// - Makes typing decisions based on usage
// - Adapts approach based on test results
// - Knows when to stop and ask for help
```

## Best Practices

1. **Define clear success criteria** - Agents perform better when they know exactly what "done" looks like (metrics, thresholds)
2. **Provide decision-making context** - Include recent git history, current metrics, and constraints so agents reason properly
3. **Implement safety guardrails** - Set limits on what agents can do (no deletion, no force pushes) to prevent catastrophic mistakes
4. **Give agents tools, not scripts** - Let agents choose the best tool sequence rather than forcing a predetermined path
5. **Monitor and log agent reasoning** - Capture what decisions agents made and why for debugging and learning
