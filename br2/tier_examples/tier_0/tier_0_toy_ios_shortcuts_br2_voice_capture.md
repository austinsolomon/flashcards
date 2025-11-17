# BR2 - Tier 0 - Voice-to-Text Quick Capture via iOS Shortcut

**What It Does**: Captures a voice memo and converts it to text, saving directly to your Obsidian inbox folder. Simple, one-step conversion with no organization or processing.

**Tier Characteristics**:
- **Direct trigger**: Voice input triggers immediate transcription and save
- **No processing**: Transcribed text saved as-is, no formatting or categorization
- **One action**: Voice → text → save to inbox
- **No organization**: All notes go to same inbox folder for later manual processing

---

## Setup Steps

1. **Open iOS Shortcuts app** on your iPhone
2. **Create new Shortcut** and name it "Quick Capture"
3. **Set up Obsidian vault access** via iCloud Drive or Obsidian app integration
4. **Add actions** as detailed below
5. **Add to Home Screen, Widget, or Siri** for instant access

---

## Shortcut Actions

### Action 1: Dictate Text
- **Type**: Dictate Text
- **Configuration**:
  - Prompt: "What's on your mind?"
  - Language: English (or your preference)
  - Stop listening: After Pause
- **Purpose**: Capture voice input and convert to text
- **Example Input**: "Interesting idea for project - create a personal knowledge graph that automatically links concepts across different domains, could help identify unexpected connections"

### Action 2: Get Current Date
- **Type**: Date
- **Configuration**:
  - Date: Current Date
  - Format: Custom → "yyyy-MM-dd HH:mm" (e.g., 2025-11-17 15:45)
- **Purpose**: Create timestamp for the note

### Action 3: Format Note Content
- **Type**: Text
- **Configuration**: Combine the following:
  ```
  ---
  created: [Current Date]
  source: voice_capture
  status: inbox
  ---

  [Dictated Text]
  ```
- **Purpose**: Add basic frontmatter metadata for Obsidian

### Action 4: Create Filename
- **Type**: Text
- **Configuration**:
  - Format: `inbox_[Current Date - yyyyMMdd_HHmmss].md`
  - Example: `inbox_20251117_154530.md`
- **Purpose**: Unique filename for each capture

### Action 5: Save to Obsidian Inbox
- **Type**: Save File
- **Configuration**:
  - File: Formatted Note Content
  - Filename: Created Filename
  - Destination: `iCloud Drive/Obsidian/YourVault/00_Inbox/`
  - Ask Where to Save: NO
  - Overwrite: NO
- **Purpose**: Save to Obsidian inbox for later processing

### Action 6: Show Notification
- **Type**: Show Notification
- **Configuration**:
  - Title: "Note Captured"
  - Body: "Added to inbox: [Filename]"
- **Purpose**: Confirm successful save

---

## Example Usage

### **Scenario 1**: Capturing Fleeting Thought

**Input** (Voice):
> "Interesting idea for project - create a personal knowledge graph that automatically links concepts across different domains, could help identify unexpected connections between reading notes and project ideas"

**Process**:
1. Activate shortcut (Siri: "Hey Siri, Quick Capture")
2. Speak your thought
3. Shortcut transcribes and saves automatically

**Output** (File: `inbox_20251117_154530.md`):
```markdown
---
created: 2025-11-17 15:45
source: voice_capture
status: inbox
---

Interesting idea for project - create a personal knowledge graph that automatically links concepts across different domains, could help identify unexpected connections between reading notes and project ideas
```

**Notification**: "Note Captured - Added to inbox: inbox_20251117_154530.md"

### **Scenario 2**: Capturing Meeting Insight

**Input** (Voice):
> "Sarah mentioned that their team uses Notion but struggles with it - pain point is that it's too flexible and people organize things inconsistently, potential sales angle"

**Output** (File: `inbox_20251117_160215.md`):
```markdown
---
created: 2025-11-17 16:02
source: voice_capture
status: inbox
---

Sarah mentioned that their team uses Notion but struggles with it - pain point is that it's too flexible and people organize things inconsistently, potential sales angle
```

---

## Why This Is Tier 0

This shortcut demonstrates **Tier 0** characteristics:

1. **Simple Linear Flow**: Voice → transcribe → timestamp → save
2. **No Intelligence**: Doesn't categorize, tag, or understand content
3. **No Organization**: Everything goes to one inbox folder
4. **No Context Awareness**: Doesn't know if this is a task, idea, meeting note, or reference
5. **Manual Processing Required**: User must later review inbox and organize notes

**Contrast with Higher Tiers**:
- **Tier 1** would automatically file by date folders and trigger daily review workflow
- **Tier 2** would use LLM to categorize by PARA (Projects/Areas/Resources/Archive) and suggest tags
- **Tier 3** would find related notes in vault and create automatic backlinks
- **Tier 4** would have specialized agents for different note types (meeting notes vs ideas vs tasks)

---

## Testing Checklist

- [ ] Shortcut captures voice input correctly
- [ ] Transcription is accurate
- [ ] Frontmatter metadata is properly formatted
- [ ] File is saved to Obsidian inbox folder
- [ ] Filename includes unique timestamp
- [ ] Notification confirms capture
- [ ] Multiple captures create separate files (no overwriting)
- [ ] Works via Siri voice command
- [ ] Works from Home Screen widget
- [ ] Works from Lock Screen widget (iOS 16+)

---

## Variations & Extensions

### **Variation 1**: Add Source Context
- Add "Ask for Input" action to capture context (e.g., "Meeting", "Book", "Podcast")
- Include in frontmatter: `source: voice_capture | [context]`
- Still Tier 0 because it's manual selection

### **Variation 2**: Append vs. New File
- Replace "Save File" with "Append to File"
- All captures go to single `daily_inbox.md` file
- Benefit: One place to review all captures

### **Variation 3**: Add Tags Prompt
- Add "Ask for Input" to manually type tags
- Include in frontmatter: `tags: [#tag1, #tag2]`
- Still Tier 0 because tags are manually entered

---

## Common Issues & Solutions

**Issue**: Transcription is inaccurate
- **Solution**: Speak clearly and pause between sentences; iOS dictation improves over time

**Issue**: File not appearing in Obsidian
- **Solution**: Check that Obsidian vault path is correct; try opening Obsidian app to force sync

**Issue**: Frontmatter formatting breaks
- **Solution**: Ensure the Text action uses proper YAML format with `---` delimiters

**Issue**: Running out of inbox files
- **Solution**: Set up daily review habit to process and clear inbox

---

## Integration with Obsidian Workflow

### Manual Processing (Tier 0):
1. Open Obsidian vault
2. Navigate to `00_Inbox/` folder
3. Review each captured note
4. Manually determine category (Project/Area/Resource/Archive)
5. Move to appropriate folder
6. Add relevant tags and links
7. Delete inbox file

### Typical Processing Time:
- 10-20 captures per day = 15-30 minutes of manual organization

---

## Next Steps: Moving to Tier 1

To upgrade this to **Tier 1** (deterministic workflow), you could:
1. Set up n8n workflow that runs daily at 6pm
2. Automatically creates a review note with all inbox items
3. Organizes inbox files by date into folders
4. Sends reminder notification to process inbox
5. Archives processed items after 7 days

To upgrade to **Tier 2** (context-aware), you could:
1. Pass note content to Claude API
2. Automatically categorize by PARA method
3. Extract key concepts and suggest tags
4. Move note to appropriate folder
5. Still requires human review of suggestions

See `tier_1_toy_n8n_br2_daily_review.json` and `tier_2_toy_n8n_br2_inbox_triage.json` for automation patterns.

---

## Advanced: Multi-Format Capture

This Tier 0 shortcut can be extended to capture multiple formats while staying in Tier 0:

**Photo Capture Variant**:
- Action 1: Take Photo
- Action 2: Save to `00_Inbox/attachments/`
- Action 3: Create note with `![[image.jpg]]` link
- Still Tier 0: No processing, just capture

**Web Clipper Variant**:
- Action 1: Get URLs from Input (Share Sheet)
- Action 2: Get contents of URL
- Action 3: Convert to Markdown
- Action 4: Save to inbox
- Still Tier 0: Direct save, no analysis

**Combined Variant**:
- Menu to choose: Voice / Photo / Web Link / Text
- Each option runs simple capture flow
- All saved to inbox for later manual processing
