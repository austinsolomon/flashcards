# Foliage Performance Analyzer

**Tier**: 2 (Context-Aware AI)
**Category**: Special Task - Massive Level Development

## Purpose

Analyzes foliage density, distribution, and performance metrics across massive landscapes. Provides real-time feedback on performance bottlenecks and suggests optimizations for draw calls, LODs, and culling strategies.

## What It Does

- Monitors foliage instance counts per region
- Analyzes draw call batching efficiency
- Validates nanite usage for high-poly foliage
- Checks for overlapping foliage volumes
- Measures GPU occlusion culling effectiveness
- Generates heat maps of performance-critical areas

## Use Case

When painting or procedurally placing millions of foliage instances, it's critical to maintain performance targets. This automation continuously monitors your level and alerts you before performance degrades.

## Implementation

```bash
#!/bin/bash
# foliage_analyzer.sh

# Extract foliage data from level
UnrealEditor-Cmd.exe \
  -run=FoliageReport \
  -map="$LEVEL_PATH" \
  -output="foliage_data.json"

# Analyze with Claude
claude-code analyze \
  --input foliage_data.json \
  --prompt "Analyze foliage performance for 60 FPS target on Epic settings" \
  --output performance_report.md
```

## Usage

```bash
# Analyze current level
./foliage_analyzer.sh --level "Content/Maps/MainWorld.umap"

# Monitor in real-time during level design
./foliage_analyzer.sh --level "Content/Maps/MainWorld.umap" --watch

# Generate heatmap of problematic areas
./foliage_analyzer.sh --level "Content/Maps/MainWorld.umap" --heatmap
```

## Example Output

```
Foliage Performance Analysis
Level: MainWorld.umap
Date: 2025-11-18

SUMMARY
Total Foliage Instances: 4,234,567
Unique Foliage Types: 23
Estimated Draw Calls: 1,847

PERFORMANCE HOTSPOTS
🔴 Critical: Grid(45, 67) - 234,000 instances
   └─ Recommendation: Split into 4 sub-grids with distance culling

🟡 Warning: Grid(23, 34) - 89,000 instances
   └─ Recommendation: Enable HISM autobatching

✅ Optimal: 89% of grids within performance budget

NANITE OPPORTUNITIES
- Oak_Tree_Hero: 45,000 polys → Convert to Nanite (12,000 instances)
- Rock_Boulder_Large: 23,000 polys → Convert to Nanite (8,500 instances)
- Estimated savings: ~450 draw calls

LOD ISSUES
⚠️  Fern_Cluster: Missing LOD2 and LOD3
⚠️  Grass_Tall: LOD1 transition too aggressive (10m)

RECOMMENDATIONS
1. Enable Virtual Texture Lightmaps for foliage
2. Implement distance-based density scaling
3. Use WorldPartition streaming for distant foliage chunks
4. Consider Nanite for all foliage >10,000 triangles
```

## Configuration

```yaml
# performance_config.yaml
target_fps: 60
graphics_preset: Epic

thresholds:
  max_instances_per_grid: 100000
  max_draw_calls: 2000
  max_triangles_per_frame: 15000000

optimization_strategies:
  - enable_nanite_above_triangle_count: 10000
  - enable_hism_autobatching: true
  - use_distance_based_density: true
  - cull_distance_scale: 1.5
```

## Files

- `foliage_analyzer.sh` - Main analysis script
- `performance_config.yaml` - Configuration file
- `claude_prompt.md` - AI analysis prompt template
- `heatmap_generator.py` - Generates visual performance heatmaps
