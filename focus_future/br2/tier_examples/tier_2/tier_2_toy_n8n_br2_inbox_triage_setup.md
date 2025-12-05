# BR2 - Tier 2 - Inbox PARA Triage (n8n + Claude)

**What It Does**: When a new email arrives in your inbox, automatically uses Claude to categorize it using the PARA method (Projects, Areas, Resources, Archives), creates an Obsidian note in the appropriate folder, optionally creates a Todoist task if actionable, and labels the email. This is a context-aware workflow with ONE AI call adding semantic PARA classification.

**Tier Characteristics**:
- **Event-based trigger**: Responds to new inbox items (not scheduled)
- **ONE LLM call**: Claude categorizes using PARA methodology - semantic understanding
- **Semantic routing**: Routes based on AI's PARA classification (not keyword rules)
- **Automated knowledge capture**: Creates notes in correct PARA folders
- **Context-aware actions**: Creates tasks only for actionable items

---

## Workflow Overview

```
┌─────────────────────────────┐
│ Gmail Trigger: New Inbox    │ ← TIER 2: Event-based trigger
└──────────┬──────────────────┘
           │
           v
    ┌─────────────┐
    │ Extract     │ ← TIER 2: Prepare email data
    │ Inbox Data  │
    └──────┬──────┘
           │
           v
    ┌──────────────────────┐
    │ Call Claude API:     │ ← TIER 2 KEY: ONE LLM call
    │ PARA Categorization  │   adds semantic PARA understanding
    └──────┬───────────────┘
           │
           v
    ┌─────────────────┐
    │ Parse PARA      │ ← TIER 2: Extract structured result
    │ Classification  │
    └──────┬──────────┘
           │
           v
    ┌──────────────────────┐
    │ Route by PARA        │ ← TIER 2: Semantic routing
    │ Category             │
    └──┬────┬────┬────┬────┘
       │    │    │    │
       v    v    v    v
    ┌───┐┌───┐┌───┐┌───┐
    │Prj││Are││Res││Arc│ ← TIER 2: Create notes in
    └─┬─┘└─┬─┘└─┬─┘└─┬─┘   correct PARA folders
      │    │    │    │
      └────┴────┴────┘
           │
           v
    ┌──────────────┐
    │ Check if     │ ← TIER 2: Conditional on AI result
    │ Actionable?  │
    └─┬──────────┬─┘
      │          │
      v          v
 ┌────────┐  ┌──────┐
 │Create  │  │Label │
 │Task    │  │Email │
 └────────┘  └──────┘
      │          │
      └────┬─────┘
           v
      ┌────────┐
      │  Log   │
      └────────┘
```

---

## Node Configuration

### **Node 1: Gmail Trigger - New Inbox Item**
- **Type**: Gmail Trigger
- **Configuration**:
  - Poll interval: Every 1 minute
  - Filters:
    - `is:unread`
    - `label:inbox`
- **Input**: None (event-driven)
- **Output**: Email object
- **Example Output**:
  ```json
  {
    "id": "18c2f1a3b4d5e6f7",
    "from": "newsletter@productivityblog.com",
    "subject": "10 Tips for Better Note-Taking with Obsidian",
    "textPlain": "Here are 10 proven techniques...",
    "snippet": "Here are 10 proven techniques to improve your...",
    "labelIds": ["INBOX", "UNREAD"]
  }
  ```
- **Tier 2 Characteristic**: Event-based trigger (responds to new emails)

### **Node 2: Extract Inbox Data**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  const item = $input.first().json;

  return [{
    json: {
      from: item.from || '',
      subject: item.subject || '',
      body: item.textPlain || item.textHtml || '',
      snippet: item.snippet || '',
      labels: item.labelIds || [],
      messageId: item.id || '',
      threadId: item.threadId || '',
      timestamp: new Date().toISOString()
    }
  }];
  ```
- **Input**: Raw Gmail object
- **Output**: Cleaned email data
- **Tier 2 Characteristic**: Preprocessing before AI call

### **Node 3: Call Claude API - PARA Categorization**
- **Type**: HTTP Request
- **Configuration**:
  - Method: POST
  - URL: `https://api.anthropic.com/v1/messages`
  - Authentication: HTTP Header Auth
    - Header: `x-api-key`
    - Value: `{{$env.ANTHROPIC_API_KEY}}`
  - Body (JSON):
  ```json
  {
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 300,
    "messages": [
      {
        "role": "user",
        "content": "Analyze this inbox item and categorize it using the PARA method (Projects, Areas, Resources, Archives). Also determine if it's actionable. Respond with ONLY a JSON object:\n\n{\"category\": \"PROJECT|AREA|RESOURCE|ARCHIVE\", \"subcategory\": \"specific topic\", \"is_actionable\": true|false, \"priority\": \"HIGH|MEDIUM|LOW\", \"suggested_action\": \"brief action\" }\n\nFrom: {{ from }}\nSubject: {{ subject }}\nContent: {{ snippet }}\n\nPARA Classification:"
      }
    ]
  }
  ```
- **Input**: Email data
- **Output**: Claude PARA classification
- **Example Output**:
  ```json
  {
    "content": [
      {
        "type": "text",
        "text": "{\"category\": \"RESOURCE\", \"subcategory\": \"productivity-tools\", \"is_actionable\": false, \"priority\": \"LOW\", \"suggested_action\": \"Read and extract key note-taking tips\"}"
      }
    ]
  }
  ```
- **Tier 2 Characteristic**: ONE LLM call adds semantic PARA understanding - this is the key tier-defining element

### **Node 4: Parse PARA Classification**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  const claudeResponse = $input.first().json;
  const classificationText = claudeResponse.content[0].text.trim();

  let classification;
  try {
    classification = JSON.parse(classificationText);
  } catch (err) {
    classification = {
      category: 'RESOURCE',
      subcategory: 'uncategorized',
      is_actionable: false,
      priority: 'LOW',
      suggested_action: 'Review manually'
    };
  }

  // Validate category
  const validCategories = ['PROJECT', 'AREA', 'RESOURCE', 'ARCHIVE'];
  if (!validCategories.includes(classification.category)) {
    classification.category = 'RESOURCE';
  }

  const inboxData = $('Extract Inbox Data').first().json;

  return [{
    json: {
      ...inboxData,
      para: {
        category: classification.category,
        subcategory: classification.subcategory || 'general',
        is_actionable: classification.is_actionable || false,
        priority: classification.priority || 'MEDIUM',
        suggested_action: classification.suggested_action || ''
      },
      classifiedAt: new Date().toISOString()
    }
  }];
  ```
- **Input**: Claude response
- **Output**: Email + PARA data
- **Tier 2 Characteristic**: Extract structured data from AI

### **Node 5: Route by PARA Category**
- **Type**: Switch
- **Configuration**:
  - Route 0: `{{$json.para.category}} equals PROJECT`
  - Route 1: `{{$json.para.category}} equals AREA`
  - Route 2: `{{$json.para.category}} equals RESOURCE`
  - Route 3: `{{$json.para.category}} equals ARCHIVE`
- **Input**: Classified email
- **Output**: Routes to appropriate note creator
- **Tier 2 Characteristic**: Semantic routing based on AI's PARA classification

### **Nodes 6A-D: Create PARA Notes**

Each route creates a note in the appropriate Obsidian folder:

**Node 6A: Create Project Note**
- **Type**: HTTP Request (Obsidian API)
- **URL**: `{{$env.OBSIDIAN_API_URL}}/notes/projects`
- **Body**:
  ```json
  {
    "title": "{{subject}}",
    "content": "# {{subject}}\n\n**From:** {{from}}\n**Date:** {{timestamp}}\n**Priority:** {{priority}}\n\n## Action\n{{suggested_action}}\n\n## Original Content\n{{body}}",
    "folder": "Projects/{{subcategory}}",
    "tags": ["inbox", "project", "{{subcategory}}"]
  }
  ```
- **Tier 2 Characteristic**: Context-aware note creation with AI-suggested action

**Similar configurations for**:
- **Node 6B**: Create Area Note (Areas/{{subcategory}})
- **Node 6C**: Create Resource Note (Resources/{{subcategory}})
- **Node 6D**: Create Archive Note (Archives/{{year}})

### **Node 7: Check if Actionable**
- **Type**: IF (Conditional)
- **Configuration**:
  - Condition: `{{$json.para.is_actionable}} equals true`
- **Input**: PARA classified email
- **Output**: Routes to task creation OR directly to labeling
- **Tier 2 Characteristic**: Conditional routing based on AI determination

### **Node 8: Create Task in Todoist**
- **Type**: HTTP Request (Todoist API)
- **Configuration**:
  - Method: POST
  - URL: `{{$env.TODOIST_API_URL}}/tasks`
  - Body:
  ```json
  {
    "content": "{{suggested_action}}",
    "description": "From: {{from}}\nSubject: {{subject}}",
    "priority": {{priority === 'HIGH' ? 4 : (priority === 'MEDIUM' ? 3 : 2)}},
    "labels": ["inbox-triage", "{{category}}"]
  }
  ```
- **Input**: Actionable email data
- **Output**: Task created confirmation
- **Example Task Created**:
  ```
  Task: "Read and extract key note-taking tips"
  Priority: Low (2)
  Labels: inbox-triage, resource
  Description: From: newsletter@productivityblog.com
              Subject: 10 Tips for Better Note-Taking
  ```
- **Tier 2 Characteristic**: Creates task with AI-generated action

### **Node 9: Label Email as Processed**
- **Type**: Gmail (Add Labels)
- **Configuration**:
  - Message ID: `{{messageId}}`
  - Labels: `['PROCESSED', '{{category}}']`
- **Input**: Email data
- **Output**: Email labeled
- **Tier 2 Characteristic**: Mark email with PARA category

### **Node 10: Log PARA Classification**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  const inboxData = $input.first().json;
  const para = $('Parse PARA Classification').first().json.para;

  const logEntry = {
    timestamp: new Date().toISOString(),
    workflow: 'br2_inbox_triage',
    messageId: inboxData.messageId,
    from: inboxData.from,
    subject: inboxData.subject,
    para_category: para.category,
    subcategory: para.subcategory,
    is_actionable: para.is_actionable,
    priority: para.priority,
    task_created: para.is_actionable
  };

  console.log('Inbox item triaged:', logEntry);

  const fs = require('fs');
  const logPath = process.env.BR2_LOG_PATH || '/tmp/br2_triage.log';
  try {
    fs.appendFileSync(logPath, JSON.stringify(logEntry) + '\n');
  } catch (err) {
    console.error('Failed to write log:', err);
  }

  return [{ json: logEntry }];
  ```
- **Input**: Processed email data
- **Output**: Log entry
- **Tier 2 Characteristic**: Track AI categorizations for PARA analytics

---

## Setup Instructions

### **1. Import Workflow to n8n**

1. Open your n8n instance
2. Click **Workflows** → **Import from File**
3. Select `tier_2_toy_n8n_br2_inbox_triage.json`
4. Workflow will be imported with all nodes

### **2. Configure Environment Variables**

```bash
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Obsidian Local REST API
OBSIDIAN_API_URL=http://localhost:27123

# Todoist API
TODOIST_API_URL=https://api.todoist.com/rest/v2

# Logging (optional)
BR2_LOG_PATH=/var/log/br2_triage.log
```

### **3. Set Up Obsidian Local REST API**

1. Install **Local REST API** plugin in Obsidian
2. Enable the plugin in Settings → Community Plugins
3. Configure API port (default: 27123)
4. Generate API key in plugin settings
5. Create PARA folder structure:
   ```
   vault/
   ├── Projects/
   ├── Areas/
   ├── Resources/
   └── Archives/
   ```

### **4. Set Up Todoist API**

1. Go to Todoist Settings → Integrations
2. Copy your API token
3. Add to n8n HTTP Header Auth credential:
   - Header: `Authorization`
   - Value: `Bearer YOUR_TODOIST_TOKEN`

### **5. Configure Gmail Credentials**

1. Add Gmail OAuth2 credential in n8n
2. Follow OAuth flow to authorize
3. Ensure permissions include:
   - Read emails
   - Modify labels

### **6. Enable the Workflow**

1. Verify all credentials are connected
2. Toggle workflow to **Active**
3. n8n will now monitor Gmail inbox

### **7. Test the Workflow**

**Send a Test Email**:
1. Email yourself: "Research best practices for daily notes in Obsidian"
2. Watch n8n execution log
3. Verify:
   - Claude classifies as RESOURCE
   - Note created in Resources/productivity-tools/
   - Email labeled with RESOURCE

**Test Actionable Item**:
1. Email: "Schedule team meeting to discuss Q4 planning"
2. Verify:
   - Classified as PROJECT (actionable)
   - Note created in Projects/
   - Task created in Todoist
   - Email labeled

---

## Example Data Flow

### **Input** (New Email):
```
From: mentor@company.com
Subject: Project kickoff - New client onboarding
Body: Hi! We need to start the new client onboarding project. Can you create a timeline and assign tasks by Friday?
```

### **Node 3 Output** (Claude Classification):
```json
{
  "content": [
    {
      "text": "{\"category\": \"PROJECT\", \"subcategory\": \"client-onboarding\", \"is_actionable\": true, \"priority\": \"HIGH\", \"suggested_action\": \"Create timeline and assign tasks for client onboarding by Friday\"}"
    }
  ]
}
```

### **Node 6A Output** (Project Note Created):
```markdown
# Project kickoff - New client onboarding

**From:** mentor@company.com
**Date:** 2025-11-17T15:30:00Z
**Priority:** HIGH

## Action
Create timeline and assign tasks for client onboarding by Friday

## Original Content
Hi! We need to start the new client onboarding project...
```
**File Location**: `Projects/client-onboarding/Project kickoff - New client onboarding.md`

### **Node 8 Output** (Task Created):
```
Todoist Task:
- Content: "Create timeline and assign tasks for client onboarding by Friday"
- Priority: 4 (HIGH)
- Labels: inbox-triage, project
```

### **Final State**:
- Email labeled: PROCESSED, PROJECT
- Obsidian note: Projects/client-onboarding/...
- Todoist task: Created with HIGH priority
- Log entry: Recorded classification

---

## Why This Is Tier 2

This workflow demonstrates **Tier 2** characteristics:

1. **Event-Based**: Triggers on new emails (not scheduled)
2. **ONE LLM Call**: Claude adds semantic PARA understanding
3. **Semantic Routing**: Routes based on meaning (not keyword rules)
4. **Context-Aware**: Creates notes in correct folders, tasks only if actionable
5. **Deterministic Actions**: Pre-defined note templates and task creation

**Contrast with Other Tiers**:
- **Tier 1**: Would use keyword matching ("if subject contains 'project' then...")
- **Tier 3**: Would use LangChain agent with tools to search existing notes, find related projects
- **Tier 4**: Would have ResearchAgent → SynthesisAgent (research context, then create comprehensive note)
- **Tier 5**: Would orchestrate human review and cross-reference with calendar/CRM
- **Tier 6**: Would autonomously learn your PARA preferences and improve over time

---

## Troubleshooting

### **Issue**: Workflow doesn't trigger
- **Solution**: Verify workflow is active
- **Solution**: Check Gmail OAuth credentials
- **Solution**: Ensure emails are labeled "inbox"

### **Issue**: Claude API fails
- **Solution**: Verify `ANTHROPIC_API_KEY`
- **Solution**: Check API credits
- **Solution**: Review prompt format

### **Issue**: Obsidian notes not created
- **Solution**: Verify Local REST API plugin is running
- **Solution**: Check API URL (http://localhost:27123)
- **Solution**: Ensure PARA folders exist in vault

### **Issue**: Wrong PARA categorization
- **Solution**: Improve Claude prompt with examples
- **Solution**: Add domain-specific context
- **Solution**: Review and log classifications for patterns

### **Issue**: Todoist tasks not created
- **Solution**: Verify Todoist API token
- **Solution**: Check task priority mapping
- **Solution**: Test API endpoint manually

---

## Customization Ideas (Still Tier 2)

### **Enhanced PARA Logic**:
- Add sub-categories automatically
- Link related notes
- Track project lifecycles

### **Better Action Detection**:
- Improve actionability prompt
- Add deadline extraction
- Parse action verbs

### **Multi-Vault Support**:
- Route to different Obsidian vaults
- Separate work/personal PARA systems
- Sync across devices

### **Analytics Dashboard**:
- Track PARA distribution
- Identify busy categories
- Optimize subcategories

---

## Next Steps: Moving to Tier 3

To upgrade this to **Tier 3** (LangChain agent), you could:
1. Add tools: `search_obsidian`, `find_related_notes`, `check_project_status`
2. Let agent research existing notes before categorizing
3. Agent decides if item should link to existing projects
4. Generate contextual note content based on research

See `tier_3_toy_langchain_br2_note_connector.py` for agent patterns.
