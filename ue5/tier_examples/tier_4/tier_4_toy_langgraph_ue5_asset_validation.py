#!/usr/bin/env python3
"""
UE5 - Tier 4 - Multi-Agent Asset Validation (LangGraph)

TIER 4: ConceptAgent → TechAgent coordination
- ConceptAgent: Reviews artistic/design quality
- TechAgent: Validates technical specifications
- Coordinated approval workflow
"""

import os
import sys
from typing import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END

load_dotenv()


class AssetValidationState(TypedDict):
    """Shared state between agents"""
    asset_name: str
    asset_type: str  # "texture", "model", "material"
    asset_path: str

    # ConceptAgent outputs
    concept_review_complete: bool
    artistic_score: int  # 0-10
    concept_notes: str
    concept_approved: bool

    # TechAgent outputs
    tech_review_complete: bool
    tech_score: int
    tech_notes: str
    tech_approved: bool

    # Final decision
    final_approval: bool
    current_agent: str


def concept_agent(state: AssetValidationState) -> AssetValidationState:
    """
    ConceptAgent: Reviews artistic and design quality

    TIER 4: Specialized agent for concept review
    """
    print(f"\n🎨 CONCEPT AGENT: Reviewing artistic quality")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    review_prompt = f"""
    Review the artistic quality of this UE5 asset:

    Asset: {state['asset_name']}
    Type: {state['asset_type']}

    Evaluate:
    1. Visual appeal and aesthetic quality (0-10)
    2. Consistency with game art style
    3. Level of detail appropriate for type
    4. Any artistic issues or improvements needed

    Provide: score (0-10) and brief notes
    """

    response = llm.invoke([
        SystemMessage(content="You are a game art director reviewing asset quality."),
        HumanMessage(content=review_prompt)
    ]).content

    # Parse response (simplified for toy example)
    artistic_score = 8  # Simulated
    concept_notes = response
    concept_approved = artistic_score >= 7

    print(f"✅ Concept review: {artistic_score}/10 - {'APPROVED' if concept_approved else 'NEEDS REVISION'}\n")

    state["concept_review_complete"] = True
    state["artistic_score"] = artistic_score
    state["concept_notes"] = concept_notes
    state["concept_approved"] = concept_approved
    state["current_agent"] = "tech"

    return state


def tech_agent(state: AssetValidationState) -> AssetValidationState:
    """
    TechAgent: Validates technical specifications

    TIER 4: Specialized agent for technical validation
    """
    print(f"\n⚙️  TECH AGENT: Validating technical specs")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    validation_prompt = f"""
    Validate technical specifications for this UE5 asset:

    Asset: {state['asset_name']}
    Type: {state['asset_type']}
    Concept Score: {state['artistic_score']}/10

    Check:
    1. File size appropriate for asset type
    2. Polygon count within budget
    3. Texture resolution standards met
    4. Naming conventions followed
    5. UE5 import readiness

    Provide: technical score (0-10) and notes
    """

    response = llm.invoke([
        SystemMessage(content="You are a technical artist validating UE5 asset specs."),
        HumanMessage(content=validation_prompt)
    ]).content

    # Parse response
    tech_score = 9  # Simulated
    tech_notes = response
    tech_approved = tech_score >= 7

    print(f"✅ Tech validation: {tech_score}/10 - {'APPROVED' if tech_approved else 'NEEDS REVISION'}\n")

    # Final approval requires both agents
    final_approval = state["concept_approved"] and tech_approved

    state["tech_review_complete"] = True
    state["tech_score"] = tech_score
    state["tech_notes"] = tech_notes
    state["tech_approved"] = tech_approved
    state["final_approval"] = final_approval
    state["current_agent"] = "complete"

    return state


def create_asset_validation_workflow():
    """Create LangGraph workflow for asset validation"""
    workflow = StateGraph(AssetValidationState)

    workflow.add_node("concept", concept_agent)
    workflow.add_node("tech", tech_agent)

    workflow.set_entry_point("concept")
    workflow.add_edge("concept", "tech")
    workflow.add_edge("tech", END)

    return workflow.compile()


def validate_asset(asset_name: str, asset_type: str, asset_path: str):
    """Validate UE5 asset using multi-agent workflow"""
    print(f"\n{'='*60}")
    print(f"🎯 TIER 4 MULTI-AGENT: Asset Validation")
    print(f"Asset: {asset_name}")
    print(f"{'='*60}\n")

    app = create_asset_validation_workflow()

    initial_state = {
        "asset_name": asset_name,
        "asset_type": asset_type,
        "asset_path": asset_path,
        "concept_review_complete": False,
        "artistic_score": 0,
        "concept_notes": "",
        "concept_approved": False,
        "tech_review_complete": False,
        "tech_score": 0,
        "tech_notes": "",
        "tech_approved": False,
        "final_approval": False,
        "current_agent": "concept"
    }

    final_state = app.invoke(initial_state)

    print(f"\n{'='*60}")
    print(f"✅ VALIDATION COMPLETE")
    print(f"{'='*60}")
    print(f"Concept: {final_state['artistic_score']}/10")
    print(f"Tech: {final_state['tech_score']}/10")
    print(f"Final: {'✅ APPROVED' if final_state['final_approval'] else '❌ NEEDS REVISION'}\n")

    return final_state


def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found")
        sys.exit(1)

    validate_asset(
        "hero_character_armor.fbx",
        "model",
        "/assets/characters/hero_armor.fbx"
    )

    print("\n🎓 WHY THIS IS TIER 4:")
    print("""
    - ConceptAgent → TechAgent coordination
    - Specialized review responsibilities
    - State sharing between agents
    - Sequential approval workflow
    """)


if __name__ == "__main__":
    main()
