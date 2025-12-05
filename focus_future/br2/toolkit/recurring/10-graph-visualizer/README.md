# Knowledge Graph Visualizer

**Tier**: 2 (Context-Aware AI)
**Category**: Recurring Development

## Purpose

Generates visual knowledge graphs showing note connections, clusters, and knowledge areas. Makes your Second Brain visible.

## What It Does

- Creates interactive network graphs
- Identifies knowledge clusters
- Highlights hub notes (highly connected)
- Shows orphaned notes (isolated)
- Generates graph metrics
- Creates visual summaries

## Usage

```bash
# Generate full vault graph
python graph_visualizer.py --full

# Graph specific area
python graph_visualizer.py --area "Productivity"

# Find knowledge clusters
python graph_visualizer.py --clusters

# Export for Obsidian Graph View
python graph_visualizer.py --export obsidian
```

## Example Metrics

```
Knowledge Graph Analysis
Vault: MySecondBrain

OVERVIEW
- Total notes: 487
- Total links: 1,243
- Avg links per note: 2.6
- Network density: 0.012

CLUSTERS DETECTED (5)
1. Productivity & Systems (98 notes)
   Hub notes: [[Second Brain Methodology]], [[GTD]]

2. Web Development (67 notes)
   Hub notes: [[React]], [[JavaScript Patterns]]

3. Business & Strategy (54 notes)
   Hub notes: [[Product Strategy]], [[Marketing]]

4. Health & Wellness (43 notes)
   Hub notes: [[Fitness]], [[Nutrition]]

5. Personal Finance (31 notes)
   Hub notes: [[Investing]], [[Budgeting]]

HUB NOTES (>20 connections)
- [[Second Brain Methodology]]: 47 connections
- [[Productivity]]: 38 connections
- [[React]]: 29 connections
- [[GTD]]: 24 connections

ORPHANED NOTES (12)
- Quick Note - Ideas.md (no links)
- Random Thoughts.md (no links)
→ Recommendation: Process and link or archive

RECOMMENDATIONS
✅ Good: High link density in Productivity cluster
✅ Good: Most notes have 2+ links
⚠️ Improve: 12 orphaned notes need linking
💡 Suggestion: Create MOC for Web Development cluster
```

## Visual Output

Generates HTML interactive graph with:
- Nodes sized by connection count
- Color-coded by PARA category
- Hover for note preview
- Click to open note
- Cluster grouping
- Link strength visualization

## Files

- `graph_visualizer.py` - Main visualization engine
- `cluster_detector.py` - Identifies knowledge clusters
- `metrics_calculator.py` - Graph statistics
- `templates/` - HTML visualization templates
