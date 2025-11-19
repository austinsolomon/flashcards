# Quick Start Guide - iPhone Compliance Agent

Get up and running in 5 minutes!

## Prerequisites

- macOS with Xcode installed
- Python 3.9+
- Node.js 16+
- Anthropic API key ([get one here](https://console.anthropic.com/))

## Installation

```bash
# 1. Navigate to the project directory
cd law/iphone_compliance_agent

# 2. Run setup script (installs everything)
./setup.sh

# 3. Add your API key to .env
nano .env
# Add: ANTHROPIC_API_KEY=your_key_here
# Save and exit (Ctrl+X, Y, Enter)
```

## Running Your First Test

### Option A: Quick Demo (Recommended for MVP)

The MVP runs in "test mode" with simulated data - no emulator needed!

```bash
# Activate Python environment
source venv/bin/activate

# Run Tier 4 (automated test)
python compliance_agent.py
```

**Expected output:**
- App selection: Instagram
- 3 test flows simulated
- Dark patterns detected
- Compliance scores calculated
- Report generated in `reports/` folder

**Time**: ~30 seconds

### Option B: Full Tier 5 Workflow

```bash
# Activate Python environment
source venv/bin/activate

# Run orchestrator (includes human review)
python orchestrator.py
```

**Expected output:**
- Client intake
- Tier 4 automated testing
- Human review simulation
- Report distribution
- Follow-up scheduling

**Time**: ~60 seconds

### Option C: With Real iOS Emulator (Advanced)

For production use with live app testing:

```bash
# Terminal 1: Start Appium server
appium --allow-cors

# Terminal 2: Run test
source venv/bin/activate

# Edit compliance_agent.py line ~450
# Change TEST_MODE=true to TEST_MODE=false

python compliance_agent.py
```

**Prerequisites:**
- App installed in iOS Simulator
- iOS Simulator running
- Appium server active

## Using the Interactive Menu

```bash
# Start the interactive runner
./run.sh
```

Choose from:
1. **Tier 4** - Automated multi-agent test
2. **Tier 5** - Full orchestrated workflow
3. **Test emulator** - Verify iOS connection
4. **Python shell** - Interactive testing

## Testing Different Apps

### Built-in Apps

The MVP includes 5 pre-configured apps:

```python
# In Python shell or script
from compliance_agent import run_compliance_test

# Test Instagram (default)
run_compliance_test("Instagram")

# Test other apps
run_compliance_test("TikTok")
run_compliance_test("Candy Crush")
run_compliance_test("DoorDash")
run_compliance_test("Robinhood")
```

### Adding Your Own App

Edit `config/compliance_standards.yaml`:

```yaml
popular_test_apps:
  - name: "MyApp"
    bundle_id: "com.company.myapp"
    category: "Your Category"
    known_concerns:
      - "Concern 1"
      - "Concern 2"
```

Then test:

```python
run_compliance_test("MyApp")
```

## Understanding the Output

### Console Output

```
🎯 APP SELECTOR AGENT
✅ Selected: Instagram

🧭 NAVIGATION AGENT
✅ Flows executed: 3

👁️ VISION ANALYSIS AGENT
🚨 Dark patterns: 4

⚖️ COMPLIANCE EVALUATION AGENT
✅ IEEE 7010: 78/100
❌ DSA Article 28: 45/100

📄 REPORT SAVED
```

### Generated Report

Check `reports/Instagram_compliance_report_YYYYMMDD_HHMMSS.md`

Contains:
- Executive summary
- Compliance scores by standard
- Dark patterns detected
- Specific violations
- Recommendations

## Common Issues

### "ANTHROPIC_API_KEY not found"

**Solution:**
```bash
nano .env
# Add your key: ANTHROPIC_API_KEY=sk-ant-...
```

### "Appium connection failed"

**For MVP:** Edit code to use `TEST_MODE=true` (default)

**For production:**
```bash
# Start Appium server
appium --allow-cors

# Verify it's running
curl http://localhost:4723/status
```

### "Module not found"

**Solution:**
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

## Next Steps

1. **Review generated report** in `reports/` folder
2. **Customize compliance standards** in `config/compliance_standards.yaml`
3. **Add more apps** to test
4. **Integrate with your workflow**:
   - Export reports to Google Drive
   - Send via email
   - Upload to client portal

## Architecture Quick Reference

```
User Request
     ↓
Tier 5 Orchestrator (orchestrator.py)
     ↓
Tier 4 Multi-Agent (compliance_agent.py)
     ├─ App Selector
     ├─ Navigation Agent → iOS Emulator
     ├─ Vision Analysis → Claude API
     ├─ Compliance Evaluation
     └─ Report Generator
     ↓
Human Review (optional)
     ↓
Distribution & Follow-up
```

## Example: Complete Workflow

```bash
# 1. Setup (one time)
./setup.sh
nano .env  # Add API key

# 2. Test multiple apps
source venv/bin/activate
python -c "
from orchestrator import ComplianceOrchestrator

orch = ComplianceOrchestrator('My Client')
orch.run_full_workflow('Instagram')
orch.run_full_workflow('TikTok')
"

# 3. Review reports
ls -la reports/
open reports/Instagram_compliance_report_*.md
```

## Getting Help

- 📖 Full documentation: [README.md](README.md)
- 🐛 Issues: Check error messages and logs
- 💡 Examples: See `compliance_agent.py` main() function
- 🔧 Configuration: Edit `config/compliance_standards.yaml`

## Production Checklist

Before deploying to production:

- [ ] Real Appium integration enabled
- [ ] Apps installed in simulator
- [ ] API keys secured (environment variables, not committed)
- [ ] Error handling tested
- [ ] Reports reviewed by compliance officer
- [ ] Client approval workflow established
- [ ] Backup and archival process
- [ ] Compliance disclaimers added

---

**Time to first report: < 5 minutes**

Happy testing! 🚀
