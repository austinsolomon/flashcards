# Deadline & Docket Tracker

**Tier**: 2 (Context-Aware AI)
**Category**: Recurring Development

## Purpose

Tracks court deadlines, filing dates, and docket entries. Prevents missed deadlines and monitors case developments automatically.

## What It Does

- Monitors PACER for docket updates
- Calculates deadlines from court orders
- Sends deadline reminders
- Tracks statute of limitations
- Monitors opposing counsel filings
- Generates calendar entries

## Usage

```bash
# Add case to tracking
python deadline_tracker.py --add-case "3:23-cv-00770" --court "N.D. Cal."

# Check upcoming deadlines
python deadline_tracker.py --upcoming --days 7

# Monitor docket for updates
python deadline_tracker.py --monitor --case "3:23-cv-00770" --alert email

# Calculate response deadline
python deadline_tracker.py --calculate --motion-served "2025-11-18" --court "N.D. Cal."
```

## Example Output

```
Deadline Report - Week of Nov 18, 2025

URGENT (Next 7 Days):
🔴 Nov 20 - Response to MTD due (Case 3:23-cv-00770)
🔴 Nov 22 - Discovery responses due (Case 4:24-cv-01234)

UPCOMING (7-14 Days):
⚠️  Nov 25 - Expert disclosure deadline (Case 5:24-cv-05678)
⚠️  Dec 1 - Summary judgment motion deadline (Case 3:23-cv-00770)

NEW DOCKET ENTRIES:
- Case 3:23-cv-00770: Opposition filed by Defendant (Nov 17)
- Case 4:24-cv-01234: Court order re: discovery dispute (Nov 16)

STATUTE OF LIMITATIONS ALERTS:
⚠️  Client Smith - Personal injury SOL expires in 45 days (Jan 2, 2026)
```

## Files

- `deadline_tracker.py` - Main tracking system
- `pacer_monitor.py` - PACER docket monitoring
- `deadline_calculator.py` - Court rule-based calculations
- `reminder_system.py` - Email/calendar alerts
