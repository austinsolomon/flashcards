"""
Evidence models for dark pattern detection.

Defines Pydantic schemas for capturing screenshots, DOM snapshots,
reasoning chains, and other evidence types.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field

from src.frameworks.base import Citation, Severity


class Screenshot(BaseModel):
    """Screenshot evidence with metadata."""

    file_path: str = Field(..., description="Path to screenshot file")
    url: str = Field(..., description="URL where screenshot was captured")
    timestamp: datetime = Field(default_factory=datetime.now)
    width: int = Field(..., description="Screenshot width in pixels")
    height: int = Field(..., description="Screenshot height in pixels")
    viewport_width: int = Field(..., description="Browser viewport width")
    viewport_height: int = Field(..., description="Browser viewport height")
    scroll_position: dict[str, int] = Field(
        default_factory=lambda: {"x": 0, "y": 0}, description="Scroll position when captured"
    )
    annotations: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Visual annotations (bounding boxes, highlights, etc.)",
    )

    def add_bounding_box(self, x: int, y: int, width: int, height: int, label: str) -> None:
        """Add a bounding box annotation."""
        self.annotations.append(
            {"type": "bounding_box", "x": x, "y": y, "width": width, "height": height, "label": label}
        )

    def add_highlight(self, selector: str, label: str) -> None:
        """Add an element highlight annotation."""
        self.annotations.append({"type": "highlight", "selector": selector, "label": label})


class DOMSnapshot(BaseModel):
    """DOM structure snapshot with metadata."""

    file_path: str = Field(..., description="Path to DOM snapshot file (HTML/JSON)")
    url: str = Field(..., description="URL where DOM was captured")
    timestamp: datetime = Field(default_factory=datetime.now)
    snapshot_type: str = Field(default="full", description="Type: full, partial, serialized")
    relevant_selectors: list[str] = Field(
        default_factory=list, description="CSS selectors of relevant elements"
    )
    element_count: int = Field(..., description="Total number of DOM elements")
    interactive_element_count: int = Field(
        default=0, description="Number of interactive elements (buttons, links, inputs)"
    )


class NetworkLog(BaseModel):
    """Network activity log for tracking requests."""

    timestamp: datetime = Field(default_factory=datetime.now)
    url: str = Field(..., description="Page URL")
    requests: list[dict[str, Any]] = Field(
        default_factory=list, description="Network requests during session"
    )
    third_party_domains: list[str] = Field(
        default_factory=list, description="Third-party domains contacted"
    )
    tracking_requests: list[dict[str, Any]] = Field(
        default_factory=list, description="Identified tracking requests"
    )


class UserFlow(BaseModel):
    """User journey/flow through the interface."""

    flow_name: str = Field(..., description="Name of the flow (e.g., 'signup', 'cancellation')")
    start_url: str = Field(..., description="Starting URL")
    end_url: Optional[str] = Field(None, description="Ending URL (if completed)")
    steps: list[dict[str, Any]] = Field(default_factory=list, description="Flow steps")
    total_steps: int = Field(default=0, description="Total number of steps")
    completion_time_seconds: Optional[float] = Field(
        None, description="Time to complete flow"
    )
    abandoned: bool = Field(default=False, description="Whether flow was abandoned")

    def add_step(
        self,
        action: str,
        url: str,
        screenshot_path: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """Add a step to the flow."""
        self.steps.append(
            {
                "step_number": len(self.steps) + 1,
                "action": action,
                "url": url,
                "screenshot_path": screenshot_path,
                "description": description,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self.total_steps = len(self.steps)


class ReasoningStep(BaseModel):
    """Single step in reasoning chain."""

    step_number: int
    timestamp: datetime = Field(default_factory=datetime.now)
    thought: str = Field(..., description="What the agent is thinking")
    observation: str = Field(..., description="What the agent observes")
    action: str = Field(..., description="Action taken")
    rationale: str = Field(..., description="Why this action was chosen")


class ReasoningChain(BaseModel):
    """Complete reasoning chain for a detection or navigation decision."""

    chain_id: str = Field(..., description="Unique chain identifier")
    timestamp: datetime = Field(default_factory=datetime.now)
    context: str = Field(..., description="Context for this reasoning chain")
    steps: list[ReasoningStep] = Field(default_factory=list)
    conclusion: str = Field(..., description="Final conclusion")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in conclusion")

    def add_step(self, thought: str, observation: str, action: str, rationale: str) -> None:
        """Add a reasoning step to the chain."""
        step = ReasoningStep(
            step_number=len(self.steps) + 1,
            thought=thought,
            observation=observation,
            action=action,
            rationale=rationale,
        )
        self.steps.append(step)


class Evidence(BaseModel):
    """Complete evidence package for a dark pattern finding."""

    evidence_id: str = Field(..., description="Unique evidence identifier")
    pattern_id: str = Field(..., description="ID of detected pattern")
    framework_name: str = Field(..., description="Framework that detected this")
    timestamp: datetime = Field(default_factory=datetime.now)
    url: str = Field(..., description="URL where pattern was detected")

    # Evidence artifacts
    screenshots: list[Screenshot] = Field(default_factory=list)
    dom_snapshots: list[DOMSnapshot] = Field(default_factory=list)
    network_logs: list[NetworkLog] = Field(default_factory=list)
    user_flows: list[UserFlow] = Field(default_factory=list)
    reasoning_chains: list[ReasoningChain] = Field(default_factory=list)

    # Detection details
    matched_rules: dict[str, list[str]] = Field(
        default_factory=dict, description="Which detection rules matched"
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    severity: Severity = Field(...)

    # Citations
    legal_citations: list[Citation] = Field(default_factory=list)

    # Metadata
    element_selector: Optional[str] = Field(None, description="CSS selector for primary element")
    additional_context: dict[str, Any] = Field(
        default_factory=dict, description="Additional contextual information"
    )

    def add_screenshot(self, screenshot: Screenshot) -> None:
        """Add screenshot to evidence."""
        self.screenshots.append(screenshot)

    def add_dom_snapshot(self, snapshot: DOMSnapshot) -> None:
        """Add DOM snapshot to evidence."""
        self.dom_snapshots.append(snapshot)

    def add_reasoning_chain(self, chain: ReasoningChain) -> None:
        """Add reasoning chain to evidence."""
        self.reasoning_chains.append(chain)


class Finding(BaseModel):
    """High-level finding representing a detected dark pattern."""

    finding_id: str = Field(..., description="Unique finding identifier")
    pattern_id: str = Field(..., description="ID of detected pattern")
    pattern_name: str = Field(..., description="Human-readable pattern name")
    framework_name: str = Field(..., description="Framework that detected this")
    severity: Severity = Field(...)
    confidence: float = Field(..., ge=0.0, le=1.0)

    # Location
    url: str = Field(..., description="URL where pattern was found")
    page_title: Optional[str] = Field(None, description="Page title")

    # Evidence reference
    evidence: Evidence = Field(..., description="Complete evidence package")

    # Summary
    summary: str = Field(..., description="Brief summary of finding")
    description: str = Field(..., description="Detailed description")
    recommendation: str = Field(..., description="Recommended remediation")

    # Status
    validated: bool = Field(default=False, description="Whether finding has been validated")
    false_positive: bool = Field(default=False, description="Marked as false positive")
    notes: str = Field(default="", description="Reviewer notes")

    timestamp: datetime = Field(default_factory=datetime.now)


class ExplorationSession(BaseModel):
    """Complete exploration session with all findings and metadata."""

    session_id: str = Field(..., description="Unique session identifier")
    session_name: str = Field(..., description="Human-readable session name")
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = Field(None)

    # Configuration
    target_url: str = Field(..., description="Initial target URL")
    frameworks_used: list[str] = Field(..., description="Frameworks applied")
    max_depth: int = Field(default=5, description="Maximum exploration depth")

    # Results
    findings: list[Finding] = Field(default_factory=list)
    pages_visited: list[str] = Field(default_factory=list)
    total_patterns_checked: int = Field(default=0)
    total_patterns_detected: int = Field(default=0)

    # Metadata
    agent_version: str = Field(default="0.1.0")
    model_used: str = Field(default="claude-sonnet-4-5-20250929")

    @property
    def duration_seconds(self) -> Optional[float]:
        """Get session duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    @property
    def findings_by_severity(self) -> dict[Severity, list[Finding]]:
        """Group findings by severity."""
        by_severity: dict[Severity, list[Finding]] = {
            Severity.MINOR: [],
            Severity.MODERATE: [],
            Severity.SEVERE: [],
            Severity.CRITICAL: [],
        }
        for finding in self.findings:
            by_severity[finding.severity].append(finding)
        return by_severity

    @property
    def findings_by_framework(self) -> dict[str, list[Finding]]:
        """Group findings by framework."""
        by_framework: dict[str, list[Finding]] = {}
        for finding in self.findings:
            if finding.framework_name not in by_framework:
                by_framework[finding.framework_name] = []
            by_framework[finding.framework_name].append(finding)
        return by_framework

    def add_finding(self, finding: Finding) -> None:
        """Add a finding to the session."""
        self.findings.append(finding)
        self.total_patterns_detected += 1

    def mark_complete(self) -> None:
        """Mark session as complete."""
        self.end_time = datetime.now()
