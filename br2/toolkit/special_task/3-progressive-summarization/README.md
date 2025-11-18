# Progressive Summarization Engine

**Tier**: 3 (Autonomous Agent)
**Category**: Special Task - Second Brain Implementation

## Purpose

Implements Tiago Forte's Progressive Summarization technique using Claude. Automatically highlights and extracts key insights from notes in layers.

## What It Does

- Layer 1: Identifies important passages (bold)
- Layer 2: Highlights most important insights
- Layer 3: Generates executive summary
- Layer 4: Creates actionable remixes
- Maintains original content
- Learns from user feedback

## Progressive Summarization Layers

**Layer 0: Original Content** (raw capture)
**Layer 1: Bold** (10-20% of content)
**Layer 2: Highlight** (10-20% of bolded text)
**Layer 3: Executive Summary** (3-5 key takeaways)
**Layer 4: Remix** (actionable insights, connections)

## Usage

```bash
# Process single note
python progressive_summarization.py --note "Book - Atomic Habits.md"

# Batch process resources folder
python progressive_summarization.py --folder "3-Resources" --recursive

# Progressive refinement
python progressive_summarization.py --note "Article.md" --to-layer 3
```

## Example: Before & After

**Before (Layer 0):**
```markdown
# Article: Building a Second Brain

Tiago Forte developed the Second Brain methodology to help knowledge
workers capture, organize, and retrieve information effectively. The
system is built around the PARA method: Projects, Areas, Resources,
and Archives. Projects are short-term efforts with deadlines. Areas
are ongoing responsibilities. Resources are topics of interest.
Archives are inactive items. The key is to organize information by
actionability, not by category or topic. Progressive Summarization
is a technique for highlighting important passages in layers. First,
you bold the important parts (10-20%). Then you highlight the most
important parts of what you bolded. Finally, you write a summary
of the highlights. This creates a "GPS trail" back to the most
important insights.
```

**After (Layers 1-3):**
```markdown
# Article: Building a Second Brain

Tiago Forte developed the Second Brain methodology to help knowledge
workers **capture, organize, and retrieve information effectively**. The
system is built around the **PARA method: Projects, Areas, Resources,
and Archives**. Projects are short-term efforts with deadlines. Areas
are ongoing responsibilities. Resources are topics of interest.
Archives are inactive items. **The key is to organize information by
actionability, not by category or topic**. Progressive Summarization
is a technique for **highlighting important passages in layers**. First,
you bold the important parts (10-20%). Then you ==highlight== the most
important parts of what you bolded. Finally, you write a summary
of the highlights. This creates a **"GPS trail" back to the most
important insights**.

---

## Executive Summary (Layer 3)

1. **PARA organizes by actionability** - Projects (deadlines), Areas
   (responsibilities), Resources (interests), Archives (inactive)

2. **Progressive Summarization creates a "GPS trail"** - Bold → Highlight →
   Summary → Remix, making key insights instantly discoverable

3. **Organize by actionability, not category** - Information should be
   organized by when/how you'll use it, not by topic

## Actionable Insights (Layer 4)

- [ ] Implement PARA structure in Obsidian vault #todo
- [ ] Use Progressive Summarization on all resource notes #todo
- Connection: This relates to [[GTD Methodology]] - both prioritize actionability

**Related Notes:** [[Second Brain Methodology]], [[PARA Method]], [[Knowledge Management]]
```

## Claude Prompt

```markdown
You are a Progressive Summarization expert. Analyze this note and:

1. LAYER 1 (Bold): Identify 10-20% most important passages. Use **bold**.

2. LAYER 2 (Highlight): From bolded text, identify the top 10-20% most
   critical insights. Use ==highlight==.

3. LAYER 3 (Executive Summary): Write 3-5 bullet points capturing the
   essence of the note. What are the key takeaways?

4. LAYER 4 (Remix): Generate actionable insights:
   - Action items (todo items)
   - Connections to other concepts
   - Applications to current projects

Preserve the original text. Only add formatting and append summaries.
```

## Quality Metrics

- Layer 1: 10-20% of original text
- Layer 2: 10-20% of Layer 1 text
- Layer 3: 3-5 concise bullet points
- Layer 4: 2-4 actionable insights
- Processing time: <30 seconds per note

## Files

- `progressive_summarization.py` - Main summarization agent
- `claude_prompts/` - Summarization prompts by note type
- `quality_checker.py` - Validates summarization quality
- `examples/` - Before/after examples
- `user_feedback.py` - Learns from corrections
