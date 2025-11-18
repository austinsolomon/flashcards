# PCG Rule Validator & Optimizer

**Tier**: 3 (Autonomous Agent)
**Category**: Special Task - Massive Level Development

## Purpose

Validates and optimizes Procedural Content Generation (PCG) rules for massive landscapes. Analyzes density patterns, performance impact, and suggests optimizations to prevent runtime bottlenecks in large-scale environments.

## What It Does

- Scans PCG graph assets for potential performance issues
- Analyzes spawn density and draw call implications
- Validates LOD configurations for foliage instances
- Suggests culling strategies for distant vegetation
- Identifies redundant or conflicting PCG rules
- Estimates memory footprint of PCG configurations

## Use Case

When building a massive open-world level with extensive foliage coverage, PCG rules can easily spiral into performance problems. This automation proactively identifies issues before they manifest in-editor or at runtime.

## Implementation

```yaml
# automation.yaml
name: pcg-rule-validator
tier: 3
trigger: on_asset_save
target_pattern: "*.uasset (PCG graphs)"

agent:
  model: claude-sonnet-4.5
  system_prompt: |
    You are an Unreal Engine 5 PCG optimization expert. Analyze PCG graph
    configurations for performance issues in large-scale environments.

  capabilities:
    - Parse UE5 PCG graph JSON exports
    - Calculate theoretical spawn counts
    - Estimate GPU/CPU overhead
    - Suggest optimization strategies

actions:
  - name: validate_density
    description: Check if spawn density exceeds performance budgets

  - name: analyze_lods
    description: Verify LOD chains are properly configured

  - name: suggest_optimizations
    description: Provide actionable optimization recommendations
```

## Usage

```bash
# Run on specific PCG asset
python pcg_validator.py --asset Content/PCG/ForestBiome_PCG.uasset

# Batch validate all PCG assets in project
python pcg_validator.py --batch --project /path/to/UEProject

# Generate optimization report
python pcg_validator.py --asset Content/PCG/MountainRange_PCG.uasset --report
```

## Example Output

```
PCG Rule Validation Report
Asset: Content/PCG/ForestBiome_PCG.uasset

⚠️  HIGH DENSITY WARNING
   Grid cell: X=1000-2000, Y=1000-2000
   Estimated instances: 45,000 trees
   Recommendation: Reduce density by 30% or implement distance-based culling

✅ LOD Configuration: GOOD
   LOD0: 0-500m (proper triangle budget)
   LOD1: 500-2000m
   LOD2: 2000-5000m

⚠️  MEMORY CONCERN
   Estimated static memory: 2.1 GB
   Recommendation: Consider instance streaming for distant chunks

💡 OPTIMIZATION SUGGESTIONS
   1. Enable hierarchical instanced static meshes (HISM)
   2. Add nanite-enabled variants for hero assets
   3. Implement PCG distance-based density scaling
```

## Files

- `pcg_validator.py` - Main validation script
- `performance_budgets.json` - Configurable performance thresholds
- `optimization_rules.yaml` - AI agent optimization strategies
- `test_assets/` - Sample PCG graphs for testing
