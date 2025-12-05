# BR2 - Tier 0 - Multi-Source Quick Capture via iOS Shortcuts

**What It Does**: Universal capture shortcut supporting voice, text, links, and screenshots - all saved directly to Obsidian inbox with metadata tagging. No processing, just frictionless capture.

**Tier Characteristics**:
- **Multi-format input**: Voice, text, URL, photo/screenshot
- **Instant save**: Direct to Obsidian inbox folder
- **No AI**: Zero processing, categorization, or organization
- **Metadata only**: Source type, timestamp, context tags

---

## iOS Shortcut Setup

### Shortcut Name: "Quick Capture"

### Actions Flow:

**1. Choose Capture Type (Menu)**
- Voice Note
- Text Note
- Web Link
- Screenshot/Photo

**2. Voice Note Path:**
- Dictate Text → "What's on your mind?"
- Get Current Date → Format: yyyy-MM-dd HH:mm
- Create filename: `voice_{{timestamp}}.md`
- Format content:
  ```markdown
  ---
  created: {{timestamp}}
  source: voice
  status: inbox
  ---

  {{dictated text}}
  ```
- Save to: `iCloud/Obsidian/Vault/00_Inbox/`
- Show notification: "Voice note captured"

**3. Text Note Path:**
- Ask for Input → "Enter note"
- Get Current Date
- Create filename: `text_{{timestamp}}.md`
- Format with frontmatter (source: text)
- Save to inbox
- Notify

**4. Web Link Path:**
- Get URLs from Input (Share Sheet)
- Get webpage contents
- Get webpage title
- Create filename: `link_{{title}}_{{timestamp}}.md`
- Format:
  ```markdown
  ---
  created: {{timestamp}}
  source: web_link
  url: {{url}}
  status: inbox
  ---

  # {{page title}}

  {{page content converted to markdown}}
  ```
- Save to inbox
- Notify

**5. Screenshot Path:**
- Take photo OR get from Share Sheet
- Save image to: `00_Inbox/attachments/img_{{timestamp}}.jpg`
- Create note: `screenshot_{{timestamp}}.md`
- Format:
  ```markdown
  ---
  created: {{timestamp}}
  source: screenshot
  status: inbox
  ---

  ![[img_{{timestamp}}.jpg]]

  [Add context here]
  ```
- Save to inbox
- Notify

---

## Usage Examples

**Voice Capture:**
- Activate: "Hey Siri, Quick Capture"
- Select: Voice Note
- Speak: "Idea for automating lead research - use LangChain agent with web search and LinkedIn tools to find decision makers automatically"
- Result: Saved to `00_Inbox/voice_20251117_093012.md`

**Web Link Capture:**
- Reading article in Safari
- Share → Quick Capture → Web Link
- Result: Full article saved with metadata

**Screenshot Capture:**
- Take screenshot of interesting slide
- Share → Quick Capture → Screenshot
- Result: Image + note saved to inbox

---

## Why Tier 0

- **No Intelligence**: Zero AI, categorization, or processing
- **Manual Followup**: All items require manual inbox processing
- **Single Destination**: Everything goes to same inbox folder
- **No Automation**: No downstream workflows triggered

---

## Integration with Higher Tiers

**Tier 1 (Router)**: n8n workflow checks inbox every hour, routes by source type
**Tier 2 (Categorizer)**: Claude analyzes content, suggests PARA categories
**Tier 3 (Connector)**: LangChain agent finds related notes and creates links

See `tier_1_cldchoice_br2_capture_router.json` for automated processing.
