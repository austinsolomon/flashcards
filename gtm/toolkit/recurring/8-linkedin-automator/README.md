# LinkedIn Connection Automator

**Tier**: 1 (Simple Automation)
**Category**: Recurring Development

## Purpose

Automates LinkedIn connection requests and follow-ups while staying within platform limits. Builds network systematically.

## What It Does

- Sends personalized connection requests
- Follows up with non-responders
- Thanks new connections
- Schedules discovery call invites
- Tracks engagement rates
- Respects LinkedIn rate limits (100/week)

## Usage

```bash
# Send connection requests to qualified leads
python linkedin_automator.py --status "qualified" --max 20

# Follow up with accepted connections
python linkedin_automator.py --follow-up --days-since 3

# Thank new connections
python linkedin_automator.py --thank-new --template welcome
```

## Example Connection Request

```
Hi Michael,

Saw JetLux raised $2.5M - congrats! I work with private aviation companies
on mobile booking platforms. Would love to connect.

- [Your Name]
```

## Safety Features

- Respects LinkedIn limits (20/day connection requests)
- Randomized timing to appear human
- Personalization required (no generic templates)
- Tracks acceptance rates
- Auto-pause if acceptance rate <40%

## Files

- `linkedin_automator.py` - Main automation script
- `connection_templates.yaml` - Message templates
- `rate_limiter.py` - Enforces platform limits
- `engagement_tracker.py` - Monitors performance
