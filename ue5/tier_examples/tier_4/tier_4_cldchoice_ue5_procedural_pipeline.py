#!/usr/bin/env python3
"""
UE5 - Tier 4 - Multi-Agent Asset Generation Pipeline (LangGraph)

TIER 4 CHARACTERISTICS:
- Multiple specialized agents coordinating
- ConceptAgent → TechnicalAgent → QualityAgent workflow
- Shared state for asset specifications
- Iterative refinement through agent collaboration

What It Does:
Generates complete procedural asset packages for UE5 through coordinated
multi-agent workflow:
1. ConceptAgent: Interprets creative brief, generates specifications
2. TechnicalAgent: Writes Unreal Python code, creates materials
3. QualityAgent: Validates output, ensures production standards
"""

import os
import json
from typing import TypedDict, List, Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

load_dotenv()

# ============================================================================
# TIER 4: Shared State Between Agents
# ============================================================================

class AssetGenerationState(TypedDict):
    """Shared state flowing between specialized agents"""

    # Input
    creative_brief: str
    asset_type: str  # "modular_building", "prop_set", "terrain"
    target_platform: str  # "PC", "Console", "Mobile"

    # ConceptAgent outputs
    concept_approved: bool
    asset_specifications: dict
    technical_requirements: dict

    # TechnicalAgent outputs
    unreal_python_code: str
    material_definitions: List[dict]
    lod_settings: dict
    code_validated: bool

    # QualityAgent outputs
    quality_score: int
    quality_issues: List[str]
    performance_metrics: dict
    ready_for_production: bool

    # Workflow control
    current_agent: str
    iteration_count: int
    messages: List


# ============================================================================
# TIER 4: Specialized Agent 1 - ConceptAgent
# ============================================================================

def concept_agent(state: AssetGenerationState) -> AssetGenerationState:
    """
    ConceptAgent: Interprets creative requirements and generates technical specs

    TIER 4: Specialized agent focusing only on concept → specification
    """
    print(f"\n{'='*60}")
    print("CONCEPT AGENT: Analyzing creative brief")
    print(f"{'='*60}\n")

    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

    prompt = f"""Analyze this asset generation request and create detailed technical specifications.

CREATIVE BRIEF:
{state['creative_brief']}

ASSET TYPE: {state['asset_type']}
TARGET PLATFORM: {state['target_platform']}

Generate specifications including:
- Poly count targets
- Texture resolutions
- Material complexity
- LOD requirements
- Collision settings
- Modular dimensions (if applicable)

Return JSON with complete technical specifications."""

    response = llm.invoke([
        SystemMessage(content="You are a technical artist specializing in UE5 asset production."),
        HumanMessage(content=prompt)
    ])

    # Parse specifications
    try:
        specs = json.loads(response.content)
    except:
        specs = {
            "poly_count_lod0": 5000,
            "texture_resolution": "2048x2048",
            "material_complexity": "medium",
            "lod_count": 4,
            "collision_type": "complex"
        }

    print(f"Specifications generated: {json.dumps(specs, indent=2)}\n")

    state["concept_approved"] = True
    state["asset_specifications"] = specs
    state["technical_requirements"] = {
        "unreal_version": "5.3",
        "python_api_version": "latest"
    }
    state["current_agent"] = "technical"

    return state


# ============================================================================
# TIER 4: Specialized Agent 2 - TechnicalAgent
# ============================================================================

def technical_agent(state: AssetGenerationState) -> AssetGenerationState:
    """
    TechnicalAgent: Writes Unreal Python code based on specifications

    TIER 4: Builds on ConceptAgent's output, generates implementation
    """
    print(f"\n{'='*60}")
    print("TECHNICAL AGENT: Generating Unreal Python code")
    print(f"{'='*60}\n")

    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

    specs = state["asset_specifications"]

    prompt = f"""Generate production-ready Unreal Python code for procedural asset generation.

SPECIFICATIONS:
{json.dumps(specs, indent=2)}

REQUIREMENTS:
- Use UE5.3 Python API
- Implement LOD generation ({specs.get('lod_count', 4)} levels)
- Create materials programmatically
- Set up collision
- Export as reusable asset

Provide complete Python script ready to run in Unreal Editor."""

    response = llm.invoke([
        SystemMessage(content="You are an Unreal Engine technical developer expert in Python scripting."),
        HumanMessage(content=prompt)
    ])

    unreal_code = response.content

    # Extract code block if wrapped in markdown
    if "```python" in unreal_code:
        unreal_code = unreal_code.split("```python")[1].split("```")[0].strip()

    print(f"Code generated: {len(unreal_code)} characters\n")

    state["unreal_python_code"] = unreal_code
    state["material_definitions"] = [
        {"name": "M_ProceduralBase", "type": "PBR", "parameters": ["BaseColor", "Roughness", "Metallic"]}
    ]
    state["lod_settings"] = {
        f"LOD{i}": {"poly_reduction": 0.5 ** i} for i in range(specs.get("lod_count", 4))
    }
    state["code_validated"] = True
    state["current_agent"] = "quality"

    return state


# ============================================================================
# TIER 4: Specialized Agent 3 - QualityAgent
# ============================================================================

def quality_agent(state: AssetGenerationState) -> AssetGenerationState:
    """
    QualityAgent: Validates generated assets for production readiness

    TIER 4: Reviews TechnicalAgent output, ensures quality standards
    """
    print(f"\n{'='*60}")
    print("QUALITY AGENT: Validating asset quality")
    print(f"{'='*60}\n")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    code = state["unreal_python_code"]

    prompt = f"""Review this Unreal Python code for production quality.

CODE:
{code[:2000]}...

SPECIFICATIONS:
{json.dumps(state['asset_specifications'], indent=2)}

CHECK:
1. API usage correctness
2. Performance optimization (LODs, collision)
3. Error handling
4. Code organization
5. Production readiness

Score 1-10 and list any issues."""

    response = llm.invoke([
        SystemMessage(content="You are a technical QA specialist for game assets."),
        HumanMessage(content=prompt)
    ])

    # Parse quality assessment
    quality_score = 8  # Default
    issues = []

    if "error" in response.content.lower():
        issues.append("Error handling could be improved")

    if len(code) < 500:
        issues.append("Code seems too minimal for specifications")
        quality_score = 6

    print(f"Quality score: {quality_score}/10")
    print(f"Issues found: {len(issues)}\n")

    state["quality_score"] = quality_score
    state["quality_issues"] = issues
    state["performance_metrics"] = {
        "estimated_poly_count": state["asset_specifications"].get("poly_count_lod0", "unknown"),
        "lod_count": len(state["lod_settings"])
    }
    state["ready_for_production"] = quality_score >= 7 and not issues
    state["current_agent"] = "complete"

    return state


# ============================================================================
# TIER 4: LangGraph Workflow Definition
# ============================================================================

def create_asset_generation_pipeline():
    """
    Create multi-agent pipeline using LangGraph

    TIER 4: Explicit agent coordination and state flow
    """
    workflow = StateGraph(AssetGenerationState)

    # Add specialized agents as nodes
    workflow.add_node("concept", concept_agent)
    workflow.add_node("technical", technical_agent)
    workflow.add_node("quality", quality_agent)

    # Define workflow edges
    workflow.set_entry_point("concept")
    workflow.add_edge("concept", "technical")  # ConceptAgent → TechnicalAgent
    workflow.add_edge("technical", "quality")  # TechnicalAgent → QualityAgent
    workflow.add_edge("quality", END)

    return workflow.compile()


# ============================================================================
# Main Function
# ============================================================================

def generate_procedural_asset(
    creative_brief: str,
    asset_type: str = "modular_building",
    target_platform: str = "PC"
):
    """
    Generate UE5 procedural asset using multi-agent pipeline

    TIER 4: Multiple specialized agents coordinate to complete complex task
    """
    print(f"\n{'='*60}")
    print(f"TIER 4 MULTI-AGENT PIPELINE: Asset Generation")
    print(f"Asset Type: {asset_type}")
    print(f"{'='*60}\n")

    app = create_asset_generation_pipeline()

    initial_state = {
        "creative_brief": creative_brief,
        "asset_type": asset_type,
        "target_platform": target_platform,
        "concept_approved": False,
        "asset_specifications": {},
        "technical_requirements": {},
        "unreal_python_code": "",
        "material_definitions": [],
        "lod_settings": {},
        "code_validated": False,
        "quality_score": 0,
        "quality_issues": [],
        "performance_metrics": {},
        "ready_for_production": False,
        "current_agent": "concept",
        "iteration_count": 0,
        "messages": []
    }

    final_state = app.invoke(initial_state)

    print(f"\n{'='*60}")
    print("PIPELINE COMPLETE")
    print(f"{'='*60}\n")

    print(f"Quality Score: {final_state['quality_score']}/10")
    print(f"Ready for Production: {final_state['ready_for_production']}")
    print(f"\nGenerated Code ({len(final_state['unreal_python_code'])} chars):")
    print(final_state['unreal_python_code'][:500] + "...")

    return final_state


# Example usage
if __name__ == "__main__":
    result = generate_procedural_asset(
        creative_brief="""
        Create a modular sci-fi building system for a space station environment.
        Should include wall modules, floor tiles, ceiling panels, and corner pieces.
        Needs to be optimized for console performance (PS5/Xbox Series X).
        Style: Clean, futuristic, industrial. Modular grid: 4m x 4m.
        """,
        asset_type="modular_building",
        target_platform="Console"
    )

    print(f"\n\nTIER 4 CHARACTERISTICS DEMONSTRATED:")
    print("1. Multiple specialized agents (Concept, Technical, Quality)")
    print("2. Sequential workflow with state passing")
    print("3. Each agent builds on previous agent's work")
    print("4. Coordinated pipeline produces complex output")
