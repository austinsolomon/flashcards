"""
Digital Services Act (EU) 2022/2065 - Article 28
Protection against manipulation and deceptive practices

This framework focuses on detecting manipulative design patterns
prohibited under EU law, including coercive patterns, deceptive practices,
asymmetric difficulty, and exploitative design.
"""

from src.frameworks.base import (
    Citation,
    DarkPatternFramework,
    DetectionRules,
    EvidenceType,
    PatternDefinition,
    Severity,
)


def create_dsa_article_28_framework() -> DarkPatternFramework:
    """Create DSA Article 28 framework for manipulative design detection."""

    patterns = [
        # Article 28(1)(a) - Materially distorting behavior
        PatternDefinition(
            id="dsa_28_1a_confirmshaming",
            name="Confirmshaming",
            description="Using guilt or shame to manipulate user decisions",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "emotional manipulation in decline option",
                    "negative framing of opt-out",
                ],
                textual_patterns=[
                    "no, i don't want",
                    "no, i hate",
                    "no thanks, i prefer",
                    "i don't want to save",
                    "no, i'll pay full price",
                    "skip this offer (and miss out)",
                ],
                structural_markers=[
                    "asymmetric button styling (accept prominent, decline shameful)",
                ],
            ),
            severity=Severity.SEVERE,
            confidence_threshold=0.85,
            legal_citations=[
                Citation(
                    source="Digital Services Act (EU) 2022/2065",
                    article="Article 28",
                    paragraph="1(a)",
                    text="materially distort or impair, either on purpose or in effect, the ability of recipients of their service to make autonomous and informed decisions",
                    url="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2065",
                )
            ],
            examples=[
                "'No thanks, I don't want to save money'",
                "'No, I hate discounts'",
                "'Skip this deal and pay more'",
            ],
        ),
        PatternDefinition(
            id="dsa_28_1a_forced_action",
            name="Forced Action",
            description="Requiring unnecessary actions to access basic functionality",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "mandatory account creation for basic viewing",
                    "forced social media connection",
                    "required app download for web-accessible content",
                ],
                textual_patterns=[
                    "you must sign up",
                    "login required",
                    "create account to view",
                    "download app to continue",
                ],
                structural_markers=[
                    "content blocked behind login wall",
                    "no guest/anonymous access option",
                ],
                behavioral_signals=[
                    "basic content requires account",
                    "forced registration before browsing",
                ],
            ),
            severity=Severity.SEVERE,
            confidence_threshold=0.8,
            legal_citations=[
                Citation(
                    source="Digital Services Act (EU) 2022/2065",
                    article="Article 28",
                    paragraph="1(a)",
                    text="nudge recipients towards taking actions they would not have otherwise taken",
                )
            ],
        ),
        PatternDefinition(
            id="dsa_28_1a_nagging",
            name="Nagging/Persistence",
            description="Repeatedly prompting user to take action they've declined",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "repeated modal dialogs",
                    "persistent popup after dismissal",
                    "notification permission re-prompt",
                ],
                textual_patterns=[
                    "are you sure",
                    "last chance",
                    "one more time",
                    "before you go",
                ],
                behavioral_signals=[
                    "same prompt appears multiple times per session",
                    "dismissed dialog reappears on same page",
                    "exit intent popup",
                ],
            ),
            severity=Severity.MODERATE,
            confidence_threshold=0.75,
            legal_citations=[
                Citation(
                    source="Digital Services Act (EU) 2022/2065",
                    article="Article 28",
                    paragraph="1(a)",
                    text="employ nagging techniques to influence user behavior",
                )
            ],
        ),
        # Article 28(1)(b) - Deceptive design
        PatternDefinition(
            id="dsa_28_1b_hidden_costs",
            name="Hidden Costs",
            description="Revealing additional costs late in the purchase process",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "price increases at checkout",
                    "fees appear in final step",
                    "total price different from advertised",
                ],
                textual_patterns=[
                    "additional fees",
                    "service charge",
                    "processing fee",
                    "convenience fee",
                    "final total",
                ],
                structural_markers=[
                    "price breakdown only shown at final step",
                    "mandatory fees not in initial price",
                ],
                behavioral_signals=[
                    "checkout price > cart price",
                    "fees disclosed only at payment",
                ],
            ),
            severity=Severity.CRITICAL,
            confidence_threshold=0.9,
            legal_citations=[
                Citation(
                    source="Digital Services Act (EU) 2022/2065",
                    article="Article 28",
                    paragraph="1(b)",
                    text="deceive or mislead recipients, including by presenting inaccurate or unclear information",
                )
            ],
            examples=["Ticketmaster hidden fees", "Hotel booking resort fees", "Food delivery fees"],
        ),
        PatternDefinition(
            id="dsa_28_1b_bait_and_switch",
            name="Bait and Switch",
            description="Advertising one thing but delivering another after commitment",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "prominent feature advertised, not actually available",
                    "different product/service after purchase",
                ],
                textual_patterns=[
                    "not available in your area",
                    "this item is out of stock",
                    "upgrade required for advertised feature",
                ],
                structural_markers=[
                    "advertised feature gated behind paywall",
                    "promoted item unavailable after click",
                ],
            ),
            severity=Severity.CRITICAL,
            confidence_threshold=0.85,
            legal_citations=[
                Citation(
                    source="Digital Services Act (EU) 2022/2065",
                    article="Article 28",
                    paragraph="1(b)",
                    text="deceive or mislead recipients through bait and switch tactics",
                )
            ],
        ),
        PatternDefinition(
            id="dsa_28_1b_disguised_ads",
            name="Disguised Advertising",
            description="Ads that look like content, search results, or independent reviews",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "sponsored content styled like editorial",
                    "ads resembling search results",
                    "paid reviews without clear disclosure",
                ],
                textual_patterns=[
                    "sponsored",
                    "ad",
                    "promoted",
                    "partner content",
                ],
                structural_markers=[
                    "ad disclosure in tiny text",
                    "sponsored content without clear boundary",
                ],
                behavioral_signals=[
                    "ads indistinguishable from content",
                    "disclosure requires hover/tap",
                ],
            ),
            severity=Severity.SEVERE,
            confidence_threshold=0.75,
            legal_citations=[
                Citation(
                    source="Digital Services Act (EU) 2022/2065",
                    article="Article 28",
                    paragraph="1(b)",
                    text="ensure clear distinction between advertising and editorial content",
                )
            ],
        ),
        PatternDefinition(
            id="dsa_28_1b_fake_urgency",
            name="Fake Urgency",
            description="Creating false scarcity or time pressure to force quick decisions",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "countdown timer",
                    "low stock warning",
                    "limited time offer badge",
                    "other users viewing indicator",
                ],
                textual_patterns=[
                    "only X left",
                    "expires in",
                    "limited time",
                    "sale ends soon",
                    "others are viewing",
                    "high demand",
                ],
                behavioral_signals=[
                    "timer resets on page refresh",
                    "stock count never changes",
                    "perpetual 'limited time' offer",
                ],
            ),
            severity=Severity.SEVERE,
            confidence_threshold=0.7,
            legal_citations=[
                Citation(
                    source="Digital Services Act (EU) 2022/2065",
                    article="Article 28",
                    paragraph="1(b)",
                    text="avoid creating false urgency or scarcity to pressure decisions",
                )
            ],
            examples=[
                "Booking.com 'only 1 room left'",
                "E-commerce countdown timers",
                "Flash sale notifications",
            ],
        ),
        # Asymmetric Difficulty
        PatternDefinition(
            id="dsa_28_asymmetric_signup_cancel",
            name="Asymmetric Signup vs Cancellation",
            description="Making signup easy but cancellation difficult",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "one-click signup, multi-step cancellation",
                    "cancellation requires phone call/email",
                ],
                structural_markers=[
                    "cancel button buried in settings",
                    "no online cancellation option",
                ],
                behavioral_signals=[
                    "signup: < 3 steps, cancellation: > 5 steps",
                    "cancellation requires contacting support",
                ],
            ),
            severity=Severity.CRITICAL,
            confidence_threshold=0.85,
            evidence_requirements=[
                EvidenceType.SCREENSHOT,
                EvidenceType.USER_FLOW,
                EvidenceType.COMPARISON,
            ],
            legal_citations=[
                Citation(
                    source="Digital Services Act (EU) 2022/2065",
                    article="Article 28",
                    paragraph="1(c)",
                    text="make cancellation of service as easy as subscription",
                )
            ],
            examples=[
                "Gym memberships requiring in-person cancellation",
                "Amazon Prime cancellation flow",
                "News subscriptions",
            ],
        ),
        PatternDefinition(
            id="dsa_28_asymmetric_privacy",
            name="Asymmetric Privacy Controls",
            description="Easy to share data, difficult to revoke permissions",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "one-click data sharing",
                    "privacy controls deeply nested",
                ],
                textual_patterns=[
                    "share with one click",
                    "easy sharing",
                ],
                structural_markers=[
                    "permissions granted in one step",
                    "revoking requires multiple screens",
                ],
            ),
            severity=Severity.SEVERE,
            confidence_threshold=0.8,
            legal_citations=[
                Citation(
                    source="Digital Services Act (EU) 2022/2065",
                    article="Article 28",
                    paragraph="1(c)",
                    text="withdrawing consent should be as easy as giving it",
                )
            ],
        ),
        # Exploitative Design
        PatternDefinition(
            id="dsa_28_exploit_children",
            name="Child Exploitation Patterns",
            description="Patterns that exploit children's cognitive vulnerabilities",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "in-app purchases in kids' apps",
                    "aggressive marketing to children",
                    "child-targeted addictive mechanics",
                ],
                textual_patterns=[
                    "ask your parents",
                    "buy now",
                    "collect them all",
                ],
                behavioral_signals=[
                    "easy in-app purchases without parental controls",
                    "reward systems targeting children",
                ],
            ),
            severity=Severity.CRITICAL,
            confidence_threshold=0.9,
            legal_citations=[
                Citation(
                    source="Digital Services Act (EU) 2022/2065",
                    article="Article 28",
                    paragraph="2",
                    text="providers shall not present their interface in a way that manipulates or otherwise materially distorts the ability of children to make free and informed decisions",
                )
            ],
        ),
        PatternDefinition(
            id="dsa_28_preselected_options",
            name="Preselected Options",
            description="Automatically selecting options that benefit the provider",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "checkboxes pre-checked",
                    "opt-out of privacy protection pre-selected",
                    "additional purchases pre-selected",
                ],
                textual_patterns=[
                    "add insurance",
                    "include warranty",
                    "subscribe to newsletter",
                ],
                structural_markers=[
                    "checked checkboxes on load",
                    "opted-in by default",
                ],
            ),
            severity=Severity.SEVERE,
            confidence_threshold=0.9,
            legal_citations=[
                Citation(
                    source="Digital Services Act (EU) 2022/2065",
                    article="Article 28",
                    paragraph="1(a)",
                    text="default settings should respect user interests, not provider interests",
                )
            ],
            examples=[
                "Newsletter subscriptions pre-checked",
                "Insurance added to cart by default",
                "Marketing consent pre-selected",
            ],
        ),
    ]

    return DarkPatternFramework(
        name="DSA Article 28",
        version="2022/2065",
        description="EU Digital Services Act prohibitions on manipulative design",
        patterns=patterns,
    )


# Singleton instance
DSAArticle28Framework = create_dsa_article_28_framework()
