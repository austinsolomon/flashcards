# AI System Compliance Checker

**Tier**: 2 (Context-Aware AI)
**Category**: Special Task - Responsive Legal Framework

## Purpose

Automated compliance checking for AI systems against current regulations. Generates compliance checklists and identifies gaps before they become violations.

## What It Does

- Evaluates AI systems against regulatory requirements
- Generates compliance checklists (EU AI Act, NYC LL144, etc.)
- Identifies documentation gaps
- Assesses risk classification
- Creates compliance reports
- Provides remediation guidance

## Compliance Frameworks

**EU AI Act:**
- Risk classification (prohibited, high, limited, minimal)
- Requirements by risk level
- Documentation standards
- Conformity assessment needs

**US Regulations:**
- NYC Local Law 144 (bias audits)
- California CPRA (automated decisions)
- Colorado AI Act (algorithmic discrimination)
- Sector-specific (HIPAA, FCRA, etc.)

**Industry Standards:**
- NIST AI Risk Management Framework
- ISO/IEC 42001 (AI Management System)
- IEEE Ethics Guidelines

## Usage

```bash
# Check AI system compliance
python compliance_checker.py --system ai_system.yaml --framework eu-ai-act

# Generate full compliance report
python compliance_checker.py --system recruitment_ai --all-frameworks --report

# Identify gaps only
python compliance_checker.py --system medical_ai --gaps-only

# Create remediation plan
python compliance_checker.py --system chatbot --remediation-plan
```

## Example Output

```markdown
# AI System Compliance Report
System: Recruitment Screening AI
Date: 2025-11-18
Frameworks: EU AI Act, NYC LL144, NIST AI RMF

## EU AI Act Compliance

**Risk Classification:** HIGH RISK ⚠️
Category: Employment and worker management (Annex III, 4.a)

**Overall Compliance:** 45% ✅ | 55% ⚠️

### Requirements Checklist

Risk Management (Art. 9):
- [x] Risk identification process documented
- [ ] Risk mitigation measures implemented
- [ ] Residual risk evaluation
- [ ] Testing for risk mitigation
Compliance: 25% ⚠️ INCOMPLETE

Data Governance (Art. 10):
- [x] Training data documented
- [ ] Bias in training data assessed
- [ ] Data quality measures documented
- [ ] Data relevance to purpose verified
Compliance: 25% ⚠️ INCOMPLETE

[... detailed checklist continues ...]

### Priority Gaps

🔴 CRITICAL: Human Oversight (Art. 14)
Status: Not implemented
Requirement: "High-risk AI systems shall be designed and developed
in such a way that they can be effectively overseen by natural persons"
Remediation: Implement human review for final hiring decisions

🟡 MODERATE: Accuracy Metrics (Art. 15)
Status: Partially implemented
Requirement: Appropriate accuracy levels documented
Remediation: Conduct formal accuracy assessment

## NYC Local Law 144 Compliance

Overall Compliance: 20% ⚠️ NON-COMPLIANT

Requirements:
- [ ] Annual bias audit by independent auditor (MISSING)
- [ ] Audit results published on website (MISSING)
- [x] Notice to candidates (IMPLEMENTED)
- [ ] Alternative selection process (UNDOCUMENTED)

**COMPLIANCE DEADLINE:** Effective immediately (overdue)
**RISK:** $1,500 fine per violation

## Remediation Roadmap

### Immediate (This Month)
1. Engage bias auditor for NYC LL144
2. Document alternative selection process
3. Begin human oversight implementation

### Short-term (1-3 Months)
4. Complete and publish bias audit
5. Conduct bias assessment on training data
6. Formalize risk management system

### Medium-term (3-6 Months)
7. Implement all Art. 15 requirements
8. Complete technical documentation
9. Prepare for conformity assessment

Cost: $100K - $175K
Timeline: 6 months to full compliance
```

## Files

- `compliance_checker.py` - Main checking engine
- `frameworks/` - Regulatory requirement definitions
- `checklist_generator.py` - Creates compliance checklists
- `gap_analyzer.py` - Identifies missing requirements
- `remediation_planner.py` - Creates action plans
