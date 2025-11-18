# Project Archive Automator

**Tier**: 2 (Context-Aware AI)
**Category**: Special Task - Second Brain Implementation

## Purpose

Automatically archives completed projects according to Second Brain methodology. Moves inactive projects to archives with proper metadata and creates project retrospectives.

## What It Does

- Detects completed/stalled projects
- Moves projects to Archives with context
- Generates project retrospectives
- Creates archival metadata
- Cleans up project references
- Updates project dashboard

## Archive Triggers

**Auto-Archive Criteria:**
- Status set to "completed" or "cancelled"
- Deadline passed by >30 days with no activity
- No modifications in >60 days
- Manual archive request

## Usage

```bash
# Archive completed project
python project_archiver.py --project "Website Redesign" --status completed

# Auto-detect and archive stale projects
python project_archiver.py --auto-detect --threshold 60

# Generate retrospective only
python project_archiver.py --project "Marketing Campaign" --retrospective

# Bulk archive
python project_archiver.py --status completed --batch
```

## Archive Process

```
1. Detect archive candidates
   └─ Check status, deadline, last modified

2. Generate retrospective
   └─ Claude analyzes project notes for insights

3. Move to Archives
   └─ 1-Projects/Active/X → 4-Archives/Projects/2025/X

4. Update metadata
   └─ Add archived_date, outcome, lessons_learned

5. Clean references
   └─ Update dashboard, remove from active lists

6. Notify user
   └─ Summary of archived projects
```

## Example: Auto-Generated Retrospective

**Project:** "Website Redesign"

```markdown
---
type: project
status: completed
start_date: 2025-09-01
deadline: 2025-11-15
completed_date: 2025-11-12
archived_date: 2025-11-18
outcome: success
tags: [project, completed, web-development]
---

# Project: Website Redesign ✅

**Status:** Completed
**Duration:** 73 days (planned: 75 days)
**Outcome:** Success - launched on time

## Retrospective (Auto-Generated)

### What Went Well ✅
- Finished 3 days ahead of schedule
- Design feedback loop was efficient (Figma collaboration)
- Developer handoff was smooth (detailed specs)
- Performance improvements: 40% faster page load

### What Could Improve ⚠️
- Initial requirements were vague (caused 2 weeks of rework)
- Mobile testing started too late (found issues at end)
- Stakeholder communication could have been more frequent

### Key Learnings 💡
1. **Start with detailed requirements** - Vague specs lead to rework
2. **Test mobile early and often** - Don't wait until end
3. **Weekly stakeholder updates** - Prevent surprise feedback at launch

### Metrics
- Budget: $45K spent (planned: $50K) - 10% under budget ✅
- Timeline: 73 days (planned: 75 days) - On time ✅
- Quality: All acceptance criteria met ✅

### Artifacts
- Final design: [[Figma - Website Redesign]]
- Technical specs: [[Website Redesign - Technical Spec]]
- Launch checklist: [[Launch Checklist - Website]]

### Team
- Designer: Alice
- Developer: Bob
- Project Manager: Charlie

### Related Areas
This project contributes to [[Area - Product Development]]

---

## Original Project Notes

[Original project content preserved below]

## Objective
Redesign company website to improve conversion rates and mobile experience.

## Success Criteria
- [x] Improve mobile page load speed by 30%
- [x] Increase conversion rate by 15%
- [x] Launch by Nov 15, 2025

[Rest of project notes...]

---
**Archived:** 2025-11-18
**Location:** `4-Archives/Projects/2025/Website Redesign/`
```

## Archive Structure

```
4-Archives/
└── Projects/
    ├── 2025/
    │   ├── Website Redesign/
    │   │   ├── Website Redesign.md (main project note)
    │   │   ├── meeting-notes/
    │   │   ├── designs/
    │   │   └── technical-specs/
    │   ├── Marketing Campaign/
    │   └── Product Launch/
    ├── 2024/
    └── 2023/
```

## Stale Project Detection

```bash
Stale Project Report
Date: 2025-11-18

Found 3 projects that may need archiving:

⚠️  "iOS App Prototype"
   Last modified: 2025-08-10 (100 days ago)
   Status: active
   Deadline: 2025-09-01 (passed 78 days ago)
   Recommendation: Archive as "cancelled" or update status

⚠️  "Content Calendar Q3"
   Last modified: 2025-10-01 (48 days ago)
   Status: active
   Deadline: 2025-09-30 (passed)
   Recommendation: Archive as "completed"

⚠️  "Team Offsite Planning"
   Last modified: 2025-09-15 (64 days ago)
   Status: active
   Notes: Offsite happened on 2025-09-20
   Recommendation: Archive as "completed"

Archive these projects? (y/n)
```

## Dashboard Update

**Before Archive:**
```
Active Projects: 8
├─ Website Redesign (completing soon)
├─ iOS App Prototype (stalled)
├─ ...
```

**After Archive:**
```
Active Projects: 5 ✅ Cleaned up!
└─ (Website Redesign archived)

Recently Archived:
├─ Website Redesign (success) - 2025-11-18
├─ iOS App Prototype (cancelled) - 2025-11-18
└─ Content Calendar Q3 (completed) - 2025-11-18
```

## Files

- `project_archiver.py` - Main archival script
- `retrospective_generator.py` - Claude-powered retrospectives
- `stale_detector.py` - Finds inactive projects
- `templates/` - Retrospective templates
- `archive_rules.yaml` - Archive trigger configurations
