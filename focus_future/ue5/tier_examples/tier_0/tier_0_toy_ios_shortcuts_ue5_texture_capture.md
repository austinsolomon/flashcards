# UE5 - Tier 0 - Texture Reference Capture via iOS Shortcut

**What It Does**: Captures a photo of a real-world texture or screenshot from the web and saves it to a reference library folder with a timestamp. Simple, direct capture with no automation logic.

**Tier Characteristics**:
- **Direct trigger**: Camera/photo input triggers single save action
- **No processing**: Image saved as-is, no analysis or tagging
- **One action**: Immediate save to designated folder
- **No organization logic**: Files are saved chronologically, manual organization needed later

---

## Setup Steps

1. **Open iOS Shortcuts app** on your iPhone/iPad
2. **Create new Shortcut** and name it "Texture Ref Capture"
3. **Add actions** as detailed below
4. **Add to Home Screen or Share Sheet** for quick access
5. **Set up your asset library folder** (iCloud Drive, Dropbox, or local Files)

---

## Shortcut Actions

### Action 1: Take Photo (or Select Photo)
- **Type**: Take Photo / Select Photos
- **Configuration**:
  - Option 1: "Take Photo" - Opens camera immediately
  - Option 2: "Select Photos" - Choose from library or web screenshots
  - Show Camera Preview: YES
- **Purpose**: Capture the texture image
- **Example Input**: Photo of brick wall, wood grain, metal surface, or screenshot of texture from ArtStation

### Action 2: Get Current Date
- **Type**: Date
- **Configuration**:
  - Date: Current Date
  - Format: Custom → "yyyyMMdd_HHmmss" (e.g., 20251117_154530)
- **Purpose**: Create unique timestamp for filename

### Action 3: Rename File
- **Type**: Rename
- **Configuration**:
  - Rename: Selected Photo
  - Name: `texture_ref_[Current Date].jpg`
  - Example output: `texture_ref_20251117_154530.jpg`
  - If File Exists: Make Unique (adds number)
- **Purpose**: Create descriptive, unique filename

### Action 4: Save to Folder
- **Type**: Save File
- **Configuration**:
  - File: Renamed File
  - Destination: iCloud Drive/UnrealProjects/TextureReferences/
  - Ask Where to Save: NO (for faster workflow)
  - Overwrite if File Exists: NO
- **Purpose**: Store in centralized reference library

### Action 5: Show Notification
- **Type**: Show Notification
- **Configuration**:
  - Title: "Texture Saved"
  - Body: "Added to Texture References: [Renamed File Name]"
- **Purpose**: Confirm successful save

---

## Example Usage

### **Scenario 1**: Capturing Real-World Texture

**Input**: Take photo of weathered concrete wall while walking around city

**Process**:
1. Tap "Texture Ref Capture" shortcut
2. Camera opens automatically
3. Take photo of concrete texture
4. Photo is saved as `texture_ref_20251117_154530.jpg`
5. Notification confirms save

**Output**:
- File saved to `iCloud Drive/UnrealProjects/TextureReferences/texture_ref_20251117_154530.jpg`
- Notification: "Texture Saved - Added to Texture References: texture_ref_20251117_154530.jpg"

### **Scenario 2**: Saving Web Screenshot

**Input**: Screenshot of interesting wood grain texture from Pinterest

**Process**:
1. Take screenshot on phone
2. Open screenshot and tap "Share"
3. Select "Texture Ref Capture" from Share Sheet
4. Screenshot is renamed and saved
5. Notification confirms save

**Output**:
- File saved with timestamp
- Ready for import to Unreal Engine later

---

## Why This Is Tier 0

This shortcut demonstrates **Tier 0** characteristics:

1. **Simple One-Action Flow**: Capture → timestamp → save
2. **No Intelligence**: Doesn't analyze texture quality, type, or categorize
3. **No Context**: All textures saved to same folder regardless of type (metal, wood, concrete)
4. **No Automation**: User must manually organize, tag, or import later
5. **No Processing**: Image saved exactly as captured, no optimization or format conversion

**Contrast with Higher Tiers**:
- **Tier 1** would automatically organize by date folders or trigger a sync workflow
- **Tier 2** would use AI vision to auto-tag texture type (wood, metal, fabric) and quality
- **Tier 3** would analyze the texture and suggest similar procedural materials in Unreal
- **Tier 4** would automatically import, create material, and apply to test mesh

---

## Testing Checklist

- [ ] Shortcut captures/selects photos correctly
- [ ] Timestamp is added to filename in correct format
- [ ] File is saved to designated folder
- [ ] Notification confirms save with filename
- [ ] Multiple captures don't overwrite (unique filenames)
- [ ] Works from Home Screen widget
- [ ] Works from Share Sheet with existing photos
- [ ] Works with screenshots from web

---

## Variations & Extensions

### **Variation 1**: Add Quick Note
- Add "Ask for Input" action to capture description (e.g., "rusty metal panel from warehouse")
- Save description as separate .txt file with same timestamp
- Still Tier 0 because it's manual input, no automation

### **Variation 2**: Immediate Upload to Cloud
- Replace local save with upload to Dropbox/Google Drive
- Benefit: Accessible from desktop Unreal Engine immediately

### **Variation 3**: Add to Photo Album
- Add "Add to Album" action to create iOS album "Texture References"
- Benefit: Easy browsing on device, keeps originals

---

## Common Issues & Solutions

**Issue**: Files saving to wrong location
- **Solution**: In "Save File" action, manually browse and select correct folder, then disable "Ask Where to Save"

**Issue**: Filename format not working
- **Solution**: Check date format string, ensure it's `yyyyMMdd_HHmmss` with no spaces

**Issue**: Running out of iCloud storage
- **Solution**: Periodically transfer to desktop and clear mobile folder

**Issue**: Photos too large for quick sync
- **Solution**: Add "Resize Image" action before save (e.g., 2048x2048 max)

---

## Integration with Unreal Engine

### Manual Import Process (Tier 0):
1. On desktop, open `iCloud Drive/UnrealProjects/TextureReferences/`
2. Review captured textures
3. Manually import selected textures to Unreal project
4. Create materials from textures
5. Delete or archive processed references

### Upgrade Path to Higher Tiers:

**Tier 1**: n8n workflow watches folder, auto-imports new textures to Unreal project folder

**Tier 2**: n8n + AI tags texture type, auto-creates material category folders

**Tier 3**: LangChain agent analyzes texture, finds similar procedural alternatives in Unreal Marketplace

**Tier 4**: LangGraph system creates complete material graph with roughness/normal/AO maps

---

## Next Steps: Moving to Tier 1

To upgrade this to **Tier 1** (deterministic workflow), you could:
1. Set up n8n workflow that monitors the texture folder
2. Automatically organize textures into subfolders by date
3. Create backup copies to external storage
4. Generate thumbnail previews for quick browsing
5. Sync to desktop Unreal project folder automatically

See `tier_1_toy_n8n_ue5_backup.json` for workflow automation patterns.
