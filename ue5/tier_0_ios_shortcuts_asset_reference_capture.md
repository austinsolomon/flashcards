# UE5 - Tier 0: Simple Triggers - Asset Reference Capture

## Use Case
While browsing art, playing games, or out in the world, instantly capture visual references (photos, screenshots, URLs) and send them to your UE5 project's reference library with proper tagging for later use in asset creation.

## Tool Used
iOS Shortcuts

## Shortcut Configuration

### Shortcut Name
"Save Game Reference"

### Actions

1. **Receive [Sharing Sheet Input]**
   - Types: Images, URLs, Screenshots
   - Store result in: `inputItem`

2. **If [inputItem] has any value**
   - THEN: Continue
   - ELSE: Take Photo → Store in `inputItem`

3. **Ask for Input** (Choose from Menu)
   - Prompt: "Asset Category"
   - Menu Items:
     - "Environment/Architecture"
     - "Character/Creature"
     - "Props/Items"
     - "VFX/Particles"
     - "Materials/Textures"
     - "Lighting/Mood"
     - "UI/HUD"
   - Store result in: `category`

4. **Ask for Input** (Text)
   - Prompt: "Quick Tags (comma separated)"
   - Default: ""
   - Placeholder: "medieval, stone, weathered"
   - Store result in: `tags`

5. **Ask for Input** (Text)
   - Prompt: "Notes (optional)"
   - Default: ""
   - Store result in: `notes`

6. **Get Current Location**
   - Store result in: `location` (optional, for outdoor reference photos)

7. **Text Block** - Create filename
   ```
   REF_[category]_[Current Date YYYYMMDD]_[Current Time HHmmss]
   ```
   - Store result in: `filename`

8. **Save File**
   - File: `inputItem`
   - Destination: iCloud Drive/UE5_Project/References/[category]/
   - Filename: `filename`
   - Overwrite: No

9. **Text Block** - Format metadata as JSON
   ```
   {
     "filename": "[filename]",
     "category": "[category]",
     "tags": "[tags]",
     "notes": "[notes]",
     "capture_date": "[Current Date]",
     "location": "[location]",
     "source_url": "[inputItem]"
   }
   ```
   - Store result in: `metadata`

10. **Append to File**
    - File: iCloud Drive/UE5_Project/References/reference_log.jsonl
    - Text: `metadata` + newline

11. **Show Notification**
    - Title: "Reference Saved ✓"
    - Body: "[category] reference added to project"

## How to Run

### Setup
1. Create folder structure in iCloud Drive:
   ```
   iCloud Drive/
     UE5_Project/
       References/
         Environment-Architecture/
         Character-Creature/
         Props-Items/
         VFX-Particles/
         Materials-Textures/
         Lighting-Mood/
         UI-HUD/
         reference_log.jsonl
   ```

2. Create the shortcut in iOS Shortcuts app

3. **Enable Share Sheet**:
   - In shortcut settings → Details
   - Turn on "Show in Share Sheet"
   - Select types: Images, URLs, Safari Web Pages

### Invoke Methods

**Method 1: From Share Sheet**
- Viewing inspiration on Pinterest/ArtStation → Tap Share → "Save Game Reference"
- Taking photo of real-world reference → Open Photos → Share → "Save Game Reference"

**Method 2: Direct Camera Capture**
- Say "Hey Siri, Save Game Reference" → Takes photo → Asks for category/tags

**Method 3: Quick Access Widget**
- Add to Home Screen or Lock Screen widget

## Expected Output

### File System Result
```
iCloud Drive/UE5_Project/References/
  Environment-Architecture/
    REF_Environment-Architecture_20250115_142530.jpg
  Materials-Textures/
    REF_Materials-Textures_20250115_143012.png
  reference_log.jsonl (append-only log)
```

### Metadata Log Entry (reference_log.jsonl)
```json
{"filename":"REF_Materials-Textures_20250115_143012","category":"Materials/Textures","tags":"concrete, weathered, pbr, tileable","notes":"Great grunge detail for industrial level","capture_date":"2025-01-15T14:30:12Z","location":"37.7749,-122.4194","source_url":"https://www.artstation.com/artwork/abc123"}
```

### Sync to Desktop
- Files automatically sync via iCloud Drive to Mac/PC
- Reference library available in UE5 Content Browser
- Metadata searchable via `reference_log.jsonl`

### Workflow Integration
When back at workstation:
1. Open UE5 project
2. iCloud Drive sync completes
3. New references appear in `/References/` folder structure
4. Import to Content Browser with metadata intact
5. Use tags from metadata for smart collections

## Tier Classification Reasoning

This is **Tier 0** because:
1. **One-action trigger**: Share sheet or voice command activates immediately
2. **No decision-making**: Saves files and appends metadata without analysis
3. **Zero context required**: Doesn't check existing references or make smart suggestions
4. **Direct file operation**: Simple save + append operations, no workflow orchestration
5. **Mobile-optimized capture**: Designed for the moment of inspiration when you see something useful
6. **No processing**: Stores raw reference as-is, no image analysis or categorization beyond manual tags

This differs from Tier 1 (which would involve automated processing pipelines) by focusing purely on **friction-free capture** with manual categorization. The power is in speed: see something inspiring → captured in 10 seconds → back to your activity.
