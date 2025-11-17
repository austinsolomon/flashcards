# Automation Intake Request Templates

This directory contains domain-specific intake templates to help you submit well-structured automation requests. A good intake form is critical for routing your automation to the correct tier (0-6) and ensuring successful implementation.

---

## Available Templates

### 1. **GTM (Marketing) - INTAKE_TEMPLATE_GTM.md**
For go-to-market, marketing, and sales automation workflows.

**Use this template for:**
- Lead enrichment and qualification
- Campaign analysis and reporting
- Email personalization and outreach
- CRM data management
- Marketing attribution and analytics
- Content generation for marketing

**Example workflows:**
- Auto-generate inbound lead intelligence summaries
- Campaign anomaly detection and alerts
- Lead scoring and routing
- Email sequence personalization
- Content outline generation for blog posts

---

### 2. **UE5 (Game Development) - INTAKE_TEMPLATE_UE5.md**
For Unreal Engine 5 and game development automation workflows.

**Use this template for:**
- Asset validation and quality checks
- 3D model processing and import
- Material/shader automation
- Level design workflow optimization
- Build pipeline automation
- Performance profiling and optimization

**Example workflows:**
- Asset quality validator with vision AI
- Blueprint documentation generator
- Automated lighting setup
- Collision mesh generation
- Material instance batch creation
- Performance anomaly detection

---

### 3. **BR2 (Personal Productivity) - INTAKE_TEMPLATE_BR2.md**
For personal knowledge management and productivity automation workflows.

**Use this template for:**
- Note-taking and knowledge capture
- Task management and GTD workflows
- PARA methodology automation
- Reading/research processing
- Meeting notes and action items
- Daily/weekly review automation

**Example workflows:**
- Article processing with PARA filing
- Email inbox triage to Obsidian
- Meeting notes → action items extractor
- Daily note template generation
- Weekly review preparation
- Reading list prioritization

---

## How to Use These Templates

### Step 1: Choose Your Template
Select the template that matches your domain:
- **Business/Marketing workflows** → GTM template
- **Game development workflows** → UE5 template
- **Personal productivity workflows** → BR2 template

### Step 2: Fill Out All Sections
Complete each section thoroughly:
1. **Problem Statement** - Clearly articulate the pain point
2. **Current Manual Process** - Document every step (be specific!)
3. **Desired Automation** - Define input, process, and output
4. **Success Criteria** - Set measurable goals
5. **Constraints & Requirements** - List integrations, technical limits
6. **Complexity Signals** - Check boxes honestly (this determines tier)
7. **Nice-to-haves** - Future features (helps with roadmap)
8. **Additional Context** - Team structure, current pain points

### Step 3: Self-Assess Complexity Tier
Use the "Complexity Signals" section to estimate which tier your automation belongs to:

| Tier | Characteristics | Common Tools |
|------|----------------|--------------|
| **Tier 0** | No-code, single-app, simple triggers | iOS Shortcuts, Zapier triggers |
| **Tier 1** | Multi-step logic, no LLM, scheduled/triggered | n8n, Make, Zapier |
| **Tier 2** | ONE LLM call, semantic routing, event-driven | n8n + Claude/GPT |
| **Tier 3** | LLM agent with tools, multi-step reasoning | LangChain, LlamaIndex |
| **Tier 4** | Multi-agent orchestration, specialized agents | CrewAI, AutoGen |
| **Tier 5** | Human-in-loop, approval workflows, compliance | n8n + agents + approvals |
| **Tier 6** | Autonomous learning, feedback loops, optimization | Custom ML + LLMs |

### Step 4: Submit Your Intake
Once completed:
- Save your filled template as `INTAKE_[workflow-name].md`
- Submit for review/routing
- Expect clarifying questions about complexity signals or success criteria

---

## Why Use These Templates?

### ✅ Better Routing
The structured format helps automation architects quickly assess:
- Which tier (0-6) is appropriate
- What tools/frameworks to use
- Time/cost estimates
- Feasibility and risks

### ✅ Clearer Requirements
Forces you to think through:
- Exact pain points and metrics
- All systems that need to integrate
- What "done" looks like
- Constraints that might block implementation

### ✅ Faster Implementation
A well-written intake means:
- Less back-and-forth clarification
- Fewer missed requirements
- Accurate tier selection = right tool for the job
- Clear success criteria = easier testing

### ✅ Reusable Patterns
After your first automation is built:
- Use it as a template for similar workflows
- Iterate and improve based on learnings
- Build a library of proven patterns

---

## Common Mistakes to Avoid

### ❌ Vague Problem Statements
**Bad:** "I want to save time on lead research"
**Good:** "BDRs spend 10-15 min/lead manually researching companies, reducing daily capacity from 20 to 12 qualified conversations"

### ❌ Missing Integration Details
**Bad:** "Integrate with our CRM"
**Good:** "Must integrate with Salesforce (API v58), ZoomInfo (100 req/min limit), Marketo (webhook trigger), and Slack (webhook notifications)"

### ❌ Unrealistic Success Criteria
**Bad:** "Make everything instant and perfect"
**Good:** "Reduce lead research time from 10min to <30sec, maintaining >90% email personalization quality per BDR spot-check"

### ❌ Under-estimating Complexity
**Bad:** Checking "Tier 1" for a workflow that needs multi-agent reasoning
**Good:** Honestly assess if your workflow needs:
- ONE LLM call → Tier 2
- Agent with tools → Tier 3
- Multiple agents → Tier 4

### ❌ Over-scoping First Automation
**Bad:** "Automate our entire sales process end-to-end"
**Good:** "Start with inbound lead intelligence summaries (one workflow), then expand to other stages"

---

## Template Customization

These templates are **starting points**. Feel free to:
- Add domain-specific sections (e.g., "Art Style Guidelines" for UE5)
- Remove irrelevant sections (e.g., "API rate limits" if not applicable)
- Merge templates for hybrid workflows (e.g., UE5 + GTM for game marketing)

**Core sections to always include:**
1. Problem Statement
2. Current Process
3. Desired Automation (Input/Process/Output)
4. Success Criteria
5. Complexity Signals

---

## Examples of Well-Written Intakes

Each template includes a fully worked example. Study these to see:
- Level of detail expected
- How to articulate pain points
- How to map manual steps to automation
- How to set measurable success criteria

---

## Next Steps

1. **Choose your template** based on domain
2. **Fill it out completely** (don't skip sections!)
3. **Self-assess complexity tier** using signals
4. **Submit for review** and routing
5. **Iterate** based on feedback
6. **Build** your first automation
7. **Use as pattern** for future workflows

---

## Questions?

If you're unsure which template to use or how to fill out a section:
- Check the example workflows in each template
- Review the tier definitions in the main README
- Look at existing implemented workflows in `br2/`, `ue5/`, or `gtm/` directories
- Ask for help with specific sections rather than submitting incomplete intake

**Remember:** 10 minutes spent on a thorough intake saves hours in implementation!
