# LangGraph Human-in-the-Loop Branches

## Concept Overview

Human-in-the-loop (HITL) branching enables workflows to pause at decision points, wait for human feedback, and branch execution accordingly. This pattern is essential for building AI systems that augment human judgment rather than replace it. HITL workflows combine LLM reasoning with human expertise, improving accuracy on ambiguous cases while maintaining automation for straightforward scenarios.

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

## Best Practices for Human-in-the-Loop Mastery

1. **Intelligent Escalation Routing**: Use LLM confidence scores, evidence quality, and historical accuracy to route decisions. High-confidence decisions with strong evidence bypass review. Low-confidence or novel cases go to experts. This maximizes efficiency while maintaining accuracy.

2. **Confidence Scoring Integration**: Generate confidence scores alongside decisions. Use evidence strength assessment and risk identification to quantify decision quality. Track how well confidence scores predict approval rates and human agreement.

3. **Reviewer Expertise Matching**: Route to reviewers with domain expertise and track their decision quality. Assign higher trust scores to reviewers with proven accuracy in relevant domains. Use expertise metadata to optimize reviewer selection.

4. **Feedback Loop Learning**: Log all human overrides and feedback. Track which LLM decisions humans regularly override. Use this data to retrain prompts, adjust confidence thresholds, or escalate similar cases proactively.

5. **Asynchronous State Management**: Implement checkpoints between LLM analysis and human review. Use queuing systems to manage multiple pending reviews. Track approval SLAs and escalate delayed decisions to supervisors.
