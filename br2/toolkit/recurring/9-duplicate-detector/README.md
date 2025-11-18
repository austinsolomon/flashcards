# Duplicate Note Detector & Merger

**Tier**: 2 (Context-Aware AI)
**Category**: Recurring Development

## Purpose

Finds duplicate or highly similar notes and suggests merging them. Prevents knowledge fragmentation.

## What It Does

- Detects exact duplicates (same content)
- Finds semantic duplicates (similar meaning)
- Suggests note mergers
- Preserves unique information from both
- Updates links after merging
- Prevents future duplicates

## Usage

```bash
# Detect duplicates
python duplicate_detector.py --scan

# Find similar notes
python duplicate_detector.py --similarity 0.85

# Merge duplicates
python duplicate_detector.py --merge --note1 "Note A" --note2 "Note B"
```

## Example Output

```
Duplicate Detection Report

Found 3 potential duplicates:

1. Exact Duplicate (100% match)
   - "Meeting Notes - CEO - 2025-11-18.md"
   - "CEO Meeting Nov 18.md"
   → Recommendation: Merge, keep first title (standardized)

2. High Similarity (92% match)
   - "Atomic Habits Summary.md"
   - "Book Notes - Atomic Habits.md"
   → Recommendation: Merge into "Book Notes - Atomic Habits.md"

3. Partial Overlap (78% match)
   - "Productivity Tips.md"
   - "Productivity Hacks.md"
   → Recommendation: Review manually, may have unique content

Merge duplicates? (y/n/review)
```

## Merge Process

- Combines unique content from both notes
- Preserves metadata from both
- Updates all inbound links
- Archives original duplicates
- Generates merge report

## Files

- `duplicate_detector.py` - Main detection engine
- `semantic_similarity.py` - Claude-powered similarity analysis
- `note_merger.py` - Intelligent note merging
