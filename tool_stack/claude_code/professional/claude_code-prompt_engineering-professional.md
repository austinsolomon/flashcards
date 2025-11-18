# Prompt Engineering in Claude Code

Prompt engineering is the art of crafting effective instructions to Claude. It's the foundation of getting useful, accurate responses. The difference between effective and ineffective prompts often determines whether Claude can complete your task successfully.

## Intermediate Example

**Concept:** Adding context, constraints, and desired output format

```javascript
// Real scenario: You're building a code review tool
// PROMPT WITH STRUCTURE
Analyze this TypeScript function for potential performance issues and security vulnerabilities.

Function:
[function code here]

Context:
- This function processes user input from an API endpoint
- It's called 500+ times per second during peak hours
- Users expect responses within 100ms

Please provide:
1. Specific issues found (if any)
2. Severity level for each issue
3. Exact code fix with explanation
4. Expected performance improvement metric
```

## Best Practices

1. **Be specific and detailed** - Include context, constraints, and expected output format rather than vague requests
2. **Use role definition** - Tell Claude what expertise or perspective to adopt ("You are a security architect")
3. **Provide examples** - Show Claude what good output looks like with 1-2 examples
4. **State constraints upfront** - Token limits, performance requirements, compliance rules, timeline
5. **Request reasoning** - Ask for "think step by step" or "explain your reasoning" for complex tasks to improve accuracy
