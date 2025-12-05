"""
Explainable reasoning system for agent decision-making.

Provides structured reasoning chains that explain why the agent makes
specific navigation and detection decisions.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from src.evidence.models import ReasoningChain, ReasoningStep


class NavigationOption(BaseModel):
    """Represents a potential navigation action."""

    element_selector: str = Field(..., description="CSS selector for element")
    element_type: str = Field(..., description="Element type (link, button, input, etc.)")
    text: str = Field(..., description="Visible text content")
    href: Optional[str] = Field(None, description="Link target (if applicable)")
    priority_score: float = Field(..., ge=0.0, le=1.0, description="Priority score (0-1)")
    priority_rationale: str = Field(..., description="Why this priority was assigned")


class PageAnalysis(BaseModel):
    """Analysis of current page state."""

    url: str
    title: str
    timestamp: datetime = Field(default_factory=datetime.now)

    # Visual analysis
    visual_observations: list[str] = Field(
        default_factory=list, description="Visual patterns observed"
    )

    # Structural analysis
    element_count: int = Field(..., description="Total DOM elements")
    interactive_elements: int = Field(..., description="Interactive elements found")
    forms_present: bool = Field(..., description="Forms detected on page")

    # Framework triggers
    framework_triggers: dict[str, list[str]] = Field(
        default_factory=dict, description="Frameworks that triggered on this page"
    )

    # Navigation options
    navigation_options: list[NavigationOption] = Field(
        default_factory=list, description="Available navigation options"
    )


class DecisionRationale(BaseModel):
    """Rationale for a specific decision."""

    decision_type: str = Field(..., description="Type of decision (navigate, analyze, conclude)")
    chosen_action: str = Field(..., description="Action that was chosen")
    alternatives_considered: list[str] = Field(
        default_factory=list, description="Other options considered"
    )
    reasoning: str = Field(..., description="Detailed reasoning for choice")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in decision")
    supporting_evidence: list[str] = Field(
        default_factory=list, description="Evidence supporting this decision"
    )


class ReasoningEngine:
    """Engine for generating explainable reasoning chains."""

    def __init__(self):
        """Initialize reasoning engine."""
        self.active_chains: dict[str, ReasoningChain] = {}

    def create_chain(self, context: str) -> str:
        """
        Create a new reasoning chain.

        Args:
            context: Context for this chain

        Returns:
            Chain ID
        """
        chain_id = str(uuid4())[:8]
        chain = ReasoningChain(
            chain_id=chain_id, context=context, steps=[], conclusion="", confidence=0.0
        )
        self.active_chains[chain_id] = chain
        return chain_id

    def add_reasoning_step(
        self, chain_id: str, thought: str, observation: str, action: str, rationale: str
    ) -> None:
        """
        Add a reasoning step to an active chain.

        Args:
            chain_id: Chain to add to
            thought: What the agent is thinking
            observation: What the agent observes
            action: Action taken
            rationale: Why this action
        """
        if chain_id not in self.active_chains:
            raise ValueError(f"Chain {chain_id} not found")

        self.active_chains[chain_id].add_step(thought, observation, action, rationale)

    def conclude_chain(self, chain_id: str, conclusion: str, confidence: float) -> ReasoningChain:
        """
        Conclude a reasoning chain.

        Args:
            chain_id: Chain to conclude
            conclusion: Final conclusion
            confidence: Confidence in conclusion

        Returns:
            Completed ReasoningChain
        """
        if chain_id not in self.active_chains:
            raise ValueError(f"Chain {chain_id} not found")

        chain = self.active_chains[chain_id]
        chain.conclusion = conclusion
        chain.confidence = confidence

        # Remove from active chains
        del self.active_chains[chain_id]

        return chain

    def create_navigation_reasoning(
        self,
        page_analysis: PageAnalysis,
        selected_option: NavigationOption,
        pattern_hypotheses: list[str],
    ) -> ReasoningChain:
        """
        Create reasoning chain for a navigation decision.

        Args:
            page_analysis: Analysis of current page
            selected_option: Navigation option selected
            pattern_hypotheses: Patterns being investigated

        Returns:
            Complete reasoning chain
        """
        chain_id = self.create_chain(f"Navigation decision on {page_analysis.url}")

        # Step 1: Page observation
        self.add_reasoning_step(
            chain_id,
            thought="I need to understand what's on this page",
            observation=f"Page has {page_analysis.interactive_elements} interactive elements. "
            f"Visual observations: {', '.join(page_analysis.visual_observations[:3])}",
            action="Analyze page structure and content",
            rationale="Understanding page structure helps identify potential dark patterns",
        )

        # Step 2: Framework analysis
        frameworks_active = list(page_analysis.framework_triggers.keys())
        if frameworks_active:
            self.add_reasoning_step(
                chain_id,
                thought="Which frameworks are detecting patterns here?",
                observation=f"Active frameworks: {', '.join(frameworks_active)}",
                action="Apply framework-specific detection rules",
                rationale="Multiple frameworks detecting patterns suggests this page warrants investigation",
            )

        # Step 3: Navigation option evaluation
        top_options = sorted(
            page_analysis.navigation_options, key=lambda x: x.priority_score, reverse=True
        )[:3]
        self.add_reasoning_step(
            chain_id,
            thought="What are the most promising paths to explore?",
            observation=f"Top options: {', '.join([opt.text[:30] for opt in top_options])}",
            action="Score navigation options by dark pattern likelihood",
            rationale="Prioritizing paths most likely to reveal manipulative patterns",
        )

        # Step 4: Selection
        self.add_reasoning_step(
            chain_id,
            thought=f"Should I navigate to '{selected_option.text}'?",
            observation=f"Priority score: {selected_option.priority_score:.2f}. "
            f"Rationale: {selected_option.priority_rationale}",
            action=f"Navigate to {selected_option.element_type}: '{selected_option.text}'",
            rationale=f"This option has highest priority and aligns with investigating: "
            f"{', '.join(pattern_hypotheses)}",
        )

        # Conclude
        conclusion = (
            f"Navigating to '{selected_option.text}' to investigate: "
            f"{', '.join(pattern_hypotheses)}"
        )
        return self.conclude_chain(chain_id, conclusion, selected_option.priority_score)

    def create_detection_reasoning(
        self,
        pattern_name: str,
        matched_rules: dict[str, list[str]],
        confidence: float,
        evidence_summary: str,
    ) -> ReasoningChain:
        """
        Create reasoning chain for a pattern detection.

        Args:
            pattern_name: Name of detected pattern
            matched_rules: Rules that matched
            confidence: Detection confidence
            evidence_summary: Summary of evidence

        Returns:
            Complete reasoning chain
        """
        chain_id = self.create_chain(f"Detecting {pattern_name}")

        # Step 1: Initial hypothesis
        self.add_reasoning_step(
            chain_id,
            thought=f"Could this be a '{pattern_name}' dark pattern?",
            observation=f"Checking detection rules for this pattern",
            action="Evaluate visual, textual, and structural indicators",
            rationale="Systematic rule evaluation ensures accurate detection",
        )

        # Step 2: Rule matching
        total_matches = sum(len(v) for v in matched_rules.values())
        self.add_reasoning_step(
            chain_id,
            thought=f"How many detection rules match?",
            observation=f"Matched {total_matches} rules across {len(matched_rules)} categories",
            action=f"Matched rules: {', '.join([f'{k}: {len(v)}' for k, v in matched_rules.items()])}",
            rationale="Multiple rule matches increase confidence in detection",
        )

        # Step 3: Evidence collection
        self.add_reasoning_step(
            chain_id,
            thought="What evidence supports this detection?",
            observation=evidence_summary,
            action="Collect screenshots, DOM snapshots, and contextual evidence",
            rationale="Strong evidence is essential for academic rigor",
        )

        # Conclude
        conclusion = (
            f"Detected '{pattern_name}' with {confidence:.0%} confidence. "
            f"Matched {total_matches} detection rules."
        )
        return self.conclude_chain(chain_id, conclusion, confidence)

    def explain_decision(self, decision: DecisionRationale) -> str:
        """
        Generate human-readable explanation of a decision.

        Args:
            decision: Decision to explain

        Returns:
            Formatted explanation
        """
        explanation = f"Decision: {decision.chosen_action}\n\n"
        explanation += f"Reasoning: {decision.reasoning}\n\n"

        if decision.alternatives_considered:
            explanation += "Alternatives considered:\n"
            for alt in decision.alternatives_considered:
                explanation += f"  - {alt}\n"
            explanation += "\n"

        if decision.supporting_evidence:
            explanation += "Supporting evidence:\n"
            for evidence in decision.supporting_evidence:
                explanation += f"  - {evidence}\n"
            explanation += "\n"

        explanation += f"Confidence: {decision.confidence:.0%}"

        return explanation
