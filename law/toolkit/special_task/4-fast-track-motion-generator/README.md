# Fast-Track Legal Motion Generator

**Tier**: 2 (Context-Aware AI)
**Category**: Special Task - Responsive Legal Framework

## Purpose

Rapidly generates legal motions and briefs for technology-related cases. Accelerates legal response times using Claude for research and drafting while maintaining quality.

## What It Does

- Generates motion drafts from fact patterns
- Incorporates relevant precedents automatically
- Creates jurisdiction-specific formatting
- Drafts supporting memoranda
- Generates discovery requests
- Produces client advisories

## Motion Types

**Litigation:**
- Motion to Dismiss (12(b)(6), lack of standing, etc.)
- Motion for Summary Judgment
- Motion for Preliminary Injunction
- Motion to Compel Discovery
- Motion in Limine

**Regulatory:**
- Comments on proposed regulations
- Administrative appeals
- Freedom of Information Act requests

**Transactional:**
- Opinion letters
- Demand letters
- Cease and desist letters

## Usage

```bash
# Generate motion from template
python motion_generator.py --type motion-to-dismiss \
  --facts case_facts.txt \
  --jurisdiction "N.D. Cal."

# Emergency motion (injunction)
python motion_generator.py --emergency --type prelim-injunction \
  --facts emergency_facts.txt --deadline "24h"

# Full brief with research
python motion_generator.py --type summary-judgment \
  --research --auto-cite --output brief.docx
```

## Example Output

```markdown
# Motion Generation Preview

Input: Motion to Dismiss - AI discrimination case
Jurisdiction: Northern District of California
Deadline: 24 hours

Generated Documents:
1. Notice of Motion
2. Memorandum of Points and Authorities (18 pages)
3. Proposed Order
4. Proof of Service

---

MEMORANDUM OF POINTS AND AUTHORITIES IN SUPPORT OF
DEFENDANT'S MOTION TO DISMISS PURSUANT TO FRCP 12(b)(6)

I. INTRODUCTION

Defendant Acme AI Corp. ("Acme") respectfully moves to dismiss
Plaintiff's complaint for failure to state a claim upon which
relief can be granted. Plaintiff alleges that Acme's hiring
algorithm discriminated against them in violation of Title VII
of the Civil Rights Act of 1964. However, Plaintiff's complaint
fails to allege facts sufficient to establish that Acme was
Plaintiff's "employer" under Title VII, that Plaintiff suffered
an adverse employment action, or that any alleged discrimination
was causally connected to Plaintiff's protected characteristics.

II. LEGAL STANDARD

To survive a motion to dismiss under Rule 12(b)(6), "a complaint
must contain sufficient factual matter, accepted as true, to
state a claim to relief that is plausible on its face."
Ashcroft v. Iqbal, 556 U.S. 662, 678 (2009).

[continues with detailed legal analysis...]

III. ARGUMENT

A. Plaintiff Fails to Allege that Acme Was Their Employer

Title VII prohibits discrimination by an "employer," defined as
a person "who has fifteen or more employees." 42 U.S.C. § 2000e(b).
Here, Plaintiff applied for a position with XYZ Corp., not Acme.
Acme merely provided software used by XYZ Corp. in its hiring
process. Plaintiff does not allege that Acme exercised control
over their employment relationship with XYZ Corp., nor do they
allege facts establishing an agency or joint employer relationship.

[Legal analysis continues with case citations...]

[Auto-generated citations include:]
- Mobley v. Workday, Inc., No. 3:23-cv-00770 (N.D. Cal. 2023)
- Nationwide Mut. Ins. Co. v. Darden, 503 U.S. 318 (1992)
- Bristol-Myers Squibb Co. v. Superior Court, 582 U.S. 255 (2017)

---

Processing Time: 8 minutes
Word Count: 4,847
Citations: 23
Pages: 18

Ready for attorney review and filing.
```

## Quality Controls

- **Attorney Review Required** - All outputs are drafts
- **Citation Verification** - Auto-check citations against Westlaw
- **Jurisdiction Formatting** - Court-specific rules applied
- **Privilege Review** - Flags potential privilege issues
- **Ethics Check** - Identifies potential conflicts

## Files

- `motion_generator.py` - Main drafting engine
- `templates/` - Motion templates by type
- `precedent_integrator.py` - Auto-inserts relevant cases
- `citation_formatter.py` - Bluebook/local rules
- `emergency_mode.py` - Accelerated generation for tight deadlines
