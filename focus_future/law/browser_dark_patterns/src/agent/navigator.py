"""
Browser navigation agent using Claude vision for page analysis.

Handles web navigation, element discovery, and Claude-powered visual analysis.
"""

import base64
import os
from typing import Any, Optional

from anthropic import Anthropic
from playwright.async_api import Page

from src.agent.reasoning import NavigationOption, PageAnalysis
from src.utils.browser import BrowserManager


class Navigator:
    """Agent for web navigation with Claude vision analysis."""

    def __init__(self, browser: BrowserManager, anthropic_client: Optional[Anthropic] = None):
        """
        Initialize navigator.

        Args:
            browser: Browser manager instance
            anthropic_client: Anthropic client (creates one if not provided)
        """
        self.browser = browser
        self.client = anthropic_client or Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")

    async def analyze_page_with_vision(self, url: str) -> PageAnalysis:
        """
        Analyze current page using Claude vision.

        Args:
            url: Current page URL

        Returns:
            PageAnalysis with visual observations and navigation options
        """
        if not self.browser.page:
            raise RuntimeError("Browser not initialized")

        # Capture screenshot for Claude vision
        screenshot_bytes = await self.browser.page.screenshot(type="png")
        screenshot_b64 = base64.standard_b64encode(screenshot_bytes).decode("utf-8")

        # Get page metadata
        title = await self.browser.get_page_title()
        element_count = await self.browser.evaluate("document.querySelectorAll('*').length")

        # Get interactive elements
        interactive_elements = await self.browser.evaluate("""
            () => {
                const selectors = 'a, button, input, select, textarea';
                return document.querySelectorAll(selectors).length;
            }
        """)

        # Check for forms
        forms_present = await self.browser.evaluate("document.querySelectorAll('form').length > 0")

        # Analyze with Claude vision
        prompt = """Analyze this webpage screenshot for potential dark patterns. Describe:
1. Visual hierarchy and design choices
2. Any manipulative elements (urgency indicators, social proof, confirmshaming, etc.)
3. Prominent call-to-action buttons and their styling
4. Any suspicious patterns you observe

Keep response concise (3-5 bullet points)."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": screenshot_b64,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )

        visual_observations = [
            block.text for block in response.content if hasattr(block, "text")
        ]

        # Extract navigation options
        nav_options = await self._extract_navigation_options()

        return PageAnalysis(
            url=url,
            title=title,
            visual_observations=visual_observations,
            element_count=element_count,
            interactive_elements=interactive_elements,
            forms_present=forms_present,
            navigation_options=nav_options,
        )

    async def _extract_navigation_options(self) -> list[NavigationOption]:
        """Extract and score navigation options from page."""
        if not self.browser.page:
            return []

        # Get all interactive elements
        elements = await self.browser.evaluate("""
            () => {
                const selectors = 'a, button, [role="button"]';
                const elements = Array.from(document.querySelectorAll(selectors));

                return elements.map((el, idx) => {
                    const rect = el.getBoundingClientRect();
                    return {
                        selector: `${el.tagName.toLowerCase()}:nth-of-type(${idx + 1})`,
                        type: el.tagName.toLowerCase(),
                        text: el.textContent?.trim() || '',
                        href: el.href || null,
                        visible: rect.width > 0 && rect.height > 0,
                        position: { x: rect.left, y: rect.top }
                    };
                }).filter(el => el.visible && el.text.length > 0);
            }
        """)

        # Score options based on dark pattern investigation potential
        options = []
        for el in elements[:20]:  # Limit to top 20
            priority_score, rationale = self._score_navigation_option(el)
            options.append(
                NavigationOption(
                    element_selector=el["selector"],
                    element_type=el["type"],
                    text=el["text"][:100],
                    href=el.get("href"),
                    priority_score=priority_score,
                    priority_rationale=rationale,
                )
            )

        return sorted(options, key=lambda x: x.priority_score, reverse=True)

    def _score_navigation_option(self, element: dict[str, Any]) -> tuple[float, str]:
        """
        Score navigation option for dark pattern investigation potential.

        Returns:
            (score, rationale) tuple
        """
        text = element["text"].lower()
        score = 0.5  # Base score
        rationales = []

        # High-value keywords
        if any(
            kw in text
            for kw in ["sign up", "subscribe", "cancel", "delete", "settings", "privacy"]
        ):
            score += 0.3
            rationales.append("Critical user flow element")

        if any(kw in text for kw in ["limited time", "expires", "only", "now", "hurry"]):
            score += 0.2
            rationales.append("Urgency language detected")

        if any(kw in text for kw in ["free", "trial", "offer", "discount"]):
            score += 0.15
            rationales.append("Promotional language")

        # Button vs link preference (buttons often more important)
        if element["type"] == "button":
            score += 0.1
            rationales.append("Interactive button element")

        return (min(score, 1.0), "; ".join(rationales) if rationales else "Standard navigation element")

    async def navigate_to_option(self, option: NavigationOption) -> bool:
        """
        Navigate to a specific option.

        Args:
            option: Navigation option to follow

        Returns:
            True if navigation successful
        """
        if not self.browser.page:
            return False

        try:
            if option.href:
                await self.browser.navigate(option.href)
            else:
                await self.browser.click(option.element_selector)
            await self.browser.wait_for_network_idle()
            return True
        except Exception as e:
            print(f"Navigation failed: {e}")
            return False
