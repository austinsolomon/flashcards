# GTM - Tier 1 - Lead Research Coordination Workflow

**What It Does**: Every weekday at 9am, this workflow automatically fetches target accounts from a Google Sheet, calls a Tier 3 research agent to autonomously gather prospect intelligence, stores results in your CRM, and triggers personalized email generation for qualified leads. This is a production-ready orchestration workflow that coordinates multiple tiers.

**Tier Characteristics**:
- **Scheduled trigger**: Runs daily at 9am weekdays
- **Orchestrates other tiers**: Calls Tier 3 agent, triggers Tier 2 workflow
- **Deterministic coordination**: Clear sequence of API calls and data transformations
- **Multi-system integration**: Google Sheets → Research Agent → CRM → Email Gen
- **No AI in orchestration**: The workflow itself uses no LLM, but orchestrates AI-powered tiers

---

## Complete Tier Stack Overview

This workflow is part of a **4-tier production stack** for automated lead research and outreach:

```
┌─────────────────────────────────────────────────────────────────┐
│ TIER 1: Lead Research Coordination (THIS WORKFLOW)              │
│ - Fetches target accounts from Google Sheets                    │
│ - Orchestrates research and email generation                    │
│ - Updates CRM and tracking systems                              │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├──────────> CALLS ─────────┐
             │                           │
             v                           v
┌────────────────────────┐    ┌────────────────────────┐
│ TIER 3: Research Agent │    │ TIER 2: Email Gen      │
│ Autonomous research    │    │ LLM-powered writing    │
│ Multi-tool agent       │    │ 3 subject variants     │
└────────────────────────┘    └────────┬───────────────┘
                                       │
                                       v
                              ┌────────────────────────┐
                              │ TIER 1: Email Sender   │
                              │ Scheduled sends        │
                              │ Tracking & follow-up   │
                              └────────────────────────┘
```

**Complete Data Flow**:
1. **9am Trigger** → Fetch target accounts from Google Sheets
2. **For each account** → Call Tier 3 research agent to find decision-maker
3. **Store results** → Update CRM with company info, decision-maker, pain points
4. **If qualified** → Trigger Tier 2 email generation workflow
5. **Update tracking** → Mark account as researched in Google Sheet
6. **Summary report** → Email sales team with daily research results

---

## Workflow Architecture

### Node-by-Node Flow

```
Schedule (9am Mon-Fri)
    │
    v
Fetch Target Accounts (Google Sheets)
    │
    v
Filter Accounts (needs research)
    │
    v
Process Each Account (loop)
    │
    v
Call Tier 3 Research Agent ──> [TIER 3: Autonomous research with tools]
    │
    v
Format Research Data
    │
    v
Update CRM with Research
    │
    v
Check if Ready for Outreach?
    │
    ├─> YES: Trigger Tier 2 Email Gen ──> [TIER 2: LLM email generation]
    │
    ├─> NO: Update Tracking Spreadsheet
    │
    v
Merge Paths
    │
    v
Loop Back (if more accounts)
    │
    v
Generate Summary Report
    │
    v
Send Summary Email to Sales Team
```

---

## Setup Instructions

### Prerequisites

1. **n8n Instance** (self-hosted or cloud)
2. **Google Sheets** with target account list
3. **Tier 3 Research Agent** deployed and accessible (see `tier_3_cldchoice_gtm_lead_research.py`)
4. **CRM** (HubSpot, Salesforce, or Pipedrive)
5. **Email Service** (SMTP, Gmail, or SendGrid)

### 1. Import Workflow to n8n

1. Open your n8n instance
2. Click **Workflows** → **Import from File**
3. Select `tier_1_cldchoice_gtm_lead_research.json`
4. Workflow will be imported with all nodes

### 2. Set Up Google Sheets Target List

Create a Google Sheet with this structure:

**Sheet Name**: `Targets`

| company_name | industry | target_role | status | last_research_date | notes |
|--------------|----------|-------------|--------|-------------------|-------|
| Acme Corp | Enterprise SaaS | VP of Sales | new | | High priority |
| TechStart Inc | FinTech | Head of Growth | new | | Series B funded |
| DataFlow Systems | Analytics | VP Engineering | researched | 2025-10-15 | Re-research monthly |

**Column Definitions**:
- `company_name`: Target company name (required)
- `industry`: Industry/vertical (helps research agent)
- `target_role`: Role to find (defaults to "VP of Sales")
- `status`: One of: new, researched, ready_for_outreach, contacted, completed
- `last_research_date`: Date of last research (ISO format)
- `notes`: Internal notes for sales team

**Share Settings**: Give n8n service account edit access

### 3. Configure Environment Variables

Add these to your n8n instance (Settings → Environment Variables):

```bash
# Google Sheets
GTM_LEADS_SHEET_ID=1ABC123_your_google_sheet_id_here

# Tier 3 Research Agent API
TIER3_RESEARCH_AGENT_URL=https://your-server.com/api/research
# OR if running locally: http://localhost:8000

# Tier 2 Email Generation Webhook
TIER2_EMAIL_GEN_WEBHOOK_URL=https://your-n8n-instance.com/webhook/tier2-email-gen

# Notifications
SALES_TEAM_EMAIL=sales@yourcompany.com
```

### 4. Set Up Credentials in n8n

#### Google Sheets OAuth2
1. Navigate to **Credentials** → **Create New**
2. Select **Google Sheets OAuth2 API**
3. Follow OAuth flow to authorize
4. Test connection

#### Research Agent API Key
1. **Credentials** → **Create New** → **HTTP Header Auth**
2. Header Name: `Authorization`
3. Header Value: `Bearer YOUR_RESEARCH_AGENT_API_KEY`

#### HubSpot API (or your CRM)
1. **Credentials** → **Create New** → **HubSpot API**
2. Enter HubSpot API key
3. Test connection

**Note**: Ensure your HubSpot instance has custom properties configured:
- `decision_maker_name`
- `decision_maker_title`
- `decision_maker_email`
- `company_size`
- `tech_stack`
- `pain_points`
- `buying_signals`
- `last_research_date`
- `research_status`

#### SMTP Email
1. **Credentials** → **Create New** → **SMTP**
2. Configure your email server settings
3. Test by sending a test email

### 5. Deploy Tier 3 Research Agent

Before this workflow can run, you need to deploy the Tier 3 research agent:

1. See `tier_3_cldchoice_gtm_lead_research.py` for agent code
2. Deploy as a web service (Flask, FastAPI, or serverless)
3. Ensure it exposes a `/research` endpoint that accepts:
   ```json
   {
     "company_name": "Acme Corp",
     "industry": "Enterprise SaaS",
     "target_role": "VP of Sales",
     "research_depth": "standard"
   }
   ```
4. Returns research results in this format:
   ```json
   {
     "success": true,
     "decision_maker": {
       "name": "Sarah Chen",
       "title": "VP of Sales",
       "email": "sarah.chen@acmecorp.com",
       "linkedin_url": "https://linkedin.com/in/sarachen"
     },
     "company_info": {
       "size": "200-500 employees",
       "funding": "$50M Series B",
       "tech_stack": ["Salesforce", "HubSpot", "Slack"]
     },
     "pain_points": [
       "Manual lead qualification process",
       "Disconnected sales tools"
     ],
     "buying_signals": [
       "Recently posted job for Sales Operations Manager",
       "CEO mentioned 'scaling challenges' on LinkedIn"
     ]
   }
   ```

### 6. Set Up Tier 2 Email Generation Webhook

This workflow triggers Tier 2 email generation via webhook:

1. Import `tier_2_cldchoice_gtm_lead_research.json` (separate workflow)
2. Note the webhook URL from the webhook trigger node
3. Update `TIER2_EMAIL_GEN_WEBHOOK_URL` environment variable

### 7. Configure Schedule

1. Open **Schedule Trigger** node
2. Verify cron expression: `0 9 * * 1-5` (9am Mon-Fri)
3. Adjust timezone if needed
4. Enable the workflow

---

## Testing the Workflow

### Manual Test Run

1. **Add test account** to Google Sheets:
   ```
   company_name: Test Company Inc
   industry: SaaS
   target_role: VP of Sales
   status: new
   ```

2. **Click "Execute Workflow"** in n8n editor

3. **Watch the execution**:
   - Fetches from Google Sheets ✓
   - Filters for accounts needing research ✓
   - Calls Tier 3 research agent ✓
   - Updates CRM ✓
   - Triggers email generation (if contact found) ✓
   - Sends summary email ✓

4. **Verify results**:
   - Check HubSpot: Company record should be updated
   - Check Google Sheets: Status should change
   - Check email: Summary should arrive
   - Check Tier 2 workflow: Should be triggered (if contact found)

### Dry Run with Mock Data

For testing without calling real research agent:

1. Temporarily replace "Call Tier 3 Research Agent" node with a Code node
2. Return mock research data:
   ```javascript
   return [{
     json: {
       success: true,
       decision_maker: {
         name: "Test Person",
         title: "VP of Sales",
         email: "test@testcompany.com",
         linkedin_url: "https://linkedin.com/in/testperson"
       },
       company_info: {
         size: "100-200",
         funding: "$10M Series A",
         tech_stack: ["Salesforce"]
       },
       pain_points: ["Manual processes"],
       buying_signals: ["Hiring for sales ops"]
     }
   }];
   ```

---

## Example Data Flow

### Input (Google Sheets)

```csv
company_name,industry,target_role,status,last_research_date,notes
Acme Corp,Enterprise SaaS,VP of Sales,new,,High priority - warm intro available
TechStart Inc,FinTech,Head of Growth,new,,Series B funded last month
DataFlow Systems,Analytics,VP Engineering,researched,2025-10-15,Re-research monthly
CompletedCo,Marketing Tech,CMO,completed,2025-11-01,Already contacted
```

### Processing Flow

#### Step 1: Filter Accounts
Filtered to research today:
- ✓ Acme Corp (new, never researched)
- ✓ TechStart Inc (new, never researched)
- ✓ DataFlow Systems (last research > 30 days ago)
- ✗ CompletedCo (status = completed, skip)

#### Step 2: Research Agent Call (for Acme Corp)

**Request to Tier 3**:
```json
{
  "company_name": "Acme Corp",
  "industry": "Enterprise SaaS",
  "target_role": "VP of Sales",
  "research_depth": "standard"
}
```

**Response from Tier 3**:
```json
{
  "success": true,
  "decision_maker": {
    "name": "Sarah Chen",
    "title": "VP of Sales & Revenue",
    "email": "sarah.chen@acmecorp.com",
    "linkedin_url": "https://linkedin.com/in/sarachen-sales"
  },
  "company_info": {
    "size": "200-500 employees",
    "funding": "$50M Series B (led by Sequoia)",
    "tech_stack": ["Salesforce", "HubSpot", "Outreach.io", "ZoomInfo"]
  },
  "pain_points": [
    "Manual lead qualification consuming 20+ hours/week",
    "Disconnected sales tools - data entry across 4 systems",
    "Difficulty tracking deal progress across team"
  ],
  "buying_signals": [
    "Posted job opening for 'Sales Operations Manager' 5 days ago",
    "CEO tweeted about 'scaling our go-to-market motion'",
    "Recently attended SaaStr conference",
    "Using free tier of competitor product (from tech stack analysis)"
  ]
}
```

#### Step 3: CRM Update

HubSpot company record created/updated with:
- **Decision Maker**: Sarah Chen (VP of Sales & Revenue)
- **Email**: sarah.chen@acmecorp.com
- **Company Size**: 200-500 employees
- **Tech Stack**: Salesforce, HubSpot, Outreach.io, ZoomInfo
- **Pain Points**: Manual lead qualification consuming 20+ hours/week; Disconnected sales tools...
- **Buying Signals**: Posted job for Sales Ops Manager; CEO mentioned scaling GTM...
- **Research Date**: 2025-11-17T09:05:23Z
- **Research Status**: completed
- **Ready for Outreach**: true

#### Step 4: Trigger Email Generation

**Webhook payload to Tier 2**:
```json
{
  "trigger_source": "tier1_lead_research",
  "company_id": "acme_corp",
  "company_name": "Acme Corp",
  "decision_maker_name": "Sarah Chen",
  "decision_maker_email": "sarah.chen@acmecorp.com",
  "pain_points": "Manual lead qualification consuming 20+ hours/week; Disconnected sales tools - data entry across 4 systems; Difficulty tracking deal progress across team",
  "buying_signals": "Posted job opening for Sales Operations Manager 5 days ago; CEO tweeted about scaling go-to-market motion; Recently attended SaaStr conference",
  "tech_stack": "Salesforce, HubSpot, Outreach.io, ZoomInfo"
}
```

This triggers Tier 2 workflow which will:
- Use Claude to generate personalized email
- Create 3 subject line variants
- Store draft in CRM for review

#### Step 5: Update Tracking Sheet

Google Sheets updated:
```csv
company_name,industry,target_role,status,last_research_date,notes
Acme Corp,Enterprise SaaS,VP of Sales,ready_for_outreach,2025-11-17T09:05:23Z,High priority - warm intro available
```

### Final Output (Summary Email)

**To**: sales@yourcompany.com
**Subject**: Daily Lead Research Complete - 3 accounts processed

```html
<h2>Daily Lead Research Summary</h2>
<p><strong>Date:</strong> 2025-11-17T09:15:30Z</p>
<ul>
  <li><strong>Total Processed:</strong> 3</li>
  <li><strong>Ready for Outreach:</strong> 2</li>
  <li><strong>Needs Follow-up:</strong> 1</li>
</ul>

<h3>Processed Companies:</h3>
<ul>
  <li><strong>Acme Corp</strong> - completed (DM: Sarah Chen)</li>
  <li><strong>TechStart Inc</strong> - completed (DM: James Patterson)</li>
  <li><strong>DataFlow Systems</strong> - needs_followup (DM: Not found)</li>
</ul>

<p>Check CRM for full details and next steps.</p>
```

---

## Integration Points

### 1. Google Sheets (Data Source)
- **Purpose**: Central list of target accounts
- **Access**: n8n reads and updates
- **Frequency**: Daily at 9am
- **Data Flow**: Spreadsheet → n8n → Research Agent

### 2. Tier 3 Research Agent (Autonomous Research)
- **Purpose**: Find decision-makers and gather intelligence
- **Integration**: HTTP API call
- **Timeout**: 60 seconds per research request
- **Data Flow**: n8n → Research Agent → n8n → CRM

### 3. CRM (HubSpot/Salesforce)
- **Purpose**: Store research data for sales team
- **Operation**: Upsert company records
- **Data Stored**: Decision-maker, pain points, buying signals, tech stack
- **Data Flow**: n8n → CRM (storage)

### 4. Tier 2 Email Generation (LLM-Powered Workflow)
- **Purpose**: Generate personalized outreach emails
- **Integration**: Webhook trigger
- **Triggering Condition**: Only if decision-maker email found
- **Data Flow**: n8n → Tier 2 Webhook → Email Draft in CRM

### 5. Tracking Spreadsheet (Process Management)
- **Purpose**: Track which accounts have been researched
- **Operation**: Update status and date fields
- **Data Flow**: n8n → Google Sheets (update)

---

## Why This Is Tier 1

This workflow demonstrates **Tier 1** characteristics:

1. **Scheduled Automation**: Runs daily at 9am, not event-triggered
2. **Deterministic Orchestration**: Fixed sequence of steps, predictable flow
3. **No AI in Orchestration**: The workflow itself has no LLM calls
4. **Multi-System Coordination**: Connects Google Sheets, Research Agent, CRM, Email
5. **Calls Higher Tiers**: Orchestrates Tier 3 (research agent) and Tier 2 (email gen)
6. **Simple Conditionals**: Only basic if/then logic (ready for outreach?)

**Contrast with Other Tiers**:
- **Tier 0**: Would require manual triggering and data entry for each company
- **Tier 2**: Would use LLM to decide which accounts to research or how to prioritize
- **Tier 3**: This tier orchestrates a Tier 3 agent, but isn't one itself
- **Tier 4**: Would have multiple orchestrating agents making decisions

**This is Tier 1 Orchestration**: It coordinates multiple tiers in a deterministic, scheduled workflow.

---

## Monitoring & Observability

### Execution Logs

Check n8n execution history for:
- Number of accounts processed daily
- Success rate of research agent calls
- CRM update success/failures
- Email generation trigger success

### Error Handling

The workflow handles these errors:

1. **Research Agent Timeout**: Logs error, continues to next account
2. **CRM Update Failure**: Logs error, doesn't trigger email gen
3. **No Decision-Maker Found**: Updates CRM, marks as "needs_followup"
4. **Google Sheets Access Error**: Workflow fails, admin notified

### Metrics to Track

- **Daily processed accounts**: Should be ~10 per day
- **Success rate**: % of accounts with decision-maker found
- **Email generation triggers**: How many qualified leads per day
- **Processing time**: Average time per account (target: <2 min)

---

## Troubleshooting

### Issue: Research agent call times out

**Symptoms**: "Call Tier 3 Research Agent" node fails with timeout error

**Solutions**:
1. Increase timeout in node settings (current: 60s)
2. Check research agent server status/logs
3. Reduce research_depth from "standard" to "quick"
4. Verify network connectivity to research agent

### Issue: No accounts being processed

**Symptoms**: "Filter Accounts for Research" returns 0 results

**Solutions**:
1. Check Google Sheets has accounts with status "new"
2. Verify last_research_date filter logic (30 days)
3. Check that completed/contacted accounts are excluded correctly
4. Manually trigger workflow to see filtering logic

### Issue: CRM updates failing

**Symptoms**: "Update CRM with Research Data" node fails

**Solutions**:
1. Verify HubSpot API credentials
2. Check that custom properties exist in HubSpot
3. Ensure company record can be created/updated
4. Check API rate limits

### Issue: Tier 2 email generation not triggering

**Symptoms**: Research completes but no emails generated

**Solutions**:
1. Verify `TIER2_EMAIL_GEN_WEBHOOK_URL` is correct
2. Check that decision_maker_email is populated
3. Verify Tier 2 workflow is enabled
4. Check webhook authentication/headers

### Issue: Summary email not sending

**Symptoms**: Workflow completes but no summary email

**Solutions**:
1. Check SMTP credentials
2. Verify `SALES_TEAM_EMAIL` environment variable
3. Check spam folder
4. Test SMTP connection manually

---

## Production Optimization

### Rate Limiting

To avoid overwhelming systems:

1. **Limit daily accounts**: Currently set to 10 per day (adjustable)
2. **Process sequentially**: One at a time to avoid parallel API calls
3. **Add delays**: Insert Wait nodes between accounts if needed

### Cost Optimization

1. **Research depth**: Use "quick" for initial research, "deep" for high-priority
2. **Re-research frequency**: Currently 30 days, increase to 60 for stable accounts
3. **Filter actively**: Skip accounts already contacted or completed

### Scaling

To process more accounts per day:

1. **Increase batch size**: Change from 10 to 20-50 accounts
2. **Parallel processing**: Use multiple n8n workflows for different segments
3. **Dedicated research agent**: Scale Tier 3 agent separately
4. **Queue-based**: Move to queue system (Redis, RabbitMQ) for large volumes

---

## Customization Ideas

### Add Lead Scoring

Before triggering email generation, add a scoring node:
```javascript
const score = 0;
if ($json.buying_signals.includes('job posting')) score += 30;
if ($json.company_funding.includes('Series B')) score += 20;
if ($json.company_size > 100) score += 15;

return [{ json: { ...$json, lead_score: score } }];
```

Trigger email gen only if `lead_score > 50`.

### Multi-Channel Outreach

Instead of just email, trigger:
- LinkedIn connection request (via LinkedIn API)
- Direct mail (via Lob API)
- Phone call reminder (via CRM task)

### Account-Based Marketing Integration

Send high-value accounts to marketing automation:
```javascript
if ($json.company_size > 500 || $json.company_funding.includes('Series C')) {
  // Trigger Marketo/HubSpot campaign
  // Add to LinkedIn Matched Audience
  // Alert sales leadership
}
```

### Intelligent Re-Research

Instead of fixed 30-day interval, re-research when:
- Company announces funding
- New executive joins
- Company posts relevant job openings
- Competitor mention detected

---

## Next Steps: Complete the Stack

This Tier 1 workflow is step 1 of 4. To complete the full automation stack:

### Step 2: Deploy Tier 3 Research Agent
- See `tier_3_cldchoice_gtm_lead_research.py`
- Deploy as web service
- Configure tools: web_search, linkedin_scraper, company_enrichment

### Step 3: Set Up Tier 2 Email Generation
- See `tier_2_cldchoice_gtm_lead_research.json`
- Configure Claude API for personalized email writing
- Generate 3 subject line variants per prospect
- Store drafts in CRM for review

### Step 4: Enable Tier 1 Email Sending
- See `tier_1_cldchoice_gtm_lead_research_sending.json`
- Schedule optimal send times
- Track opens/clicks
- Create follow-up reminders

---

## Security Considerations

1. **API Keys**: Store all keys in n8n credentials, never in workflow JSON
2. **Data Privacy**: Ensure research data complies with GDPR/privacy laws
3. **Access Control**: Limit who can modify this workflow
4. **Audit Log**: Track all CRM updates and email sends
5. **Data Retention**: Auto-delete research data after 90 days if not contacted

---

## Support & Resources

- **n8n Documentation**: https://docs.n8n.io
- **HubSpot API**: https://developers.hubspot.com
- **Tier 3 Agent Setup**: See `tier_3_cldchoice_gtm_lead_research_setup.md`
- **Tier 2 Email Gen**: See `tier_2_cldchoice_gtm_lead_research_setup.md`

For issues or questions, check the setup documentation for each tier in this stack.
