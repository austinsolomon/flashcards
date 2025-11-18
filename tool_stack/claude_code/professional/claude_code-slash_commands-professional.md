# Slash Commands in Claude Code

Slash commands are custom workflows triggered by `/command` syntax. They allow you to create domain-specific operations that integrate deeply with Claude Code's capabilities, automating multi-step tasks in your repository.

## Intermediate Example

**Concept:** Complex review workflow with conditional logic

```markdown
# Command file: .claude/commands/review-pr.md
# Real scenario: Automated code review command for pull requests

## Purpose
Review a Pull Request for code quality, security, and architecture issues.

## Usage
`/review-pr <pr-number>`

## Implementation

You are a senior code reviewer. Analyze PR #{argument} for:

1. **Code Quality**
   - Style consistency with project standards
   - Complexity analysis
   - Test coverage

2. **Security**
   - Input validation
   - Authentication/Authorization
   - Dependency vulnerabilities
   - SQL injection, XSS risks

3. **Architecture**
   - Design patterns used
   - Coupling and cohesion
   - Performance implications
   - Breaking changes

4. **Best Practices**
   - Error handling
   - Logging
   - Documentation

Search the codebase for:
- Similar implementations (to check consistency)
- Related tests (to understand coverage)
- Architecture decision records (to check alignment)

Generate a detailed review with:
- Severity scores for each issue
- Specific code locations
- Suggested improvements
- Questions for the author
```

## Best Practices

1. **Make commands idempotent** - Running the same command twice should be safe and produce consistent results
2. **Add meaningful output** - Structure results clearly with sections, error messages, and actionable recommendations
3. **Use conditional logic** - Commands should adapt based on what they find (branch exists? tests pass? etc.)
4. **Document expected behavior** - Include usage examples and describe what success looks like
5. **Integrate with existing tools** - Leverage git, npm, environment variables, and filesystem for context
