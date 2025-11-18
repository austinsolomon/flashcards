# Lead Scoring & Prioritization Engine

**Tier**: 3 (Autonomous Agent)
**Category**: Special Task - iPhone App Lead Generation

## Purpose

Scores and prioritizes leads based on budget indicators, urgency, fit, and likelihood to close. Ensures BDRs focus on highest-value opportunities first.

## What It Does

- Scores leads across multiple dimensions
- Prioritizes outreach queue
- Identifies "hot" leads requiring immediate action
- Estimates deal size and close probability
- Recommends optimal outreach strategy
- Tracks lead score changes over time

## Scoring Dimensions

**Budget Indicators (30 points)**
- Recent funding: +15
- Revenue signals: +10
- Premium branding: +5
- Hiring developers: +10

**Urgency (25 points)**
- "Launching soon": +15
- Hiring now: +10
- Competitor gap: +10
- Seasonal timing: +5

**Fit (25 points)**
- Perfect vertical match: +15
- Clear app use case: +10
- Mobile-first business: +10

**Engagement Potential (20 points)**
- Warm intro available: +10
- Active on social: +5
- Responded to outreach before: +10
- Attended webinar/event: +5

**Total: 100 points**

## Priority Tiers

- **P1 (80-100)**: Immediate outreach, executive involvement
- **P2 (60-79)**: Outreach within 48 hours
- **P3 (40-59)**: Standard nurture sequence
- **P4 (<40)**: Long-term nurture or disqualify

## Usage

```bash
# Score single lead
python lead_scoring.py --lead "JetLux Aviation"

# Batch score and prioritize
python lead_scoring.py --input leads.json --output scored_leads.json

# Generate daily priority list
python lead_scoring.py --today --notify slack

# Track score changes
python lead_scoring.py --track --alert-on-increase
```

## Example Output

```
Lead Scoring Report
Date: 2025-11-18

TOP PRIORITY LEADS (P1)

1. JetLux Private Aviation
   Score: 92/100 (P1 - Immediate Action)

   Budget Indicators: 30/30 ✅
   ├─ $2.5M Series A funding (yesterday) [+15]
   ├─ Hiring mobile developers [+10]
   └─ Premium branding [+5]

   Urgency: 25/25 ✅
   ├─ Hiring NOW for mobile team [+10]
   ├─ Launching "booking platform" Q1 2026 [+15]

   Fit: 23/25 ✅
   ├─ Perfect match: luxury + on-demand [+15]
   ├─ Clear native app need [+10]
   └─ Desktop website exists (needs mobile) [-2]

   Engagement: 14/20
   ├─ CEO active on LinkedIn [+5]
   ├─ No prior relationship [-6]
   └─ Engaged with competitor content [+5]

   Estimated Deal Size: $100K - $150K
   Close Probability: 75%
   Expected Value: $112K

   RECOMMENDED ACTION: Immediate personalized outreach
   ├─ Angle: "You're hiring mobile devs - have you considered outsourcing?"
   ├─ Mention: Private aviation case study
   ├─ Contact: CEO Michael Thompson (LinkedIn)
   └─ Timing: Today (funding announcement still fresh)

   Talking Points:
   - "Saw your Series A announcement - congratulations!"
   - "Building vs buying: fractional team vs full-time hires"
   - "We built a similar booking platform for [competitor]"
   - "90-day MVP vs 6-month hiring + build cycle"

2. VeganChefEmily
   Score: 88/100 (P1 - Immediate Action)

   Budget Indicators: 25/30
   ├─ Professional production quality [+5]
   ├─ 850K followers = strong monetization [+10]
   ├─ Launching paid subscription [+10]

   Urgency: 22/25
   ├─ Launching subscription "next month" [+15]
   ├─ Timing: Pre-launch is perfect [+7]

   Fit: 25/25 ✅
   ├─ Perfect: influencer monetization [+15]
   ├─ Subscription model = clear app fit [+10]

   Engagement: 16/20
   ├─ Warm intro available via mutual connection [+10]
   ├─ Engaged with our content on IG [+5]
   ├─ Responded to DM 6 months ago [+1]

   Estimated Deal Size: $80K - $120K
   Close Probability: 70%
   Expected Value: $84K

   RECOMMENDED ACTION: Warm intro via Sarah (mutual connection)
   ├─ Angle: "Your subscription launch needs a branded app"
   ├─ Mention: 1M vegan influencer case study
   ├─ Timing: This week (before launch commitment made)

---

MEDIUM PRIORITY LEADS (P2)

3. FitMomClub
   Score: 67/100 (P2 - Outreach within 48h)
   [Details...]

---

SCORE CHANGES (Past 24h)

📈 JetLux Aviation: 45 → 92 (+47)
   Trigger: Funding announcement + job posting

📈 VeganChefEmily: 78 → 88 (+10)
   Trigger: Subscription launch timing clarified

📉 FitnessGuru: 71 → 52 (-19)
   Trigger: Launched web platform (reduced urgency)

---

RECOMMENDED FOCUS TODAY

Immediate (P1): 2 leads
├─ JetLux Aviation (CEO outreach)
└─ VeganChefEmily (warm intro)

This Week (P2): 5 leads
Next Week (P3): 12 leads
Long-term nurture (P4): 23 leads
```

## Scoring Model

```python
class LeadScoringEngine:
    def score_lead(self, lead):
        budget_score = self.score_budget(lead)
        urgency_score = self.score_urgency(lead)
        fit_score = self.score_fit(lead)
        engagement_score = self.score_engagement(lead)

        total = budget_score + urgency_score + fit_score + engagement_score

        return {
            "total": total,
            "priority": self.get_priority(total),
            "budget": budget_score,
            "urgency": urgency_score,
            "fit": fit_score,
            "engagement": engagement_score,
            "deal_size": self.estimate_deal_size(lead),
            "close_probability": self.estimate_close_prob(total),
            "expected_value": self.calculate_ev(lead, total),
            "recommended_action": self.recommend_action(lead, total)
        }

    def score_budget(self, lead):
        score = 0
        if lead.recent_funding:
            score += 15
        if lead.revenue_indicators:
            score += 10
        if lead.hiring_developers:
            score += 10
        if lead.premium_branding:
            score += 5
        return min(score, 30)

    def get_priority(self, score):
        if score >= 80:
            return "P1"
        elif score >= 60:
            return "P2"
        elif score >= 40:
            return "P3"
        else:
            return "P4"
```

## Files

- `lead_scoring.py` - Main scoring engine
- `scoring_model.py` - Algorithm implementation
- `priority_queue.py` - Daily prioritization
- `tracking.py` - Score change monitoring
- `deal_size_estimator.py` - Revenue prediction
- `action_recommender.py` - Next best action suggestions
