# LangGraph - Core Concepts Guide

This guide explains the 10 core concepts that give you maximum power when using LangGraph. Each concept includes a brief explanation and how it fits into your stateful agent workflow development.

---

## Beginner Concepts

### 1. Nodes & Edges (Graph Structure)
**What it is:** The building blocks of LangGraph where nodes are functions that process state and edges define how execution flows between nodes.

**Role in the system:** LangGraph models workflows as directed graphs instead of linear chains. Each node does one thing (call LLM, run tool, transform data), and edges connect them to create the flow. This lets you visualize complex workflows, understand execution paths, and modify logic by rearranging nodes. Unlike simple chains, graphs can loop back, branch, and create cycles, enabling iterative agent behaviors.

### 2. State Management
**What it is:** A typed schema that defines what data flows through your graph, gets updated by nodes, and persists across execution steps.

**Role in the system:** State is the shared memory that every node reads from and writes to. You define a state class (e.g., `messages`, `current_step`, `documents`) and LangGraph ensures it's available everywhere. Nodes modify state, and the graph automatically propagates changes to downstream nodes. This eliminates passing variables manually and provides a single source of truth for workflow data, making complex multi-step processes manageable.

### 3. Message Passing & MessageGraph
**What it is:** A specialized graph type where state is a list of messages (user/AI/system), optimized for conversational agents.

**Role in the system:** Many agent workflows revolve around conversations. MessageGraph simplifies this by treating state as a message history automatically. Nodes add messages, and LangGraph handles appending to the list. This pattern fits perfectly with chat models and tool calling, where you need to maintain conversation context while the agent reasons through multi-step tasks. It's the foundation for building conversational AI that remembers context.

### 4. Conditional Routing & Dynamic Edges
**What it is:** Logic that determines which node to execute next based on the current state, enabling branching workflows.

**Role in the system:** Not all paths are predetermined—agents need to make decisions. Conditional edges let you define routing functions that examine state and choose the next node (e.g., "if error, go to retry node; else continue"). This creates adaptive workflows that respond to results, handle different cases, and implement decision trees. It's what separates static pipelines from intelligent agents that adjust behavior dynamically.

---

## Professional Concepts

### 5. Checkpoints & Persistence
**What it is:** Automatic saving of graph state at each step, allowing you to pause execution, resume later, or replay from any point.

**Role in the system:** Long-running agent workflows can't rely on in-memory state—they need durability. LangGraph checkpoints state to databases (Postgres, SQLite) after each node execution. If the process crashes or you want to pause for human input, you can resume exactly where you left off. This enables multi-session agents, fault tolerance, and debugging by replaying from specific checkpoints to investigate failures.

### 6. Human-in-the-Loop Interrupts
**What it is:** Pausing graph execution at designated points to wait for human approval, input, or correction before continuing.

**Role in the system:** Fully autonomous agents are risky—sometimes you need human oversight. Interrupt nodes pause execution and save state, returning control to your application. You can show the user what the agent plans to do, wait for approval, let them edit the plan, then resume with modified state. This creates supervised agents for high-stakes workflows (deployments, financial transactions) where human judgment is required at critical decision points.

### 7. Node-Level Tool Calling
**What it is:** Giving individual nodes in your graph the ability to call external tools and incorporate results into the workflow.

**Role in the system:** Instead of one agent with all tools, you can create specialized nodes that each have specific tools. For example, a "research" node calls search APIs, a "code" node runs code interpreters, and an "analysis" node queries databases. This modular approach lets you control which tools are available at which stages, implement security boundaries (only certain nodes can access sensitive tools), and create more maintainable multi-step agent architectures.

---

## Master Concepts

### 8. Multi-Agent Orchestration
**What it is:** Coordinating multiple specialized agents (each a subgraph) that collaborate, delegate tasks, and combine results.

**Role in the system:** Complex problems need specialized expertise. Multi-agent systems create separate agents for different domains (researcher, coder, reviewer), each with their own graph, tools, and prompts. A supervisor agent routes tasks to specialists, aggregates results, and manages the overall workflow. LangGraph makes this possible by composing graphs within graphs, enabling hierarchical agent systems where each agent focuses on what it does best.

### 9. State Reducers & Memory Systems
**What it is:** Custom functions that control how state updates are merged when multiple nodes modify the same field, enabling sophisticated memory patterns.

**Role in the system:** Default state merging overwrites values, but complex agents need smarter memory. Reducers let you define custom merge logic: append to lists, update specific keys in dicts, accumulate scores, or implement sliding windows that keep recent history. This creates memory systems that summarize conversations when they get too long, track entities mentioned across turns, or maintain priorities lists that nodes can add to without conflicts.

### 10. Streaming & Partial State Updates
**What it is:** Receiving real-time updates as nodes execute and state changes, rather than waiting for the entire graph to complete.

**Role in the system:** Long-running agent graphs take time—users need progress feedback. Streaming emits state updates after each node execution, letting you show live progress in UIs, log intermediate results, or make decisions before completion. You can stream individual node outputs, state snapshots, or token-level LLM responses. This creates responsive agent experiences and enables monitoring dashboards that track agent reasoning in real time.

---

## How to Use This Guide

1. **Beginners:** Learn graph structure, state management, and basic routing to build stateful workflows
2. **Professionals:** Add checkpoints, human-in-the-loop, and modular tool calling for production reliability
3. **Masters:** Orchestrate multi-agent systems with custom memory and streaming for enterprise-scale applications

Each concept folder (beginner/professional/master) contains practical examples showing these concepts in action.
