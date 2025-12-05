"""
Base classes for dark pattern detection frameworks.

Provides the foundation for implementing multiple legal/policy frameworks
with configurable detection rules, evidence requirements, and severity levels.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class Severity(str, Enum):
    """Severity levels for detected dark patterns."""

    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class EvidenceType(str, Enum):
    """Types of evidence that can be collected."""

    SCREENSHOT = "screenshot"
    DOM_SNAPSHOT = "dom_snapshot"
    NETWORK_LOG = "network_log"
    USER_FLOW = "user_flow"
    REASONING_CHAIN = "reasoning_chain"
    COMPARISON = "comparison"


class Citation(BaseModel):
    """Legal or policy citation for a dark pattern."""

    source: str = Field(..., description="Source document (e.g., 'DSA Article 28')")
    article: Optional[str] = Field(None, description="Specific article number")
    paragraph: Optional[str] = Field(None, description="Specific paragraph")
    text: str = Field(..., description="Relevant quoted text")
    url: Optional[str] = Field(None, description="URL to full text")


class DetectionRules(BaseModel):
    """Detection rules for identifying a dark pattern."""

    visual_indicators: list[str] = Field(
        default_factory=list,
        description="Visual patterns (e.g., 'red button larger than alternatives')",
    )
    textual_patterns: list[str] = Field(
        default_factory=list,
        description="Text patterns (e.g., 'limited time', 'act now')",
    )
    structural_markers: list[str] = Field(
        default_factory=list,
        description="DOM/structural patterns (e.g., 'hidden form fields')",
    )
    behavioral_signals: list[str] = Field(
        default_factory=list,
        description="Behavioral patterns (e.g., 'auto-play after 3 seconds')",
    )

    @field_validator("visual_indicators", "textual_patterns", "structural_markers", "behavioral_signals")
    @classmethod
    def validate_non_empty_strings(cls, v: list[str]) -> list[str]:
        """Ensure all rule strings are non-empty."""
        return [item.strip() for item in v if item.strip()]


class PatternDefinition(BaseModel):
    """Definition of a specific dark pattern within a framework."""

    id: str = Field(..., description="Unique pattern identifier (e.g., 'dsa_28_1a')")
    name: str = Field(..., description="Human-readable pattern name")
    description: str = Field(..., description="Detailed description of the pattern")
    detection_rules: DetectionRules = Field(..., description="Rules for detecting this pattern")
    severity: Severity = Field(..., description="Severity level")
    evidence_requirements: list[EvidenceType] = Field(
        default_factory=lambda: [EvidenceType.SCREENSHOT, EvidenceType.REASONING_CHAIN],
        description="Required evidence types",
    )
    legal_citations: list[Citation] = Field(
        default_factory=list, description="Legal/policy citations"
    )
    confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence to report (0.0-1.0)",
    )
    examples: list[str] = Field(
        default_factory=list, description="Example instances of this pattern"
    )


class DarkPatternFramework(BaseModel):
    """Base class for all dark pattern detection frameworks."""

    name: str = Field(..., description="Framework name (e.g., 'IEEE 7010-2020')")
    version: str = Field(..., description="Framework version")
    description: str = Field(..., description="Framework description")
    patterns: list[PatternDefinition] = Field(..., description="Pattern definitions")
    enabled: bool = Field(default=True, description="Whether framework is active")

    def get_pattern(self, pattern_id: str) -> Optional[PatternDefinition]:
        """Get a specific pattern by ID."""
        return next((p for p in self.patterns if p.id == pattern_id), None)

    def get_patterns_by_severity(self, severity: Severity) -> list[PatternDefinition]:
        """Get all patterns of a specific severity."""
        return [p for p in self.patterns if p.severity == severity]

    def adjust_confidence_threshold(self, pattern_id: str, threshold: float) -> bool:
        """Adjust confidence threshold for a specific pattern."""
        pattern = self.get_pattern(pattern_id)
        if pattern:
            pattern.confidence_threshold = max(0.0, min(1.0, threshold))
            return True
        return False

    def validate_evidence(self, pattern_id: str, evidence_types: list[EvidenceType]) -> bool:
        """Check if provided evidence meets pattern requirements."""
        pattern = self.get_pattern(pattern_id)
        if not pattern:
            return False
        return all(req in evidence_types for req in pattern.evidence_requirements)


class DetectionMatch(BaseModel):
    """Represents a detected pattern match."""

    pattern_id: str = Field(..., description="ID of matched pattern")
    framework_name: str = Field(..., description="Framework that detected this")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    matched_rules: dict[str, list[str]] = Field(
        ..., description="Which rules matched (e.g., {'visual': ['red button'], 'textual': []})"
    )
    timestamp: datetime = Field(default_factory=datetime.now, description="Detection timestamp")
    url: str = Field(..., description="URL where pattern was detected")
    element_selector: Optional[str] = Field(
        None, description="CSS selector for element (if applicable)"
    )


class AnalysisResult(BaseModel):
    """Result of analyzing a page with a framework."""

    framework_name: str = Field(..., description="Framework that performed analysis")
    url: str = Field(..., description="Analyzed URL")
    timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    matches: list[DetectionMatch] = Field(default_factory=list, description="Detected patterns")
    total_patterns_checked: int = Field(..., description="Number of patterns evaluated")
    analysis_duration_seconds: float = Field(..., description="Time taken for analysis")

    @property
    def has_findings(self) -> bool:
        """Whether any patterns were detected."""
        return len(self.matches) > 0

    @property
    def highest_severity(self) -> Optional[Severity]:
        """Get the highest severity level among findings."""
        if not self.matches:
            return None
        # This would need pattern definitions to determine severity
        return Severity.CRITICAL  # Placeholder

    def get_matches_by_pattern(self, pattern_id: str) -> list[DetectionMatch]:
        """Get all matches for a specific pattern."""
        return [m for m in self.matches if m.pattern_id == pattern_id]


class FrameworkConfig(BaseModel):
    """Configuration for framework behavior."""

    framework_name: str
    enabled: bool = True
    confidence_overrides: dict[str, float] = Field(
        default_factory=dict, description="Pattern-specific confidence thresholds"
    )
    custom_rules: dict[str, Any] = Field(
        default_factory=dict, description="Additional custom detection rules"
    )
    focus_patterns: list[str] = Field(
        default_factory=list,
        description="If specified, only check these pattern IDs",
    )
    exclude_patterns: list[str] = Field(
        default_factory=list, description="Pattern IDs to exclude from checking"
    )

    def should_check_pattern(self, pattern_id: str) -> bool:
        """Determine if a pattern should be checked based on config."""
        if not self.enabled:
            return False
        if pattern_id in self.exclude_patterns:
            return False
        if self.focus_patterns and pattern_id not in self.focus_patterns:
            return False
        return True

    def get_confidence_threshold(self, pattern_id: str, default: float) -> float:
        """Get confidence threshold for a pattern (uses override if exists)."""
        return self.confidence_overrides.get(pattern_id, default)
