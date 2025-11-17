#!/usr/bin/env python3
"""
GTM - Tier 6 - Autonomous Lead Scoring & Optimization

TIER 6 CHARACTERISTICS:
- Fully autonomous operation (no human in loop)
- Continuous learning from outcomes
- Self-optimization based on performance data
- Adapts strategy based on what works
- Feedback loop improves over time

What It Does:
Autonomously scores leads, learns from conversion data, and continuously
improves its scoring model without human intervention.

Tier Contrast:
- Tier 5: Human approval required, fixed logic
- Tier 6: Fully autonomous with continuous learning
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class AutonomousLeadScorer:
    """
    TIER 6: Autonomous lead scoring system with continuous learning

    Key characteristics:
    - Learns from conversion outcomes
    - Adjusts scoring weights automatically
    - No human intervention required
    - Improves performance over time
    """

    def __init__(self):
        # Initial scoring weights (will be learned)
        self.weights = {
            "company_size": 0.25,
            "funding_stage": 0.20,
            "tech_stack_match": 0.20,
            "industry_fit": 0.15,
            "buying_signals": 0.20
        }

        self.performance_history = []
        self.learning_rate = 0.1

    def score_lead(self, lead_data: Dict) -> Tuple[int, Dict]:
        """
        Score a lead using current model weights

        Returns: (score, factors)
        """
        factors = {
            "company_size": self._score_company_size(lead_data.get("employees", 0)),
            "funding_stage": self._score_funding(lead_data.get("funding", "Unknown")),
            "tech_stack_match": self._score_tech_stack(lead_data.get("tech_stack", [])),
            "industry_fit": self._score_industry(lead_data.get("industry", "")),
            "buying_signals": self._score_signals(lead_data.get("signals", []))
        }

        # Calculate weighted score
        total_score = sum(
            factors[key] * self.weights[key]
            for key in self.weights.keys()
        )

        final_score = int(total_score)

        return final_score, factors

    def record_outcome(self, lead_id: str, score: int, converted: bool, days_to_convert: int = None):
        """
        TIER 6 KEY: Record outcome and learn from it

        Autonomous learning loop:
        1. Record what happened
        2. Analyze performance
        3. Adjust weights automatically
        4. Improve future scoring
        """
        self.performance_history.append({
            "lead_id": lead_id,
            "score": score,
            "converted": converted,
            "days_to_convert": days_to_convert,
            "timestamp": datetime.now().isoformat()
        })

        # Trigger learning every 10 outcomes
        if len(self.performance_history) % 10 == 0:
            self._autonomous_learning()

    def _autonomous_learning(self):
        """
        TIER 6: Autonomous learning from outcomes

        Analyzes recent performance and adjusts weights WITHOUT human intervention
        """
        print(f"\n🧠 [AUTONOMOUS LEARNING] Analyzing {len(self.performance_history)} outcomes")

        if len(self.performance_history) < 10:
            return

        recent = self.performance_history[-50:]  # Analyze last 50

        # Calculate conversion rate by score band
        high_score_conversions = [o for o in recent if o["score"] >= 80 and o["converted"]]
        mid_score_conversions = [o for o in recent if 50 <= o["score"] < 80 and o["converted"]]
        low_score_conversions = [o for o in recent if o["score"] < 50 and o["converted"]]

        high_conversion_rate = len(high_score_conversions) / max(len([o for o in recent if o["score"] >= 80]), 1)
        mid_conversion_rate = len(mid_score_conversions) / max(len([o for o in recent if 50 <= o["score"] < 80]), 1)

        print(f"   High score (80+) conversion rate: {high_conversion_rate:.2%}")
        print(f"   Mid score (50-79) conversion rate: {mid_conversion_rate:.2%}")

        # AUTONOMOUS OPTIMIZATION: Adjust weights based on what's working
        if high_conversion_rate < 0.3:  # Model is not predictive enough
            # Increase emphasis on signals that correlate with conversions
            print("   🔄 Model underperforming - adjusting weights")
            self.weights["buying_signals"] = min(0.35, self.weights["buying_signals"] + 0.05)
            self.weights["tech_stack_match"] = min(0.30, self.weights["tech_stack_match"] + 0.05)

            # Normalize weights to sum to 1.0
            total = sum(self.weights.values())
            self.weights = {k: v/total for k, v in self.weights.items()}

            print(f"   ✅ New weights: {json.dumps({k: round(v, 2) for k, v in self.weights.items()})}")
        else:
            print("   ✅ Model performing well - maintaining current weights")

    def _score_company_size(self, employees: int) -> float:
        """Score based on company size (0-100)"""
        if 100 <= employees <= 500:
            return 100
        elif 50 <= employees < 100 or 500 < employees <= 1000:
            return 75
        elif employees > 1000:
            return 50
        return 25

    def _score_funding(self, stage: str) -> float:
        """Score based on funding stage"""
        scores = {
            "Series B": 100,
            "Series A": 80,
            "Seed": 60,
            "Bootstrap": 40,
            "Unknown": 20
        }
        return scores.get(stage, 20)

    def _score_tech_stack(self, stack: List[str]) -> float:
        """Score based on tech stack compatibility"""
        desired_tech = {"salesforce", "hubspot", "slack", "jira", "aws", "stripe"}
        matches = len(set([t.lower() for t in stack]) & desired_tech)
        return (matches / len(desired_tech)) * 100

    def _score_industry(self, industry: str) -> float:
        """Score based on industry fit"""
        scores = {
            "SaaS": 100,
            "Enterprise Software": 90,
            "FinTech": 80,
            "E-commerce": 70,
            "Other": 40
        }
        return scores.get(industry, 40)

    def _score_signals(self, signals: List[str]) -> float:
        """Score based on buying signals"""
        return min(100, len(signals) * 25)


def simulate_autonomous_operation():
    """
    TIER 6: Simulate autonomous operation with learning

    Demonstrates:
    - Continuous operation without human intervention
    - Learning from outcomes
    - Self-optimization
    - Performance improvement over time
    """
    print(f"\n{'='*60}")
    print(f"🤖 TIER 6: Autonomous Lead Scoring System")
    print(f"{'='*60}\n")

    scorer = AutonomousLeadScorer()

    # Simulate 50 leads being scored and outcomes recorded
    print("🔄 Simulating autonomous operation with 50 leads...\n")

    sample_leads = [
        {
            "id": f"LEAD-{i:03d}",
            "company": f"Company {i}",
            "employees": random.choice([50, 150, 300, 600, 1200]),
            "funding": random.choice(["Seed", "Series A", "Series B", "Bootstrap"]),
            "industry": random.choice(["SaaS", "FinTech", "E-commerce", "Other"]),
            "tech_stack": random.sample(["Salesforce", "HubSpot", "Slack", "Jira", "AWS", "Stripe"], k=random.randint(2, 5)),
            "signals": random.sample(["Recent funding", "Job postings", "Tech mentions", "Conference attendance"], k=random.randint(0, 3))
        }
        for i in range(1, 51)
    ]

    for lead in sample_leads:
        # Score the lead
        score, factors = scorer.score_lead(lead)

        # Simulate conversion outcome (higher scores more likely to convert)
        conversion_probability = score / 150  # 100 score = 67% conversion chance
        converted = random.random() < conversion_probability
        days_to_convert = random.randint(7, 30) if converted else None

        # TIER 6: System autonomously records and learns from outcome
        scorer.record_outcome(lead["id"], score, converted, days_to_convert)

        if lead == sample_leads[0] or lead == sample_leads[25] or lead == sample_leads[-1]:
            print(f"Lead {lead['id']}: Score {score}/100 → {'✅ Converted' if converted else '❌ No conversion'}")

    print(f"\n{'='*60}")
    print(f"📊 AUTONOMOUS SYSTEM SUMMARY")
    print(f"{'='*60}\n")

    total_leads = len(sample_leads)
    conversions = sum(1 for o in scorer.performance_history if o["converted"])
    conversion_rate = conversions / total_leads

    print(f"Total Leads Scored: {total_leads}")
    print(f"Conversions: {conversions}")
    print(f"Conversion Rate: {conversion_rate:.1%}")
    print(f"\nFinal Model Weights (after autonomous learning):")
    print(json.dumps({k: round(v, 3) for k, v in scorer.weights.items()}, indent=2))

    print(f"\n✅ System has autonomously learned and optimized")
    print(f"   No human intervention required")
    print(f"   Continuous improvement from feedback loop\n")


def main():
    """Demonstrate Tier 6 autonomous operation"""

    simulate_autonomous_operation()

    print("="*60)
    print("🎓 WHY THIS IS TIER 6:")
    print("="*60)
    print("""
    1. FULLY AUTONOMOUS:
       - No human approval required
       - Operates continuously without intervention
       - Makes decisions independently

    2. CONTINUOUS LEARNING:
       - Records all outcomes
       - Analyzes performance automatically
       - Learns what factors predict conversions

    3. SELF-OPTIMIZATION:
       - Adjusts scoring weights based on data
       - Improves accuracy over time
       - Adapts to changing patterns

    4. FEEDBACK LOOP:
       - Score lead → Track outcome → Learn → Improve scoring
       - Gets better with every interaction
       - Never stops learning

    Contrast with other tiers:
    - Tier 5: Orchestrates AI + human + systems (human in loop)
    - Tier 6: Fully autonomous with continuous learning (no human needed)

    Future enhancements:
    - A/B test different scoring strategies
    - Predict optimal contact timing
    - Automatically adjust outreach messaging
    - Identify new buying signal patterns
    """)


if __name__ == "__main__":
    main()
