# BR2 - Tier 1 - Daily Review Note Creator (n8n)

**What It Does**: Every evening at 6pm, automatically creates a daily review note in your Obsidian vault with a consistent template (wins, learnings, tomorrow's focus) and sends a reminder. This is a deterministic workflow with no AI or personalization.

**Tier Characteristics**:
- **Scheduled trigger**: Runs at same time every day (6pm)
- **Template-based**: Same note structure every day, no dynamic customization
- **No AI/LLM**: Uses fixed templates and date formatting only
- **Deterministic workflow**: Same steps every execution
- **Simple automation**: Create → write → notify

---

## Workflow Overview

```
┌──────────────────────────────┐
│  Schedule: 6pm Daily         │ ← TIER 1: Time-based trigger
└──────────┬───────────────────┘
           │
           v
    ┌─────────────────┐
    │ Generate Date   │ ← TIER 1: Simple date formatting
    │ Info            │
    └────────┬────────┘
             │
             v
    ┌─────────────────┐
    │ Create Note     │ ← TIER 1: Fixed template
    │ Template        │    (same structure every day)
    └────────┬────────┘
             │
             v
    ┌─────────────────┐
    │ Write to        │ ← TIER 1: Deterministic file write
    │ Obsidian        │
    └────────┬────────┘
             │
             v
    ┌─────────────────┐
    │ Send Reminder   │ ← TIER 1: Template-based email
    │ Email/Push      │
    └────────┬────────┘
             │
             v
    ┌─────────────────┐
    │ Log Completion  │
    └─────────────────┘
```

---

## Node Configuration

### **Node 1: Schedule Trigger**
- **Type**: Schedule Trigger
- **Configuration**:
  - Cron Expression: `0 18 * * *` (6pm every day)
  - Timezone: Your local timezone
- **Input**: None
- **Output**: Execution timestamp
- **Tier 1 Characteristic**: Runs automatically at consistent time

### **Node 2: Generate Date Info**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  const now = new Date();
  const dateString = now.toISOString().split('T')[0]; // YYYY-MM-DD
  const dayName = now.toLocaleDateString('en-US', { weekday: 'long' });
  const formattedDate = now.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  return [{
    json: {
      dateString,      // 2025-11-17
      dayName,         // Sunday
      formattedDate,   // November 17, 2025
      timestamp: now.toISOString()
    }
  }];
  ```
- **Input**: Trigger timestamp
- **Output**: Formatted date strings
- **Example Output**:
  ```json
  {
    "dateString": "2025-11-17",
    "dayName": "Sunday",
    "formattedDate": "November 17, 2025",
    "timestamp": "2025-11-17T18:00:05.000Z"
  }
  ```
- **Tier 1 Characteristic**: Simple date formatting, no AI

### **Node 3: Create Note Template**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  const { dateString, dayName, formattedDate } = $input.first().json;

  const noteContent = `---
  date: ${dateString}
  type: daily_review
  status: pending
  created: ${new Date().toISOString()}
  ---

  # Daily Review - ${formattedDate} (${dayName})

  ## 🎯 Wins Today
  -
  -
  -

  ## 📚 Key Learnings
  -
  -
  -

  ## 💡 Ideas Captured
  -
  -
  -

  ## 🔄 Reflections
  - What went well:
  - What could improve:
  - Energy level (1-10):

  ## 📋 Tomorrow's Focus
  - [ ]
  - [ ]
  - [ ]

  ## 🔗 Related
  - [[${dateString} Daily Note]]
  - [[Weekly Review]]

  ---
  *Created automatically by daily review workflow*
  `;

  return [{
    json: {
      content: noteContent,
      filename: `${dateString}_review.md`,
      dateString
    }
  }];
  ```
- **Input**: Date info
- **Output**: Note content and filename
- **Example Output**:
  ```json
  {
    "content": "---\ndate: 2025-11-17\ntype: daily_review...",
    "filename": "2025-11-17_review.md",
    "dateString": "2025-11-17"
  }
  ```
- **Tier 1 Characteristic**: Fixed template - same sections every day, user fills in manually

### **Node 4: Write Note to Obsidian**
- **Type**: Read/Write File
- **Configuration**:
  - Operation: Write
  - File Path: `{{$env.OBSIDIAN_VAULT_PATH}}/01_Daily_Reviews/{{$json.filename}}`
  - Data: `{{$json.content}}`
  - Encoding: UTF-8
- **Input**: Note content
- **Output**: File write confirmation
- **Example**: Creates `/home/user/Obsidian/MyVault/01_Daily_Reviews/2025-11-17_review.md`
- **Tier 1 Characteristic**: Deterministic file write to predictable location

### **Alternative Node 4B: Obsidian Local REST API**
- **Type**: HTTP Request
- **Configuration**:
  - Method: POST
  - URL: `{{$env.OBSIDIAN_LOCAL_API}}/vault/append`
  - Body:
    ```json
    {
      "file": "{{$json.filename}}",
      "data": "{{$json.content}}"
    }
    ```
- **Purpose**: Alternative method using Obsidian Local REST API plugin
- **Benefit**: Works if Obsidian vault is on different machine or mobile device

### **Node 5: Send Reminder Email**
- **Type**: Email Send
- **Configuration**:
  - From: `{{$env.FROM_EMAIL}}`
  - To: `{{$env.USER_EMAIL}}`
  - Subject: `⏰ Daily Review Ready - {{$json.dateString}}`
  - Message:
    ```
    Your daily review note has been created!

    📝 File: {{$json.filename}}
    📂 Location: 01_Daily_Reviews/

    Take 10 minutes to reflect on your day:
    - What wins did you achieve?
    - What did you learn?
    - What's your focus for tomorrow?

    Open Obsidian to complete your review.

    ---
    Automated reminder from your Second Brain system
    ```
- **Input**: Note info
- **Output**: Email sent confirmation
- **Tier 1 Characteristic**: Template-based reminder, same message structure every day

### **Alternative Node 5B: Push Notification**
- **Type**: Pushover (or similar push notification service)
- **Configuration**:
  - Title: `📝 Daily Review Ready`
  - Message: `Your review note for {{$json.dateString}} has been created...`
  - Sound: Default
- **Purpose**: Alternative notification via mobile push (iOS/Android)
- **Benefit**: Immediate notification on phone

### **Node 6: Log Completion**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  const logEntry = {
    timestamp: new Date().toISOString(),
    workflow: 'daily_review_creator',
    status: 'completed',
    noteCreated: $json.filename,
    location: '01_Daily_Reviews/'
  };

  console.log('Daily review note created:', logEntry);

  const fs = require('fs');
  const logPath = process.env.BR2_LOG_PATH || '/var/log/br2_automation.log';
  fs.appendFileSync(logPath, JSON.stringify(logEntry) + '\n');

  return [{ json: logEntry }];
  ```
- **Input**: Note creation confirmation
- **Output**: Log entry
- **Tier 1 Characteristic**: Simple logging for tracking

---

## Setup Instructions

### **1. Import Workflow**

1. Open n8n instance
2. Import `tier_1_toy_n8n_br2_daily_review.json`
3. Workflow loads with all nodes

### **2. Configure Environment Variables**

```bash
# Obsidian Vault Path (file system)
OBSIDIAN_VAULT_PATH=/home/user/Obsidian/MyVault

# OR Obsidian Local REST API (if using API method)
OBSIDIAN_LOCAL_API=http://localhost:27123

# Email Configuration
FROM_EMAIL=automations@yourcompany.com
USER_EMAIL=you@yourcompany.com

# Log Path
BR2_LOG_PATH=/var/log/br2_automation.log
```

### **3. Create Daily Reviews Folder in Obsidian**

```bash
mkdir -p "$OBSIDIAN_VAULT_PATH/01_Daily_Reviews"
```

Or manually create folder in Obsidian: `01_Daily_Reviews/`

### **4. Set Up Email Credentials** (if using email)

- Add **SMTP** credential in n8n
- Host: Your SMTP server (e.g., `smtp.gmail.com`)
- Port: 587
- Username: Your email
- Password: App-specific password

### **5. Optional: Install Obsidian Local REST API Plugin**

If you want to use the API method instead of direct file write:

1. Open Obsidian Settings → Community Plugins
2. Browse and install **Local REST API**
3. Enable the plugin
4. Note the API URL (default: `http://localhost:27123`)
5. Copy API key if authentication is enabled

### **6. Test Workflow**

**Manual Test**:
1. Click **Execute Workflow** in n8n
2. Watch nodes execute
3. Open Obsidian and check `01_Daily_Reviews/` folder
4. Verify note was created with today's date
5. Check your email for reminder

**Verify Note Content**:
```markdown
---
date: 2025-11-17
type: daily_review
status: pending
created: 2025-11-17T18:00:10.000Z
---

# Daily Review - November 17, 2025 (Sunday)

## 🎯 Wins Today
-
-
-

## 📚 Key Learnings
-
-
-

...
```

### **7. Enable Workflow**

1. Toggle workflow to **Active**
2. Will run automatically at 6pm every day

---

## Example Data Flow

### **Input** (6pm trigger):
```
Timestamp: 2025-11-17 18:00:00
```

### **Node 2 Output** (Date Info):
```json
{
  "dateString": "2025-11-17",
  "dayName": "Sunday",
  "formattedDate": "November 17, 2025",
  "timestamp": "2025-11-17T18:00:05.000Z"
}
```

### **Node 3 Output** (Template):
```json
{
  "content": "---\ndate: 2025-11-17\ntype: daily_review\nstatus: pending\ncreated: 2025-11-17T18:00:10.000Z\n---\n\n# Daily Review - November 17, 2025 (Sunday)\n\n## 🎯 Wins Today...",
  "filename": "2025-11-17_review.md",
  "dateString": "2025-11-17"
}
```

### **Node 4 Output** (File Write):
```
File created: /home/user/Obsidian/MyVault/01_Daily_Reviews/2025-11-17_review.md
```

### **Node 5 Output** (Email):
```
Email sent to: you@yourcompany.com
Subject: ⏰ Daily Review Ready - 2025-11-17
```

### **Final Result** (Obsidian Note):
```markdown
---
date: 2025-11-17
type: daily_review
status: pending
created: 2025-11-17T18:00:10.000Z
---

# Daily Review - November 17, 2025 (Sunday)

## 🎯 Wins Today
-
-
-

## 📚 Key Learnings
-
-
-

## 💡 Ideas Captured
-
-
-

## 🔄 Reflections
- What went well:
- What could improve:
- Energy level (1-10):

## 📋 Tomorrow's Focus
- [ ]
- [ ]
- [ ]

## 🔗 Related
- [[2025-11-17 Daily Note]]
- [[Weekly Review]]

---
*Created automatically by daily review workflow*
```

---

## Why This Is Tier 1

This workflow demonstrates **Tier 1** characteristics:

1. **Scheduled Automation**: Runs at same time every day, no manual triggering
2. **Template-Based**: Fixed structure, same sections every day
3. **No AI/LLM**: Uses date formatting and string templates only
4. **No Personalization**: Doesn't analyze past reviews or customize sections
5. **Deterministic**: Same workflow path every execution
6. **User Still Does the Work**: Automation creates structure, user fills in content

**Contrast with Other Tiers**:
- **Tier 0**: Would require manual note creation each day
- **Tier 2**: Would use LLM to pre-populate sections based on calendar events, emails, captures
- **Tier 3**: Would have agent review past captures and suggest wins/learnings
- **Tier 4**: Would have agents for summarizing day, extracting insights, and suggesting tomorrow's focus

---

## Troubleshooting

**Issue**: Note not appearing in Obsidian
- **Solution**: Verify `OBSIDIAN_VAULT_PATH` is correct
- **Solution**: Check folder permissions (n8n needs write access)
- **Solution**: Manually create `01_Daily_Reviews/` folder first

**Issue**: Duplicate notes created
- **Solution**: Workflow creates new note each day (by design)
- **Solution**: If duplicate on same day, check workflow isn't running multiple times

**Issue**: Email not received
- **Solution**: Check SMTP credentials
- **Solution**: Verify email address is correct
- **Solution**: Check spam folder

**Issue**: Note format broken in Obsidian
- **Solution**: Ensure frontmatter has `---` delimiters
- **Solution**: Check no extra backticks or special characters

---

## Customization (Still Tier 1)

### **Different Template Sections**:
Modify the `noteContent` in Node 3 to match your review style:
```markdown
## 🔥 Top 3 Priorities Completed
## 🚧 Challenges Faced
## 🎉 Gratitude
## 💪 Tomorrow's Top 3
```

### **Weekly Review Instead of Daily**:
Change cron to Friday 6pm: `0 18 * * 5`
Adjust template to weekly structure

### **Monthly Review**:
Change cron to first day of month: `0 18 1 * *`

### **Multiple Time Zones**:
If traveling, adjust cron timezone dynamically (still Tier 1 logic)

### **Include Daily Stats** (borderline Tier 2):
Fetch task completion count from task manager
Add to template: `Tasks Completed: {{$json.taskCount}}`
Still deterministic if just fetching a number

---

## Next Steps: Moving to Tier 2

To upgrade to **Tier 2** (context-aware), you could:
1. Fetch today's calendar events
2. Use Claude API to summarize meetings and activities
3. Pre-populate "Wins" based on completed tasks
4. Pre-populate "Learnings" from inbox captures or reading notes
5. Suggest "Tomorrow's Focus" based on calendar and priorities

Example Tier 2 enhancement:
```
## 🎯 Wins Today (Auto-suggested)
- Completed client demo with Acme Corp (from calendar)
- Shipped v2.3 release (from GitHub commits)
- Reviewed 12 inbox captures (from automation logs)
```

See `tier_2_toy_n8n_br2_inbox_triage.json` for LLM-powered note processing.

---

## Integration with Other Workflows

### **Tier 0**: iOS Shortcut Captures
- User captures ideas throughout day with `tier_0_toy_ios_shortcuts_br2_voice_capture`
- This Tier 1 workflow creates review template at 6pm
- User manually reviews captures and fills in template

### **Future Tier 2**: Smart Population
- Tier 2 workflow reads inbox captures
- Pre-populates review sections with AI summaries
- User just edits and confirms

### **Habit Tracking**:
Add to template:
```markdown
## 📊 Habits
- [ ] Morning routine
- [ ] Exercise
- [ ] Reading
- [ ] Review inbox
```

Track completion over time with simple queries (still Tier 1 if no AI analysis).
