# Personalized Outreach Generator

**Tier**: 2 (Context-Aware AI)
**Category**: Recurring Development

## Purpose

Generates personalized email and LinkedIn outreach using Claude. Tailors messaging based on prospect vertical, signals, and case studies.

## What It Does

- Creates personalized cold emails
- Generates LinkedIn connection requests and messages
- Tailors messaging by vertical and prospect signals
- Incorporates relevant case studies
- A/B tests subject lines and opening hooks
- Maintains brand voice consistency

## Usage

```bash
# Generate email for prospect
python outreach_generator.py --lead "JetLux Aviation" --type email

# Generate LinkedIn sequence
python outreach_generator.py --lead "VeganChefEmily" --type linkedin --sequence

# Batch generate for pipeline
python outreach_generator.py --status "qualified" --batch --output drafts/
```

## Example Output

```markdown
TO: mthompson@jetlux.com
SUBJECT: JetLux + Mobile Booking (NetJets has one)

Hi Michael,

Congrats on the $2.5M Series A! Saw the announcement on LinkedIn yesterday.

Quick question: I noticed you're hiring mobile developers. Have you considered
a fractional development team vs full-time hires?

We helped a private aviation client build their booking app (think "Uber for
private jets") in 90 days vs 6+ months with in-house hiring.

Results:
- 35% higher booking conversion vs mobile web
- $1M incremental revenue (year 1)
- Apple Pay integration = impulse bookings

All your competitors (NetJets, Wheels Up, VistaJet) have native apps. We could
show you what they're doing right (and wrong) in a 15-min call.

[Calendar link]

Best,
[Name]

P.S. - Here's the private aviation case study: [link]
```

## Personalization Elements

- Recent news (funding, hiring, launches)
- Competitor references
- Vertical-specific pain points
- Relevant case studies
- ROI projections
- Social proof

## Files

- `outreach_generator.py` - Main generation script
- `templates/` - Base templates by vertical
- `case_study_matcher.py` - Finds relevant success stories
- `ab_test_tracker.py` - Tracks performance by variant
