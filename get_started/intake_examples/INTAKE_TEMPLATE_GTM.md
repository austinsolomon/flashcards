# AUTOMATION INTAKE REQUEST TEMPLATE
## Domain: GTM (Marketing)

**Workflow Name:** [Short, descriptive name for this automation]

---

## 1. PROBLEM STATEMENT (2-3 sentences)
[Describe the pain point this automation will solve. Include:]
- What manual work is currently slowing down your team?
- How much time is wasted per occurrence?
- What is the impact on sales velocity, lead quality, or team capacity?

**Example:**
> When inbound leads come through Marketo, BDRs waste 10-15 min/lead manually researching the company, reviewing form responses, and checking intent signals before first outreach. This delays response time and reduces daily lead capacity from 20 to 12 qualified conversations.

---

## 2. CURRENT MANUAL PROCESS (Step-by-step)
[List each step currently done manually. Be specific about tools, inputs, and decisions made.]

**Example:**
1. BDR receives Slack notification of new Marketo lead
2. Opens Salesforce, copies company name
3. Opens ZoomInfo, searches company, copies firmographics
4. Opens Marketo, reviews behavior score and page visits
5. Opens LinkedIn, searches contact + company
6. Opens Google, searches recent news
7. Pastes all into Salesforce notes field (unstructured)
8. Drafts personalized email based on findings
9. Sends via Outreach.io

**Time per occurrence:** 10-15 minutes/lead
**Frequency:** 15-30 leads/day
**Total weekly burden:** 15-30 hours across team

---

## 3. DESIRED AUTOMATION

### Input:
[What triggers the automation and what data is available?]

**Example:**
- **Trigger:** New lead created in Marketo (webhook)
- **Data Available:**
  - Lead email, company name
  - Form responses (how they found us, pain points)
  - Behavior score (page visits, content downloads)
  - Source campaign

### Process:
[Step-by-step automated workflow. Be specific about AI calls, API integrations, and decision logic.]

**Example:**
1. Enrich firmographic data (ZoomInfo API)
   - Company size, industry, revenue, tech stack
2. Summarize intent signals (Marketo activity log API)
   - Which pages visited, content downloaded
   - Engagement score trending up/down
3. Search recent company news (Perplexity API or web search)
   - Funding rounds, leadership changes, product launches
4. Generate structured lead brief (Claude API)
   - 3-5 bullet summary of company context
   - Key intent signals ("visited pricing page 3x")
   - Relevant news hooks for outreach
5. Draft personalized outreach email (Claude API)
   - Reference specific pain points from form
   - Tie to company news or intent signals
   - Include relevant case study/resource

### Output:
[What is created/updated/delivered after automation runs?]

**Example:**
- **Auto-populated Salesforce lead record** with:
  - Structured "Intelligence Summary" field (markdown formatted)
  - Enriched firmographic data fields
  - Pre-drafted email in "Next Steps" field
- **Slack notification** to assigned BDR with:
  - Lead name and company
  - 2-sentence summary
  - Priority level (based on ICP fit)
  - Link to Salesforce record
- **Outreach.io draft email** (BDR must review/approve before send)

---

## 4. SUCCESS CRITERIA
[Measurable outcomes that define success. Use metrics, percentages, or time savings.]

**Example:**
- [ ] Lead research time reduced from 10min → <30sec per lead
- [ ] BDR daily capacity increases from 12 → 20+ qualified conversations
- [ ] First response time improves from 2hrs → 15min (median)
- [ ] Email personalization quality maintained or improved (>90% BDR approval rate on AI drafts)
- [ ] Lead-to-meeting conversion rate maintained or increased (currently 8%)

---

## 5. CONSTRAINTS & REQUIREMENTS

### Must Integrate With:
[List all systems/tools that need to connect]

**Example:**
- Marketo (webhook trigger, activity log API)
- Salesforce (lead record updates, custom fields)
- ZoomInfo (firmographic enrichment, 100 req/min rate limit)
- Slack (webhook notifications to #sales-leads)
- Outreach.io (draft email creation, API v2)

### Technical Constraints:
[API limits, cost constraints, performance requirements]

**Example:**
- Claude API calls must stay <$0.50/lead (targeting $0.30/lead)
- System must handle 30-50 leads/day (burst capacity for campaign spikes)
- End-to-end processing <2 minutes per lead
- 99% uptime during business hours (9am-5pm ET)
- Must log all API calls for compliance audit

### Human-in-the-Loop Requirements:
[What needs manual review/approval?]

**Example:**
- BDR must review and approve AI-generated email before send (NO auto-send)
- BDR can edit intelligence summary if AI misses context
- Sales manager spot-checks 10% of AI summaries weekly
- Flagged leads (e.g., enterprise accounts >$1B revenue) route to senior BDR

### Compliance/Security:
[Audit logs, data retention, privacy requirements]

**Example:**
- All AI decisions must be logged for audit trail
- PII handling must comply with GDPR/CCPA
- No lead data sent to external APIs without encryption
- Retain AI-generated content for 2 years (compliance requirement)
- API keys must be rotated quarterly

---

## 6. COMPLEXITY SIGNALS (Help the router)

### Decision Complexity:
[Check all that apply - helps determine automation tier]

- [x] Needs contextual reasoning (synthesizing company research into personalized brief)
- [x] Needs natural language generation (email drafting, summary writing)
- [x] Needs multi-source data fusion (Marketo + ZoomInfo + web search + LLM synthesis)
- [ ] Requires sequential decision-making (e.g., agent decides which research steps to take)
- [ ] Needs to learn from feedback (e.g., improve summaries based on BDR edits)

### Integration Complexity:
[Check all that apply]

- [ ] 1-2 systems (Tier 0-1: simple integrations)
- [ ] 3-4 systems (Tier 2-3: moderate integrations)
- [x] 5+ systems (Tier 3-4: complex integrations)
- [x] API rate limits to manage (ZoomInfo: 100/min, Marketo: 10k/day)
- [x] Real-time webhook trigger required (Marketo → automation)
- [ ] Batch processing acceptable (scheduled runs)

### State Management:
[Check all that apply]

- [x] Stateless (each lead processed independently)
- [ ] Stateful (needs to track lead history across multiple touchpoints)
- [ ] Multi-step agent coordination (e.g., ResearchAgent → WriterAgent → EditorAgent)
- [x] Human approval loops (BDR must approve email before send)

### Suggested Tier:
[Based on complexity signals - see tier definitions]

**Tier Estimate:** 2-3 (n8n + Claude OR LangChain agent)

**Reasoning:**
- Event-based trigger (Marketo webhook) = Tier 2
- ONE LLM call combines research synthesis + email drafting = Tier 2
  - OR: TWO LLM calls (one for summary, one for email) = still Tier 2
- Multi-source enrichment (ZoomInfo, Marketo, web) = Tier 2-3
- No agent decision-making (deterministic workflow) = Tier 2
- If future: agent decides which research sources to use = Tier 3

---

## 7. NICE-TO-HAVES (Future iterations)
[Features that would be valuable but aren't required for MVP]

**Example:**
- Adaptive email tone based on industry/seniority (formal for enterprise, casual for startups)
- Auto-prioritize leads by ICP fit score (ML model trained on closed-won deals)
- A/B test subject lines and track open rates
- Feedback loop: BDR marks summaries "helpful/not helpful" → retrain prompts
- Integration with Gong/Chorus to reference past conversations with same company
- Predictive lead scoring using historical conversion data
- Auto-detect if lead is already in CRM (duplicate prevention)
- Scheduled follow-up if BDR doesn't action within 24 hours

---

## 8. ADDITIONAL CONTEXT

### Team Structure:
[Who will use this automation?]

**Example:**
- 8 BDRs (process leads daily)
- 2 Sales Development Managers (monitor quality, coach BDRs)
- 1 Sales Ops (owns Salesforce, Marketo, integrations)

### Current Pain Points:
[Specific frustrations or blockers]

**Example:**
- BDRs inconsistent in research depth (junior BDRs skip LinkedIn/news checks)
- Salesforce notes unstructured → hard to review quality
- Response time varies wildly (some leads contacted in 15min, others 6 hours)
- Email personalization drops during high lead volume days
- ZoomInfo credits wasted on manual searches (no tracking)

### Related Workflows:
[Other automations that might interact with this one]

**Example:**
- Lead scoring model (Tier 1) runs hourly to update Salesforce scores
- Email sequence automation (Tier 1) triggers follow-ups after initial send
- Weekly performance dashboard (Tier 2) aggregates BDR metrics
- Account-based marketing enrichment (Tier 3) for enterprise accounts

---

## ROUTING VALUE FOR AUTOMATION TIERS

| Intake Field | Routing Value |
|---|---|
| **Problem Statement** | Clarifies scope - one workflow, not entire sales process |
| **Current Process** | Shows manual steps → identifies automation tier |
| **Input/Output** | Defines data contracts → API feasibility check |
| **Success Criteria** | Measurable → validates tier can achieve goals |
| **Constraints** | Surfaces technical limits (API costs, compliance) |
| **Complexity Signals** | **Most important** - directly maps to tiers 0-6 |

---

## EXAMPLE: QUICK WIN WORKFLOWS FOR GTM

Use this template for common marketing/sales automation requests:

1. **Auto-summaries of inbound leads** ← Start here (Tier 2-3)
2. **Campaign analysis anomaly detection** ← Tier 3-4
3. **Content outline generator for blog posts** ← Tier 2-3
4. **Lead enrichment validator** ← Tier 1-2
5. **Lifecycle email selection agent** ← Tier 3-4
6. **Social media post scheduler** ← Tier 1-2
7. **Competitive intelligence aggregator** ← Tier 2-3

**Recommendation:** Submit #1 first using the template above. Once built, use it as a pattern for the others.
