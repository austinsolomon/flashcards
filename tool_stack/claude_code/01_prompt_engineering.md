# Prompt Engineering in Claude Code

Prompt engineering is the art of crafting effective instructions to Claude. It's the foundation of getting useful, accurate responses. The difference between effective and ineffective prompts often determines whether Claude can complete your task successfully.

## Beginner Example

**Concept:** Basic, clear instructions

```
# Simple prompt - LESS EFFECTIVE
Fix the bug in this code.

# Better prompt - MORE EFFECTIVE
I have a React component that's supposed to show a loading spinner while fetching user data,
but it's always showing the spinner even after data loads. Here's the code: [code].
What's causing this and how do I fix it?
```

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

## Advanced Example

**Concept:** Chain-of-thought prompting with role definition and external constraints

```javascript
// Real scenario: Building an intelligent deployment assistant
// SOPHISTICATED PROMPT WITH REASONING
You are an expert DevOps engineer specializing in Kubernetes deployments for high-traffic applications.

Analyze the following deployment configuration for a production microservice:

[deployment.yaml]

Context:
- Current load: 50K requests/second
- SLA: 99.99% uptime
- Budget constraint: $X per month
- Regional requirements: US, EU, APAC

Provide analysis in this exact format:
{
  "criticalIssues": ["issue1", "issue2"],
  "performanceOptimizations": ["opt1", "opt2"],
  "costSavings": "potential savings",
  "implementationPriority": ["step1", "step2"],
  "rollbackStrategy": "detailed plan"
}

Think through your reasoning step by step before providing the JSON response.
```

## Best Practices

1. **Be specific and detailed** - Include context, constraints, and expected output format rather than vague requests
2. **Use role definition** - Tell Claude what expertise or perspective to adopt ("You are a security architect")
3. **Provide examples** - Show Claude what good output looks like with 1-2 examples
4. **State constraints upfront** - Token limits, performance requirements, compliance rules, timeline
5. **Request reasoning** - Ask for "think step by step" or "explain your reasoning" for complex tasks to improve accuracy
