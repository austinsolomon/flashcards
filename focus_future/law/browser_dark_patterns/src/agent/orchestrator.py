"""
LangGraph-based orchestrator for dark pattern exploration workflow.

Coordinates navigation, analysis, and evidence collection in a structured workflow.
"""

import os
from datetime import datetime
from typing import Optional
from uuid import uuid4

from anthropic import Anthropic

from src.agent.analyzer import MultiFrameworkAnalyzer
from src.agent.navigator import Navigator
from src.agent.reasoning import ReasoningEngine
from src.evidence.collector import EvidenceCollector
from src.evidence.models import ExplorationSession, Finding
from src.frameworks.base import DarkPatternFramework
from src.utils.browser import BrowserManager, create_browser
from src.utils.storage import SessionStorage


class DarkPatternOrchestrator:
    """Orchestrates dark pattern detection workflow."""

    def __init__(
        self,
        frameworks: list[DarkPatternFramework],
        max_depth: int = 5,
        storage: Optional[SessionStorage] = None,
    ):
        """
        Initialize orchestrator.

        Args:
            frameworks: Frameworks to apply
            max_depth: Maximum exploration depth
            storage: Optional session storage
        """
        self.frameworks = frameworks
        self.max_depth = max_depth
        self.storage = storage

        # Components (initialized during exploration)
        self.browser: Optional[BrowserManager] = None
        self.navigator: Optional[Navigator] = None
        self.analyzer: Optional[MultiFrameworkAnalyzer] = None
        self.reasoning_engine = ReasoningEngine()

    async def explore(
        self, url: str, session_name: Optional[str] = None
    ) -> ExplorationSession:
        """
        Explore a website for dark patterns.

        Args:
            url: Target URL
            session_name: Optional session name

        Returns:
            Completed exploration session
        """
        # Create session
        session_id = str(uuid4())[:12]
        session = ExplorationSession(
            session_id=session_id,
            session_name=session_name or f"Exploration of {url}",
            target_url=url,
            frameworks_used=[f.name for f in self.frameworks],
            max_depth=self.max_depth,
        )

        print(f"\n🔍 Starting exploration: {session.session_name}")
        print(f"📋 Frameworks: {', '.join(session.frameworks_used)}")
        print(f"🎯 Target: {url}\n")

        # Initialize components
        self.browser = await create_browser()
        evidence_collector = EvidenceCollector(session_id)

        anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.navigator = Navigator(self.browser, anthropic_client)
        self.analyzer = MultiFrameworkAnalyzer(
            self.frameworks, self.browser, evidence_collector, self.reasoning_engine
        )

        try:
            # Start exploration
            await self._explore_recursive(url, session, depth=0, visited=set())

        finally:
            # Cleanup
            if self.browser:
                await self.browser.stop()

        # Mark session complete
        session.mark_complete()

        # Save session if storage available
        if self.storage:
            await self.storage.save_session(session)

        print(f"\n✅ Exploration complete!")
        print(f"📊 Pages visited: {len(session.pages_visited)}")
        print(f"🔴 Patterns detected: {session.total_patterns_detected}")
        print(f"⏱️  Duration: {session.duration_seconds:.1f}s\n")

        return session

    async def _explore_recursive(
        self, url: str, session: ExplorationSession, depth: int, visited: set[str]
    ) -> None:
        """
        Recursively explore pages.

        Args:
            url: Current URL
            session: Exploration session
            depth: Current depth
            visited: Set of visited URLs
        """
        # Check depth limit
        if depth >= self.max_depth:
            print(f"⚠️  Max depth {self.max_depth} reached")
            return

        # Check if already visited
        if url in visited:
            return

        visited.add(url)
        session.pages_visited.append(url)

        print(f"\n{'  ' * depth}📄 [{depth + 1}/{self.max_depth}] {url}")

        try:
            # Navigate to page
            await self.browser.navigate(url)

            # Analyze page with Claude vision
            print(f"{'  ' * depth}   🤖 Analyzing with Claude vision...")
            page_analysis = await self.navigator.analyze_page_with_vision(url)

            # Check for dark patterns
            print(f"{'  ' * depth}   🔍 Checking {len(self.frameworks)} frameworks...")
            findings = await self.analyzer.analyze_page(url, page_analysis)

            # Add findings to session
            for finding in findings:
                session.add_finding(finding)
                print(
                    f"{'  ' * depth}   🔴 Detected: {finding.pattern_name} "
                    f"({finding.framework_name}, {finding.confidence:.0%})"
                )

            # Select next navigation option (if not at max depth)
            if depth < self.max_depth - 1 and page_analysis.navigation_options:
                # Get highest priority unvisited option
                for option in page_analysis.navigation_options:
                    if option.href and option.href not in visited:
                        print(
                            f"{'  ' * depth}   ➡️  Navigating to: {option.text[:40]}"
                        )

                        # Create reasoning chain
                        pattern_hypotheses = [
                            f.pattern_name for f in findings
                        ] or ["General exploration"]
                        reasoning = self.reasoning_engine.create_navigation_reasoning(
                            page_analysis, option, pattern_hypotheses
                        )

                        # Navigate
                        if await self.navigator.navigate_to_option(option):
                            new_url = await self.browser.get_current_url()
                            # Recurse
                            await self._explore_recursive(
                                new_url, session, depth + 1, visited
                            )
                        break

        except Exception as e:
            print(f"{'  ' * depth}   ❌ Error exploring {url}: {e}")


# Example usage function
async def run_exploration_example() -> None:
    """Example of running an exploration."""
    from src.frameworks.ieee_7010 import IEEE7010Framework
    from src.frameworks.dsa_article_28 import DSAArticle28Framework

    # Initialize frameworks
    frameworks = [IEEE7010Framework, DSAArticle28Framework]

    # Create orchestrator
    orchestrator = DarkPatternOrchestrator(frameworks=frameworks, max_depth=3)

    # Run exploration
    session = await orchestrator.explore(
        url="https://www.instagram.com",
        session_name="Instagram Dark Pattern Analysis",
    )

    # Print summary
    print("\n" + "=" * 60)
    print("EXPLORATION SUMMARY")
    print("=" * 60)
    print(f"Session: {session.session_name}")
    print(f"Patterns detected: {session.total_patterns_detected}")
    print(f"\nFindings by severity:")
    for severity, findings in session.findings_by_severity.items():
        if findings:
            print(f"  {severity.value.upper()}: {len(findings)}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_exploration_example())
