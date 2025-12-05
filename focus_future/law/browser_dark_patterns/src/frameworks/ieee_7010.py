"""
IEEE 7010-2020: Recommended Practice for Assessing the Impact of
Autonomous and Intelligent Systems on Human Well-being

This framework focuses on detecting patterns that negatively impact
user well-being through addiction mechanisms, time displacement,
social pressure, and autonomy violation.
"""

from src.frameworks.base import (
    Citation,
    DarkPatternFramework,
    DetectionRules,
    EvidenceType,
    PatternDefinition,
    Severity,
)


def create_ieee_7010_framework() -> DarkPatternFramework:
    """Create IEEE 7010-2020 framework with well-being impact patterns."""

    patterns = [
        # Addiction Mechanisms
        PatternDefinition(
            id="ieee_7010_addiction_infinite_scroll",
            name="Infinite Scroll",
            description="Continuously loading content without clear endpoint, exploiting human tendency to continue scrolling",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "continuously loading content indicator",
                    "no visible end of page",
                    "loading spinner appearing repeatedly",
                ],
                structural_markers=[
                    "infinite scroll implementation",
                    "lazy loading containers",
                    "pagination-less content feed",
                ],
                behavioral_signals=[
                    "auto-loads content on scroll",
                    "no pagination controls visible",
                    "content extends beyond 3 screen heights without break",
                ],
            ),
            severity=Severity.SEVERE,
            confidence_threshold=0.75,
            legal_citations=[
                Citation(
                    source="IEEE 7010-2020",
                    article="6.2.1",
                    text="Systems should support user autonomy and not exploit psychological vulnerabilities",
                    url="https://standards.ieee.org/standard/7010-2020.html",
                )
            ],
            examples=[
                "Social media feeds (Facebook, Instagram, TikTok)",
                "News aggregator sites",
                "Video platform recommendations",
            ],
        ),
        PatternDefinition(
            id="ieee_7010_addiction_variable_rewards",
            name="Variable Reward Mechanisms",
            description="Unpredictable rewards (likes, notifications) that create compulsive checking behavior",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "notification badges with counts",
                    "reward animations",
                    "achievement unlocked messages",
                    "surprise bonus indicators",
                ],
                textual_patterns=[
                    "you earned",
                    "new reward",
                    "achievement unlocked",
                    "surprise",
                    "bonus",
                ],
                behavioral_signals=[
                    "randomized reward delivery",
                    "notification-driven engagement",
                    "unpredictable positive feedback",
                ],
            ),
            severity=Severity.SEVERE,
            confidence_threshold=0.7,
            legal_citations=[
                Citation(
                    source="IEEE 7010-2020",
                    article="6.3.2",
                    text="Avoid design patterns that exploit reward-seeking behavior",
                )
            ],
        ),
        PatternDefinition(
            id="ieee_7010_addiction_streak_system",
            name="Streak/Commitment Systems",
            description="Loss aversion through streaks, daily login requirements, and progress loss threats",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "streak counter display",
                    "daily login indicator",
                    "progress bar showing consecutive days",
                    "flame/fire icons indicating streaks",
                ],
                textual_patterns=[
                    "day streak",
                    "don't break your streak",
                    "login daily",
                    "consecutive days",
                    "you'll lose your progress",
                ],
                structural_markers=[
                    "streak counter element",
                    "daily check-in button",
                    "progress loss warning",
                ],
            ),
            severity=Severity.MODERATE,
            confidence_threshold=0.8,
            legal_citations=[
                Citation(
                    source="IEEE 7010-2020",
                    article="6.2.3",
                    text="Systems should not create artificial dependencies that harm well-being",
                )
            ],
            examples=["Duolingo streaks", "Snapchat snap streaks", "Fitness app daily goals"],
        ),
        # Time Displacement
        PatternDefinition(
            id="ieee_7010_time_autoplay",
            name="Auto-play Next Content",
            description="Automatically playing next video/episode without user action, reducing intentional usage",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "countdown timer before next video",
                    "'playing next' indicator",
                    "auto-play toggle in settings",
                ],
                textual_patterns=[
                    "playing next in",
                    "up next",
                    "auto-play",
                    "next episode starts in",
                ],
                behavioral_signals=[
                    "content starts without user action",
                    "countdown to auto-play visible",
                    "requires action to prevent auto-play",
                ],
            ),
            severity=Severity.MODERATE,
            confidence_threshold=0.85,
            legal_citations=[
                Citation(
                    source="IEEE 7010-2020",
                    article="6.4.1",
                    text="Respect user time and enable intentional usage decisions",
                )
            ],
            examples=["YouTube auto-play", "Netflix episode auto-play", "TikTok continuous feed"],
        ),
        PatternDefinition(
            id="ieee_7010_time_obfuscation",
            name="Time Obfuscation",
            description="Hiding or obscuring time spent, preventing users from making informed usage decisions",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "no visible clock or time indicator",
                    "no session duration display",
                    "usage statistics hidden in deep settings",
                ],
                structural_markers=[
                    "absence of time tracking display",
                    "no usage dashboard",
                    "screen time features disabled by default",
                ],
                behavioral_signals=[
                    "no periodic time spent notifications",
                    "no usage reminders",
                    "time data not surfaced to user",
                ],
            ),
            severity=Severity.MODERATE,
            confidence_threshold=0.65,
            legal_citations=[
                Citation(
                    source="IEEE 7010-2020",
                    article="6.4.2",
                    text="Provide transparency about time spent and usage patterns",
                )
            ],
        ),
        # Social Pressure
        PatternDefinition(
            id="ieee_7010_social_fomo",
            name="FOMO Inducement",
            description="Creating fear of missing out through time-limited content or social pressure",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "story/status expiration timers",
                    "limited time badges",
                    "friends activity feed",
                    "online status indicators",
                ],
                textual_patterns=[
                    "expires in",
                    "available for",
                    "limited time",
                    "friends are watching",
                    "don't miss out",
                    "everyone is",
                ],
                behavioral_signals=[
                    "ephemeral content (24 hours)",
                    "real-time friend activity updates",
                    "disappearing messages",
                ],
            ),
            severity=Severity.SEVERE,
            confidence_threshold=0.75,
            legal_citations=[
                Citation(
                    source="IEEE 7010-2020",
                    article="6.5.1",
                    text="Avoid exploiting social anxiety and fear of exclusion",
                )
            ],
            examples=["Instagram Stories", "Snapchat ephemeral content", "LinkedIn 'trending' posts"],
        ),
        PatternDefinition(
            id="ieee_7010_social_comparison",
            name="Social Comparison Triggers",
            description="Emphasizing metrics that encourage unhealthy social comparison",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "prominent follower counts",
                    "like count displays",
                    "view count indicators",
                    "ranking/leaderboard displays",
                ],
                textual_patterns=[
                    "followers",
                    "likes",
                    "views",
                    "top ranked",
                    "most popular",
                ],
                structural_markers=[
                    "engagement metric displays",
                    "comparison widgets",
                    "popularity indicators",
                ],
            ),
            severity=Severity.MODERATE,
            confidence_threshold=0.7,
            legal_citations=[
                Citation(
                    source="IEEE 7010-2020",
                    article="6.5.2",
                    text="Design should not encourage harmful social comparison",
                )
            ],
        ),
        # Autonomy Violation
        PatternDefinition(
            id="ieee_7010_autonomy_difficult_optout",
            name="Difficult Opt-out",
            description="Making it difficult to disable features, delete accounts, or opt out of engagement",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "opt-out buried in settings",
                    "multiple confirmation dialogs",
                    "delete account option hard to find",
                ],
                textual_patterns=[
                    "are you sure",
                    "you'll lose access",
                    "think carefully",
                    "permanent decision",
                ],
                structural_markers=[
                    "multi-step opt-out process",
                    "settings deeply nested",
                    "no unsubscribe link in notification settings",
                ],
                behavioral_signals=[
                    "opt-out requires > 5 steps",
                    "account deletion requires contact support",
                    "cool-off period before deletion",
                ],
            ),
            severity=Severity.SEVERE,
            confidence_threshold=0.8,
            legal_citations=[
                Citation(
                    source="IEEE 7010-2020",
                    article="6.2.1",
                    text="Users should have easy control over their engagement and data",
                )
            ],
            examples=[
                "Facebook account deletion process",
                "Amazon Prime cancellation flow",
                "Newspaper subscription cancellation",
            ],
        ),
        PatternDefinition(
            id="ieee_7010_autonomy_forced_engagement",
            name="Forced Engagement",
            description="Requiring social engagement to access features or content",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "locked features with social requirement",
                    "invite friends to unlock",
                    "share to continue",
                ],
                textual_patterns=[
                    "invite friends to unlock",
                    "share to access",
                    "follow to see",
                    "connect to continue",
                ],
                structural_markers=[
                    "content gated by social action",
                    "feature locked until sharing",
                ],
                behavioral_signals=[
                    "cannot proceed without social action",
                    "forced friend invitation",
                ],
            ),
            severity=Severity.MODERATE,
            confidence_threshold=0.85,
            legal_citations=[
                Citation(
                    source="IEEE 7010-2020",
                    article="6.2.2",
                    text="Features should not require unwanted social disclosure",
                )
            ],
        ),
        # Notification Abuse
        PatternDefinition(
            id="ieee_7010_notification_overload",
            name="Notification Overload",
            description="Excessive notifications designed to re-engage users frequently",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "notification permission prompt on first visit",
                    "multiple notification toggles (all on by default)",
                    "notification badges everywhere",
                ],
                textual_patterns=[
                    "enable notifications",
                    "don't miss updates",
                    "stay informed",
                    "get notified when",
                ],
                structural_markers=[
                    "notification permission request",
                    "multiple notification categories (all enabled)",
                ],
                behavioral_signals=[
                    "notification prompt before meaningful engagement",
                    "opt-out requires disabling many categories individually",
                ],
            ),
            severity=Severity.MODERATE,
            confidence_threshold=0.7,
            legal_citations=[
                Citation(
                    source="IEEE 7010-2020",
                    article="6.4.3",
                    text="Notification systems should respect user attention and time",
                )
            ],
        ),
    ]

    return DarkPatternFramework(
        name="IEEE 7010-2020",
        version="1.0",
        description="Well-being impact indicators for autonomous and intelligent systems",
        patterns=patterns,
    )


# Singleton instance
IEEE7010Framework = create_ieee_7010_framework()
