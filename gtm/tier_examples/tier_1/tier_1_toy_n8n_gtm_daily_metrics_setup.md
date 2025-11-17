# GTM - Tier 1 - Daily Sales Metrics Email (n8n)

**What It Does**: Every weekday at 8am, automatically fetches calendar meetings and CRM pipeline data, formats them into a digest email, and sends to the sales team. This is a deterministic workflow with no AI or decision-making.

**Tier Characteristics**:
- **Scheduled trigger**: Runs at predictable time (8am weekdays), not event-based
- **Deterministic steps**: Same sequence of API calls every execution
- **No AI/LLM**: Uses templates and simple calculations only
- **No conditional logic**: Same workflow path every time (no if/then branching)
- **Multi-step workflow**: Fetches data → processes → formats → sends

---

## Workflow Overview

```
┌─────────────────────────────┐
│  Schedule: 8am Mon-Fri      │ ← TIER 1: Time-based trigger
└──────────┬──────────────────┘
           │
           ├──────────┬───────────────┐
           │          │               │
           v          v               v
    ┌──────────┐  ┌──────────┐       │
    │ Fetch    │  │ Fetch    │       │
    │ Meetings │  │ Pipeline │       │
    └────┬─────┘  └────┬─────┘       │
         │             │              │
         v             v              │
    ┌──────────┐  ┌──────────┐       │
    │ Count    │  │ Extract  │       │ TIER 1: Deterministic
    │ Meetings │  │ Metrics  │       │ processing - no AI
    └────┬─────┘  └────┬─────┘       │
         │             │              │
         └──────┬──────┘              │
                v                     │
         ┌─────────────┐              │
         │ Merge Data  │              │
         └──────┬──────┘              │
                v                     │
         ┌─────────────┐              │
         │Format Email │ ← TIER 1: Template-based
         └──────┬──────┘
                v
         ┌─────────────┐
         │ Send Email  │
         └──────┬──────┘
                v
         ┌─────────────┐
         │ Log Result  │
         └─────────────┘
```

---

## Node Configuration

### **Node 1: Schedule Trigger**
- **Type**: Schedule Trigger
- **Configuration**:
  - Cron Expression: `0 8 * * 1-5` (8am weekdays)
  - Timezone: Your local timezone
- **Input**: None (time-based)
- **Output**: Execution timestamp
- **Tier 1 Characteristic**: Predictable, scheduled trigger (not event-based)

### **Node 2: Fetch Today's Meetings**
- **Type**: HTTP Request
- **Configuration**:
  - Method: GET
  - URL: `{{$env.CALENDAR_API_URL}}` (your calendar API endpoint)
  - Authentication: HTTP Header Auth
  - Query Parameters:
    - `start_date`: `{{$today}}`
    - `end_date`: `{{$today}}`
- **Input**: Trigger timestamp
- **Output**: Array of meeting objects
- **Example Output**:
  ```json
  [
    {"id": "1", "title": "Client Demo", "type": "client", "time": "10:00"},
    {"id": "2", "title": "Team Standup", "type": "internal", "time": "9:00"},
    {"id": "3", "title": "Sales Call", "type": "client", "time": "14:00"}
  ]
  ```
- **Tier 1 Characteristic**: Same API call every day, no dynamic query generation

### **Node 3: Count Meetings**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  const meetings = $input.all();
  const totalMeetings = meetings.length;
  const clientMeetings = meetings.filter(m => m.json.type === 'client').length;
  const internalMeetings = totalMeetings - clientMeetings;

  return [{
    json: {
      totalMeetings,
      clientMeetings,
      internalMeetings,
      date: new Date().toISOString().split('T')[0]
    }
  }];
  ```
- **Input**: Meeting array
- **Output**: Meeting counts
- **Example Output**:
  ```json
  {
    "totalMeetings": 3,
    "clientMeetings": 2,
    "internalMeetings": 1,
    "date": "2025-11-17"
  }
  ```
- **Tier 1 Characteristic**: Simple counting and filtering - no AI, no decision-making

### **Node 4: Fetch Pipeline Value**
- **Type**: HTTP Request
- **Configuration**:
  - Method: GET
  - URL: `{{$env.CRM_API_URL}}/pipeline/value`
  - Authentication: HTTP Header Auth
- **Input**: Trigger timestamp
- **Output**: Pipeline data object
- **Example Output**:
  ```json
  {
    "total_value": 450000,
    "deal_count": 12,
    "average_deal_size": 37500
  }
  ```
- **Tier 1 Characteristic**: Deterministic CRM query, same endpoint every time

### **Node 5: Extract Pipeline Metrics**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  const pipelineData = $input.first().json;

  return [{
    json: {
      totalValue: pipelineData.total_value || 0,
      dealsInPipeline: pipelineData.deal_count || 0,
      avgDealSize: pipelineData.average_deal_size || 0
    }
  }];
  ```
- **Input**: Raw pipeline data
- **Output**: Formatted metrics
- **Tier 1 Characteristic**: Simple data extraction and default handling, no analysis

### **Node 6: Merge Data**
- **Type**: Aggregate
- **Configuration**:
  - Operation: Aggregate all item data
  - Include: All fields
- **Input**: Meeting counts + pipeline metrics
- **Output**: Combined data object
- **Tier 1 Characteristic**: Deterministic merge operation

### **Node 7: Format Email**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  const meetingData = $('Count Meetings').first().json;
  const pipelineData = $('Extract Pipeline Metrics').first().json;

  const emailBody = `
  Good morning!

  Here are your daily sales metrics for ${meetingData.date}:

  📅 MEETINGS TODAY:
  - Total: ${meetingData.totalMeetings}
  - Client Meetings: ${meetingData.clientMeetings}
  - Internal: ${meetingData.internalMeetings}

  💰 PIPELINE STATUS:
  - Total Pipeline Value: $${pipelineData.totalValue.toLocaleString()}
  - Active Deals: ${pipelineData.dealsInPipeline}
  - Average Deal Size: $${pipelineData.avgDealSize.toLocaleString()}

  ---
  This is an automated report. Reply to this email if you need details.
  `;

  return [{
    json: {
      subject: `Daily Sales Metrics - ${meetingData.date}`,
      body: emailBody,
      to: process.env.RECIPIENT_EMAIL || 'sales@company.com'
    }
  }];
  ```
- **Input**: Merged data
- **Output**: Formatted email object
- **Example Output**:
  ```json
  {
    "subject": "Daily Sales Metrics - 2025-11-17",
    "body": "Good morning!\n\nHere are your daily sales metrics...",
    "to": "sales@company.com"
  }
  ```
- **Tier 1 Characteristic**: Template-based email generation - same structure every time, no AI writing

### **Node 8: Send Email**
- **Type**: Email Send
- **Configuration**:
  - From: `{{$env.FROM_EMAIL}}`
  - To: `{{$json.to}}`
  - Subject: `{{$json.subject}}`
  - Message: `{{$json.body}}`
  - Email Type: Text
- **Input**: Email object
- **Output**: Send confirmation
- **Tier 1 Characteristic**: Final delivery action

### **Node 9: Log Completion**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  const result = {
    timestamp: new Date().toISOString(),
    workflow: 'daily_sales_metrics',
    status: 'completed',
    emailSent: true
  };

  console.log('Daily metrics workflow completed:', result);
  return [{ json: result }];
  ```
- **Input**: Send confirmation
- **Output**: Log entry
- **Tier 1 Characteristic**: Simple logging for observability

---

## Setup Instructions

### **1. Import Workflow to n8n**

1. Open your n8n instance
2. Click **Workflows** → **Import from File**
3. Select `tier_1_toy_n8n_gtm_daily_metrics.json`
4. Workflow will be imported with all nodes configured

### **2. Configure Environment Variables**

Add these to your n8n instance (Settings → Environment Variables) or `.env` file:

```bash
# Calendar API (Google Calendar, Outlook, etc.)
CALENDAR_API_URL=https://your-calendar-api.com/events

# CRM API (HubSpot, Salesforce, Pipedrive, etc.)
CRM_API_URL=https://your-crm-api.com

# Email Configuration
FROM_EMAIL=automations@yourcompany.com
RECIPIENT_EMAIL=sales@yourcompany.com
```

### **3. Set Up Credentials**

**For Calendar API**:
- Navigate to **Credentials** in n8n
- Add new **HTTP Header Auth** credential
- Header Name: `Authorization`
- Header Value: `Bearer YOUR_CALENDAR_API_KEY`

**For CRM API**:
- Add another **HTTP Header Auth** credential
- Header Name: `Authorization`
- Header Value: `Bearer YOUR_CRM_API_KEY`

**For Email**:
- Add **SMTP** credential
- Host: Your SMTP server (e.g., `smtp.gmail.com`)
- Port: 587 (or your SMTP port)
- Username: Your email
- Password: Your email password or app-specific password

### **4. Configure Schedule**

1. Open **Schedule Trigger** node
2. Verify cron expression: `0 8 * * 1-5` (8am Mon-Fri)
3. Adjust timezone if needed
4. Enable the workflow

### **5. Test the Workflow**

**Manual Test**:
1. Click **Execute Workflow** button in n8n editor
2. Watch each node execute sequentially
3. Verify email is received

**Check Execution Log**:
1. View execution history
2. Inspect data flowing through each node
3. Verify correct counts and calculations

---

## Example Data Flow

### **Input** (Trigger at 8:00am):
```
Timestamp: 2025-11-17 08:00:00
```

### **Node 2 Output** (Fetch Meetings):
```json
[
  {"id": "1", "title": "Client Demo - Acme Corp", "type": "client", "time": "10:00"},
  {"id": "2", "title": "Team Standup", "type": "internal", "time": "9:00"},
  {"id": "3", "title": "Sales Call - TechStart", "type": "client", "time": "14:00"},
  {"id": "4", "title": "Product Planning", "type": "internal", "time": "16:00"}
]
```

### **Node 3 Output** (Count Meetings):
```json
{
  "totalMeetings": 4,
  "clientMeetings": 2,
  "internalMeetings": 2,
  "date": "2025-11-17"
}
```

### **Node 4 Output** (Fetch Pipeline):
```json
{
  "total_value": 850000,
  "deal_count": 18,
  "average_deal_size": 47222
}
```

### **Node 7 Output** (Formatted Email):
```json
{
  "subject": "Daily Sales Metrics - 2025-11-17",
  "body": "Good morning!\n\nHere are your daily sales metrics for 2025-11-17:\n\n📅 MEETINGS TODAY:\n- Total: 4\n- Client Meetings: 2\n- Internal: 2\n\n💰 PIPELINE STATUS:\n- Total Pipeline Value: $850,000\n- Active Deals: 18\n- Average Deal Size: $47,222\n\n---\nThis is an automated report...",
  "to": "sales@company.com"
}
```

### **Final Output** (Email Received):
```
To: sales@company.com
Subject: Daily Sales Metrics - 2025-11-17

Good morning!

Here are your daily sales metrics for 2025-11-17:

📅 MEETINGS TODAY:
- Total: 4
- Client Meetings: 2
- Internal: 2

💰 PIPELINE STATUS:
- Total Pipeline Value: $850,000
- Active Deals: 18
- Average Deal Size: $47,222

---
This is an automated report. Reply to this email if you need details.
```

---

## Why This Is Tier 1

This workflow demonstrates **Tier 1** characteristics:

1. **Scheduled Automation**: Runs at fixed time, not event-triggered
2. **Deterministic Logic**: Same steps every execution - fetch → count → format → send
3. **No AI/LLM**: Uses templates, simple math, and string formatting only
4. **No Decision-Making**: No if/then branching, no intelligent routing
5. **Multi-Step Workflow**: Coordinates multiple API calls and data processing
6. **Predictable Output**: Email format and content structure never changes

**Contrast with Other Tiers**:
- **Tier 0**: Would require manual triggering and data entry
- **Tier 2**: Would use LLM to analyze metrics and generate insights (e.g., "Pipeline is down 15% from last week - consider these actions...")
- **Tier 3**: Would have an agent that proactively researches why metrics changed
- **Tier 4**: Would have multiple agents (one for data analysis, one for recommendations, one for forecasting)

---

## Troubleshooting

### **Issue**: Workflow doesn't trigger at 8am
- **Solution**: Check workflow is enabled (toggle in top-right)
- **Solution**: Verify cron expression and timezone settings
- **Solution**: Check n8n instance is running continuously

### **Issue**: API calls fail
- **Solution**: Verify API credentials are correct
- **Solution**: Check API endpoint URLs in environment variables
- **Solution**: Test API endpoints manually with Postman/curl

### **Issue**: Email not sending
- **Solution**: Verify SMTP credentials
- **Solution**: Check firewall/security settings for SMTP port
- **Solution**: Try different SMTP provider (Gmail, SendGrid, etc.)

### **Issue**: Meeting count is always 0
- **Solution**: Verify calendar API is returning data
- **Solution**: Check date format matches API expectations
- **Solution**: Inspect node output to see actual API response

---

## Customization Ideas (Still Tier 1)

### **Add More Metrics**:
- Fetch deal win rate
- Count emails sent/received
- Track tasks completed
- All still deterministic calculations

### **Multiple Recipients**:
- Send to different team members
- Format personalized sections per recipient
- Still template-based, no AI personalization

### **Weekly Summary**:
- Change schedule to Monday 8am
- Aggregate metrics from past week
- Still deterministic aggregation

### **Conditional Alerts** (Borderline Tier 2):
- If pipeline drops below threshold, send alert
- Adds simple if/then logic but no AI
- Could be considered Tier 1.5

---

## Next Steps: Moving to Tier 2

To upgrade this to **Tier 2** (context-aware workflow), you could:
1. Add Claude API call to analyze metrics
2. Generate natural language insights: "Pipeline is up 20% from last week, driven by 3 large enterprise deals"
3. Provide recommendations: "Consider focusing on Acme Corp deal - highest value and closing soon"
4. Personalize email tone based on metrics (celebratory if good, action-oriented if concerning)

See `tier_2_toy_n8n_gtm_email_classifier.json` for LLM-powered workflow patterns.
