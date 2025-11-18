# Slash Commands in Claude Code

Slash commands are custom workflows triggered by `/command` syntax. They allow you to create domain-specific operations that integrate deeply with Claude Code's capabilities, automating multi-step tasks in your repository.

## Beginner Example

**Concept:** Basic custom command

```bash
# Command file: .claude/commands/test.md
# Creates a command that runs tests

Run `npm test` to execute the test suite for the current project.
Display results and highlight any failures.
```

## Best Practices

1. **Make commands idempotent** - Running the same command twice should be safe and produce consistent results
2. **Add meaningful output** - Structure results clearly with sections, error messages, and actionable recommendations
3. **Use conditional logic** - Commands should adapt based on what they find (branch exists? tests pass? etc.)
4. **Document expected behavior** - Include usage examples and describe what success looks like
5. **Integrate with existing tools** - Leverage git, npm, environment variables, and filesystem for context
