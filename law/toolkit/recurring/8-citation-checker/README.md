# Citation Checker & Formatter

**Tier**: 1 (Simple Automation)
**Category**: Recurring Development

## Purpose

Validates and formats legal citations according to Bluebook or local court rules. Ensures citation accuracy and consistency.

## What It Does

- Validates citations against legal databases
- Formats citations (Bluebook, ALWD, local rules)
- Checks if cases still good law (Shepardizing)
- Identifies citation errors
- Auto-corrects common mistakes
- Generates citation tables

## Usage

```bash
# Check citations in document
python citation_checker.py --document brief.docx --format bluebook

# Validate case law citations
python citation_checker.py --check-validity --document memo.pdf

# Generate table of authorities
python citation_checker.py --toa --document motion.docx

# Fix citation format
python citation_checker.py --fix --document draft.docx --rules "N.D. Cal."
```

## Example Output

```
Citation Check Report

Document: Motion for Summary Judgment
Court: N.D. Cal.

ERRORS FOUND: 4

1. Line 23: "Iqbal v. Ashcroft, 556 U.S. 662"
   ❌ Incorrect party order
   ✅ Should be: "Ashcroft v. Iqbal, 556 U.S. 662, 678 (2009)"

2. Line 45: "42 U.S.C. 2000e"
   ⚠️ Missing subdivision
   ✅ Should be: "42 U.S.C. § 2000e(b)"

3. Line 67: "Mobley v. Workday, N.D. Cal. 2023"
   ❌ Incomplete citation
   ✅ Should be: "Mobley v. Workday, Inc., No. 3:23-cv-00770 (N.D. Cal. 2023)"

4. Line 89: "Smith v. Jones, 123 F.3d 456 (9th Cir. 1995)"
   ⚠️ Negative treatment
   Warning: This case was questioned by Brown v. Board, 456 F.3d 789 (9th Cir. 2010)

Auto-fix available? (y/n)
```

## Files

- `citation_checker.py` - Main validation tool
- `bluebook_rules.yaml` - Citation format rules
- `legal_db_integration/` - Westlaw/Lexis API
- `table_generator.py` - Creates tables of authorities
