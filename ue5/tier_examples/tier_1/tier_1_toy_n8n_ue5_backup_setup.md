# UE5 - Tier 1 - Project Backup Automation (n8n)

**What It Does**: Every night at midnight, checks if Unreal Engine project files have changed. If yes, creates a compressed archive and uploads to cloud storage. If no changes, skips backup and logs. This is a deterministic workflow with simple conditional logic.

**Tier Characteristics**:
- **Scheduled trigger**: Runs daily at midnight automatically
- **Simple conditional logic**: If files changed → backup, else → skip (deterministic decision)
- **No AI/LLM**: Uses file timestamps and simple comparisons only
- **Predictable workflow**: Same steps every night, predictable branching
- **Multi-step automation**: Check → compress → upload → log

---

## Workflow Overview

```
┌──────────────────────────────┐
│  Schedule: Midnight Daily    │ ← TIER 1: Time-based trigger
└──────────┬───────────────────┘
           │
           v
    ┌─────────────────┐
    │ Check Changed   │ ← TIER 1: Deterministic file check
    │ Files           │
    └────────┬────────┘
             │
             v
    ┌─────────────────┐
    │ Evaluate Need   │ ← TIER 1: Simple comparison (changed > 0?)
    └────────┬────────┘
             │
             v
    ┌─────────────────┐
    │ If Changed?     │ ← TIER 1: Boolean condition
    └────┬───────┬────┘
         │       │
      YES│       │NO
         │       │
         v       v
   ┌─────────┐  ┌────────────┐
   │ Zip     │  │ Log Skip   │
   │ Project │  └────────────┘
   └────┬────┘
        │
        ├────────┐
        │        │
        v        v
   ┌──────┐  ┌──────┐
   │ Get  │  │Upload│
   │ Info │  │Cloud │
   └───┬──┘  └───┬──┘
       │         │
       └────┬────┘
            v
     ┌────────────┐
     │ Log Done   │
     └──────┬─────┘
            v
     ┌────────────┐
     │Update Mark │
     └────────────┘
```

---

## Node Configuration

### **Node 1: Schedule Trigger**
- **Type**: Schedule Trigger
- **Configuration**:
  - Cron Expression: `0 0 * * *` (midnight every day)
  - Timezone: Your local timezone
- **Input**: None
- **Output**: Execution timestamp
- **Tier 1 Characteristic**: Runs automatically on schedule

### **Node 2: Check for Changed Files**
- **Type**: Execute Command
- **Command**:
  ```bash
  find {{$env.UE5_PROJECT_PATH}} -type f -newer {{$env.LAST_BACKUP_MARKER}} | wc -l
  ```
- **Input**: Trigger timestamp
- **Output**: Count of files modified since last backup
- **Example Output**:
  ```json
  {
    "stdout": "47",
    "stderr": "",
    "code": 0
  }
  ```
- **Tier 1 Characteristic**: Deterministic file comparison using timestamps

### **Node 3: Evaluate Backup Need**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  const changedFiles = parseInt($input.first().json.stdout) || 0;
  const shouldBackup = changedFiles > 0;

  return [{
    json: {
      changedFiles,
      shouldBackup,
      timestamp: new Date().toISOString()
    }
  }];
  ```
- **Input**: File change count
- **Output**: Backup decision
- **Example Output**:
  ```json
  {
    "changedFiles": 47,
    "shouldBackup": true,
    "timestamp": "2025-11-17T00:00:15.000Z"
  }
  ```
- **Tier 1 Characteristic**: Simple comparison logic, no AI

### **Node 4: If Files Changed**
- **Type**: IF (Conditional)
- **Condition**: `shouldBackup === true`
- **Input**: Backup decision
- **Output**: Routes to backup path or skip path
- **Tier 1 Characteristic**: Deterministic boolean branching

### **Node 5A: Create Zip Archive** (TRUE path)
- **Type**: Execute Command
- **Command**:
  ```bash
  cd {{$env.UE5_PROJECT_PATH}} && tar -czf /tmp/ue5_backup_{{$now.toFormat('yyyyMMdd_HHmmss')}}.tar.gz .
  ```
- **Input**: Backup decision (true)
- **Output**: Compressed archive file
- **Example Output**:
  ```json
  {
    "stdout": "",
    "stderr": "",
    "code": 0
  }
  ```
- **Example Filename**: `/tmp/ue5_backup_20251117_000030.tar.gz`
- **Tier 1 Characteristic**: Deterministic compression command

### **Node 6: Get Archive Info**
- **Type**: Execute Command
- **Command**:
  ```bash
  ls -lh /tmp/ue5_backup_*.tar.gz | tail -1
  ```
- **Input**: Zip completion
- **Output**: Archive file metadata
- **Example Output**:
  ```json
  {
    "stdout": "-rw-r--r-- 1 user user 2.3G Nov 17 00:02 /tmp/ue5_backup_20251117_000030.tar.gz"
  }
  ```
- **Tier 1 Characteristic**: Extract file metadata for logging

### **Node 7: Upload to Cloud Storage**
- **Type**: HTTP Request
- **Configuration**:
  - Method: POST
  - URL: `{{$env.CLOUD_STORAGE_URL}}/upload`
  - Authentication: HTTP Header Auth
  - Body: File binary data
  - Path: `/ue5_backups/`
- **Input**: Archive file
- **Output**: Upload confirmation
- **Example Output**:
  ```json
  {
    "success": true,
    "url": "https://storage.cloud.com/ue5_backups/ue5_backup_20251117_000030.tar.gz",
    "size": 2417483648
  }
  ```
- **Tier 1 Characteristic**: Deterministic upload to cloud

### **Node 8: Log Backup Completion**
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  const archiveInfo = $('Get Archive Info').first().json.stdout;
  const timestamp = new Date().toISOString();

  const logEntry = {
    timestamp,
    workflow: 'ue5_project_backup',
    status: 'completed',
    archiveInfo,
    uploaded: true
  };

  const fs = require('fs');
  const logPath = process.env.BACKUP_LOG_PATH || '/var/log/ue5_backup.log';
  fs.appendFileSync(logPath, JSON.stringify(logEntry) + '\n');

  return [{ json: logEntry }];
  ```
- **Input**: Archive info + upload confirmation
- **Output**: Log entry
- **Tier 1 Characteristic**: Deterministic logging

### **Node 9: Update Backup Marker**
- **Type**: Execute Command
- **Command**:
  ```bash
  touch {{$env.LAST_BACKUP_MARKER}}
  ```
- **Input**: Log completion
- **Output**: Updated marker file timestamp
- **Purpose**: Sets reference point for next backup check
- **Tier 1 Characteristic**: Simple timestamp update

### **Node 5B: Log Backup Skipped** (FALSE path)
- **Type**: Code (JavaScript)
- **Logic**:
  ```javascript
  const logEntry = {
    timestamp: new Date().toISOString(),
    workflow: 'ue5_project_backup',
    status: 'skipped',
    reason: 'no_changes_detected'
  };

  console.log('Backup skipped:', logEntry);
  return [{ json: logEntry }];
  ```
- **Input**: Backup decision (false)
- **Output**: Skip log entry
- **Tier 1 Characteristic**: Log when no action taken

---

## Setup Instructions

### **1. Import Workflow**

1. Open n8n instance
2. Import `tier_1_toy_n8n_ue5_backup.json`
3. Workflow loads with all nodes

### **2. Configure Environment Variables**

```bash
# Unreal Engine Project Path
UE5_PROJECT_PATH=/home/user/UnrealProjects/MyGame

# Backup Marker File (timestamp reference)
LAST_BACKUP_MARKER=/tmp/ue5_last_backup.marker

# Cloud Storage API
CLOUD_STORAGE_URL=https://api.dropbox.com/2/files
# OR
CLOUD_STORAGE_URL=https://storage.googleapis.com/upload/storage/v1/b/my-bucket

# Backup Log Path
BACKUP_LOG_PATH=/var/log/ue5_backup.log
```

### **3. Create Initial Marker File**

```bash
touch /tmp/ue5_last_backup.marker
```

This establishes the baseline timestamp for the first backup check.

### **4. Set Up Cloud Storage Credentials**

**For Dropbox**:
- Add **HTTP Header Auth** credential
- Header Name: `Authorization`
- Header Value: `Bearer YOUR_DROPBOX_TOKEN`

**For Google Cloud Storage**:
- Add **OAuth2** credential
- Or use service account JSON key

### **5. Test Workflow**

**Manual Test**:
1. Click **Execute Workflow**
2. Watch nodes execute
3. Verify archive created in `/tmp/`
4. Verify upload to cloud
5. Check log file

**Check First Run**:
```bash
# Should create full backup on first run (all files are "new")
ls -lh /tmp/ue5_backup_*.tar.gz

# Check log
tail -f /var/log/ue5_backup.log
```

### **6. Enable Workflow**

1. Toggle workflow to **Active**
2. Runs automatically at midnight every day

---

## Example Data Flow

### **Scenario 1: Files Have Changed**

**Input** (Midnight trigger):
```
Timestamp: 2025-11-17 00:00:00
```

**Node 2 Output** (Check Changed):
```json
{
  "stdout": "47",
  "stderr": "",
  "code": 0
}
```
*47 files modified since last backup*

**Node 3 Output** (Evaluate):
```json
{
  "changedFiles": 47,
  "shouldBackup": true,
  "timestamp": "2025-11-17T00:00:15.000Z"
}
```

**Node 4**: Routes to TRUE path (backup)

**Node 5A Output** (Zip):
```
Archive created: /tmp/ue5_backup_20251117_000030.tar.gz
```

**Node 6 Output** (Archive Info):
```json
{
  "stdout": "-rw-r--r-- 1 user user 2.3G Nov 17 00:02 /tmp/ue5_backup_20251117_000030.tar.gz"
}
```

**Node 7 Output** (Upload):
```json
{
  "success": true,
  "url": "https://storage.cloud.com/ue5_backups/ue5_backup_20251117_000030.tar.gz"
}
```

**Node 8 Output** (Log):
```json
{
  "timestamp": "2025-11-17T00:02:45.000Z",
  "workflow": "ue5_project_backup",
  "status": "completed",
  "archiveInfo": "-rw-r--r-- 1 user user 2.3G Nov 17 00:02 /tmp/ue5_backup_20251117_000030.tar.gz",
  "uploaded": true
}
```

**Log File**:
```
{"timestamp":"2025-11-17T00:02:45.000Z","workflow":"ue5_project_backup","status":"completed","archiveInfo":"-rw-r--r-- 1 user user 2.3G Nov 17 00:02 /tmp/ue5_backup_20251117_000030.tar.gz","uploaded":true}
```

### **Scenario 2: No Changes Detected**

**Node 2 Output** (Check Changed):
```json
{
  "stdout": "0",
  "stderr": "",
  "code": 0
}
```

**Node 3 Output** (Evaluate):
```json
{
  "changedFiles": 0,
  "shouldBackup": false,
  "timestamp": "2025-11-18T00:00:10.000Z"
}
```

**Node 4**: Routes to FALSE path (skip)

**Node 5B Output** (Skip Log):
```json
{
  "timestamp": "2025-11-18T00:00:12.000Z",
  "workflow": "ue5_project_backup",
  "status": "skipped",
  "reason": "no_changes_detected"
}
```

**Log Output**:
```
Backup skipped: {timestamp: "2025-11-18T00:00:12.000Z", workflow: "ue5_project_backup", status: "skipped", reason: "no_changes_detected"}
```

---

## Why This Is Tier 1

This workflow demonstrates **Tier 1** characteristics:

1. **Scheduled Automation**: Runs at fixed time every day
2. **Deterministic Logic**: Simple if/then based on file count
3. **No AI/LLM**: Uses file timestamps and shell commands only
4. **Predictable Branching**: Always same two paths (backup or skip)
5. **Multi-Step Workflow**: Check → decide → execute → log
6. **Simple Conditions**: Boolean comparisons, no complex decision-making

**Contrast with Other Tiers**:
- **Tier 0**: Would require manual triggering and file selection
- **Tier 2**: Would use AI to analyze which files are important to backup (code vs temp files)
- **Tier 3**: Would have agent decide optimal backup strategy based on project size and cloud costs
- **Tier 4**: Would have agents for backup, verification, retention policy, and restoration testing

---

## Troubleshooting

**Issue**: Backup runs every night even with no changes
- **Solution**: Verify `LAST_BACKUP_MARKER` path is correct and writable
- **Solution**: Check that "Update Backup Marker" node is executing successfully

**Issue**: Archive is too large for cloud storage
- **Solution**: Exclude build artifacts: `tar -czf ... --exclude='Binaries' --exclude='Intermediate'`
- **Solution**: Use cloud storage with sufficient space

**Issue**: Upload fails with timeout
- **Solution**: Increase timeout in HTTP Request node
- **Solution**: Split large projects into multiple archives

**Issue**: Marker file gets deleted
- **Solution**: Move marker to persistent location (not `/tmp/`)
- **Solution**: Use `/var/lib/n8n/ue5_backup.marker`

---

## Customization (Still Tier 1)

### **Exclude Build Artifacts**:
```bash
tar -czf ... --exclude='Binaries' --exclude='Intermediate' --exclude='Saved' --exclude='DerivedDataCache'
```

### **Retention Policy**:
Add node to delete backups older than 30 days:
```bash
find /cloud/backups/ -name "ue5_backup_*.tar.gz" -mtime +30 -delete
```

### **Multiple Projects**:
Duplicate workflow for each project, change `UE5_PROJECT_PATH`

### **Email Notification**:
Add email node after logging to notify on completion/errors

---

## Next Steps: Moving to Tier 2

To upgrade to **Tier 2** (context-aware), you could:
1. Add LLM call to analyze changed files
2. Intelligently decide what to backup (skip temp files, prioritize source code)
3. Generate backup summary: "Backed up 47 files including 12 Blueprint changes and 8 new textures"
4. Provide recommendations: "Large asset added (500MB), consider Perforce LFS"

See `tier_2_toy_n8n_ue5_asset_tagger.json` for AI-powered asset management.
