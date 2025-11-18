# Law - Tier 0 (TOY) - Quick Legal Research Capture

## What Is Available Today

**Current Practice**: Law students, clerks, and junior attorneys spend hours reading cases and statutes, taking notes in Word docs, Google Docs, or legal pads. These notes are scattered and hard to search later.

**Basic Digital Solution**: A simple iOS Shortcut can capture research notes with minimal friction - speak a case name and your thoughts, and it's instantly saved with metadata.

---

## How AI Could Improve It (Future Vision)

**Today (Tier 0)**: Voice → Text file
**Future (Tier 2+)**: Voice → AI extracts case citation → Auto-fetches case from Lexis/Westlaw → Links to related memos → Suggests relevant statutes

---

**What It Does**: Minimal viable legal research capture - voice input saved as markdown file with timestamp.

**Tier Characteristics**:
- **Single input mode**: Voice only (simplest use case)
- **Instant save**: Direct to research folder
- **No AI**: Just transcription, no analysis
- **Basic metadata**: Timestamp only

---

## iOS Shortcut Setup

### Shortcut Name: "Research Note"

### Actions Flow:

**1. Dictate Research Note**
- Dictate Text → "What did you learn?"
- Get Current Date → Format: yyyy-MM-dd HH:mm

**2. Save Note**
- Create filename: `research_{{timestamp}}.md`
- Format content:
  ```markdown
  # Research Note - {{timestamp}}

  {{dictated text}}
  ```
- Save to: `iCloud/LegalResearch/`
- Show notification: "Research note saved"

---

## Usage Example

**Scenario**: Reading *Brown v. Board of Education* for Con Law class

1. Activate: "Hey Siri, Research Note"
2. Speak: "Brown v Board - Equal Protection Clause. Court held separate but equal is inherently unequal. Key for our education policy memo - shows strict scrutiny applies to racial classifications."
3. Result: Saved to `research_20251118_1530.md`

**Later**: Search notes for "Equal Protection" to find all related research.

---

## Why Tier 0

- **No Processing**: Just saves raw transcription
- **No Structure**: No auto-extraction of case names or citations
- **No Context**: Can't search by case name, topic, or jurisdiction
- **Manual Organization**: User must manually organize notes later

---

## Upgrade Path

**Tier 1**: Add scheduled routing - every night, move notes to dated folders
**Tier 2**: Add Claude to extract case citations and create structured summaries
**Tier 3**: LangChain agent auto-Shepardizes cases and finds related holdings
**Tier 4**: Multi-agent system builds full research memo from scattered notes

See `tier_3_langchain_legal_research_agent.py` for AI-powered research compilation.
