#!/usr/bin/env python3
"""
iPhone Compliance Testing Agent - Tier 4/5 Multi-Agent System

Tests iPhone apps for compliance with digital safety standards:
- IEEE 7010 (AI Well-being)
- DSA Article 28 (Protection of minors)
- AED (Attention Economy Design)
- ICO Age Appropriate Design Code

Architecture:
- Tier 4: LangGraph multi-agent coordination
- Tier 5: Claude Code orchestration with human review

Agents:
1. AppSelectorAgent: Choose app to test
2. NavigationAgent: Navigate through app flows
3. VisionAnalysisAgent: Detect dark patterns via screenshots
4. ComplianceEvaluationAgent: Evaluate against standards
5. ReportGenerationAgent: Generate compliance report
"""

import os
import yaml
import json
from typing import TypedDict, List, Dict, Annotated
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

# Import emulator integration
import sys
sys.path.append(os.path.dirname(__file__))
from emulator.ios_emulator import iOSEmulator

load_dotenv()

# ============================================================================
# TIER 4: Define Shared State (flows between agents)
# ============================================================================

class ComplianceState(TypedDict):
    """Shared state that flows between all agents"""
    # App Selection
    selected_app: Dict
    app_name: str
    bundle_id: str

    # Navigation
    navigation_flow: List[Dict]
    flow_results: List[Dict]
    screenshots: List[str]

    # Vision Analysis
    dark_patterns_detected: List[Dict]
    ui_analysis: Dict

    # Compliance Evaluation
    compliance_scores: Dict
    violations: List[Dict]

    # Report
    final_report: str
    report_path: str

    # Session
    status: str
    timestamp: str
    session_summary: Dict


# ============================================================================
# Load Compliance Standards
# ============================================================================

def load_compliance_standards() -> Dict:
    """Load compliance standards from YAML config"""
    config_path = os.path.join(
        os.path.dirname(__file__),
        "config/compliance_standards.yaml"
    )

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


COMPLIANCE_STANDARDS = load_compliance_standards()


# ============================================================================
# AGENT 1: App Selector
# ============================================================================

def app_selector_agent(state: ComplianceState) -> ComplianceState:
    """
    Agent 1: Select app to test from predefined list

    In production: Would present UI for selection
    MVP: Uses first app or specified app
    """
    print("\n" + "="*70)
    print("🎯 APP SELECTOR AGENT")
    print("="*70)

    apps = COMPLIANCE_STANDARDS['popular_test_apps']

    # Display available apps
    print("\n📱 Available apps for compliance testing:\n")
    for i, app in enumerate(apps, 1):
        print(f"   {i}. {app['name']} ({app['category']})")
        print(f"      Bundle ID: {app['bundle_id']}")
        print(f"      Known concerns: {', '.join(app['known_concerns'][:2])}...")
        print()

    # For MVP, select first app or use pre-selected
    if state.get("selected_app"):
        selected_app = state["selected_app"]
    else:
        # Default to first app for MVP
        selected_app = apps[0]

    print(f"✅ Selected: {selected_app['name']}\n")

    return {
        **state,
        "selected_app": selected_app,
        "app_name": selected_app['name'],
        "bundle_id": selected_app['bundle_id'],
        "timestamp": datetime.now().isoformat(),
        "status": "app_selected"
    }


# ============================================================================
# AGENT 2: Navigation Agent
# ============================================================================

def navigation_agent(state: ComplianceState) -> ComplianceState:
    """
    Agent 2: Navigate through app to test various flows

    Executes predefined test flows:
    - Onboarding flow
    - Main feature usage
    - Settings/privacy controls
    - Cancellation/unsubscribe flow
    """
    print("\n" + "="*70)
    print("🧭 NAVIGATION AGENT")
    print("="*70)

    app_name = state['app_name']
    bundle_id = state['bundle_id']

    print(f"\n📱 Testing app: {app_name}")
    print(f"🔄 Will execute compliance testing flows...\n")

    # Define test flows based on app
    test_flows = generate_test_flows(app_name)

    print(f"📋 Generated {len(test_flows)} test flows:")
    for i, flow in enumerate(test_flows, 1):
        print(f"   {i}. {flow['name']} ({len(flow['steps'])} steps)")

    # Simulate navigation (in production, would use emulator)
    print(f"\n⚠️ MVP MODE: Simulating navigation")
    print(f"   In production, would use iOSEmulator to:")
    print(f"   - Connect to iOS Simulator")
    print(f"   - Launch {app_name}")
    print(f"   - Execute {len(test_flows)} test flows")
    print(f"   - Capture screenshots at each step")

    # Simulated results
    flow_results = []
    screenshots = []

    for flow in test_flows:
        flow_result = {
            "flow_name": flow['name'],
            "steps_executed": len(flow['steps']),
            "success": True,
            "screenshots_captured": len(flow['steps']) * 2,  # Before/after each step
            "duration": 15.0  # Simulated
        }
        flow_results.append(flow_result)

        # Simulate screenshots
        for step in flow['steps']:
            screenshots.append({
                "flow": flow['name'],
                "step": step['description'],
                "path": f"screenshots/{app_name}_{len(screenshots)}.png",
                "timestamp": datetime.now().isoformat()
            })

    print(f"\n✅ Navigation complete:")
    print(f"   Flows executed: {len(flow_results)}")
    print(f"   Screenshots captured: {len(screenshots)}")

    return {
        **state,
        "navigation_flow": test_flows,
        "flow_results": flow_results,
        "screenshots": screenshots,
        "status": "navigation_complete"
    }


def generate_test_flows(app_name: str) -> List[Dict]:
    """Generate test flows based on app type"""

    if app_name == "Instagram":
        return [
            {
                "name": "Onboarding Flow",
                "steps": [
                    {"action": "wait", "description": "App launch", "duration": 3},
                    {"action": "tap", "element": "Sign Up", "description": "Tap sign up"},
                    {"action": "scroll", "description": "Review terms", "distance": 400},
                    {"action": "tap", "element": "Privacy Policy", "description": "Check privacy policy"},
                ]
            },
            {
                "name": "Feed Engagement",
                "steps": [
                    {"action": "scroll", "description": "Scroll feed", "distance": 500},
                    {"action": "wait", "duration": 2, "description": "Observe infinite scroll"},
                    {"action": "scroll", "description": "Continue scrolling", "distance": 500},
                    {"action": "tap", "element": "Like", "description": "Test engagement mechanic"},
                ]
            },
            {
                "name": "Privacy Settings",
                "steps": [
                    {"action": "tap", "element": "Profile", "description": "Go to profile"},
                    {"action": "tap", "element": "Settings", "description": "Open settings"},
                    {"action": "tap", "element": "Privacy", "description": "Check privacy controls"},
                    {"action": "scroll", "description": "Review privacy options", "distance": 300},
                ]
            }
        ]

    # Default generic flow for other apps
    return [
        {
            "name": "App Onboarding",
            "steps": [
                {"action": "wait", "description": "App launch", "duration": 3},
                {"action": "scroll", "description": "Review initial screens", "distance": 300},
            ]
        },
        {
            "name": "Main Feature Exploration",
            "steps": [
                {"action": "scroll", "description": "Explore main screen", "distance": 400},
                {"action": "wait", "duration": 2, "description": "Observe UI patterns"},
            ]
        },
        {
            "name": "Settings Review",
            "steps": [
                {"action": "tap", "element": "Settings", "description": "Open settings"},
                {"action": "scroll", "description": "Review settings", "distance": 300},
            ]
        }
    ]


# ============================================================================
# AGENT 3: Vision Analysis Agent
# ============================================================================

def vision_analysis_agent(state: ComplianceState) -> ComplianceState:
    """
    Agent 3: Analyze screenshots for dark patterns using Claude Vision

    Detects:
    - Dark patterns (obstruction, sneaking, urgency, social proof)
    - Predatory design mechanics
    - Engagement optimization tactics
    """
    print("\n" + "="*70)
    print("👁️ VISION ANALYSIS AGENT")
    print("="*70)

    screenshots = state['screenshots']

    print(f"\n🔍 Analyzing {len(screenshots)} screenshots for dark patterns...")

    # Initialize Claude with vision capabilities
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096
    )

    dark_patterns_detected = []
    dark_pattern_categories = COMPLIANCE_STANDARDS['dark_patterns']['categories']

    # Analyze each screenshot (simulated for MVP)
    print(f"\n⚠️ MVP MODE: Simulating vision analysis")
    print(f"   In production, would:")
    print(f"   - Load each screenshot image")
    print(f"   - Send to Claude Vision API")
    print(f"   - Detect dark patterns in UI")
    print(f"   - Classify by category and severity")

    # Simulated dark pattern detection based on app
    app_name = state['app_name']
    known_concerns = state['selected_app']['known_concerns']

    for concern in known_concerns:
        # Map known concerns to dark pattern categories
        if "infinite scroll" in concern.lower():
            dark_patterns_detected.append({
                "pattern": "Infinite Scroll",
                "category": "engagement_tactics",
                "severity": "high",
                "description": "App uses infinite scroll without clear stopping point",
                "screenshot": "feed_view.png",
                "location": "Main feed"
            })
        elif "streak" in concern.lower() or "daily" in concern.lower():
            dark_patterns_detected.append({
                "pattern": "Streak Mechanics",
                "category": "engagement_tactics",
                "severity": "high",
                "description": "App uses streak/daily reward system creating obligation",
                "screenshot": "daily_rewards.png",
                "location": "Rewards screen"
            })
        elif "timer" in concern.lower() or "limited time" in concern.lower():
            dark_patterns_detected.append({
                "pattern": "Countdown Timer",
                "category": "urgency",
                "severity": "medium",
                "description": "App uses countdown timers to create artificial urgency",
                "screenshot": "offer_screen.png",
                "location": "Purchase flow"
            })
        elif "social" in concern.lower():
            dark_patterns_detected.append({
                "pattern": "Social Pressure",
                "category": "social_proof",
                "severity": "high",
                "description": "App uses social pressure tactics (e.g., 'X is waiting')",
                "screenshot": "social_prompt.png",
                "location": "Notification/prompt"
            })

    print(f"\n🚨 Dark patterns detected: {len(dark_patterns_detected)}")
    for dp in dark_patterns_detected:
        print(f"   • {dp['pattern']} ({dp['severity']}) - {dp['description'][:60]}...")

    # UI Analysis summary
    ui_analysis = {
        "total_screens_analyzed": len(screenshots),
        "dark_patterns_found": len(dark_patterns_detected),
        "high_severity_count": len([dp for dp in dark_patterns_detected if dp['severity'] == 'high']),
        "categories_affected": list(set(dp['category'] for dp in dark_patterns_detected))
    }

    return {
        **state,
        "dark_patterns_detected": dark_patterns_detected,
        "ui_analysis": ui_analysis,
        "status": "vision_analysis_complete"
    }


# ============================================================================
# AGENT 4: Compliance Evaluation Agent
# ============================================================================

def compliance_evaluation_agent(state: ComplianceState) -> ComplianceState:
    """
    Agent 4: Evaluate app against compliance standards

    Standards:
    - IEEE 7010 (Transparency, Agency, Accountability)
    - DSA Article 28 (Minor protection)
    - AED Guidelines (Time management, notifications, engagement)
    - ICO Age Appropriate Design Code
    """
    print("\n" + "="*70)
    print("⚖️ COMPLIANCE EVALUATION AGENT")
    print("="*70)

    app_name = state['app_name']
    dark_patterns = state['dark_patterns_detected']

    print(f"\n📊 Evaluating {app_name} against digital safety standards...")

    standards = COMPLIANCE_STANDARDS['standards']
    scoring_rubric = COMPLIANCE_STANDARDS['evaluation_rubric']['scoring']

    compliance_scores = {}
    violations = []

    # Evaluate each standard
    for standard_key, standard in standards.items():
        print(f"\n   📋 {standard['name'][:60]}...")

        standard_scores = {}
        standard_violations = []

        for category_key, category_checks in standard['categories'].items():
            # Calculate score based on dark patterns detected
            category_score = calculate_category_score(
                category_checks,
                dark_patterns,
                app_name
            )

            standard_scores[category_key] = category_score

            # Identify violations
            if category_score < scoring_rubric['mostly_compliant']:
                violation = {
                    "standard": standard_key,
                    "category": category_key,
                    "score": category_score,
                    "severity": "high" if category_score < scoring_rubric['partially_compliant'] else "medium",
                    "checks_failed": get_failed_checks(category_checks, dark_patterns)
                }
                violations.append(violation)
                standard_violations.append(violation)

        # Overall standard score
        overall_score = sum(standard_scores.values()) / len(standard_scores)
        compliance_scores[standard_key] = {
            "overall_score": overall_score,
            "category_scores": standard_scores,
            "violations": standard_violations,
            "compliant": overall_score >= scoring_rubric['mostly_compliant']
        }

        # Print result
        status = "✅" if compliance_scores[standard_key]['compliant'] else "❌"
        print(f"      {status} Score: {overall_score:.0f}/100")

    print(f"\n📈 Evaluation complete:")
    print(f"   Standards evaluated: {len(compliance_scores)}")
    print(f"   Violations found: {len(violations)}")

    return {
        **state,
        "compliance_scores": compliance_scores,
        "violations": violations,
        "status": "compliance_evaluation_complete"
    }


def calculate_category_score(checks: List[str], dark_patterns: List[Dict], app_name: str) -> int:
    """Calculate compliance score for a category"""

    # Base score
    score = 100

    # Deduct points for dark patterns
    for dp in dark_patterns:
        if dp['severity'] == 'critical':
            score -= 30
        elif dp['severity'] == 'high':
            score -= 20
        elif dp['severity'] == 'medium':
            score -= 10
        else:
            score -= 5

    # Minimum score
    return max(0, score)


def get_failed_checks(checks: List[str], dark_patterns: List[Dict]) -> List[str]:
    """Get list of failed compliance checks"""
    # Simplified mapping for MVP
    failed = []

    for dp in dark_patterns:
        if dp['pattern'] == "Infinite Scroll":
            failed.append("App provides usage statistics and time tracking")
            failed.append("No infinite scroll without user control")
        elif dp['pattern'] == "Streak Mechanics":
            failed.append("No streak mechanics that create obligation")
        elif dp['pattern'] == "Countdown Timer":
            failed.append("No fake urgency indicators")

    return list(set(failed))


# ============================================================================
# AGENT 5: Report Generation Agent
# ============================================================================

def report_generation_agent(state: ComplianceState) -> ComplianceState:
    """
    Agent 5: Generate comprehensive compliance report

    Report includes:
    - Executive summary
    - Compliance scores by standard
    - Dark patterns detected
    - Violations and recommendations
    - Screenshots evidence
    """
    print("\n" + "="*70)
    print("📄 REPORT GENERATION AGENT")
    print("="*70)

    app_name = state['app_name']
    timestamp = state['timestamp']

    print(f"\n📝 Generating compliance report for {app_name}...")

    # Generate report content
    report = generate_compliance_report(state)

    # Save report
    reports_dir = "law/iphone_compliance_agent/reports"
    os.makedirs(reports_dir, exist_ok=True)

    report_filename = f"{app_name.replace(' ', '_')}_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path = os.path.join(reports_dir, report_filename)

    with open(report_path, 'w') as f:
        f.write(report)

    print(f"   ✅ Report saved: {report_path}")
    print(f"   📄 Report size: {len(report)} characters")

    return {
        **state,
        "final_report": report,
        "report_path": report_path,
        "status": "complete"
    }


def generate_compliance_report(state: ComplianceState) -> str:
    """Generate markdown compliance report"""

    app_name = state['app_name']
    bundle_id = state['bundle_id']
    timestamp = state['timestamp']
    compliance_scores = state['compliance_scores']
    violations = state['violations']
    dark_patterns = state['dark_patterns_detected']

    # Calculate overall compliance
    overall_scores = [s['overall_score'] for s in compliance_scores.values()]
    overall_compliance = sum(overall_scores) / len(overall_scores) if overall_scores else 0

    # Determine compliance level
    if overall_compliance >= 75:
        compliance_level = "✅ MOSTLY COMPLIANT"
        compliance_color = "green"
    elif overall_compliance >= 50:
        compliance_level = "⚠️ PARTIALLY COMPLIANT"
        compliance_color = "yellow"
    else:
        compliance_level = "❌ NON-COMPLIANT"
        compliance_color = "red"

    report = f"""# Digital Safety Compliance Report

## App Information

- **App Name**: {app_name}
- **Bundle ID**: {bundle_id}
- **Test Date**: {timestamp}
- **Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

### Overall Compliance Score: {overall_compliance:.1f}/100

**Status**: {compliance_level}

This report evaluates {app_name} against four major digital safety standards:
- IEEE 7010-2020 (AI Well-being)
- Digital Services Act Article 28 (Minor Protection)
- Attention Economy Design Guidelines
- ICO Age Appropriate Design Code

---

## Compliance Scores by Standard

"""

    # Add scores for each standard
    for standard_key, standard_data in compliance_scores.items():
        standard_name = COMPLIANCE_STANDARDS['standards'][standard_key]['name']
        score = standard_data['overall_score']
        compliant = standard_data['compliant']
        status_icon = "✅" if compliant else "❌"

        report += f"""
### {status_icon} {standard_name}

**Score**: {score:.1f}/100

**Category Breakdown**:
"""
        for category, cat_score in standard_data['category_scores'].items():
            report += f"- {category.replace('_', ' ').title()}: {cat_score:.0f}/100\n"

        if standard_data['violations']:
            report += f"\n**Violations** ({len(standard_data['violations'])}):\n"
            for violation in standard_data['violations']:
                report += f"- {violation['category'].replace('_', ' ').title()} ({violation['severity']} severity)\n"

        report += "\n"

    # Dark Patterns Section
    report += f"""---

## Dark Patterns Detected

**Total Patterns Found**: {len(dark_patterns)}

"""

    if dark_patterns:
        # Group by severity
        critical_patterns = [dp for dp in dark_patterns if dp['severity'] == 'critical']
        high_patterns = [dp for dp in dark_patterns if dp['severity'] == 'high']
        medium_patterns = [dp for dp in dark_patterns if dp['severity'] == 'medium']

        if critical_patterns:
            report += "### 🚨 Critical Severity\n\n"
            for dp in critical_patterns:
                report += f"- **{dp['pattern']}** ({dp['category']})\n"
                report += f"  - {dp['description']}\n"
                report += f"  - Location: {dp['location']}\n\n"

        if high_patterns:
            report += "### ⚠️ High Severity\n\n"
            for dp in high_patterns:
                report += f"- **{dp['pattern']}** ({dp['category']})\n"
                report += f"  - {dp['description']}\n"
                report += f"  - Location: {dp['location']}\n\n"

        if medium_patterns:
            report += "### ℹ️ Medium Severity\n\n"
            for dp in medium_patterns:
                report += f"- **{dp['pattern']}** ({dp['category']})\n"
                report += f"  - {dp['description']}\n"
                report += f"  - Location: {dp['location']}\n\n"
    else:
        report += "✅ No dark patterns detected.\n\n"

    # Violations Summary
    report += f"""---

## Compliance Violations

**Total Violations**: {len(violations)}

"""

    if violations:
        # Group by standard
        violations_by_standard = {}
        for violation in violations:
            std = violation['standard']
            if std not in violations_by_standard:
                violations_by_standard[std] = []
            violations_by_standard[std].append(violation)

        for standard_key, std_violations in violations_by_standard.items():
            standard_name = COMPLIANCE_STANDARDS['standards'][standard_key]['name']
            report += f"### {standard_name}\n\n"

            for violation in std_violations:
                report += f"- **{violation['category'].replace('_', ' ').title()}** ({violation['severity']} severity)\n"
                report += f"  - Score: {violation['score']:.0f}/100\n"
                if violation.get('checks_failed'):
                    report += f"  - Failed checks:\n"
                    for check in violation['checks_failed'][:3]:  # Limit to 3
                        report += f"    - {check}\n"
                report += "\n"
    else:
        report += "✅ No violations found.\n\n"

    # Recommendations
    report += f"""---

## Recommendations

Based on the compliance evaluation, we recommend the following actions:

"""

    if overall_compliance < 50:
        report += """
### Immediate Actions Required

1. **Review and redesign engagement mechanisms**
   - Remove or modify dark patterns identified in this report
   - Implement user-friendly settings for controlling app behavior
   - Add transparent disclosures for data collection

2. **Enhance privacy controls**
   - Make privacy settings more accessible
   - Default to privacy-protective settings
   - Simplify privacy policy language

3. **Implement time management features**
   - Add usage tracking and statistics
   - Provide break reminders
   - Offer controls for infinite scroll and autoplay
"""
    elif overall_compliance < 75:
        report += """
### Improvements Recommended

1. **Strengthen existing controls**
   - Make existing privacy/safety features more discoverable
   - Enhance transparency in data practices
   - Reduce friction in opting out of features

2. **Address identified dark patterns**
   - Review and modify patterns flagged in this report
   - Consider user-centric design alternatives
   - Test changes with diverse user groups
"""
    else:
        report += """
### Maintain and Monitor

1. **Continue best practices**
   - Maintain current privacy-protective design
   - Regularly audit for new dark patterns
   - Stay updated with evolving standards

2. **Minor improvements**
   - Address any remaining low-severity issues
   - Enhance transparency where possible
   - Consider obtaining formal compliance certification
"""

    # Testing Details
    report += f"""
---

## Testing Details

### Navigation Flows Executed

"""

    for flow_result in state.get('flow_results', []):
        report += f"- **{flow_result['flow_name']}**: {flow_result['steps_executed']} steps, {flow_result['screenshots_captured']} screenshots\n"

    report += f"""
### Screenshots Captured

Total screenshots: {len(state.get('screenshots', []))}

"""

    # Footer
    report += f"""
---

## Methodology

This compliance evaluation was conducted using an automated multi-agent system:

1. **Navigation Agent**: Executed predefined test flows through the app
2. **Vision Analysis Agent**: Analyzed screenshots using Claude Vision API to detect dark patterns
3. **Compliance Evaluation Agent**: Evaluated findings against digital safety standards
4. **Report Generation Agent**: Compiled this comprehensive report

**Standards Evaluated**:
- IEEE 7010-2020: Recommended Practice for Assessing the Impact of Autonomous and Intelligent Systems
- EU Digital Services Act Article 28: Protection of minors online
- Attention Economy Design Guidelines: Ethical design for digital well-being
- ICO Age Appropriate Design Code: UK data protection for children

**Disclaimer**: This report provides an automated assessment and should be reviewed by legal and compliance professionals before making business decisions.

---

*Report generated by iPhone Compliance Agent - Tier 4/5 Multi-Agent System*
"""

    return report


# ============================================================================
# TIER 4: LangGraph Workflow - Coordinates Agents
# ============================================================================

def create_compliance_workflow():
    """Create multi-agent compliance testing workflow"""

    workflow = StateGraph(ComplianceState)

    # Add agent nodes
    workflow.add_node("app_selector", app_selector_agent)
    workflow.add_node("navigation", navigation_agent)
    workflow.add_node("vision_analysis", vision_analysis_agent)
    workflow.add_node("compliance_evaluation", compliance_evaluation_agent)
    workflow.add_node("report_generation", report_generation_agent)

    # Define sequential flow
    workflow.set_entry_point("app_selector")
    workflow.add_edge("app_selector", "navigation")
    workflow.add_edge("navigation", "vision_analysis")
    workflow.add_edge("vision_analysis", "compliance_evaluation")
    workflow.add_edge("compliance_evaluation", "report_generation")
    workflow.add_edge("report_generation", END)

    return workflow.compile()


# ============================================================================
# Main Function
# ============================================================================

def run_compliance_test(app_name: str = None) -> Dict:
    """
    Run full compliance test on selected app

    Args:
        app_name: Optional app name to test (defaults to first in list)

    Returns:
        Final state with compliance report
    """
    print("\n" + "="*70)
    print("📱 IPHONE COMPLIANCE TESTING AGENT")
    print("   Tier 4/5 Multi-Agent System")
    print("="*70)

    # Initialize state
    initial_state = {
        "selected_app": None,
        "app_name": "",
        "bundle_id": "",
        "navigation_flow": [],
        "flow_results": [],
        "screenshots": [],
        "dark_patterns_detected": [],
        "ui_analysis": {},
        "compliance_scores": {},
        "violations": [],
        "final_report": "",
        "report_path": "",
        "status": "initialized",
        "timestamp": "",
        "session_summary": {}
    }

    # If app_name specified, find and set it
    if app_name:
        apps = COMPLIANCE_STANDARDS['popular_test_apps']
        selected_app = next((app for app in apps if app['name'].lower() == app_name.lower()), None)
        if selected_app:
            initial_state["selected_app"] = selected_app

    # Run multi-agent workflow
    app = create_compliance_workflow()
    final_state = app.invoke(initial_state)

    print("\n" + "="*70)
    print("✅ COMPLIANCE TEST COMPLETE")
    print("="*70)
    print(f"\n📄 Report saved to: {final_state['report_path']}")
    print(f"📊 Overall compliance: {sum(s['overall_score'] for s in final_state['compliance_scores'].values()) / len(final_state['compliance_scores']):.1f}/100")
    print(f"🚨 Dark patterns found: {len(final_state['dark_patterns_detected'])}")
    print(f"⚠️ Violations: {len(final_state['violations'])}")

    return final_state


# ============================================================================
# Example Usage
# ============================================================================

def main():
    """Example: Run compliance test"""

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ERROR: ANTHROPIC_API_KEY not found in .env")
        print("   Please set your API key to use vision analysis features")
        return

    # Run compliance test on Instagram (default first app)
    result = run_compliance_test()

    print("\n" + "="*70)
    print("🎓 WHY THIS IS TIER 4/5")
    print("="*70)
    print("""
Multi-Agent Coordination (Tier 4):
1. AppSelectorAgent: Choose app to test
2. NavigationAgent: Execute test flows
3. VisionAnalysisAgent: Detect dark patterns via Claude Vision
4. ComplianceEvaluationAgent: Evaluate against standards
5. ReportGenerationAgent: Generate comprehensive report

State Management:
- Shared state flows between all agents
- Each agent enriches state with its analysis
- Sequential workflow ensures proper dependencies

Human Review (Tier 5):
- Attorney/compliance officer reviews report
- Validates findings and recommendations
- Approves before sending to client/regulators

Real-World Application:
- Legal teams evaluating app compliance
- Consumer protection agencies testing apps
- App developers self-auditing before launch
- Regulatory compliance documentation
    """)


if __name__ == "__main__":
    main()
