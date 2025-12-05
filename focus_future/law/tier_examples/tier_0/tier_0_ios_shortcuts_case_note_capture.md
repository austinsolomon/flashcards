# Law - Tier 0 - Case Note & Research Capture via iOS Shortcuts

## What Is Available Today

**Current State of Legal Note-Taking (2025)**:

Most attorneys and legal professionals use a patchwork of tools for capturing case notes, client communications, and legal research:
- **Handwritten notes** in courtrooms (many courts still ban electronic devices)
- **Voice memos** recorded after meetings or hearings
- **Email to self** with quick thoughts or citations
- **Screenshots** of key case law or documents on phones
- **Native Notes app** for ad-hoc capture
- **Practice management software** (Clio, MyCase) - but often too cumbersome for quick capture

**The Problem**: Legal professionals lose critical details in the hours between a hearing/meeting and when they return to their desk. Client conversations, opposing counsel's statements, judge's comments, and research ideas evaporate before they can be properly documented.

**What Exists**: Apps like Evernote, OneNote, or legal-specific tools (Fastcase Docket, CaseFleet) offer mobile capture, but they're typically siloed - voice notes go one place, photos another, text notes elsewhere.

---

## How AI Could Improve It

**Vision**: A unified capture system that uses AI to automatically:
- **Transcribe & structure** voice notes into case timeline entries
- **Extract citations** from screenshots of case law
- **Categorize** notes by matter/client using natural language understanding
- **Link** new notes to existing case files automatically
- **Flag** action items and deadlines mentioned in voice/text
- **Suggest** relevant precedents based on captured research ideas

**Tools That Enable This**:
- **Tool A (Capture Layer)**: iOS Shortcuts for frictionless multi-format capture
- **Tool B (Processing Layer - Tier 2+)**: Claude/GPT-4 for transcription analysis, citation extraction, categorization
- **Tool C (Routing Layer - Tier 1+)**: n8n workflows to route by matter type and priority
- **Tool D (Future/Experimental)**: Vision models (Claude with vision, GPT-4V) to read handwritten notes from photos

**Current Implementation Below (Tier 0)**: Just the capture - no AI processing yet.

---

**What It Does**: Universal legal capture shortcut supporting voice, text, URLs, and photos - all saved to a central inbox with legal-specific metadata tagging. No processing, just frictionless capture optimized for legal workflows.

**Tier Characteristics**:
- **Multi-format input**: Voice, text, URL, photo/screenshot
- **Instant save**: Direct to legal notes folder (Obsidian/Notion/filesystem)
- **No AI**: Zero processing, categorization, or organization
- **Legal metadata**: Matter tag, source type, timestamp, urgency flag

---

## iOS Shortcut Setup

### Shortcut Name: "Legal Capture"

### Actions Flow:

**1. Choose Capture Type (Menu)**
- Voice Note (Hearing/Meeting)
- Case Law Screenshot
- Quick Text Note
- Client Communication
- Deadline/Action Item

**2. Voice Note Path:**
- Dictate Text → "Record your note"
- Get Current Date → Format: yyyy-MM-dd HH:mm
- Ask for Input → "Matter name or number?" (optional)
- Create filename: `voice_{{timestamp}}.md`
- Format content:
  ```markdown
  ---
  created: {{timestamp}}
  source: voice
  matter: {{matter_input}}
  status: inbox
  type: legal_note
  ---

  # Voice Note - {{timestamp}}

  {{dictated text}}

  ---
  **Next Steps**: Review and categorize
  ```
- Save to: `iCloud/LegalNotes/00_Inbox/`
- Show notification: "Voice note captured - {{matter_input}}"

**3. Case Law Screenshot Path:**
- Take photo OR get from Share Sheet
- Ask for Input → "Case name or citation?" (optional)
- Save image to: `00_Inbox/attachments/case_{{timestamp}}.jpg`
- Create note: `case_screenshot_{{timestamp}}.md`
- Format:
  ```markdown
  ---
  created: {{timestamp}}
  source: screenshot
  case_citation: {{citation_input}}
  status: inbox
  type: case_law
  ---

  # Case Law - {{citation_input}}

  ![[case_{{timestamp}}.jpg]]

  **Context**: [Add why this case matters]

  **Next Steps**: Extract key holdings, add to research memo
  ```
- Save to inbox
- Notify

**4. Quick Text Note Path:**
- Ask for Input → "Enter note"
- Ask for Input → "Related matter?" (optional)
- Ask for Input → "Urgent? (yes/no)" → Default: no
- Get Current Date
- Create filename: `note_{{timestamp}}.md`
- Format with frontmatter:
  ```markdown
  ---
  created: {{timestamp}}
  source: text
  matter: {{matter_input}}
  urgent: {{urgent_flag}}
  status: inbox
  type: quick_note
  ---

  {{note_text}}
  ```
- Save to inbox
- Notify

**5. Client Communication Path:**
- Ask for Input → "Client name?"
- Dictate Text → "What was discussed?"
- Get Current Date
- Create filename: `client_{{client_name}}_{{timestamp}}.md`
- Format:
  ```markdown
  ---
  created: {{timestamp}}
  source: client_communication
  client: {{client_name}}
  status: inbox
  type: client_note
  ---

  # Client Communication - {{client_name}}

  **Date**: {{timestamp}}

  **Discussion**:
  {{dictated text}}

  **Follow-up Required**: [Review and add action items]
  ```
- Save to inbox
- Notify

**6. Deadline/Action Item Path:**
- Ask for Input → "What is the deadline/action?"
- Ask for Date → "Due date?"
- Ask for Input → "Related matter?"
- Get Current Date
- Create filename: `deadline_{{timestamp}}.md`
- Format:
  ```markdown
  ---
  created: {{timestamp}}
  source: deadline
  due_date: {{due_date}}
  matter: {{matter_input}}
  status: inbox
  type: deadline
  urgent: true
  ---

  # ⚠️ DEADLINE - {{due_date}}

  **Action Required**: {{deadline_description}}

  **Matter**: {{matter_input}}

  **Created**: {{timestamp}}

  **Next Steps**: Add to calendar, assign responsibility
  ```
- Save to inbox
- Add to Calendar (optional)
- Notify with urgency

---

## Usage Examples

**Scenario 1: Post-Hearing Voice Note**
- Walking out of courthouse after hearing
- Activate: "Hey Siri, Legal Capture"
- Select: Voice Note
- Speak: "Judge Thompson seemed receptive to our motion to dismiss arguments, especially the jurisdictional points. Opposing counsel mentioned they may be willing to discuss settlement in the $400-500K range. Need to call client today to discuss."
- Matter: "Johnson v. TechCorp"
- Result: Saved to `00_Inbox/voice_20251118_1430.md`

**Scenario 2: Case Law Discovery**
- Reading case on Westlaw mobile
- Find key precedent that supports argument
- Screenshot the headnote
- Share → Legal Capture → Case Law Screenshot
- Enter citation: "Smith v. Jones, 123 F.3d 456 (9th Cir. 2024)"
- Result: Image + structured note saved, ready for research memo integration

**Scenario 3: Client Phone Call**
- Just finished client call about new development
- Select: Client Communication
- Client name: "Sarah Martinez"
- Dictate: "Client just received discovery requests from opposing counsel. 45 interrogatories and 30 requests for production. Client concerned about cost of response. Discussed limiting scope through meet-and-confer. Client authorized up to $5K for discovery response prep."
- Result: Timestamped client communication logged for billing and case strategy

**Scenario 4: Deadline Capture**
- Receive court order with new filing deadline
- Select: Deadline/Action Item
- Action: "File opposition to motion for summary judgment"
- Due date: December 15, 2025
- Matter: "Martinez v. City of Springfield"
- Result: Deadline logged, calendar entry created, flagged as urgent

---

## Why Tier 0

- **No Intelligence**: Zero AI, categorization, or processing
- **Manual Followup**: All items require manual review and filing
- **Single Destination**: Everything goes to inbox folder
- **No Automation**: No downstream workflows triggered
- **No Analysis**: Citations, deadlines, action items must be manually extracted

---

## Integration with Higher Tiers (Future State)

**Tier 1 (Router - Available Today)**:
- n8n workflow checks inbox hourly
- Routes voice notes, case screenshots, client communications to appropriate matter folders
- Based on simple rules (matter name matching)

**Tier 2 (AI Categorizer - Available Today)**:
- Claude analyzes voice transcriptions
- Extracts: case citations, deadlines, action items, client names
- Categorizes by: matter type (litigation, transactional, etc.), urgency, practice area
- **Example**: "Judge mentioned December 15th deadline" → Auto-creates calendar event

**Tier 3 (Citation Extractor - Available Today)**:
- LangChain agent with OCR tool
- Reads case law screenshots
- Extracts citations, holdings, procedural posture
- Links to Westlaw/Lexis if available
- Suggests related cases from your research database

**Tier 4 (Multi-Agent Research Assistant - Experimental)**:
- CoordinatorAgent receives new case law screenshot
- ResearchAgent finds related cases and statutes
- SummaryAgent creates research memo with holdings
- CitationAgent validates all citations for accuracy
- **Experimental**: Relies on legal-trained models (e.g., LexGPT, CaseText's Co-Counsel)

**Tier 5 (Human-in-Loop Brief Prep - Experimental)**:
- AI processes captured research notes
- Generates draft argument outline
- Attorney reviews and edits
- AI expands outline into full brief section
- Attorney finalizes and cites
- **Experimental**: Requires high confidence in AI-generated legal writing

**Tier 6 (Autonomous Case Tracker - Future/Speculative)**:
- System learns from all captured notes over time
- Predicts case outcomes based on judge, opposing counsel, case type
- Automatically identifies gaps in research
- Suggests case strategy adjustments
- **Highly Experimental**: Requires extensive training on firm's historical data

---

## Technical Implementation Notes

**Storage Options**:
1. **Obsidian Vault** (Recommended for lawyers):
   - Markdown-native
   - Works with iOS Shortcuts via iCloud
   - Local-first (client confidentiality)
   - Powerful linking and search
   - Path: `iCloud Drive/Obsidian/LegalVault/00_Inbox/`

2. **Notion**:
   - Via Notion API (requires webhook)
   - Better for team collaboration
   - Cloud-based (evaluate against ethics rules)

3. **Local Filesystem**:
   - Direct file save to iCloud/Dropbox
   - Most flexible, most manual

**Security Considerations**:
- **Client Confidentiality**: All captured notes may contain privileged information
- **Encryption**: Use encrypted cloud storage (Apple's iCloud is encrypted in transit and at rest)
- **Device Security**: Ensure iPhone has passcode/biometric lock
- **Ethics Rules**: Verify your jurisdiction's ethics opinions on cloud storage (most now allow with reasonable precautions)

**Metadata Schema**:
```yaml
---
created: 2025-11-18 14:30:00
source: voice|screenshot|text|client_communication|deadline
matter: "Client v. Opposing Party" or matter number
status: inbox|reviewed|filed|archived
type: legal_note|case_law|client_note|deadline|quick_note
urgent: true|false
practice_area: litigation|transactional|ip|family|criminal
case_citation: (if applicable)
due_date: (if deadline)
client: (if client communication)
---
```

---

## Advanced Customization (Still Tier 0)

### Add Practice Area Tagging:
In each capture path, add:
- Ask for Input → "Practice area?" → Menu: Litigation, Transactional, IP, Family, Criminal, Other
- Include in frontmatter: `practice_area: {{selected_area}}`

### Add Billing Flag:
- Ask for Input → "Billable? (yes/no)"
- Include: `billable: {{billable_flag}}`
- Enables later time entry automation (Tier 3+)

### Add Dictation Templates:
For recurring note types (e.g., deposition prep, client intake):
- Create separate shortcuts with pre-filled templates
- "Deposition Prep Capture"
- "New Client Intake"
- "Settlement Conference Notes"

### Share Extension Optimization:
Enable shortcut in Share Sheet for:
- Safari (capture legal research articles)
- Mail (save important emails as notes)
- Files (annotate documents)

---

## Comparison: Manual vs. This System

| Task | Manual Method | This System (Tier 0) | Future with AI (Tier 3+) |
|------|---------------|---------------------|--------------------------|
| **Capture Time** | 2-5 min to write/type | 30 sec voice dictation | 30 sec + auto-categorization |
| **Organization** | Manual filing later | Manual filing from inbox | Auto-filed by matter |
| **Citation Extraction** | Manual copy/paste | Screenshot saved | Auto-extracted, Shepardized |
| **Deadline Tracking** | Manual calendar entry | Screenshot + manual entry | Auto-calendar + reminders |
| **Search/Retrieval** | Dig through folders/emails | Full-text search in notes | Semantic search: "cases about attorney's fees" |
| **Integration** | Re-enter into practice mgmt | Copy/paste from notes | Auto-sync to Clio/MyCase |

---

## Why This Matters for Law (2025 Context)

**Current Trends**:
1. **Solo/Small Firms**: Most practitioners (67%) work in firms of 5 or fewer lawyers - need efficient systems without big budgets
2. **Hybrid Work**: Post-pandemic, lawyers work from court, home, office - need universal capture
3. **Client Expectations**: Clients expect faster responses and better communication
4. **Billing Pressure**: Captured contemporaneous notes improve billing accuracy and reduce writeoffs
5. **Ethics Evolution**: Bar associations increasingly recognize cloud tools as ethically compliant with proper safeguards

**AI's Role** (Near Future):
- **Reduces Administrative Burden**: Lawyers spend 48% of time on admin tasks (ABA survey) - AI can reclaim this time for legal work
- **Improves Client Service**: Faster note processing → faster follow-up → happier clients
- **Enhances Research**: AI citation extraction and case linking makes research more thorough
- **Risk Mitigation**: AI-flagged deadlines and action items reduce malpractice risk from missed deadlines
- **Access to Justice**: Efficiency gains could make legal services more affordable

**What's Holding It Back**:
- **Ethics Concerns**: Confidentiality, competence requirements for understanding AI tools
- **Hallucination Risk**: AI-generated legal citations must be verified (see Mata v. Avianca sanctions)
- **Liability Questions**: Who's responsible for AI errors in legal work?
- **Training Gap**: Most lawyers not trained in AI prompt engineering or workflow design

See `tier_2_cldchoice_law_contract_analyzer.json` for AI-enhanced contract review.
