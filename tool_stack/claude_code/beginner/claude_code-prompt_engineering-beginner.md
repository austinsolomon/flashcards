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

## Best Practices

1. **Be specific and detailed** - Include context, constraints, and expected output format rather than vague requests
2. **Use role definition** - Tell Claude what expertise or perspective to adopt ("You are a security architect")
3. **Provide examples** - Show Claude what good output looks like with 1-2 examples
4. **State constraints upfront** - Token limits, performance requirements, compliance rules, timeline
5. **Request reasoning** - Ask for "think step by step" or "explain your reasoning" for complex tasks to improve accuracy
