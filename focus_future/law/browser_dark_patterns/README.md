# Dark Pattern Detection Agent - MVP

An academically rigorous dark pattern detection system with an interactive web interface that enables iterative agent development through a tight feedback loop.

## Overview

This system uses Claude Sonnet 4.5's vision capabilities combined with browser automation to navigate websites and detect dark patterns across multiple legal and policy frameworks. The agent provides explainable reasoning for each navigation decision and pattern detection, creating a transparent audit trail for academic research and compliance assessment.

## Key Features

### 🤖 Multi-Framework Dark Pattern Detection

The agent analyzes websites through four complementary frameworks:

1. **IEEE 7010-2020**: Well-being impact indicators for autonomous systems
2. **DSA Article 28**: EU Digital Services Act manipulative design prohibitions
3. **Attention Economy Design (AED)**: Time well-spent and attention extraction patterns
4. **ICO Age Appropriate Design Code (AADC)**: Child-focused design requirements

Each framework provides:
- Specific detection rules (visual, textual, behavioral, structural)
- Configurable confidence thresholds
- Evidence requirements (screenshots, DOM snapshots, citations)
- Severity levels (minor/moderate/severe/critical)

### 🧠 Explainable Agent Reasoning

Every navigation decision includes:
- **Current State**: What the agent sees (screenshot + DOM structure)
- **Framework Analysis**: Which frameworks triggered on current page
- **Navigation Options**: Discovered links/buttons with priority scores
- **Decision Rationale**: Why the chosen path was selected
- **Pattern Hypotheses**: What patterns the agent is investigating

### 🔄 Iterative Feedback Loop

```
┌──────────────┐
│ 1. Configure │ Developer selects frameworks, target URL
└──────┬───────┘
       │
┌──────▼───────┐
│ 2. Explore   │ Agent navigates with Claude vision reasoning
└──────┬───────┘
       │
┌──────▼───────┐
│ 3. Report    │ Visual pathway + detected patterns + reasoning
└──────┬───────┘
       │
┌──────▼───────┐
│ 4. Review    │ Developer validates findings, adjusts frameworks
└──────┬───────┘
       │
┌──────▼───────┐
│ 5. Refine    │ Agent re-explores with updated detection rules
└──────────────┘
```

### 📊 Web Interface

- **Configuration Panel**: Select frameworks, target URL, exploration depth
- **Live Progress**: Real-time agent reasoning display via WebSockets
- **Pathway Visualization**: Screenshot sequence with decision points
- **Pattern Report**: Categorized findings by framework
- **Reasoning Explainer**: Detailed explanation of each navigation choice
- **Feedback Tools**: Accept/reject findings, adjust detection rules
- **Session Management**: Save/load exploration sessions for comparison

## Architecture

### Agent Components

```
┌─────────────────────────────────────────────────────────┐
│                    LangGraph Orchestrator                │
│  (Coordinates workflow with explainable state machine)   │
└───────────┬─────────────────────────────┬───────────────┘
            │                             │
    ┌───────▼────────┐          ┌────────▼────────┐
    │   Navigator    │          │    Analyzer     │
    │ Browser Use +  │          │ Multi-framework │
    │ Claude Vision  │          │    Detection    │
    └───────┬────────┘          └────────┬────────┘
            │                            │
    ┌───────▼────────────────────────────▼────────┐
    │          Evidence Collector                 │
    │   Screenshots + DOM + Reasoning Chain       │
    └─────────────────┬───────────────────────────┘
                      │
              ┌───────▼────────┐
              │  SQLite Store  │
              │ Session Persist│
              └────────────────┘
```

### Framework System

Each framework is implemented as a Pydantic model with:

```python
class DarkPatternFramework(BaseModel):
    name: str
    version: str
    patterns: list[PatternDefinition]

class PatternDefinition(BaseModel):
    id: str
    name: str
    description: str
    detection_rules: DetectionRules
    severity: Severity
    evidence_requirements: list[EvidenceType]
    legal_citations: list[Citation]
    confidence_threshold: float
```

### Evidence Collection

All findings include:

1. **Visual Evidence**: Screenshot with bounding boxes on detected elements
2. **Structural Evidence**: DOM snapshot of relevant elements
3. **Reasoning Chain**: Step-by-step agent reasoning
4. **Framework Citations**: Specific legal/policy references
5. **Confidence Scores**: Per-rule and aggregate confidence

## Installation

### Prerequisites

- Python 3.11+
- Chrome/Chromium browser
- Anthropic API key with Claude Sonnet 4.5 access

### Setup

```bash
# Clone repository
cd law/browser_dark_patterns

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Set up environment variables
cp .env.sample .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Configuration

Edit `.env` with your settings:

```env
ANTHROPIC_API_KEY=your_api_key_here
BROWSER_HEADLESS=false  # Set to true for headless mode
MAX_EXPLORATION_DEPTH=5
SESSION_DB_PATH=./data/sessions/sessions.db
```

## Usage

### Web Interface (Recommended)

```bash
# Start the web server
uv run python -m src.web.app

# Open browser to http://localhost:8000
```

1. **Configure Exploration**:
   - Enter target URL (e.g., `https://www.instagram.com`)
   - Select frameworks to apply
   - Set exploration depth (default: 5)

2. **Monitor Progress**:
   - Watch live agent reasoning in the console panel
   - See screenshots appear as agent navigates
   - View detected patterns in real-time

3. **Review Findings**:
   - Examine pathway visualization
   - Read detailed pattern reports
   - Review evidence for each finding

4. **Refine Detection**:
   - Accept/reject pattern findings
   - Adjust confidence thresholds
   - Add custom detection rules
   - Re-run exploration with updated config

### Programmatic Usage

```python
from src.agent.orchestrator import DarkPatternOrchestrator
from src.frameworks.ieee_7010 import IEEE7010Framework
from src.frameworks.dsa_article_28 import DSAArticle28Framework

# Configure agent
orchestrator = DarkPatternOrchestrator(
    frameworks=[
        IEEE7010Framework(),
        DSAArticle28Framework()
    ],
    max_depth=5
)

# Run exploration
session = orchestrator.explore(
    url="https://www.instagram.com",
    session_name="Instagram Signup Flow Analysis"
)

# Access results
for finding in session.findings:
    print(f"Pattern: {finding.pattern_name}")
    print(f"Framework: {finding.framework}")
    print(f"Severity: {finding.severity}")
    print(f"Confidence: {finding.confidence:.2f}")
    print(f"Evidence: {len(finding.screenshots)} screenshots")
    print(f"Reasoning: {finding.reasoning_chain}")
    print("---")
```

## How the Agent Works

### Navigation Strategy

The agent uses a breadth-first exploration strategy with priority scoring:

1. **Page Analysis**: Use Claude Vision to analyze screenshot
2. **Element Discovery**: Extract all interactive elements (links, buttons, forms)
3. **Priority Scoring**: Score elements based on:
   - Likelihood of revealing dark patterns
   - Framework-specific targets (e.g., signup flows for DSA)
   - Unexplored paths
   - User journey criticality
4. **Decision**: Select highest-priority element with explanation
5. **Evidence Collection**: Capture state before navigation
6. **Repeat**: Continue until max depth or no new patterns found

### Pattern Detection

For each page, the agent:

1. **Visual Analysis**: Claude Vision examines screenshot for:
   - UI element styling (color, size, position)
   - Visual hierarchy and emphasis
   - Textual content and framing
   - Layout patterns

2. **Structural Analysis**: Parse DOM for:
   - Element types and attributes
   - Form field requirements
   - Interaction patterns
   - Data collection points

3. **Framework Application**: Run detection rules from each active framework:
   ```python
   # Example: Detecting "Hard to Cancel" pattern (DSA Article 28)
   if (signup_steps < 3) and (cancellation_steps > signup_steps * 2):
       report_pattern(
           pattern="asymmetric_difficulty",
           confidence=0.9,
           evidence=[signup_flow_screenshots, cancellation_flow_screenshots],
           reasoning="Cancellation requires 7 steps vs 2 for signup"
       )
   ```

4. **Confidence Aggregation**: Combine rule matches into overall finding

### Reasoning Explainability

Each decision point records:

```python
class ReasoningNode(BaseModel):
    timestamp: datetime
    state_description: str  # What the agent sees
    framework_triggers: list[str]  # Which frameworks are active
    navigation_options: list[NavigationOption]  # Available actions
    selected_option: NavigationOption  # Chosen action
    selection_rationale: str  # Why this was chosen
    pattern_hypotheses: list[str]  # What patterns are being investigated
    confidence_scores: dict[str, float]  # Per-framework confidence
```

This creates a full audit trail for academic research and compliance validation.

## Framework Implementations

### IEEE 7010-2020: Well-being Impact

Detects patterns affecting user well-being:

- **Addiction Mechanisms**: Infinite scroll, variable rewards, streak systems
- **Time Displacement**: Intentional time-sink features
- **Social Pressure**: FOMO-inducing design, social comparison
- **Autonomy Violation**: Difficult opt-outs, forced engagement

### DSA Article 28: Manipulative Design

Focuses on EU-prohibited practices:

- **Coercive Patterns**: Forced actions, confirmshaming
- **Deceptive Patterns**: Hidden costs, bait-and-switch
- **Asymmetric Difficulty**: Easy signup, hard cancellation
- **Exploitative Design**: Targeting vulnerabilities

### Attention Economy Design (AED)

Analyzes attention extraction:

- **Engagement Maximization**: Autoplay, notifications, endless feeds
- **Distraction Injection**: Interruptive elements
- **Time Obfuscation**: Hidden time spent, no usage data
- **Competitive Gamification**: Ranking, streaks, achievements

### ICO Age Appropriate Design Code (AADC)

Child-focused requirements:

- **Privacy by Default**: Default settings protecting children
- **Data Minimization**: Excessive data collection from minors
- **Transparency**: Age-appropriate communication
- **Harmful Content**: Exposure to inappropriate material

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific framework tests
uv run pytest tests/test_frameworks.py -v
```

### Project Structure

```
law/browser_dark_patterns/
├── README.md                          # This file
├── pyproject.toml                     # Dependencies (uv)
├── .env.sample                        # Environment template
├── src/
│   ├── agent/
│   │   ├── navigator.py              # Browser automation + Claude vision
│   │   ├── analyzer.py               # Multi-framework pattern detection
│   │   ├── orchestrator.py           # LangGraph workflow
│   │   └── reasoning.py              # Explainable decision-making
│   ├── frameworks/
│   │   ├── base.py                   # Framework base classes (Pydantic)
│   │   ├── ieee_7010.py              # IEEE 7010-2020 framework
│   │   ├── dsa_article_28.py         # DSA Article 28
│   │   ├── attention_economy.py      # AED framework
│   │   └── ico_aadc.py               # ICO Age Appropriate Design Code
│   ├── evidence/
│   │   ├── collector.py              # Screenshot + DOM + reasoning capture
│   │   └── models.py                 # Pydantic evidence schemas
│   ├── web/
│   │   ├── app.py                    # FastAPI web interface
│   │   ├── static/                   # CSS/JS for pathway visualization
│   │   └── templates/                # HTML templates
│   └── utils/
│       ├── browser.py                # Browser Use wrapper
│       └── storage.py                # SQLite for sessions
├── data/
│   └── sessions/                     # Stored exploration sessions
└── tests/
    └── test_frameworks.py
```

### Adding Custom Frameworks

```python
from src.frameworks.base import DarkPatternFramework, PatternDefinition

class MyCustomFramework(DarkPatternFramework):
    name = "My Custom Framework"
    version = "1.0"

    def __init__(self):
        super().__init__(
            patterns=[
                PatternDefinition(
                    id="custom_001",
                    name="Custom Pattern",
                    description="Description of what to detect",
                    detection_rules=DetectionRules(
                        visual_indicators=["red buttons", "large text"],
                        textual_patterns=["limited time", "act now"],
                        structural_markers=["countdown timer elements"]
                    ),
                    severity=Severity.MODERATE,
                    confidence_threshold=0.7
                )
            ]
        )
```

### Adjusting Detection Rules

Edit framework files in `src/frameworks/` to adjust:

- `confidence_threshold`: Minimum confidence to report pattern (0.0-1.0)
- `detection_rules`: Add/remove visual, textual, structural indicators
- `severity`: Change pattern severity classification
- `evidence_requirements`: Modify what evidence must be captured

## Academic Rigor

### Citation System

All pattern findings include:

```python
class Finding(BaseModel):
    pattern_id: str
    framework: str
    legal_citations: list[Citation]
    policy_citations: list[Citation]
    academic_references: list[Reference]
```

Example citation:

```python
Citation(
    source="Digital Services Act (EU) 2022/2065",
    article="Article 28",
    paragraph="1(a)",
    text="materially distort the behaviour of service recipients",
    url="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2065"
)
```

### Reproducibility

All exploration sessions are stored with:
- Exact timestamp
- Framework versions
- Detection rule configurations
- Full screenshot and DOM captures
- Complete reasoning chains

Sessions can be re-analyzed with different frameworks or replayed for verification.

### Validation Workflow

1. **Initial Exploration**: Agent explores with default settings
2. **Expert Review**: Researcher reviews findings
3. **Rule Refinement**: Adjust thresholds/rules based on false positives
4. **Re-exploration**: Agent re-runs with updated config
5. **Comparison**: Side-by-side comparison of sessions
6. **Documentation**: Export findings with full citation trail

## MVP Scope

### In Scope
- ✅ Single-agent sequential exploration
- ✅ BFS navigation strategy
- ✅ SQLite session storage
- ✅ Local execution
- ✅ Four framework implementations
- ✅ Web interface with live updates
- ✅ Feedback loop for rule refinement

### Future Enhancements
- Multi-agent parallel exploration
- Graph-based navigation with Neo4j
- Advanced pathfinding algorithms (A*)
- Distributed crawling
- Real-time monitoring dashboards
- Automated regression testing for frameworks
- Comparative analysis across platforms

## Use Cases

### Academic Research

```python
# Comparative study of social media dark patterns
platforms = ["instagram.com", "tiktok.com", "facebook.com"]
results = {}

for platform in platforms:
    session = orchestrator.explore(url=f"https://{platform}")
    results[platform] = session.analyze_patterns_by_framework()

# Generate comparative report
report = generate_comparative_analysis(results)
```

### Compliance Auditing

```python
# DSA compliance check for e-commerce site
orchestrator = DarkPatternOrchestrator(
    frameworks=[DSAArticle28Framework()],
    max_depth=10
)

session = orchestrator.explore(
    url="https://shop.example.com",
    focus_flows=["signup", "checkout", "cancellation"]
)

# Generate compliance report
compliance_report = session.generate_dsa_compliance_report()
```

### Framework Development

```python
# Test new detection rules iteratively
framework = IEEE7010Framework()
framework.patterns[0].confidence_threshold = 0.8  # Adjust threshold

session1 = orchestrator.explore(url="test_site.com")
# Review findings, adjust rules
framework.patterns[0].detection_rules.add_visual_indicator("new pattern")

session2 = orchestrator.explore(url="test_site.com")
# Compare sessions to validate improvement
comparison = compare_sessions(session1, session2)
```

## Troubleshooting

### Browser Issues

```bash
# If browser fails to launch
playwright install chromium

# If screenshots are blank
export BROWSER_HEADLESS=false
```

### API Rate Limits

The agent includes automatic retry logic for Claude API calls. If you hit rate limits:

```python
# Reduce exploration depth
orchestrator = DarkPatternOrchestrator(max_depth=3)

# Add delays between navigations
orchestrator.navigation_delay = 2.0  # seconds
```

### Evidence Storage

Sessions can grow large. Clean up old sessions:

```bash
# Remove sessions older than 30 days
uv run python -m src.utils.storage --cleanup --days 30
```

## Contributing

This is an MVP focused on proof-of-concept. Contributions welcome for:

1. Additional framework implementations
2. Improved detection rules with academic citations
3. Enhanced reasoning explainability
4. Performance optimizations
5. Test coverage improvements

## License

This project is for academic research and educational purposes. See LICENSE file for details.

## References

- IEEE 7010-2020: Recommended Practice for Assessing the Impact of Autonomous and Intelligent Systems on Human Well-being
- Digital Services Act (EU) 2022/2065, Article 28
- Attention Economy Design: Principles for time well-spent design
- ICO Age Appropriate Design Code: UK children's privacy framework

## Citation

If you use this tool in academic research, please cite:

```bibtex
@software{dark_pattern_detection_agent,
  title={Dark Pattern Detection Agent: Multi-Framework Browser Automation for Manipulative Design Detection},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/automation_architecture}
}
```
