# iPhone App Compliance Testing Agent - MVP

> **Tier 4/5 Multi-Agent System for Digital Safety Compliance Auditing**

An automated system for testing iPhone applications against digital safety standards including IEEE 7010, DSA Article 28, Attention Economy Design Guidelines, and ICO Age Appropriate Design Code.

## 🎯 Overview

This MVP demonstrates how AI agents can automate compliance testing of mobile applications to detect dark patterns, predatory design mechanics, and violations of digital safety standards.

### What It Does

1. **Selects** from 5 popular iPhone apps (Instagram, TikTok, Candy Crush, DoorDash, Robinhood)
2. **Navigates** through the app using iOS Simulator automation (Appium)
3. **Detects** dark patterns and predatory design mechanics using Claude Vision
4. **Evaluates** compliance against 4 major digital safety standards
5. **Generates** comprehensive compliance reports with recommendations
6. **Orchestrates** human review workflow (Tier 5)

### Business Value

- **Traditional manual audit**: 20-40 hours @ $350/hr = **$7,000-14,000**
- **This AI system**: 0.5 hr AI + 2 hr review = **$875**
- **Savings: 85-90%** while maintaining professional standards

## 🏗️ Architecture

### Tier 4: Multi-Agent System (LangGraph)

Five specialized agents coordinate via shared state:

1. **AppSelectorAgent** - Choose app to test
2. **NavigationAgent** - Execute test flows in iOS Simulator
3. **VisionAnalysisAgent** - Detect dark patterns using Claude Vision
4. **ComplianceEvaluationAgent** - Score against standards
5. **ReportGenerationAgent** - Generate comprehensive reports

### Tier 5: Claude Code Orchestration

Human-in-the-loop workflow orchestration:

- Client intake and app selection
- Tier 4 agent execution
- **Human compliance officer review** (key differentiator)
- Automatic distribution to stakeholders
- Follow-up action scheduling
- Integration with practice management systems

```
┌─────────────────────────────────────────────────────────────┐
│                   Tier 5 Orchestrator                        │
│              (Claude Code + Human Review)                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────┐              ┌─────────────────┐
│  Client       │              │  Human Review   │
│  Intake       │              │  & Approval     │
└───────┬───────┘              └────────┬────────┘
        │                               │
        ▼                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Tier 4 Multi-Agent System                       │
│                    (LangGraph)                               │
├─────────────────────────────────────────────────────────────┤
│  App Selector → Navigation → Vision → Compliance → Report   │
│      Agent        Agent      Analysis   Evaluation   Gen    │
│                              Agent       Agent       Agent   │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│              iOS Emulator Integration                        │
│        (Appium + XCUITest + iOS Simulator)                  │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Compliance Standards

The system evaluates apps against four major digital safety frameworks:

### 1. IEEE 7010-2020
**Assessing Impact of AI on Human Well-being**
- Transparency (data practices, privacy policy)
- Agency (user control, opt-out mechanisms)
- Accountability (harm mechanisms, contact info)

### 2. DSA Article 28
**Digital Services Act - Protection of Minors**
- Age verification mechanisms
- No targeting of minors with profiling
- Parental controls and content moderation

### 3. Attention Economy Design (AED)
**Ethical Design Guidelines**
- Time management features
- Notification ethics
- Anti-addiction engagement tactics

### 4. ICO Age Appropriate Design Code
**UK Data Protection for Children**
- Best interests of child
- Age-appropriate transparency
- No detrimental design or manipulation
- Data minimization

## 🎨 Dark Pattern Detection

The system detects and classifies dark patterns across 5 categories:

| Category | Patterns | Severity |
|----------|----------|----------|
| **Obstruction** | Forced Action, Hard to Cancel | High/Critical |
| **Sneaking** | Hidden Costs, Bait and Switch | High/Critical |
| **Urgency** | Countdown Timers, Limited Availability | Medium |
| **Social Proof** | Activity Notifications, FOMO Triggers | Medium/High |
| **Misdirection** | Visual Interference, Trick Questions | Medium/High |

## 🚀 Quick Start

### Prerequisites

1. **macOS with Xcode** (for iOS Simulator)
2. **Node.js** (for Appium)
3. **Python 3.9+**
4. **Anthropic API Key** (for Claude Vision)

### Installation

```bash
# 1. Install iOS development tools
# Install Xcode from App Store
xcode-select --install

# 2. Install Appium
npm install -g appium
appium driver install xcuitest

# 3. Install Python dependencies
cd law/iphone_compliance_agent
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Configuration

Create `.env` file:

```bash
ANTHROPIC_API_KEY=your_api_key_here
APPIUM_SERVER=http://localhost:4723
IOS_PLATFORM_VERSION=17.0
IOS_DEVICE_NAME=iPhone 15 Pro
```

### Running Tests

#### Option 1: Tier 4 Only (Automated Testing)

```bash
# Start Appium server (in separate terminal)
appium --allow-cors

# Run compliance test
python compliance_agent.py
```

#### Option 2: Tier 5 (With Human Review)

```bash
# Start Appium server (in separate terminal)
appium --allow-cors

# Run orchestrated workflow
python orchestrator.py
```

#### Option 3: Batch Testing

```python
from orchestrator import ComplianceOrchestrator

orchestrator = ComplianceOrchestrator(client_name="Your Client")
results = orchestrator.batch_test_apps([
    "Instagram",
    "TikTok",
    "Candy Crush"
])
```

## 📱 Supported Apps (MVP)

The MVP comes pre-configured to test these popular apps:

1. **Instagram** - Social media (infinite scroll, engagement metrics)
2. **TikTok** - Short-form video (recommendation algorithm, addictive design)
3. **Candy Crush** - Mobile gaming (lives system, in-app purchases)
4. **DoorDash** - Food delivery (surge pricing, tip defaults)
5. **Robinhood** - Finance (gamification, push notifications)

### Adding New Apps

Edit `config/compliance_standards.yaml`:

```yaml
popular_test_apps:
  - name: "Your App"
    bundle_id: "com.yourcompany.app"
    category: "Category"
    known_concerns:
      - "Concern 1"
      - "Concern 2"
```

## 📊 Sample Output

### Console Output

```
════════════════════════════════════════════════════════════════════
📱 IPHONE COMPLIANCE TESTING AGENT
   Tier 4/5 Multi-Agent System
════════════════════════════════════════════════════════════════════

🎯 APP SELECTOR AGENT
────────────────────────────────────────────────────────────────────
✅ Selected: Instagram

🧭 NAVIGATION AGENT
────────────────────────────────────────────────────────────────────
✅ Navigation complete:
   Flows executed: 3
   Screenshots captured: 24

👁️ VISION ANALYSIS AGENT
────────────────────────────────────────────────────────────────────
🚨 Dark patterns detected: 4
   • Infinite Scroll (high)
   • Social Pressure (high)
   • Streak Mechanics (high)

⚖️ COMPLIANCE EVALUATION AGENT
────────────────────────────────────────────────────────────────────
   ✅ IEEE 7010: 78/100
   ❌ DSA Article 28: 45/100
   ❌ AED Guidelines: 42/100
   ✅ ICO Code: 68/100

📄 REPORT GENERATION AGENT
────────────────────────────────────────────────────────────────────
✅ Report saved: Instagram_compliance_report_20250119_143022.md

════════════════════════════════════════════════════════════════════
✅ COMPLIANCE TEST COMPLETE
════════════════════════════════════════════════════════════════════
```

### Generated Report

See `reports/` directory for full markdown reports including:

- Executive summary with overall compliance score
- Detailed scoring by standard and category
- Dark patterns detected with screenshots
- Specific violations identified
- Actionable recommendations
- Testing methodology and disclaimer

## 🔧 Technical Components

### File Structure

```
iphone_compliance_agent/
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
│
├── compliance_agent.py             # Tier 4 multi-agent system
├── orchestrator.py                 # Tier 5 orchestration layer
│
├── config/
│   └── compliance_standards.yaml   # Standards & app definitions
│
├── emulator/
│   └── ios_emulator.py            # Appium integration
│
├── agents/                         # (Future) Individual agent modules
│
├── utils/                          # (Future) Helper utilities
│
└── reports/                        # Generated compliance reports
    ├── screenshots/                # App screenshots captured
    └── *.md                        # Markdown reports
```

### Key Technologies

- **LangGraph**: Multi-agent orchestration and state management
- **LangChain**: Agent framework and LLM integration
- **Claude 3.5 Sonnet**: Vision analysis for dark pattern detection
- **Appium**: iOS app automation via WebDriver
- **XCUITest**: iOS UI testing framework
- **iOS Simulator**: Xcode's iPhone emulator

## 🎯 Use Cases

### Legal & Compliance

1. **Law Firms**
   - Advise app developers on compliance before launch
   - Represent clients in regulatory matters
   - Generate expert reports for litigation

2. **Consumer Protection Agencies**
   - Audit apps for dark patterns at scale
   - Investigate consumer complaints
   - Build enforcement cases

3. **Corporate Compliance**
   - Self-audit before app store submission
   - Ongoing monitoring for design changes
   - Competitive intelligence on peer apps

### Regulatory & Standards Bodies

4. **Regulatory Filings**
   - DSA compliance documentation
   - GDPR/data protection assessments
   - Industry standard certifications

5. **Academic Research**
   - Study dark pattern prevalence
   - Measure industry compliance trends
   - Evaluate regulatory effectiveness

## 🚧 MVP Limitations & Future Work

### Current MVP Limitations

- **Simulated navigation**: Uses predefined flows rather than live emulator
- **5 apps only**: Limited to pre-configured popular apps
- **Basic vision analysis**: Simplified dark pattern detection logic
- **No real distribution**: Simulates sending to client/systems
- **Single platform**: iOS only (no Android)

### Planned Enhancements

#### Phase 2 (Production Ready)

- [ ] Full Appium integration with real iOS Simulator
- [ ] Dynamic navigation using AI agent decision-making
- [ ] Advanced vision analysis with bounding boxes and heatmaps
- [ ] Real-time screenshot annotation
- [ ] Support for custom apps (TestFlight integration)
- [ ] Android support via Espresso/UIAutomator

#### Phase 3 (Scale & Integration)

- [ ] Web dashboard for report viewing
- [ ] API for third-party integrations
- [ ] Batch testing UI for multiple apps
- [ ] Historical tracking and trend analysis
- [ ] Automated re-testing on app updates
- [ ] Integration with Clio, MyCase, NetDocuments

#### Phase 4 (Advanced Features)

- [ ] A/B testing for design variations
- [ ] Comparative industry benchmarking
- [ ] Custom compliance standard builder
- [ ] Multilingual support for international standards
- [ ] Video recording of test sessions
- [ ] Accessibility compliance (WCAG, Section 508)

## 🧪 Testing

### Run Tests

```bash
# Test emulator connection
python emulator/ios_emulator.py

# Test compliance agent
python compliance_agent.py

# Test full orchestration
python orchestrator.py
```

### Manual Testing Checklist

- [ ] Appium server starts successfully
- [ ] iOS Simulator launches
- [ ] App installs and launches in simulator
- [ ] Screenshots captured correctly
- [ ] Claude Vision API responds
- [ ] Report generates with all sections
- [ ] Report saves to correct location

## 📚 References

### Standards Documentation

- [IEEE 7010-2020](https://standards.ieee.org/standard/7010-2020.html)
- [EU Digital Services Act](https://digital-strategy.ec.europa.eu/en/policies/digital-services-act-package)
- [ICO Age Appropriate Design Code](https://ico.org.uk/for-organisations/guide-to-data-protection/ico-codes-of-practice/age-appropriate-design-a-code-of-practice-for-online-services/)

### Technical Documentation

- [Appium Documentation](https://appium.io/docs/en/latest/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Claude Vision API](https://docs.anthropic.com/claude/docs/vision)

### Dark Pattern Research

- [Deceptive Design (darkpatterns.org)](https://www.deceptive.design/)
- [Princeton Dark Patterns Study](https://webtransparency.cs.princeton.edu/dark-patterns/)

## 💼 Business Model

### Pricing Tiers

**Self-Service (Developer)**
- $99/app test
- Automated report only
- No human review

**Professional (Law Firm)**
- $875/app test
- AI testing + attorney review
- Client-ready deliverable
- Includes distribution

**Enterprise (Agency/Corporate)**
- Custom pricing
- Batch testing
- Ongoing monitoring
- API access
- Dedicated support

### ROI Calculation

Traditional approach:
- 20-40 hours attorney time
- $350/hour billing rate
- **Total: $7,000-14,000 per app**

AI-assisted approach:
- 0.5 hours AI testing ($50 compute)
- 2 hours attorney review ($700)
- **Total: $750-875 per app**
- **Savings: 85-90%**

## 📞 Support & Contributing

### Getting Help

1. Check the [documentation](#documentation)
2. Review [common issues](#troubleshooting)
3. Open a GitHub issue
4. Email: compliance-agent@example.com

### Contributing

We welcome contributions! Areas needing help:

- Additional compliance standards (COPPA, CCPA, etc.)
- Android support
- More sophisticated dark pattern detection
- UI/UX for report viewing
- Integration with legal tech platforms

## 📄 License

MIT License - see LICENSE file for details

## ⚠️ Disclaimer

This system provides automated compliance assessment tools. Reports generated should be reviewed by qualified legal and compliance professionals before making business decisions or submitting to regulators.

The system does not provide legal advice. For legal advice, consult with a licensed attorney in your jurisdiction.

---

## 🎓 Why This Architecture?

### Tier 4 vs Tier 3

**Tier 3** (Single Agent):
- One agent tries to do everything
- Less specialized, more generalized
- Harder to debug and improve

**Tier 4** (Multi-Agent):
- Specialized agents for each task
- Better quality through specialization
- Parallel execution where possible
- Easier to improve individual components

### Tier 5 vs Tier 4

**Tier 4** (Automated Only):
- Fully automated testing and reporting
- No professional judgment
- Can't maintain attorney-client privilege
- Not suitable for client deliverables

**Tier 5** (Human-in-Loop):
- AI generates draft, human reviews
- Maintains professional standards
- Attorney-client privilege preserved
- Client-ready deliverables
- Trust building through transparency

---

**Built with the Automation Architecture Framework**

Part of the comprehensive automation tiering system demonstrating best practices for AI agent orchestration in legal tech.

For more examples, see `/law/tier_examples/` in the parent repository.
