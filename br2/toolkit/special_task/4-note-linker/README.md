# AI-Powered Note Linker

**Tier**: 3 (Autonomous Agent)
**Category**: Special Task - Second Brain Implementation

## Purpose

Automatically discovers and creates connections between notes using Claude. Builds a rich knowledge graph through semantic analysis.

## What It Does

- Analyzes note content for semantic relationships
- Suggests bidirectional links between related notes
- Creates "hub" notes for related concepts
- Identifies missing connections
- Generates "Map of Content" (MOC) notes
- Maintains link quality over time

## Connection Types

**Explicit Connections:**
- Direct references (author, source, citation)
- Shared topics (both discuss X)
- Project relationships (both part of same project)

**Semantic Connections:**
- Similar concepts (different words, same idea)
- Complementary ideas (different perspectives)
- Cause-and-effect relationships
- Examples of broader principles

## Usage

```bash
# Analyze single note for connections
python note_linker.py --note "Atomic Habits.md"

# Build connections across vault
python note_linker.py --vault ~/Obsidian/MyVault --batch

# Generate Map of Content
python note_linker.py --create-moc "Productivity"

# Find orphaned notes (no links)
python note_linker.py --find-orphans --auto-link
```

## Example: Connection Analysis

**Input Note:** "Atomic Habits.md"

**Analysis Output:**
```markdown
# Link Suggestions for "Atomic Habits"

## High Confidence Connections (Auto-link)

1. [[Habit Formation]] - Both discuss habit creation mechanisms
   Suggested link location: "Habits are formed through repetition..."
   Reason: Central concept, bidirectional reference

2. [[Second Brain Methodology]] - Shared theme: systems over goals
   Suggested link location: "Focus on systems, not goals..."
   Reason: Thematic alignment with PARA/Second Brain philosophy

3. [[Project - Build Morning Routine]] - Practical application
   Suggested link location: Add to project's "Key Resources" section
   Reason: Direct application to active project

## Medium Confidence Connections (Review)

4. [[Compound Interest]] - Similar concept: small gains compound
   Suggested addition: "The compound effect of habits is like [[Compound Interest]]
   in finance - small improvements compound over time."

5. [[Feedback Loops]] - Mechanism discussed in book
   Suggested link: "Habits create [[Feedback Loops]] that reinforce behavior"

## Suggested Map of Content

This note would fit well in a "Productivity MOC" with:
- [[Getting Things Done]]
- [[Deep Work]]
- [[Atomic Habits]]
- [[Time Blocking]]
- [[Second Brain Methodology]]

Create MOC? (y/n)
```

## Auto-Generated MOC

```markdown
# Productivity MOC (Map of Content)

A curated collection of notes on productivity systems and techniques.

## Core Methodologies
- [[Second Brain Methodology]] - PARA system for knowledge management
- [[Getting Things Done (GTD)]] - Capture, clarify, organize, reflect, engage
- [[Atomic Habits]] - System-based approach to behavior change

## Techniques
- [[Time Blocking]] - Scheduling focused work periods
- [[Pomodoro Technique]] - 25-minute focus sessions
- [[Progressive Summarization]] - Layer-based note highlighting

## Applications
### Active Projects
- [[Project - Build Second Brain Toolkit]]
- [[Project - Morning Routine Design]]

### Areas
- [[Area - Personal Productivity]]
- [[Area - Knowledge Management]]

## Key Insights
```dataview
TABLE file.ctime as "Created", tags as "Tags"
FROM [[Productivity MOC]]
SORT file.ctime DESC
```

---
**Type:** Map of Content
**Created:** {{date}}
**Last Updated:** {{date}}
```

## Orphan Detection

```bash
Found 12 orphaned notes (no inbound or outbound links):

⚠️  "Meeting Notes 2025-11-15.md"
   Suggested links:
   - [[Project - Website Redesign]] (mentioned in notes)
   - [[Area - Product Development]] (related area)

⚠️  "Article - Flow State Research.md"
   Suggested MOC: [[Productivity MOC]]
   Related notes: [[Deep Work]], [[Focus Techniques]]

Auto-link orphans? (y/n)
```

## Link Quality Metrics

- **Link Density**: Avg 5-10 links per note (optimal)
- **Bidirectional Links**: >80% of links are bidirectional
- **Orphan Rate**: <5% of notes have zero links
- **Hub Notes**: 3-5 highly connected "hub" notes per area

## Files

- `note_linker.py` - Main linking agent
- `semantic_analyzer.py` - Claude-powered semantic analysis
- `moc_generator.py` - Map of Content creator
- `link_quality_checker.py` - Validates link health
- `orphan_detector.py` - Finds disconnected notes
