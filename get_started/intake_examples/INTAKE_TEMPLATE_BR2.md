# AUTOMATION INTAKE REQUEST TEMPLATE
## Domain: BR2 (Personal Productivity & Knowledge Management)

**Workflow Name:** [Short, descriptive name for this automation]

---

## 1. PROBLEM STATEMENT (2-3 sentences)
[Describe the productivity pain point this automation will solve. Include:]
- What manual knowledge work is slowing you down?
- How much time is wasted per occurrence?
- What is the impact on your ability to focus, capture insights, or execute?

**Example:**
> When I finish reading articles, newsletters, or documentation, I manually spend 10-15 min per item extracting key insights, categorizing with PARA, creating Obsidian notes, and deciding if action items need to go to Todoist. This interrupts flow state and reduces my daily reading capacity from 15 articles to 6-8, leaving valuable insights uncaptured.

---

## 2. CURRENT MANUAL PROCESS (Step-by-step)
[List each step currently done manually. Be specific about tools, apps, and decision points.]

**Example:**
1. Finish reading article in browser or Pocket
2. Open Obsidian, create new note manually
3. Copy/paste article title, URL, author
4. Re-read article to extract 3-5 key insights
5. Manually categorize using PARA methodology:
   - Is this for an active Project?
   - Ongoing Area of responsibility?
   - Reference Resource?
   - Archive?
6. Add relevant tags (#productivity, #ai, #career, etc.)
7. Check if any insights are actionable
8. If actionable: open Todoist, create task(s) with context
9. Link Todoist task to Obsidian note
10. File note in correct PARA folder
11. Update weekly review dashboard

**Time per occurrence:** 10-15 minutes/article
**Frequency:** 5-10 articles/day
**Total weekly burden:** 6-12 hours

---

## 3. DESIRED AUTOMATION

### Input:
[What triggers the automation and what data is available?]

**Example:**
- **Trigger:** Pocket article saved with tag "#process" (webhook)
  - OR: Obsidian quick capture note created in /Inbox
  - OR: Email forwarded to custom address
- **Data Available:**
  - Article URL or full text
  - Title and author
  - Source (Pocket, email, RSS)
  - Timestamp saved
  - User-added tags (if any)

### Process:
[Step-by-step automated workflow. Be specific about AI calls, decision logic, and routing.]

**Example:**
1. Fetch article full text (via web scraper or Pocket API)
2. Call Claude API to:
   - Summarize article (3-5 key insights)
   - Classify using PARA methodology (Project/Area/Resource/Archive)
   - Suggest relevant tags based on content
   - Identify if actionable (yes/no + suggested actions)
   - Determine priority level (high/medium/low)
3. Route based on PARA classification:
   - **Project**: Link to active project note, update project dashboard
   - **Area**: File in relevant area folder (career, health, learning, etc.)
   - **Resource**: Add to reference library with topic tags
   - **Archive**: Store in archives with date
4. If actionable:
   - Create Todoist task(s) with AI-suggested action
   - Set due date based on priority
   - Add link back to Obsidian note
5. Create Obsidian note with:
   - Article metadata (title, URL, author, date)
   - AI-generated summary
   - Key insights (bullet points)
   - PARA classification and tags
   - Link to related notes (if applicable)
6. Post to designated Slack channel or update Notion dashboard

### Output:
[What is created/updated/delivered after automation runs?]

**Example:**
- **Obsidian note** created in correct PARA folder:
  - Clean markdown formatting
  - AI-generated summary and insights
  - Proper tags and frontmatter
  - Backlinks to related notes
- **Todoist task(s)** created (if actionable):
  - Context-rich task description
  - Due date based on priority
  - Project assignment
  - Link to source note
- **Weekly review dashboard** updated:
  - New insights count
  - Category breakdown (PARA distribution)
  - Action items generated
- **Notification** sent (Slack or email):
  - Summary of what was processed
  - Link to new note
  - Flagged high-priority items

---

## 4. SUCCESS CRITERIA
[Measurable outcomes that define success. Use metrics, percentages, or time savings.]

**Example:**
- [ ] Article processing time reduced from 12min → <1min per item
- [ ] Daily reading/processing capacity increases from 6-8 → 20+ articles
- [ ] Knowledge capture completeness improves (spot-check: >90% of insights captured)
- [ ] Actionable items successfully converted to tasks (>95% accuracy on actionability detection)
- [ ] Weekly review prep time reduced from 90min → 15min
- [ ] PARA categorization accuracy >85% (manual correction needed <15% of time)

---

## 5. CONSTRAINTS & REQUIREMENTS

### Must Integrate With:
[List all apps/tools that need to connect]

**Example:**
- Obsidian (Local REST API plugin)
- Todoist (REST API)
- Pocket (API for article saving)
- Notion or Airtable (dashboard/tracking)
- Slack (webhook notifications)
- Email (IMAP for forwarded articles)

### Technical Constraints:
[API limits, cost constraints, performance requirements]

**Example:**
- Claude API calls must stay <$0.15/article
- System must handle 10-20 articles/day
- Processing must complete within 2 minutes per article
- Must work offline for Obsidian local vault (no cloud-only solutions)
- Must preserve original article formatting/images where possible

### Human-in-the-Loop Requirements:
[What needs manual review/approval?]

**Example:**
- I want to review/approve AI-generated summaries before filing (initially)
- After 2 weeks, auto-file if confidence score >85%
- Flag edge cases for manual PARA classification (e.g., could be Project OR Area)
- Let me manually edit task descriptions before they go to Todoist

### Privacy/Security:
[Data handling, sensitive info, local vs cloud]

**Example:**
- All article processing must use local LLM OR encrypted API calls
- Do not send proprietary/sensitive content to external APIs
- Obsidian vault must remain local (no cloud sync without encryption)
- Log all AI decisions for personal audit trail
- Delete processed articles from Pocket after 30 days

---

## 6. COMPLEXITY SIGNALS (Help the router)

### Decision Complexity:
[Check all that apply - helps determine automation tier]

- [ ] Needs contextual reasoning (e.g., "Does this relate to my current project goals?")
- [ ] Needs natural language generation (e.g., writing summaries, drafting tasks)
- [ ] Needs multi-source data fusion (e.g., combining article content + my existing notes + calendar context)
- [ ] Requires sequential decision-making (e.g., classify → decide actionability → route to folder)
- [ ] Needs to learn from feedback (e.g., improve PARA classification based on my corrections)

### Integration Complexity:
[Check all that apply]

- [ ] 1-2 systems (Tier 0-1: simple integrations like Pocket → Obsidian)
- [ ] 3-4 systems (Tier 2-3: Pocket → Claude → Obsidian → Todoist)
- [ ] 5+ systems (Tier 3-4: Pocket → Claude → Obsidian → Todoist → Notion → Slack)
- [ ] API rate limits to manage (specify: e.g., Anthropic: 50 requests/min)
- [ ] Real-time trigger required (webhook, file watcher, email polling)
- [ ] Batch processing acceptable (run once daily)

### State Management:
[Check all that apply]

- [ ] Stateless (each article processed independently)
- [ ] Stateful (needs to track my reading history, note connections over time)
- [ ] Multi-step agent coordination (e.g., SummaryAgent → ClassificationAgent → ActionAgent)
- [ ] Human approval loops (I must approve before final filing/task creation)

### Suggested Tier:
[Based on complexity signals - see tier definitions]

**Tier Estimate:** 2-3 (n8n + Claude OR LangChain agent)

**Reasoning:**
- Event-based trigger (Pocket webhook) = Tier 2
- ONE LLM call (Claude summarizes + classifies + suggests actions) = Tier 2
- Semantic PARA routing (not keyword-based) = Tier 2
- Multi-system integration (Pocket, Obsidian, Todoist) = Tier 2-3
- If agent needs to search my existing notes for context = Tier 3

---

## 7. NICE-TO-HAVES (Future iterations)
[Features that would be valuable but aren't required for MVP]

**Example:**
- Auto-detect duplicate articles already in my vault
- Link new notes to related existing notes using semantic search
- Summarize weekly reading patterns and suggest focus areas
- Auto-generate Anki flashcards from key insights
- Adaptive learning: improve PARA classification based on my manual corrections
- Calendar integration: schedule "deep work" blocks for high-priority tasks
- Cross-reference with my goals/OKRs in Notion
- Voice note transcription and processing (iOS Shortcuts integration)
- Generate monthly "knowledge graph" visualization of learned topics

---

## 8. ADDITIONAL CONTEXT

### My Productivity System:
[How do you currently work? What's your stack?]

**Example:**
- **PKM System:** Obsidian (Zettelkasten + PARA hybrid)
- **Task Manager:** Todoist (GTD methodology)
- **Read-it-later:** Pocket (20-30 articles saved/week)
- **Calendar:** Google Calendar
- **Notes:** Obsidian for long-form, Apple Notes for quick capture
- **Communication:** Slack (work), Email (personal)

### Current Pain Points:
[Specific frustrations or blockers]

**Example:**
- I capture articles but don't have time to process them → backlog of 200+ unread
- PARA classification is inconsistent → hard to find notes later
- Insights don't turn into action → great ideas lost in notes
- Weekly review takes too long → often skip it
- No way to track which topics I'm learning about most

### Related Workflows:
[Other automations that might interact with this one]

**Example:**
- Daily note template automation (Tier 1) creates daily notes at 6am
- Weekly review prep (Tier 2) aggregates completed tasks and new notes
- Meeting notes processor (Tier 2) extracts action items from meeting transcripts
- Email inbox triage (Tier 2) routes emails to Obsidian inbox

---

## ROUTING VALUE FOR AUTOMATION TIERS

| Intake Field | Routing Value |
|---|---|
| **Problem Statement** | Clarifies scope - one workflow, not entire productivity system |
| **Current Process** | Shows manual steps → identifies automation tier |
| **Input/Output** | Defines data contracts → API feasibility check |
| **Success Criteria** | Measurable → validates tier can achieve goals |
| **Constraints** | Surfaces technical limits (API costs, privacy) |
| **Complexity Signals** | **Most important** - directly maps to tiers 0-6 |

---

## EXAMPLE: QUICK WIN WORKFLOWS FOR BR2

Use this template for common personal productivity automation requests:

1. **Article processing & PARA filing** ← Start here (Tier 2-3)
2. **Daily note template with AI-suggested focus** ← Tier 2-3
3. **Meeting notes → action items extractor** ← Tier 2-3
4. **Email inbox PARA triage** ← Tier 2-3
5. **Weekly review prep automation** ← Tier 2-3
6. **Goal/OKR progress tracker** ← Tier 1-2
7. **Reading list prioritizer** ← Tier 3-4
8. **Habit tracker anomaly detection** ← Tier 3-4

**Recommendation:** Submit #1 first using this template. Once built, use it as a pattern for the others.
