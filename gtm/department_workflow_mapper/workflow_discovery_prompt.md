# Workflow Discovery Prompt Template

## Usage
Replace `{DEPARTMENT}` with: Marketing, Sales, BDRs, Customer Success, Finance, etc.

---

## PROMPT

You are a workflow automation consultant analyzing the **{DEPARTMENT}** function. Your goal is to identify the top 10 automation candidates that would deliver the highest ROI through AI-powered automation.

### Context Questions (Answer these first)
1. **What are the primary KPIs this {DEPARTMENT} team is measured on?**
2. **What is the typical team size and daily workload?**
3. **What are the 3-5 most time-consuming manual tasks?**
4. **Which systems/tools does this team use daily?** (CRM, marketing automation, data tools, etc.)
5. **What percentage of their time is spent on repetitive vs. strategic work?**

### Discovery Framework

For each workflow candidate, evaluate:

**Time-Sink Analysis:**
- How much time per occurrence? (minutes/hours)
- How often does this occur? (daily/weekly/monthly)
- How many people perform this task?
- Total weekly hours = Time × Frequency × People

**Automation Feasibility:**
- Does it involve structured data transformation? ✅/❌
- Does it require contextual reasoning/judgment? ✅/❌
- Does it require multi-source data synthesis? ✅/❌
- Does it require natural language generation? ✅/❌
- Are APIs/integrations available for key systems? ✅/❌

**Business Impact:**
- Does it delay a time-sensitive process? ✅/❌
- Does it block other team members? ✅/❌
- Does manual execution introduce errors/inconsistency? ✅/❌
- Would automation improve customer experience? ✅/❌

### Output Format

For each workflow candidate, provide:

```markdown
## Workflow Candidate #{N}: {Workflow Name}

**Priority Score:** {1-10} (based on time saved × frequency × impact)

**Quick Summary:**
{2-3 sentence description of the manual process and why it's a bottleneck}

**Time Burden:**
- Per occurrence: {X} minutes
- Frequency: {Y} times per day/week
- Team members affected: {Z}
- **Total weekly hours:** {X × Y × Z}

**Automation Potential:**
{1-2 sentences on why this is a good automation candidate}

**Suggested Tier:** {0-6}
{Brief justification based on complexity signals}

**Ready-to-Submit Intake Preview:**

1. **PROBLEM STATEMENT**
{2-3 sentences - what's the pain point and business impact?}

2. **CURRENT MANUAL PROCESS** (abbreviated)
- Step 1: ...
- Step 2: ...
- Step 3: ...
- [Time: X min | Frequency: Y/day]

3. **DESIRED AUTOMATION** (high-level)
- Input: {trigger and data sources}
- Process: {key automation steps}
- Output: {what gets created/updated}

4. **SUCCESS CRITERIA** (key metrics)
- Time reduced from X → Y
- Capacity increased from A → B
- Quality metric: {how to measure}

5. **KEY INTEGRATIONS NEEDED**
{List of systems: CRM, marketing automation, data tools, etc.}

6. **COMPLEXITY SIGNALS**
- Decision complexity: {Low/Med/High - why?}
- Integration complexity: {Low/Med/High - why?}
- State management: {Simple/Complex - why?}
```

### Ranking Criteria

Rank all 10 candidates by **Automation ROI Score**:
```
ROI Score = (Weekly Hours Saved × $100/hr) ÷ (Estimated Build Complexity Score)

Where Build Complexity =
- Tier 0-1: 1x
- Tier 2-3: 2x
- Tier 4-5: 4x
- Tier 6: 8x
```

Present candidates in descending ROI order, with a final recommendation on which 3 to start with.

---

## Example Usage

**Prompt:** "Apply the Workflow Discovery Framework to the **BDR** function at a B2B SaaS company with 8 BDRs handling 200 inbound leads/week."

**Expected Output:** 10 ranked workflow candidates like "Auto-Generate Lead Intelligence Summary" (Tier 2-3), "Automated Follow-up Sequence Selection" (Tier 3-4), "Lead Routing & Assignment" (Tier 1-2), etc.

---

## Integration with Intake Form

Each candidate's "Ready-to-Submit Intake Preview" maps directly to:
- Section 1-2: Problem + Current Process
- Section 3: Desired Automation
- Section 4: Success Criteria
- Section 5-6: Constraints + Complexity Signals

The analyst can copy/paste and expand with specific details during formal intake.

---

## Department-Specific Variations

### For Marketing
Focus on: campaign execution, content production, data analysis, lead management

### For Sales
Focus on: deal research, proposal generation, pipeline management, forecasting

### For BDRs/SDRs
Focus on: lead research, outreach personalization, follow-up sequencing, data enrichment

### For Customer Success
Focus on: health score monitoring, renewal prep, QBR generation, onboarding workflows

### For Finance
Focus on: data reconciliation, report generation, anomaly detection, approval routing

### For Operations
Focus on: data syncing, report aggregation, alert triaging, tool provisioning
