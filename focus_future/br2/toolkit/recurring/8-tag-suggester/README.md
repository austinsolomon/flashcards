# Smart Tag Suggester

**Tier**: 2 (Context-Aware AI)
**Category**: Recurring Development

## Purpose

Suggests relevant tags for notes based on content analysis. Maintains consistent tagging taxonomy across vault.

## What It Does

- Analyzes note content for themes
- Suggests tags from existing taxonomy
- Creates new tags when needed
- Prevents tag sprawl (synonyms, duplicates)
- Maintains tag hierarchy
- Generates tag usage reports

## Usage

```bash
# Suggest tags for note
python tag_suggester.py --note "Atomic Habits.md"

# Batch tag untagged notes
python tag_suggester.py --untagged --batch

# Audit tag consistency
python tag_suggester.py --audit --fix-duplicates
```

## Example Output

```
Tag Suggestions for "Atomic Habits.md"

Recommended tags:
- #book (existing, 45 notes)
- #productivity (existing, 78 notes)
- #habits (existing, 12 notes)
- #behavior-change (new tag, related to habits)

⚠️ Avoid tag sprawl:
- Don't use: #habit (singular, use #habits instead)
- Don't use: #productive (use #productivity)

Apply tags? (y/n)
```

## Tag Hierarchy

```
#productivity
├── #habits
├── #time-management
└── #focus

#knowledge-management
├── #second-brain
├── #note-taking
└── #pkm

#development
├── #programming
├── #web-dev
└── #mobile-dev
```

## Files

- `tag_suggester.py` - Main tagging engine
- `tag_taxonomy.yaml` - Tag hierarchy and rules
- `duplicate_detector.py` - Finds tag synonyms
