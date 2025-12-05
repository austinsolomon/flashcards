"""
ICO Age Appropriate Design Code (Children's Code)
UK Information Commissioner's Office

Framework focused on detecting patterns that harm children through
inadequate privacy defaults, excessive data collection, inappropriate
transparency, and harmful content exposure.
"""

from src.frameworks.base import (
    Citation,
    DarkPatternFramework,
    DetectionRules,
    EvidenceType,
    PatternDefinition,
    Severity,
)


def create_ico_aadc_framework() -> DarkPatternFramework:
    """Create ICO AADC framework for child-focused dark pattern detection."""

    patterns = [
        # Privacy by Default
        PatternDefinition(
            id="ico_aadc_privacy_default_public",
            name="Default Public Profiles for Children",
            description="Child accounts default to public/discoverable rather than private",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "profile visibility set to public by default",
                    "location sharing enabled by default",
                    "content visible to all by default",
                ],
                textual_patterns=[
                    "public profile",
                    "everyone can see",
                    "visible to all",
                ],
                structural_markers=[
                    "privacy settings default to permissive",
                    "no age-based privacy differentiation",
                ],
                behavioral_signals=[
                    "child account created with public visibility",
                    "no privacy prompt during child signup",
                ],
            ),
            severity=Severity.CRITICAL,
            confidence_threshold=0.85,
            legal_citations=[
                Citation(
                    source="ICO Age Appropriate Design Code",
                    article="Standard 4",
                    text="Privacy settings must be 'high' by default for children",
                    url="https://ico.org.uk/for-organisations/guide-to-data-protection/ico-codes-of-practice/age-appropriate-design-code/",
                )
            ],
        ),
        PatternDefinition(
            id="ico_aadc_privacy_default_tracking",
            name="Default Data Sharing for Children",
            description="Tracking and data sharing enabled by default for child users",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "tracking enabled by default",
                    "data sharing toggles on",
                    "marketing consent pre-selected",
                ],
                structural_markers=[
                    "tracking cookies set without consent",
                    "analytics enabled for all ages",
                ],
                behavioral_signals=[
                    "child data collected without explicit opt-in",
                    "no age-based tracking differentiation",
                ],
            ),
            severity=Severity.CRITICAL,
            confidence_threshold=0.8,
            legal_citations=[
                Citation(
                    source="ICO Age Appropriate Design Code",
                    article="Standard 4",
                    text="Profiling, tracking, and location services must be off by default for children",
                )
            ],
        ),
        # Data Minimization
        PatternDefinition(
            id="ico_aadc_data_excessive_collection",
            name="Excessive Data Collection from Children",
            description="Collecting more data than necessary from child users",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "long registration forms for children",
                    "optional fields presented as required",
                    "personal questions beyond necessity",
                ],
                textual_patterns=[
                    "required",
                    "tell us about yourself",
                    "complete your profile",
                ],
                structural_markers=[
                    "extensive data collection forms",
                    "mandatory non-essential fields",
                ],
            ),
            severity=Severity.SEVERE,
            confidence_threshold=0.75,
            legal_citations=[
                Citation(
                    source="ICO Age Appropriate Design Code",
                    article="Standard 5",
                    text="Collect only the minimum amount of personal data necessary",
                )
            ],
        ),
        PatternDefinition(
            id="ico_aadc_data_location_always",
            name="Always-On Location Tracking",
            description="Requiring constant location access for child-targeted apps",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "location permission request",
                    "'always allow' location prompt",
                    "location required for features",
                ],
                textual_patterns=[
                    "allow location access",
                    "always",
                    "location required",
                ],
                behavioral_signals=[
                    "app requires 'always' location permission",
                    "no 'while using' option for children",
                ],
            ),
            severity=Severity.CRITICAL,
            confidence_threshold=0.9,
            legal_citations=[
                Citation(
                    source="ICO Age Appropriate Design Code",
                    article="Standard 5",
                    text="Location data collection should be minimized and not 'always on'",
                )
            ],
        ),
        # Transparency
        PatternDefinition(
            id="ico_aadc_transparency_complex_privacy",
            name="Non-Age-Appropriate Privacy Policies",
            description="Privacy policies too complex for children to understand",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "lengthy legal document",
                    "small font legal text",
                    "no simplified explanation",
                ],
                textual_patterns=[
                    "privacy policy",
                    "terms of service",
                    "legal jargon",
                ],
                structural_markers=[
                    "no child-friendly privacy explainer",
                    "adult-level language in policies",
                ],
            ),
            severity=Severity.SEVERE,
            confidence_threshold=0.7,
            legal_citations=[
                Citation(
                    source="ICO Age Appropriate Design Code",
                    article="Standard 7",
                    text="Privacy information must be concise, prominent, and age-appropriate",
                )
            ],
        ),
        PatternDefinition(
            id="ico_aadc_transparency_hidden_commercial",
            name="Hidden Commercial Relationships",
            description="Not clearly disclosing sponsored content or advertising to children",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "ads that look like content",
                    "influencer partnerships not disclosed",
                    "sponsored content without clear labels",
                ],
                textual_patterns=[
                    "ad",
                    "sponsored",
                    "partner",
                ],
                structural_markers=[
                    "advertising without age-appropriate disclosure",
                    "unclear commercial boundaries",
                ],
            ),
            severity=Severity.SEVERE,
            confidence_threshold=0.75,
            legal_citations=[
                Citation(
                    source="ICO Age Appropriate Design Code",
                    article="Standard 7",
                    text="Commercial intent must be clearly communicated to children",
                )
            ],
        ),
        # Nudge Techniques
        PatternDefinition(
            id="ico_aadc_nudge_children_sharing",
            name="Nudging Children to Share Data",
            description="Using nudges to encourage children to reduce privacy or share more data",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "prompts to make profile public",
                    "suggestions to share location",
                    "encouragement to add personal info",
                ],
                textual_patterns=[
                    "complete your profile",
                    "add more info",
                    "share your location",
                    "everyone else is",
                ],
                behavioral_signals=[
                    "repeated prompts for data sharing",
                    "privacy reduction suggestions",
                ],
            ),
            severity=Severity.CRITICAL,
            confidence_threshold=0.8,
            legal_citations=[
                Citation(
                    source="ICO Age Appropriate Design Code",
                    article="Standard 8",
                    text="Do not use nudge techniques to lead children to reduce privacy or increase data sharing",
                )
            ],
        ),
        PatternDefinition(
            id="ico_aadc_nudge_default_sharing",
            name="Encouraging Oversharing",
            description="Design that encourages children to share more than they otherwise would",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "prompts to share personal content",
                    "default share settings",
                    "prominent share buttons",
                ],
                textual_patterns=[
                    "share this",
                    "tell everyone",
                    "post about",
                    "let friends know",
                ],
            ),
            severity=Severity.SEVERE,
            confidence_threshold=0.7,
            legal_citations=[
                Citation(
                    source="ICO Age Appropriate Design Code",
                    article="Standard 8",
                    text="Design should not encourage children to overshare",
                )
            ],
        ),
        # Geolocation
        PatternDefinition(
            id="ico_aadc_geo_default_on",
            name="Geolocation On by Default",
            description="Location services enabled by default for child users",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "location toggle on by default",
                    "geotags on posts by default",
                    "location sharing in profile",
                ],
                structural_markers=[
                    "geolocation enabled without explicit opt-in",
                ],
                behavioral_signals=[
                    "location data collected from first use",
                    "no location permission prompt",
                ],
            ),
            severity=Severity.CRITICAL,
            confidence_threshold=0.9,
            legal_citations=[
                Citation(
                    source="ICO Age Appropriate Design Code",
                    article="Standard 9",
                    text="Geolocation must be switched off by default for children",
                )
            ],
        ),
        # Parental Controls
        PatternDefinition(
            id="ico_aadc_parental_no_controls",
            name="Lack of Parental Controls",
            description="No parental control tools for services likely used by children",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "no parental controls section",
                    "no family settings",
                    "no child safety features",
                ],
                structural_markers=[
                    "absence of parental control features",
                    "no age-gated settings",
                ],
            ),
            severity=Severity.SEVERE,
            confidence_threshold=0.8,
            legal_citations=[
                Citation(
                    source="ICO Age Appropriate Design Code",
                    article="Standard 10",
                    text="Provide parental controls unless service is clearly not accessed by children",
                )
            ],
        ),
        PatternDefinition(
            id="ico_aadc_parental_difficult_access",
            name="Difficult-to-Access Parental Controls",
            description="Parental controls exist but are hidden or difficult to use",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "parental controls deeply nested in settings",
                    "complex setup process for controls",
                ],
                structural_markers=[
                    "parental controls require technical knowledge",
                    "multi-step activation process",
                ],
            ),
            severity=Severity.MODERATE,
            confidence_threshold=0.75,
            legal_citations=[
                Citation(
                    source="ICO Age Appropriate Design Code",
                    article="Standard 10",
                    text="Parental controls should be accessible and easy to use",
                )
            ],
        ),
        # Profiling and Targeting
        PatternDefinition(
            id="ico_aadc_profiling_behavioral",
            name="Behavioral Profiling of Children",
            description="Creating behavioral profiles of child users for advertising or content",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "personalized ads to children",
                    "behavior-based recommendations",
                    "targeted content based on activity",
                ],
                textual_patterns=[
                    "based on your activity",
                    "recommended for you",
                    "because you liked",
                ],
                structural_markers=[
                    "profiling algorithms for child users",
                    "behavioral tracking implementation",
                ],
            ),
            severity=Severity.CRITICAL,
            confidence_threshold=0.75,
            legal_citations=[
                Citation(
                    source="ICO Age Appropriate Design Code",
                    article="Standard 11",
                    text="Profiling must be off by default for children unless you can demonstrate compelling reason",
                )
            ],
        ),
        PatternDefinition(
            id="ico_aadc_advertising_targeted",
            name="Targeted Advertising to Children",
            description="Serving behaviorally targeted ads to child users",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "personalized ads in child app",
                    "retargeted advertising",
                    "behavior-based ad delivery",
                ],
                structural_markers=[
                    "ad targeting based on child data",
                    "remarketing to children",
                ],
            ),
            severity=Severity.CRITICAL,
            confidence_threshold=0.85,
            legal_citations=[
                Citation(
                    source="ICO Age Appropriate Design Code",
                    article="Standard 12",
                    text="Do not use profiling for targeting children with advertising",
                )
            ],
        ),
        # Detrimental Use
        PatternDefinition(
            id="ico_aadc_detrimental_addictive",
            name="Addictive Design for Children",
            description="Features designed to maximize child usage beyond their best interests",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "infinite scroll in kids apps",
                    "streaks and daily login rewards",
                    "auto-play next content",
                ],
                textual_patterns=[
                    "day streak",
                    "keep playing",
                    "one more level",
                ],
                behavioral_signals=[
                    "addictive mechanics in child-targeted app",
                    "no usage time limits",
                ],
            ),
            severity=Severity.CRITICAL,
            confidence_threshold=0.8,
            legal_citations=[
                Citation(
                    source="ICO Age Appropriate Design Code",
                    article="Standard 13",
                    text="Identify and mitigate risks of harm to children from design features",
                )
            ],
        ),
        PatternDefinition(
            id="ico_aadc_detrimental_harmful_content",
            name="Exposure to Harmful Content",
            description="Inadequate protections from harmful content for child users",
            detection_rules=DetectionRules(
                visual_indicators=[
                    "no content filtering for children",
                    "inappropriate content recommendations",
                    "no age-appropriate content controls",
                ],
                structural_markers=[
                    "absence of content moderation for children",
                    "adult content accessible to children",
                ],
            ),
            severity=Severity.CRITICAL,
            confidence_threshold=0.75,
            legal_citations=[
                Citation(
                    source="ICO Age Appropriate Design Code",
                    article="Standard 13",
                    text="Protect children from harmful content through age-appropriate measures",
                )
            ],
        ),
    ]

    return DarkPatternFramework(
        name="ICO Age Appropriate Design Code (AADC)",
        version="2020",
        description="UK ICO requirements for child-focused design and privacy",
        patterns=patterns,
    )


# Singleton instance
ICOAADCFramework = create_ico_aadc_framework()
