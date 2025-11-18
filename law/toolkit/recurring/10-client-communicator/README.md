# Client Communication Automator

**Tier**: 2 (Context-Aware AI)
**Category**: Recurring Development

## Purpose

Automates routine client communications while maintaining personalization and professional quality. Uses Claude to draft updates, advisories, and responses.

## What It Does

- Generates case status updates
- Drafts client advisories on legal developments
- Creates engagement letters
- Responds to common client questions
- Translates "legalese" to plain language
- Schedules follow-up communications

## Communication Types

**Case Updates:**
- Weekly status reports
- Significant development notifications
- Settlement offer summaries
- Trial preparation updates

**Legal Advisories:**
- Regulatory changes affecting client
- New case law impacts
- Compliance reminders

**Administrative:**
- Engagement letters
- Retainer reminders
- Document request follow-ups

## Usage

```bash
# Generate weekly case update
python client_communicator.py --update --case "3:23-cv-00770" --client acme

# Draft advisory on new regulation
python client_communicator.py --advisory \
  --topic "EU AI Act compliance" \
  --clients tech-companies

# Translate legal document to plain language
python client_communicator.py --translate brief.pdf --plain-language

# Schedule recurring updates
python client_communicator.py --schedule weekly --case "3:23-cv-00770"
```

## Example Output

```markdown
TO: Jane Smith, CEO - Acme Corp
FROM: Legal Team
RE: Weekly Update - Mobley Litigation
DATE: November 18, 2025

Hi Jane,

Here's your weekly update on the Mobley case:

WHAT HAPPENED THIS WEEK
- We filed our response to Plaintiff's motion to dismiss on Nov 15
- The court scheduled oral arguments for Dec 10, 2025
- Discovery deadline was extended to Jan 15, 2026 (good news - gives us more time)

NEXT STEPS
- We're preparing for oral arguments
- Continue document review for discovery
- Schedule prep session with you for Dec 5

WHAT THIS MEANS FOR YOU
The extended discovery deadline is helpful - it gives us time to gather
stronger evidence without rushing. The oral arguments on Dec 10 will be
important, but we feel well-prepared.

UPCOMING DEADLINES
- Dec 5: Prep session with you (2 hours)
- Dec 10: Oral arguments
- Jan 15: Discovery responses due

ANY QUESTIONS?
Feel free to call or email anytime. Our next scheduled check-in is Nov 25.

Best regards,
Legal Team

---
Estimated attorney time this week: 8 hours
Total case spend to date: $45,000 (budget: $100,000)
```

## Plain Language Translation

**Legal Document:**
> "The Court hereby GRANTS Defendant's Motion for Summary Judgment
> pursuant to Fed. R. Civ. P. 56, finding no genuine dispute of material
> fact and that Defendant is entitled to judgment as a matter of law."

**Plain Language:**
> "The judge decided in our favor and dismissed the case. The judge found
> that the facts were clear and the law was on our side, so there's no
> need for a trial."

## Files

- `client_communicator.py` - Main communication engine
- `templates/` - Email and letter templates
- `plain_language.py` - Legalese translator
- `scheduler.py` - Recurring communication scheduling
- `personalization_engine.py` - Tailors messaging to client
