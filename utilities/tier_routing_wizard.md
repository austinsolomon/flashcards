# Tier Routing Wizard - Implementation Guide

This guide contains everything you need to implement the `/tier-wizard` slash command in any automation project. The wizard helps users determine the correct automation tier (0-6) for their workflow through simple yes/no questions.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Complete File Content](#complete-file-content)
3. [Decision Tree Reference](#decision-tree-reference)
4. [Customization Guide](#customization-guide)
5. [Testing & Validation](#testing--validation)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Step 1: Create the Command File

```bash
# Navigate to your project root
cd /path/to/your/project

# Create the commands directory if it doesn't exist
mkdir -p .claude/commands

# Create the tier-wizard.md file
touch .claude/commands/tier-wizard.md
```

### Step 2: Copy the Content

Copy the **complete file content** from the [Complete File Content](#complete-file-content) section below into `.claude/commands/tier-wizard.md`

### Step 3: Customize for Your Project

Update these sections:
- **Q1: Domain Options** - Replace GTM/UE5/BR2 with your domains
- **Examples** - Add domain-specific examples in Q2-Q8
- **Template Paths** - Update file paths to match your structure
- **Tool Recommendations** - Adjust for your tech stack

### Step 4: Test

```bash
# In Claude Code, type:
/tier-wizard

# Follow the prompts and verify it outputs the correct tier
```

---

## Complete File Content

Copy this entire content into `.claude/commands/tier-wizard.md`:

```markdown
---
description: Interactive wizard to determine the correct automation tier for your workflow through simple yes/no questions
---

You are the Automation Tier Wizard. Your job is to help the user determine which automation tier (0-6) is appropriate for their workflow by asking simple yes/no questions.

## Instructions

Ask questions ONE AT A TIME. Wait for the user's answer before asking the next question. Keep responses brief and conversational.

Start with this introduction, then begin asking questions:

---

**🧙 Welcome to the Automation Tier Wizard!**

I'll ask you simple yes/no questions to determine the right automation tier for your workflow.

This will take about 2-3 minutes. Answer with **yes** or **no** (or **skip** if uncertain).

Ready? Let's start!

---

## Question Flow (Ask ONE at a time)

### Q1: Domain Context
**Question:** "Is this workflow for: (a) Marketing/Sales (GTM), (b) Game Development (UE5), or (c) Personal Productivity (BR2)?"

*[Store domain for template recommendation later]*

---

### Q2: AI Requirement - Basic
**Question:** "Does this workflow need AI to understand context or make decisions? (e.g., understand meaning of text, analyze images, reason about data)"

- If **NO** → Ask Q3 (multi-step check for Tier 0 vs 1)
- If **YES** → Ask Q4 (agent check)

---

### Q3: Multi-Step Logic (only if NO to Q2)
**Question:** "Does it involve multiple steps or branching logic? (e.g., if-then rules, routing based on conditions, connecting 3+ apps)"

- If **NO** → **Tier 0** (Simple automation - iOS Shortcuts, Zapier single trigger)
- If **YES** → **Tier 1** (Multi-step automation - n8n, Make, no AI needed)

---

### Q4: Agent Reasoning (only if YES to Q2)
**Question:** "Does the AI need to make multi-step decisions or choose which tools to use? (e.g., 'decide whether to search docs OR check database based on the question')"

- If **NO** → Ask Q5 (single AI call check)
- If **YES** → Ask Q6 (multi-agent check)

---

### Q5: Single AI Call (only if NO to Q4)
**Question:** "Can the AI task be done in ONE API call? (e.g., summarize article, categorize email, analyze image quality)"

- If **YES** → **Tier 2** (Single LLM automation - n8n + Claude/GPT)
- If **NO** → Ask Q6 (multi-agent check)

---

### Q6: Multi-Agent Coordination (only if YES to Q4 or NO to Q5)
**Question:** "Do you need MULTIPLE specialized AI agents working together? (e.g., ResearchAgent → WriterAgent → EditorAgent, each with different expertise)"

- If **NO** → **Tier 3** (Single agent with tools - LangChain, LlamaIndex)
- If **YES** → Ask Q7 (human approval check)

---

### Q7: Human Approval Required (only if YES to Q6)
**Question:** "Do humans need to review and approve AI decisions before they execute? (e.g., legal review, compliance approval, manager sign-off)"

- If **NO** → **Tier 4** (Multi-agent orchestration - CrewAI, AutoGen)
- If **YES** → Ask Q8 (learning requirement)

---

### Q8: Learning from Feedback (always ask after Q7)
**Question:** "Does the system need to learn and improve from user feedback over time? (e.g., get better at categorization based on corrections, optimize based on outcomes)"

- If **NO** and Q7 was YES → **Tier 5** (Human-in-loop workflows)
- If **NO** and Q7 was NO → **Tier 4** (Multi-agent orchestration)
- If **YES** → **Tier 6** (Autonomous learning system)

---

## After Determining Tier

Once you've determined the tier, provide this summary:

---

**🎯 TIER RECOMMENDATION: Tier [X]**

**What this means:**
[1-2 sentence description of what this tier involves]

**Typical tools:**
- [List 2-3 common tools/frameworks for this tier]

**Complexity level:**
[Simple / Moderate / Complex / Advanced / Expert / Cutting-edge]

**Estimated implementation time:**
[Rough estimate: hours / days / weeks]

**Cost range:**
[Rough monthly cost estimate if applicable]

---

**📋 NEXT STEPS:**

1. **Use this template:** `get_started/intake_examples/INTAKE_TEMPLATE_[domain].md`
   - Domain: [GTM / UE5 / BR2 based on Q1]

2. **Fill out the "Complexity Signals" section** with these answers:
   - [Summarize their yes/no answers from above]

3. **Review example workflows** in:
   - `[domain]/tier_examples/tier_[X]/`

4. **Key considerations for Tier [X]:**
   - [List 2-3 specific things they should think about for this tier]

---

**💡 QUICK TIPS:**

[Tier-specific advice, e.g.:]
- **Tier 0-1:** Keep it simple - don't over-engineer
- **Tier 2:** Focus on ONE high-value AI call
- **Tier 3:** Design clear tool interfaces for your agent
- **Tier 4:** Map out agent handoffs carefully
- **Tier 5:** Define approval workflows upfront
- **Tier 6:** Start with supervised learning, iterate

---

**Would you like to:**
- (a) Review a similar example workflow
- (b) Get help filling out the intake template
- (c) Discuss technical implementation
- (d) Start over with a different workflow

---

## Important Notes

- Keep your tone friendly and conversational
- If the user is unsure about a question, offer a brief example to clarify
- If answers suggest they're between two tiers, recommend starting with the LOWER tier and upgrading later
- Always remind them: "Start simple, iterate later"
- If they describe a complex workflow that should be broken down, suggest splitting into multiple automations

## Example Clarifications

If user asks for clarification on questions, use these examples:

**Q2 (AI requirement):**
- YES: "Understand if this email is about a project or personal task"
- NO: "Route emails with 'invoice' in subject to accounting folder"

**Q4 (Agent reasoning):**
- YES: "AI decides whether to search documentation, check database, or ask user for clarification"
- NO: "AI always summarizes the article, no decisions about what to do"

**Q6 (Multi-agent):**
- YES: "ResearchAgent gathers data → AnalystAgent analyzes → WriterAgent creates report"
- NO: "Single agent uses multiple tools (search, calculator, database) but makes all decisions"

**Q8 (Learning):**
- YES: "System learns from my corrections to improve future categorizations"
- NO: "System follows the same prompt/rules every time"
```

---

## Decision Tree Reference

### Visual Flow

```
START
  │
  ├─ Q1: Domain? → [Your domains here]
  │
  └─ Q2: Needs AI for context/decisions?
      │
      ├─ NO ──────────────────────────┐
      │                                │
      │  Q3: Multiple steps or         │
      │      branching logic?          │
      │      │                         │
      │      ├─ NO → TIER 0            │
      │      │    (Simple automation)  │
      │      │                         │
      │      └─ YES → TIER 1           │
      │           (Multi-step, no AI)  │
      │                                │
      └─ YES ─────────────────────────┤
                                       │
         Q4: AI makes multi-step       │
             decisions or chooses      │
             tools?                    │
             │                         │
             ├─ NO ───────────────────┐│
             │                        ││
             │  Q5: Single AI call?   ││
             │      │                 ││
             │      ├─ YES → TIER 2   ││
             │      │                 ││
             │      └─ NO ────────────┤│
             │                        ││
             └─ YES ──────────────────┤│
                                      ││
                Q6: Multiple          ││
                    specialized       ││
                    AI agents?        ││
                    │                 ││
                    ├─ NO → TIER 3 ◄──┘│
                    │                  │
                    └─ YES ────────────┤
                                       │
                       Q7: Human       │
                           approval    │
                           required?   │
                           │           │
                           ├─ NO → Q8 ─┤
                           │      │    │
                           │      ├─NO → TIER 4
                           │      │
                           │      └─YES→ TIER 6
                           │
                           └─ YES → Q8 ┤
                                  │    │
                                  ├─NO → TIER 5
                                  │
                                  └─YES→ TIER 6
```

### All Decision Paths

```
Path 1: Q2=NO  → Q3=NO                              → TIER 0
Path 2: Q2=NO  → Q3=YES                             → TIER 1
Path 3: Q2=YES → Q4=NO  → Q5=YES                    → TIER 2
Path 4: Q2=YES → Q4=NO  → Q5=NO  → Q6=NO            → TIER 3
Path 5: Q2=YES → Q4=YES → Q6=NO                     → TIER 3
Path 6: Q2=YES → Q4=YES → Q6=YES → Q7=NO  → Q8=NO  → TIER 4
Path 7: Q2=YES → Q4=YES → Q6=YES → Q7=YES → Q8=NO  → TIER 5
Path 8: Q2=YES → Q4=YES → Q6=YES → Q7=ANY → Q8=YES → TIER 6
```

### Quick Reference Table

| Question | NO → | YES → |
|----------|------|-------|
| Q2: Needs AI? | Q3 | Q4 |
| Q3: Multi-step? (no AI) | **TIER 0** | **TIER 1** |
| Q4: Agent reasoning? | Q5 | Q6 |
| Q5: Single AI call? | Q6 | **TIER 2** |
| Q6: Multi-agent? | **TIER 3** | Q7 |
| Q7: Human approval? | Q8 → T4/T6 | Q8 → T5/T6 |
| Q8: Learning? | T4 or T5 | **TIER 6** |

---

## Customization Guide

### 1. Update Domain Options (Q1)

**Current default:**
```markdown
**Question:** "Is this workflow for: (a) Marketing/Sales (GTM), (b) Game Development (UE5), or (c) Personal Productivity (BR2)?"
```

**Example customizations:**

**E-commerce:**
```markdown
**Question:** "Is this workflow for: (a) Customer Service, (b) Inventory Management, or (c) Marketing & Analytics?"
```

**Healthcare:**
```markdown
**Question:** "Is this workflow for: (a) Patient Care, (b) Administrative Operations, or (c) Clinical Research?"
```

**Finance:**
```markdown
**Question:** "Is this workflow for: (a) Trading Operations, (b) Compliance & Risk, or (c) Reporting & Analytics?"
```

**Software Development:**
```markdown
**Question:** "Is this workflow for: (a) Development & CI/CD, (b) Code Quality & Testing, or (c) Project Management?"
```

---

### 2. Update Template Paths

**Find this line in the "After Determining Tier" section:**
```markdown
1. **Use this template:** `get_started/intake_examples/INTAKE_TEMPLATE_[domain].md`
```

**Update to match your project structure:**
```markdown
1. **Use this template:** `docs/templates/INTAKE_TEMPLATE_[domain].md`
   # or
1. **Use this template:** `automation/intake/[domain]_template.md`
```

**Also update example workflow paths:**
```markdown
3. **Review example workflows** in:
   - `[domain]/tier_examples/tier_[X]/`
   # Change to your structure
   - `examples/[domain]/tier_[X]/`
```

---

### 3. Add Domain-Specific Examples

For each question (Q2-Q8), add examples relevant to your domain.

**Example for Healthcare domain:**

**Q2 (AI requirement):**
```markdown
- YES: "Analyze patient symptoms to suggest relevant diagnostic tests"
- NO: "Route lab results with 'URGENT' flag to attending physician"
```

**Q4 (Agent reasoning):**
```markdown
- YES: "AI decides whether to check patient history, drug interactions, or recent labs based on the question"
- NO: "AI always summarizes patient chart, no decision-making about which sections to review"
```

**Q6 (Multi-agent):**
```markdown
- YES: "TriageAgent assesses urgency → DiagnosticAgent suggests tests → TreatmentAgent recommends care plan"
- NO: "Single agent uses tools (EMR lookup, drug database, clinical guidelines) but makes all decisions"
```

**Q8 (Learning):**
```markdown
- YES: "System learns from physician corrections to improve diagnosis suggestions"
- NO: "System follows same clinical decision rules every time"
```

---

### 4. Update Tool Recommendations

**Find the "Typical tools" section for each tier and update:**

**Default (current):**
```markdown
**Tier 2 tools:**
- n8n + Claude/GPT
- Make + OpenAI API
```

**Example for Python-heavy projects:**
```markdown
**Tier 2 tools:**
- Prefect + Anthropic API
- Airflow + Claude integration
- Python scripts + langchain
```

**Example for Microsoft ecosystem:**
```markdown
**Tier 2 tools:**
- Power Automate + Azure OpenAI
- Logic Apps + GPT-4
- Microsoft Graph + Claude
```

---

### 5. Adjust Tier Definitions

If your project uses different tier definitions, update the outcomes:

**Example: 4-tier system instead of 7-tier:**

```markdown
### Q3: Multi-Step Logic (only if NO to Q2)
**Question:** "Does it involve multiple steps or branching logic?"

- If **NO** → **Tier 1** (Simple automation)
- If **YES** → **Tier 2** (Complex automation, no AI)

### Q5: Single AI Call (only if NO to Q4)
**Question:** "Can the AI task be done in ONE API call?"

- If **YES** → **Tier 3** (AI-enhanced automation)
- If **NO** → **Tier 4** (Advanced AI system)
```

---

### 6. Customize Cost Ranges

Update the cost estimates based on your typical usage:

**Example for high-volume enterprise:**
```markdown
**Cost range:**
- **Tier 0-1:** $0-50/month (automation platform fees)
- **Tier 2:** $200-500/month (1000+ AI calls/day)
- **Tier 3:** $500-2000/month (agent with tools)
- **Tier 4:** $2000-5000/month (multi-agent system)
- **Tier 5:** $3000-10000/month (+ human approval overhead)
- **Tier 6:** $5000+/month (custom ML infrastructure)
```

**Example for small team/indie:**
```markdown
**Cost range:**
- **Tier 0-1:** $0-20/month (free tiers + minimal automation)
- **Tier 2:** $20-100/month (50-200 AI calls/day)
- **Tier 3:** $100-300/month (agent with tools)
- **Tier 4:** $300-800/month (multi-agent system)
- **Tier 5:** Not recommended (overhead too high for small team)
- **Tier 6:** Not recommended (infrastructure too complex)
```

---

### 7. Add Domain-Specific Tips

Customize the "QUICK TIPS" section:

**Example for DevOps domain:**
```markdown
**💡 QUICK TIPS:**

- **Tier 0-1:** Use CI/CD webhooks, keep logic in scripts
- **Tier 2:** AI for log analysis, incident triage, release notes
- **Tier 3:** Agent decides which metrics to check, which services to restart
- **Tier 4:** Multi-agent: MonitorAgent → DiagnosticAgent → RemediationAgent
- **Tier 5:** Human approval for production changes, auto-approve staging
- **Tier 6:** Learn optimal deployment windows, auto-tune resource allocation
```

**Example for Content Creation:**
```markdown
**💡 QUICK TIPS:**

- **Tier 0-1:** Schedule posts, auto-format, simple templates
- **Tier 2:** AI generates draft content from outline
- **Tier 3:** Agent researches topic, chooses sources, generates content
- **Tier 4:** ResearchAgent → WriterAgent → EditorAgent → SEOAgent
- **Tier 5:** Human editorial approval before publishing
- **Tier 6:** Learn audience preferences, optimize posting times
```

---

## Testing & Validation

### Test Cases

Run through these scenarios to validate your wizard:

#### Test 1: Simple Automation (Expected: Tier 0)
```
Q1: Any domain
Q2: NO (no AI needed)
Q3: NO (single step)
→ Should output: TIER 0
```

#### Test 2: Multi-Step No AI (Expected: Tier 1)
```
Q1: Any domain
Q2: NO (no AI needed)
Q3: YES (multiple steps)
→ Should output: TIER 1
```

#### Test 3: Single LLM Call (Expected: Tier 2)
```
Q1: Any domain
Q2: YES (needs AI)
Q4: NO (no agent reasoning)
Q5: YES (single call)
→ Should output: TIER 2
```

#### Test 4: Single Agent (Expected: Tier 3)
```
Q1: Any domain
Q2: YES (needs AI)
Q4: YES (agent reasoning)
Q6: NO (single agent)
→ Should output: TIER 3
```

#### Test 5: Multi-Agent (Expected: Tier 4)
```
Q1: Any domain
Q2: YES (needs AI)
Q4: YES (agent reasoning)
Q6: YES (multi-agent)
Q7: NO (no approval)
Q8: NO (no learning)
→ Should output: TIER 4
```

#### Test 6: Human-in-Loop (Expected: Tier 5)
```
Q1: Any domain
Q2: YES (needs AI)
Q4: YES (agent reasoning)
Q6: YES (multi-agent)
Q7: YES (needs approval)
Q8: NO (no learning)
→ Should output: TIER 5
```

#### Test 7: Autonomous Learning (Expected: Tier 6)
```
Q1: Any domain
Q2: YES (needs AI)
Q4: YES (agent reasoning)
Q6: YES (multi-agent)
Q7: YES or NO
Q8: YES (learning)
→ Should output: TIER 6
```

### Validation Checklist

- [ ] Command appears when typing `/tier-wizard`
- [ ] Welcome message displays correctly
- [ ] Questions appear one at a time (not all at once)
- [ ] Decision logic follows correct paths
- [ ] Tier recommendation includes all sections:
  - [ ] What this means
  - [ ] Typical tools
  - [ ] Complexity level
  - [ ] Implementation time
  - [ ] Cost range
- [ ] Template paths point to correct locations
- [ ] Example workflow paths are valid
- [ ] Domain-specific examples are relevant
- [ ] Tool recommendations match your tech stack

---

## Troubleshooting

### Issue: Command not appearing

**Problem:** Typing `/tier-wizard` doesn't show the command

**Solutions:**
1. Verify file is in `.claude/commands/tier-wizard.md`
2. Check file has `.md` extension
3. Ensure frontmatter has `description:` field
4. Restart Claude Code session
5. Check file permissions (should be readable)

### Issue: Questions appear all at once

**Problem:** All questions display instead of one-at-a-time flow

**Solution:**
- This is expected behavior in the markdown - Claude will ask one at a time during execution
- If Claude is asking multiple questions, it's not following instructions
- Verify the "Ask questions ONE AT A TIME" instruction is present

### Issue: Wrong tier recommendation

**Problem:** Wizard recommends incorrect tier for a known workflow

**Solutions:**
1. Trace through decision tree manually with answers
2. Check if conditional logic is correct (Q5: NO should go to Q6, not directly to Tier 3)
3. Verify Q8 logic accounts for both Q7 paths
4. Review examples - they may be confusing the LLM

### Issue: Template paths don't work

**Problem:** Next steps reference non-existent file paths

**Solutions:**
1. Update template paths in "After Determining Tier" section
2. Ensure paths are relative to project root
3. Create example templates at those paths
4. Or update to match your actual structure

### Issue: Domain options too limited

**Problem:** Q1 domains don't cover your use case

**Solutions:**
1. Update Q1 with your specific domains
2. Add "(d) Other - please specify" option
3. Create generic templates if domains vary widely

---

## Advanced Customization

### Adding Tier Sub-Classifications

If you need more granular tiers (e.g., Tier 2A, 2B):

```markdown
### Q5: Single AI Call (only if NO to Q4)
**Question:** "Can the AI task be done in ONE API call?"

- If **YES** → Ask Q5A (synchronous or async?)
  - **Synchronous (real-time response)** → **Tier 2A**
  - **Asynchronous (batch processing)** → **Tier 2B**
- If **NO** → Ask Q6 (multi-agent check)
```

### Adding Cost Calculators

Provide specific cost formulas:

```markdown
**Cost estimate for Tier 2:**

Based on your inputs:
- Expected volume: [X] calls/day
- AI model: Claude Sonnet
- Cost per call: ~$0.02-0.05

**Monthly estimate:** [X calls/day] × 30 days × $0.03 = $[total]/month
```

### Adding Time Estimates

Provide implementation timeline breakdowns:

```markdown
**Estimated implementation time: 2-3 days**

**Breakdown:**
- Day 1: Set up integrations, test APIs (4-6 hours)
- Day 2: Build workflow, configure AI prompts (4-6 hours)
- Day 3: Testing, refinement, documentation (2-4 hours)
```

---

## Integration with Intake Templates

The wizard should reference your intake templates. Ensure these exist:

### Required Files

```
project-root/
├── .claude/
│   └── commands/
│       └── tier-wizard.md          # This wizard
├── get_started/                     # Or your docs folder
│   └── intake_examples/
│       ├── README.md
│       ├── INTAKE_TEMPLATE_[domain-a].md
│       ├── INTAKE_TEMPLATE_[domain-b].md
│       └── INTAKE_TEMPLATE_[domain-c].md
└── [domain-folders]/
    └── tier_examples/
        ├── tier_0/
        ├── tier_1/
        ├── tier_2/
        ├── tier_3/
        ├── tier_4/
        ├── tier_5/
        └── tier_6/
```

### Template References

Update these paths in the wizard to match your structure:

```markdown
1. **Use this template:** `get_started/intake_examples/INTAKE_TEMPLATE_[domain].md`

3. **Review example workflows** in:
   - `[domain]/tier_examples/tier_[X]/`
```

---

## Version Control

### Recommended Git Strategy

```bash
# Add to version control
git add .claude/commands/tier-wizard.md

# Commit with clear message
git commit -m "Add tier routing wizard for automation classification"

# Tag version if part of release
git tag -a v1.0.0 -m "Initial tier wizard release"
```

### Changelog Template

Keep a changelog section in your wizard or separate file:

```markdown
## Changelog

### v1.2.0 (2025-01-15)
- Added Tier 2A/2B sub-classification
- Updated cost estimates for 2025 pricing
- Added 5 new domain-specific examples

### v1.1.0 (2024-12-01)
- Customized for healthcare domain
- Updated Q1 with three healthcare categories
- Added HIPAA compliance considerations

### v1.0.0 (2024-11-17)
- Initial wizard implementation
- Supports 7 tiers (0-6)
- Generic examples for GTM/UE5/BR2
```

---

## Support & Maintenance

### Regular Updates Needed

**Quarterly:**
- [ ] Review and update cost estimates
- [ ] Update tool recommendations (new frameworks)
- [ ] Refresh examples with current best practices

**When adding new domains:**
- [ ] Update Q1 domain options
- [ ] Add domain-specific examples to Q2-Q8
- [ ] Create corresponding intake templates
- [ ] Add example workflows for new domain

**When tier definitions change:**
- [ ] Update decision tree logic
- [ ] Revise all conditional statements
- [ ] Update tier outcome descriptions
- [ ] Adjust tool recommendations

---

## FAQ

### Q: Can I use this for projects without Claude Code?

Yes! The decision tree logic can be implemented in:
- Web forms (JavaScript logic)
- Notion databases (formula fields)
- Spreadsheets (IF statements)
- Chatbots (dialog flow)

### Q: How do I handle edge cases?

Add escape hatches:
```markdown
If you're unsure about any answer, or if your workflow doesn't fit these questions:
- Choose the LOWER tier (easier to upgrade than downgrade)
- Consult the full tier definitions in the documentation
- Request a manual tier assessment from the automation team
```

### Q: Can I skip questions?

Yes, allow skips and handle them:
```markdown
If user says "skip" or "unsure":
- Ask a clarifying question with concrete examples
- If still unsure, recommend the lower tier
- Flag for manual review
```

### Q: Should I add more questions?

Only if necessary. Guidelines:
- Keep total questions ≤10
- Each question should definitively route to different outcomes
- Avoid questions that duplicate decision logic
- Test with real users - remove questions they always answer the same way

---

## License & Attribution

```markdown
# Tier Routing Wizard
Created: 2024-11-17
License: MIT (or your preferred license)
Attribution: [Your name/organization]

Feel free to customize and distribute this wizard for your automation projects.
```

---

## Complete Example: Healthcare Implementation

Here's a fully customized example for a healthcare organization:

**File:** `.claude/commands/tier-wizard.md`

```markdown
---
description: Determine the right automation tier for healthcare workflow automation
---

You are the Healthcare Automation Tier Wizard. Help users classify their clinical and administrative workflows into the correct automation tier (0-6).

## Instructions

Ask questions ONE AT A TIME. Keep responses HIPAA-conscious and clinical-terminology friendly.

**🏥 Welcome to the Healthcare Automation Tier Wizard!**

I'll help you determine the right automation tier for your clinical or administrative workflow.

This takes 2-3 minutes. Answer with **yes** or **no**.

Ready? Let's start!

---

## Question Flow

### Q1: Domain Context
**Question:** "Is this workflow for: (a) Patient Care, (b) Administrative Operations, or (c) Clinical Research?"

---

### Q2: AI Requirement - Basic
**Question:** "Does this workflow need AI to understand clinical context or make care-related decisions? (e.g., interpret symptoms, analyze medical images, reason about treatments)"

Healthcare examples:
- YES: "Analyze patient symptoms to suggest relevant diagnostic tests"
- NO: "Route lab results marked 'CRITICAL' to attending physician"

- If **NO** → Ask Q3
- If **YES** → Ask Q4

---

### Q3: Multi-Step Logic (only if NO to Q2)
**Question:** "Does it involve multiple steps or complex routing? (e.g., if-then protocols, escalation paths, multiple system integrations)"

Healthcare examples:
- YES: "If lab value > threshold → notify physician → if no response in 15min → escalate to charge nurse"
- NO: "When patient checks in → send appointment reminder SMS"

- If **NO** → **Tier 0** (Simple automation)
- If **YES** → **Tier 1** (Multi-step automation, no AI)

---

[Continue with Q4-Q8 following the same pattern, with healthcare-specific examples]

---

## After Determining Tier

**🎯 TIER RECOMMENDATION: Tier [X]**

**Healthcare Implementation Notes:**
[Tier-specific HIPAA considerations, clinical validation requirements, etc.]

**Typical tools for healthcare:**
- **Tier 0:** HL7 triggers, simple webhooks
- **Tier 1:** Mirth Connect, n8n with EMR integrations
- **Tier 2:** n8n + Claude (HIPAA-compliant deployment)
- **Tier 3:** LangChain + healthcare tools (clinical databases, drug interactions)
- **Tier 4:** Multi-agent clinical decision support
- **Tier 5:** Clinical decision support with physician approval
- **Tier 6:** Adaptive clinical protocols with continuous learning

**Compliance considerations:**
- HIPAA BAA required for Tier 2+
- Clinical validation needed for Tier 3+
- FDA approval may be required for Tier 4+ (check regulations)

**📋 NEXT STEPS:**

1. **Use this template:** `docs/intake/INTAKE_TEMPLATE_[domain].md`
2. **Clinical validation:** Consult with medical director for Tier 3+
3. **Review example workflows:** `healthcare/tier_examples/tier_[X]/`
4. **Compliance check:** Review with compliance officer for PHI handling

**Would you like to:**
- (a) Review HIPAA-compliant implementation examples
- (b) Discuss clinical validation requirements
- (c) Explore similar healthcare workflows
- (d) Start over with a different workflow
```

---

## Summary Checklist

Before deploying your customized wizard:

- [ ] Created `.claude/commands/tier-wizard.md`
- [ ] Copied complete file content
- [ ] Updated Q1 domain options
- [ ] Added domain-specific examples (Q2-Q8)
- [ ] Updated template file paths
- [ ] Updated example workflow paths
- [ ] Customized tool recommendations
- [ ] Adjusted cost estimates
- [ ] Added domain-specific compliance notes
- [ ] Tested with 7 test cases (one per tier)
- [ ] Validated all file paths exist
- [ ] Documented customizations
- [ ] Added to version control
- [ ] Trained team on usage

---

**You're ready to deploy the Tier Routing Wizard!** 🎉

For questions or issues, refer to the Troubleshooting section or consult the decision tree reference.
