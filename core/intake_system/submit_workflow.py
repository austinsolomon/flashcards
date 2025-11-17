#!/usr/bin/env python3
"""
Automation Workflow Intake Submission Tool

This CLI tool allows users to submit workflow automation requests either:
1. Interactively (prompted for each field)
2. From a YAML/JSON file
3. Programmatically via Python API

Usage:
    # Interactive mode
    python submit_workflow.py --interactive

    # From file
    python submit_workflow.py --file intake_bdr_lead_intel.yaml

    # Validate only (don't submit)
    python submit_workflow.py --file intake.yaml --validate-only

Requirements:
    pip install pyyaml psycopg2-binary python-dotenv rich
"""

import argparse
import json
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from decimal import Decimal

try:
    import psycopg2
    from psycopg2.extras import Json
    from dotenv import load_dotenv
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich import print as rprint
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Install with: pip install pyyaml psycopg2-binary python-dotenv rich")
    sys.exit(1)

# Load environment variables
load_dotenv()

console = Console()


@dataclass
class WorkflowSubmission:
    """Data class representing a workflow automation submission"""

    # Metadata
    submitted_by: str
    department: str
    priority: str  # High, Medium, Low

    # Section 1: Problem Statement
    problem_statement: str

    # Section 2: Current Manual Process
    current_process: List[Dict[str, Any]]
    time_per_occurrence_minutes: Optional[int] = None
    frequency_per_period: Optional[int] = None
    frequency_period: Optional[str] = None  # day, week, month
    people_affected: Optional[int] = None
    total_weekly_hours: Optional[float] = None

    # Section 3: Desired Automation
    trigger_description: Optional[str] = None
    data_sources: Optional[List[Dict[str, str]]] = None
    process_steps: Optional[List[Dict[str, str]]] = None
    outputs: Optional[List[Dict[str, str]]] = None

    # Section 4: Success Criteria
    success_criteria: Optional[List[Dict[str, str]]] = None

    # Section 5: Constraints & Requirements
    integrations_required: Optional[List[Dict[str, str]]] = None
    cost_constraints: Optional[Dict[str, Any]] = None
    volume_scale: Optional[Dict[str, Any]] = None
    compliance_requirements: Optional[List[str]] = None
    security_requirements: Optional[List[str]] = None
    human_approval_gates: Optional[List[str]] = None
    other_requirements: Optional[str] = None

    # Section 6: Complexity Signals
    decision_complexity: Optional[Dict[str, Any]] = None
    integration_complexity: Optional[Dict[str, Any]] = None
    state_management_complexity: Optional[Dict[str, Any]] = None
    suggested_tier: Optional[int] = None
    suggested_tier_reasoning: Optional[str] = None

    # Section 7: Additional Context
    current_workarounds: Optional[str] = None
    related_workflows: Optional[str] = None
    known_edge_cases: Optional[str] = None
    dependencies: Optional[str] = None
    nice_to_haves: Optional[str] = None

    def calculate_weekly_hours(self) -> Optional[float]:
        """Calculate total weekly hours if inputs are available"""
        if all(
            [
                self.time_per_occurrence_minutes,
                self.frequency_per_period,
                self.frequency_period,
                self.people_affected,
            ]
        ):
            # Convert to weekly
            if self.frequency_period == "day":
                weekly_occurrences = self.frequency_per_period * 5
            elif self.frequency_period == "week":
                weekly_occurrences = self.frequency_per_period
            elif self.frequency_period == "month":
                weekly_occurrences = self.frequency_per_period / 4
            else:
                return None

            hours_per_week = (
                (self.time_per_occurrence_minutes / 60)
                * weekly_occurrences
                * self.people_affected
            )
            return round(hours_per_week, 2)
        return None

    def validate(self) -> tuple[bool, List[str]]:
        """Validate submission data. Returns (is_valid, error_messages)"""
        errors = []

        # Required fields
        if not self.submitted_by:
            errors.append("submitted_by is required")
        if not self.department:
            errors.append("department is required")
        if self.priority not in ["High", "Medium", "Low"]:
            errors.append("priority must be High, Medium, or Low")
        if not self.problem_statement or len(self.problem_statement) < 50:
            errors.append("problem_statement must be at least 50 characters")
        if not self.current_process or len(self.current_process) == 0:
            errors.append("current_process must have at least one step")

        # Tier validation
        if self.suggested_tier is not None:
            if not (0 <= self.suggested_tier <= 6):
                errors.append("suggested_tier must be between 0 and 6")

        return (len(errors) == 0, errors)


class IntakeSubmissionTool:
    """Main tool for submitting workflow automation requests"""

    def __init__(self, db_config: Optional[Dict[str, str]] = None):
        self.db_config = db_config or self._get_db_config_from_env()
        self.conn = None

    def _get_db_config_from_env(self) -> Dict[str, str]:
        """Load database configuration from environment variables"""
        import os

        return {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": os.getenv("POSTGRES_PORT", "5432"),
            "database": os.getenv("POSTGRES_DB", "automation_db"),
            "user": os.getenv("POSTGRES_USER", "automation_user"),
            "password": os.getenv("POSTGRES_PASSWORD", ""),
        }

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            return True
        except psycopg2.Error as e:
            console.print(f"[red]Database connection failed: {e}[/red]")
            return False

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def load_from_file(self, filepath: str) -> WorkflowSubmission:
        """Load submission from YAML or JSON file"""
        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(path, "r") as f:
            if path.suffix in [".yaml", ".yml"]:
                data = yaml.safe_load(f)
            elif path.suffix == ".json":
                data = json.load(f)
            else:
                raise ValueError("File must be .yaml, .yml, or .json")

        return WorkflowSubmission(**data)

    def interactive_submission(self) -> WorkflowSubmission:
        """Guide user through interactive submission"""
        console.print("\n[bold cyan]Workflow Automation Intake - Interactive Mode[/bold cyan]\n")

        # Metadata
        submitted_by = Prompt.ask("Your email")
        department = Prompt.ask(
            "Department",
            choices=[
                "Marketing",
                "Sales",
                "BDR",
                "Customer Success",
                "Finance",
                "Operations",
                "Other",
            ],
        )
        priority = Prompt.ask("Priority", choices=["High", "Medium", "Low"])

        # Section 1
        console.print("\n[bold]Section 1: Problem Statement[/bold]")
        problem_statement = Prompt.ask(
            "Describe the pain point and business impact (2-3 sentences)"
        )

        # Section 2
        console.print("\n[bold]Section 2: Current Manual Process[/bold]")
        current_process = []
        step_num = 1
        while True:
            step_desc = Prompt.ask(
                f"Step {step_num} description (or 'done' to finish)",
                default="done" if step_num > 1 else "",
            )
            if step_desc.lower() == "done":
                break
            tool = Prompt.ask(f"Tool/system used in step {step_num}", default="")
            current_process.append({"step": step_num, "description": step_desc, "tool": tool})
            step_num += 1

        time_per_occurrence = int(Prompt.ask("Time per occurrence (minutes)", default="0"))
        frequency_per_period = int(Prompt.ask("Frequency (how many times)", default="0"))
        frequency_period = Prompt.ask(
            "Per period", choices=["day", "week", "month"], default="day"
        )
        people_affected = int(Prompt.ask("Number of people affected", default="1"))

        # Calculate weekly hours
        submission = WorkflowSubmission(
            submitted_by=submitted_by,
            department=department,
            priority=priority,
            problem_statement=problem_statement,
            current_process=current_process,
            time_per_occurrence_minutes=time_per_occurrence if time_per_occurrence > 0 else None,
            frequency_per_period=frequency_per_period if frequency_per_period > 0 else None,
            frequency_period=frequency_period,
            people_affected=people_affected if people_affected > 0 else None,
        )

        weekly_hours = submission.calculate_weekly_hours()
        if weekly_hours:
            console.print(f"\n[green]Calculated weekly hours: {weekly_hours}[/green]")
            submission.total_weekly_hours = weekly_hours

        # Simplified for remaining sections - user can fill YAML file for full detail
        console.print(
            "\n[yellow]For complete details, consider filling out a YAML file.[/yellow]"
        )
        console.print(
            "[yellow]This interactive mode captures core information only.[/yellow]\n"
        )

        return submission

    def submit(self, submission: WorkflowSubmission, validate_only: bool = False) -> Optional[str]:
        """Submit workflow to database. Returns submission_id if successful"""

        # Validate
        is_valid, errors = submission.validate()
        if not is_valid:
            console.print("[red]Validation failed:[/red]")
            for error in errors:
                console.print(f"  - {error}")
            return None

        console.print("[green]✓ Validation passed[/green]")

        if validate_only:
            console.print("[yellow]Validate-only mode. Not submitting to database.[/yellow]")
            return None

        # Calculate weekly hours if not provided
        if not submission.total_weekly_hours:
            submission.total_weekly_hours = submission.calculate_weekly_hours()

        # Connect to database
        if not self.connect():
            return None

        try:
            cursor = self.conn.cursor()

            # Generate submission ID
            cursor.execute("SELECT intake.generate_submission_id()")
            submission_id = cursor.fetchone()[0]

            # Insert submission
            insert_query = """
                INSERT INTO intake.workflow_submissions (
                    submission_id,
                    submitted_by,
                    department,
                    priority,
                    problem_statement,
                    current_process,
                    time_per_occurrence_minutes,
                    frequency_per_period,
                    frequency_period,
                    people_affected,
                    total_weekly_hours,
                    trigger_description,
                    data_sources,
                    process_steps,
                    outputs,
                    success_criteria,
                    integrations_required,
                    cost_constraints,
                    volume_scale,
                    compliance_requirements,
                    security_requirements,
                    human_approval_gates,
                    other_requirements,
                    decision_complexity,
                    integration_complexity,
                    state_management_complexity,
                    suggested_tier,
                    suggested_tier_reasoning,
                    current_workarounds,
                    related_workflows,
                    known_edge_cases,
                    dependencies,
                    nice_to_haves,
                    created_by
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """

            cursor.execute(
                insert_query,
                (
                    submission_id,
                    submission.submitted_by,
                    submission.department,
                    submission.priority,
                    submission.problem_statement,
                    Json(submission.current_process),
                    submission.time_per_occurrence_minutes,
                    submission.frequency_per_period,
                    submission.frequency_period,
                    submission.people_affected,
                    submission.total_weekly_hours,
                    submission.trigger_description,
                    Json(submission.data_sources) if submission.data_sources else None,
                    Json(submission.process_steps) if submission.process_steps else None,
                    Json(submission.outputs) if submission.outputs else None,
                    Json(submission.success_criteria) if submission.success_criteria else None,
                    Json(submission.integrations_required)
                    if submission.integrations_required
                    else None,
                    Json(submission.cost_constraints) if submission.cost_constraints else None,
                    Json(submission.volume_scale) if submission.volume_scale else None,
                    Json(submission.compliance_requirements)
                    if submission.compliance_requirements
                    else None,
                    Json(submission.security_requirements)
                    if submission.security_requirements
                    else None,
                    Json(submission.human_approval_gates)
                    if submission.human_approval_gates
                    else None,
                    submission.other_requirements,
                    Json(submission.decision_complexity)
                    if submission.decision_complexity
                    else None,
                    Json(submission.integration_complexity)
                    if submission.integration_complexity
                    else None,
                    Json(submission.state_management_complexity)
                    if submission.state_management_complexity
                    else None,
                    submission.suggested_tier,
                    submission.suggested_tier_reasoning,
                    submission.current_workarounds,
                    submission.related_workflows,
                    submission.known_edge_cases,
                    submission.dependencies,
                    submission.nice_to_haves,
                    submission.submitted_by,
                ),
            )

            self.conn.commit()
            cursor.close()

            console.print(f"\n[bold green]✓ Submission successful![/bold green]")
            console.print(f"Submission ID: [cyan]{submission_id}[/cyan]")

            return submission_id

        except psycopg2.Error as e:
            console.print(f"[red]Database error: {e}[/red]")
            if self.conn:
                self.conn.rollback()
            return None
        finally:
            self.close()

    def export_template(self, filepath: str, format: str = "yaml"):
        """Export a blank template file"""
        template = {
            "submitted_by": "your.email@company.com",
            "department": "Marketing",
            "priority": "Medium",
            "problem_statement": "Describe the pain point and business impact in 2-3 sentences...",
            "current_process": [
                {"step": 1, "description": "First step description", "tool": "Tool name"},
                {"step": 2, "description": "Second step description", "tool": "Tool name"},
            ],
            "time_per_occurrence_minutes": 10,
            "frequency_per_period": 20,
            "frequency_period": "day",
            "people_affected": 5,
            "trigger_description": "What triggers the automation...",
            "data_sources": [
                {"source": "System name", "description": "What data", "api": "API details"}
            ],
            "process_steps": [
                {"step": 1, "description": "What the automation does"},
                {"step": 2, "description": "Next step"},
            ],
            "outputs": [
                {
                    "system": "Salesforce",
                    "field": "Field_Name__c",
                    "format": "JSON/Text/etc",
                    "description": "What gets created/updated",
                }
            ],
            "success_criteria": [
                {
                    "metric": "Time Savings",
                    "before": "10 minutes",
                    "after": "30 seconds",
                    "measurement": "How to measure",
                }
            ],
            "integrations_required": [
                {
                    "system": "Salesforce",
                    "api": "REST API v57",
                    "rate_limits": "100 req/min",
                    "auth": "OAuth 2.0",
                }
            ],
            "cost_constraints": {
                "max_per_execution": 0.50,
                "max_monthly": 500,
                "details": "Additional cost notes",
            },
            "volume_scale": {
                "average": 50,
                "peak": 100,
                "concurrent": 20,
                "response_time": "< 2 minutes",
            },
            "compliance_requirements": ["SOC 2", "GDPR"],
            "security_requirements": ["PII encryption", "Audit logging"],
            "human_approval_gates": ["BDR reviews email before send"],
            "other_requirements": "Any additional requirements...",
            "decision_complexity": {
                "flags": ["contextual_reasoning", "nlg"],
                "explanation": "Why these apply...",
            },
            "integration_complexity": {
                "flags": ["3_plus_systems", "rate_limits"],
                "explanation": "Why these apply...",
            },
            "state_management_complexity": {
                "flags": ["multi_step"],
                "explanation": "Why these apply...",
            },
            "suggested_tier": 2,
            "suggested_tier_reasoning": "Tier 2-3 because...",
            "current_workarounds": "How people currently work around this...",
            "related_workflows": "Other workflows this connects to...",
            "known_edge_cases": "Edge cases to handle...",
            "dependencies": "What needs to be in place first...",
            "nice_to_haves": "Future enhancements...",
        }

        path = Path(filepath)
        with open(path, "w") as f:
            if format == "yaml":
                yaml.dump(template, f, default_flow_style=False, sort_keys=False)
            else:
                json.dump(template, f, indent=2)

        console.print(f"[green]Template exported to {filepath}[/green]")


def main():
    parser = argparse.ArgumentParser(
        description="Submit workflow automation intake requests"
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Interactive mode (guided prompts)",
    )
    parser.add_argument("--file", "-f", type=str, help="Load submission from YAML/JSON file")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate submission without submitting to database",
    )
    parser.add_argument(
        "--export-template",
        type=str,
        help="Export a blank template to the specified file",
    )
    parser.add_argument(
        "--format",
        choices=["yaml", "json"],
        default="yaml",
        help="Template format (default: yaml)",
    )

    args = parser.parse_args()

    tool = IntakeSubmissionTool()

    # Export template
    if args.export_template:
        tool.export_template(args.export_template, args.format)
        return

    # Load submission
    if args.file:
        try:
            submission = tool.load_from_file(args.file)
            console.print(f"[green]✓ Loaded submission from {args.file}[/green]")
        except Exception as e:
            console.print(f"[red]Error loading file: {e}[/red]")
            sys.exit(1)
    elif args.interactive:
        submission = tool.interactive_submission()
    else:
        console.print("[yellow]Please specify --interactive or --file[/yellow]")
        parser.print_help()
        sys.exit(1)

    # Submit
    submission_id = tool.submit(submission, validate_only=args.validate_only)

    if submission_id:
        console.print("\n[bold]Next Steps:[/bold]")
        console.print("1. Your submission will be reviewed within 1-2 business days")
        console.print("2. You'll receive tier assignment and ROI estimate")
        console.print("3. Approved workflows are prioritized and scheduled for build")


if __name__ == "__main__":
    main()
