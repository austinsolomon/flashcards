# Automation Workflow Intake Form

**Submission Date:** `YYYY-MM-DD`
**Submitted By:** `[Your Name]`
**Department:** `[Marketing / Sales / BDR / Customer Success / Finance / Operations / Other]`
**Priority:** `[High / Medium / Low]`

---

## 1. PROBLEM STATEMENT

**Instructions:** In 2-3 sentences, describe the pain point and business impact. Focus on:
- What manual process is causing the problem?
- What is the business impact? (delays, capacity constraints, errors, costs)
- Who is affected and how often?

**Your Response:**
```
[Example: When inbound leads come through Marketo, BDRs waste 10-15 min/lead
manually researching the company, reviewing form responses, and checking intent
signals before first outreach. This delays response time and reduces daily lead
capacity from 20 to 12 qualified conversations.]

[YOUR RESPONSE HERE]
```

---

## 2. CURRENT MANUAL PROCESS

**Instructions:** List the step-by-step manual workflow as it exists today. Include:
- Each discrete step
- Tools/systems used in each step
- Total time per occurrence
- Frequency (how often this happens)

**Your Response:**
```
Step-by-step process:
1. [Example: BDR receives Slack notification of new Marketo lead]
2. [Example: Opens Salesforce, copies company name]
3. [Example: Opens ZoomInfo, searches company, copies firmographics]
4. [Continue listing steps...]

Time: [X minutes/hours] per occurrence
Frequency: [Y times per day/week/month]
Total weekly burden: [Calculate: Time × Frequency × People]
```

---

## 3. DESIRED AUTOMATION

**Instructions:** Describe what you want the automated version to look like. Break it into three parts:

### 3A. Input (Trigger & Data Sources)
What triggers the automation? What data does it start with?

```
Trigger: [Example: New lead created in Marketo (webhook)]
Data Sources:
- [Example: Lead email, company name, form responses from Marketo]
- [Example: Behavior score from Marketo activity log]
- [Add more as needed]
```

### 3B. Process (What the automation does)
What steps should the automation perform?

```
Process Steps:
1. [Example: Enrich firmographic data via ZoomInfo API]
2. [Example: Summarize intent signals from Marketo activity log]
3. [Example: Search recent company news via web search API]
4. [Example: Generate structured lead brief using Claude API]
5. [Example: Draft personalized outreach email using Claude API]
```

### 3C. Output (Results & Deliverables)
What gets created, updated, or sent?

```
Outputs:
- [Example: Auto-populated Salesforce lead record with Intelligence Summary field]
- [Example: Pre-drafted email in Salesforce "Next Steps" field]
- [Example: Slack notification to assigned BDR with summary]
```

---

## 4. SUCCESS CRITERIA

**Instructions:** Define measurable outcomes that prove the automation is working. Include:
- Time savings (before → after)
- Capacity improvements (throughput before → after)
- Quality metrics (accuracy, consistency, user satisfaction)
- Speed improvements (cycle time reduction)

**Your Response:**
```
Primary Success Metrics:
1. Time Savings: [Example: Lead research time reduced from 10min → <30sec]
2. Capacity: [Example: BDR daily capacity increases from 12 → 20+ qualified conversations]
3. Speed: [Example: First response time improves from 2hrs → 15min]
4. Quality: [Example: Email personalization quality maintained or improved (BDR spot-check approval)]

How We'll Measure:
- [Example: Track time spent per lead (before/after) for 30 days]
- [Example: Count qualified conversations booked per BDR per day]
- [Example: Measure timestamp from lead creation to first touchpoint]
- [Example: Weekly BDR survey rating email quality 1-5]
```

---

## 5. CONSTRAINTS & REQUIREMENTS

**Instructions:** List any technical, compliance, security, or business constraints. Consider:
- Required integrations (which systems must connect?)
- Cost limits (API usage, infrastructure)
- Compliance requirements (SOC 2, GDPR, HIPAA)
- Security requirements (PII handling, data retention)
- Human-in-the-loop requirements (approval gates, manual reviews)
- Scale requirements (volume, concurrent users)

**Your Response:**
```
Integrations Required:
- [Example: Marketo, Salesforce, ZoomInfo, Slack, Outreach.io]

Cost Constraints:
- [Example: Claude API calls must stay <$0.50/lead]
- [Example: Total monthly cost <$500]

Volume/Scale:
- [Example: Must handle 30-50 leads/day]
- [Example: Peak load: 20 concurrent workflows]

Compliance/Security:
- [Example: Must log all AI decisions for compliance audit]
- [Example: PII must stay within SOC 2-compliant systems]
- [Example: No auto-send of external communications (human approval required)]

Other Requirements:
- [Example: BDR must review/approve email before send]
- [Example: Must integrate with existing Outreach.io cadences]
```

---

## 6. COMPLEXITY SIGNALS

**Instructions:** Help the routing system determine which tier (0-6) is appropriate. Check all that apply:

### Decision Complexity
- [ ] Requires contextual reasoning (not just if/then logic)
- [ ] Requires natural language understanding or generation
- [ ] Requires multi-source data synthesis
- [ ] Requires learning from past decisions
- [ ] Requires domain expertise or specialized knowledge

**If checked, explain:**
```
[Example: Needs contextual reasoning to synthesize company research from multiple
sources (ZoomInfo, web search, Marketo) into coherent brief. Needs NLG to draft
personalized emails that sound human and reference specific intent signals.]
```

### Integration Complexity
- [ ] Connects 3+ systems
- [ ] Requires API rate limit management
- [ ] Requires real-time webhooks or streaming data
- [ ] Requires bidirectional sync between systems
- [ ] Requires handling of API failures/retries

**If checked, explain:**
```
[Example: Integrates 5 systems (Marketo, Salesforce, ZoomInfo, Slack, Outreach).
ZoomInfo has 100 req/min rate limit that needs throttling. Marketo webhook triggers
real-time execution. Must handle ZoomInfo API failures gracefully.]
```

### State Management
- [ ] Requires multi-step coordination (Step 2 depends on Step 1 results)
- [ ] Requires long-running processes (>5 minutes)
- [ ] Requires human approval gates mid-workflow
- [ ] Requires persistent memory across executions
- [ ] Requires rollback/undo capability

**If checked, explain:**
```
[Example: Single-pass enrichment + generation workflow. No multi-step coordination
needed. Executes in <2 minutes. No persistent memory required.]
```

### Suggested Tier (Optional)
If you have a sense of which tier this belongs in (0-6), note it here:

```
Suggested Tier: [0 / 1 / 2 / 3 / 4 / 5 / 6]
Reasoning: [Example: Tier 2-3 because it needs Claude API for synthesis/NLG and
orchestrates multiple API calls, but doesn't require multi-agent coordination or
complex state management]
```

---

## 7. ADDITIONAL CONTEXT

**Instructions:** Anything else that would help implementers understand this workflow?

### Current Workarounds
```
[Example: BDRs currently use a shared Notion template to copy/paste research,
but it's inconsistent and often skipped when busy]
```

### Related Workflows
```
[Example: This feeds into our existing Outreach.io cadence system. After the
initial email is approved, BDRs add prospects to cadence "Inbound - High Intent"]
```

### Known Edge Cases
```
[Example: Sometimes ZoomInfo doesn't have data for very small companies (<10 employees).
In those cases, skip enrichment and note "Manual research required" in summary]
```

### Dependencies
```
[Example: Requires Marketo webhook integration to be set up first (IT owns this)]
```

### Nice-to-Haves (Future Iterations)
```
[Example:
- Adaptive email tone based on industry/seniority
- Auto-prioritize leads by ICP fit score
- A/B test subject lines and track open rates
- Feedback loop: BDR marks "good/bad" summaries → improve prompts over time]
```

---

## Submission Checklist

Before submitting, confirm:
- [ ] Problem statement clearly describes pain point and impact
- [ ] Manual process includes all steps, time estimates, and frequency
- [ ] Desired automation specifies trigger, process, and outputs
- [ ] Success criteria are measurable and specific
- [ ] All required integrations are listed
- [ ] Complexity signals help indicate appropriate tier
- [ ] Cost constraints are noted (if applicable)
- [ ] Compliance/security requirements are documented (if applicable)

---

## What Happens Next?

1. **Intake Review (1-2 business days)**
   Your submission will be reviewed for completeness and clarity.

2. **Tier Assignment (automated or manual)**
   The routing system (or human reviewer) will assign this to the appropriate tier (0-6) based on complexity signals.

3. **Approval & Prioritization**
   Approved workflows are added to the implementation backlog and prioritized by ROI score.

4. **Build & Test**
   Implementation team builds the automation using tier-appropriate tools and tests with your team.

5. **Deployment & Measurement**
   Automation goes live, and we track success metrics for 30 days.

6. **Iteration**
   Based on results, we refine and consider expanding to "nice-to-haves."

---

## Need Help?

- **Not sure which tier?** Leave "Suggested Tier" blank - the routing system will determine it.
- **Don't know exact time savings?** Estimate and note "estimated - needs validation"
- **Missing technical details?** Submit what you know - we'll schedule a follow-up session
- **Want to see examples?** Check `/intake_system/intake_examples/` for filled-out samples

**Questions?** Contact: [automation-intake@yourcompany.com] or Slack: [#automation-requests]
