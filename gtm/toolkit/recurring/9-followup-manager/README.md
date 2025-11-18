# Follow-up Sequence Manager

**Tier**: 2 (Context-Aware AI)
**Category**: Recurring Development

## Purpose

Manages multi-touch follow-up sequences with intelligent timing and messaging. Prevents leads from going cold.

## What It Does

- Tracks outreach attempts across channels
- Schedules follow-ups at optimal times
- Generates context-aware follow-up messages
- Escalates persistent non-responders
- Knows when to stop (avoid spam)
- A/B tests follow-up strategies

## Follow-up Cadence

```
Day 0: Initial outreach (email)
Day 3: Follow-up #1 (different angle)
Day 7: Follow-up #2 (LinkedIn)
Day 14: Follow-up #3 (value-add content)
Day 30: Final attempt (break-up email)
```

## Usage

```bash
# Check who needs follow-up today
python followup_manager.py --due-today

# Generate follow-up messages
python followup_manager.py --generate --lead "JetLux Aviation"

# Update sequence based on engagement
python followup_manager.py --adjust --opened --lead 12345
```

## Example Follow-up Sequence

```
Email 1 (Day 0): Initial pitch with case study

Email 2 (Day 3):
Subject: Quick follow-up: JetLux mobile app

Michael,

Following up on my email from Tuesday. I know you're busy with the Series A close.

One quick data point: Our private aviation client saw 35% higher conversion
with their app vs mobile web.

Worth a 15-min conversation?

[Calendar link]


Email 3 (Day 7): LinkedIn message
Michael - sent an email last week about mobile booking platforms for JetLux.
Happy to share what NetJets and Wheels Up are doing with their apps.


Email 4 (Day 14): Value-add
Subject: Private aviation app benchmarks (no pitch)

Michael,

Not sure if you saw my previous emails, but I put together a quick competitive
analysis of booking apps in private aviation. Thought it might be useful as
you build out your mobile strategy.

[Link to PDF]

No strings attached - happy to chat if helpful.


Email 5 (Day 30): Break-up email
Subject: Should I close your file?

Michael,

I've reached out a few times about mobile booking for JetLux. I'm guessing
it's not a priority right now, which is totally fine.

Should I close your file, or is this worth revisiting in Q2 2026?

Either way, best of luck with the Series A momentum!
```

## Smart Features

- Adjusts timing based on opens/clicks
- Pauses sequence if prospect engages elsewhere
- Escalates to sales manager after 3 attempts
- Auto-disqualifies chronic non-responders
- Learns from successful patterns

## Files

- `followup_manager.py` - Main sequence engine
- `sequences/` - Template sequences by stage
- `timing_optimizer.py` - Learns optimal send times
- `engagement_tracker.py` - Monitors interactions
