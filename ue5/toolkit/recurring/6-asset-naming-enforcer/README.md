# Asset Naming Convention Enforcer

**Tier**: 1 (Simple Automation)
**Category**: Recurring Development

## Purpose

Enforces Unreal Engine asset naming conventions automatically. Prevents technical debt from accumulating due to inconsistent file naming.

## What It Does

- Scans project directories for assets
- Validates names against UE5 naming conventions
- Auto-renames assets or generates warnings
- Checks prefix conventions (BP_, M_, T_, SM_, etc.)
- Validates snake_case vs PascalCase usage
- Detects duplicate or ambiguous names

## Naming Conventions

```
Prefixes:
- BP_   = Blueprint
- M_    = Material
- MI_   = Material Instance
- T_    = Texture
- SM_   = Static Mesh
- SK_   = Skeletal Mesh
- A_    = Animation
- NS_   = Niagara System
- PCG_  = PCG Graph
- WBP_  = Widget Blueprint

Format: PREFIX_AssetName_Variant
Examples:
✅ BP_PlayerCharacter
✅ M_Rock_Wet
✅ T_Grass_Normal
❌ player_blueprint
❌ rock-material
❌ GrassTexture_normal
```

## Usage

```bash
# Check naming conventions
./naming_enforcer.sh --check

# Auto-fix simple violations
./naming_enforcer.sh --fix --backup

# Check specific directory
./naming_enforcer.sh --check --path Content/Characters

# Generate report
./naming_enforcer.sh --check --report violations.md
```

## Example Output

```
Asset Naming Convention Report
Project: MyUE5Project
Scan Date: 2025-11-18

VIOLATIONS FOUND: 23

MISSING PREFIXES (12)
❌ Content/Materials/RockWet.uasset
   → Should be: M_Rock_Wet.uasset

❌ Content/Blueprints/PlayerController.uasset
   → Should be: BP_PlayerController.uasset

INCORRECT CASE (6)
❌ Content/Textures/grass_diffuse.uasset
   → Should be: T_Grass_Diffuse.uasset

WRONG SEPARATORS (5)
❌ Content/Meshes/SM-Tree-Oak.uasset
   → Should be: SM_Tree_Oak.uasset

AUTO-FIX AVAILABLE: 18/23
MANUAL REVIEW NEEDED: 5

Run with --fix to automatically correct violations.
```

## Implementation

```bash
#!/bin/bash
# naming_enforcer.sh

CONTENT_DIR="Content"
VIOLATIONS=()

check_prefix() {
    local file=$1
    local type=$2
    local expected_prefix=$3

    if [[ ! "$file" =~ ^${expected_prefix}_ ]]; then
        VIOLATIONS+=("$file: Missing prefix $expected_prefix")
    fi
}

# Scan all assets
find "$CONTENT_DIR" -name "*.uasset" | while read asset; do
    basename=$(basename "$asset" .uasset)
    dir=$(dirname "$asset")

    # Check based on directory
    if [[ "$dir" == *"/Materials/"* ]]; then
        check_prefix "$basename" "Material" "M"
    elif [[ "$dir" == *"/Blueprints/"* ]]; then
        check_prefix "$basename" "Blueprint" "BP"
    fi
    # ... more checks
done
```

## Files

- `naming_enforcer.sh` - Main enforcement script
- `naming_rules.yaml` - Configurable naming rules
- `exceptions.txt` - Assets exempt from rules
- `auto_rename.py` - Safe renaming with references update
