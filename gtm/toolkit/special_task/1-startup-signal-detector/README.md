# Social Media Startup Signal Detector

**Tier**: 3 (Autonomous Agent)
**Category**: Special Task - iPhone App Lead Generation

## Purpose

Monitors social media platforms for startup signals indicating iPhone app development opportunities. Detects funding announcements, team expansion, digital transformation initiatives, and mobile-first business models.

## What It Does

- Monitors Twitter/X, LinkedIn, Instagram for startup activity
- Detects funding announcements, hiring posts, product launches
- Identifies mobile-first business models
- Tracks influencer business ventures
- Analyzes follower growth and engagement patterns
- Generates qualified lead lists with context

## Target Signals

**Funding Signals**
- "We raised $X in seed/Series A funding"
- "Excited to announce our investment from..."
- "Closed our round with..."

**Hiring Signals**
- "Looking for mobile developers"
- "Building our tech team"
- "Hiring: iOS Engineer"

**Business Model Signals**
- "Launching our digital platform"
- "Taking our business online"
- "Building a community app"
- Subscription/membership models
- Direct-to-consumer brands

**Influencer Signals**
- Large follower count (100K+) with high engagement
- Multiple revenue streams mentioned
- Course/program launches
- Merchandise/product lines
- "Taking my brand to the next level"

## Implementation

```yaml
# automation.yaml
name: startup-signal-detector
tier: 3

sources:
  twitter:
    keywords:
      - "raised funding"
      - "seed round"
      - "Series A"
      - "mobile app"
      - "iOS development"
    accounts_to_monitor:
      - "@ycombinator"
      - "@TechCrunch"
      - Influencers with 100K+ followers

  linkedin:
    search_queries:
      - "We're hiring mobile developers"
      - "Announcing our funding round"
      - "Building a mobile-first platform"

  instagram:
    hashtags:
      - "#startup"
      - "#entrepreneur"
      - "#businessgrowth"
      - "#digitalproducts"

agent:
  model: claude-sonnet-4.5

  system_prompt: |
    You are an expert BDR at a mobile app development agency. Analyze
    social media posts to identify startups and influencers who likely
    need iPhone app development services. Focus on:
    - Funding events (now have budget)
    - Influencer monetization (need branded apps)
    - Luxury/niche businesses going digital
    - High-engagement communities without apps

capabilities:
  - analyze_post_context
  - extract_company_info
  - assess_app_need_likelihood
  - generate_lead_profile
  - prioritize_opportunities

qualification_criteria:
  min_follower_count: 50000
  engagement_rate_threshold: 0.02
  funding_range: "$100K - $5M"
  business_maturity: "early-stage to growth"
```

## Usage

```bash
# Monitor for 24 hours
python signal_detector.py --duration 24h

# Focus on specific vertical
python signal_detector.py --vertical "wellness" --vertical "luxury"

# Real-time monitoring with alerts
python signal_detector.py --watch --alert slack --webhook $WEBHOOK_URL

# Analyze past week for missed opportunities
python signal_detector.py --backfill 7d --output leads.json
```

## Example Output

```json
{
  "leads_found": 12,
  "scan_period": "2025-11-18 to 2025-11-19",
  "leads": [
    {
      "source": "twitter",
      "handle": "@VeganChefEmily",
      "name": "Emily Rodriguez",
      "followers": 850000,
      "engagement_rate": 0.045,
      "signal_type": "influencer_expansion",
      "trigger_post": "Excited to announce my meal prep subscription service launching next month! 🌱",
      "timestamp": "2025-11-18T14:23:00Z",
      "app_need_score": 0.92,
      "analysis": {
        "business_model": "Subscription meal plans for vegan audience",
        "app_opportunity": "Custom meal planning app with recipes, shopping lists, macro tracking",
        "budget_indicator": "Professional branding, video production suggests solid budget",
        "urgency": "High - launching next month",
        "similar_success": "Vegan influencer case study (1M followers)"
      },
      "contact_info": {
        "email": "emily@veganwithemily.com",
        "website": "veganwithemily.com",
        "instagram": "@veganchefemily",
        "linkedin": "emily-rodriguez-chef"
      },
      "recommended_action": "Immediate outreach with vegan influencer case study",
      "priority": "P1 - High Value"
    },
    {
      "source": "linkedin",
      "company": "JetLux Private Aviation",
      "industry": "Luxury Travel",
      "signal_type": "funding + hiring",
      "trigger_post": "JetLux raises $2.5M Series A to revolutionize private jet booking. Now hiring mobile developers!",
      "timestamp": "2025-11-18T09:15:00Z",
      "app_need_score": 0.88,
      "analysis": {
        "business_model": "On-demand private jet charter marketplace",
        "app_opportunity": "Uber-style booking app for private jets",
        "budget_indicator": "$2.5M funding, actively hiring mobile devs",
        "urgency": "High - hiring now means they need to build fast",
        "similar_success": "Private jet rental case study"
      },
      "contact_info": {
        "ceo": "Michael Thompson",
        "email": "mthompson@jetlux.com",
        "linkedin": "jetlux-aviation",
        "website": "jetlux.com"
      },
      "recommended_action": "Propose fractional CTO + dev team vs full-time hires",
      "priority": "P1 - High Value"
    },
    {
      "source": "instagram",
      "handle": "@FitMomClub",
      "name": "Sarah Martinez",
      "followers": 320000,
      "engagement_rate": 0.038,
      "signal_type": "community_monetization",
      "trigger_post": "Big announcement! FitMom Club membership is coming... exclusive workouts, meal plans, and accountability!",
      "timestamp": "2025-11-18T16:45:00Z",
      "app_need_score": 0.75,
      "analysis": {
        "business_model": "Paid fitness community for mothers",
        "app_opportunity": "Community app with workouts, tracking, social features",
        "budget_indicator": "Moderate - influencer monetization stage",
        "urgency": "Medium - planning phase",
        "competitors": "Similar to Sweat app but niche focused"
      },
      "contact_info": {
        "email": "sarah@fitmomclub.com",
        "website": "fitmomclub.com",
        "instagram": "@fitmomclub"
      },
      "recommended_action": "Warm outreach with fitness influencer examples",
      "priority": "P2 - Good Fit"
    }
  ],
  "statistics": {
    "total_posts_analyzed": 45678,
    "qualified_leads": 12,
    "by_vertical": {
      "wellness": 5,
      "luxury": 3,
      "education": 2,
      "ecommerce": 2
    },
    "by_signal_type": {
      "funding": 4,
      "influencer_expansion": 6,
      "hiring": 2
    }
  }
}
```

## Scoring Algorithm

```python
def calculate_app_need_score(lead):
    score = 0.0

    # Follower count (max 0.3)
    if lead.followers > 1000000:
        score += 0.3
    elif lead.followers > 500000:
        score += 0.25
    elif lead.followers > 100000:
        score += 0.2

    # Engagement rate (max 0.2)
    if lead.engagement_rate > 0.05:
        score += 0.2
    elif lead.engagement_rate > 0.03:
        score += 0.15

    # Business signals (max 0.3)
    if "funding" in lead.signals:
        score += 0.15
    if "subscription" in lead.business_model:
        score += 0.1
    if "launching" in lead.trigger_post:
        score += 0.05

    # Budget indicators (max 0.2)
    if lead.has_funding:
        score += 0.15
    if lead.professional_branding:
        score += 0.05

    return min(score, 1.0)
```

## Files

- `signal_detector.py` - Main detection agent
- `social_media_monitors/` - Platform-specific scrapers
- `qualification_rules.yaml` - Lead scoring criteria
- `vertical_patterns.yaml` - Industry-specific signal patterns
- `alert_templates/` - Slack/email notification templates
- `case_studies/` - Successful client examples for reference
