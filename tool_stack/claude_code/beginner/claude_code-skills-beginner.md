# Skills in Claude Code

Skills are reusable, specialized capabilities that Claude Code can invoke to handle specific domains or complex operations. They enable modular, composable automation workflows by breaking complex problems into domain-specific skill sets.

## Beginner Example

**Concept:** Basic skill invocation

```bash
# Skills are predefined capabilities Claude can use
# Example: PDF skill for working with PDFs

# In Claude Code:
# "Extract text and tables from this PDF and create a CSV"

# Claude invokes the PDF skill:
# - Reads PDF
# - Extracts text
# - Identifies tables
# - Converts to CSV

# From user perspective: "just ask, Claude handles it"
```

## Best Practices

1. **Design skills with clear boundaries** - Each skill should handle a distinct domain or capability
2. **Define input/output contracts** - Skills should have clear schemas for inputs and outputs to enable composition
3. **Implement error handling** - Skills should gracefully handle errors and provide meaningful feedback
4. **Make skills reusable** - Design skills to be composable so they work well together in workflows
5. **Document skill capabilities** - Clear documentation of what each skill does enables better orchestration
