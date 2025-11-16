# automation_architecture
tiered automation architecture including voice dispatching, claude code orchestration, langgraph/langchain strategy, n8n execution, application storage.

## Applications

### GTM Automation

A multi-layered automation architecture for go-to-market processes with the following components:

#### a. Voice Dispatching Layer
Claude Code serves as the central router, accepting voice commands and routing requests through the automation pipeline.

#### b. Strategy Layer
LangGraph-based agent orchestration using LLMs with tools that dictate cyclic control flow and task deconstruction, breaking down complex automation requirements into manageable workflows.

#### c. Project Management Layer
A 1:1 mapping of agents to projects implemented as mini LangChain RAG applications. Each agent has a dedicated vector store containing specialized corpus and knowledge bases for their assigned product domain.

#### d. Deterministic + Workflow Layer
n8n serves as the execution engine, accepting formalized top-down commands from the strategy and routing layers. It executes sequential workflows across the application layer, including LLM nodes for intelligent routing, classification, and sentiment analysis tasks.

#### e. Application Layer

**Buy (External)**: Integration with young startups and third-party services that support core GTM tools.

**Buy/Native (Pre-built)**: Pre-built connectors for core tools, public APIs, and SFDC AppExchange applications enabling rapid integration.

**Build/Native (Open Source & Enterprise)**: Popular open source tools and core enterprise platforms form the foundation. Core tools include Hubspot, Marketo, Salesforce (SFDC), Gong, Outreach, LinkedIn, and ZoomInfo.

**Tool-Specific Automation**:
- **Salesforce (SFDC)**: Formulas, Flows, and APEX code
- **Gong**: Call trackers and playbooks
- **Outreach**: Trigger-based automation
- **Marketo/Hubspot**: Native workflow and automation engines
