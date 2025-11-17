# GTM - Tier 0: Simple Triggers - Quick Lead Capture

## Use Case
Instantly capture lead information from a business card, networking event, or conversation and send it directly to your CRM without opening any apps or filling forms.

## Tool Used
iOS Shortcuts

## Shortcut Configuration

### Shortcut Name
"Capture Lead"

### Actions

1. **Ask for Input** (Text)
   - Prompt: "Lead Name"
   - Store result in: `leadName`

2. **Ask for Input** (Text)
   - Prompt: "Company"
   - Store result in: `company`

3. **Ask for Input** (Email)
   - Prompt: "Email Address"
   - Store result in: `email`

4. **Ask for Input** (Choose from Menu)
   - Prompt: "Lead Source"
   - Menu Items: "Conference", "LinkedIn", "Referral", "Cold Outreach", "Website"
   - Store result in: `source`

5. **Ask for Input** (Text)
   - Prompt: "Quick Notes (optional)"
   - Default: ""
   - Store result in: `notes`

6. **Text Block** - Format data as JSON
   ```
   {
     "name": [leadName],
     "company": [company],
     "email": [email],
     "source": [source],
     "notes": [notes],
     "captured_date": [Current Date],
     "captured_time": [Current Time]
   }
   ```
   - Store result in: `jsonPayload`

7. **Get Contents of URL**
   - URL: `https://your-crm-webhook.com/leads`
   - Method: POST
   - Headers:
     - Content-Type: application/json
     - Authorization: Bearer YOUR_API_KEY
   - Request Body: `jsonPayload`

8. **Show Notification**
   - Title: "Lead Captured ✓"
   - Body: "Added [leadName] from [company] to CRM"

## How to Run

1. **Setup**: Create the shortcut in iOS Shortcuts app following the actions above
2. **Configure**: Replace `https://your-crm-webhook.com/leads` with your actual CRM webhook URL
3. **Add to Home Screen** (optional): For one-tap access
4. **Invoke**:
   - Say "Hey Siri, Capture Lead" OR
   - Tap the shortcut from Shortcuts app OR
   - Add to Lock Screen widget for instant access

## Expected Output

**User Experience:**
- 5 quick prompts (10-15 seconds total)
- Visual confirmation notification
- Lead appears in CRM within seconds

**CRM Payload Example:**
```json
{
  "name": "Sarah Chen",
  "company": "TechVentures Inc",
  "email": "schen@techventures.com",
  "source": "Conference",
  "notes": "Interested in Enterprise plan, follow up next week",
  "captured_date": "2025-01-15",
  "captured_time": "14:23:00"
}
```

**CRM Result:**
- New lead record created
- Tagged with source = "Conference"
- Assigned to default lead owner
- Triggers follow-up sequence (if CRM automation configured)

## Tier Classification Reasoning

This is **Tier 0** because:
1. **Single-step trigger**: Activated with one command/tap, no conditional logic
2. **No context needed**: Doesn't query existing data or make decisions
3. **Deterministic flow**: Same 5 questions every time, no branching
4. **Direct action**: Immediate POST to webhook with structured data
5. **No orchestration**: Self-contained, doesn't chain to other automations
6. **Perfect for mobile capture**: Optimized for the moment when you meet someone and need to capture info before you forget

This sits below Tier 1 (which would involve multi-step workflows with conditional logic or scheduled execution) and focuses purely on **friction-free data capture**.
