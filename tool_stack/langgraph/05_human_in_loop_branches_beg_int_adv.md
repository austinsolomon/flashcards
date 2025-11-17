# LangGraph Human-in-the-Loop Branches: Beginner to Advanced

## Concept Overview

Human-in-the-loop (HITL) branching enables workflows to pause at decision points, wait for human feedback, and branch execution accordingly. This pattern is essential for building AI systems that augment human judgment rather than replace it. HITL workflows combine LLM reasoning with human expertise, improving accuracy on ambiguous cases while maintaining automation for straightforward scenarios.

---

## Beginner Level: Simple User Approval Branch

A basic workflow that requires user approval before proceeding.

```python
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from typing import Literal
import json

class ApprovalBranchState(BaseModel):
    request: str
    llm_recommendation: str
    human_decision: Literal["approve", "reject", "pending"]
    final_action: str

def create_simple_approval_branch():
    """Create workflow with approval branch."""

    def analyze_request(state: ApprovalBranchState):
        """LLM analyzes request."""
        recommendation = f"LLM recommends: {state.request.lower()}"
        return {"llm_recommendation": recommendation}

    def human_review(state: ApprovalBranchState):
        """Pause for human decision."""
        # In production, this would connect to UI
        return {"human_decision": "pending"}

    def execute_approved(state: ApprovalBranchState):
        """Execute if approved."""
        return {
            "final_action": f"Executed: {state.request}",
            "human_decision": "approve"
        }

    def reject_request(state: ApprovalBranchState):
        """Reject if not approved."""
        return {
            "final_action": f"Rejected: {state.request}",
            "human_decision": "reject"
        }

    # Build workflow
    workflow = StateGraph(ApprovalBranchState)
    workflow.add_node("analyze", analyze_request)
    workflow.add_node("human_review", human_review)
    workflow.add_node("execute", execute_approved)
    workflow.add_node("reject", reject_request)

    workflow.add_edge(START, "analyze")
    workflow.add_edge("analyze", "human_review")
    workflow.add_conditional_edges(
        "human_review",
        lambda s: "execute" if s.human_decision == "approve" else "reject",
        {"execute": "execute", "reject": "reject"}
    )
    workflow.add_edge("execute", END)
    workflow.add_edge("reject", END)

    return workflow.compile()

# Usage
workflow = create_simple_approval_branch()
state = ApprovalBranchState(
    request="Process payment for customer",
    llm_recommendation="",
    human_decision="pending",
    final_action=""
)
result = workflow.invoke(state)
print(result.final_action)
```

---

## Intermediate Level: Multi-Path Human Review with Feedback Collection

A sophisticated approval workflow with multiple review paths and feedback collection.

```python
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from typing import Literal, Annotated, Optional
from datetime import datetime
from enum import Enum
import operator

class ReviewerRole(str, Enum):
    TECHNICAL = "technical"
    BUSINESS = "business"
    COMPLIANCE = "compliance"

class ReviewComment(BaseModel):
    """Feedback from a reviewer."""
    reviewer_id: str
    role: ReviewerRole
    timestamp: str
    comment: str
    approved: bool

class MultiReviewState(BaseModel):
    """State for multi-reviewer approval workflow."""
    request_id: str
    request_content: str
    required_reviews: list[ReviewerRole]
    review_comments: Annotated[list[ReviewComment], operator.add]
    pending_reviewers: list[ReviewerRole]
    final_status: Literal["pending", "approved", "rejected", "needs_revision"]
    revision_count: int = 0

def create_multi_review_workflow():
    """Create workflow with multiple reviewers."""

    def prepare_for_review(state: MultiReviewState):
        """Prepare request for review."""
        return {
            "pending_reviewers": state.required_reviews.copy(),
            "final_status": "pending"
        }

    def technical_review(state: MultiReviewState):
        """Technical reviewer checks."""
        if ReviewerRole.TECHNICAL not in state.pending_reviewers:
            return state

        # Simulate review
        comment = ReviewComment(
            reviewer_id="tech_001",
            role=ReviewerRole.TECHNICAL,
            timestamp=datetime.now().isoformat(),
            comment="Technical implementation looks sound",
            approved=True
        )

        remaining = [r for r in state.pending_reviewers if r != ReviewerRole.TECHNICAL]

        return {
            "review_comments": [comment],
            "pending_reviewers": remaining
        }

    def business_review(state: MultiReviewState):
        """Business reviewer checks."""
        if ReviewerRole.BUSINESS not in state.pending_reviewers:
            return state

        comment = ReviewComment(
            reviewer_id="biz_001",
            role=ReviewerRole.BUSINESS,
            timestamp=datetime.now().isoformat(),
            comment="Business case is justified",
            approved=True
        )

        remaining = [r for r in state.pending_reviewers if r != ReviewerRole.BUSINESS]

        return {
            "review_comments": [comment],
            "pending_reviewers": remaining
        }

    def compliance_review(state: MultiReviewState):
        """Compliance reviewer checks."""
        if ReviewerRole.COMPLIANCE not in state.pending_reviewers:
            return state

        comment = ReviewComment(
            reviewer_id="comp_001",
            role=ReviewerRole.COMPLIANCE,
            timestamp=datetime.now().isoformat(),
            comment="Compliant with regulations",
            approved=True
        )

        remaining = [r for r in state.pending_reviewers if r != ReviewerRole.COMPLIANCE]

        return {
            "review_comments": [comment],
            "pending_reviewers": remaining
        }

    def finalize_decision(state: MultiReviewState):
        """Determine final status based on all reviews."""
        # Check if any reviewer rejected
        rejected = any(not c.approved for c in state.review_comments)

        if rejected:
            status = "rejected"
        elif len(state.review_comments) == len(state.required_reviews):
            status = "approved"
        else:
            status = "pending"

        return {"final_status": status}

    # Build workflow
    workflow = StateGraph(MultiReviewState)
    workflow.add_node("prepare", prepare_for_review)
    workflow.add_node("tech_review", technical_review)
    workflow.add_node("biz_review", business_review)
    workflow.add_node("compliance_review", compliance_review)
    workflow.add_node("finalize", finalize_decision)

    workflow.add_edge(START, "prepare")
    workflow.add_edge("prepare", "tech_review")
    workflow.add_edge("tech_review", "biz_review")
    workflow.add_edge("biz_review", "compliance_review")
    workflow.add_edge("compliance_review", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile()

# Usage
workflow = create_multi_review_workflow()
state = MultiReviewState(
    request_id="req_001",
    request_content="Deploy new feature to production",
    required_reviews=[
        ReviewerRole.TECHNICAL,
        ReviewerRole.BUSINESS,
        ReviewerRole.COMPLIANCE
    ],
    review_comments=[],
    pending_reviewers=[]
)
result = workflow.invoke(state)
print(f"Final status: {result.final_status}")
```

---

## Advanced Level: Adaptive HITL with Confidence Scoring and Escalation

A sophisticated system that uses LLM confidence scores to intelligently route to human review.

```python
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field
from typing import Literal, Annotated, Optional
from datetime import datetime
from enum import Enum
import operator
import json

class ConfidenceLevel(str, Enum):
    HIGH = "high"  # > 0.85
    MEDIUM = "medium"  # 0.6-0.85
    LOW = "low"  # < 0.6

class EscalationPath(str, Enum):
    AUTO_APPROVE = "auto_approve"
    HUMAN_REVIEW = "human_review"
    EXPERT_CONSULTATION = "expert_consultation"
    REJECTION = "rejection"

class DecisionInsight(BaseModel):
    """LLM-generated decision with confidence."""
    decision: str
    confidence_score: float
    confidence_level: ConfidenceLevel
    reasoning: str
    potential_risks: list[str]
    evidence_strength: str  # "strong", "moderate", "weak"

class HumanFeedback(BaseModel):
    """Human feedback on decision."""
    reviewer_id: str
    timestamp: str
    override_decision: Optional[str] = None
    feedback_comment: str
    expertise_area: str
    trust_score: float  # How much we trust this reviewer

class AdaptiveHITLState(BaseModel):
    """State for adaptive HITL workflow."""
    request_id: str
    user_query: str
    llm_decision: Optional[DecisionInsight] = None
    escalation_path: EscalationPath = EscalationPath.HUMAN_REVIEW
    human_feedbacks: Annotated[list[HumanFeedback], operator.add]
    final_decision: str
    applied_routing_rules: list[str] = Field(default_factory=list)
    historical_accuracy: float = 0.0

class ConfidenceRouter:
    """Routes decisions to appropriate paths based on confidence."""
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4")
        self.high_confidence_threshold = 0.85
        self.medium_confidence_threshold = 0.60
        self.expert_review_threshold = 0.70

    async def generate_decision_with_confidence(
        self,
        query: str
    ) -> DecisionInsight:
        """Generate decision and estimate confidence."""
        # Simulate LLM decision
        confidence_score = 0.82
        confidence_level = ConfidenceLevel.MEDIUM if confidence_score < 0.85 else ConfidenceLevel.HIGH

        return DecisionInsight(
            decision="Proceed with action",
            confidence_score=confidence_score,
            confidence_level=confidence_level,
            reasoning="Based on historical patterns and current context",
            potential_risks=["User might be dissatisfied", "Edge case not covered"],
            evidence_strength="moderate"
        )

    def select_escalation_path(
        self,
        insight: DecisionInsight,
        historical_accuracy: float
    ) -> tuple[EscalationPath, list[str]]:
        """Intelligently select escalation path."""
        rules_applied = []

        # Rule 1: High confidence with strong evidence
        if (insight.confidence_level == ConfidenceLevel.HIGH and
            insight.evidence_strength == "strong" and
            historical_accuracy > 0.9):
            rules_applied.append("High confidence + strong evidence + proven accuracy")
            return EscalationPath.AUTO_APPROVE, rules_applied

        # Rule 2: High confidence but weak evidence
        if (insight.confidence_level == ConfidenceLevel.HIGH and
            insight.evidence_strength == "weak"):
            rules_applied.append("High confidence but weak evidence - needs review")
            return EscalationPath.HUMAN_REVIEW, rules_applied

        # Rule 3: Medium confidence
        if insight.confidence_level == ConfidenceLevel.MEDIUM:
            # Check potential risks
            if len(insight.potential_risks) > 2:
                rules_applied.append("Medium confidence with multiple risks - expert")
                return EscalationPath.EXPERT_CONSULTATION, rules_applied
            rules_applied.append("Medium confidence - standard review")
            return EscalationPath.HUMAN_REVIEW, rules_applied

        # Rule 4: Low confidence
        rules_applied.append("Low confidence - expert required or reject")
        if historical_accuracy < 0.7:
            return EscalationPath.REJECTION, rules_applied
        return EscalationPath.EXPERT_CONSULTATION, rules_applied

def create_adaptive_hitl_system():
    """Create adaptive HITL workflow."""
    router = ConfidenceRouter()

    async def analyze_with_confidence(state: AdaptiveHITLState):
        """Generate decision with confidence scoring."""
        decision = await router.generate_decision_with_confidence(state.user_query)
        return {"llm_decision": decision}

    async def route_by_confidence(state: AdaptiveHITLState):
        """Route based on confidence and context."""
        path, rules = router.select_escalation_path(
            state.llm_decision,
            state.historical_accuracy
        )
        return {
            "escalation_path": path,
            "applied_routing_rules": rules
        }

    async def auto_approve_path(state: AdaptiveHITLState):
        """Auto-approve high-confidence decisions."""
        return {
            "final_decision": state.llm_decision.decision,
            "human_feedbacks": []
        }

    async def human_review_path(state: AdaptiveHITLState):
        """Route to human for standard review."""
        # Simulate human feedback
        feedback = HumanFeedback(
            reviewer_id="human_001",
            timestamp=datetime.now().isoformat(),
            override_decision=None,
            feedback_comment="Decision looks good, approving",
            expertise_area="general",
            trust_score=0.85
        )
        return {
            "human_feedbacks": [feedback],
            "final_decision": state.llm_decision.decision
        }

    async def expert_consultation_path(state: AdaptiveHITLState):
        """Route to domain expert."""
        feedback = HumanFeedback(
            reviewer_id="expert_001",
            timestamp=datetime.now().isoformat(),
            override_decision="Modified decision based on expertise",
            feedback_comment="Consider risk factors in domain X",
            expertise_area="specialized",
            trust_score=0.95
        )
        return {
            "human_feedbacks": [feedback],
            "final_decision": feedback.override_decision or state.llm_decision.decision
        }

    async def rejection_path(state: AdaptiveHITLState):
        """Reject low-confidence decisions."""
        return {
            "final_decision": "REJECTED - Insufficient confidence",
            "human_feedbacks": []
        }

    # Build workflow
    workflow = StateGraph(AdaptiveHITLState)
    workflow.add_node("analyze", analyze_with_confidence)
    workflow.add_node("route", route_by_confidence)
    workflow.add_node("auto_approve", auto_approve_path)
    workflow.add_node("human_review", human_review_path)
    workflow.add_node("expert_consultation", expert_consultation_path)
    workflow.add_node("rejection", rejection_path)

    workflow.add_edge(START, "analyze")
    workflow.add_edge("analyze", "route")

    workflow.add_conditional_edges(
        "route",
        lambda s: s.escalation_path.value,
        {
            "auto_approve": "auto_approve",
            "human_review": "human_review",
            "expert_consultation": "expert_consultation",
            "rejection": "rejection"
        }
    )

    workflow.add_edge("auto_approve", END)
    workflow.add_edge("human_review", END)
    workflow.add_edge("expert_consultation", END)
    workflow.add_edge("rejection", END)

    return workflow.compile()

# Usage
async def main():
    system = create_adaptive_hitl_system()
    initial_state = AdaptiveHITLState(
        request_id="req_001",
        user_query="Should we approve this customer request?",
        historical_accuracy=0.92
    )
    # result = await asyncio.to_thread(system.invoke, initial_state)
```

---

## Best Practices for Human-in-the-Loop Mastery

1. **Intelligent Escalation Routing**: Use LLM confidence scores, evidence quality, and historical accuracy to route decisions. High-confidence decisions with strong evidence bypass review. Low-confidence or novel cases go to experts. This maximizes efficiency while maintaining accuracy.

2. **Confidence Scoring Integration**: Generate confidence scores alongside decisions. Use evidence strength assessment and risk identification to quantify decision quality. Track how well confidence scores predict approval rates and human agreement.

3. **Reviewer Expertise Matching**: Route to reviewers with domain expertise and track their decision quality. Assign higher trust scores to reviewers with proven accuracy in relevant domains. Use expertise metadata to optimize reviewer selection.

4. **Feedback Loop Learning**: Log all human overrides and feedback. Track which LLM decisions humans regularly override. Use this data to retrain prompts, adjust confidence thresholds, or escalate similar cases proactively.

5. **Asynchronous State Management**: Implement checkpoints between LLM analysis and human review. Use queuing systems to manage multiple pending reviews. Track approval SLAs and escalate delayed decisions to supervisors.
