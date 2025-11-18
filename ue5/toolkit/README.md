# UE5 Developer Toolkit

## Special Task: Massive Level Development
Building a large-scale UE5 level with foliage, landscape, PCG, metahumans, Lumen, Niagara (fire, lightning), collisions (Blueprints & C++), and small LLM models for NPC AI.

## Automation Index

### Special Task Automations (5)
These automations directly support the massive level development task:

1. **PCG Rule Validator & Optimizer** (Tier 3) - `special_task/1-pcg-rule-validator/`
2. **Foliage Performance Analyzer** (Tier 2) - `special_task/2-foliage-performance-analyzer/`
3. **Blueprint-to-C++ Collision Converter** (Tier 3) - `special_task/3-blueprint-to-cpp-converter/`
4. **Niagara Performance Profiler** (Tier 2) - `special_task/4-niagara-performance-profiler/`
5. **LLM NPC Behavior Validator** (Tier 3) - `special_task/5-llm-npc-validator/`

### Recurring Development Automations (5)
These automations support ongoing UE5 development workflows:

6. **Asset Naming Convention Enforcer** (Tier 1) - `recurring/6-asset-naming-enforcer/`
7. **Blueprint Complexity Analyzer** (Tier 2) - `recurring/7-blueprint-complexity-analyzer/`
8. **Automated Build & Cook Pipeline** (Tier 2) - `recurring/8-build-cook-pipeline/`
9. **C++ Memory Leak Detector** (Tier 2) - `recurring/9-memory-leak-detector/`
10. **Lighting Build Quality Checker** (Tier 2) - `recurring/10-lighting-quality-checker/`

## Quick Start

Each automation directory contains:
- `README.md` - Detailed documentation
- `automation.yaml` - Automation configuration
- Implementation files (Python scripts, bash scripts, or config files)
- Example usage and outputs

## Tier Definitions

- **Tier 1**: Simple, deterministic automations (scripts, templates)
- **Tier 2**: Context-aware with basic AI (Claude with specific prompts)
- **Tier 3**: Autonomous agents with complex decision-making
