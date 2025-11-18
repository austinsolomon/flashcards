# LangGraph Human-in-the-Loop Branches

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

## Best Practices for Human-in-the-Loop Mastery

1. **Intelligent Escalation Routing**: Use LLM confidence scores, evidence quality, and historical accuracy to route decisions. High-confidence decisions with strong evidence bypass review. Low-confidence or novel cases go to experts. This maximizes efficiency while maintaining accuracy.

2. **Confidence Scoring Integration**: Generate confidence scores alongside decisions. Use evidence strength assessment and risk identification to quantify decision quality. Track how well confidence scores predict approval rates and human agreement.

3. **Reviewer Expertise Matching**: Route to reviewers with domain expertise and track their decision quality. Assign higher trust scores to reviewers with proven accuracy in relevant domains. Use expertise metadata to optimize reviewer selection.

4. **Feedback Loop Learning**: Log all human overrides and feedback. Track which LLM decisions humans regularly override. Use this data to retrain prompts, adjust confidence thresholds, or escalate similar cases proactively.

5. **Asynchronous State Management**: Implement checkpoints between LLM analysis and human review. Use queuing systems to manage multiple pending reviews. Track approval SLAs and escalate delayed decisions to supervisors.
