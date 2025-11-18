# Slash Commands in Claude Code

Slash commands are custom workflows triggered by `/command` syntax. They allow you to create domain-specific operations that integrate deeply with Claude Code's capabilities, automating multi-step tasks in your repository.

## Advanced Example

**Concept:** Multi-stage automation with state management and integration

```markdown
# Command file: .claude/commands/deploy-feature.md
# Real scenario: Intelligent deployment pipeline for new features

## Purpose
Deploy a feature branch with comprehensive pre-flight checks,
staged rollout, and automatic rollback on issues.

## Usage
`/deploy-feature <branch-name> [--canary] [--rollback]`

## Implementation

You are a deployment automation specialist managing a complex SaaS platform.
Execute the deployment pipeline for {branch-name} with extreme attention to detail.

### Stage 1: Pre-flight Validation
- Fetch branch details and recent commits
- Run comprehensive test suite
- Verify all CI/CD checks pass
- Check for database migrations (validate compatibility)
- Verify environment variables are configured
- Audit changes for breaking API changes

### Stage 2: Staging Deployment
- Deploy to staging environment
- Run smoke tests
- Monitor error rates and performance
- Validate all integrations (payment, auth, etc.)
- Check for memory leaks

### Stage 3: Decision Point
If {--canary} flag: Deploy to 5% of production traffic
Else: Get human approval before proceeding

### Stage 4: Production Deployment (Staged Rollout)
- Deploy to 5% of users initially
- Monitor:
  * Error rates (should stay <0.1% increase)
  * Response latency (should stay <10% slower)
  * Database connection pool
  * Memory usage
- If healthy, scale to 25% → 50% → 100%

### Stage 5: Post-deployment
- Run comprehensive integration tests
- Generate deployment report with metrics
- Send notification to team
- Archive deployment logs

### Rollback Strategy
If {--rollback} flag or if any metric exceeds thresholds:
- Immediately revert to previous version
- Trigger incident response
- Analyze logs for root cause
- Generate incident report

Available tools:
- Execute Git commands
- Run build and test commands
- Access deployment configuration
- Check monitoring dashboards
```

## Best Practices

1. **Make commands idempotent** - Running the same command twice should be safe and produce consistent results
2. **Add meaningful output** - Structure results clearly with sections, error messages, and actionable recommendations
3. **Use conditional logic** - Commands should adapt based on what they find (branch exists? tests pass? etc.)
4. **Document expected behavior** - Include usage examples and describe what success looks like
5. **Integrate with existing tools** - Leverage git, npm, environment variables, and filesystem for context
