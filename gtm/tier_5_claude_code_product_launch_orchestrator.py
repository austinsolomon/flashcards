"""
GTM - Tier 5: Recursive Task Decomposition - Product Launch Orchestrator

Use Case: Autonomously decompose a product launch into subtasks and spawn
appropriate tier automations (Tier 1-4) for each component.

Tool Used: Claude Code with subagent spawning capability
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any


# ============================================================================
# TIER ORCHESTRATION LOGIC
# ============================================================================

def decompose_product_launch(product: str, launch_date: str, target_market: str) -> Dict[str, Any]:
    """
    Recursively decompose product launch into hierarchical subtasks.
    Returns task tree with tier assignments.
    """

    launch_plan = {
        "product": product,
        "launch_date": launch_date,
        "target_market": target_market,
        "generated_at": datetime.now().isoformat(),
        "tasks": []
    }

    # Level 1: Major launch workstreams
    major_tasks = [
        {
            "id": "market_research",
            "name": "Market & Competitive Research",
            "tier": 3,  # LangChain single agent
            "automation": "tier_3_langchain_competitor_research_agent.py",
            "subtasks": [
                {"name": "Research top 5 competitors", "tier": 3},
                {"name": "Analyze target market segments", "tier": 3},
                {"name": "Create competitive battlecards", "tier": 3}
            ]
        },
        {
            "id": "campaign_planning",
            "name": "Campaign Strategy & Planning",
            "tier": 4,  # Multi-agent collaboration
            "automation": "tier_4_langgraph_campaign_planner.py",
            "subtasks": [
                {"name": "Market research (feeds into strategy)", "tier": 3},
                {"name": "Develop positioning & messaging", "tier": 4},
                {"name": "Create content calendar", "tier": 4},
                {"name": "Plan asset requirements", "tier": 4}
            ]
        },
        {
            "id": "content_production",
            "name": "Content & Asset Production",
            "tier": 1,  # Deterministic workflows
            "automation": "tier_1_n8n_content_production_workflow.json",
            "subtasks": [
                {"name": "Blog posts (5 articles)", "tier": 1},
                {"name": "Social media graphics", "tier": 1},
                {"name": "Demo videos", "tier": 1},
                {"name": "Email templates", "tier": 1},
                {"name": "Landing pages", "tier": 1}
            ]
        },
        {
            "id": "lead_gen_setup",
            "name": "Lead Generation Infrastructure",
            "tier": 2,  # Context-aware workflows
            "automation": "tier_2_n8n_lead_scoring_classifier.json",
            "subtasks": [
                {"name": "Setup lead capture forms", "tier": 1},
                {"name": "Configure AI lead scoring", "tier": 2},
                {"name": "Create email nurture sequences", "tier": 2},
                {"name": "Setup CRM automation", "tier": 1}
            ]
        },
        {
            "id": "metrics_dashboard",
            "name": "Launch Metrics & Reporting",
            "tier": 1,  # Deterministic aggregation
            "automation": "tier_1_n8n_daily_sales_metrics_digest.json",
            "subtasks": [
                {"name": "Setup daily metrics digest", "tier": 1},
                {"name": "Configure real-time alerts", "tier": 1},
                {"name": "Create executive dashboard", "tier": 1}
            ]
        }
    ]

    launch_plan["tasks"] = major_tasks

    # Calculate execution order based on dependencies
    launch_plan["execution_sequence"] = [
        {"week": 1, "task_ids": ["market_research"], "rationale": "Must complete before campaign planning"},
        {"week": 2, "task_ids": ["campaign_planning"], "rationale": "Uses research outputs"},
        {"week": 3-6, "task_ids": ["content_production", "lead_gen_setup"], "rationale": "Parallel execution"},
        {"week": 7, "task_ids": ["metrics_dashboard"], "rationale": "Setup before launch"},
    ]

    return launch_plan


def spawn_tier_automation(task: Dict[str, Any]) -> str:
    """
    Spawn appropriate tier automation for a task.
    In real implementation, this would actually execute the automation.
    """

    tier = task["tier"]
    automation = task.get("automation", "")

    print(f"\n>>> Spawning Tier {tier} automation: {task['name']}")
    print(f"    Automation: {automation}")

    # Simulated execution
    if tier == 1:
        result = f"Tier 1 (n8n workflow) scheduled for: {task['name']}"
    elif tier == 2:
        result = f"Tier 2 (n8n + AI) configured for: {task['name']}"
    elif tier == 3:
        result = f"Tier 3 (LangChain agent) launched for: {task['name']}"
    elif tier == 4:
        result = f"Tier 4 (LangGraph multi-agent) executing: {task['name']}"
    else:
        result = f"Unknown tier for: {task['name']}"

    return result


def execute_launch_orchestration(launch_plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the product launch by spawning appropriate tier automations.
    Claude Code would orchestrate this, spawning subagents as needed.
    """

    execution_log = []

    print(f"\n{'='*70}")
    print(f"PRODUCT LAUNCH ORCHESTRATION: {launch_plan['product']}")
    print(f"Launch Date: {launch_plan['launch_date']}")
    print(f"{'='*70}\n")

    # Execute in sequence based on dependencies
    for phase in launch_plan["execution_sequence"]:
        print(f"\n{'─'*70}")
        print(f"Week {phase['week']}: {phase['rationale']}")
        print(f"{'─'*70}")

        for task_id in phase["task_ids"]:
            # Find the task
            task = next((t for t in launch_plan["tasks"] if t["id"] == task_id), None)

            if task:
                # Spawn automation for main task
                result = spawn_tier_automation(task)
                execution_log.append({
                    "task": task["name"],
                    "tier": task["tier"],
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })

                # Handle subtasks
                if "subtasks" in task:
                    for subtask in task["subtasks"]:
                        sub_result = spawn_tier_automation(subtask)
                        execution_log.append({
                            "task": f"  └─ {subtask['name']}",
                            "tier": subtask["tier"],
                            "result": sub_result,
                            "timestamp": datetime.now().isoformat()
                        })

    # Save execution log
    output_dir = "./launch_orchestrations"
    os.makedirs(output_dir, exist_ok=True)

    orchestration_record = {
        **launch_plan,
        "execution_log": execution_log,
        "completed_at": datetime.now().isoformat()
    }

    filename = f"{output_dir}/launch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(orchestration_record, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Orchestration complete. Spawned {len(execution_log)} automations.")
    print(f"Execution log saved to: {filename}")
    print(f"{'='*70}\n")

    return orchestration_record


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    How to Run:

    1. This represents Claude Code's orchestration capability
    2. In practice, Claude Code would:
       - Analyze the launch requirements
       - Decompose into subtasks recursively
       - Determine appropriate tier for each subtask
       - Spawn actual automations (n8n workflows, LangChain agents, etc.)
       - Monitor execution and coordinate dependencies

    3. Run this script to see the orchestration plan:
       python tier_5_claude_code_product_launch_orchestrator.py
    """

    # Example: Orchestrate a product launch
    launch_plan = decompose_product_launch(
        product="AI-Powered Sales Intelligence Platform v2.0",
        launch_date="2025-03-15",
        target_market="B2B SaaS companies, 50-500 employees"
    )

    # Execute orchestration
    execution_record = execute_launch_orchestration(launch_plan)

    print("\n" + "="*70)
    print("TIER 5 CLASSIFICATION REASONING:")
    print("="*70)
    print("""
This is Tier 5 (Recursive Task Decomposition) because:

1. **Hierarchical decomposition**: Breaks complex project into levels
   - Level 0: Product launch (top)
   - Level 1: Major workstreams (research, campaign, content, etc.)
   - Level 2: Specific subtasks within each workstream
   - Could decompose further if needed

2. **Tier assignment**: Determines appropriate automation tier for each task
   - Market research → Tier 3 (LangChain agent)
   - Campaign planning → Tier 4 (Multi-agent)
   - Content production → Tier 1 (n8n workflows)
   - Lead scoring → Tier 2 (n8n + AI)

3. **Dependency management**: Coordinates execution order
   - Research before strategy
   - Strategy before content production
   - Parallel execution where possible

4. **Autonomous spawning**: Claude Code spawns appropriate tier automations
   - Doesn't do all work itself
   - Delegates to specialized tiers
   - Monitors and coordinates

5. **Adaptive planning**: Could adjust based on intermediate results
   - If research reveals new competitor, spawn additional research
   - If campaign test fails, re-route to strategy refinement

This differs from Tier 4 (multi-agent) because:
- Tier 4: Fixed agent graph for single task type
- Tier 5: Dynamic decomposition across multiple automation tiers
- Tier 5 is the "project manager" tier

This differs from Tier 6 (autonomous specialist) because:
- Tier 5: One-time project decomposition
- Tier 6: Ongoing autonomous management with persistent state

Use Cases:
- Product launches
- Market expansion projects
- Complete automation system buildouts
- Complex multi-phase initiatives

Execution:
- Claude Code analyzes requirements
- Recursively decomposes into subtasks
- Spawns Tier 1-4 automations as needed
- Monitors progress and adjusts
- Coordinates dependencies

Cost: Variable (sum of all spawned automations)
Time: Days to weeks (coordinates long-running project)
Output: Fully executed project with all components automated
""")
