# Lighting Build Quality Checker

**Tier**: 2 (Context-Aware AI)
**Category**: Recurring Development

## Purpose

Validates lighting build quality, detects common lighting artifacts, and ensures proper Lumen configuration. Catches issues before they reach QA.

## What It Does

- Analyzes lightmap resolution settings
- Detects lighting artifacts (light bleeding, shadow errors)
- Validates Lumen configuration for quality and performance
- Checks reflection capture placement
- Identifies excessive light overlap
- Suggests optimization opportunities

## Usage

```bash
# Check current level
python lighting_checker.py --level Content/Maps/MainLevel.umap

# Check all levels
python lighting_checker.py --all-levels

# Generate visual artifact report
python lighting_checker.py --level MainLevel.umap --screenshots
```

## Example Output

```
Lighting Quality Report
Level: MainLevel.umap
Mode: Lumen + Baked Lighting (hybrid)

CONFIGURATION
✅ Lumen Global Illumination: Enabled
✅ Lumen Reflections: Enabled
✅ Virtual Shadow Maps: Enabled
⚠️  Ray Tracing: Disabled (consider enabling for hero areas)

QUALITY ISSUES

🔴 Critical: Light Bleeding
   Location: X=1234, Y=5678, Z=90
   Objects: Floor mesh bleeding through wall
   Cause: Insufficient lightmap resolution
   Fix: Increase lightmap resolution from 64 to 256

🟡 Warning: Overlapping Lights
   Location: Interior room 3B
   Count: 8 stationary lights in 5m radius
   Performance impact: High shadow cost
   Recommendation: Consolidate to 3-4 lights

🟡 Warning: Missing Reflection Capture
   Room: Warehouse area
   Size: 50m x 30m
   Recommendation: Add sphere reflection capture

LUMEN OPTIMIZATION

💡 Suggestion: Surface Cache Quality
   Current: Medium
   Recommendation: High for interior areas, Medium for exterior
   Benefit: Better GI quality in detailed areas

💡 Suggestion: Lumen Scene Detail
   38 meshes missing distance field
   Recommendation: Enable "Generate Distance Field" for:
   - SM_DetailedProp_*
   - SM_Architecture_*

PERFORMANCE ANALYSIS

Light complexity view shows:
- 12% of pixels exceed 8 overlapping lights
- Avg: 4.2 lights per pixel ✅
- Max: 23 lights per pixel ⚠️  (optimize)

Shadow cost:
- Cascaded Shadow Maps: 2.1ms ✅
- Lumen shadows: 3.8ms ✅
- Contact shadows: 0.9ms ✅

RECOMMENDATIONS

1. Fix critical light bleeding (3 instances)
2. Reduce light overlap in interior_room_3B
3. Add 4 reflection captures in large rooms
4. Enable distance fields for 38 meshes
5. Consider GPU Lightmass for higher quality bakes

Estimated fixes: 30 minutes
Impact: Significantly improved visual quality
```

## Configuration

```yaml
# quality_standards.yaml
lumen:
  required_for_indoor: true
  gi_quality: high
  reflection_quality: high

lightmaps:
  min_resolution: 128
  max_resolution: 2048
  padding: 4

thresholds:
  max_overlapping_lights: 6
  light_bleeding_tolerance: 0.02
  shadow_cascade_count: 4

quality_checks:
  - light_bleeding
  - shadow_artifacts
  - reflection_quality
  - lightmap_seams
  - excessive_light_overlap
```

## Files

- `lighting_checker.py` - Main quality checker
- `quality_standards.yaml` - Configurable quality rules
- `artifact_detector.py` - Image analysis for visual artifacts
- `lumen_optimizer.py` - Lumen-specific recommendations
- `screenshot_comparison.py` - Before/after comparison
