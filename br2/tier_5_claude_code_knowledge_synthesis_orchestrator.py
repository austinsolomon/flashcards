"""
BR2 - Tier 5: Recursive Task Decomposition - Knowledge Synthesis Orchestrator

Use Case: Decompose comprehensive knowledge synthesis project into research,
organization, and connection subtasks, spawning appropriate tier automations.

Tool Used: Claude Code orchestrating Tiers 1-4 for PKM
"""

import os
import json
from datetime import datetime


def decompose_knowledge_project(topic: str, scope: str) -> dict:
    """Decompose large knowledge synthesis into subtasks."""

    project = {
        "topic": topic,
        "scope": scope,
        "generated_at": datetime.now().isoformat(),
        "workstreams": []
    }

    workstreams = [
        {
            "id": "inbox_processing",
            "name": "Inbox Processing & Organization",
            "tier": 2,
            "automation": "tier_2_n8n_claude_note_processor.json",
            "tasks": [
                {"name": "Process all inbox notes with AI", "tier": 2},
                {"name": "Auto-categorize into PARA", "tier": 2},
                {"name": "Extract action items to Todoist", "tier": 2},
                {"name": "Generate smart links", "tier": 2}
            ]
        },
        {
            "id": "deep_research",
            "name": "Deep Research on Topic",
            "tier": 4,
            "automation": "tier_4_langgraph_research_system.py",
            "tasks": [
                {"name": "Decompose research question", "tier": 4},
                {"name": "Research sub-questions", "tier": 4},
                {"name": "Synthesize findings", "tier": 4},
                {"name": "Quality review", "tier": 4}
            ]
        },
        {
            "id": "permanent_notes",
            "name": "Permanent Note Generation",
            "tier": 3,
            "automation": "tier_3_langchain_knowledge_synthesis_agent.py",
            "tasks": [
                {"name": "Search vault for existing knowledge", "tier": 3},
                {"name": "Fill gaps with external research", "tier": 3},
                {"name": "Generate atomic permanent notes", "tier": 3},
                {"name": "Create bi-directional links", "tier": 3}
            ]
        },
        {
            "id": "structure_optimization",
            "name": "Vault Structure Optimization",
            "tier": 1,
            "automation": "tier_1_n8n_vault_maintenance.json",
            "tasks": [
                {"name": "Archive old project notes", "tier": 1},
                {"name": "Consolidate duplicate notes", "tier": 1},
                {"name": "Update MOCs (Maps of Content)", "tier": 1},
                {"name": "Generate tag hierarchy", "tier": 1}
            ]
        },
        {
            "id": "daily_systems",
            "name": "Daily Note System Setup",
            "tier": 1,
            "automation": "tier_1_n8n_daily_note_creator.json",
            "tasks": [
                {"name": "Automated daily notes", "tier": 1},
                {"name": "Weekly review templates", "tier": 1},
                {"name": "Monthly retrospectives", "tier": 1}
            ]
        }
    ]

    project["workstreams"] = workstreams

    project["execution_phases"] = [
        {"week": 1, "workstreams": ["inbox_processing"], "goal": "Clean slate - achieve inbox zero"},
        {"week": 2, "workstreams": ["deep_research"], "goal": "Research foundation"},
        {"week": 3, "workstreams": ["permanent_notes"], "goal": "Knowledge synthesis"},
        {"week": 4, "workstreams": ["structure_optimization", "daily_systems"], "goal": "Ongoing maintenance"}
    ]

    return project


def execute_knowledge_orchestration(project: dict):
    """Execute knowledge project by spawning tier automations."""

    print(f"\n{'='*70}")
    print(f"KNOWLEDGE SYNTHESIS PROJECT: {project['topic']}")
    print(f"Scope: {project['scope']}")
    print(f"{'='*70}\n")

    for phase in project["execution_phases"]:
        print(f"\nWeek {phase['week']}: {phase['goal']}")
        print("─" * 70)

        for ws_id in phase["workstreams"]:
            ws = next((w for w in project["workstreams"] if w["id"] == ws_id), None)

            if ws:
                print(f"\n  ► {ws['name']} (Tier {ws['tier']})")
                print(f"    Automation: {ws['automation']}")

                for task in ws["tasks"]:
                    print(f"      └─ {task['name']} (Tier {task['tier']})")

    # Save
    output_dir = "./knowledge_projects"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{output_dir}/project_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(project, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Knowledge project orchestration complete!")
    print(f"Saved to: {filename}")
    print(f"{'='*70}\n")

    return project


if __name__ == "__main__":
    """
    Tier 5: Orchestrates comprehensive Second Brain overhaul.

    Claude Code coordinates:
    - Tier 1: Daily note automation
    - Tier 2: AI-powered note processing
    - Tier 3: Knowledge synthesis agents
    - Tier 4: Multi-agent research systems
    """

    project = decompose_knowledge_project(
        topic="Comprehensive Learning System on AI Agents & Automation",
        scope="Research, synthesize, and organize all knowledge on building AI agent systems"
    )

    execute_knowledge_orchestration(project)

    print("\nTier 5: Recursive decomposition for PKM projects")
