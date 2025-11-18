# Blueprint Complexity Analyzer

**Tier**: 2 (Context-Aware AI)
**Category**: Recurring Development

## Purpose

Analyzes Blueprint graphs for "spaghetti code" patterns, excessive complexity, and maintainability issues. Helps teams maintain clean, performant Blueprints.

## What It Does

- Calculates cyclomatic complexity
- Detects excessive noodle length and crossing wires
- Identifies performance anti-patterns (tick-heavy logic, expensive loops)
- Finds unused variables and functions
- Suggests refactoring opportunities
- Scores Blueprint maintainability

## Complexity Metrics

```
Scoring System (0-100):
- 90-100: Excellent (clean, maintainable)
- 70-89: Good (minor improvements possible)
- 50-69: Fair (needs refactoring)
- 0-49: Poor (significant technical debt)

Checks:
- Node count
- Function length
- Nesting depth
- Variable usage
- Execution path complexity
- Comment coverage
```

## Usage

```bash
# Analyze single Blueprint
python blueprint_analyzer.py --bp "BP_PlayerCharacter"

# Analyze all Blueprints in project
python blueprint_analyzer.py --all --threshold 70

# Generate refactoring suggestions
python blueprint_analyzer.py --bp "BP_GameMode" --suggest
```

## Example Output

```
Blueprint Complexity Analysis
Asset: BP_EnemyAI
Complexity Score: 42/100 ⚠️  POOR

ISSUES DETECTED

🔴 Critical: Event Tick Complexity
   └─ 47 nodes in Event Tick
   └─ Recommendation: Move to timer-based updates

🔴 Critical: Excessive Nesting
   └─ 8 levels deep in "UpdatePathfinding" function
   └─ Recommendation: Break into smaller functions

🟡 Warning: Long Function
   └─ "CalculateDamage" has 65 nodes
   └─ Recommendation: Extract sub-functions

🟡 Warning: Unused Variables (5)
   └─ LastTargetPosition, CachedHealth, DebugMode, TempVector, OldState

💡 REFACTORING SUGGESTIONS

1. Extract Event Tick logic to separate functions:
   - UpdateMovement()
   - CheckLineOfSight()
   - EvaluateThreat()

2. Create utility Blueprint Function Library:
   - DamageCalculations
   - PathfindingHelpers

3. Use Blueprint Interfaces for cleaner communication

ESTIMATED IMPROVEMENTS
- Performance: 15-20% faster (reduced tick cost)
- Maintainability: 70% easier to understand
- Debugging: Much simpler to troubleshoot
```

## Files

- `blueprint_analyzer.py` - Main analysis script
- `complexity_rules.yaml` - Configurable thresholds
- `refactoring_patterns.md` - Common refactoring strategies
- `claude_prompt.md` - AI analysis template
