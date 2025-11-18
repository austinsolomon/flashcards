# Contract Review Automation

**Tier**: 2 (Context-Aware AI)
**Category**: Recurring Development

## Purpose

AI-powered contract review and analysis using Claude. Identifies risks, unusual terms, and missing provisions in agreements.

## What It Does

- Analyzes contracts for risks and red flags
- Compares against standard terms
- Identifies missing clauses
- Extracts key terms and obligations
- Generates redline suggestions
- Creates executive summaries

## Contract Types

- Software/SaaS agreements
- Data processing agreements
- Employment contracts
- Vendor agreements
- Partnership agreements
- Privacy policies and terms of service

## Usage

```bash
# Review single contract
python contract_review.py --contract vendor_agreement.pdf

# Compare to standard template
python contract_review.py --contract saas_agreement.pdf --template standard_saas.docx

# Batch review multiple contracts
python contract_review.py --folder contracts/ --priority high-value
```

## Example Output

```markdown
# Contract Review Summary
Document: Vendor SaaS Agreement
Client: Acme Corp
Date: 2025-11-18

## Risk Assessment: MODERATE ⚠️

### High-Priority Issues (3)

1. **Unlimited Liability** 🔴 HIGH RISK
   Location: Section 8.2
   Issue: "Vendor's liability is unlimited for any breach"
   Risk: Exposure could exceed contract value by 100x
   Recommendation: Cap liability at 12 months fees or $500K

2. **Broad IP Assignment** 🔴 HIGH RISK
   Location: Section 10.1
   Issue: "All IP created using the software belongs to Vendor"
   Risk: Lose ownership of custom configurations, integrations
   Recommendation: Limit to Vendor's background IP only

3. **Auto-Renewal Without Notice** ⚠️ MODERATE RISK
   Location: Section 3.4
   Issue: "Agreement auto-renews unless terminated 90 days prior"
   Risk: Unintended renewal, budget impact
   Recommendation: Require affirmative renewal consent

### Missing Provisions (5)

- ❌ Data security requirements (critical for SaaS)
- ❌ Service level agreement (SLA) / uptime guarantee
- ❌ Data portability on termination
- ❌ GDPR/CCPA compliance warranties
- ❌ Indemnification for IP infringement

### Favorable Terms ✅

- ✅ 30-day payment terms (industry standard)
- ✅ Termination for convenience with 60 days notice
- ✅ Confidentiality provisions (mutual, reasonable)

## Recommended Redlines

1. Section 8.2 - Cap Liability
   FROM: "unlimited liability"
   TO: "limited to fees paid in 12 months preceding claim, max $500,000"

2. Section 10.1 - Clarify IP Ownership
   ADD: "excluding Client's data, configurations, and custom integrations"

3. NEW Section 5 - Service Levels
   ADD: "99.9% uptime SLA with service credits for downtime"

[... detailed recommendations continue ...]
```

## Files

- `contract_review.py` - Main review engine
- `risk_patterns.yaml` - Common contract risks
- `clause_library/` - Standard contract clauses
- `redline_generator.py` - Creates markup suggestions
