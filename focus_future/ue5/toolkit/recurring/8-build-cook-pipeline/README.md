# Automated Build & Cook Pipeline

**Tier**: 2 (Context-Aware AI)
**Category**: Recurring Development

## Purpose

Automates the build, cook, and packaging process for Unreal Engine projects with intelligent error detection and reporting.

## What It Does

- Automated project building (Development, Shipping, Debug)
- Content cooking for multiple platforms
- Packaging with compression
- Build artifact management
- Error detection and Claude-powered analysis
- Performance regression detection
- Automated deployment to test servers

## Configuration

```yaml
# build_config.yaml
project: MyUE5Project.uproject

platforms:
  - Windows
  - Linux
  - PS5
  - XboxSeries

configurations:
  - Development
  - Shipping

cook_settings:
  compression: enabled
  pak_files: true
  iterative_cooking: true

notifications:
  slack_webhook: "https://hooks.slack.com/..."
  email: "team@example.com"

deployment:
  development_server: "build-server.local:/builds"
  staging_server: "staging.example.com:/releases"
```

## Usage

```bash
# Quick build for testing
./build_pipeline.sh --config Development --platform Windows

# Full shipping build
./build_pipeline.sh --config Shipping --all-platforms

# Cook only (no build)
./build_pipeline.sh --cook-only --platform PS5

# Build with deployment
./build_pipeline.sh --config Shipping --platform Windows --deploy staging
```

## Example Build Output

```
Build Pipeline Started
Project: MyUE5Project
Time: 2025-11-18 14:30:00

[1/5] Cleaning previous builds... ✅ (15s)
[2/5] Building C++ modules... ✅ (4m 23s)
[3/5] Cooking content (Windows)... ✅ (8m 47s)
      - Cooked 4,234 assets
      - Pak size: 2.3 GB (compressed)
[4/5] Packaging... ✅ (2m 10s)
[5/5] Running smoke tests... ✅ (45s)

BUILD SUCCESSFUL
Total time: 16m 20s
Output: Builds/Windows/Shipping/MyUE5Project.exe

PERFORMANCE METRICS
- Binary size: 145 MB (prev: 142 MB) +2.1%
- Startup time: 3.2s (prev: 3.1s) +3.2%
⚠️  Warning: Binary size increased, review recent changes

DEPLOYMENT
Uploading to staging server... ✅
Available at: https://staging.example.com/builds/20251118-1430

Notification sent to: #game-dev Slack channel
```

## Error Handling

When build errors occur, Claude analyzes and provides solutions:

```
BUILD FAILED
Error: Linker error in PlayerCharacter.cpp

Claude Analysis:
The linker cannot find the definition for APlayerCharacter::Attack().
This function is declared in PlayerCharacter.h but not implemented.

Suggested fixes:
1. Add implementation in PlayerCharacter.cpp
2. If the function is Blueprint-native, mark it as BlueprintImplementableEvent
3. Check for typos in function name between .h and .cpp

Related files:
- Source/MyProject/PlayerCharacter.h:45
- Source/MyProject/PlayerCharacter.cpp (missing implementation)
```

## Files

- `build_pipeline.sh` - Main build orchestration
- `build_config.yaml` - Configuration
- `error_analyzer.py` - Claude-powered error analysis
- `performance_tracker.py` - Tracks build metrics over time
- `deploy.sh` - Deployment automation
