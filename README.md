# Generalized Automation Architecture: "The Agentic Workforce"

## Architecture Overview

This is a **tiered automation hierarchy** with Claude Code as the orchestration brain, managing complexity levels from simple deterministic shortcuts to fully autonomous multi-agent systems.

---

## 1. The Automation Hierarchy (7 Tiers)

### Tier 0: Simple Triggers
- **Tools**: iOS Shortcuts, Keyboard Maestro macros
- **Use Cases**: One-step actions, simple data capture, quick launchers
- **Example**: "Save this thought to Obsidian inbox", "Toggle Do Not Disturb"
- **Orchestration**: Direct triggers, no Claude Code involvement

### Tier 1: Deterministic Workflows
- **Tools**: n8n workflows, iOS Automation chains
- **Use Cases**: Multi-step but predictable sequences, scheduled tasks, webhooks
- **Example**: "Every morning, compile my daily brief from calendar + tasks", "When email arrives with invoice, extract data and log to spreadsheet"
- **Orchestration**: n8n handles execution, Claude Code designs/modifies workflows

### Tier 2: Context-Aware Workflows
- **Tools**: n8n + LLM API calls (ChatGPT/Claude), NotebookLM for context
- **Use Cases**: Workflows that need light reasoning or context retrieval
- **Example**: "Summarize meeting notes and categorize by project", "Draft email response based on conversation history"
- **Orchestration**: n8n orchestrates, embeds LLM calls for decisions, Claude Code monitors

### Tier 3: Single-Purpose Agents
- **Tools**: LangChain agents with tools, RAG systems
- **Use Cases**: Focused autonomous tasks with tool use and retrieval
- **Example**: "Research competitor pricing and update our strategy doc", "Find all UE5 tutorials about procedural materials and summarize"
- **Orchestration**: Claude Code spawns and monitors single agents, stores results

### Tier 4: Multi-Agent Collaboration
- **Tools**: LangGraph orchestration, multiple LangChain agents
- **Use Cases**: Complex tasks requiring specialized roles working together
- **Example**: "Plan Q1 marketing campaign" (researcher + writer + analyst agents), "Generate game asset set" (concept artist + 3D modeler + texture artist agents)
- **Orchestration**: Claude Code designs agent graph, LangGraph executes, results synced to state store

### Tier 5: Recursive Task Decomposition
- **Tools**: Claude Code subagents + LangGraph + full tool stack
- **Use Cases**: Open-ended projects that require planning, execution, and adaptation
- **Example**: "Build complete sales enablement system", "Create procedural city generation system for game"
- **Orchestration**: Claude Code recursively breaks down tasks, spawns appropriate tier for each subtask

### Tier 6: Autonomous Domain Specialists
- **Tools**: Full stack orchestrated by Claude Code with domain-specific memory/context
- **Use Cases**: Ongoing autonomous management of entire functional areas
- **Example**: "Autonomous RevOps agent managing pipeline health", "Autonomous game asset pipeline maintaining style consistency"
- **Orchestration**: Claude Code manages long-running agents with persistent memory and decision authority

---

## 2. Intake Process: "The Classifier"

```
┌─────────────────────────────────────────────────┐
│  Task Input (via Claude Code CLI)              │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  AI Intake Agent (LangChain)                    │
│  - Analyzes task complexity                     │
│  - Checks for existing automations              │
│  - Suggests tier + reasoning                    │
│  - Estimates resource requirements              │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  Human Approval Gate (You via CLI)             │
│  - Review AI suggestion                         │
│  - Override tier if needed                      │
│  - Approve execution                            │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  Execution Router                               │
│  - Initializes appropriate tier                │
│  - Sets up monitoring/logging                   │
│  - Provisions state storage                    │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  Tier Execution with State Tracking            │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  Results & Learning                             │
│  - Store to Postgres + Obsidian                │
│  - Update automation library                    │
│  - Suggest reusable patterns                    │
└─────────────────────────────────────────────────┘
```

---

## 3. State Management Architecture

### PostgreSQL Database
**Schema**:
- `tasks` - All automation tasks with metadata
- `executions` - Execution logs and status
- `agents` - Active and historical agent instances
- `knowledge` - Structured data for RAG retrieval
- `domain_config` - Domain-specific settings (gtm, ue5, br2)

### Obsidian Vault Structure
```
/automation-system/
  /inbox/              # Quick capture, unprocessed tasks
  /tasks/              # Active task tracking with status
  /logs/               # Human-readable execution logs
  /patterns/           # Reusable automation patterns
  /domains/
    /gtm/              # GTM-specific knowledge
    /ue5/              # Game dev knowledge
    /br2/              # PKM system knowledge
  /agents/             # Agent configurations and memories
```

### Sync Mechanism
- Claude Code maintains bidirectional sync
- Postgres = structured queries, fast retrieval, relationships
- Obsidian = human review, context building, planning
- Updates in either system trigger sync

---

## 4. Core Components for MVP

### Component 1: Claude Code Orchestrator
- CLI interface for task submission
- Intake classifier integration
- Tier routing logic
- State management coordination
- Subagent spawning system

### Component 2: Intake Classifier Agent
- LangChain agent with decision-making tools
- Access to automation pattern library
- Complexity scoring algorithm
- Human-readable reasoning output

### Component 3: State Management Layer
- PostgreSQL schema setup
- Obsidian vault structure
- Sync service (Python/TypeScript)
- API for tier components to access state

### Component 4: Tier Implementations (MVP scope: Tiers 0-3)
- Tier 0: Document iOS Shortcut templates
- Tier 1: n8n workflow templates library
- Tier 2: n8n + LLM call patterns
- Tier 3: LangChain agent framework + tools

### Component 5: Monitoring & Observability
- Execution logging system
- Dashboard for active tasks (CLI-based initially)
- Error handling and retry logic
- Cost tracking for LLM usage

---

## 5. MVP Project Spec

### Scope
Build a functional Tier 0-3 automation system with:
- Claude Code CLI for task intake
- AI-powered classifier with human approval
- PostgreSQL + Obsidian state management
- Ability to execute iOS Shortcuts, n8n workflows, and single LangChain agents
- Basic monitoring and logging

### Out of Scope for MVP
- Tiers 4-6 (multi-agent, recursive, autonomous)
- Domain-specific specializations (gtm/ue5/br2)
- Advanced UI/dashboard
- Full bidirectional Obsidian sync (read-only for MVP)

### Success Criteria
1. Submit task via Claude Code CLI
2. AI suggests tier with reasoning
3. User approves/overrides
4. System executes appropriate automation
5. Results stored in Postgres + Obsidian
6. User can query task status and history

---

## 6. Technology Stack Mapping

| Component | Primary Tool | Supporting Tools |
|-----------|-------------|------------------|
| Orchestration Layer | Claude Code | Python scripts |
| Intake Classification | LangChain | ChatGPT API |
| Workflow Execution | n8n | - |
| Single Agents | LangChain | ChatGPT/Claude API |
| Multi-Agent (future) | LangGraph | - |
| Knowledge Management | Obsidian | NotebookLM |
| State Storage | PostgreSQL | - |
| Mobile Triggers | iOS Shortcuts | iOS Automations |
| Desktop Triggers | Keyboard Maestro | - |

---

## 7. Implementation Phases

### Phase 1: Foundation (Week 1-2)
- PostgreSQL schema design & setup
- Obsidian vault structure
- Basic Claude Code CLI interface
- Simple task model

### Phase 2: Classifier (Week 2-3)
- Build intake classifier agent
- Tier decision logic
- Human approval gate
- Routing mechanism

### Phase 3: Tier Execution (Week 3-5)
- Tier 0: iOS Shortcuts templates
- Tier 1: n8n workflow library + triggers
- Tier 2: n8n + LLM patterns
- Tier 3: LangChain agent framework

### Phase 4: State & Monitoring (Week 5-6)
- Sync service between Postgres & Obsidian
- Logging system
- Status dashboard (CLI)
- Error handling

### Phase 5: Testing & Refinement (Week 6-7)
- End-to-end test cases
- Performance optimization
- Documentation
- Prepare for domain specialization

---

## Key Architectural Insights

### 1. Tiered Complexity Model
The 7-tier hierarchy mirrors how humans think about automation: from "just click this button" to "autonomously run my marketing ops." This maps cognitive load to system capability.

### 2. Claude Code as Orchestrator
Unlike traditional automation where tools are peers, Claude Code's ability to spawn subagents and reason about tasks makes it uniquely suited to sit atop the hierarchy, deciding which tier fits each task.

### 3. Hybrid State
Postgres gives you queryability and performance for runtime operations, while Obsidian gives you the knowledge graph, context, and human-reviewable audit trail. The sync layer bridges the machine-optimized and human-optimized representations.

### 4. Approval Gate
The hybrid AI-suggests, human-approves pattern prevents runaway automation while building your intuition for tier classification. Over time, you'll develop pattern recognition.

### 5. Tier 3 as MVP Ceiling
Single-purpose agents with tools represent the inflection point where automation becomes "smart enough" for most tasks, but doesn't require complex LangGraph orchestration. Perfect MVP scope.

---

## Domain Specializations (Future)

### GTM (Go-to-Market for B2B SaaS)
- Marketing ops automation
- Sales ops automation
- CX ops automation
- Revenue operations

### UE5 (Unreal Engine 5 Game Development)
- Asset creation automation
- C++ development assistance
- Blueprint automation
- Sequencer and materials workflow

### BR2 (Second Brain / PKM)
- Knowledge management automation
- AI-powered note organization
- Thiago Forte PARA method implementation
- Context-aware retrieval

---

## Tool Stack
- **Claude Code** (primary operating system/orchestrator)
- **n8n** (workflow automation)
- **LangChain** (agent framework)
- **LangGraph** (multi-agent orchestration)
- **Keyboard Maestro** (desktop automation)
- **iOS Shortcuts/Automations** (mobile triggers)
- **iOS Accessibility Features** (advanced mobile automation)
- **ChatGPT** (LLM provider)
- **NotebookLM** (context/knowledge)
- **Obsidian** (second brain/knowledge management)
- **PostgreSQL** (state storage)
