# Law - Tier 1 - Deadline Router & Daily Digest (n8n)

## What Is Available Today

**Current Practice for Deadline Management**:
- Attorneys manually check calendar multiple times daily
- Scattered deadlines across personal calendars, Outlook, case management systems
- Morning email: "What's due this week?"
- Missed deadlines due to calendar blindspots

**Available Solutions (2025)**:
- **Calendar apps** (Google Calendar, Outlook): Manual setup of recurring reminders
- **Practice management software** (Clio, MyCase): Built-in deadline digests, but require manual data entry
- **Email filters**: Basic rules to route court notices to folders

**The Gap**: No unified system that automatically aggregates deadlines from multiple sources and delivers a daily prioritized digest. Most lawyers cobble together manual checks.

---

## How AI Could Improve It

**Current Tier 1 (Rule-Based Automation - Available Today)**:
- **Tool A**: n8n checks deadline folder every morning
- **Tool B**: Aggregates deadlines by priority and date
- **Tool C**: Sends formatted email/Slack digest
- **No AI needed** - just scheduled automation

**Future Tier 2+ (AI-Enhanced)**:
- **Tool X (Tier 2)**: Claude analyzes deadlines, identifies conflicts, suggests prioritization
- **Tool Y (Tier 3)**: LangChain agent cross-references deadlines with your availability, proposes optimal work schedule
- **Tool Z (Tier 4)**: Multi-agent system predicts workload bottlenecks, suggests delegation before you're overwhelmed
- **Experimental (Tier 6)**: System learns your work patterns, proactively blocks calendar time for complex briefs

**This Example (Tier 1)**: Basic scheduled routing and digest generation - no AI, just reliable automation.

---

**What It Does**: Every morning at 7 AM, scans deadline notes folder, categorizes by urgency, routes to appropriate channels (email, Slack), and creates a formatted daily digest.

**Tier Characteristics**:
- **Scheduled trigger**: Runs daily at 7 AM
- **No AI**: Pure rule-based logic (no LLM calls)
- **File-based routing**: Reads markdown frontmatter, routes by metadata
- **Multi-channel output**: Email + Slack notification
- **Deterministic**: Same inputs always produce same outputs

---

## Workflow Overview

```
┌──────────────────────────┐
│  Cron Trigger: 7:00 AM   │ ← TIER 1: Scheduled, not event-based
└──────────┬───────────────┘
           │
           v
    ┌─────────────────┐
    │ Read Deadline   │ ← TIER 1: File system operations
    │ Notes Folder    │
    └──────┬──────────┘
           │
           v
    ┌─────────────────┐
    │ Parse YAML      │ ← TIER 1: Extract metadata
    │ Frontmatter     │
    └──────┬──────────┘
           │
           v
    ┌─────────────────┐
    │ Filter Active   │ ← TIER 1: Rule-based filtering
    │ Deadlines       │   (due within 14 days)
    └──────┬──────────┘
           │
           v
    ┌─────────────────┐
    │ Sort by         │ ← TIER 1: Deterministic sorting
    │ Priority & Date │
    └──────┬──────────┘
           │
           v
    ┌─────────────────┐
    │ Route by        │ ← TIER 1: Rule-based routing
    │ Urgency         │
    └──┬───────┬──────┘
       │       │
       v       v
    ┌────┐ ┌──────┐
    │Email│ │Slack │ ← TIER 1: Deterministic outputs
    └────┘ └──────┘
```

---

## Node Configuration

### **Node 1: Schedule Trigger - Daily 7 AM**
- **Type**: Cron
- **Configuration**:
  - Cron Expression: `0 7 * * *` (7:00 AM daily)
  - Timezone: America/Los_Angeles (adjust for your timezone)
- **Input**: None (scheduled trigger)
- **Output**: Timestamp of execution
- **Example Output**:
  ```json
  {
    "timestamp": "2025-11-18T07:00:00-08:00"
  }
  ```
- **Tier 1 Characteristic**: Time-based trigger (no external event)

### **Node 2: Read Deadline Notes Folder**
- **Type**: Read Binary Files (or Execute Command with `find`)
- **Configuration**:
  - File Path: `/home/user/LegalNotes/Deadlines/*.md`
  - Binary Data: false (read as text)
- **Alternative**: Use Execute Command node
  ```bash
  find /home/user/LegalNotes/Deadlines -name "*.md" -type f -exec cat {} \;
  ```
- **Input**: Trigger timestamp
- **Output**: Array of file contents
- **Example Output**:
  ```json
  [
    {
      "fileName": "deadline_johnson_v_techcorp_20251215.md",
      "content": "---\ncreated: 2025-11-01 09:00:00\ntype: court_deadline\nmatter: Johnson v. TechCorp\ndeadline_date: 2025-12-15\nfiling: File opposition to MSJ\npriority: Critical\nstatus: pending\n---\n\n# ⚠️ COURT DEADLINE - 2025-12-15\n..."
    },
    {
      "fileName": "deadline_martinez_discovery_20251128.md",
      "content": "---\ncreated: 2025-10-29 14:00:00\ntype: court_deadline\nmatter: Martinez v. City\ndeadline_date: 2025-11-28\nfiling: Respond to interrogatories\npriority: High\nstatus: pending\n---\n..."
    }
  ]
  ```
- **Tier 1 Characteristic**: File system reading (no API calls, no AI)

### **Node 3: Parse YAML Frontmatter**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  // TIER 1: Parse markdown frontmatter using simple regex
  const items = $input.all();
  const parsed = [];

  for (const item of items) {
    const content = item.json.content || item.json.data?.toString() || '';

    // Extract YAML frontmatter between --- delimiters
    const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);

    if (!frontmatterMatch) {
      console.log(`No frontmatter found in ${item.json.fileName}`);
      continue;
    }

    const frontmatter = frontmatterMatch[1];
    const bodyContent = content.replace(/^---\n[\s\S]*?\n---\n/, '');

    // Parse YAML (simple key: value pairs)
    const metadata = {};
    frontmatter.split('\n').forEach(line => {
      const match = line.match(/^(\w+):\s*(.+)$/);
      if (match) {
        metadata[match[1]] = match[2];
      }
    });

    // Extract deadline date and calculate days until
    const deadlineDate = new Date(metadata.deadline_date);
    const today = new Date();
    const daysUntil = Math.ceil((deadlineDate - today) / (1000 * 60 * 60 * 24));

    parsed.push({
      json: {
        fileName: item.json.fileName,
        matter: metadata.matter || 'Unknown Matter',
        filing: metadata.filing || 'Unknown Filing',
        deadlineDate: metadata.deadline_date,
        priority: metadata.priority || 'Normal',
        status: metadata.status || 'pending',
        daysUntil: daysUntil,
        bodyContent: bodyContent.trim()
      }
    });
  }

  return parsed;
  ```
- **Input**: File contents array
- **Output**: Structured deadline objects
- **Example Output**:
  ```json
  [
    {
      "fileName": "deadline_johnson_v_techcorp_20251215.md",
      "matter": "Johnson v. TechCorp",
      "filing": "File opposition to MSJ",
      "deadlineDate": "2025-12-15",
      "priority": "Critical",
      "status": "pending",
      "daysUntil": 27,
      "bodyContent": "# ⚠️ COURT DEADLINE - 2025-12-15\n..."
    },
    {
      "fileName": "deadline_martinez_discovery_20251128.md",
      "matter": "Martinez v. City",
      "filing": "Respond to interrogatories",
      "deadlineDate": "2025-11-28",
      "priority": "High",
      "status": "pending",
      "daysUntil": 10
    }
  ]
  ```
- **Tier 1 Characteristic**: Deterministic parsing (no AI interpretation)

### **Node 4: Filter Active Deadlines**
- **Type**: Filter (or Code)
- **Configuration**:
  - Condition 1: `status` equals `pending` (not completed)
  - Condition 2: `daysUntil` greater than or equal to `0` (not past)
  - Condition 3: `daysUntil` less than or equal to `14` (within 2 weeks)
- **Alternative Code**:
  ```javascript
  // TIER 1: Simple filtering logic
  const deadlines = $input.all();
  const active = deadlines.filter(d => {
    return d.json.status === 'pending' &&
           d.json.daysUntil >= 0 &&
           d.json.daysUntil <= 14;
  });

  return active;
  ```
- **Input**: All parsed deadlines
- **Output**: Only active deadlines within next 14 days
- **Tier 1 Characteristic**: Rule-based filtering (no AI prioritization)

### **Node 5: Sort by Priority & Date**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  // TIER 1: Deterministic sorting
  const deadlines = $input.all();

  // Priority weights
  const priorityWeight = {
    'Critical': 3,
    'High': 2,
    'Normal': 1
  };

  // Sort: Priority descending, then daysUntil ascending (soonest first)
  deadlines.sort((a, b) => {
    const aPriority = priorityWeight[a.json.priority] || 1;
    const bPriority = priorityWeight[b.json.priority] || 1;

    if (aPriority !== bPriority) {
      return bPriority - aPriority; // Higher priority first
    }

    return a.json.daysUntil - b.json.daysUntil; // Sooner deadlines first
  });

  return deadlines;
  ```
- **Input**: Filtered deadlines
- **Output**: Sorted deadlines (Critical first, then by date)
- **Example Output**:
  ```json
  [
    {
      "matter": "Johnson v. TechCorp",
      "filing": "File opposition to MSJ",
      "deadlineDate": "2025-12-15",
      "priority": "Critical",
      "daysUntil": 27
    },
    {
      "matter": "Martinez v. City",
      "filing": "Respond to interrogatories",
      "deadlineDate": "2025-11-28",
      "priority": "High",
      "daysUntil": 10
    },
    {
      "matter": "Smith v. Jones",
      "filing": "File status report",
      "deadlineDate": "2025-11-25",
      "priority": "Normal",
      "daysUntil": 7
    }
  ]
  ```
- **Tier 1 Characteristic**: Algorithmic sorting (no AI-based prioritization)

### **Node 6: Generate Email Digest**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  // TIER 1: Template-based email generation (no AI)
  const deadlines = $input.all();
  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  // Group by urgency
  const critical = deadlines.filter(d => d.json.priority === 'Critical');
  const high = deadlines.filter(d => d.json.priority === 'High');
  const normal = deadlines.filter(d => d.json.priority === 'Normal');

  // Format deadline list
  function formatDeadlines(list) {
    return list.map(d => {
      const daysText = d.json.daysUntil === 0 ? '⚠️ TODAY' :
                       d.json.daysUntil === 1 ? '⚠️ TOMORROW' :
                       `in ${d.json.daysUntil} days`;
      return `  • ${d.json.filing} (${d.json.matter}) - Due ${daysText} (${d.json.deadlineDate})`;
    }).join('\n');
  }

  // Build email body
  let emailBody = `📅 DEADLINE DIGEST - ${today}\n\n`;
  emailBody += `You have ${deadlines.length} upcoming deadline(s) in the next 14 days.\n\n`;

  if (critical.length > 0) {
    emailBody += `🚨 CRITICAL PRIORITY (${critical.length}):\n`;
    emailBody += formatDeadlines(critical) + '\n\n';
  }

  if (high.length > 0) {
    emailBody += `⚠️ HIGH PRIORITY (${high.length}):\n`;
    emailBody += formatDeadlines(high) + '\n\n';
  }

  if (normal.length > 0) {
    emailBody += `📋 NORMAL PRIORITY (${normal.length}):\n`;
    emailBody += formatDeadlines(normal) + '\n\n';
  }

  if (deadlines.length === 0) {
    emailBody = `📅 DEADLINE DIGEST - ${today}\n\n✅ No upcoming deadlines in the next 14 days. Enjoy your day!`;
  }

  emailBody += `\n---\nGenerated automatically by n8n Legal Automation`;

  return [{
    json: {
      subject: `📅 Deadline Digest - ${deadlines.length} upcoming`,
      body: emailBody,
      to: process.env.ATTORNEY_EMAIL || 'attorney@lawfirm.com'
    }
  }];
  ```
- **Input**: Sorted deadlines
- **Output**: Formatted email content
- **Example Output**:
  ```json
  {
    "subject": "📅 Deadline Digest - 3 upcoming",
    "body": "📅 DEADLINE DIGEST - Monday, November 18, 2025\n\nYou have 3 upcoming deadline(s) in the next 14 days.\n\n🚨 CRITICAL PRIORITY (1):\n  • File opposition to MSJ (Johnson v. TechCorp) - Due in 27 days (2025-12-15)\n\n⚠️ HIGH PRIORITY (1):\n  • Respond to interrogatories (Martinez v. City) - Due in 10 days (2025-11-28)\n\n📋 NORMAL PRIORITY (1):\n  • File status report (Smith v. Jones) - Due in 7 days (2025-11-25)\n\n---\nGenerated automatically by n8n Legal Automation",
    "to": "attorney@lawfirm.com"
  }
  ```
- **Tier 1 Characteristic**: Template-based formatting (no AI content generation)

### **Node 7: Send Email**
- **Type**: Send Email (or Gmail)
- **Configuration**:
  - From: `no-reply@lawfirm.com`
  - To: `{{$json.to}}`
  - Subject: `{{$json.subject}}`
  - Body: `{{$json.body}}`
  - Format: Plain text
- **Input**: Email content object
- **Output**: Success confirmation
- **Tier 1 Characteristic**: Direct delivery (no AI analysis of content)

### **Node 8: Send Slack Alert** (Parallel Branch)
- **Type**: Slack (Send Message)
- **Configuration**:
  - Channel: `#legal-deadlines`
  - Message: Same as email body
  - Optional: Add emoji reactions based on urgency
    - Critical: 🚨
    - High: ⚠️
    - Normal: 📋
- **Input**: Email content object
- **Output**: Slack message ID
- **Tier 1 Characteristic**: Multi-channel broadcasting (no AI channel selection)

---

## Setup Instructions

### **1. Import Workflow to n8n**

1. Open your n8n instance
2. Click **Workflows** → **Import from File**
3. Select `tier_1_toy_n8n_law_deadline_router.json`
4. Workflow will be imported with all nodes configured

### **2. Configure Environment Variables**

Add these to your n8n instance or `.env` file:

```bash
# Email settings
ATTORNEY_EMAIL=your.email@lawfirm.com

# Legal notes path
LEGAL_NOTES_PATH=/home/user/LegalNotes/Deadlines

# Slack webhook (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### **3. Set Up Credentials**

**For Email Send Node**:
1. Navigate to **Credentials** in n8n
2. Add **SMTP** credential
3. Configure with your email server settings
4. Test connection

**For Slack Node** (optional):
1. Add **Slack API** credential
2. Create Slack app at api.slack.com
3. Add Bot Token Scopes: `chat:write`, `channels:read`
4. Install app to workspace
5. Copy Bot User OAuth Token to n8n
6. Test connection

### **4. Test with Sample Data**

Create sample deadline files in `/home/user/LegalNotes/Deadlines/`:

**test_deadline_1.md**:
```markdown
---
created: 2025-11-01 09:00:00
type: court_deadline
matter: Test Case v. Sample Corp
deadline_date: 2025-11-25
filing: File test motion
priority: Critical
status: pending
---

# Test Deadline

This is a test deadline.
```

**test_deadline_2.md**:
```markdown
---
created: 2025-11-05 14:00:00
type: court_deadline
matter: Another Matter
deadline_date: 2025-11-28
filing: Respond to discovery
priority: High
status: pending
---

# Another Test
```

### **5. Enable the Workflow**

1. Verify all credentials are connected
2. Toggle workflow to **Active** (top-right switch)
3. n8n will now run daily at 7:00 AM

### **6. Test the Workflow Manually**

1. Click **Execute Workflow** in n8n dashboard
2. Watch execution log
3. Verify email received
4. Check Slack message (if configured)

---

## Why This Is Tier 1

This workflow demonstrates **Tier 1** characteristics:

1. **Scheduled**: Runs on cron schedule (not event-driven)
2. **No AI**: Pure rule-based logic (no LLM calls)
3. **File-Based**: Reads from filesystem (no API integrations)
4. **Deterministic**: Same inputs always produce same outputs
5. **Template-Based**: Email content from templates (not AI-generated)

**Contrast with Other Tiers**:
- **Tier 0**: Manual capture with iOS Shortcuts (no automation)
- **Tier 1** ←: Scheduled routing and digest (rule-based)
- **Tier 2**: Would add Claude to analyze deadlines and suggest priority changes
- **Tier 3**: LangChain agent would cross-reference calendar, suggest optimal work schedule
- **Tier 4**: Multi-agent system would predict workload, propose delegation
- **Tier 5**: Human reviews AI-generated work plan before auto-blocking calendar
- **Tier 6**: System autonomously learns from missed deadlines and adjusts lead times

---

## Customization Ideas (Still Tier 1)

### **Add Weekend Exclusion**:
In Filter node, exclude deadlines falling on Saturday/Sunday:
```javascript
const deadlineDate = new Date(d.json.deadlineDate);
const dayOfWeek = deadlineDate.getDay();
return dayOfWeek !== 0 && dayOfWeek !== 6; // Exclude Sun (0) and Sat (6)
```

### **Add Matter-Specific Routing**:
Route certain high-stakes cases to specific partners:
```javascript
if (d.json.matter.includes('Johnson v. TechCorp')) {
  d.json.assignedAttorney = 'senior.partner@lawfirm.com';
}
```

### **Add Weekly Summary**:
Duplicate workflow, change cron to `0 7 * * 1` (Mondays only), extend filter to 30 days.

### **Add Completed Deadline Archival**:
After sending digest, move files with `status: completed` to archive folder:
```javascript
// In Code node after email send
const fs = require('fs');
const completedFiles = deadlines.filter(d => d.json.status === 'completed');
completedFiles.forEach(file => {
  const oldPath = `/home/user/LegalNotes/Deadlines/${file.json.fileName}`;
  const newPath = `/home/user/LegalNotes/Archive/${file.json.fileName}`;
  fs.renameSync(oldPath, newPath);
});
```

---

## Next Steps: Moving to Tier 2

To upgrade this to **Tier 2** (AI-enhanced), you could:
1. Add Claude API call to analyze deadline descriptions
2. Extract implicit deadlines: "Motion hearing is Dec 10" → Create deadline for opposition brief (due 5 days before)
3. Suggest priority: Claude reads case importance, adjusts priority
4. Identify conflicts: "You have 3 critical deadlines in the same week - consider delegation"

See `tier_2_cldchoice_law_deadline_analyzer.json` for AI-enhanced deadline intelligence.

---

## Legal Tech Context (2025)

**Why Tier 1 Matters**:
- **Trust**: Lawyers trust rule-based systems more than AI (no hallucination risk)
- **Ethics**: No confidentiality concerns (all processing is local/firm-controlled)
- **Cost**: $0 incremental cost (no AI API fees)
- **Reliability**: Deterministic behavior, easy to debug

**When to Add AI (Tier 2+)**:
- High deadline volume (100+ cases): AI can identify patterns humans miss
- Complex court rule variations: AI can apply jurisdiction-specific rules
- Cross-matter conflicts: AI can spot scheduling issues across entire firm
- Predictive workload: AI learns time requirements for different motion types

**Current Adoption (2025)**:
- 30% of law firms use basic automation (Tier 1)
- 5% use AI-enhanced systems (Tier 2-3)
- <1% use autonomous systems (Tier 5-6)
- Main barrier: Ethics uncertainty and liability concerns
