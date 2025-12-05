"""
Attention Economy Design (AED) Framework

Focuses on patterns that extract and monetize user attention through
engagement maximization, distraction injection, time obfuscation,
and competitive gamification.

Based on "Time Well Spent" principles and attention ethics research.
"""

from src.frameworks.base import (
    Citation,
    DarkPatternFramework,
    DetectionRules,
    EvidenceType,
    PatternDefinition,
    Severity,
)


def create_attention_economy_framework() -> DarkPatternFramework:
    """Create Attention Economy Design framework for attention extraction detection."""

    patterns = [
        # Engagement Maximization
        PatternDefinition(
            id="aed_engagement_endless_feed",
            name="Endless Content Feed",
            description="Algorithmically-generated infinite content designed to maximize time on platform",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "infinite scroll implementation",
                    "algorithmic feed label",
                    "'for you' personalized feed",
                    "recommended content section",
                ],
                textual_patterns=[
                    "for you",
                    "recommended",
                    "you might like",
                    "based on your activity",
                    "keep watching",
                ],
                structural_markers=[
                    "infinite scroll container",
                    "recommendation algorithm indicators",
                    "personalized feed endpoints",
                ],
                behavioral_signals=[
                    "continuous content loading",
                    "no natural stopping point",
                    "algorithmic content ordering",
                ],
            ),
            severity=Severity.SEVERE,
            confidence_threshold=0.75,
            legal_citations=[
                Citation(
                    source="Time Well Spent Design Principles",
                    text="Platforms should provide natural stopping points and respect user time intentions",
                )
            ],
            examples=["TikTok For You page", "Instagram Explore", "YouTube recommendations"],
        ),
        PatternDefinition(
            id="aed_engagement_autoplay_video",
            name="Automatic Video Playback",
            description="Auto-playing video content to capture attention without explicit user request",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "video playing without user interaction",
                    "muted auto-play with unmute prompt",
                    "video player with auto-advance",
                ],
                textual_patterns=[
                    "auto-play",
                    "tap to unmute",
                    "playing next",
                    "up next",
                ],
                behavioral_signals=[
                    "video starts on page load",
                    "video starts on scroll into view",
                    "next video auto-plays",
                ],
            ),
            severity=Severity.MODERATE,
            confidence_threshold=0.85,
            legal_citations=[
                Citation(
                    source="Attention Economy Ethics",
                    text="Content should only play with explicit user consent",
                )
            ],
        ),
        PatternDefinition(
            id="aed_engagement_pull_to_refresh",
            name="Pull-to-Refresh Slot Machine",
            description="Variable reward mechanism disguised as content refresh",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "pull-to-refresh indicator",
                    "loading animation on pull",
                    "refresh reveals new content",
                ],
                structural_markers=[
                    "pull-to-refresh implementation",
                    "swipe-down refresh handler",
                ],
                behavioral_signals=[
                    "pull gesture triggers refresh",
                    "unpredictable new content on refresh",
                ],
            ),
            severity=Severity.MODERATE,
            confidence_threshold=0.7,
            legal_citations=[
                Citation(
                    source="Behavioral Design Ethics",
                    text="Refresh mechanisms should not exploit variable reward psychology",
                )
            ],
        ),
        # Distraction Injection
        PatternDefinition(
            id="aed_distraction_interruptions",
            name="Interruptive Elements",
            description="Injecting distracting content to prevent user from completing intended task",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "popup overlays during reading",
                    "interstitial ads",
                    "notification banners while using app",
                    "suggested content interrupting flow",
                ],
                textual_patterns=[
                    "before you go",
                    "wait",
                    "you might also like",
                    "recommended for you",
                ],
                behavioral_signals=[
                    "modal appears during content consumption",
                    "interruption before task completion",
                ],
            ),
            severity=Severity.MODERATE,
            confidence_threshold=0.75,
            legal_citations=[
                Citation(
                    source="Humane Technology Principles",
                    text="Interfaces should support user goals, not interrupt them",
                )
            ],
        ),
        PatternDefinition(
            id="aed_distraction_notification_bait",
            name="Notification Bait",
            description="Vague notifications designed to make users open app",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "notification badges",
                    "red dot indicators",
                    "unread count bubbles",
                ],
                textual_patterns=[
                    "someone mentioned you",
                    "you have new activity",
                    "see what's happening",
                    "trending now",
                    "X people viewed your profile",
                ],
                structural_markers=[
                    "notification permission prompt",
                    "badge count displays",
                ],
            ),
            severity=Severity.MODERATE,
            confidence_threshold=0.7,
            legal_citations=[
                Citation(
                    source="Attention Economy Ethics",
                    text="Notifications should be specific and meaningful, not vague engagement bait",
                )
            ],
            examples=[
                "LinkedIn 'people viewed your profile'",
                "Facebook 'you have memories to look back on'",
                "Instagram 'see what X is up to'",
            ],
        ),
        PatternDefinition(
            id="aed_distraction_bottomless_comments",
            name="Bottomless Comments/Replies",
            description="Infinite comment threads that extend engagement beyond primary content",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "show more comments button",
                    "load more replies",
                    "nested comment threads",
                ],
                textual_patterns=[
                    "view more comments",
                    "show more replies",
                    "load previous comments",
                ],
                behavioral_signals=[
                    "comments extend indefinitely",
                    "nested replies multiple levels deep",
                ],
            ),
            severity=Severity.MINOR,
            confidence_threshold=0.65,
            legal_citations=[
                Citation(
                    source="Time Well Spent Principles",
                    text="Comment sections should have natural boundaries",
                )
            ],
        ),
        # Time Obfuscation
        PatternDefinition(
            id="aed_time_no_usage_data",
            name="No Usage Transparency",
            description="Hiding time spent and usage patterns from users",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "no time spent indicator",
                    "no session duration display",
                    "usage stats hidden or absent",
                ],
                structural_markers=[
                    "absence of screen time features",
                    "no usage dashboard",
                ],
                behavioral_signals=[
                    "no time tracking visible",
                    "no usage reminders",
                ],
            ),
            severity=Severity.MODERATE,
            confidence_threshold=0.6,
            legal_citations=[
                Citation(
                    source="Digital Well-being Standards",
                    text="Platforms should provide transparent usage data to users",
                )
            ],
        ),
        PatternDefinition(
            id="aed_time_deliberate_friction_removal",
            name="Deliberate Friction Removal",
            description="Removing natural friction points that allow reflection on usage",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "one-tap actions for everything",
                    "no confirmation dialogs",
                    "instant gratification design",
                ],
                textual_patterns=[
                    "instant",
                    "one tap",
                    "quick",
                ],
                behavioral_signals=[
                    "no pause before significant actions",
                    "immediate execution without confirmation",
                ],
            ),
            severity=Severity.MINOR,
            confidence_threshold=0.65,
            legal_citations=[
                Citation(
                    source="Reflective Design Principles",
                    text="Interfaces should include appropriate friction for meaningful actions",
                )
            ],
        ),
        # Competitive Gamification
        PatternDefinition(
            id="aed_gamification_leaderboards",
            name="Public Leaderboards/Rankings",
            description="Social comparison through competitive rankings to drive engagement",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "leaderboard display",
                    "ranking position indicator",
                    "competitive scoring",
                    "top user showcases",
                ],
                textual_patterns=[
                    "leaderboard",
                    "top",
                    "ranked",
                    "you're #",
                    "climb the ranks",
                ],
                structural_markers=[
                    "ranking table",
                    "competitive score display",
                ],
            ),
            severity=Severity.MODERATE,
            confidence_threshold=0.8,
            legal_citations=[
                Citation(
                    source="Ethical Gamification Principles",
                    text="Gamification should enhance intrinsic motivation, not exploit competition",
                )
            ],
        ),
        PatternDefinition(
            id="aed_gamification_public_metrics",
            name="Public Engagement Metrics",
            description="Prominently displaying likes, followers, views to encourage metric-chasing",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "large follower counts",
                    "prominent like counters",
                    "view count displays",
                    "engagement metrics highlighted",
                ],
                textual_patterns=[
                    "followers",
                    "likes",
                    "views",
                    "shares",
                ],
                structural_markers=[
                    "engagement metric displays",
                    "social proof counters",
                ],
            ),
            severity=Severity.MODERATE,
            confidence_threshold=0.75,
            legal_citations=[
                Citation(
                    source="Humane Social Media Design",
                    text="Public metrics should be optional and de-emphasized to reduce addictive metric-chasing",
                )
            ],
            examples=[
                "Instagram like counts",
                "Twitter follower displays",
                "YouTube view counters",
            ],
        ),
        PatternDefinition(
            id="aed_gamification_achievement_hunting",
            name="Achievement/Badge Systems",
            description="Arbitrary achievements that extend engagement beyond user goals",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "achievement unlocked notifications",
                    "badge collections",
                    "progress bars for achievements",
                    "trophy/medal icons",
                ],
                textual_patterns=[
                    "achievement unlocked",
                    "badge earned",
                    "collect all",
                    "complete your collection",
                ],
                structural_markers=[
                    "achievement tracking system",
                    "badge display",
                ],
            ),
            severity=Severity.MINOR,
            confidence_threshold=0.7,
            legal_citations=[
                Citation(
                    source="Goal-Supportive Design",
                    text="Achievement systems should align with user goals, not platform goals",
                )
            ],
        ),
        # Algorithmic Manipulation
        PatternDefinition(
            id="aed_algorithm_outrage_amplification",
            name="Engagement-Optimized Algorithms",
            description="Algorithms that prioritize controversial/emotional content for engagement",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "trending/viral content highlighted",
                    "controversial topics promoted",
                    "emotionally charged content prioritized",
                ],
                textual_patterns=[
                    "trending",
                    "viral",
                    "everyone's talking about",
                    "heated discussion",
                ],
                behavioral_signals=[
                    "feed shows mostly controversial content",
                    "rage-bait prioritization",
                ],
            ),
            severity=Severity.SEVERE,
            confidence_threshold=0.65,
            legal_citations=[
                Citation(
                    source="Ethical Algorithm Design",
                    text="Recommendation algorithms should prioritize user well-being over engagement metrics",
                )
            ],
        ),
        PatternDefinition(
            id="aed_algorithm_no_chronological",
            name="No Chronological Feed Option",
            description="Forcing algorithmic feed without option for chronological viewing",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "no chronological sort option",
                    "algorithmic feed only",
                    "feed settings without time-based option",
                ],
                structural_markers=[
                    "absence of chronological feed toggle",
                    "algorithmic ordering enforced",
                ],
            ),
            severity=Severity.MODERATE,
            confidence_threshold=0.8,
            legal_citations=[
                Citation(
                    source="User Control Principles",
                    text="Users should have control over content ordering and algorithmic curation",
                )
            ],
        ),
    ]

    return DarkPatternFramework(
        name="Attention Economy Design (AED)",
        version="1.0",
        description="Framework for detecting attention extraction and time well-spent violations",
        patterns=patterns,
    )


# Singleton instance
AttentionEconomyFramework = create_attention_economy_framework()
