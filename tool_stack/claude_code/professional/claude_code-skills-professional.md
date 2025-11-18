# Skills in Claude Code

Skills are reusable, specialized capabilities that Claude Code can invoke to handle specific domains or complex operations. They enable modular, composable automation workflows by breaking complex problems into domain-specific skill sets.

## Intermediate Example

**Concept:** Composing multiple skills for complex workflows

```javascript
// Real scenario: Document processing pipeline with multiple skills

// User request:
// "Extract data from these 50 invoices (PDFs), structure them in a database,
//  generate a summary report, and email it to finance team."

// Claude Code uses a skill composition:

const skillComposition = {
  step1: {
    skill: "pdf_extraction",
    action: "Extract structured data from PDF invoices",
    input: "50 invoice PDFs",
    output: "Structured invoice data (JSON)"
  },

  step2: {
    skill: "data_validation",
    action: "Validate extracted data quality",
    input: "Invoice JSON data",
    validation: [
      "All required fields present",
      "Numeric fields are valid",
      "Dates in correct format",
      "Total calculations correct"
    ],
    output: "Validated invoice data"
  },

  step3: {
    skill: "database_operations",
    action: "Store validated invoices in database",
    input: "Validated invoice data",
    output: "Invoice records with IDs"
  },

  step4: {
    skill: "data_analysis",
    action: "Generate summary report",
    input: "Invoice data from database",
    analyses: [
      "Total invoice amount",
      "Invoices by vendor",
      "Payment status breakdown",
      "Average processing time"
    ],
    output: "Summary report (PDF)"
  },

  step5: {
    skill: "email_communication",
    action: "Send report to finance team",
    input: "Summary report",
    recipients: "finance@company.com",
    output: "Email sent confirmation"
  }
};

// Claude autonomously:
// 1. Invokes appropriate skill for each step
// 2. Chains results between steps
// 3. Handles errors and retries
// 4. Provides progress updates
```

## Best Practices

1. **Design skills with clear boundaries** - Each skill should handle a distinct domain or capability
2. **Define input/output contracts** - Skills should have clear schemas for inputs and outputs to enable composition
3. **Implement error handling** - Skills should gracefully handle errors and provide meaningful feedback
4. **Make skills reusable** - Design skills to be composable so they work well together in workflows
5. **Document skill capabilities** - Clear documentation of what each skill does enables better orchestration
