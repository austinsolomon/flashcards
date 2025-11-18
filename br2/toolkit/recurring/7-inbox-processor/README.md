# Inbox Zero Processor

**Tier**: 2 (Context-Aware AI)
**Category**: Recurring Development

## Purpose

Processes inbox notes and suggests PARA categorization. Achieves "inbox zero" with Claude's help.

## What It Does

- Analyzes inbox notes for content and intent
- Suggests PARA category (Project/Area/Resource/Archive)
- Recommends tags and metadata
- Identifies related notes for linking
- Batch processes multiple notes
- Learns from user corrections

## Usage

```bash
# Process single note
python inbox_processor.py --note "0-Inbox/Meeting with CEO.md"

# Process entire inbox
python inbox_processor.py --batch --auto-tag

# Interactive mode
python inbox_processor.py --interactive
```

## Example Processing

**Input:** "Meeting with CEO about Q1 planning.md"

```markdown
Analysis:
- Type: Meeting note
- Suggested Category: Project (if Q1 planning is a project)
  OR Area (if it's ongoing strategy)
- Suggested tags: #meeting, #q1-planning, #strategy
- Related notes: [[Strategic Planning]], [[Q4 Review]]
- Recommended location: 1-Projects/Active/Q1 Planning/

Actions:
1. Move to: 1-Projects/Active/Q1 Planning/
2. Add tags: #meeting #q1-planning
3. Link to: [[Strategic Planning]]
4. Create action items: 3 todos detected

Proceed? (y/n/edit)
```

## Files

- `inbox_processor.py` - Main processing script
- `categorization_agent.py` - PARA categorization logic
- `tag_suggester.py` - Intelligent tagging
