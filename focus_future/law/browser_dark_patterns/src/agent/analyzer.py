"""
Multi-framework dark pattern analyzer.

Applies detection rules from multiple frameworks to analyze pages for dark patterns.
"""

import re
from typing import Any, Optional

from src.evidence.models import Evidence, Finding
from src.evidence.collector import EvidenceCollector
from src.frameworks.base import (
    AnalysisResult,
    DarkPatternFramework,
    DetectionMatch,
    Severity,
)
from src.agent.reasoning import PageAnalysis, ReasoningEngine
from src.utils.browser import BrowserManager


class MultiFrameworkAnalyzer:
    """Analyzes pages using multiple dark pattern frameworks."""

    def __init__(
        self,
        frameworks: list[DarkPatternFramework],
        browser: BrowserManager,
        evidence_collector: EvidenceCollector,
        reasoning_engine: ReasoningEngine,
    ):
        """
        Initialize analyzer.

        Args:
            frameworks: List of frameworks to apply
            browser: Browser manager
            evidence_collector: Evidence collector
            reasoning_engine: Reasoning engine
        """
        self.frameworks = frameworks
        self.browser = browser
        self.evidence_collector = evidence_collector
        self.reasoning_engine = reasoning_engine

    async def analyze_page(
        self, url: str, page_analysis: PageAnalysis
    ) -> list[Finding]:
        """
        Analyze page with all frameworks.

        Args:
            url: Page URL
            page_analysis: Visual analysis of page

        Returns:
            List of findings
        """
        findings = []

        # Get page content for textual analysis
        html_content = await self.browser.get_page_content()

        for framework in self.frameworks:
            framework_findings = await self._analyze_with_framework(
                framework, url, page_analysis, html_content
            )
            findings.extend(framework_findings)

        return findings

    async def _analyze_with_framework(
        self,
        framework: DarkPatternFramework,
        url: str,
        page_analysis: PageAnalysis,
        html_content: str,
    ) -> list[Finding]:
        """Analyze page with a specific framework."""
        findings = []

        for pattern in framework.patterns:
            matched_rules = {
                "visual": [],
                "textual": [],
                "structural": [],
                "behavioral": [],
            }

            # Visual indicator matching (from Claude's observations)
            for indicator in pattern.detection_rules.visual_indicators:
                for observation in page_analysis.visual_observations:
                    if self._fuzzy_match(indicator.lower(), observation.lower()):
                        matched_rules["visual"].append(indicator)
                        break

            # Textual pattern matching
            for text_pattern in pattern.detection_rules.textual_patterns:
                if self._text_found_in_html(text_pattern, html_content):
                    matched_rules["textual"].append(text_pattern)

            # Structural marker matching
            for marker in pattern.detection_rules.structural_markers:
                if await self._structural_marker_present(marker):
                    matched_rules["structural"].append(marker)

            # Calculate confidence based on matches
            total_rules = (
                len(pattern.detection_rules.visual_indicators)
                + len(pattern.detection_rules.textual_patterns)
                + len(pattern.detection_rules.structural_markers)
            )
            total_matches = sum(len(v) for v in matched_rules.values())

            if total_rules > 0 and total_matches > 0:
                confidence = total_matches / total_rules

                # Check confidence threshold
                if confidence >= pattern.confidence_threshold:
                    # Create finding
                    finding = await self._create_finding(
                        pattern, framework, url, confidence, matched_rules, page_analysis
                    )
                    findings.append(finding)

        return findings

    def _fuzzy_match(self, pattern: str, text: str, threshold: float = 0.6) -> bool:
        """Check if pattern fuzzy matches text."""
        pattern_words = set(pattern.split())
        text_words = set(text.split())
        if not pattern_words:
            return False
        overlap = len(pattern_words & text_words)
        return overlap / len(pattern_words) >= threshold

    def _text_found_in_html(self, pattern: str, html: str) -> bool:
        """Check if text pattern exists in HTML."""
        # Case-insensitive search
        return re.search(re.escape(pattern), html, re.IGNORECASE) is not None

    async def _structural_marker_present(self, marker: str) -> bool:
        """Check if structural marker is present."""
        if not self.browser.page:
            return False

        # Simple heuristic checks for common markers
        marker_lower = marker.lower()

        if "infinite scroll" in marker_lower:
            # Check for lazy loading or infinite scroll indicators
            return await self.browser.evaluate("""
                () => {
                    return document.querySelector('[data-infinite-scroll], [class*="infinite"]') !== null;
                }
            """)

        if "hidden" in marker_lower or "nested" in marker_lower:
            # Check for deeply nested or hidden elements
            return await self.browser.evaluate("""
                () => {
                    const hiddenInputs = document.querySelectorAll('input[type="hidden"]');
                    return hiddenInputs.length > 0;
                }
            """)

        # Default: check if related text exists in DOM
        return await self.browser.evaluate(
            f"""
            () => {{
                const text = '{marker}';
                return document.body.textContent.toLowerCase().includes(text.toLowerCase());
            }}
        """
        )

    async def _create_finding(
        self,
        pattern: Any,
        framework: DarkPatternFramework,
        url: str,
        confidence: float,
        matched_rules: dict[str, list[str]],
        page_analysis: PageAnalysis,
    ) -> Finding:
        """Create a finding with evidence."""
        # Capture evidence
        screenshot = await self.evidence_collector.capture_screenshot(
            self.browser.page, url, label=pattern.id
        )
        dom_snapshot = await self.evidence_collector.capture_dom_snapshot(
            self.browser.page, url, label=pattern.id
        )

        # Create reasoning chain
        evidence_summary = f"Screenshot captured, DOM snapshot saved. Matched {sum(len(v) for v in matched_rules.values())} rules."
        reasoning_chain = self.reasoning_engine.create_detection_reasoning(
            pattern.name, matched_rules, confidence, evidence_summary
        )

        # Save reasoning chain
        self.evidence_collector.save_reasoning_chain(reasoning_chain)

        # Create evidence package
        evidence = self.evidence_collector.create_evidence_package(
            pattern_id=pattern.id,
            framework_name=framework.name,
            url=url,
            confidence=confidence,
            severity=pattern.severity,
            matched_rules=matched_rules,
            legal_citations=pattern.legal_citations,
            screenshots=[screenshot],
            dom_snapshots=[dom_snapshot],
            reasoning_chains=[reasoning_chain],
        )

        # Create finding
        finding_id = f"finding_{evidence.evidence_id}"

        finding = Finding(
            finding_id=finding_id,
            pattern_id=pattern.id,
            pattern_name=pattern.name,
            framework_name=framework.name,
            severity=pattern.severity,
            confidence=confidence,
            url=url,
            page_title=page_analysis.title,
            evidence=evidence,
            summary=f"Detected {pattern.name} with {confidence:.0%} confidence",
            description=pattern.description,
            recommendation=f"Review and remediate {pattern.name} pattern according to {framework.name} standards.",
        )

        return finding
