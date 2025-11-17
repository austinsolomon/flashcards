# GTM - Tier 0 - Lead Capture via iOS Shortcut

**What It Does**: Captures a quick voice note about a prospect and sends it to a shared list for follow-up. This is a simple, one-action trigger with no automation logic or context awareness.

**Tier Characteristics**:
- **Direct trigger**: Single voice input triggers single action
- **No context processing**: Records information exactly as spoken, no interpretation
- **One action**: Immediate append to list with no conditional logic or multi-step workflow
- **No automation intelligence**: User still needs to manually review and process the leads later

---

## Setup Steps

1. **Open iOS Shortcuts app** on your iPhone
2. **Create new Shortcut** and name it "Quick Lead Capture"
3. **Add actions** as detailed below
4. **Add to Home Screen or Share Sheet** for quick access
5. **Configure your leads list location** (Notes app, Reminders, or cloud storage)

---

## Shortcut Actions

### Action 1: Dictate Text
- **Type**: Dictate Text
- **Configuration**:
  - Prompt: "Tell me about the lead..."
  - Language: English (or your preference)
  - Stop listening: After Pause
- **Purpose**: Capture voice input about the prospect
- **Example Input**: "Sarah Johnson, VP of Sales at TechCorp, interested in our enterprise plan, met at conference booth"

### Action 2: Get Current Date
- **Type**: Date
- **Configuration**:
  - Date: Current Date
  - Format: Medium (e.g., Nov 17, 2025, 3:45 PM)
- **Purpose**: Add timestamp to the lead entry for context

### Action 3: Combine Text
- **Type**: Text
- **Configuration**: Combine the following:
  ```
  [Current Date]
  Lead: [Dictated Text]
  ---
  ```
- **Purpose**: Format the lead entry with timestamp

### Action 4: Append to Note
- **Type**: Append to Note (or Append to Reminder/File)
- **Configuration**:
  - Note: "Sales Leads Inbox"
  - Location: iCloud Notes (or your preferred location)
  - Show Compose Sheet: NO (for faster capture)
- **Purpose**: Store the lead in a centralized list for later processing

### Action 5: Show Notification
- **Type**: Show Notification
- **Configuration**:
  - Title: "Lead Captured"
  - Body: "Added to Sales Leads Inbox"
- **Purpose**: Confirm the lead was saved

---

## Example Usage

### **Input** (Voice):
> "Sarah Johnson, VP of Sales at TechCorp, they have 500 employees, currently using our competitor, interested in our enterprise plan with custom integrations, met at conference booth 247"

### **Output** (Appended to "Sales Leads Inbox" note):
```
Nov 17, 2025, 3:45 PM
Lead: Sarah Johnson, VP of Sales at TechCorp, they have 500 employees, currently using our competitor, interested in our enterprise plan with custom integrations, met at conference booth 247
---
```

### **Notification**:
- Title: "Lead Captured"
- Body: "Added to Sales Leads Inbox"

---

## Why This Is Tier 0

This shortcut demonstrates **Tier 0** characteristics:

1. **Simple Trigger**: Voice input → immediate action
2. **No Decision Making**: No if/then logic, no routing, no AI interpretation
3. **No Context Awareness**: Doesn't know what a "good lead" is or how to prioritize
4. **No Multi-Step Workflow**: Just capture → timestamp → append
5. **Manual Follow-Up Required**: User must later review the list and take action

**Contrast with Higher Tiers**:
- **Tier 1** would automatically parse the lead and create a CRM entry
- **Tier 2** would use LLM to extract structured fields (name, company, pain points)
- **Tier 3** would research the company and enrich the lead automatically

---

## Testing Checklist

- [ ] Shortcut captures voice input correctly
- [ ] Timestamp is added to each entry
- [ ] Lead is appended to the designated note/list
- [ ] Notification confirms capture
- [ ] Multiple captures in succession work without overwriting
- [ ] Works from Home Screen widget
- [ ] Works from Share Sheet (if configured)

---

## Variations & Extensions

### **Variation 1**: Use Reminders Instead of Notes
- Replace "Append to Note" with "Add to Reminder"
- Benefit: Can set reminders for follow-up

### **Variation 2**: Add Quick Tags
- Add a "Choose from Menu" action to let user tag urgency (Hot/Warm/Cold)
- Still Tier 0 because it's manual selection, not intelligent routing

### **Variation 3**: Send to Team Slack Channel
- Replace note append with "Send Message" to Slack
- Benefit: Immediate team visibility

---

## Common Issues & Solutions

**Issue**: Dictation stops too early
- **Solution**: In Dictate Text settings, adjust "Stop Listening" timing

**Issue**: Note not found
- **Solution**: Manually create "Sales Leads Inbox" note in iCloud Notes first

**Issue**: No notification appears
- **Solution**: Check Shortcuts notification permissions in iOS Settings

---

## Next Steps: Moving to Tier 1

To upgrade this to **Tier 1** (deterministic workflow), you could:
1. Connect to an n8n workflow that parses the note
2. Automatically create CRM entries from the captured leads
3. Send daily digest emails of new leads
4. Archive processed leads to a separate list

See `tier_1_toy_n8n_gtm_daily_metrics.json` for workflow automation patterns.
