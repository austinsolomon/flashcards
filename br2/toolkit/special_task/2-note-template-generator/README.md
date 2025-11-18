# Obsidian Note Template Generator

**Tier**: 2 (Context-Aware AI)
**Category**: Special Task - Second Brain Implementation

## Purpose

Generates context-aware note templates for different types of content in your Second Brain. Uses Claude to create intelligent, reusable templates.

## What It Does

- Creates templates for projects, areas, resources
- Generates meeting note templates
- Builds book/article summary templates
- Creates daily/weekly review templates
- Includes Dataview queries and metadata
- Adapts templates based on context

## Template Types

**Project Template**
```markdown
---
type: project
status: active
start_date: {{date}}
deadline: {{deadline}}
tags: [project, {{tags}}]
---

# {{project_name}}

## Objective
What is the goal of this project?

## Success Criteria
- [ ] Criteria 1
- [ ] Criteria 2

## Key Resources
- [[Resource 1]]
- [[Resource 2]]

## Action Items
- [ ] Task 1 #todo
- [ ] Task 2 #todo

## Notes


## Review
Next review: {{date:+7d}}

---
**Related Areas:** [[Area 1]]
**Created:** {{date}}
**Modified:** {{date}}
```

**Meeting Note Template**
```markdown
---
type: meeting
date: {{date}}
attendees: []
tags: [meeting, {{project}}]
---

# Meeting: {{title}}

**Date:** {{date}}
**Attendees:** {{attendees}}
**Project:** [[{{project}}]]

## Agenda
1.
2.
3.

## Notes


## Action Items
- [ ] {{name}}: Task description #todo #{{name}}

## Decisions Made


## Follow-up
Next meeting: {{date:+7d}}
```

## Usage

```bash
# Generate project template
python template_generator.py --type project --name "Website Redesign"

# Generate meeting template with context
python template_generator.py --type meeting \
  --project "Second Brain Toolkit" \
  --attendees "Alice, Bob"

# Create custom template
python template_generator.py --custom \
  --prompt "Create a template for tracking books I'm reading"
```

## Example: AI-Generated Custom Template

**Prompt:** "Create a template for tracking books I'm reading"

**Output:**
```markdown
---
type: resource
category: book
status: reading
rating:
tags: [book, reading]
---

# 📚 {{book_title}}

**Author:** {{author}}
**Started:** {{date}}
**Finished:**
**Rating:** ⭐⭐⭐⭐⭐

## Summary
One-paragraph summary of the book.

## Key Ideas
1. Main idea #1
2. Main idea #2
3. Main idea #3

## Highlights & Notes

### Chapter 1: {{chapter_name}}
- Quote or highlight
  - My thoughts on this

## Progressive Summary
### Layer 1: Bold
Important passages

### Layer 2: Highlighted
Very important insights

### Layer 3: Executive Summary
The 3-5 most important takeaways from this book.

## Actionable Insights
- [ ] Action item based on book #todo

## Related
- Similar books: [[Book 1]], [[Book 2]]
- Related areas: [[Area]]

---
**Category:** [[3-Resources/Books]]
**Tags:** #{{genre}} #{{topic}}
```

## Files

- `template_generator.py` - Main template creation script
- `templates/` - Pre-built template library
- `claude_prompts/` - Template generation prompts
- `metadata_schemas.yaml` - Frontmatter configurations
