# LangChain - Core Concepts Guide

This guide explains the 10 core concepts that give you maximum power when using LangChain. Each concept includes a brief explanation and how it fits into your AI application development workflow.

---

## Beginner Concepts

### 1. Chains (LCEL - LangChain Expression Language)
**What it is:** A way to connect LLM calls, data processing, and other operations into sequential workflows using a pipe-like syntax.

**Role in the system:** Chains are LangChain's fundamental building block for creating AI workflows. You connect prompts to models to parsers using the `|` operator, creating readable pipelines like `prompt | model | parser`. This replaces writing custom glue code and makes it easy to modify, test, and reuse parts of your AI application. Chains run in sequence but can also branch, making them the backbone of any LangChain application.

### 2. Prompts & Templates
**What it is:** Reusable text templates with variables that structure how you communicate with language models.

**Role in the system:** Instead of writing prompt strings everywhere, templates let you define prompts once with placeholders like `{user_input}` or `{context}`. You can version control prompts, swap them for different models, and maintain consistency across your application. LangChain provides prompt templates, few-shot templates, and chat templates. This separates prompt engineering from application logic, making both easier to improve.

### 3. Output Parsers
**What it is:** Tools that convert raw LLM text responses into structured data formats like JSON, lists, or custom objects.

**Role in the system:** LLMs return text, but your application needs structured data. Output parsers define the schema you want (e.g., "extract person name and age as JSON"), add formatting instructions to the prompt automatically, and parse the LLM's response into typed objects. This handles the messy work of getting reliable structured output from text models, with retry logic when parsing fails.

### 4. Document Loaders & Text Splitters
**What it is:** Components that read files (PDFs, web pages, databases) and split large documents into smaller chunks that fit in LLM context windows.

**Role in the system:** RAG (Retrieval Augmented Generation) applications need to work with documents bigger than what LLMs can process at once. Loaders import from 100+ sources (PDFs, websites, databases), while splitters intelligently chunk text by sentences, paragraphs, or code structure. This preprocessing pipeline turns raw data into LLM-ready pieces while preserving semantic meaning, enabling you to build knowledge bases and Q&A systems.

---

## Professional Concepts

### 5. Retrieval & Vector Stores
**What it is:** Systems that convert text into numerical vectors, store them in specialized databases, and find similar content based on semantic meaning.

**Role in the system:** Vector stores (like Pinecone, Chroma, FAISS) enable semantic search over your documents. You embed text chunks into vectors, store them, then query "find documents similar to this question" without exact keyword matching. LangChain provides unified interfaces to 50+ vector databases, making it easy to build RAG systems where you retrieve relevant context and feed it to LLMs for accurate, grounded answers.

### 6. Memory Systems
**What it is:** Components that store and retrieve conversation history or application state across multiple LLM interactions.

**Role in the system:** Stateless LLM calls don't remember previous messages. Memory systems add continuity by maintaining chat history, summaries, or key facts. You can use simple buffer memory (store last N messages), summary memory (compress history), or entity memory (track people/places mentioned). This enables conversational agents, multi-turn workflows, and applications that build context over time without hitting token limits.

### 7. Agents & Tool Calling
**What it is:** LLM-powered systems that reason about which tools to use, execute them, and iterate based on results until solving a task.

**Role in the system:** Instead of hardcoding logic, agents let LLMs decide what to do next. You give the agent tools (search Wikipedia, run calculations, query databases), a goal, and it plans and executes steps autonomously. LangChain handles the loop of calling the LLM, parsing tool calls, executing tools, and feeding results back. This creates adaptive applications that solve problems you didn't explicitly program.

---

## Master Concepts

### 8. Callbacks, Tracing & Observability
**What it is:** Hooks that capture events during LLM execution (tokens streamed, tools called, errors) for logging, monitoring, and debugging.

**Role in the system:** Production LLM apps need visibility into what's happening: costs, latency, failures, and decision paths. Callbacks let you inject custom logic at each step (on_llm_start, on_chain_end) to track metrics, log to external systems, or implement custom behaviors. Integrated tracing (LangSmith, Weights & Biases) visualizes entire execution flows, showing you exactly why an agent made certain decisions or where chains fail.

### 9. Streaming & Partial Updates
**What it is:** Processing LLM output as it's generated token-by-token rather than waiting for complete responses.

**Role in the system:** Streaming improves user experience by showing results immediately instead of waiting 10+ seconds for full responses. LangChain supports streaming at every level: individual LLM calls, chains, and agents. You can stream to web UIs for real-time display, process tokens as they arrive for early decisions, or implement progress indicators. This makes applications feel responsive and enables use cases like live transcription or interactive agents.

### 10. LangGraph Integration
**What it is:** A framework for building stateful, multi-step agent workflows with cycles, conditional branching, and human-in-the-loop checkpoints.

**Role in the system:** LangChain's linear chains can't handle complex agent workflows that need loops, parallel branches, or waiting for human approval. LangGraph extends LangChain by modeling workflows as graphs where nodes are operations and edges define flow. You can build sophisticated agents that retry failed steps, route to different paths based on conditions, persist state between runs, and pause for human input. This bridges the gap between simple chains and production-grade autonomous systems.

---

## How to Use This Guide

1. **Beginners:** Master chains, prompts, and parsers to build basic LLM applications
2. **Professionals:** Add retrieval, memory, and agents for sophisticated AI workflows
3. **Masters:** Implement observability, streaming, and LangGraph for production systems

Each concept folder (beginner/professional/master) contains practical examples showing these concepts in action.
