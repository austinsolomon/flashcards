# Workflow Automation Intake System

## Overview

The Intake System is the entry point for all workflow automation requests. It provides a structured process for submitting, validating, routing, and tracking automation workflows through the tiered architecture.

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Database

```bash
# Create PostgreSQL database
createdb automation_db

# Run schema
psql -U your_user -d automation_db < intake_database_schema.sql
```

### 3. Configure Environment

Create `.env` file in the project root:

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=automation_db
POSTGRES_USER=automation_user
POSTGRES_PASSWORD=your_password
```

### 4. Submit a Workflow

```bash
# Interactive mode
python submit_workflow.py --interactive

# From YAML file
python submit_workflow.py --file my_workflow.yaml

# Export template first
python submit_workflow.py --export-template my_workflow.yaml
```

---

## Files in This System

| File | Purpose |
|------|---------|
| `intake_form_template.md` | Comprehensive 7-section intake form with examples |
| `submission_guide.md` | Detailed guide for filling out the form correctly |
| `intake_database_schema.sql` | PostgreSQL schema for storing submissions |
| `submit_workflow.py` | CLI tool for submitting workflows |
| `requirements.txt` | Python dependencies |
| `README.md` | This file |

---

## Workflow Submission Process

```
┌─────────────────────────────────────────────┐
│ 1. PREPARE                                  │
│ - Review submission_guide.md                │
│ - Gather time estimates and data            │
│ - Validate with team doing the work         │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ 2. FILL OUT INTAKE FORM                     │
│ Option A: Use intake_form_template.md       │
│ Option B: Create YAML file                  │
│ Option C: Use interactive CLI               │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ 3. VALIDATE                                 │
│ python submit_workflow.py --file x.yaml     │
│     --validate-only                         │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ 4. SUBMIT                                   │
│ python submit_workflow.py --file x.yaml     │
│ → Receives submission ID (e.g., WF-2024-001)│
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ 5. REVIEW (1-2 business days)               │
│ - Intake team reviews for completeness      │
│ - May request clarification                 │
│ - Status: Submitted → Under Review          │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ 6. TIER ASSIGNMENT (automated or manual)    │
│ - Complexity signals → Tier (0-6)           │
│ - ROI calculation                           │
│ - Priority ranking                          │
│ - Status: Under Review → Approved           │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ 7. IMPLEMENTATION                           │
│ - Added to backlog                          │
│ - Assigned to implementation team           │
│ - Built using tier-appropriate tools        │
│ - Status: Approved → In Development         │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ 8. DEPLOYMENT & MEASUREMENT                 │
│ - Deployed to production                    │
│ - Success metrics tracked                   │
│ - Feedback collected                        │
│ - Status: In Development → Deployed         │
└─────────────────────────────────────────────┘
```

---

## The 7-Section Intake Form

### Section 1: Problem Statement
**Purpose:** Convince reviewers this is worth automating

**Required:**
- Clear pain point description
- Quantified business impact
- Who is affected and how often

---

### Section 2: Current Manual Process
**Purpose:** Understand what to replicate and improve

**Required:**
- Step-by-step process
- Tools used in each step
- Time per occurrence
- Frequency

**Auto-calculated:**
- Total weekly hours

---

### Section 3: Desired Automation
**Purpose:** Define automation scope

**Required:**
- **Input:** Trigger and data sources
- **Process:** What automation does (step-by-step)
- **Output:** What gets created/updated and where

---

### Section 4: Success Criteria
**Purpose:** Define measurable outcomes

**Required:**
- Before/after metrics
- How you'll measure them
- Quality checks (not just speed)

---

### Section 5: Constraints & Requirements
**Purpose:** Surface technical and business limitations

**Include:**
- Required integrations (with API details)
- Cost constraints
- Volume/scale requirements
- Compliance requirements (SOC 2, GDPR, HIPAA)
- Security requirements
- Human approval gates

---

### Section 6: Complexity Signals
**Purpose:** Help route to correct tier (0-6)

**Check all that apply:**
- **Decision Complexity:** Contextual reasoning, NLG, multi-source synthesis
- **Integration Complexity:** 3+ systems, rate limits, webhooks
- **State Management:** Multi-step coordination, long-running, human gates

**Include:**
- Suggested tier (0-6)
- Reasoning for tier suggestion

---

### Section 7: Additional Context
**Purpose:** Capture everything else

**Optional but helpful:**
- Current workarounds
- Related workflows
- Known edge cases
- Dependencies
- Nice-to-haves (future iterations)

---

## Using the CLI Tool

### Export Template

```bash
# YAML format (recommended)
python submit_workflow.py --export-template my_workflow.yaml

# JSON format
python submit_workflow.py --export-template my_workflow.json --format json
```

### Fill Out Template

Edit the exported file with your workflow details:

```yaml
submitted_by: john.doe@company.com
department: BDR
priority: High
problem_statement: |
  BDRs waste 10-15 min/lead manually researching companies before outreach,
  reducing capacity from 20 to 12 qualified conversations per day.

current_process:
  - step: 1
    description: Receive Slack notification of new Marketo lead
    tool: Slack
  - step: 2
    description: Open Salesforce, copy company name
    tool: Salesforce
  # ... more steps

time_per_occurrence_minutes: 12
frequency_per_period: 25
frequency_period: day
people_affected: 8

# ... rest of sections
```

### Validate

```bash
python submit_workflow.py --file my_workflow.yaml --validate-only
```

**Output:**
```
✓ Validation passed
Validate-only mode. Not submitting to database.
```

### Submit

```bash
python submit_workflow.py --file my_workflow.yaml
```

**Output:**
```
✓ Loaded submission from my_workflow.yaml
✓ Validation passed
✓ Submission successful!
Submission ID: WF-2024-001

Next Steps:
1. Your submission will be reviewed within 1-2 business days
2. You'll receive tier assignment and ROI estimate
3. Approved workflows are prioritized and scheduled for build
```

### Interactive Mode

```bash
python submit_workflow.py --interactive
```

The CLI will prompt you for each required field. This is good for quick submissions but YAML files are recommended for complex workflows.

---

## Database Schema

The intake system uses PostgreSQL with the following key tables:

### `intake.workflow_submissions`
Stores all submitted workflows with complete intake form data.

**Key fields:**
- `submission_id` - Unique ID (e.g., WF-2024-001)
- `status` - Submitted, Under Review, Approved, In Development, Deployed
- `assigned_tier` - Tier 0-6
- `roi_score` - (Annual Savings / Build Cost)
- All 7 sections of intake form

### `intake.tier_routing_log`
Logs all tier assignment decisions (automated + manual).

**Tracks:**
- Complexity scores
- Recommended tier + reasoning
- Confidence level
- Human overrides

### `intake.workflow_executions`
Tracks individual executions of deployed workflows.

**Metrics:**
- Duration
- Cost (API calls, tokens)
- Success/failure rate
- Performance data

### `intake.success_metrics`
Compares expected vs. actual success criteria.

**Measures:**
- Time savings (actual vs. target)
- Quality metrics
- Business impact
- ROI validation

### `intake.workflow_feedback`
User feedback and iteration requests.

**Captures:**
- Usefulness/quality ratings
- What worked well
- What needs improvement
- Bug reports

### Views

- `intake.pending_review` - Submissions needing review (sorted by priority + ROI)
- `intake.roi_ranking` - Top automation candidates by ROI score
- `intake.workflow_performance` - Performance dashboard for deployed workflows
- `intake.tier_routing_accuracy` - Routing accuracy analysis

---

## Querying Submissions

### View Pending Submissions

```sql
SELECT * FROM intake.pending_review;
```

### Top ROI Candidates

```sql
SELECT
    submission_id,
    department,
    problem_statement,
    total_weekly_hours,
    roi_score
FROM intake.roi_ranking
LIMIT 10;
```

### Workflow Performance

```sql
SELECT * FROM intake.workflow_performance
WHERE department = 'BDR'
ORDER BY avg_usefulness_score DESC;
```

### Search by Keyword

```sql
SELECT submission_id, problem_statement, department
FROM intake.workflow_submissions
WHERE to_tsvector('english', problem_statement) @@ to_tsquery('lead & research')
AND status = 'Submitted';
```

---

## Tier Assignment Logic

Workflows are routed to tiers based on complexity signals:

### Tier 0-1: Simple Automation
- ❌ No AI/LLM needed
- ❌ No complex integrations
- ✅ Deterministic logic
- ✅ Simple triggers or scheduled tasks

**Tools:** iOS Shortcuts, n8n basic workflows

---

### Tier 2-3: AI-Powered Workflows
- ✅ Requires AI for reasoning, synthesis, or NLG
- ✅ Orchestrates 2-5 API integrations
- ✅ Single-pass execution (no complex state)
- ❌ No multi-agent coordination

**Tools:** n8n + Claude API, LangChain agents

---

### Tier 4-5: Multi-Agent Systems
- ✅ Requires multiple specialized agents
- ✅ Complex state management
- ✅ Recursive task decomposition
- ❌ Not fully autonomous (human oversight)

**Tools:** LangGraph, CrewAI

---

### Tier 6: Autonomous Agents
- ✅ Ongoing autonomous decision-making
- ✅ Learning from feedback over time
- ✅ Full domain authority
- ✅ Persistent memory and context

**Tools:** Full stack orchestrated by Claude Code

---

## ROI Calculation

```
ROI Score = (Annual Cost Savings) / (Build Cost)

Where:
  Annual Cost Savings = Weekly Hours Saved × $100/hr × 52 weeks
  Build Cost = Estimated Build Hours × $150/hr + Infrastructure Costs

Example:
  Weekly Hours Saved: 80 hours
  Annual Savings: 80 × $100 × 52 = $416,000
  Build Hours: 40 hours
  Build Cost: 40 × $150 = $6,000
  ROI Score: $416,000 / $6,000 = 69.3
```

Workflows are prioritized by ROI score within each tier.

---

## Best Practices

### Before Submitting

✅ **DO:**
- Time the manual process yourself (don't guess)
- Validate time estimates with 3+ team members
- List ALL systems that need to integrate
- Note compliance/security requirements upfront
- Define measurable success criteria
- Document edge cases

❌ **DON'T:**
- Combine multiple workflows into one submission
- Use vague terms ("streamline", "optimize")
- Skip the submission guide
- Forget to check with IT about API access

### Writing Problem Statements

**Good:**
```
BDRs waste 10-15 min/lead manually researching companies, reducing
daily capacity from 20 to 12 qualified conversations.
```
- ✅ Specific time (10-15 min)
- ✅ Quantified impact (20 → 12)
- ✅ Clear business metric (qualified conversations)

**Bad:**
```
Lead research takes too long and we need to be more efficient.
```
- ❌ "Too long" - how long?
- ❌ "More efficient" - not measurable

### Defining Success Criteria

Include multiple dimensions:

- **Time Savings:** 12min → <1min per lead
- **Capacity:** 12 → 20+ qualified conversations per day
- **Speed:** 2hrs → 15min first response time
- **Quality:** 4.2/5 email personalization score maintained

Don't just measure speed - measure quality too!

---

## Integration with Workflow Discovery System

The intake system integrates with the [Department Workflow Mapper](/gtm/department_workflow_mapper/):

1. **Discover** workflows using discovery prompts
2. **Receive** 10 ranked candidates with intake previews
3. **Copy/paste** "ready-to-submit" previews into YAML file
4. **Expand** with specific details (tools, teams, constraints)
5. **Submit** via this intake system

This creates a complete pipeline from discovery → intake → routing → build.

---

## Support

### Documentation
- Full intake form: `intake_form_template.md`
- Submission guide: `submission_guide.md`
- Database schema: `intake_database_schema.sql`

### Getting Help
- **Before submitting:** Review `submission_guide.md` thoroughly
- **Questions:** automation-intake@yourcompany.com
- **Slack:** #automation-requests
- **Office Hours:** Tuesdays 2-3pm

### After Submission
- Confirmation: Within 1 business day
- Tier assignment: Within 2 business days
- Implementation timeline: Within 3 business days
- Clarification call: Scheduled if needed (30 min)

---

## Future Enhancements

**Phase 2 (Planned):**
- Web UI for submissions (alternative to CLI)
- Auto-routing with ML classifier
- Slack bot for status updates
- Integration with Jira/Linear for implementation tracking
- Email notifications for status changes

**Phase 3 (Future):**
- Auto-suggest related workflows
- Historical ROI tracking
- A/B testing for tier assignments
- Feedback loop for classifier improvement
