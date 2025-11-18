# Weekly Review Automation

**Tier**: 2 (Context-Aware AI)
**Category**: Recurring Development

## Purpose

Automates the weekly review process from Getting Things Done/Second Brain methodologies. Generates comprehensive review reports using Claude.

## What It Does

- Analyzes week's activities and progress
- Reviews project statuses
- Identifies stalled projects
- Suggests projects to archive
- Reviews inbox and uncategorized notes
- Generates next week's priorities
- Creates weekly review note

## Weekly Review Checklist

```markdown
# Weekly Review - {{date}}

## 1. Clear Inbox ✅
- [ ] Process all notes in `0-Inbox/`
- [ ] Move to appropriate PARA folders
- Inbox items processed: {{count}}

## 2. Review Projects
- [ ] Update project statuses
- [ ] Archive completed projects
- [ ] Identify stalled projects

Active Projects: {{active_count}}
Completed this week: {{completed_count}}
Need attention: {{stalled_count}}

## 3. Review Areas
- [ ] Check area dashboards
- [ ] Update ongoing responsibilities
- Standards maintained: {{areas_on_track}}

## 4. Review Calendar
- [ ] Process meeting notes
- [ ] Extract action items
- Meetings this week: {{meeting_count}}
- Action items created: {{action_count}}

## 5. Next Week Planning
Priority Projects:
1. {{project_1}}
2. {{project_2}}
3. {{project_3}}

## Insights & Reflections
{{claude_insights}}
```

## Usage

```bash
# Generate weekly review
python weekly_review.py --generate

# Review specific week
python weekly_review.py --week 2025-11-11

# Auto-process inbox
python weekly_review.py --process-inbox --auto
```

## Example Output

```markdown
# Weekly Review - Week of Nov 18, 2025

## Summary
- 📥 Inbox: 12 notes processed
- ✅ Projects: 2 completed, 5 active, 1 stalled
- 📝 Notes created: 23
- 🔗 Links added: 47

## Projects Update

**Completed ✅**
- Website Redesign (on time, under budget)
- Q4 Marketing Campaign (successful launch)

**Active 🔄**
- Second Brain Toolkit (80% complete)
- iOS App Prototype (needs attention - no updates in 14 days)
- Team Training Program (on track)

**Attention Needed ⚠️**
- iOS App Prototype: Last update 14 days ago
  → Recommendation: Schedule planning session or archive

## Areas Health Check
- ✅ Health & Fitness: 3 workouts logged
- ✅ Knowledge Management: System running smoothly
- ⚠️ Finance: Monthly review overdue by 5 days
- ✅ Career Development: 2 learning sessions completed

## This Week's Highlights
- Launched website redesign 3 days early
- Processed 47 articles into Resources
- Created 5 new project connections

## Next Week's Priorities
1. **Complete Second Brain Toolkit** (final push)
2. **Decide on iOS App Prototype** (continue or archive?)
3. **Complete monthly financial review** (overdue)

## AI Insights
You're maintaining good momentum on active projects. The Website Redesign
success shows your planning process is working well. Consider applying the
same detailed requirements approach to other projects.

Inbox processing is excellent - you're staying on top of inputs. The 47 new
links show you're building a connected knowledge graph.

⚠️ Watch: iOS App Prototype has gone silent. Decide this week: commit or archive.

**Recommendation:** Block Friday morning for deep work on Second Brain Toolkit
to finish strong before the weekend.
```

## Files

- `weekly_review.py` - Main review generator
- `project_analyzer.py` - Project health analysis
- `inbox_processor.py` - Automated inbox processing
- `templates/` - Review templates
