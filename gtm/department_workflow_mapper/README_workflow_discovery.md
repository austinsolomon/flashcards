# Workflow Discovery System

## Overview

This system helps you identify and prioritize automation candidates for any department in your organization. Instead of manually brainstorming what to automate, use these prompts to systematically discover high-ROI workflows that are ready to submit through your tiered automation architecture.

## The Problem This Solves

❌ **Before:**
- "We should automate something in marketing" (too vague)
- Guessing which workflows would benefit from automation
- Inconsistent intake submissions missing key details
- Building automations that don't deliver ROI
- No systematic way to compare opportunities across departments

✅ **After:**
- Generate 10 ranked candidates in minutes
- ROI scores guide prioritization
- Ready-to-submit intake previews
- Consistent evaluation framework
- Build the right thing, in the right order

## Files in This System

| File | Purpose | When to Use |
|------|---------|-------------|
| `workflow_discovery_prompt.md` | Full framework and methodology | Reference for how the system works |
| `workflow_discovery_examples.md` | Pre-filled prompts for 6 common departments | Copy/paste for Marketing, Sales, BDR, CS, RevOps, Finance |
| `workflow_discovery_quick_start.md` | 2-minute fill-in-the-blank template | Use for any department not in examples |

## How to Use This System

### Option 1: Use a Pre-Built Department Prompt (Fastest)

1. Open `workflow_discovery_examples.md`
2. Find your department (Marketing, Sales, BDR, CS, RevOps, Finance)
3. **Copy the entire prompt** (it includes context)
4. **Paste into Claude** (or Claude Code)
5. **Receive 10 ranked workflow candidates** with intake previews
6. **Submit top 3** through your intake form

**Time:** 5 minutes

---

### Option 2: Fill-in-the-Blank for Any Department

1. Open `workflow_discovery_quick_start.md`
2. Copy the template
3. Fill in your department's details:
   - Team size
   - KPIs
   - Tools used
   - Top time-sinks
4. Paste into Claude
5. Receive ranked workflow candidates

**Time:** 10 minutes

---

### Option 3: Multi-Department Discovery

Use the multi-department template in `workflow_discovery_quick_start.md` to discover workflows across 3+ teams in one session. This also surfaces **cross-functional automation opportunities** (e.g., Marketing → Sales handoff workflows).

**Time:** 15 minutes

---

## What You Get Back

When you run a discovery prompt, Claude returns:

### 1. **Ranked Workflow Candidates** (10 per department)

Each includes:
- **Priority Score** (1-10)
- **Quick Summary** (the pain point)
- **Time Burden** (hours saved per week)
- **Automation Potential** (why it's a good fit)
- **Suggested Tier** (0-6, maps to your architecture)

### 2. **Ready-to-Submit Intake Previews**

Pre-filled sections for:
- Problem statement
- Current manual process
- Desired automation
- Success criteria
- Key integrations
- Complexity signals

**You just copy/paste and expand with specific details.**

### 3. **ROI Ranking Table**

Sorted by:
```
ROI Score = (Weekly Hours Saved × $100/hr) ÷ Build Complexity
```

Tells you exactly which 3 to start with.

### 4. **Implementation Roadmap**

Suggested build sequence based on dependencies and quick wins.

---

## Example Output (Abbreviated)

```markdown
## Workflow Candidate #1: Auto-Generate Inbound Lead Intelligence Summary

**Priority Score:** 9.2/10

**Time Burden:**
- Per occurrence: 12 minutes
- Frequency: 25 leads/day (per BDR)
- Team members affected: 8 BDRs
- **Total weekly hours:** 80 hours/week

**Suggested Tier:** 2-3 (n8n + Claude API)

**Ready-to-Submit Intake Preview:**
1. PROBLEM STATEMENT
   When inbound leads come through Marketo, BDRs waste 10-15 min/lead
   manually researching companies...

[Full intake form preview included]
```

---

## Workflow Discovery → Intake → Build Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: DISCOVER (This System)                              │
│ Run discovery prompt → Get 10 ranked candidates             │
│ Time: 5-10 minutes                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: PRIORITIZE                                          │
│ Review ROI scores → Validate with team → Pick top 3        │
│ Time: 30 minutes                                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: SUBMIT INTAKE                                       │
│ Copy "Ready-to-Submit" preview → Expand details →          │
│ Submit through intake form                                  │
│ Time: 15 minutes per workflow                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: ROUTE TO TIER                                       │
│ Intake form routes to appropriate tier (0-6)                │
│ Complexity signals → Tier mapping (automated)               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: BUILD                                               │
│ Implementation team builds using tier-appropriate tools     │
│ - Tier 0-1: No-code (Zapier)                               │
│ - Tier 2-3: Workflows (n8n + Claude API)                   │
│ - Tier 4-6: Agents (LangGraph, CrewAI)                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 6: MEASURE & ITERATE                                   │
│ Track success criteria → Adjust → Move to next candidate   │
└─────────────────────────────────────────────────────────────┘
```

---

## Department Coverage

### Currently Available (Pre-Built Prompts)

- ✅ **Marketing** - Campaign execution, content, analysis
- ✅ **Sales (AEs)** - Deal research, proposals, pipeline
- ✅ **BDR/SDR** - Lead research, outreach, enrichment
- ✅ **Customer Success** - QBRs, health monitoring, renewals
- ✅ **Revenue Operations** - Reporting, data quality, attribution
- ✅ **Finance/FP&A** - Reconciliation, variance, board decks

### Easily Adaptable (Use Quick Start Template)

- Product Management
- Engineering/DevOps
- HR/Recruiting
- Legal/Compliance
- IT/Support
- Executive/Strategy

---

## Common Workflow Patterns Discovered

Based on 100+ workflow discoveries, here are the most common high-ROI patterns:

### Pattern 1: **Research → Summary → Action**
*Examples:* Lead intelligence, deal research, competitive analysis
- **Tier:** 2-3
- **Avg Time Saved:** 60-80 hrs/week
- **Key Tech:** Claude API for synthesis + NLG

### Pattern 2: **Multi-Source Data → Report**
*Examples:* Campaign dashboards, pipeline forecasts, QBR decks
- **Tier:** 1-3
- **Avg Time Saved:** 40-60 hrs/week
- **Key Tech:** API integrations + data transformation

### Pattern 3: **Alert → Triage → Route**
*Examples:* Support ticket routing, anomaly detection, lead scoring
- **Tier:** 2-4
- **Avg Time Saved:** 30-50 hrs/week
- **Key Tech:** Classification models + business logic

### Pattern 4: **Template + Data → Personalized Content**
*Examples:* Email drafts, proposals, outreach sequences
- **Tier:** 2-3
- **Avg Time Saved:** 50-70 hrs/week
- **Key Tech:** Claude API for NLG

### Pattern 5: **Data Quality → Validation → Enrichment**
*Examples:* CRM hygiene, lead enrichment, attribution cleanup
- **Tier:** 1-2
- **Avg Time Saved:** 20-40 hrs/week
- **Key Tech:** Data validation rules + external APIs

---

## Success Metrics

Track these for each workflow you build:

### Time Savings
- ✅ Baseline: Manual time per occurrence
- ✅ Target: Automated time per occurrence
- ✅ Actual: Measured after 30 days
- ✅ Weekly hours saved: (Baseline - Actual) × Frequency

### Quality Metrics
- ✅ Error rate: Manual vs. Automated
- ✅ Consistency: Variance in output quality
- ✅ User satisfaction: Team spot-check scores

### Business Impact
- ✅ Capacity increase: Tasks completed per day/week
- ✅ Speed improvement: Cycle time reduction
- ✅ Revenue impact: Pipeline/bookings influenced

### Cost Efficiency
- ✅ Build cost: Engineering hours + tools
- ✅ Run cost: API calls + infrastructure per month
- ✅ ROI: (Time saved × $100/hr - Run cost) ÷ Build cost

---

## Tips for Great Results

### ✅ DO:
- Be specific about team size and volume
- Include actual time estimates (ask the team)
- List all tools/systems (Claude will check for APIs)
- Mention compliance constraints upfront
- Focus on repetitive, high-frequency tasks

### ❌ DON'T:
- Say "automate marketing" (too vague)
- Guess wildly at time savings
- Submit workflows that happen monthly (low frequency)
- Ignore integration complexity
- Skip validation with the team doing the work

---

## FAQ

**Q: How accurate are the time savings estimates?**
A: Claude estimates based on typical task times. Validate with your team before submitting intake.

**Q: What if my department isn't in the examples?**
A: Use the Quick Start template - it works for any function.

**Q: Can I customize the discovery criteria?**
A: Yes! Add constraints at the end of the prompt (e.g., "prioritize workflows that reduce customer wait time").

**Q: How many workflows should I discover at once?**
A: Start with 1 department, 10 candidates. Validate ROI rankings before expanding.

**Q: What if the suggested tier seems wrong?**
A: The intake form allows override. Note your reasoning in "Constraints" section.

**Q: Should I build all 10 candidates?**
A: No. Build top 3, measure results, then decide on next batch.

---

## Next Steps

1. **Choose your approach:**
   - Pre-built department prompt → `workflow_discovery_examples.md`
   - Custom department → `workflow_discovery_quick_start.md`

2. **Run the discovery** (paste into Claude)

3. **Review the output** (10 ranked candidates)

4. **Submit top 3** through intake form

5. **Build → Measure → Iterate**

---

## Example Session Flow

```bash
# 1. User opens workflow_discovery_examples.md
# 2. Copies the "BDR Team" prompt
# 3. Pastes into Claude
# 4. Claude returns:
#    - 10 workflow candidates
#    - ROI ranking table
#    - Ready-to-submit intake previews
# 5. User reviews, picks #1: "Auto-Generate Lead Intelligence"
# 6. Copies the intake preview
# 7. Expands with specific details
# 8. Submits through intake form
# 9. System routes to Tier 2-3 (n8n + Claude)
# 10. Build team implements
# 11. Measures: 80 hrs/week saved
# 12. Moves to candidate #2
```

---

## Maintenance

- **Quarterly:** Re-run discovery for departments as tools/processes change
- **After major hires:** Adjust team size and re-calculate ROI
- **After automation wins:** Update baseline times (manual process is faster now)
- **Cross-functional:** Run multi-department discovery to find handoff optimizations

---

## Support

- **Documentation:** See `workflow_discovery_prompt.md` for full methodology
- **Examples:** See `workflow_discovery_examples.md` for 6 departments
- **Quick Start:** See `workflow_discovery_quick_start.md` for custom departments
- **Issues:** Submit feedback via your intake form with "Discovery System" tag
