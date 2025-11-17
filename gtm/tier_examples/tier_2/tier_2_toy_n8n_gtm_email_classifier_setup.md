# GTM - Tier 2 - Email Intent Classifier (n8n + Claude)

**What It Does**: When a new email arrives, automatically classifies the sender's intent using Claude AI (MEETING_REQUEST, QUESTION, OBJECTION, etc.), then routes to the appropriate response template. This is a context-aware workflow with ONE AI call adding semantic understanding.

**Tier Characteristics**:
- **Event-based trigger**: Responds to new emails (not scheduled)
- **ONE LLM call**: Claude classifies email intent - adds semantic understanding
- **Semantic routing**: Routes based on AI classification (not rules)
- **Template responses**: Pre-written replies (not AI-generated responses)
- **Context-aware**: Understands email meaning, not just keywords

---

## Workflow Overview

```
┌─────────────────────────────┐
│  Gmail Trigger: New Email   │ ← TIER 2: Event-based trigger
└──────────┬──────────────────┘
           │
           v
    ┌─────────────┐
    │ Extract     │ ← TIER 2: Prepare data for AI
    │ Email Data  │
    └──────┬──────┘
           │
           v
    ┌─────────────────────┐
    │ Call Claude API:    │ ← TIER 2 KEY: ONE LLM call adds
    │ Classify Intent     │   semantic understanding
    └──────┬──────────────┘
           │
           v
    ┌─────────────────┐
    │ Parse Intent    │ ← TIER 2: Extract structured result
    │ Category        │
    └──────┬──────────┘
           │
           v
    ┌──────────────────────┐
    │ Route Based on       │ ← TIER 2: Semantic routing
    │ AI Classification    │   (vs rule-based routing)
    └──┬───────┬───────┬───┘
       │       │       │
       v       v       v
    ┌────┐ ┌────┐ ┌────┐
    │Mtg │ │Qstn│ │Obj │ ← TIER 2: Template responses
    └────┘ └────┘ └────┘   (not AI-generated)
       │       │       │
       └───────┴───────┘
               │
               v
        ┌──────────┐
        │ Log      │
        │ Result   │
        └──────────┘
```

---

## Node Configuration

### **Node 1: Gmail Trigger - New Email**
- **Type**: Gmail Trigger
- **Configuration**:
  - Poll interval: Every 1 minute
  - Filters: `is:unread`
  - Label: (optional) Specific label to monitor
- **Input**: None (event-driven)
- **Output**: Email object with full metadata
- **Example Output**:
  ```json
  {
    "id": "18c2f1a3b4d5e6f7",
    "threadId": "18c2f1a3b4d5e6f7",
    "from": "john@acmecorp.com",
    "subject": "Quick question about pricing",
    "textPlain": "Hi! I'm interested in your Enterprise plan. Could you send me pricing details for 50 users?\n\nThanks,\nJohn",
    "date": "2025-11-17T10:30:00Z"
  }
  ```
- **Tier 2 Characteristic**: Event-based trigger (responds to real-world events, not schedules)

### **Node 2: Extract Email Data**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  // TIER 2: Simple extraction - prepare data for AI call
  const email = $input.first().json;

  return [{
    json: {
      from: email.from || '',
      subject: email.subject || '',
      body: email.textPlain || email.textHtml || '',
      messageId: email.id || '',
      threadId: email.threadId || '',
      timestamp: new Date().toISOString()
    }
  }];
  ```
- **Input**: Raw email object
- **Output**: Cleaned email data
- **Tier 2 Characteristic**: Deterministic preprocessing before AI call

### **Node 3: Call Claude API - Classify Intent**
- **Type**: HTTP Request
- **Configuration**:
  - Method: POST
  - URL: `https://api.anthropic.com/v1/messages`
  - Authentication: HTTP Header Auth
    - Header: `x-api-key`
    - Value: `{{$env.ANTHROPIC_API_KEY}}`
  - Additional Headers:
    - `anthropic-version`: `2023-06-01`
    - `content-type`: `application/json`
  - Body (JSON):
  ```json
  {
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 200,
    "messages": [
      {
        "role": "user",
        "content": "Analyze this email and classify the sender's intent. Respond with ONLY ONE of these categories: MEETING_REQUEST, QUESTION, OBJECTION, PRICING_INTEREST, GENERAL_INQUIRY, SPAM\n\nFrom: {{ $json.from }}\nSubject: {{ $json.subject }}\nBody: {{ $json.body.substring(0, 500) }}\n\nIntent Category:"
      }
    ]
  }
  ```
- **Input**: Email data object
- **Output**: Claude API response
- **Example Output**:
  ```json
  {
    "id": "msg_01ABC123",
    "type": "message",
    "role": "assistant",
    "content": [
      {
        "type": "text",
        "text": "PRICING_INTEREST"
      }
    ],
    "model": "claude-sonnet-4-5-20250929",
    "usage": {
      "input_tokens": 85,
      "output_tokens": 3
    }
  }
  ```
- **Tier 2 Characteristic**: ONE LLM call adds semantic understanding - this is the key tier-defining element

### **Node 4: Parse Intent Category**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  // TIER 2: Parse AI response and extract intent category
  const claudeResponse = $input.first().json;
  const intentText = claudeResponse.content[0].text.trim();

  // Validate intent is one of expected categories
  const validIntents = [
    'MEETING_REQUEST',
    'QUESTION',
    'OBJECTION',
    'PRICING_INTEREST',
    'GENERAL_INQUIRY',
    'SPAM'
  ];

  const intent = validIntents.find(i => intentText.includes(i)) || 'GENERAL_INQUIRY';

  // Get original email data
  const emailData = $('Extract Email Data').first().json;

  return [{
    json: {
      ...emailData,
      intent,
      classifiedAt: new Date().toISOString()
    }
  }];
  ```
- **Input**: Claude API response
- **Output**: Email data + classified intent
- **Example Output**:
  ```json
  {
    "from": "john@acmecorp.com",
    "subject": "Quick question about pricing",
    "body": "Hi! I'm interested in your Enterprise plan...",
    "messageId": "18c2f1a3b4d5e6f7",
    "intent": "PRICING_INTEREST",
    "classifiedAt": "2025-11-17T10:31:05Z"
  }
  ```
- **Tier 2 Characteristic**: Extract structured data from LLM response for routing

### **Node 5: Route Based on AI Classification**
- **Type**: Switch
- **Configuration**:
  - Route 0: `{{$json.intent}} equals MEETING_REQUEST`
  - Route 1: `{{$json.intent}} equals QUESTION`
  - Route 2: `{{$json.intent}} equals OBJECTION`
  - Route 3: `{{$json.intent}} equals PRICING_INTEREST`
  - Default: All other intents
- **Input**: Classified email data
- **Output**: Routes to appropriate handler
- **Tier 2 Characteristic**: Semantic routing based on AI classification (not rule-based keyword matching)

### **Node 6A: Check Calendar Availability** (Meeting Request Path)
- **Type**: HTTP Request
- **Configuration**:
  - Method: POST
  - URL: `{{$env.CALENDAR_API_URL}}/check_availability`
  - Body:
  ```json
  {
    "requester_email": "{{$json.from}}",
    "check_next_days": 7
  }
  ```
- **Input**: Classified email
- **Output**: Available time slots
- **Example Output**:
  ```json
  {
    "availableSlots": "- Tuesday 11/19 at 2:00 PM\n- Wednesday 11/20 at 10:00 AM\n- Thursday 11/21 at 3:00 PM"
  }
  ```
- **Tier 2 Characteristic**: Context-aware action triggered by AI classification

### **Node 6B-E: Send Templated Responses**
- **Type**: Gmail (Send)
- **Configuration varies by intent**:

**For MEETING_REQUEST**:
```
To: {{$('Extract Email Data').first().json.from}}
Subject: Re: {{$('Extract Email Data').first().json.subject}}
Body:
Hi,

Thank you for your meeting request! I have availability in the next week. Here are some options:

{{ $json.availableSlots }}

Please let me know which time works best for you.

Best regards
```

**For PRICING_INTEREST**:
```
To: {{$('Extract Email Data').first().json.from}}
Subject: Re: {{$('Extract Email Data').first().json.subject}}
Body:
Hi,

Thank you for your interest in our Enterprise plan! I'd be happy to provide pricing details.

For 50 users, our Enterprise plan includes:
- Unlimited seats: $XX/user/month
- Priority support
- Advanced analytics
- Custom integrations

I'll send you a detailed quote within the next hour. Would you like to schedule a quick call to discuss your specific needs?

Best regards
```

**For QUESTION**:
```
Body: Thank you for your email. I've received your question and will get back to you within 24 hours with a detailed response.
```

**For OBJECTION**:
```
Body: I understand your concerns. Let me address them personally - I'll follow up with a detailed response that addresses your specific situation.
```

- **Tier 2 Characteristic**: Template-based responses (not AI-generated), but selected via AI routing

### **Node 7: Log Classification**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  // TIER 2: Log the classification for analytics
  const emailData = $input.first().json;

  const logEntry = {
    timestamp: new Date().toISOString(),
    workflow: 'email_intent_classifier',
    messageId: emailData.messageId,
    from: emailData.from,
    intent: emailData.intent,
    responseType: 'auto_reply'
  };

  console.log('Email classified and handled:', logEntry);

  // Optional: Write to file for analytics
  try {
    const fs = require('fs');
    const logPath = process.env.GTM_LOG_PATH || '/tmp/gtm_automation.log';
    fs.appendFileSync(logPath, JSON.stringify(logEntry) + '\n');
  } catch (err) {
    console.error('Failed to write log:', err);
  }

  return [{ json: logEntry }];
  ```
- **Input**: Classified email
- **Output**: Log entry
- **Tier 2 Characteristic**: Track AI classifications for improvement

---

## Setup Instructions

### **1. Import Workflow to n8n**

1. Open your n8n instance
2. Click **Workflows** → **Import from File**
3. Select `tier_2_toy_n8n_gtm_email_classifier.json`
4. Workflow will be imported with all nodes configured

### **2. Configure Environment Variables**

Add these to your n8n instance or `.env` file:

```bash
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Calendar API
CALENDAR_API_URL=https://your-calendar-api.com

# Logging (optional)
GTM_LOG_PATH=/var/log/gtm_automation.log
```

### **3. Set Up Credentials**

**For Gmail Trigger & Send**:
1. Navigate to **Credentials** in n8n
2. Add **Gmail OAuth2** credential
3. Follow OAuth flow to authorize n8n to access your Gmail
4. Test connection

**For Anthropic API**:
1. Add **HTTP Header Auth** credential
2. Header Name: `x-api-key`
3. Header Value: Your Anthropic API key
4. Add another header: `anthropic-version` = `2023-06-01`

**For Calendar API**:
1. Add **HTTP Header Auth** credential
2. Configure according to your calendar system (Google Calendar, Calendly, etc.)

### **4. Enable the Workflow**

1. Verify all credentials are connected
2. Toggle workflow to **Active** (top-right switch)
3. n8n will now monitor Gmail for new emails

### **5. Test the Workflow**

**Send a Test Email**:
1. Send an email to your monitored Gmail account with intent: "Can we schedule a meeting next week?"
2. Watch n8n execution log
3. Verify Claude classifies it as `MEETING_REQUEST`
4. Confirm auto-reply is sent

**Check Logs**:
1. View execution in n8n dashboard
2. Inspect each node's output
3. Verify Claude response and routing

---

## Example Data Flow

### **Input** (New Email Arrives):
```
From: prospect@company.com
Subject: Questions about your product
Body: Hi! I have a few questions about your Enterprise plan. Does it include API access? What's the onboarding process like?
```

### **Node 2 Output** (Extract Email Data):
```json
{
  "from": "prospect@company.com",
  "subject": "Questions about your product",
  "body": "Hi! I have a few questions about your Enterprise plan. Does it include API access? What's the onboarding process like?",
  "messageId": "18c2f1a3b4d5e6f7",
  "timestamp": "2025-11-17T10:30:00Z"
}
```

### **Node 3 Output** (Claude Classification):
```json
{
  "content": [
    {
      "type": "text",
      "text": "QUESTION"
    }
  ],
  "usage": {
    "input_tokens": 92,
    "output_tokens": 2
  }
}
```

### **Node 4 Output** (Parsed Intent):
```json
{
  "from": "prospect@company.com",
  "subject": "Questions about your product",
  "body": "Hi! I have a few questions...",
  "messageId": "18c2f1a3b4d5e6f7",
  "intent": "QUESTION",
  "classifiedAt": "2025-11-17T10:30:05Z"
}
```

### **Node 5** (Routing):
Routes to "Reply: Question Acknowledgment" path

### **Final Output** (Email Sent):
```
To: prospect@company.com
Subject: Re: Questions about your product

Hi,

Thank you for your email. I've received your questions and will get back to you within 24 hours with detailed answers about API access and our onboarding process.

Best regards
```

---

## Why This Is Tier 2

This workflow demonstrates **Tier 2** characteristics:

1. **Event-Based**: Triggers on new emails (not scheduled)
2. **ONE LLM Call**: Claude adds semantic understanding of intent
3. **Semantic Routing**: Routes based on meaning, not keywords
4. **Context-Aware**: Understands "Can we meet?" vs "What's your pricing?" vs "I have concerns"
5. **Deterministic Actions**: Pre-written templates (not AI-generated responses)

**Contrast with Other Tiers**:
- **Tier 1**: Would use keyword matching ("if subject contains 'meeting' then...")
- **Tier 3**: Would use a LangChain agent with tools (web search, CRM lookup) to research the sender
- **Tier 4**: Would have multiple agents (ResearchAgent finds context, WriterAgent drafts personalized response)
- **Tier 5**: Would orchestrate human handoff and multi-step qualification
- **Tier 6**: Would autonomously learn from past emails and improve classifications over time

---

## Troubleshooting

### **Issue**: Workflow doesn't trigger on new emails
- **Solution**: Verify workflow is enabled (active toggle)
- **Solution**: Check Gmail OAuth credentials are valid
- **Solution**: Test Gmail trigger manually

### **Issue**: Claude API call fails
- **Solution**: Verify `ANTHROPIC_API_KEY` is correct
- **Solution**: Check API key has sufficient credits
- **Solution**: Inspect error response from Anthropic API

### **Issue**: Wrong intent classification
- **Solution**: Review Claude's prompt - may need to add examples
- **Solution**: Check email body isn't truncated (currently 500 chars)
- **Solution**: Add more context to classification prompt

### **Issue**: Auto-reply not sending
- **Solution**: Verify Gmail OAuth has send permissions
- **Solution**: Check "From" email is authorized
- **Solution**: Test Gmail send node manually

---

## Customization Ideas (Still Tier 2)

### **Add More Intent Categories**:
- `CUSTOMER_SUPPORT`
- `REFUND_REQUEST`
- `FEATURE_REQUEST`
- Update Claude prompt and routing logic

### **Improve Classification Prompt**:
- Add few-shot examples
- Include sender domain context
- Consider email thread history

### **Add Slack Notification**:
- For high-priority intents (OBJECTION)
- Alert sales team immediately
- Still Tier 2 - no additional AI

### **Track Classification Accuracy**:
- Log all classifications
- Periodic human review
- Retrain prompt with corrections

---

## Next Steps: Moving to Tier 3

To upgrade this to **Tier 3** (LangChain agent), you could:
1. Add tools: `web_search`, `crm_lookup`, `linkedin_search`
2. Let agent research the sender before responding
3. Agent decides which tools to use based on email content
4. Generate personalized response based on research findings

See `tier_3_toy_langchain_gtm_prospect_finder.py` for agent patterns.
