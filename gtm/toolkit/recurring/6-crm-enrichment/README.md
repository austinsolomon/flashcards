# CRM Data Enrichment

**Tier**: 2 (Context-Aware AI)
**Category**: Recurring Development

## Purpose

Automatically enriches CRM records with company data, social profiles, funding info, and tech stack details. Keeps lead data fresh and actionable.

## What It Does

- Enriches contact/company records automatically
- Pulls data from Clearbit, Apollo, LinkedIn, Crunchbase
- Updates company size, revenue, funding, tech stack
- Finds missing email addresses and phone numbers
- Identifies decision-makers
- Tracks company changes (funding, hiring, leadership)

## Usage

```bash
# Enrich single lead
python crm_enrichment.py --lead-id 12345

# Batch enrich all new leads
python crm_enrichment.py --status "new" --batch

# Refresh stale data (>30 days old)
python crm_enrichment.py --refresh-stale

# Find missing emails
python crm_enrichment.py --find-emails --status "needs-contact"
```

## Example Enrichment

```
Before:
- Company: JetLux
- Contact: Michael T.
- Email: (missing)

After:
- Company: JetLux Private Aviation
- Industry: Luxury Travel & Transportation
- Employee Count: 45
- Revenue: $5M - $10M (estimated)
- Funding: $2.5M Series A (Nov 2025)
- Website: jetlux.com
- LinkedIn: /company/jetlux-aviation
- Tech Stack: Salesforce, AWS, Stripe
- Contact: Michael Thompson, CEO
- Email: mthompson@jetlux.com
- LinkedIn: /in/michael-thompson-ceo
- Phone: +1 (555) 123-4567
- Decision Maker: ✅ Yes (CEO)
```

## Files

- `crm_enrichment.py` - Main enrichment script
- `data_sources/` - Integrations (Clearbit, Apollo, etc.)
- `email_finder.py` - Email discovery and verification
- `change_detector.py` - Monitors company changes
