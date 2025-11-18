# Intake Form Submission Guide

## Overview

This guide helps you fill out the automation workflow intake form effectively. Good intake submissions lead to faster implementation, better results, and higher ROI.

---

## General Principles

### ✅ DO:
- **Be specific** - "10 minutes per lead" not "a lot of time"
- **Include real numbers** - Team size, frequency, time estimates
- **Focus on one workflow** - Not "automate all of marketing"
- **Describe current state** - What's actually happening today
- **Define success clearly** - Measurable outcomes, not vague goals
- **List all systems** - Every tool that needs to integrate
- **Note constraints upfront** - Compliance, security, budget limits

### ❌ DON'T:
- Use vague terms like "streamline" or "optimize" without specifics
- Combine multiple unrelated workflows into one submission
- Skip time estimates or frequency data
- Assume technical details ("just use AI")
- Omit compliance or security requirements
- Forget to validate with the people doing the work

---

## Section-by-Section Guide

### Section 1: Problem Statement

**Purpose:** Convince reviewers this workflow is worth automating.

**What to include:**
- Current pain point (what's broken/slow/manual?)
- Business impact (cost, delays, errors, capacity limits)
- Who is affected and how often

**Good Example:**
```
When inbound leads come through Marketo, BDRs waste 10-15 min/lead manually
researching the company, reviewing form responses, and checking intent signals
before first outreach. This delays response time and reduces daily lead capacity
from 20 to 12 qualified conversations.
```

**Why it's good:**
- ✅ Specific time waste (10-15 min)
- ✅ Clear business impact (capacity reduced 20→12)
- ✅ Quantified frequency (per lead, daily)

**Bad Example:**
```
Lead research takes too long and BDRs are overwhelmed. We need to automate this
to be more efficient and improve our sales process.
```

**Why it's bad:**
- ❌ "Too long" - how long exactly?
- ❌ "Overwhelmed" - what does this mean in numbers?
- ❌ "Be more efficient" - not measurable
- ❌ No business impact quantified

---

### Section 2: Current Manual Process

**Purpose:** Help implementers understand what to replicate and improve.

**What to include:**
- Every step, in order
- Tools used in each step
- Time per step (if known) or total time
- Frequency (daily, weekly, per event)
- Number of people performing this task

**Good Example:**
```
Step-by-step process:
1. BDR receives Slack notification of new Marketo lead
2. Opens Salesforce, copies company name
3. Opens ZoomInfo, searches company, copies firmographics
4. Opens Marketo, reviews behavior score and page visits
5. Opens LinkedIn, searches contact + company
6. Opens Google, searches recent news
7. Pastes all into Salesforce notes field (unstructured)
8. Drafts personalized email based on findings
9. Sends via Outreach.io

Time: 12 minutes per lead (average)
Frequency: 25 leads per day per BDR
Team size: 8 BDRs
Total weekly burden: 12 min × 25/day × 8 BDRs × 5 days = 80 hours/week
```

**Why it's good:**
- ✅ Detailed steps with specific tools
- ✅ Actual time measurement
- ✅ Real frequency data
- ✅ Calculated total burden

**Bad Example:**
```
BDRs research leads by looking them up in various systems and then send an email.
This takes a while and happens throughout the day.
```

**Why it's bad:**
- ❌ No specific steps
- ❌ "Various systems" - which ones?
- ❌ "Takes a while" - how long?
- ❌ "Throughout the day" - how many times?

---

### Section 3: Desired Automation

**Purpose:** Define the automation scope clearly.

#### 3A. Input (Trigger & Data Sources)

**Good Example:**
```
Trigger: New lead created in Marketo (webhook to automation system)
Data Sources:
- Lead email, company name, form responses from Marketo
- Behavior score from Marketo activity log (last 30 days)
- Firmographic data from ZoomInfo API
```

**Why it's good:**
- ✅ Specific trigger mechanism (webhook)
- ✅ Clear data sources
- ✅ Notes what data comes from each source

**Bad Example:**
```
Trigger: When a new lead comes in
Data: Lead information
```

**Why it's bad:**
- ❌ "Comes in" where? Marketo? Salesforce? Website?
- ❌ "Lead information" too vague

#### 3B. Process (What the automation does)

**Good Example:**
```
Process Steps:
1. Receive Marketo webhook with lead data
2. Enrich firmographic data via ZoomInfo API (company size, industry, revenue)
3. Summarize intent signals from Marketo activity log (pages visited, content downloaded)
4. Search recent company news via Perplexity API (last 90 days)
5. Generate structured lead brief using Claude API (synthesize all data)
6. Draft personalized outreach email using Claude API (reference intent signals)
7. Create Salesforce task for assigned BDR with summary + draft email
8. Send Slack notification to BDR with key highlights
```

**Why it's good:**
- ✅ Specific sequence
- ✅ Names exact APIs/tools
- ✅ Notes what each step does

**Bad Example:**
```
Use AI to research the lead and write an email.
```

**Why it's bad:**
- ❌ Doesn't specify data sources
- ❌ Doesn't explain the process
- ❌ No mention of how/where results go

#### 3C. Output (Results & Deliverables)

**Good Example:**
```
Outputs:
- Salesforce lead record updated with:
  - "Intelligence Summary" field (structured brief)
  - "Recommended Talking Points" field (3-5 bullets)
  - "Draft Email" field (personalized message)
- Slack message to assigned BDR with:
  - Lead name, company, title
  - ICP fit score (1-10)
  - Top 2 intent signals
  - Link to Salesforce record
- Outreach.io prospect created (but email NOT sent - requires BDR approval)
```

**Why it's good:**
- ✅ Specifies exact fields updated
- ✅ Notes what goes where
- ✅ Clarifies human approval requirement

**Bad Example:**
```
The BDR gets the information they need to reach out.
```

**Why it's bad:**
- ❌ Doesn't specify where information appears
- ❌ Doesn't define format or structure

---

### Section 4: Success Criteria

**Purpose:** Define measurable outcomes to validate ROI.

**What to include:**
- Before/after comparisons
- Specific metrics with targets
- How you'll measure them
- Quality checks (not just speed)

**Good Example:**
```
Primary Success Metrics:
1. Time Savings: Lead research time reduced from 12min → <1min
2. Capacity: BDR daily qualified conversations increase from 12 → 20+
3. Speed: First response time improves from 2hrs (avg) → 15min
4. Quality: Email personalization quality maintained at 4.2/5 or higher (BDR spot-check)

How We'll Measure:
- Track time spent per lead (before/after) using time-tracking tool for 30 days
- Count qualified conversations booked per BDR per day (Salesforce report)
- Measure timestamp from lead creation to first touchpoint (Salesforce → Outreach)
- Weekly BDR survey: rate 10 random AI-drafted emails on 1-5 scale for personalization
```

**Why it's good:**
- ✅ Specific before/after targets
- ✅ Multiple dimensions (time, capacity, speed, quality)
- ✅ Defines measurement method
- ✅ Includes quality check (not just efficiency)

**Bad Example:**
```
BDRs will be more productive and respond to leads faster.
```

**Why it's bad:**
- ❌ "More productive" - by how much?
- ❌ "Faster" - what's the target?
- ❌ No measurement method defined

---

### Section 5: Constraints & Requirements

**Purpose:** Surface technical, compliance, and business limitations early.

**What to include:**
- All systems that need to connect
- Cost limits (API calls, infrastructure)
- Volume/scale requirements
- Compliance requirements (SOC 2, GDPR, HIPAA)
- Security requirements (PII handling, encryption)
- Human approval gates
- Service level requirements (uptime, response time)

**Good Example:**
```
Integrations Required:
- Marketo (webhook + REST API)
- Salesforce (SOAP API for custom fields)
- ZoomInfo (REST API, rate limit: 100 req/min)
- Slack (Webhook for notifications)
- Outreach.io (API v2 for prospect creation)

Cost Constraints:
- Claude API calls: <$0.50/lead (based on 50 leads/day = $25/day max)
- ZoomInfo API: included in existing contract (unlimited calls)
- Total monthly infrastructure: <$500

Volume/Scale:
- Average: 30-50 leads/day
- Peak: up to 100 leads/day (during campaigns)
- Must handle 20 concurrent workflow executions
- Response time: <2 minutes from trigger to completion

Compliance/Security:
- Must log all AI decisions for compliance audit (SOC 2 requirement)
- PII (email, name) must stay within SOC 2-compliant systems (Salesforce, Marketo)
- No data sent to non-approved third parties without explicit consent
- AI prompts must not include sensitive company information

Human-in-the-Loop:
- BDR must review and approve email before send (no auto-send)
- BDR can edit AI-generated summary before saving
- BDR can request re-generation if quality is poor

Other Requirements:
- Must integrate with existing Outreach.io cadences (don't duplicate)
- Must respect "Do Not Contact" list in Salesforce
- Must handle ZoomInfo API failures gracefully (degrade to manual lookup)
```

**Why it's good:**
- ✅ Complete integration list with API details
- ✅ Specific cost calculations
- ✅ Real volume data (average + peak)
- ✅ Compliance requirements spelled out
- ✅ Human approval gates defined
- ✅ Failure handling noted

**Bad Example:**
```
Needs to work with Salesforce and Marketo. Should be cheap and handle a lot of leads.
Must comply with data privacy rules.
```

**Why it's bad:**
- ❌ No API details
- ❌ "Cheap" - what's the budget?
- ❌ "A lot of leads" - how many?
- ❌ "Data privacy rules" - which ones?

---

### Section 6: Complexity Signals

**Purpose:** Help the routing system assign the correct tier (0-6).

**How to use:**
- Check boxes that apply
- Explain WHY you checked them
- Be honest about complexity - underestimating leads to delays

**Decision Complexity Examples:**

✅ **Check "Requires contextual reasoning" if:**
- AI needs to synthesize data from multiple sources
- AI needs to make judgment calls (not just if/then)
- AI needs to understand business context

❌ **Don't check if:**
- It's just data transformation (field A → field B)
- It's simple rules (if X then Y)

✅ **Check "Requires NLG" if:**
- AI needs to write emails, summaries, reports
- Output needs to sound natural/human

❌ **Don't check if:**
- Output is just structured data (JSON, CSV)
- Using templates with simple variable substitution

**Integration Complexity Examples:**

✅ **Check "Connects 3+ systems" if:**
- You listed 3 or more integrations in Section 5

✅ **Check "Requires API rate limit management" if:**
- Any API has rate limits noted in documentation
- Volume could exceed limits during peak

✅ **Check "Requires real-time webhooks" if:**
- Trigger is an event (not scheduled)
- Response time requirement is <5 minutes

**State Management Examples:**

✅ **Check "Multi-step coordination" if:**
- Step 2 depends on Step 1 completing
- Workflow branches based on intermediate results

❌ **Don't check if:**
- Steps run in parallel
- Single linear sequence with no dependencies

✅ **Check "Requires human approval gates" if:**
- Workflow pauses for human review mid-execution
- Human can modify and resume

**Suggested Tier Guidance:**

- **Tier 0-1:** No AI, simple automation, no rate limits
- **Tier 2-3:** AI for reasoning/NLG, orchestrates 2-5 APIs, single-pass execution
- **Tier 4-5:** Multi-agent coordination, complex state management, recursive tasks
- **Tier 6:** Autonomous decision-making over time, learning from feedback

---

### Section 7: Additional Context

**Purpose:** Capture anything that doesn't fit above but would help implementers.

**What to include:**

**Current Workarounds:**
```
BDRs currently use a shared Notion template to copy/paste research findings,
but only 40% use it consistently. The rest freestyle their notes in Salesforce,
making it hard to maintain quality standards.
```

**Related Workflows:**
```
This feeds into our existing Outreach.io cadence system. After the initial email
is approved and sent, BDRs add prospects to cadence "Inbound - High Intent" which
handles follow-ups. We should ensure the automation creates the Outreach prospect
but doesn't interfere with cadence logic.
```

**Known Edge Cases:**
```
- ZoomInfo doesn't have data for very small companies (<10 employees) or non-US companies.
  In these cases, skip enrichment and note "Manual research required" in summary.

- Some Marketo leads are duplicates (same email, different form submissions).
  Check Salesforce for existing lead before creating new intelligence summary.

- If behavior score is 0 (brand new lead, no activity), AI should note "No intent
  signals available - consider discovery call approach instead of high-intent pitch."
```

**Dependencies:**
```
- Marketo webhook integration requires IT to configure (1 week lead time)
- Salesforce custom fields need to be created (requires Salesforce admin approval)
- ZoomInfo API access needs to be provisioned (contact vendor)
```

**Nice-to-Haves:**
```
Phase 2 ideas (not required for MVP):
- Adaptive email tone based on industry/seniority (formal for finance, casual for startups)
- Auto-prioritize leads by ICP fit score (integrate with existing scoring model)
- A/B test subject lines and track open rates
- Feedback loop: BDR marks summaries as "helpful/not helpful" → improve prompts
- Integrate with LinkedIn Sales Navigator for additional enrichment
```

---

## Common Mistakes & How to Avoid Them

### Mistake 1: Combining Multiple Workflows
**Bad:** "Automate our entire lead management process"
**Good:** Submit separate forms for:
- Lead intelligence generation
- Lead routing/assignment
- Follow-up sequence selection

### Mistake 2: Vague Time Estimates
**Bad:** "This takes a long time"
**Good:** "12 minutes per lead (timed across 20 leads)"

If you don't have exact data:
- Time yourself doing it 5-10 times
- Ask the team for estimates and average them
- Note "estimated - needs validation" if unsure

### Mistake 3: Missing Integration Details
**Bad:** "Uses Salesforce"
**Good:** "Salesforce REST API v57, needs to update custom fields: Intelligence_Summary__c, Draft_Email__c, Last_Enriched_Date__c"

### Mistake 4: Forgetting Failure Scenarios
**Bad:** Only describe happy path
**Good:** "If ZoomInfo API is down, skip enrichment and notify BDR via Slack to do manual research"

### Mistake 5: No Quality Metrics
**Bad:** Only measure speed/time savings
**Good:** Include quality checks:
- Accuracy (AI summary matches manual research 90%+)
- User satisfaction (BDR rates usefulness 4/5+)
- Error rate (false positives, bad data <5%)

---

## Intake Form Checklist

Use this before submitting:

**Problem Statement:**
- [ ] Describes specific pain point (not vague)
- [ ] Quantifies business impact (numbers, not adjectives)
- [ ] Identifies who is affected and how often

**Current Manual Process:**
- [ ] Lists every step
- [ ] Names specific tools/systems
- [ ] Includes time per occurrence
- [ ] Includes frequency
- [ ] Calculates total weekly/monthly burden

**Desired Automation:**
- [ ] Trigger is specific (webhook, schedule, event)
- [ ] Data sources are named with fields/APIs
- [ ] Process steps are sequenced and detailed
- [ ] Outputs specify where data goes (system + field/format)

**Success Criteria:**
- [ ] Metrics are measurable (not "better" or "faster")
- [ ] Before/after targets are defined
- [ ] Measurement method is specified
- [ ] Includes quality checks (not just efficiency)

**Constraints:**
- [ ] All integrations listed with API details
- [ ] Cost limits defined (if applicable)
- [ ] Volume/scale requirements specified
- [ ] Compliance requirements documented
- [ ] Human approval gates noted

**Complexity Signals:**
- [ ] Checkboxes reflect actual requirements
- [ ] Explanations provided for checked items
- [ ] Suggested tier reasoning is clear

**Additional Context:**
- [ ] Edge cases documented
- [ ] Dependencies noted
- [ ] Related workflows identified

---

## Example: Complete Filled-Out Form

See `/intake_system/intake_examples/bdr_lead_intelligence_example.md` for a fully completed intake form based on the BDR lead intelligence workflow.

---

## Getting Help

**Before Submitting:**
- Review this guide thoroughly
- Check example submissions in `/intake_system/intake_examples/`
- Validate time estimates with your team
- Confirm all integrations/tools with IT/systems team

**Questions During Submission:**
- Slack: #automation-requests
- Email: automation-intake@yourcompany.com
- Office Hours: Tuesdays 2-3pm (book via Calendly link)

**After Submission:**
- You'll receive confirmation within 1 business day
- Tier assignment within 2 business days
- Implementation timeline estimate within 3 business days
- We may schedule a 30-minute clarification call if needed
