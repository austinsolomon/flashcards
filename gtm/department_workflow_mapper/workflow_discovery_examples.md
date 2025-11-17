# Workflow Discovery - Department Examples

## Quick-Start Prompts

Copy and paste these prompts directly into Claude to generate workflow candidates:

---

### 🎯 Marketing Team

```
Apply the Workflow Discovery Framework to the MARKETING function at a B2B SaaS company.

Context:
- Team size: 12 people (content, demand gen, ops)
- Primary KPIs: MQLs, pipeline generated, campaign ROI, content output
- Key tools: Marketo, Salesforce, Google Analytics, SEMrush, WordPress, LinkedIn
- Time split: 60% execution, 40% analysis/strategy
- Top time-sinks: Campaign reporting (5hrs/week), content creation (20hrs/week), lead scoring review (3hrs/week)

Generate 10 ranked automation candidates with ROI scores and ready-to-submit intake previews.
```

---

### 💼 Sales Team (AEs)

```
Apply the Workflow Discovery Framework to the SALES (Account Executive) function at a B2B SaaS company.

Context:
- Team size: 15 AEs, average 20 active opps each
- Primary KPIs: Bookings, win rate, sales cycle length, forecast accuracy
- Key tools: Salesforce, Gong, Outreach, LinkedIn Sales Navigator, Slack
- Time split: 40% customer calls, 30% deal admin, 30% research/prep
- Top time-sinks: Deal research (2hrs/deal), proposal customization (3hrs/proposal), CRM hygiene (5hrs/week)

Generate 10 ranked automation candidates with ROI scores and ready-to-submit intake previews.
```

---

### 📞 BDR/SDR Team

```
Apply the Workflow Discovery Framework to the BDR/SDR function at a B2B SaaS company.

Context:
- Team size: 8 BDRs
- Daily volume: 30 inbound leads + 50 outbound targets per BDR
- Primary KPIs: Qualified meetings booked, response time, personalization quality
- Key tools: Salesforce, Outreach, ZoomInfo, LinkedIn, Marketo, Slack
- Time split: 50% research, 30% outreach, 20% admin
- Top time-sinks: Lead research (10min/lead), email personalization (5min/email), list building (8hrs/week)

Generate 10 ranked automation candidates with ROI scores and ready-to-submit intake previews.
```

---

### 🤝 Customer Success

```
Apply the Workflow Discovery Framework to the CUSTOMER SUCCESS function at a B2B SaaS company.

Context:
- Team size: 10 CSMs, average 40 accounts each (mix of high/low touch)
- Primary KPIs: Net retention, health score trends, QBR completion, time-to-value
- Key tools: Gainsight, Salesforce, Zendesk, Looker, Slack, Zoom
- Time split: 50% customer meetings, 25% account planning, 25% firefighting
- Top time-sinks: QBR prep (4hrs/account), health score review (6hrs/week), renewal risk analysis (3hrs/week)

Generate 10 ranked automation candidates with ROI scores and ready-to-submit intake previews.
```

---

### 📊 Revenue Operations

```
Apply the Workflow Discovery Framework to the REVENUE OPERATIONS function at a B2B SaaS company.

Context:
- Team size: 5 people (sales ops, marketing ops, systems)
- Primary KPIs: System uptime, data quality, report accuracy, process cycle time
- Key tools: Salesforce, Marketo, Tableau, Zapier, Jira, dbt
- Time split: 40% firefighting, 30% reporting, 30% process improvement
- Top time-sinks: Data quality audits (10hrs/week), ad-hoc reporting (12hrs/week), attribution reconciliation (6hrs/week)

Generate 10 ranked automation candidates with ROI scores and ready-to-submit intake previews.
```

---

### 💰 Finance/FP&A

```
Apply the Workflow Discovery Framework to the FINANCE/FP&A function at a B2B SaaS company.

Context:
- Team size: 6 people (FP&A, accounting, billing)
- Primary KPIs: Close speed, forecast accuracy, variance analysis, compliance
- Key tools: NetSuite, Salesforce, Excel/Google Sheets, Stripe, Adaptive Insights
- Time split: 50% data collection, 30% analysis, 20% reporting
- Top time-sinks: Revenue reconciliation (8hrs/month), variance analysis (12hrs/month), board deck prep (20hrs/quarter)

Generate 10 ranked automation candidates with ROI scores and ready-to-submit intake previews.
```

---

## Expected Output Structure

When you run any of these prompts, you'll get:

### Workflow Candidate #1: Auto-Generate Inbound Lead Intelligence Summary
**Priority Score:** 9.2/10

**Quick Summary:**
BDRs spend 10-15 minutes per inbound lead manually researching company info, reviewing form data, checking intent signals, and searching news before first outreach. This delays response time and reduces daily capacity from 20 to 12 qualified conversations.

**Time Burden:**
- Per occurrence: 12 minutes
- Frequency: 25 leads per day (per BDR)
- Team members affected: 8 BDRs
- **Total weekly hours:** 80 hours

**Automation Potential:**
High - involves structured data enrichment (APIs available), content synthesis (Claude strength), and has clear input/output. No complex multi-step coordination needed.

**Suggested Tier:** 2-3 (n8n workflow + Claude API)

**Ready-to-Submit Intake Preview:**

1. **PROBLEM STATEMENT**
When inbound leads come through Marketo, BDRs waste 10-15 min/lead manually researching the company, reviewing form responses, and checking intent signals before first outreach. This delays response time and reduces daily lead capacity from 20 to 12 qualified conversations.

2. **CURRENT MANUAL PROCESS**
- BDR receives Slack notification of new Marketo lead
- Opens Salesforce, copies company name
- Opens ZoomInfo, searches company, copies firmographics
- Opens Marketo, reviews behavior score and page visits
- Opens LinkedIn + Google for contact/company research
- Pastes all into Salesforce notes (unstructured)
- Drafts personalized email based on findings
- [Time: 12 min | Frequency: 25/day per BDR]

3. **DESIRED AUTOMATION**
- Input: New lead webhook from Marketo (email, company, form data, behavior score)
- Process: Enrich via ZoomInfo API → Summarize intent signals → Web search for news → Generate structured brief + draft email via Claude
- Output: Auto-populated Salesforce Intelligence Summary field + pre-drafted email + Slack notification

4. **SUCCESS CRITERIA**
- Lead research time reduced from 12min → <30sec
- BDR daily capacity increases from 12 → 20+ qualified conversations
- First response time improves from 2hrs → 15min
- Email personalization quality maintained (BDR spot-check approval)

5. **KEY INTEGRATIONS NEEDED**
Marketo, Salesforce, ZoomInfo, Slack, Outreach.io, web search API

6. **COMPLEXITY SIGNALS**
- Decision complexity: Medium (needs contextual synthesis, NLG)
- Integration complexity: Medium (5 systems, API rate limits)
- State management: Low (single-pass enrichment, no multi-step agents)

---

*(Repeat for 9 more candidates...)*

---

## ROI Ranking Table

| Rank | Workflow | Weekly Hrs Saved | Build Tier | ROI Score | Start Priority |
|------|----------|------------------|------------|-----------|----------------|
| 1 | Auto-Generate Lead Intelligence | 80 | 2-3 | 40.0 | 🟢 START FIRST |
| 2 | Automated Follow-up Sequence Selection | 48 | 3-4 | 12.0 | 🟢 START SECOND |
| 3 | Lead Enrichment Validator | 32 | 1-2 | 16.0 | 🟢 START THIRD |
| 4 | ... | ... | ... | ... | ... |

---

## How to Use This Output

1. **Review the top 3 ranked candidates**
2. **Copy the "Ready-to-Submit Intake Preview" for #1**
3. **Expand it with specific details** (team names, exact tool versions, compliance requirements)
4. **Submit through the formal intake form**
5. **Route to appropriate tier** (already suggested)
6. **Build, measure, iterate**
7. **Move to candidate #2**

This approach ensures you're always working on the highest-ROI automation opportunities first.
