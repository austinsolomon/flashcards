#!/usr/bin/env python3
"""
UE5 - Tier 3 - Procedural Asset Code Generator (LangChain Agent)

TIER 3 CHARACTERISTICS:
- Single agent with Unreal Python expertise
- Tools for API docs, code validation, parameter generation
- Generates production-ready Unreal Python scripts
- Autonomous decision-making for asset generation approach

What It Does:
Given an asset description (e.g., "modular building set"), generates
Unreal Python code for procedural asset creation using geometry scripts,
PCG (Procedural Content Generation), or blueprint scripting.
"""

import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool

load_dotenv()

# ============================================================================
# TIER 3 TOOLS: Unreal Engine Specific
# ============================================================================

def unreal_api_docs(query: str) -> str:
    """Search Unreal Engine Python API documentation"""
    # Production: Integrate with UE docs API or scraped documentation
    docs = {
        "geometry": "unreal.GeometryScriptLibrary - Create/modify static mesh geometry procedurally",
        "pcg": "PCGComponent, PCGSettings - Procedural Content Generation framework",
        "material": "unreal.MaterialEditingLibrary - Create and modify materials programmatically",
        "asset": "unreal.EditorAssetLibrary - Save, load, and manage assets"
    }

    for key, doc in docs.items():
        if key in query.lower():
            return doc

    return "Use unreal.EditorAssetLibrary for asset operations, unreal.GeometryScriptLibrary for geometry"


def code_template_library(asset_type: str) -> str:
    """Get code templates for common procedural asset types"""
    templates = {
        "modular_building": '''
import unreal
import math

def create_modular_building(width_modules=3, height_modules=2, depth_modules=2):
    """Generate modular building with procedural geometry"""

    # Create new static mesh asset
    asset_path = "/Game/Procedural/Buildings/"
    asset_name = f"ModularBuilding_{width_modules}x{height_modules}x{depth_modules}"

    mesh = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        asset_name, asset_path,
        unreal.StaticMesh,
        unreal.StaticMeshFactory()
    )

    # Use geometry script to build modules
    geo_script = unreal.GeometryScriptLibrary_MeshPrimitiveFunctions

    module_size = 400.0  # cm (4 meters)

    for x in range(width_modules):
        for y in range(depth_modules):
            for z in range(height_modules):
                # Create module geometry
                location = unreal.Vector(x * module_size, y * module_size, z * module_size)
                # Add procedural cube module

    return mesh
''',
        "terrain": '''
import unreal
import random

def generate_terrain_heightmap(size_x=512, size_y=512, height_scale=1000):
    """Procedural terrain using PCG"""

    # Create landscape
    landscape_info = unreal.LandscapeEditorObject()
    landscape_info.new_landscape_size_x = size_x
    landscape_info.new_landscape_size_y = size_y

    # Generate height data using noise
    heightmap = []
    for y in range(size_y):
        for x in range(size_x):
            height = generate_perlin_noise(x, y) * height_scale
            heightmap.append(height)

    return heightmap
'''
    }

    return templates.get(asset_type, "# Template not found, use custom approach")


def parameter_validator(params: str) -> str:
    """Validate parameters for procedural generation"""
    try:
        param_dict = json.loads(params)

        # Validate common parameters
        issues = []

        if "size" in param_dict and param_dict["size"] > 10000:
            issues.append("Size exceeds practical limit for static mesh")

        if "lod_levels" in param_dict and param_dict["lod_levels"] > 8:
            issues.append("LOD levels should be <= 8 for performance")

        if not issues:
            return "Parameters validated successfully"
        else:
            return "Issues: " + "; ".join(issues)

    except Exception as e:
        return f"Parameter validation error: {e}"


# ============================================================================
# TIER 3 AGENT
# ============================================================================

tools = [
    Tool(
        name="unreal_api_docs",
        description="Search Unreal Engine Python API documentation. Input: API topic or class name",
        func=unreal_api_docs
    ),
    Tool(
        name="code_template_library",
        description="Get code templates for procedural asset types: modular_building, terrain, props, etc.",
        func=code_template_library
    ),
    Tool(
        name="parameter_validator",
        description="Validate procedural generation parameters (JSON). Checks size limits, LOD levels, etc.",
        func=parameter_validator
    )
]

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert Unreal Engine technical artist specializing in procedural asset generation using Python.

Generate production-ready Unreal Python scripts that:
1. Use proper Unreal Python API (unreal module)
2. Include error handling
3. Support parametric control
4. Optimize for performance (LODs, collision, etc.)
5. Follow UE5 best practices

When given an asset description, provide complete Python code ready to run in Unreal Editor."""),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])


def create_procedural_code_agent():
    """Create UE5 procedural code generation agent"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3, api_key=os.getenv("OPENAI_API_KEY"))
    agent = create_openai_tools_agent(llm, tools, agent_prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=10)


def generate_procedural_asset_code(description: str, parameters: Dict = None) -> str:
    """Main function: Generate UE5 Python code for procedural assets"""
    agent = create_procedural_code_agent()

    query = f"Generate Unreal Python code for: {description}"
    if parameters:
        query += f"\nParameters: {json.dumps(parameters)}"

    result = agent.invoke({"input": query})
    return result["output"]


# Example usage
if __name__ == "__main__":
    code = generate_procedural_asset_code(
        "Modular sci-fi building set with walls, floors, ceilings",
        {"module_size": 400, "variants": 5, "lod_levels": 4}
    )

    print("\n" + "="*60)
    print("GENERATED UNREAL PYTHON CODE:")
    print("="*60)
    print(code)
