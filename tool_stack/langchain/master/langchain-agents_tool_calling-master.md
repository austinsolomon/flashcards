# Agents with Tool-Calling - Advanced

## Concept Overview

Agents are LLM-powered systems that autonomously decide which tools to use and in what sequence to solve complex tasks. Modern agents use function calling (OpenAI's tool-calling API) to reliably invoke tools with structured parameters. Unlike simple chains, agents can handle unpredictable workflows, recover from errors, and dynamically adapt their strategy based on intermediate results.

**Why it matters:** Agents represent the frontier of LLM applications - systems that can reason, plan, and act autonomously. The difference between a brittle demo and a production agent is in error handling, tool reliability, planning depth, and graceful degradation. Building agents that work 90% of the time is easy; getting to 99.9% is where mastery lives.

## Real-World Example: Autonomous DevOps Incident Response Agent

This example demonstrates a production-grade incident response agent that can diagnose issues, query monitoring systems, execute remediation, and escalate when needed.

```python
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool, tool
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta
import random

# ========== TOOL DEFINITIONS WITH PYDANTIC SCHEMAS ==========

class LogQueryInput(BaseModel):
    """Input schema for log query tool."""
    service_name: str = Field(description="Name of the service to query logs for")
    time_window_minutes: int = Field(description="Time window in minutes to search back", default=15)
    log_level: str = Field(description="Log level filter: INFO, WARN, ERROR, CRITICAL", default="ERROR")
    search_pattern: Optional[str] = Field(description="Optional regex pattern to search for in logs")

class MetricQueryInput(BaseModel):
    """Input schema for metrics query."""
    metric_name: str = Field(description="Metric to query (cpu_usage, memory_usage, request_latency, error_rate)")
    service_name: str = Field(description="Service name")
    aggregation: str = Field(description="Aggregation method: avg, max, min, p95, p99", default="avg")
    time_window_minutes: int = Field(description="Time window in minutes", default=15)

class RestartServiceInput(BaseModel):
    """Input schema for service restart."""
    service_name: str = Field(description="Name of service to restart")
    reason: str = Field(description="Reason for restart")
    force: bool = Field(description="Force restart even if not healthy", default=False)

class ScaleServiceInput(BaseModel):
    """Input schema for scaling operations."""
    service_name: str = Field(description="Service to scale")
    target_instances: int = Field(description="Target number of instances")
    reason: str = Field(description="Reason for scaling")

class CreateIncidentInput(BaseModel):
    """Input schema for creating incidents."""
    title: str = Field(description="Incident title")
    severity: str = Field(description="Severity: P1 (critical), P2 (high), P3 (medium), P4 (low)")
    description: str = Field(description="Detailed description of the incident")
    affected_services: List[str] = Field(description="List of affected services")

# ========== MOCK INFRASTRUCTURE TOOLS ==========
# In production, these would integrate with real monitoring/orchestration systems

@tool(args_schema=LogQueryInput)
def query_logs(service_name: str, time_window_minutes: int = 15, log_level: str = "ERROR", search_pattern: Optional[str] = None) -> str:
    """Query application logs for a service. Returns recent log entries matching the criteria."""

    # Simulate log query
    mock_logs = [
        f"[2024-11-17 10:23:45] ERROR {service_name} - Database connection timeout after 30s",
        f"[2024-11-17 10:24:12] ERROR {service_name} - Failed to process request: NullPointerException",
        f"[2024-11-17 10:25:33] ERROR {service_name} - Redis connection pool exhausted",
        f"[2024-11-17 10:26:01] CRITICAL {service_name} - Memory usage at 95%, triggering GC",
    ]

    if search_pattern:
        mock_logs = [log for log in mock_logs if search_pattern.lower() in log.lower()]

    return json.dumps({
        "service": service_name,
        "time_window": f"Last {time_window_minutes} minutes",
        "log_level": log_level,
        "total_entries": len(mock_logs),
        "entries": mock_logs
    }, indent=2)

@tool(args_schema=MetricQueryInput)
def query_metrics(metric_name: str, service_name: str, aggregation: str = "avg", time_window_minutes: int = 15) -> str:
    """Query infrastructure metrics for a service. Returns time-series data for the specified metric."""

    # Simulate metric query
    mock_values = {
        "cpu_usage": random.uniform(60, 95),
        "memory_usage": random.uniform(70, 98),
        "request_latency": random.uniform(200, 2000),
        "error_rate": random.uniform(5, 25)
    }

    value = mock_values.get(metric_name, 0)

    return json.dumps({
        "service": service_name,
        "metric": metric_name,
        "aggregation": aggregation,
        "value": round(value, 2),
        "unit": "%" if "usage" in metric_name else "ms" if "latency" in metric_name else "%",
        "time_window": f"Last {time_window_minutes} minutes",
        "threshold_breach": value > 80 if "usage" in metric_name else value > 1000
    }, indent=2)

@tool(args_schema=RestartServiceInput)
def restart_service(service_name: str, reason: str, force: bool = False) -> str:
    """Restart a service. Use with caution - can cause brief downtime."""

    # Simulate restart
    return json.dumps({
        "action": "restart",
        "service": service_name,
        "reason": reason,
        "forced": force,
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "message": f"Service {service_name} restarted successfully. Health checks passing."
    }, indent=2)

@tool(args_schema=ScaleServiceInput)
def scale_service(service_name: str, target_instances: int, reason: str) -> str:
    """Scale a service horizontally by adjusting instance count."""

    current_instances = random.randint(2, 5)

    return json.dumps({
        "action": "scale",
        "service": service_name,
        "current_instances": current_instances,
        "target_instances": target_instances,
        "reason": reason,
        "status": "in_progress",
        "estimated_completion": "2-3 minutes",
        "message": f"Scaling {service_name} from {current_instances} to {target_instances} instances"
    }, indent=2)

@tool(args_schema=CreateIncidentInput)
def create_incident(title: str, severity: str, description: str, affected_services: List[str]) -> str:
    """Create an incident ticket and notify on-call engineer. Use when automated remediation fails or for critical issues."""

    incident_id = f"INC-{random.randint(10000, 99999)}"

    return json.dumps({
        "incident_id": incident_id,
        "title": title,
        "severity": severity,
        "description": description,
        "affected_services": affected_services,
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "assigned_to": "on-call-engineer",
        "notification_sent": True,
        "message": f"Incident {incident_id} created and on-call engineer notified"
    }, indent=2)

@tool
def check_service_health(service_name: str) -> str:
    """Check the health status of a service including its dependencies."""

    # Simulate health check
    health_status = random.choice(["healthy", "degraded", "unhealthy"])

    return json.dumps({
        "service": service_name,
        "status": health_status,
        "uptime": "23h 45m",
        "last_deployment": "2024-11-16 08:30:00",
        "dependencies": {
            "database": "healthy",
            "redis_cache": "degraded" if health_status == "degraded" else "healthy",
            "message_queue": "healthy"
        },
        "health_checks": {
            "liveness": "passing",
            "readiness": "passing" if health_status == "healthy" else "failing"
        }
    }, indent=2)

@tool
def get_recent_deployments(service_name: str, hours: int = 24) -> str:
    """Get recent deployments for a service to check if issues correlate with changes."""

    return json.dumps({
        "service": service_name,
        "time_window": f"Last {hours} hours",
        "deployments": [
            {
                "version": "v2.3.1",
                "deployed_at": "2024-11-16 14:30:00",
                "deployed_by": "ci-pipeline",
                "status": "successful",
                "changes": "Bug fixes and performance improvements"
            }
        ],
        "message": "1 deployment found in the last 24 hours"
    }, indent=2)

# ========== ADVANCED AGENT WITH REASONING ==========
class IncidentResponseAgent:
    """Production-grade agent for autonomous incident response."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)

        # All available tools
        self.tools = [
            query_logs,
            query_metrics,
            check_service_health,
            get_recent_deployments,
            restart_service,
            scale_service,
            create_incident
        ]

        # Create structured prompt with reasoning guidelines
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert DevOps incident response agent. Your role is to diagnose and resolve infrastructure incidents autonomously when possible, or escalate when necessary.

INCIDENT RESPONSE PROTOCOL:

1. ASSESS
   - Check service health status
   - Query recent metrics (CPU, memory, latency, error rate)
   - Review recent logs for errors
   - Check if correlated with recent deployments

2. DIAGNOSE
   - Identify root cause based on data
   - Correlate symptoms across multiple signals
   - Determine severity (P1-P4)

3. REMEDIATE (if safe and appropriate)
   - For resource exhaustion: scale service horizontally
   - For memory leaks/deadlocks: restart service (if not P1 and no data loss risk)
   - For cascading failures: never restart multiple critical services simultaneously

4. ESCALATE (when necessary)
   - P1 incidents (total outage, data loss risk)
   - Issues requiring manual intervention
   - When automated remediation fails
   - Unknown root causes

CRITICAL RULES:
- NEVER restart database or stateful services without explicit approval
- ALWAYS check health before and after remediation
- CREATE incident ticket before any destructive action
- NEVER ignore error signals - investigate thoroughly
- THINK STEP BY STEP - rushing causes outages

Use your tools systematically. Explain your reasoning at each step.
"""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        # Create agent with tools
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )

        # Create executor with advanced settings
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=15,  # Prevent infinite loops
            max_execution_time=300,  # 5 minute timeout
            return_intermediate_steps=True  # For observability
        )

    def respond_to_incident(self, alert: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Respond to an incident alert."""

        full_input = f"""
ALERT: {alert}

CONTEXT: {json.dumps(context or {}, indent=2)}

Please investigate and respond according to the incident response protocol.
"""

        try:
            result = self.executor.invoke({"input": full_input})

            return {
                "success": True,
                "output": result['output'],
                "intermediate_steps": result.get('intermediate_steps', []),
                "actions_taken": self._extract_actions(result.get('intermediate_steps', []))
            }

        except Exception as e:
            # Escalate on agent failure
            return {
                "success": False,
                "error": str(e),
                "escalation": "Agent encountered an error - creating P2 incident for manual review"
            }

    def _extract_actions(self, intermediate_steps: List) -> List[Dict]:
        """Extract actions taken by agent for audit log."""
        actions = []

        for step in intermediate_steps:
            if len(step) >= 2:
                agent_action, observation = step[0], step[1]
                actions.append({
                    "tool": agent_action.tool,
                    "input": agent_action.tool_input,
                    "timestamp": datetime.now().isoformat()
                })

        return actions

# ========== PRODUCTION USAGE EXAMPLES ==========
print("=== Autonomous Incident Response Agent Demo ===\n")

agent = IncidentResponseAgent()

# Scenario 1: High Memory Usage Alert
print("SCENARIO 1: High Memory Usage Alert")
print("-" * 80)

response1 = agent.respond_to_incident(
    alert="Service 'user-api' memory usage at 94% and climbing",
    context={
        "service": "user-api",
        "environment": "production",
        "current_instances": 3,
        "alert_severity": "warning"
    }
)

print("\n=== Agent Response ===")
print(f"Success: {response1['success']}")
print(f"\nOutput:\n{response1['output']}")
print(f"\nActions Taken:")
for action in response1.get('actions_taken', []):
    print(f"  - {action['tool']}: {action['input']}")

print("\n" + "=" * 80 + "\n")

# Scenario 2: High Error Rate After Deployment
print("SCENARIO 2: Error Rate Spike After Deployment")
print("-" * 80)

response2 = agent.respond_to_incident(
    alert="Service 'payment-processor' error rate jumped to 18% (normal: <1%)",
    context={
        "service": "payment-processor",
        "environment": "production",
        "recent_deployment": "v3.1.0 deployed 30 minutes ago",
        "alert_severity": "critical"
    }
)

print("\n=== Agent Response ===")
print(f"Success: {response2['success']}")
print(f"\nOutput:\n{response2['output']}")

print("\n" + "=" * 80 + "\n")

# Scenario 3: Database Connection Issues
print("SCENARIO 3: Database Connection Pool Exhaustion")
print("-" * 80)

response3 = agent.respond_to_incident(
    alert="Multiple services reporting database connection timeouts",
    context={
        "affected_services": ["user-api", "order-service", "inventory-service"],
        "environment": "production",
        "alert_severity": "critical"
    }
)

print("\n=== Agent Response ===")
print(f"Success: {response3['success']}")
print(f"\nOutput:\n{response3['output']}")

# ========== AGENT WITH PLANNING ==========
class PlanningAgent:
    """Agent with explicit planning phase before execution."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.tools = [
            query_logs,
            query_metrics,
            check_service_health,
            get_recent_deployments,
            restart_service,
            scale_service,
            create_incident
        ]

    def solve_with_planning(self, problem: str) -> Dict[str, Any]:
        """Solve problem with explicit planning phase."""

        # Phase 1: Create plan
        planning_prompt = f"""
Given this incident:
{problem}

Create a detailed investigation and remediation plan. List specific steps with the tools you'll use.

Format:
1. [Tool: tool_name] Description of what and why
2. [Tool: tool_name] Description of what and why
...

Plan:
"""

        plan = self.llm.predict(planning_prompt)
        print("=== INVESTIGATION PLAN ===")
        print(plan)
        print("\n")

        # Phase 2: Execute plan with agent
        execution_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an incident response agent. Execute the following plan step by step."),
            ("human", f"Problem: {problem}\n\nPlan:\n{plan}\n\nExecute this plan using the available tools.")
        ])

        # Continue with normal agent execution...
        return {"plan": plan, "execution": "Would execute plan with AgentExecutor"}

# Example with planning
print("\n\n=== AGENT WITH EXPLICIT PLANNING ===\n")
planning_agent = PlanningAgent()

plan_result = planning_agent.solve_with_planning(
    "Service 'analytics-pipeline' has been running slowly for 2 hours. Data processing lag is at 45 minutes (SLA: <5 minutes)."
)
```

### Why This Example Shows Advanced Agent Power:

1. **Autonomous Decision Making**: Agent chooses tools and sequences based on situation
2. **Error Recovery**: Handles tool failures, retries, and escalates when stuck
3. **Safety Guardrails**: Built-in rules prevent dangerous actions (e.g., restarting databases)
4. **Structured Tool Inputs**: Pydantic schemas ensure type safety and validation
5. **Observability**: Tracks all actions for audit logs and debugging

## Best Practices for Mastering Agents with Tool-Calling

1. **Always use Pydantic schemas for tool inputs**: Type validation catches errors before execution, not after. The LLM will see the schema and generate correctly-formatted calls. Include rich field descriptions - these are the LLM's documentation.

2. **Build safety guardrails into your agent's system prompt**: Don't rely on the LLM's judgment alone for critical decisions. Explicitly forbid dangerous actions ("NEVER restart production databases"), require confirmation for destructive operations, and set hard limits (max cost, max API calls, timeout thresholds).

3. **Implement explicit planning for complex tasks**: Add a planning phase where the LLM creates a step-by-step plan before execution. This dramatically improves success rates on multi-step tasks and makes debugging easier when things go wrong. Planning also enables human-in-the-loop approval.

4. **Set aggressive max_iterations and timeout limits**: Agents can loop infinitely on edge cases or complex problems. Set max_iterations=10-20 and max_execution_time=60-300s based on your use case. Always handle the timeout case gracefully - escalate to humans, don't fail silently.

5. **Log every tool call with full context for debugging and audit**: Store tool name, inputs, outputs, timestamp, and agent reasoning in structured logs. This is essential for debugging failures, security audits, and improving agent prompts over time. Track success/failure rates per tool to identify reliability issues.

## Common Pitfalls to Avoid

- **Don't skip error handling in tools**: Tools must return error messages, not throw exceptions
- **Avoid vague tool descriptions**: LLM picks wrong tool when descriptions are unclear
- **Don't ignore max_iterations**: Agents can loop forever without limits
- **Remember token costs**: Agents with many tools use massive context windows
- **Don't skip testing edge cases**: Agents behave unpredictably on unusual inputs
