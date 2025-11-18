# Context Engineering in Claude Code

Context engineering is strategically selecting and organizing information provided to Claude to maximize its ability to understand your problem. The right context dramatically improves accuracy, relevance, and solution quality.

## Beginner Example

**Concept:** Providing relevant code and file structure

```
# POOR CONTEXT
The authentication isn't working. Here's some code:
[random code snippet]

# BETTER CONTEXT
I'm building a multi-tenant SaaS app. Here's the architecture:
- Frontend: React with Redux (auth state in Redux)
- Backend: Node.js/Express with JWT tokens
- Auth flow: User logs in → gets JWT → stores in localStorage

Here's my login component:
[component code]

Here's my API middleware:
[middleware code]

The issue: Users can log in, but after refreshing the page, they're logged out.
```

## Best Practices

1. **Provide codebase structure** - Include relevant file paths and directory organization so Claude understands relationships
2. **Include system metrics and baselines** - Show before/after comparisons and current performance data
3. **Add Git history context** - What changed recently that could be related?
4. **Specify versions and dependencies** - Breaking changes often happen in minor version updates
5. **Include error messages and logs** - Raw error output and stack traces are crucial context that prevents guessing
