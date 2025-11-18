# Law - Tier 0 - Court Filing & Deadline Tracker (iOS Shortcuts)

## What Is Available Today

**Manual Deadline Tracking (Standard Practice)**:
- Receive court order via email or PACER
- Manually calculate filing deadlines (accounting for court rules on counting days)
- Manually enter into calendar
- Set reminders 7 days, 3 days, 1 day before deadline
- Hope you didn't miscalculate or miss a holiday

**Commercial Solutions**:
- **CompuLaw** ($50-100/month/user): Automated deadline calculation based on court rules
- **LawToolBox** ($40-60/month/user): Integrates with Outlook/Google Calendar
- **Deadlines on Demand** (pay-per-use): Upload order, get calculated deadlines

**The Gap**: These tools require manual upload and are expensive for solo practitioners or small firms. Most lawyers still use manual calendar entry, which is error-prone.

---

## How AI Could Improve It

**Vision (Using AI Tools)**:
- **Tool A (OCR + NLP)**: Claude with vision or GPT-4V reads court order PDF/photo
- **Tool B (Rule Engine)**: AI applies jurisdiction-specific court rules automatically (Fed. R. Civ. P. 6, local rules)
- **Tool C (Calendar Integration)**: Auto-creates calendar events with proper lead time
- **Tool D (Monitoring - Experimental)**: AI monitors PACER docket, alerts to new filings automatically

**Example Flow**:
1. Screenshot court order on phone
2. AI reads: "Defendant's motion for summary judgment due 21 days from service"
3. AI calculates: Service date (from docket) + 21 days (excluding weekends/holidays)
4. AI creates: Calendar event for filing deadline, reminders at T-7, T-3, T-1 days
5. AI adds: Draft preparation time blocking (e.g., 5 days before deadline)

**What's Available vs. Experimental**:
- ✅ **Available Today**: OCR text extraction (Apple's on-device OCR, Claude vision API)
- ✅ **Available Today**: Basic deadline calculation (simple date math)
- ⚠️ **Partially Available**: Court rule application (requires building rule database)
- ❌ **Experimental**: Automatic PACER monitoring and parsing (would require API access + AI docket analysis)

---

**What It Does (Tier 0 Implementation)**: Quick capture of court deadlines via voice or text with manual date input. No AI calculation of rules-based deadlines - that's Tier 2+.

**Tier Characteristics**:
- **Manual input**: User specifies deadline date (already calculated)
- **Multi-format**: Voice description or text
- **Calendar integration**: Auto-creates iOS calendar event
- **No intelligence**: No rule application, no PACER integration
- **Reminder stacking**: Multiple reminders for critical deadlines

---

## iOS Shortcut Setup

### Shortcut Name: "Court Deadline"

### Actions Flow:

**1. Capture Deadline Details**
- Ask for Input → "What is the filing/deadline?"
  - Example: "File opposition to MSJ in Johnson v. TechCorp"

**2. Set Deadline Date**
- Ask for Input → "Deadline date?" (Type: Date)
  - Shows date picker
  - User selects date

**3. Capture Case/Matter**
- Ask for Input → "Case or matter name?"
  - Example: "Johnson v. TechCorp, Case No. 3:24-cv-12345"

**4. Set Urgency**
- Ask for Input → "Priority level?"
  - Menu: Critical, High, Normal
  - Critical = multiple reminders, High = standard reminders, Normal = minimal reminders

**5. Create Reminder Structure**
- Get Current Date → Format: yyyy-MM-dd HH:mm
- Create filename: `deadline_{{matter}}_{{date}}.md`
- Format note:
  ```markdown
  ---
  created: {{timestamp}}
  type: court_deadline
  matter: {{matter_name}}
  deadline_date: {{deadline_date}}
  filing: {{filing_description}}
  priority: {{priority_level}}
  status: pending
  ---

  # ⚠️ COURT DEADLINE - {{deadline_date}}

  **Case**: {{matter_name}}

  **Filing Required**: {{filing_description}}

  **Deadline**: {{deadline_date}}

  **Priority**: {{priority_level}}

  **Next Steps**:
  - [ ] Begin draft (recommended: {{deadline_date - 5 days}})
  - [ ] Internal review (recommended: {{deadline_date - 2 days}})
  - [ ] Final filing (deadline: {{deadline_date}})

  **Notes**: [Add details about requirements, page limits, service requirements, etc.]
  ```

**6. Create Calendar Event**
- Add New Event to Calendar:
  - Calendar: "Court Deadlines" (create this calendar first)
  - Title: "⚠️ DEADLINE: {{filing_description}}"
  - Date: {{deadline_date}}
  - Time: 11:59 PM (EOD deadline)
  - Notes: "Case: {{matter_name}}\nFiling: {{filing_description}}\nPriority: {{priority_level}}"
  - Alerts (if Critical priority):
    - 7 days before at 9:00 AM
    - 3 days before at 9:00 AM
    - 1 day before at 9:00 AM
    - Day of at 9:00 AM
  - Alerts (if High priority):
    - 3 days before at 9:00 AM
    - 1 day before at 9:00 AM
  - Alerts (if Normal priority):
    - 1 day before at 9:00 AM

**7. Create Draft Preparation Event** (Optional)
- If priority is Critical or High:
  - Add New Event:
    - Title: "⏰ START: {{filing_description}}"
    - Date: {{deadline_date - 5 days}}
    - Time: 9:00 AM
    - Duration: 4 hours (time block)
    - Notes: "Begin drafting for deadline on {{deadline_date}}"
    - Alert: Day of at 9:00 AM

**8. Save & Notify**
- Save deadline note to: `iCloud/LegalNotes/Deadlines/`
- Show notification: "Court deadline tracked - {{filing_description}} due {{deadline_date}}"
- Optional: Send email to self with deadline details

---

## Usage Examples

**Scenario 1: Motion Deadline from Court Order**
- Just received court order: "Defendant's opposition to motion for summary judgment due December 15, 2025"
- Activate: "Hey Siri, Court Deadline"
- Filing: "File opposition to plaintiff's MSJ"
- Deadline: [Select December 15, 2025]
- Case: "Johnson v. TechCorp, Case No. 3:24-cv-12345"
- Priority: Critical
- Result:
  - Calendar event created for Dec 15 @ 11:59 PM
  - Reminders set for Dec 8, Dec 12, Dec 14, Dec 15 at 9 AM
  - Draft prep time block created for Dec 10-14
  - Note saved to Deadlines folder

**Scenario 2: Discovery Response Deadline**
- Received discovery requests with 30-day response deadline
- Calculated deadline: November 28, 2025
- Activate shortcut
- Filing: "Respond to Plaintiff's First Set of Interrogatories and RFPs"
- Deadline: [Select November 28, 2025]
- Case: "Martinez v. City of Springfield"
- Priority: High
- Result:
  - Calendar event + reminders at -3 days, -1 day
  - Draft prep block created for November 23

**Scenario 3: Appellate Brief Deadline**
- Appellate court order: Opening brief due in 45 days (January 20, 2026)
- Activate shortcut
- Filing: "File Appellant's Opening Brief"
- Deadline: [Select January 20, 2026]
- Case: "Smith v. State Board of Education, Court of Appeal Case No. A054321"
- Priority: Critical
- Result:
  - Full reminder cascade created
  - Extended draft prep time blocks (appeals take longer)

---

## Why Tier 0

- **Manual Date Entry**: User must calculate deadline (no AI rule application)
- **No PACER Integration**: User manually inputs from court orders
- **No Rule Engine**: Doesn't apply court rules (e.g., "21 days excluding weekends")
- **No Document Parsing**: User reads order and extracts deadline manually
- **No Validation**: Doesn't check if deadline conflicts with court holidays

**What's Missing** (Available in Higher Tiers):
- **Tier 2**: Claude reads court order PDF, extracts deadline text, proposes date
- **Tier 3**: LangChain agent applies jurisdiction-specific rules, fetches court holidays, calculates exact deadline
- **Tier 4**: Multi-agent system: ParsingAgent reads order → RuleAgent applies court rules → ValidationAgent checks conflicts → CalendarAgent creates events
- **Tier 5**: Human reviews AI-calculated deadline → Approves → Auto-files to practice management system
- **Tier 6**: Autonomous PACER monitoring, learns from firm's case history to predict optimal time allocation for different motion types

---

## Advanced Customization (Still Tier 0)

### Add Delegation:
- After creating calendar event, ask: "Delegate to team member? (yes/no)"
- If yes: Ask for Input → "Attorney name?"
- Send email with deadline details to delegated attorney
- Include in calendar invite

### Add Service Requirements:
- Ask: "Requires service on opposing counsel? (yes/no)"
- If yes: Create additional calendar event 1-3 days before deadline (depending on service method)
- Title: "SERVE: {{filing_description}}"

### Add Local Rule Reminders:
- For specific courts, add court-specific requirements
- Example: "Central District of California - ECF filing by 11:59 PM PT"
- Add to event notes: "Note: File via ECF at [court's ECF portal URL]"

### Integrate with Practice Management:
- If using Clio, MyCase, etc. with Zapier integration:
- At end of shortcut, trigger Zapier webhook
- Zapier creates task in practice management system
- Maintains single source of truth

---

## Integration with Higher Tiers (Future State)

### Tier 1 (Automated Routing - Available Today)
- n8n workflow monitors `Deadlines/` folder
- Routes by priority: Critical → Slack alert to senior partner, High → Email digest
- Daily summary email: "Upcoming deadlines this week"
- See `tier_1_n8n_law_deadline_router.json`

### Tier 2 (AI Deadline Extraction - Available Today)
- Upload court order PDF
- Claude extracts: "Defendant shall file opposition within 21 days of service"
- Proposes deadline date based on docket service date
- User confirms → Creates calendar event
- See `tier_2_cldchoice_law_order_parser.json`

### Tier 3 (Rule-Based Calculation - Partially Experimental)
- LangChain agent with tools:
  - `court_rule_lookup`: Fetches FRCP/local rules on deadline calculation
  - `holiday_checker`: Gets federal/state/court-specific holidays
  - `date_calculator`: Applies rules (exclude weekends, add court rule time)
- Example: "21 days from service" + service date 11/1 + FRCP 6(a) rules → Deadline: 11/26 (excluding weekends, accounting for Thanksgiving if court is closed)
- See `tier_3_langchain_deadline_calculator.py`

### Tier 4 (Multi-Agent Deadline System - Experimental)
- **ParsingAgent**: OCR + NLP to read court order
- **RuleAgent**: Applies jurisdiction rules, checks conflicts
- **ValidationAgent**: Cross-references with case docket, ensures no errors
- **CalendarAgent**: Optimally schedules prep time based on team workload
- See `tier_4_langgraph_deadline_manager.py`

### Tier 5 (Human-in-Loop Workflow - Experimental)
- AI processes order → Calculates deadline → Proposes calendar events
- Attorney reviews → Edits if needed → Approves
- AI auto-syncs to: Outlook/Google Calendar, Clio/MyCase, team Slack channel
- AI generates delegation email with context
- See `tier_5_claude_code_deadline_orchestrator.py`

### Tier 6 (Autonomous Deadline Monitoring - Future/Speculative)
- System monitors PACER dockets 24/7
- Instantly detects new filings/orders
- Predicts likely deadlines based on motion type
- Auto-calculates and proposes calendar entries
- Learns from corrections: "Attorney always starts briefs 10 days early, not 5"
- Adapts scheduling to attorney's historical patterns
- **Highly Experimental**: Requires PACER API access (currently restricted), legal authorization for automated monitoring
- See `tier_6_autonomous_docket_monitor.py`

---

## Legal Tech Context (2025)

### What's Driving Adoption:
1. **Malpractice Insurance Pressure**: Missed deadlines are leading cause of malpractice claims - insurers incentivize deadline tracking tech
2. **Solo Practitioner Growth**: 50%+ of lawyers are solo - need affordable deadline solutions
3. **Post-COVID Remote Work**: Lawyers not in office to see physical calendars, need mobile-first solutions
4. **Ethics Rule Updates**: State bars now require "technological competence" (ABA Model Rule 1.1, Comment 8)

### Current Market Solutions:
- **CompuLaw**: $1,200-2,400/year per attorney - robust but expensive
- **LawToolBox**: $480-720/year per attorney - Outlook/Google integration
- **DIY Solutions** (like this): $0 cost, requires tech comfort, manual entry
- **Emerging AI Tools** (2025): Harvey AI, CaseText CoCounsel offer deadline extraction (experimental, not yet court-vetted)

### The AI Opportunity:
- **Reduce Manual Entry**: 80% of lawyers manually enter deadlines - AI could automate
- **Reduce Errors**: Deadline miscalculation causes $100M+ in malpractice claims annually
- **Improve Access to Justice**: Solo/small firms could compete with big law tech stacks
- **Experimental Frontier**: Predictive scheduling (AI learns optimal prep time), proactive conflict detection (AI spots scheduling conflicts before they happen)

### The AI Risks:
- **Hallucination**: AI could misread court order ("21 days" vs "21 business days")
- **Liability**: Who's responsible if AI miscalculates deadline?
- **Over-Reliance**: Lawyers must maintain competence to spot AI errors
- **Ethics**: Some jurisdictions may not yet approve fully automated deadline systems without human review

**Current Best Practice (2025)**: Use AI to *propose* deadlines (Tier 2-3), but always require attorney review (Tier 5) before finalizing. Fully autonomous systems (Tier 6) are not yet ethically viable without human oversight.

---

## Why This Example Matters

This Tier 0 example demonstrates:
1. **Immediate Value**: Even without AI, structured capture beats scattered notes
2. **Foundation for AI**: Metadata schema enables future AI processing
3. **Gradual Adoption**: Lawyers can start simple, add AI layers later
4. **Ethics Compliance**: Human remains in control, AI augments (when added in higher tiers)

**Next Steps**: Try the basic shortcut, then explore Tier 2 AI-enhanced parsing in `tier_2_cldchoice_law_order_parser.json`.
