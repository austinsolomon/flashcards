# UE5 - Tier 2 - Asset Quality Tagger (n8n + ChatGPT Vision)

**What It Does**: When a new asset file is added to the watch folder, automatically analyzes it using ChatGPT Vision API (for images) or heuristics (for 3D models), tags with quality rating (HIGH/MEDIUM/LOW), writes metadata file, and alerts team if low quality. This is a context-aware workflow with ONE AI call adding semantic visual understanding.

**Tier Characteristics**:
- **Event-based trigger**: Responds to new files (not scheduled)
- **ONE Vision AI call**: ChatGPT analyzes image quality - semantic understanding of visuals
- **Semantic assessment**: Understands visual quality, not just file size
- **Automated metadata**: Creates .metadata.json for UE5 import pipeline
- **Context-aware routing**: Alerts team only for low-quality assets

---

## Workflow Overview

```
┌─────────────────────────────┐
│ File Watcher: New Asset     │ ← TIER 2: Event-based file trigger
└──────────┬──────────────────┘
           │
           v
    ┌─────────────────┐
    │ Extract Asset   │ ← TIER 2: Prepare file metadata
    │ Metadata        │
    └──────┬──────────┘
           │
           v
    ┌──────────────────┐
    │ Branch: Image    │ ← TIER 2: Route by file type
    │ or 3D Asset?     │
    └─────┬────────────┘
          │
      ┌───┴───────────────┐
      │                   │
      v                   v
┌──────────┐      ┌──────────────┐
│ Read     │      │ Analyze 3D   │
│ Image    │      │ Asset        │
│ File     │      │ (Heuristic)  │
└────┬─────┘      └──────┬───────┘
     │                   │
     v                   │
┌────────────────────┐   │
│ Call ChatGPT       │   │ ← TIER 2 KEY: Vision AI
│ Vision API         │   │   analyzes visual quality
└────┬───────────────┘   │
     │                   │
     v                   │
┌────────────┐           │
│ Parse      │           │
│ Vision     │           │
│ Analysis   │           │
└────┬───────┘           │
     │                   │
     └─────┬─────────────┘
           │
           v
    ┌──────────────┐
    │ Merge        │
    │ Analysis     │
    └──────┬───────┘
           │
           v
    ┌──────────────┐
    │ Write Asset  │ ← TIER 2: Create metadata file
    │ Metadata     │
    └──────┬───────┘
           │
           v
    ┌──────────────────┐
    │ Check if         │ ← TIER 2: Conditional on AI result
    │ Low Quality?     │
    └─────┬────────────┘
          │
     ┌────┴────┐
     │         │
     v         v
 ┌─────┐   ┌─────┐
 │Alert│   │ Log │
 └─────┘   └─────┘
```

---

## Node Configuration

### **Node 1: File Watcher - New Asset**
- **Type**: Local File Trigger
- **Configuration**:
  - Watch Path: `{{$env.UE5_ASSET_WATCH_PATH}}`
  - Event: `add` (new files only)
  - File Filters: `*.png,*.jpg,*.jpeg,*.fbx,*.uasset`
- **Input**: None (file system event)
- **Output**: File path and basic info
- **Example Output**:
  ```json
  {
    "path": "/home/user/ue5_assets/character_concept_001.png",
    "event": "add",
    "timestamp": "2025-11-17T14:30:00Z"
  }
  ```
- **Tier 2 Characteristic**: Event-driven trigger (responds to file system events)

### **Node 2: Extract Asset Metadata**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  const filePath = $input.first().json.path;
  const fs = require('fs');
  const path = require('path');

  const fileStats = fs.statSync(filePath);
  const fileName = path.basename(filePath);
  const fileExt = path.extname(filePath);

  // Determine if it's an image or 3D asset
  const isImage = ['.png', '.jpg', '.jpeg'].includes(fileExt.toLowerCase());
  const is3DAsset = ['.fbx', '.uasset'].includes(fileExt.toLowerCase());

  return [{
    json: {
      filePath,
      fileName,
      fileExt,
      fileSize: fileStats.size,
      isImage,
      is3DAsset,
      createdAt: fileStats.birthtime.toISOString()
    }
  }];
  ```
- **Input**: File path from trigger
- **Output**: Structured file metadata
- **Tier 2 Characteristic**: Preprocessing before AI call

### **Node 3: Branch - Image or 3D Asset**
- **Type**: IF (Conditional)
- **Configuration**:
  - Condition: `{{$json.isImage}} equals true`
- **Input**: Asset metadata
- **Output**: Routes to image analysis OR 3D analysis
- **Tier 2 Characteristic**: Deterministic routing by file type

### **Node 4: Read Image File**
- **Type**: Read Binary File
- **Configuration**:
  - File Path: `{{$('Extract Asset Metadata').first().json.filePath}}`
  - Encoding: `base64`
- **Input**: File path
- **Output**: Base64-encoded image data
- **Tier 2 Characteristic**: Load image for vision AI

### **Node 5: Call ChatGPT Vision API - Analyze Image**
- **Type**: HTTP Request
- **Configuration**:
  - Method: POST
  - URL: `https://api.openai.com/v1/chat/completions`
  - Authentication: HTTP Header Auth
    - Header: `Authorization`
    - Value: `Bearer {{$env.OPENAI_API_KEY}}`
  - Body (JSON):
  ```json
  {
    "model": "gpt-4o",
    "max_tokens": 300,
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Analyze this UE5 game asset image. Rate the quality (LOW, MEDIUM, HIGH) and provide 2-3 word tags. Respond in JSON format: {\"quality\": \"HIGH|MEDIUM|LOW\", \"tags\": [\"tag1\", \"tag2\"], \"notes\": \"brief description\"}"
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "data:image/jpeg;base64,{{IMAGE_BASE64}}"
            }
          }
        ]
      }
    ]
  }
  ```
- **Input**: Base64 image data
- **Output**: ChatGPT vision analysis
- **Example Output**:
  ```json
  {
    "choices": [
      {
        "message": {
          "content": "{\"quality\": \"HIGH\", \"tags\": [\"character\", \"detailed\", \"professional\"], \"notes\": \"Well-rendered character concept with good lighting and detail. Production-ready quality.\"}"
        }
      }
    ],
    "usage": {
      "prompt_tokens": 1250,
      "completion_tokens": 45
    }
  }
  ```
- **Tier 2 Characteristic**: ONE Vision AI call adds semantic understanding of image quality - this is the key tier-defining element

### **Node 6: Analyze 3D Asset (Heuristic)**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  const metadata = $('Extract Asset Metadata').first().json;
  const fileName = metadata.fileName;
  const fileSize = metadata.fileSize;

  // Heuristic-based quality assessment
  let quality = 'MEDIUM';
  let tags = [];
  let notes = '';

  // File size heuristics
  if (fileSize > 50 * 1024 * 1024) {
    quality = 'HIGH';
    tags.push('high-poly');
    notes = 'Large file suggests detailed model';
  } else if (fileSize < 5 * 1024 * 1024) {
    quality = 'LOW';
    tags.push('low-poly');
    notes = 'Small file suggests simple model';
  } else {
    tags.push('medium-poly');
    notes = 'Moderate complexity';
  }

  // Extract tags from filename
  if (fileName.toLowerCase().includes('character')) tags.push('character');
  if (fileName.toLowerCase().includes('prop')) tags.push('prop');
  if (fileName.toLowerCase().includes('environment')) tags.push('environment');

  return [{
    json: {
      quality,
      tags,
      notes,
      analysis_type: 'heuristic'
    }
  }];
  ```
- **Input**: Asset metadata
- **Output**: Quality assessment (rule-based)
- **Tier 2 Characteristic**: Fallback for non-image files (no vision AI available)

### **Node 7: Parse Vision Analysis**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  const visionResponse = $input.first().json;
  const aiContent = visionResponse.choices[0].message.content;

  let analysis;
  try {
    analysis = JSON.parse(aiContent);
  } catch (err) {
    analysis = {
      quality: 'MEDIUM',
      tags: ['unclassified'],
      notes: 'Failed to parse AI response'
    };
  }

  return [{
    json: {
      quality: analysis.quality || 'MEDIUM',
      tags: analysis.tags || [],
      notes: analysis.notes || '',
      analysis_type: 'vision_ai'
    }
  }];
  ```
- **Input**: ChatGPT vision response
- **Output**: Structured quality data
- **Tier 2 Characteristic**: Extract structured data from AI response

### **Node 8: Merge Analysis Results**
- **Type**: Merge
- **Configuration**: Combine both analysis paths
- **Input**: Vision AI result OR heuristic result
- **Output**: Unified quality assessment
- **Tier 2 Characteristic**: Combine parallel processing paths

### **Node 9: Write Asset Metadata**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  const metadata = $('Extract Asset Metadata').first().json;
  const analysis = $input.first().json;

  const assetMetadata = {
    file: {
      name: metadata.fileName,
      path: metadata.filePath,
      size: metadata.fileSize,
      type: metadata.fileExt,
      created: metadata.createdAt
    },
    quality: {
      rating: analysis.quality,
      tags: analysis.tags,
      notes: analysis.notes,
      analyzedBy: analysis.analysis_type,
      analyzedAt: new Date().toISOString()
    },
    unreal: {
      recommended_folder: analysis.quality === 'HIGH' ? 'Assets/Production' :
                         analysis.quality === 'MEDIUM' ? 'Assets/WIP' :
                         'Assets/Drafts',
      import_priority: analysis.quality === 'HIGH' ? 1 :
                       analysis.quality === 'MEDIUM' ? 2 : 3
    }
  };

  const fs = require('fs');
  const metadataPath = metadata.filePath.replace(metadata.fileExt, '.metadata.json');
  fs.writeFileSync(metadataPath, JSON.stringify(assetMetadata, null, 2));

  return [{ json: { ...assetMetadata, metadataPath } }];
  ```
- **Input**: Analysis results
- **Output**: Metadata file written + data object
- **Example Output File** (`character_concept_001.metadata.json`):
  ```json
  {
    "file": {
      "name": "character_concept_001.png",
      "path": "/home/user/ue5_assets/character_concept_001.png",
      "size": 2458624,
      "type": ".png",
      "created": "2025-11-17T14:30:00Z"
    },
    "quality": {
      "rating": "HIGH",
      "tags": ["character", "detailed", "professional"],
      "notes": "Well-rendered character concept with good lighting and detail",
      "analyzedBy": "vision_ai",
      "analyzedAt": "2025-11-17T14:30:15Z"
    },
    "unreal": {
      "recommended_folder": "Assets/Production",
      "import_priority": 1
    }
  }
  ```
- **Tier 2 Characteristic**: Automated metadata creation for downstream use

### **Node 10: Check if Low Quality**
- **Type**: IF (Conditional)
- **Configuration**:
  - Condition: `{{$json.quality.rating}} equals LOW`
- **Input**: Asset metadata with quality rating
- **Output**: Routes to alert OR directly to log
- **Tier 2 Characteristic**: Context-aware routing based on AI assessment

### **Node 11: Alert - Low Quality Asset**
- **Type**: HTTP Request (Slack Webhook)
- **Configuration**:
  - URL: `{{$env.SLACK_WEBHOOK_URL}}`
  - Body:
  ```json
  {
    "text": "⚠️ Low quality asset detected",
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "*Low Quality Asset Alert*\n\nFile: `{{fileName}}`\nQuality: {{quality}}\nTags: {{tags}}\nNotes: {{notes}}"
        }
      }
    ]
  }
  ```
- **Input**: Low-quality asset metadata
- **Output**: Slack notification sent
- **Tier 2 Characteristic**: Context-aware notification (only for problematic assets)

### **Node 12: Log Asset Analysis**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  const assetData = $input.first().json;

  const logEntry = {
    timestamp: new Date().toISOString(),
    workflow: 'ue5_asset_tagger',
    file: assetData.file.name,
    quality: assetData.quality.rating,
    tags: assetData.quality.tags,
    alertSent: assetData.quality.rating === 'LOW'
  };

  console.log('Asset analyzed:', logEntry);

  const fs = require('fs');
  const logPath = process.env.UE5_LOG_PATH || '/tmp/ue5_assets.log';
  try {
    fs.appendFileSync(logPath, JSON.stringify(logEntry) + '\n');
  } catch (err) {
    console.error('Failed to write log:', err);
  }

  return [{ json: logEntry }];
  ```
- **Input**: Asset metadata
- **Output**: Log entry
- **Tier 2 Characteristic**: Track AI assessments for quality analytics

---

## Setup Instructions

### **1. Import Workflow to n8n**

1. Open your n8n instance
2. Click **Workflows** → **Import from File**
3. Select `tier_2_toy_n8n_ue5_asset_tagger.json`
4. Workflow will be imported with all nodes configured

### **2. Configure Environment Variables**

Add these to your n8n instance or `.env` file:

```bash
# OpenAI API for Vision Analysis
OPENAI_API_KEY=sk-proj-your-key-here

# Asset Watch Folder
UE5_ASSET_WATCH_PATH=/home/user/ue5_assets/incoming

# Slack Webhook for Alerts
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Logging (optional)
UE5_LOG_PATH=/var/log/ue5_assets.log
```

### **3. Create Asset Watch Folder**

```bash
mkdir -p /home/user/ue5_assets/incoming
chmod 755 /home/user/ue5_assets/incoming
```

### **4. Set Up Credentials**

**For OpenAI API**:
1. Navigate to **Credentials** in n8n
2. Add **HTTP Header Auth** credential
3. Header Name: `Authorization`
4. Header Value: `Bearer YOUR_OPENAI_API_KEY`
5. Add another header: `Content-Type` = `application/json`

### **5. Enable the Workflow**

1. Verify all credentials are connected
2. Toggle workflow to **Active**
3. n8n will now watch the asset folder

### **6. Test the Workflow**

**Add a Test Asset**:
1. Copy an image file to the watch folder:
   ```bash
   cp test_character.png /home/user/ue5_assets/incoming/
   ```
2. Watch n8n execution log
3. Verify vision AI analysis runs
4. Check metadata file is created: `test_character.metadata.json`

**Verify Low Quality Alert**:
1. Add a low-quality image (small, blurry, etc.)
2. Confirm Slack alert is sent
3. Check log file for entry

---

## Example Data Flow

### **Input** (New File Added):
```
File: /home/user/ue5_assets/incoming/character_hero_v3.png
Size: 3.2 MB
Type: PNG image
```

### **Node 2 Output** (Extract Metadata):
```json
{
  "filePath": "/home/user/ue5_assets/incoming/character_hero_v3.png",
  "fileName": "character_hero_v3.png",
  "fileExt": ".png",
  "fileSize": 3355443,
  "isImage": true,
  "is3DAsset": false,
  "createdAt": "2025-11-17T14:30:00Z"
}
```

### **Node 5 Output** (Vision AI Analysis):
```json
{
  "choices": [
    {
      "message": {
        "content": "{\"quality\": \"HIGH\", \"tags\": [\"character\", \"hero\", \"detailed\"], \"notes\": \"High-quality character render with excellent lighting, textures, and composition. Production-ready.\"}"
      }
    }
  ]
}
```

### **Node 9 Output** (Metadata File Created):
```json
{
  "file": {
    "name": "character_hero_v3.png",
    "path": "/home/user/ue5_assets/incoming/character_hero_v3.png",
    "size": 3355443,
    "type": ".png",
    "created": "2025-11-17T14:30:00Z"
  },
  "quality": {
    "rating": "HIGH",
    "tags": ["character", "hero", "detailed"],
    "notes": "High-quality character render with excellent lighting, textures, and composition",
    "analyzedBy": "vision_ai",
    "analyzedAt": "2025-11-17T14:30:18Z"
  },
  "unreal": {
    "recommended_folder": "Assets/Production",
    "import_priority": 1
  }
}
```

### **Final Actions**:
- Metadata file saved: `character_hero_v3.metadata.json`
- No alert sent (HIGH quality)
- Log entry created

---

## Why This Is Tier 2

This workflow demonstrates **Tier 2** characteristics:

1. **Event-Based**: Triggers on new files (not scheduled)
2. **ONE Vision AI Call**: ChatGPT analyzes image quality semantically
3. **Visual Understanding**: Assesses lighting, composition, detail (not just file size)
4. **Automated Actions**: Creates metadata, routes by quality
5. **Context-Aware**: Alerts only for low-quality assets

**Contrast with Other Tiers**:
- **Tier 1**: Would use only file size/resolution rules (no visual understanding)
- **Tier 3**: Would use a LangChain agent with tools to research asset standards, compare to style guides
- **Tier 4**: Would have ConceptAgent → TechAgent validation (artist review → tech specs validation)
- **Tier 5**: Would orchestrate human artist review and UE5 import automation
- **Tier 6**: Would autonomously learn team quality preferences and improve over time

---

## Troubleshooting

### **Issue**: File trigger doesn't detect new assets
- **Solution**: Verify `UE5_ASSET_WATCH_PATH` exists
- **Solution**: Check n8n has read permissions
- **Solution**: Test by manually copying file to folder

### **Issue**: Vision API call fails
- **Solution**: Verify `OPENAI_API_KEY` is correct
- **Solution**: Check API key has GPT-4o access
- **Solution**: Verify image is under 20MB limit

### **Issue**: Metadata file not created
- **Solution**: Check n8n has write permissions to asset folder
- **Solution**: Verify file path in error logs
- **Solution**: Test with simple console.log() first

### **Issue**: Slack alerts not sending
- **Solution**: Verify `SLACK_WEBHOOK_URL` is correct
- **Solution**: Test webhook with curl manually
- **Solution**: Check Slack app permissions

---

## Customization Ideas (Still Tier 2)

### **Add More Asset Types**:
- Support `.blend`, `.max`, `.obj` files
- Add specific analysis for each type
- Still ONE AI call per asset

### **Enhanced Quality Criteria**:
- Check for specific UE5 requirements
- Validate texture resolutions
- Verify naming conventions

### **Team Notifications**:
- Alert specific team members by asset type
- Post to dedicated Slack channels
- Include preview thumbnails

### **Quality Trends**:
- Track quality over time
- Generate weekly reports
- Identify problem areas

---

## Next Steps: Moving to Tier 3

To upgrade this to **Tier 3** (LangChain agent), you could:
1. Add tools: `search_asset_library`, `check_style_guide`, `validate_naming`
2. Let agent decide which validations to run
3. Research similar assets for comparison
4. Generate recommendations for improvement

See `tier_3_toy_langchain_ue5_tutorial_finder.py` for agent patterns.
