# Niagara Performance Profiler

**Tier**: 2 (Context-Aware AI)
**Category**: Special Task - Massive Level Development

## Purpose

Profiles Niagara particle systems (fire, lightning, environmental effects) and identifies GPU/CPU bottlenecks. Critical for maintaining performance with many concurrent visual effects in a massive level.

## What It Does

- Captures GPU/CPU performance metrics for Niagara systems
- Analyzes particle counts, sprite overdraw, and compute shader costs
- Identifies systems exceeding performance budgets
- Suggests LOD strategies for particle effects
- Validates collision and physics interactions
- Recommends batching and instancing opportunities

## Use Case

Complex Niagara systems for fire and lightning can easily consume GPU budget. This automation helps optimize effects while maintaining visual quality through intelligent LODs and performance-based adjustments.

## Implementation

```python
# niagara_profiler.py
import json
import subprocess

class NiagaraProfiler:
    def __init__(self, project_path):
        self.project_path = project_path
        self.performance_data = {}

    def profile_system(self, niagara_asset):
        """Profile a Niagara system using UE5 profiling tools"""

        # Run UE5 with profiling enabled
        cmd = [
            "UnrealEditor-Cmd.exe",
            self.project_path,
            "-run=ProfileNiagara",
            f"-system={niagara_asset}",
            "-duration=60",
            "-output=profile_data.json"
        ]

        subprocess.run(cmd)

        # Load and analyze results
        with open("profile_data.json") as f:
            data = json.load(f)

        return self.analyze_performance(data)

    def analyze_performance(self, data):
        """Use Claude to analyze performance data"""

        analysis_prompt = f"""
        Analyze this Niagara system performance data:

        {json.dumps(data, indent=2)}

        Provide:
        1. Performance bottlenecks (GPU/CPU)
        2. Particle count recommendations
        3. LOD strategy suggestions
        4. Shader optimization opportunities
        5. Collision/physics impact assessment
        """

        # Call Claude for analysis
        result = claude_analyze(analysis_prompt)
        return result
```

## Usage

```bash
# Profile specific Niagara system
python niagara_profiler.py --system "NS_Fire_Large"

# Profile all fire/lightning systems
python niagara_profiler.py --tag "fire" --tag "lightning"

# Generate optimization recommendations
python niagara_profiler.py --system "NS_Lightning" --recommendations

# Compare before/after optimization
python niagara_profiler.py --system "NS_Fire_Large" --compare baseline.json
```

## Example Output

```
Niagara Performance Profile
System: NS_Fire_Large
Duration: 60 seconds (600 frames @ 10 FPS simulated)

PERFORMANCE METRICS
GPU Time: 4.2ms (avg) | 8.7ms (max) | 2.1ms (min)
CPU Time: 1.3ms (avg) | 2.8ms (max) | 0.7ms (min)
⚠️  WARNING: Max GPU time exceeds 5ms budget on Epic settings

PARTICLE STATISTICS
Active Particles: 12,450 (avg) | 23,000 (max)
Sprite Count: 8,200
Mesh Particles: 4,250
Ribbons: 0

BOTTLENECK ANALYSIS
🔴 Critical: GPU Particle Simulation
   └─ Collision queries consuming 2.8ms
   └─ Recommendation: Reduce collision sample count from 8 to 4

🟡 Warning: Sprite Overdraw
   └─ Average overdraw: 3.2x in close-up scenarios
   └─ Recommendation: Implement distance-based sprite size scaling

✅ CPU Performance: Good
   └─ Emitter logic within budget

SHADER ANALYSIS
- Custom HLSL nodes: 3
- Texture samples: 6 (4 color, 2 normal)
- ⚠️  FlipbookUV has expensive gradient calculation

OPTIMIZATION RECOMMENDATIONS

1. COLLISION OPTIMIZATION (Estimated savings: 2.0ms GPU)
   - Reduce collision samples from 8 to 4
   - Use simplified collision shapes
   - Implement collision culling for distant particles

2. LOD STRATEGY (Estimated savings: 1.5ms GPU)
   - LOD0 (0-10m): Current quality
   - LOD1 (10-30m): Reduce particles by 50%, disable collision
   - LOD2 (30-60m): Reduce particles by 75%, simplified shader
   - LOD3 (60m+): Static sprite imposter

3. SHADER OPTIMIZATION (Estimated savings: 0.5ms GPU)
   - Bake flipbook gradients into texture
   - Reduce texture samples from 6 to 4
   - Use cheaper noise functions for distortion

4. PARTICLE BUDGET (Estimated savings: 0.8ms GPU)
   - Cap max particles at 15,000 (currently unlimited)
   - Implement adaptive spawn rate based on frame time

IMPLEMENTATION NOTES
- Test on target hardware (consoles have different bottlenecks)
- Consider GPU particle simulation for large counts
- Use Niagara debugger to visualize bottlenecks
- Profile with multiple simultaneous systems (fire + lightning)

ESTIMATED TOTAL SAVINGS: 4.8ms GPU time
Target achieved: ✅ Under 5ms budget
```

## Configuration

```yaml
# performance_budgets.yaml
target_platform: PC_Epic

budgets:
  gpu_time_ms: 5.0
  cpu_time_ms: 2.0
  max_particles: 20000
  max_sprite_overdraw: 2.0

lod_distances:
  lod0: 0-10
  lod1: 10-30
  lod2: 30-60
  lod3: 60+

optimization_priorities:
  - reduce_collision_cost
  - implement_lods
  - optimize_shaders
  - cap_particle_counts
```

## Files

- `niagara_profiler.py` - Main profiling script
- `performance_budgets.yaml` - Performance targets
- `claude_analysis_prompt.md` - AI analysis template
- `optimization_strategies.yaml` - Common optimization patterns
- `lod_generator.py` - Automated LOD variant generator
