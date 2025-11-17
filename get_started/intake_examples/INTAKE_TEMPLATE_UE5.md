# AUTOMATION INTAKE REQUEST TEMPLATE
## Domain: UE5 (Game Development)

**Workflow Name:** [Short, descriptive name for this automation]

---

## 1. PROBLEM STATEMENT (2-3 sentences)
[Describe the pain point this automation will solve. Include:]
- What manual work is currently slowing down your team?
- How much time is wasted per occurrence?
- What is the impact on game development velocity or quality?

**Example:**
> When new 3D assets are submitted by artists, technical artists spend 15-20 min/asset manually checking polycount, texture resolution, naming conventions, and UV maps before importing to UE5. This creates a bottleneck where only 15-20 assets/day can be processed, delaying level design by 2-3 days per sprint.

---

## 2. CURRENT MANUAL PROCESS (Step-by-step)
[List each step currently done manually. Be specific about tools, inputs, and decisions made.]

**Example:**
1. Artist uploads .fbx file to shared folder
2. Tech artist receives Slack notification
3. Opens file in Blender/Maya to check:
   - Polycount (must be <50k for props, <100k for characters)
   - Texture resolution (power of 2, max 4k)
   - Naming convention (prefix_category_name_lod#)
4. Checks UV maps for overlaps or stretching
5. Opens Unreal Editor, imports asset manually
6. Applies material presets based on asset category
7. Updates asset tracking spreadsheet
8. Posts validation results to Slack
9. If issues found: documents problems, sends back to artist

**Time per occurrence:** 15-20 minutes/asset
**Frequency:** 20-30 assets/day
**Total weekly burden:** 25-40 hours across team

---

## 3. DESIRED AUTOMATION

### Input:
[What triggers the automation and what data is available?]

**Example:**
- **Trigger:** New .fbx file added to /assets/incoming folder (file watcher)
- **Data Available:**
  - File path and metadata
  - Artist name (from file naming convention)
  - Asset category (from folder structure or filename)
  - Project name/sprint number

### Process:
[Step-by-step automated workflow. Be specific about AI calls, API integrations, and decision logic.]

**Example:**
1. Extract asset metadata (polycount, texture count, UV data) via Python script
2. Run validation rules:
   - Polycount check (category-specific limits)
   - Texture resolution validation (power of 2, max 4k)
   - Naming convention regex match
   - UV overlap detection
3. If image/texture asset: Call GPT-4 Vision API to assess visual quality
4. Generate structured validation report (JSON)
5. Auto-import to UE5 via Python API if validation passes
6. Apply material presets based on asset category (Blueprint automation)
7. Update Notion/Airtable asset tracking database
8. Post validation results to dedicated Slack channel

### Output:
[What is created/updated/delivered after automation runs?]

**Example:**
- **Auto-imported UE5 asset** (if validation passed)
- **Validation report** posted to Slack with:
  - Pass/fail status
  - Detailed metrics (polycount, texture info, UV health)
  - Screenshot preview (if applicable)
  - Recommended fixes (if failed)
- **Asset tracking database** updated with:
  - Import timestamp
  - Validation status
  - Technical specs
  - Assigned to level designer
- **Rejected assets** moved to /assets/review folder with error report

---

## 4. SUCCESS CRITERIA
[Measurable outcomes that define success. Use metrics, percentages, or time savings.]

**Example:**
- [ ] Asset validation time reduced from 15min → <2min per asset
- [ ] Tech artist daily capacity increases from 20 → 60+ assets processed
- [ ] Asset import errors detected pre-import reduced by 80%
- [ ] Level designers receive validated assets within 5 minutes of artist upload
- [ ] Asset quality standards maintained (tech artist spot-check approval >95%)

---

## 5. CONSTRAINTS & REQUIREMENTS

### Must Integrate With:
[List all systems/tools that need to connect]

**Example:**
- Unreal Engine 5.3 (Python Editor API)
- Blender/Maya (command-line export validation)
- Slack (webhook notifications)
- Notion or Airtable (asset database)
- File system (network drive or cloud storage)

### Technical Constraints:
[API limits, cost constraints, performance requirements]

**Example:**
- GPT-4 Vision API calls must stay <$0.30/asset
- System must handle 30-60 assets/day
- Validation must complete within 2 minutes per asset
- Must run on Linux server (Docker container preferred)
- Must support .fbx, .blend, .uasset file formats

### Human-in-the-Loop Requirements:
[What needs manual review/approval?]

**Example:**
- Tech artist must review/approve assets flagged with validation warnings
- Failed assets require manual artist revision before re-submission
- Quality spot-checks: tech artist reviews 10% of auto-imported assets weekly

### Compliance/Security:
[Audit logs, access control, data handling]

**Example:**
- All AI decisions must be logged for asset audit trail
- Asset files must remain on company network (no cloud uploads)
- Only authorized artists can upload to /assets/incoming folder
- Validation reports retained for 90 days

---

## 6. COMPLEXITY SIGNALS (Help the router)

### Decision Complexity:
[Check all that apply - helps determine automation tier]

- [ ] Needs contextual reasoning (e.g., "Is this asset suitable for this game's art style?")
- [ ] Needs natural language generation (e.g., writing artist feedback)
- [ ] Needs multi-source data fusion (e.g., combining file metadata + visual analysis + naming conventions)
- [ ] Requires sequential decision-making (e.g., if validation fails, determine best fix recommendation)
- [ ] Needs to learn from feedback (e.g., improve validation rules based on tech artist corrections)

### Integration Complexity:
[Check all that apply]

- [ ] 1-2 systems (Tier 0-1: simple integrations)
- [ ] 3-4 systems (Tier 2-3: moderate integrations)
- [ ] 5+ systems (Tier 3-4: complex integrations)
- [ ] API rate limits to manage (specify: e.g., OpenAI: 60 requests/min)
- [ ] Real-time trigger required (file watcher, webhook)
- [ ] Batch processing acceptable (scheduled runs)

### State Management:
[Check all that apply]

- [ ] Stateless (each asset processed independently)
- [ ] Stateful (needs to track asset history across submissions)
- [ ] Multi-step agent coordination (e.g., ValidationAgent → ImportAgent → NotificationAgent)
- [ ] Human approval loops (tech artist must approve certain decisions)

### Suggested Tier:
[Based on complexity signals - see tier definitions]

**Tier Estimate:** 2-3 (n8n + GPT-4 Vision OR LangChain agent)

**Reasoning:**
- Event-based trigger (file watcher) = Tier 2
- ONE AI call (vision analysis for quality) = Tier 2
- Multi-system integration (UE5, Slack, database) = Tier 2-3
- Semantic validation (visual quality assessment) = Tier 2
- If agent needs to decide which validations to run = Tier 3

---

## 7. NICE-TO-HAVES (Future iterations)
[Features that would be valuable but aren't required for MVP]

**Example:**
- Auto-generate LOD (Level of Detail) variants for high-poly models
- Suggest material/shader optimizations based on target platform (PC vs console)
- Detect duplicate assets already in the library
- Auto-tag assets with semantic labels (e.g., "medieval", "weapon", "hero character")
- A/B test different validation rule strictness levels
- Predictive analytics: flag artists who frequently submit invalid assets for training
- Integration with version control (Perforce/Git LFS) for asset history

---

## 8. ADDITIONAL CONTEXT

### Team Structure:
[Who will use this automation?]

**Example:**
- 5 3D artists (submit assets)
- 2 tech artists (currently validate manually, will spot-check automated results)
- 3 level designers (consume validated assets)

### Current Pain Points:
[Specific frustrations or blockers]

**Example:**
- Artists often don't know validation failed until hours later
- Naming convention violations are most common error (60% of rejections)
- UV map issues hard to spot without loading in Blender
- No centralized asset tracking - Excel spreadsheet frequently out of sync

### Related Workflows:
[Other automations that might interact with this one]

**Example:**
- Asset backup automation (Tier 1) runs nightly
- Material library updater (Tier 1) syncs shader presets weekly
- Build pipeline automation (Tier 4) packages assets for deployment

---

## ROUTING VALUE FOR AUTOMATION TIERS

| Intake Field | Routing Value |
|---|---|
| **Problem Statement** | Clarifies scope - single workflow, not entire pipeline |
| **Current Process** | Shows manual steps → identifies automation tier |
| **Input/Output** | Defines data contracts → API feasibility check |
| **Success Criteria** | Measurable → validates tier can achieve goals |
| **Constraints** | Surfaces technical limits (API costs, performance) |
| **Complexity Signals** | **Most important** - directly maps to tiers 0-6 |

---

## EXAMPLE: QUICK WIN WORKFLOWS FOR UE5

Use this template for common UE5 automation requests:

1. **Asset quality validator** ← Start here (Tier 2-3)
2. **Blueprint documentation generator** ← Tier 2-3
3. **Performance profiler anomaly detection** ← Tier 3-4
4. **Automated level lighting setup** ← Tier 2-3
5. **Collision mesh generator** ← Tier 1-2
6. **Material instance batch creator** ← Tier 1-2

**Recommendation:** Submit #1 first using this template. Once built, use it as a pattern for the others.
