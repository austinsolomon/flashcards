"""
Browser automation utilities using Browser Use and Playwright.

Provides high-level interface for browser automation with Claude vision integration.
"""

import asyncio
import os
from typing import Any, Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright


class BrowserManager:
    """Manages browser instances and contexts for exploration."""

    def __init__(
        self,
        headless: bool = False,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        timeout: int = 30000,
    ):
        """
        Initialize browser manager.

        Args:
            headless: Run browser in headless mode
            viewport_width: Viewport width in pixels
            viewport_height: Viewport height in pixels
            timeout: Default timeout in milliseconds
        """
        self.headless = headless
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.timeout = timeout

        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def start(self) -> None:
        """Start browser and create context."""
        self.playwright = await async_playwright().start()

        # Launch browser (using Chromium for best compatibility)
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )

        # Create context with viewport
        self.context = await self.browser.new_context(
            viewport={"width": self.viewport_width, "height": self.viewport_height},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
        )

        # Set default timeout
        self.context.set_default_timeout(self.timeout)

        # Create page
        self.page = await self.context.new_page()

    async def stop(self) -> None:
        """Stop browser and clean up."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def navigate(self, url: str, wait_until: str = "networkidle") -> None:
        """
        Navigate to URL.

        Args:
            url: URL to navigate to
            wait_until: When to consider navigation complete
                       (load, domcontentloaded, networkidle)
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        await self.page.goto(url, wait_until=wait_until)

    async def click(self, selector: str, timeout: Optional[int] = None) -> None:
        """
        Click element by selector.

        Args:
            selector: CSS selector
            timeout: Optional timeout override
        """
        if not self.page:
            raise RuntimeError("Browser not started.")

        await self.page.click(selector, timeout=timeout or self.timeout)

    async def fill(self, selector: str, value: str, timeout: Optional[int] = None) -> None:
        """
        Fill form field.

        Args:
            selector: CSS selector
            value: Value to fill
            timeout: Optional timeout override
        """
        if not self.page:
            raise RuntimeError("Browser not started.")

        await self.page.fill(selector, value, timeout=timeout or self.timeout)

    async def wait_for_selector(
        self, selector: str, state: str = "visible", timeout: Optional[int] = None
    ) -> None:
        """
        Wait for selector to reach state.

        Args:
            selector: CSS selector
            state: State to wait for (attached, detached, visible, hidden)
            timeout: Optional timeout override
        """
        if not self.page:
            raise RuntimeError("Browser not started.")

        await self.page.wait_for_selector(
            selector, state=state, timeout=timeout or self.timeout
        )

    async def get_page_content(self) -> str:
        """Get full HTML content of current page."""
        if not self.page:
            raise RuntimeError("Browser not started.")

        return await self.page.content()

    async def get_current_url(self) -> str:
        """Get current page URL."""
        if not self.page:
            raise RuntimeError("Browser not started.")

        return self.page.url

    async def get_page_title(self) -> str:
        """Get current page title."""
        if not self.page:
            raise RuntimeError("Browser not started.")

        return await self.page.title()

    async def evaluate(self, script: str) -> Any:
        """
        Execute JavaScript in page context.

        Args:
            script: JavaScript code to execute

        Returns:
            Result of script execution
        """
        if not self.page:
            raise RuntimeError("Browser not started.")

        return await self.page.evaluate(script)

    async def scroll_to_bottom(self, smooth: bool = True) -> None:
        """
        Scroll to bottom of page.

        Args:
            smooth: Use smooth scrolling
        """
        if not self.page:
            raise RuntimeError("Browser not started.")

        await self.page.evaluate(
            f"""
            window.scrollTo({{
                top: document.body.scrollHeight,
                behavior: '{'smooth' if smooth else 'auto'}'
            }})
        """
        )

    async def scroll_by(self, pixels: int, smooth: bool = True) -> None:
        """
        Scroll by specified pixels.

        Args:
            pixels: Number of pixels to scroll (positive = down, negative = up)
            smooth: Use smooth scrolling
        """
        if not self.page:
            raise RuntimeError("Browser not started.")

        await self.page.evaluate(
            f"""
            window.scrollBy({{
                top: {pixels},
                behavior: '{'smooth' if smooth else 'auto'}'
            }})
        """
        )

    async def get_element_info(self, selector: str) -> Optional[dict[str, Any]]:
        """
        Get information about an element.

        Args:
            selector: CSS selector

        Returns:
            Dict with element information or None if not found
        """
        if not self.page:
            raise RuntimeError("Browser not started.")

        return await self.page.evaluate(
            f"""
            () => {{
                const el = document.querySelector('{selector}');
                if (!el) return null;

                const rect = el.getBoundingClientRect();
                const styles = window.getComputedStyle(el);

                return {{
                    tag: el.tagName.toLowerCase(),
                    text: el.textContent?.trim() || '',
                    href: el.href || null,
                    id: el.id || null,
                    classes: Array.from(el.classList),
                    visible: rect.width > 0 && rect.height > 0,
                    position: {{
                        x: rect.left,
                        y: rect.top,
                        width: rect.width,
                        height: rect.height
                    }},
                    styles: {{
                        color: styles.color,
                        backgroundColor: styles.backgroundColor,
                        fontSize: styles.fontSize,
                        fontWeight: styles.fontWeight
                    }}
                }};
            }}
        """
        )

    async def find_elements_by_text(
        self, text: str, tag: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        Find elements containing specific text.

        Args:
            text: Text to search for
            tag: Optional tag filter (e.g., 'button', 'a')

        Returns:
            List of matching elements with metadata
        """
        if not self.page:
            raise RuntimeError("Browser not started.")

        tag_filter = tag if tag else "*"

        return await self.page.evaluate(
            f"""
            () => {{
                const text = '{text}';
                const elements = Array.from(document.querySelectorAll('{tag_filter}'));
                const matches = elements.filter(el =>
                    el.textContent?.toLowerCase().includes(text.toLowerCase())
                );

                return matches.map(el => {{
                    const rect = el.getBoundingClientRect();
                    return {{
                        tag: el.tagName.toLowerCase(),
                        text: el.textContent?.trim().substring(0, 100) || '',
                        href: el.href || null,
                        id: el.id || null,
                        classes: Array.from(el.classList),
                        visible: rect.width > 0 && rect.height > 0,
                        position: {{
                            x: rect.left,
                            y: rect.top,
                            width: rect.width,
                            height: rect.height
                        }}
                    }};
                }});
            }}
        """
        )

    async def wait_for_network_idle(self, timeout: Optional[int] = None) -> None:
        """Wait for network to be idle."""
        if not self.page:
            raise RuntimeError("Browser not started.")

        await self.page.wait_for_load_state("networkidle", timeout=timeout or self.timeout)

    async def __aenter__(self):
        """Context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.stop()


# Helper function for common use case
async def create_browser(
    headless: Optional[bool] = None,
    viewport_width: int = 1920,
    viewport_height: int = 1080,
) -> BrowserManager:
    """
    Create and start a browser instance.

    Args:
        headless: Run in headless mode (defaults to env var BROWSER_HEADLESS)
        viewport_width: Viewport width
        viewport_height: Viewport height

    Returns:
        Started BrowserManager instance
    """
    if headless is None:
        headless = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"

    browser = BrowserManager(
        headless=headless, viewport_width=viewport_width, viewport_height=viewport_height
    )
    await browser.start()
    return browser
