# Quick Start Guide - Automation Architecture

Get started with automation examples in under 5 minutes to 1 hour, depending on your chosen path.

---

## 🚀 Zero to Running in 3 Steps

### Step 1: Clone and Setup (5-10 minutes)

```bash
# Clone the repository
git clone https://github.com/austinsolomon/automation_architecture.git
cd automation_architecture

# Run setup script (installs all dependencies)
# macOS/Linux:
./setup.sh

# Windows (PowerShell as Administrator):
.\setup.ps1
```

**What the setup script installs:**
- ✅ Python 3.10+ and virtual environment
- ✅ Node.js and npm
- ✅ n8n workflow automation platform
- ✅ LangChain, LangGraph, and AI libraries
- ✅ Environment configuration template

### Step 2: Configure API Keys (2-5 minutes)

```bash
# Edit the .env file
nano .env  # or: code .env (VS Code), notepad .env (Windows)
```

**Minimum required for different paths:**

| Path | Required Keys | Where to Get |
|------|--------------|--------------|
| **Tier 0** (iOS Shortcuts) | None! | Works offline |
| **Tier 1** (n8n workflows) | None! | Uses mock data |
| **Tier 2** (AI-enhanced) | `ANTHROPIC_API_KEY` | https://console.anthropic.com/ |
| **Tier 3** (Agents) | `ANTHROPIC_API_KEY`, `SERPER_API_KEY` | https://serper.dev/ |

**Quick setup for Tier 2+ (AI examples):**
```bash
# Minimum .env for AI examples:
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
SERPER_API_KEY=xxxxxxxxxxxxx
```

### Step 3: Choose Your Path

Pick the fastest path based on your time and requirements:

---

## 🎯 Path A: iOS Shortcuts (5 Minutes) ⚡ FASTEST

**Best for**: Learning tier concepts, works offline, no APIs needed

**What you'll build**: Voice capture shortcut for leads, textures, or notes

```bash
# No installation needed - just read and implement
cat gtm/tier_0/tier_0_toy_ios_shortcuts_gtm_lead_capture.md
```

**Steps:**
1. Open iOS Shortcuts app on your iPhone
2. Follow instructions in any Tier 0 markdown file
3. Create the shortcut (5 minutes)
4. Start capturing immediately

**Example shortcuts:**
- `gtm/tier_0/tier_0_toy_ios_shortcuts_gtm_lead_capture.md` - Capture sales leads
- `ue5/tier_0/tier_0_toy_ios_shortcuts_ue5_texture_capture.md` - Capture texture references
- `br2/tier_0/tier_0_toy_ios_shortcuts_br2_voice_capture.md` - Capture voice notes

**Result**: Working automation in 5 minutes, no code required.

---

## 🎯 Path B: n8n Workflow (30 Minutes)

**Best for**: Learning workflow automation, visual programming

**What you'll build**: Automated daily sales metrics email

```bash
# Activate Python environment
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\Activate.ps1  # Windows

# Start n8n
n8n start
```

**Then:**
1. Open http://localhost:5678
2. Click "Workflows" → "Import from File"
3. Select `gtm/tier_1/tier_1_toy_n8n_gtm_daily_metrics.json`
4. Configure credentials (or use test mode)
5. Click "Execute Workflow"

**Read the setup guide:**
```bash
cat gtm/tier_1/tier_1_toy_n8n_gtm_daily_metrics_setup.md
```

**Other Tier 1 examples:**
- `gtm/tier_1/tier_1_toy_n8n_gtm_daily_metrics.json` - Daily sales email
- `ue5/tier_1/tier_1_toy_n8n_ue5_backup.json` - Project backup automation
- `br2/tier_1/tier_1_toy_n8n_br2_daily_review.json` - Daily review note creator

**Result**: Visual workflow automation running in 30 minutes.

---

## 🎯 Path C: AI-Enhanced Automation (1 Hour)

**Best for**: Learning how to add AI to workflows

**What you'll build**: Email intent classifier using Claude

**Requirements:**
- ✅ n8n installed (from setup.sh)
- ✅ `ANTHROPIC_API_KEY` in .env

```bash
# 1. Add your Anthropic API key to .env
echo "ANTHROPIC_API_KEY=sk-ant-xxxxx" >> .env

# 2. Start n8n
source venv/bin/activate
n8n start

# 3. Import workflow
# Go to http://localhost:5678
# Import: gtm/tier_2/tier_2_toy_n8n_gtm_email_classifier.json

# 4. Read setup guide
cat gtm/tier_2/tier_2_toy_n8n_gtm_email_classifier_setup.md
```

**What this demonstrates:**
- ONE LLM call adds semantic understanding
- Intelligent routing based on AI classification
- Context-aware automation vs. rule-based logic

**Other Tier 2 examples:**
- `gtm/tier_2/tier_2_toy_n8n_gtm_email_classifier.json` - Email intent detection
- `ue5/tier_2/tier_2_toy_n8n_ue5_asset_tagger.json` - Asset quality scoring
- `br2/tier_2/tier_2_toy_n8n_br2_inbox_triage.json` - Smart note categorization

**Result**: AI-powered workflow in 1 hour.

---

## 🎯 Path D: Autonomous Agent (1-2 Hours)

**Best for**: Learning agent-based automation with tool selection

**What you'll build**: Research agent that autonomously finds decision-makers

**Requirements:**
- ✅ Python environment activated
- ✅ `ANTHROPIC_API_KEY` in .env
- ✅ `SERPER_API_KEY` in .env (for web search)

```bash
# 1. Activate environment
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\Activate.ps1  # Windows

# 2. Install example-specific dependencies (if needed)
cd gtm/tier_3
pip install -r tier_3_cldchoice_gtm_lead_research_requirements.txt

# 3. Configure .env with both keys
# Edit .env and add:
# ANTHROPIC_API_KEY=sk-ant-xxxxx
# SERPER_API_KEY=xxxxx

# 4. Run the agent
python tier_3_toy_langchain_gtm_prospect_finder.py

# Or run the production agent:
python tier_3_cldchoice_gtm_lead_research.py --company "Acme Corp"
```

**What this demonstrates:**
- Agent with multiple tools (web_search, linkedin_lookup, company_info)
- Autonomous decision-making (which tool to use when)
- Structured output (JSON with decision-maker, pain points, etc.)

**Other Tier 3 examples:**
- `gtm/tier_3/tier_3_toy_langchain_gtm_prospect_finder.py` - Find decision-makers
- `ue5/tier_3/tier_3_toy_langchain_ue5_tutorial_finder.py` - Find UE5 tutorials
- `br2/tier_3/tier_3_toy_langchain_br2_note_connector.py` - Find related notes

**Result**: Autonomous agent running in 1-2 hours.

---

## 📚 Complete Use Case Examples (Half Day)

**Best for**: Implementing full production automation for your business

### GTM: Automated Lead Research & Outreach

**Complete tier stack: Tier 1 → Tier 3 → Tier 2 → Tier 1**

```bash
# 1. Setup (if not already done)
./setup.sh

# 2. Configure all required keys in .env:
ANTHROPIC_API_KEY=sk-ant-xxxxx
SERPER_API_KEY=xxxxx
PROXYCURL_API_KEY=xxxxx  # Optional: LinkedIn data
HUBSPOT_API_KEY=xxxxx     # Optional: CRM integration

# 3. Start with Tier 3 agent
cd gtm/tier_3
python tier_3_cldchoice_gtm_lead_research.py --company "TechCorp Inc"

# 4. Start n8n for orchestration
n8n start
# Import: gtm/tier_1/tier_1_cldchoice_gtm_lead_research.json

# 5. Read complete setup guide
cat gtm/tier_1/tier_1_cldchoice_gtm_lead_research_setup.md
```

**What you'll build:**
1. Daily orchestration (Tier 1 n8n) fetches target accounts
2. Research agent (Tier 3) finds decision-makers, pain points, buying signals
3. Email generator (Tier 2) creates personalized outreach
4. Sending workflow (Tier 1) schedules and tracks emails

**Data flow:**
```
Google Sheets (target accounts)
  → Tier 1 orchestrator
    → Tier 3 agent (research each account)
      → CRM (store results)
        → Tier 2 (generate personalized email)
          → Tier 1 (send & track)
```

### BR2: Multi-Source Capture & Organization

**Complete tier stack: Tier 0 → Tier 1 → Tier 2 → Tier 3**

```bash
# 1. Setup iOS Shortcut (Tier 0)
# Read: br2/tier_0/tier_0_cldchoice_br2_capture.md
# Create multi-format capture shortcut

# 2. Configure Obsidian path in .env
OBSIDIAN_VAULT_PATH=/Users/yourname/Documents/ObsidianVault

# 3. Start n8n
n8n start
# Import: br2/tier_1/tier_1_cldchoice_br2_capture_router.json
# Import: br2/tier_2/tier_2_cldchoice_br2_smart_categorizer.json

# 4. Run connection finder agent
cd br2/tier_3
python tier_3_cldchoice_br2_connection_finder.py
```

**What you'll build:**
1. iOS capture (Tier 0) → voice, text, links, screenshots
2. Router (Tier 1) → normalizes from multiple sources
3. Categorizer (Tier 2) → PARA method with Claude
4. Connection finder (Tier 3) → semantic note linking

### UE5: Procedural Asset Generation

**Complete tier stack: Tier 4 → Tier 3 → Tier 2**

```bash
# 1. Configure UE5 path in .env
UE5_PROJECT_PATH=/Users/yourname/UnrealProjects/MyGame

# 2. Run multi-agent pipeline (Tier 4)
cd ue5/tier_4
pip install -r requirements.txt
python tier_4_cldchoice_ue5_procedural_pipeline.py \
  --brief "Modular sci-fi building for space station"

# 3. Generated code will be in output/
# Review with quality checker (Tier 2):
n8n start
# Import: ue5/tier_2/tier_2_cldchoice_ue5_quality_check.json
```

**What you'll build:**
1. Multi-agent pipeline (Tier 4): Concept → Technical → Quality agents
2. Code generator (Tier 3): Writes Unreal Python
3. Quality checker (Tier 2): Claude Vision rates assets

---

## 🔑 API Keys Quick Reference

### Free Tiers Available

| Service | Free Tier | Cost After | Sign Up |
|---------|-----------|------------|---------|
| **Anthropic Claude** | $5 free credit | ~$3/million tokens | https://console.anthropic.com/ |
| **Serper** | 2,500 searches | $50/1M searches | https://serper.dev/ |
| **n8n** | Self-hosted free | Cloud: $20/mo | Self-host with setup.sh |

### Optional APIs

| Service | Purpose | Examples That Need It |
|---------|---------|----------------------|
| Proxycurl | LinkedIn data | GTM lead research |
| Clearbit | Company enrichment | GTM ICP hunting |
| OpenAI | GPT-4 Vision | UE5 asset quality (alternative to Claude Vision) |
| HubSpot | CRM integration | GTM production workflows |

---

## 🆘 Troubleshooting

### Setup Script Fails

**macOS: "permission denied"**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows: "execution policy"**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup.ps1
```

### Python Issues

**"command not found: python3"**
```bash
# macOS:
brew install python@3.11

# Linux:
sudo apt-get install python3.11

# Windows:
choco install python311
```

**"No module named 'langchain'"**
```bash
source venv/bin/activate  # Activate environment first!
pip install -r requirements.txt
```

### n8n Issues

**"n8n command not found"**
```bash
npm install -g n8n
# If that fails:
npx n8n  # Run without global install
```

**"Port 5678 already in use"**
```bash
# Kill existing n8n:
pkill -f n8n
# Or use different port:
n8n start --port 5679
```

### API Key Issues

**"Invalid API key"**
- Check `.env` file has no spaces around `=`
- Restart n8n after adding keys
- For Python: `source venv/bin/activate` reloads environment

**"Rate limit exceeded"**
- Anthropic: Check usage at https://console.anthropic.com/
- Serper: Free tier = 2,500 searches/month
- Wait or upgrade plan

---

## 📖 Next Steps

### Learning Path

1. ✅ **Start simple** - Tier 0 iOS Shortcuts (5 min)
2. ✅ **Add automation** - Tier 1 n8n workflows (30 min)
3. ✅ **Add intelligence** - Tier 2 AI-enhanced (1 hour)
4. ✅ **Add autonomy** - Tier 3 agents (2 hours)
5. ✅ **Scale up** - Complete use cases (half day)

### Reading List

1. `EXAMPLES_SUMMARY.md` - Complete inventory of all 57 examples
2. `README.md` - Architecture overview and tier definitions
3. Individual `*_setup.md` files - Detailed configuration for each example

### Community & Support

- 📚 **Documentation**: All examples have comprehensive setup guides
- 🐛 **Issues**: Report at https://github.com/austinsolomon/automation_architecture/issues
- 💡 **Discussions**: Share your implementations and questions

---

## ⚡ Speed Run (10 Minutes to Working Example)

**Absolute fastest path to a working automation:**

```bash
# 1. Clone (1 min)
git clone https://github.com/austinsolomon/automation_architecture.git
cd automation_architecture

# 2. Install only what we need (3 min)
python3 -m venv venv
source venv/bin/activate
npm install -g n8n

# 3. Start n8n (1 min)
n8n start &

# 4. Import workflow (2 min)
# Open http://localhost:5678
# Workflows → Import → gtm/tier_1/tier_1_toy_n8n_gtm_daily_metrics.json

# 5. Execute (1 min)
# Click "Execute Workflow"
# Watch it run!

# 6. Read what you just ran (2 min)
cat gtm/tier_1/tier_1_toy_n8n_gtm_daily_metrics_setup.md
```

**Total time: 10 minutes** from clone to working workflow.

---

## 🎯 Recommended First Example by Role

| Your Role | Start Here | Time | Why |
|-----------|-----------|------|-----|
| **Sales/Marketing** | GTM Tier 2 Email Classifier | 1 hour | Immediate value, practical AI use |
| **Game Developer** | UE5 Tier 1 Backup | 30 min | Solves real problem, introduces workflows |
| **Knowledge Worker** | BR2 Tier 0 Capture | 5 min | Instant productivity boost |
| **Engineer** | GTM Tier 3 Research Agent | 1-2 hours | Shows full agent capabilities |
| **Product Manager** | Complete GTM Lead Research | Half day | End-to-end automation value |

---

## ✨ Success Checklist

After setup, you should be able to:

- [ ] Run `n8n start` and access http://localhost:5678
- [ ] Run `python -c "import langchain"` without errors
- [ ] Import an n8n workflow JSON file
- [ ] See your `ANTHROPIC_API_KEY` in `.env`
- [ ] Activate Python environment: `source venv/bin/activate`
- [ ] Read an example setup guide and understand the tier characteristics

If all checked ✅ - you're ready to start automating!

---

**Need Help?** See individual example `*_setup.md` files or EXAMPLES_SUMMARY.md for complete reference.
