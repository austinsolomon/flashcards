# Hooks in Claude Code

Hooks are event-driven automations that execute shell commands in response to Claude Code events. They enable deep integration with your development workflow, allowing Claude to react to tool calls, form submissions, and other events with custom logic.

## Beginner Example

**Concept:** Simple validation hook

```bash
# Hook: .claude/hooks/user-prompt-submit.sh
# Runs before Claude responds to user prompts

#!/bin/bash
# Ensure Git is clean before making changes
if [ -z \"$(git status --porcelain)\" ]; then
  echo \"Ready: No uncommitted changes\"
  exit 0
else
  echo \"WARNING: You have uncommitted changes. Commit or stash before proceeding.\"
  exit 1
fi
```

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

## Advanced Example

**Concept:** Intelligent post-tool-call hook with adaptive formatting and CI integration

```bash
#!/bin/bash
# Hook: .claude/hooks/tool-call-finish.sh
# Real scenario: Post-processing tool outputs with validation and CI feedback

set -e

# Extract tool information from hook context
TOOL_NAME=\"${CLAUDE_TOOL_NAME:-}\"
TOOL_RESULT=\"${CLAUDE_TOOL_RESULT:-}\"
RETURN_CODE=\"${CLAUDE_TOOL_RETURN_CODE:-0}\"

# Log all tool executions for audit trail
echo \"[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Tool: $TOOL_NAME | Return: $RETURN_CODE\" >> .claude/tool_audit.log

case \"$TOOL_NAME\" in
  \"Bash\")
    # After running bash commands, verify no dangerous operations occurred
    if echo \"$TOOL_RESULT\" | grep -qE \"rm -rf|git push.*force|truncate|DROP TABLE\"; then
      echo \"SECURITY WARNING: Potentially destructive command detected\"
      exit 1
    fi

    # If build command succeeded, trigger CI checks
    if [[ \"$TOOL_RESULT\" == *\"build\"* ]] && [ $RETURN_CODE -eq 0 ]; then
      echo \"Build succeeded. Triggering CI pipeline...\"
      # Could integrate with GitHub Actions, GitLab CI, etc.
    fi
    ;;

  \"Edit\")
    # After file edits, run linter and formatter
    EDITED_FILE=\"${CLAUDE_EDITED_FILE:-}\"
    if [ -n \"$EDITED_FILE\" ]; then
      if [ \"${EDITED_FILE##*.}\" = \"js\" ] || [ \"${EDITED_FILE##*.}\" = \"ts\" ]; then
        npm run lint -- \"$EDITED_FILE\" || true
        npm run format -- \"$EDITED_FILE\" || true
      fi
    fi
    ;;

  \"Glob\")
    # After glob searches, verify results are what we expected
    PATTERN=\"${CLAUDE_GLOB_PATTERN:-}\"
    FILE_COUNT=$(echo \"$TOOL_RESULT\" | wc -l)

    if [ $FILE_COUNT -eq 0 ]; then
      echo \"WARNING: Glob pattern '$PATTERN' returned no results\"
    elif [ $FILE_COUNT -gt 1000 ]; then
      echo \"WARNING: Glob pattern '$PATTERN' returned $FILE_COUNT files (may be too broad)\"
    fi
    ;;
esac

# Post-processing: Enrich tool output with additional context
if [ $RETURN_CODE -ne 0 ]; then
  echo \"Tool failed. Attempting to gather diagnostic information...\"

  # Collect debug info
  git log --oneline -n 5 > /tmp/recent_commits.txt
  npm list > /tmp/dependencies.txt

  echo \"Debug info saved for analysis\"
fi

exit 0
```

## Best Practices

1. **Keep hooks focused** - Each hook should do one thing well; avoid complex multi-purpose hooks
2. **Fail fast with clear errors** - Use exit codes properly; provide helpful error messages
3. **Make hooks non-blocking where possible** - Use conditional logic (exit 0) for warnings that shouldn't block
4. **Log important operations** - Maintain audit trails of what hooks executed and why
5. **Test hooks independently** - Ensure hooks work standalone before relying on them in automation
