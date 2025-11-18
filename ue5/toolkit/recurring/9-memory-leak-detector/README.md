# C++ Memory Leak Detector

**Tier**: 2 (Context-Aware AI)
**Category**: Recurring Development

## Purpose

Detects memory leaks in C++ components using UE5's memory profiling tools and static analysis. Critical for maintaining stable performance in long play sessions.

## What It Does

- Runs automated memory profiling sessions
- Detects growing memory allocations
- Identifies missing UProperty() macros
- Finds improper pointer management
- Validates garbage collection integration
- Suggests UPROPERTY and TSharedPtr usage

## Usage

```bash
# Profile current project
python memory_leak_detector.py --profile 300  # 5 min session

# Analyze specific classes
python memory_leak_detector.py --class AEnemyCharacter --class AProjectile

# Static analysis only
python memory_leak_detector.py --static-only --path Source/
```

## Example Output

```
Memory Leak Detection Report
Session: 5 minutes of gameplay simulation

LEAKS DETECTED: 3

🔴 Critical: AProjectileActor
   Growth rate: +2.3 MB/min
   Cause: Particle systems not being destroyed

   Location: Source/Combat/ProjectileActor.cpp:67
   Code:
   ```cpp
   // Spawning without tracking lifetime
   UGameplayStatics::SpawnEmitterAtLocation(this, ImpactParticle, Location);
   ```

   Fix:
   ```cpp
   // Store and destroy with projectile
   ImpactParticleComponent = UGameplayStatics::SpawnEmitterAtLocation(...);
   // In destructor: ImpactParticleComponent->DestroyComponent();
   ```

🟡 Warning: UInventoryComponent
   Growth rate: +400 KB/min
   Cause: TArray growing without bounds

   Recommendation: Implement max inventory size or use TCircularBuffer

✅ No leaks in: Character movement, AI controllers, UI widgets

STATIC ANALYSIS WARNINGS

⚠️  Missing UPROPERTY() in Source/Player/InventoryItem.h:23
   ```cpp
   class UInventoryItem : public UObject
   {
       TArray<UTexture2D*> Icons;  // ⚠️  Not marked for GC
   };
   ```
   Fix: Add UPROPERTY() to prevent dangling pointers
```

## Files

- `memory_leak_detector.py` - Main detection script
- `static_analyzer.py` - Code analysis for common mistakes
- `profile_config.yaml` - Profiling parameters
- `common_patterns.md` - Memory leak patterns and fixes
