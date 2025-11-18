# Hooks in Claude Code

Hooks are event-driven automations that execute shell commands in response to Claude Code events. They enable deep integration with your development workflow, allowing Claude to react to tool calls, form submissions, and other events with custom logic.

## Intermediate Example

**Concept:** Real-world pre-commit validation hook with multiple checks

```bash
#!/bin/bash
# Hook: .claude/hooks/user-prompt-submit.sh
# Real scenario: Enforce code quality standards before Claude makes changes

set -e

echo \"Running pre-submission checks...\"

# Check 1: Verify branch is not main
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ \"$CURRENT_BRANCH\" = \"main\" ] || [ \"$CURRENT_BRANCH\" = \"master\" ]; then
  echo \"ERROR: Cannot make changes directly to main branch\"
  exit 1
fi

# Check 2: Verify all tests pass
echo \"Running tests...\"
if ! npm test -- --coverage; then
  echo \"ERROR: Tests failed. Fix tests before proceeding.\"
  exit 1
fi

# Check 3: Verify no security vulnerabilities
echo \"Checking for vulnerabilities...\"
if npm audit | grep -q \"high\\|critical\"; then
  echo \"ERROR: High/Critical vulnerabilities detected\"
  exit 1
fi

# Check 4: Ensure staging area is clean for reproducible commits
if [ -n \"$(git status --porcelain)\" ]; then
  echo \"ERROR: Unstaged changes detected. Stage or stash changes.\"
  exit 1
fi

# Check 5: Verify Node version
REQUIRED_NODE_VERSION=\"18.0.0\"
CURRENT_NODE=$(node -v | cut -d'v' -f 2)
if [ \"$(printf '%s\\n' \"$REQUIRED_NODE_VERSION\" \"$CURRENT_NODE\" | sort -V | head -n1)\" != \"$REQUIRED_NODE_VERSION\" ]; then
  echo \"ERROR: Node.js version must be >= $REQUIRED_NODE_VERSION\"
  exit 1
fi

echo \"✓ All pre-submission checks passed\"
exit 0
```

## Best Practices

1. **Keep hooks focused** - Each hook should do one thing well; avoid complex multi-purpose hooks
2. **Fail fast with clear errors** - Use exit codes properly; provide helpful error messages
3. **Make hooks non-blocking where possible** - Use conditional logic (exit 0) for warnings that shouldn't block
4. **Log important operations** - Maintain audit trails of what hooks executed and why
5. **Test hooks independently** - Ensure hooks work standalone before relying on them in automation
