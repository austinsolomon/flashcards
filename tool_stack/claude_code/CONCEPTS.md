# Claude Code - Core Concepts Guide

This guide explains the 10 core concepts that give you maximum power when using Claude Code. Each concept includes a brief explanation and how it fits into your development workflow.

---

## Beginner Concepts

### 1. Slash Commands
**What it is:** Custom shortcuts that trigger predefined workflows when you type `/command-name` in Claude Code.

**Role in the system:** Slash commands turn repetitive tasks into single commands, like `/test` to run tests or `/commit` to create git commits. You create them by adding markdown files to `.claude/commands/` folder, and Claude executes the instructions when you invoke the command. This makes common operations faster and more consistent across your team.

### 2. Hooks
**What it is:** Automated scripts that run automatically when specific events happen in Claude Code, like before submitting a prompt or after Claude uses a tool.

**Role in the system:** Hooks let you add validation, formatting, or checks at key moments without manual intervention. For example, a hook can verify git status is clean before Claude makes changes, or auto-format code after edits. You configure them in `.claude/hooks/` and they act as guardrails and automations in your workflow.

### 3. Tools (Read, Write, Edit, Bash)
**What it is:** The basic operations Claude uses to interact with your filesystem and execute commands.

**Role in the system:** Tools are Claude's hands and eyes in your codebase. When you ask Claude to modify code, it uses Read to examine files, Edit to change them, and Write to create new ones. Bash lets Claude run terminal commands. Understanding which tool Claude should use helps you guide it to work more efficiently with your code.

### 4. Context Engineering
**What it is:** Providing Claude with the right information at the right time so it understands your codebase and makes better decisions.

**Role in the system:** Claude works best when it knows what files exist, what patterns your code uses, and what constraints matter. You can point Claude to specific files, ask it to search the codebase first, or provide architecture context upfront. Good context means fewer mistakes and faster solutions because Claude understands your project's structure.

---

## Professional Concepts

### 5. Agents & Subagents
**What it is:** Autonomous processes that Claude launches to handle complex tasks independently, breaking down problems and executing multiple steps without constant guidance.

**Role in the system:** When a task requires many steps or exploration (like "find all type errors and fix them"), Claude can launch a specialized agent with specific tools and goals. Subagents run in parallel or handle subtasks. This delegation model lets you describe what you want accomplished rather than prescribing every step, and Claude orchestrates the work.

### 6. Model Context Protocol (MCP)
**What it is:** A standardized way to extend Claude Code with custom tools, data sources, and integrations that Claude can use during sessions.

**Role in the system:** MCP servers add capabilities beyond Claude's built-in tools, like database access, API integrations, or specialized analysis tools. You configure MCP servers in your settings, and Claude automatically has access to these tools when relevant. This turns Claude into a customizable development environment tailored to your stack.

### 7. Plan Mode
**What it is:** A workflow where Claude first creates a detailed implementation plan for your review before executing any changes.

**Role in the system:** Plan mode helps with complex features or risky changes by separating planning from execution. Claude analyzes requirements, proposes steps, and waits for your approval. You can refine the plan, ask questions, or adjust the approach before any code is written. This prevents Claude from going down wrong paths and ensures alignment on the solution.

---

## Master Concepts

### 8. Agent Patterns & Orchestration
**What it is:** Advanced techniques for designing multi-agent workflows where specialized agents collaborate, handle errors, and adapt to changing conditions.

**Role in the system:** Complex automation requires agents that retry on failure, pass context between steps, and make intelligent decisions about what to do next. Master patterns include supervisor agents that coordinate workers, fallback strategies when tools fail, and state management across long-running processes. These patterns enable building production-grade automation that runs reliably.

### 9. Skills (Custom Reusable Components)
**What it is:** Pre-packaged workflows that can be invoked like tools, combining prompts, commands, and logic into reusable modules.

**Role in the system:** Skills are more powerful than slash commands—they can contain complex logic, conditional behavior, and multi-step processes. You install skills into `.claude/skills/` and they become part of Claude's toolkit. For example, a "deployment" skill might check tests, build, and deploy with rollback logic. Skills let you build a library of domain-specific operations.

### 10. SDK Integration & Programmatic Control
**What it is:** Using the Claude Code SDK to embed Claude's capabilities into your own scripts, CI/CD pipelines, or automation systems.

**Role in the system:** The SDK lets you trigger Claude programmatically from Node.js, Python, or other environments. You can run Claude sessions in CI to auto-fix issues, generate code during builds, or create custom tooling that leverages Claude's reasoning. This bridges Claude Code with your broader development infrastructure, enabling Claude to work as part of automated systems beyond interactive sessions.

---

## How to Use This Guide

1. **Beginners:** Start with slash commands and hooks to automate repetitive tasks
2. **Professionals:** Learn agents and MCP to handle complex, multi-step workflows
3. **Masters:** Combine skills, SDK, and agent patterns to build production automation systems

Each concept folder (beginner/professional/master) contains practical examples showing these concepts in action.
