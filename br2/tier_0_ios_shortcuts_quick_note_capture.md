# BR2 - Tier 0: Simple Triggers - Quick Note Capture to Inbox

## Use Case
Instantly capture fleeting thoughts, ideas, or information you encounter throughout the day and send them to your Second Brain inbox for later processing, following the PARA method's "capture everything" principle without breaking flow.

## Tool Used
iOS Shortcuts

## Shortcut Configuration

### Shortcut Name
"Quick Capture"

### Actions

1. **Ask for Input** (Text)
   - Prompt: "What's on your mind?"
   - Input Type: Text
   - Multi-line: Yes
   - Store result in: `thoughtContent`

2. **Ask for Input** (Choose from Menu)
   - Prompt: "Quick Tag (optional)"
   - Menu Items:
     - "None"
     - "💡 Idea"
     - "📚 To Learn"
     - "✅ Task"
     - "🔖 Reference"
     - "❓ Question"
     - "💭 Reflection"
   - Store result in: `tag`

3. **Get Current Location** (if permission granted)
   - Store result in: `location`

4. **If [tag] = "None"**
   - THEN: Set variable `tagPrefix` = ""
   - ELSE: Set variable `tagPrefix` = "[tag] "

5. **Text Block** - Format note with metadata
   ```
   [tagPrefix][thoughtContent]

   ---
   Captured: [Current Date] at [Current Time]
   Location: [location]
   ```
   - Store result in: `formattedNote`

6. **Text Block** - Create filename
   ```
   [Current Date YYYYMMDD]-[Current Time HHmmss]-quick-capture.md
   ```
   - Store result in: `filename`

7. **Save File**
   - File: `formattedNote`
   - Destination: iCloud Drive/Obsidian/Inbox/
   - Filename: `filename`
   - Overwrite: No

8. **Text Block** - Create JSON log entry
   ```
   {
     "timestamp": "[Current Date ISO8601]",
     "filename": "[filename]",
     "tag": "[tag]",
     "content_preview": "[thoughtContent first 50 chars]",
     "word_count": [Word Count of thoughtContent],
     "location": "[location]"
   }
   ```
   - Store result in: `logEntry`

9. **Append to File**
   - File: iCloud Drive/Obsidian/Inbox/_capture_log.jsonl
   - Text: `logEntry` + newline

10. **Show Notification**
    - Title: "💾 Captured"
    - Body: "Added to inbox for processing"
    - Sound: None (silent)

## How to Run

### Setup
1. **Create folder structure** in iCloud Drive:
   ```
   iCloud Drive/
     Obsidian/
       Inbox/
         _capture_log.jsonl
   ```

2. **Configure Obsidian vault** to sync with iCloud Drive location

3. **Create shortcut** in iOS Shortcuts app

4. **Quick access options**:
   - Add to Lock Screen widget (iOS 16+)
   - Add to Action Button (iPhone 15 Pro)
   - Create Siri phrase: "Hey Siri, Quick Capture"
   - Add to Home Screen as icon

### Invoke Methods

**Method 1: Lock Screen Widget** (fastest)
- Swipe to Lock Screen widgets → Tap "Quick Capture"

**Method 2: Action Button** (iPhone 15 Pro)
- Configure Action Button → Shortcut → "Quick Capture"
- Physical button press → Immediate capture

**Method 3: Siri Voice**
- "Hey Siri, Quick Capture"
- Dictate your thought
- Select tag
- Done

**Method 4: Share Sheet**
- Share text from any app → "Quick Capture"

## Expected Output

### File Created (Example 1)
**Filename**: `20250115-142337-quick-capture.md`

**Content**:
```markdown
💡 Idea What if we used spaced repetition for code patterns, not just facts? Create flashcards for design patterns with real implementation examples.

---
Captured: 2025-01-15 at 14:23:37
Location: Home Office
```

### File Created (Example 2)
**Filename**: `20250115-153012-quick-capture.md`

**Content**:
```markdown
📚 To Learn Look into LangGraph's StateGraph - seems perfect for the multi-agent orchestration tier. Check if it supports persistent state across sessions.

---
Captured: 2025-01-15 at 15:30:12
Location: Coffee Shop, Downtown
```

### Log Entry (_capture_log.jsonl)
```json
{"timestamp":"2025-01-15T14:23:37Z","filename":"20250115-142337-quick-capture.md","tag":"💡 Idea","content_preview":"What if we used spaced repetition for code pattern","word_count":24,"location":"37.7749,-122.4194"}
{"timestamp":"2025-01-15T15:30:12Z","filename":"20250115-153012-quick-capture.md","tag":"📚 To Learn","content_preview":"Look into LangGraph's StateGraph - seems perfect","word_count":22,"location":"37.7847,-122.4012"}
```

### Desktop Sync Result
- Files appear in Obsidian vault's Inbox folder within seconds
- Ready for later processing during daily review
- Log provides analytics on capture patterns

### Processing Workflow (Manual - happens later)
During your daily/weekly review:
1. Open Obsidian → Navigate to Inbox
2. Process each quick capture note:
   - Expand into full note if valuable
   - Move to appropriate PARA folder (Projects/Areas/Resources/Archives)
   - Delete if no longer relevant
   - Link to related notes
3. Inbox returns to zero

## Tier Classification Reasoning

This is **Tier 0** because:
1. **Single trigger, immediate capture**: One tap/voice command → thought saved
2. **Zero processing**: No AI analysis, summarization, or smart categorization
3. **No context awareness**: Doesn't check existing notes or suggest connections
4. **Manual tagging only**: User chooses tag, no automated classification
5. **Simple file operations**: Save file + append log, no workflow complexity
6. **Optimized for speed**: Designed to capture thoughts in < 10 seconds without breaking flow

This is the foundation of the PARA method's "capture everything" principle. It sits below Tier 1 (which would involve automated processing) and Tier 2 (which would add AI-powered categorization/linking).

The key insight: **Capture speed > Organization quality** at the point of capture. Organization happens later during deliberate review sessions. This prevents the "I'll remember this later" trap that loses most valuable ideas.
