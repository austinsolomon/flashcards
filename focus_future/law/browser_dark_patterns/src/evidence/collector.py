"""
Evidence collector for capturing screenshots, DOM snapshots, and other artifacts.

Handles the actual collection and storage of evidence during agent exploration.
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from playwright.async_api import Page

from src.evidence.models import (
    DOMSnapshot,
    Evidence,
    NetworkLog,
    ReasoningChain,
    Screenshot,
    UserFlow,
)
from src.frameworks.base import Citation, Severity


class EvidenceCollector:
    """Collects and manages evidence artifacts during exploration."""

    def __init__(self, session_id: str, base_dir: Optional[Path] = None):
        """
        Initialize evidence collector.

        Args:
            session_id: Unique session identifier
            base_dir: Base directory for storing evidence (default: ./data/sessions)
        """
        self.session_id = session_id
        self.base_dir = base_dir or Path("./data/sessions")
        self.session_dir = self.base_dir / session_id

        # Create directories
        self.screenshot_dir = self.session_dir / "screenshots"
        self.dom_dir = self.session_dir / "dom_snapshots"
        self.network_dir = self.session_dir / "network_logs"
        self.reasoning_dir = self.session_dir / "reasoning"

        for directory in [
            self.session_dir,
            self.screenshot_dir,
            self.dom_dir,
            self.network_dir,
            self.reasoning_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        # Track evidence count for naming
        self.screenshot_count = 0
        self.dom_count = 0
        self.reasoning_count = 0

    async def capture_screenshot(
        self,
        page: Page,
        url: str,
        label: Optional[str] = None,
        full_page: bool = False,
    ) -> Screenshot:
        """
        Capture screenshot of current page.

        Args:
            page: Playwright page object
            url: Current URL
            label: Optional label for screenshot
            full_page: Whether to capture full page or just viewport

        Returns:
            Screenshot object with metadata
        """
        self.screenshot_count += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{self.screenshot_count:04d}_{timestamp}.png"
        if label:
            safe_label = "".join(c for c in label if c.isalnum() or c in ("_", "-"))
            filename = f"screenshot_{self.screenshot_count:04d}_{safe_label}_{timestamp}.png"

        file_path = self.screenshot_dir / filename

        # Capture screenshot
        await page.screenshot(path=str(file_path), full_page=full_page)

        # Get viewport dimensions
        viewport = page.viewport_size
        viewport_width = viewport["width"] if viewport else 1920
        viewport_height = viewport["height"] if viewport else 1080

        # Get scroll position
        scroll_position = await page.evaluate(
            "() => ({ x: window.scrollX, y: window.scrollY })"
        )

        # Get actual image dimensions
        from PIL import Image

        with Image.open(file_path) as img:
            width, height = img.size

        screenshot = Screenshot(
            file_path=str(file_path.relative_to(self.base_dir)),
            url=url,
            width=width,
            height=height,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            scroll_position=scroll_position,
        )

        return screenshot

    async def capture_dom_snapshot(
        self, page: Page, url: str, label: Optional[str] = None
    ) -> DOMSnapshot:
        """
        Capture DOM snapshot as HTML.

        Args:
            page: Playwright page object
            url: Current URL
            label: Optional label for snapshot

        Returns:
            DOMSnapshot object with metadata
        """
        self.dom_count += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dom_{self.dom_count:04d}_{timestamp}.html"
        if label:
            safe_label = "".join(c for c in label if c.isalnum() or c in ("_", "-"))
            filename = f"dom_{self.dom_count:04d}_{safe_label}_{timestamp}.html"

        file_path = self.dom_dir / filename

        # Get HTML content
        html_content = await page.content()

        # Save to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Count elements
        element_count = await page.evaluate("() => document.querySelectorAll('*').length")

        # Count interactive elements
        interactive_count = await page.evaluate("""
            () => {
                const selectors = 'a, button, input, select, textarea, [onclick], [role="button"]';
                return document.querySelectorAll(selectors).length;
            }
        """)

        snapshot = DOMSnapshot(
            file_path=str(file_path.relative_to(self.base_dir)),
            url=url,
            element_count=element_count,
            interactive_element_count=interactive_count,
        )

        return snapshot

    async def capture_interactive_elements(self, page: Page) -> list[dict[str, Any]]:
        """
        Extract all interactive elements from page.

        Args:
            page: Playwright page object

        Returns:
            List of interactive element descriptors
        """
        elements = await page.evaluate("""
            () => {
                const selectors = 'a, button, input, select, textarea, [onclick], [role="button"]';
                const elements = Array.from(document.querySelectorAll(selectors));

                return elements.map((el, idx) => {
                    const rect = el.getBoundingClientRect();
                    return {
                        index: idx,
                        tag: el.tagName.toLowerCase(),
                        type: el.type || null,
                        text: el.textContent?.trim().substring(0, 100) || '',
                        href: el.href || null,
                        id: el.id || null,
                        classes: Array.from(el.classList),
                        visible: rect.width > 0 && rect.height > 0,
                        position: {
                            x: rect.left,
                            y: rect.top,
                            width: rect.width,
                            height: rect.height
                        }
                    };
                });
            }
        """)

        return elements

    def save_reasoning_chain(self, chain: ReasoningChain) -> str:
        """
        Save reasoning chain to file.

        Args:
            chain: ReasoningChain object

        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reasoning_{timestamp}_{chain.chain_id}.json"
        file_path = self.reasoning_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(chain.model_dump(mode="json"), f, indent=2, default=str)

        return str(file_path.relative_to(self.base_dir))

    def create_evidence_package(
        self,
        pattern_id: str,
        framework_name: str,
        url: str,
        confidence: float,
        severity: Severity,
        matched_rules: dict[str, list[str]],
        legal_citations: list[Citation],
        screenshots: Optional[list[Screenshot]] = None,
        dom_snapshots: Optional[list[DOMSnapshot]] = None,
        reasoning_chains: Optional[list[ReasoningChain]] = None,
        element_selector: Optional[str] = None,
    ) -> Evidence:
        """
        Create a complete evidence package.

        Args:
            pattern_id: ID of detected pattern
            framework_name: Framework name
            url: URL where detected
            confidence: Detection confidence
            severity: Severity level
            matched_rules: Rules that matched
            legal_citations: Legal citations
            screenshots: Optional list of screenshots
            dom_snapshots: Optional list of DOM snapshots
            reasoning_chains: Optional list of reasoning chains
            element_selector: Optional CSS selector

        Returns:
            Evidence object
        """
        # Generate evidence ID
        evidence_id = self._generate_evidence_id(pattern_id, url)

        evidence = Evidence(
            evidence_id=evidence_id,
            pattern_id=pattern_id,
            framework_name=framework_name,
            url=url,
            confidence=confidence,
            severity=severity,
            matched_rules=matched_rules,
            legal_citations=legal_citations,
            screenshots=screenshots or [],
            dom_snapshots=dom_snapshots or [],
            reasoning_chains=reasoning_chains or [],
            element_selector=element_selector,
        )

        return evidence

    def _generate_evidence_id(self, pattern_id: str, url: str) -> str:
        """Generate unique evidence ID."""
        timestamp = datetime.now().isoformat()
        content = f"{pattern_id}_{url}_{timestamp}"
        hash_value = hashlib.md5(content.encode()).hexdigest()[:12]
        return f"evidence_{hash_value}"

    async def annotate_screenshot(
        self, screenshot: Screenshot, annotations: list[dict[str, Any]]
    ) -> Screenshot:
        """
        Add annotations to screenshot (bounding boxes, highlights).

        Args:
            screenshot: Screenshot object to annotate
            annotations: List of annotation dicts

        Returns:
            Updated screenshot object
        """
        from PIL import Image, ImageDraw, ImageFont

        # Load screenshot
        img_path = self.base_dir / screenshot.file_path
        img = Image.open(img_path)
        draw = ImageDraw.Draw(img)

        # Try to load a font, fall back to default if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            font = ImageFont.load_default()

        # Draw annotations
        for annotation in annotations:
            if annotation["type"] == "bounding_box":
                x, y, w, h = (
                    annotation["x"],
                    annotation["y"],
                    annotation["width"],
                    annotation["height"],
                )
                # Draw red rectangle
                draw.rectangle([x, y, x + w, y + h], outline="red", width=3)
                # Draw label
                if "label" in annotation:
                    draw.text((x, y - 20), annotation["label"], fill="red", font=font)

        # Save annotated version
        annotated_path = img_path.parent / f"annotated_{img_path.name}"
        img.save(annotated_path)

        # Update screenshot object
        screenshot.file_path = str(annotated_path.relative_to(self.base_dir))
        screenshot.annotations = annotations

        return screenshot

    def create_user_flow(self, flow_name: str, start_url: str) -> UserFlow:
        """
        Create a new user flow tracker.

        Args:
            flow_name: Name of the flow
            start_url: Starting URL

        Returns:
            UserFlow object
        """
        return UserFlow(flow_name=flow_name, start_url=start_url)

    def save_network_log(
        self, url: str, requests: list[dict[str, Any]], tracking_requests: list[dict[str, Any]]
    ) -> NetworkLog:
        """
        Save network activity log.

        Args:
            url: Page URL
            requests: All network requests
            tracking_requests: Identified tracking requests

        Returns:
            NetworkLog object
        """
        # Extract third-party domains
        from urllib.parse import urlparse

        page_domain = urlparse(url).netloc
        third_party_domains = set()

        for req in requests:
            req_domain = urlparse(req.get("url", "")).netloc
            if req_domain and req_domain != page_domain:
                third_party_domains.add(req_domain)

        network_log = NetworkLog(
            url=url,
            requests=requests,
            third_party_domains=list(third_party_domains),
            tracking_requests=tracking_requests,
        )

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"network_{timestamp}.json"
        file_path = self.network_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(network_log.model_dump(mode="json"), f, indent=2, default=str)

        return network_log

    def get_session_summary(self) -> dict[str, Any]:
        """Get summary of evidence collected in this session."""
        return {
            "session_id": self.session_id,
            "screenshots_captured": self.screenshot_count,
            "dom_snapshots_captured": self.dom_count,
            "reasoning_chains_saved": self.reasoning_count,
            "total_artifacts": self.screenshot_count
            + self.dom_count
            + self.reasoning_count,
        }
