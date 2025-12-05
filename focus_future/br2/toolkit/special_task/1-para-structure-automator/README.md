# PARA Folder Structure Automator

**Tier**: 1 (Simple Automation)
**Category**: Special Task - Second Brain Implementation

## Purpose

Automatically creates and maintains PARA folder structure in Obsidian vault. Ensures consistent organization according to Second Brain methodology.

## What It Does

- Creates PARA folder hierarchy
- Generates README files for each folder
- Sets up Obsidian-specific configuration
- Creates index files with Dataview queries
- Maintains folder structure consistency
- Guides users on PARA categorization

## PARA Structure

```
📁 Obsidian Vault/
├── 📁 1-Projects/
│   ├── README.md
│   ├── _Projects Dashboard.md
│   ├── 📁 Active/
│   └── 📁 Templates/
├── 📁 2-Areas/
│   ├── README.md
│   ├── _Areas Dashboard.md
│   └── 📁 Templates/
├── 📁 3-Resources/
│   ├── README.md
│   ├── _Resources Dashboard.md
│   └── 📁 Templates/
├── 📁 4-Archives/
│   ├── README.md
│   ├── _Archives Dashboard.md
│   ├── 📁 Projects/
│   ├── 📁 Areas/
│   └── 📁 Resources/
└── 📁 0-Inbox/
    ├── README.md
    └── _Inbox Dashboard.md
```

## Usage

```bash
# Initialize PARA structure in vault
python para_automator.py --init --vault ~/Obsidian/MyVault

# Add new project
python para_automator.py --new-project "Build Second Brain Toolkit"

# Add new area
python para_automator.py --new-area "Health & Fitness"

# Validate structure integrity
python para_automator.py --validate --fix
```

## Example: Projects Dashboard

```markdown
# Projects Dashboard

## Active Projects

```dataview
TABLE
  status as "Status",
  deadline as "Deadline",
  file.mtime as "Last Modified"
FROM "1-Projects/Active"
WHERE status != "completed"
SORT deadline ASC
```

## Recently Completed

```dataview
TABLE
  completed_date as "Completed",
  outcome as "Outcome"
FROM "1-Projects/Active"
WHERE status = "completed"
SORT completed_date DESC
LIMIT 5
```

## Project Template
[[Project Template]] - Use this for new projects
```

## PARA Decision Guide

```
Is it something you're working on RIGHT NOW with a deadline?
├─ YES → Projects
└─ NO ↓

Is it an ongoing responsibility or standard you maintain?
├─ YES → Areas
└─ NO ↓

Is it a topic of interest for future reference?
├─ YES → Resources
└─ NO ↓

Is it something completed or no longer active?
└─ YES → Archives
```

## Automated README Content

**Projects/README.md:**
```markdown
# Projects

Projects are short-term efforts with specific goals and deadlines.

**Examples:**
- Launch new product
- Write a book
- Plan a trip
- Complete a course

**Criteria:**
- Has a clear goal
- Has a deadline
- Will be "done" at some point

**When to Archive:**
When the project is complete or cancelled, move to `4-Archives/Projects/`.
```

## Files

- `para_automator.py` - Main structure creation script
- `templates/` - Dashboard and README templates
- `decision_guide.yaml` - PARA categorization rules
- `dataview_queries/` - Pre-built Dataview queries
