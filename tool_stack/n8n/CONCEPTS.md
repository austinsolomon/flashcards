# n8n - Core Concepts Guide

This guide explains the 10 core concepts that give you maximum power when using n8n. Each concept includes a brief explanation and how it fits into your workflow automation development.

---

## Beginner Concepts

### 1. Workflows & Nodes
**What it is:** Visual automations built by connecting nodes (boxes) that each perform one specific action like sending emails, processing data, or calling APIs.

**Role in the system:** n8n is a visual programming platform where you drag and drop nodes onto a canvas and connect them to create automations. Each node is a reusable component (Google Sheets, Slack, HTTP Request) with configuration options. Workflows execute left-to-right, passing data between nodes. This no-code/low-code approach lets you build complex integrations without writing full applications, making automation accessible while remaining powerful enough for technical users.

### 2. Connections & Data Flow
**What it is:** Lines between nodes that pass data (JSON objects) from one step to the next, determining execution order and what information each node receives.

**Role in the system:** When you connect nodes, you create a data pipeline. The output of one node (e.g., fetched database rows) becomes the input to the next (e.g., send email for each row). n8n automatically handles batching—if a node returns 10 items, the next node runs 10 times. Understanding data flow helps you debug workflows by inspecting what data moves between steps and why nodes execute in certain orders.

### 3. Triggers (Webhook, Schedule, Manual)
**What it is:** Starting points for workflows that define when and how automations run—on incoming HTTP requests, time schedules, or manual execution.

**Role in the system:** Triggers activate workflows. Webhook triggers let external systems (forms, apps, APIs) start workflows by POSTing data. Schedule triggers run workflows on cron schedules for periodic tasks (daily reports, hourly syncs). Manual triggers let you test workflows or run them on demand. This flexibility means n8n can respond to real-time events, run background jobs, or serve as on-demand automation tools depending on your needs.

### 4. Expressions & Variables
**What it is:** Dynamic placeholders using `{{ }}` syntax that reference data from previous nodes, manipulate values, and create conditional logic.

**Role in the system:** Hardcoded values don't work for real automations—you need dynamic data. Expressions let you reference any field from previous nodes: `{{ $json.email }}` gets the email field from incoming data. You can transform data (`{{ $json.name.toUpperCase() }}`), do math, combine strings, and access workflow metadata. This makes workflows adaptive to the data they receive, enabling personalized emails, dynamic API calls, and data transformations without code.

---

## Professional Concepts

### 5. HTTP Request Node
**What it is:** A flexible node that makes HTTP calls to any API, with full control over methods, headers, authentication, and body content.

**Role in the system:** While n8n has 400+ pre-built integrations, you'll eventually need to call custom APIs or services without dedicated nodes. The HTTP Request node is your Swiss Army knife—call REST APIs, webhooks, or internal services. You can authenticate with API keys, OAuth, or custom headers, send JSON/form data, and process responses. This makes n8n extensible to any web service, turning it into a universal API orchestration platform.

### 6. Function & Code Nodes
**What it is:** Nodes that let you write JavaScript to process data, implement custom logic, or do complex transformations that visual nodes can't handle.

**Role in the system:** Some logic is too complex for visual nodes—nested loops, custom algorithms, complex data reshaping. Function nodes let you write JavaScript with access to all node data and return transformed results. This bridges the gap between no-code simplicity and programming flexibility. You can parse unusual data formats, implement business logic, call external libraries, or do heavy data processing while staying within n8n's visual workflow paradigm.

### 7. Error Handling & Error Workflows
**What it is:** Built-in mechanisms to catch failures in workflows, retry operations, send alerts, or route errors to specialized recovery workflows.

**Role in the system:** Production automations fail—APIs are down, data is malformed, rate limits hit. n8n's error handling lets you define what happens on failure: retry nodes automatically, send Slack alerts, log to databases, or trigger dedicated error workflows that handle recovery. You can implement graceful degradation, fallback APIs, or manual review processes. This turns fragile automations into robust systems that handle real-world failure scenarios.

---

## Master Concepts

### 8. Sub-workflows & Modularity
**What it is:** Breaking complex automations into reusable workflow modules that can be called from other workflows, creating a library of automation components.

**Role in the system:** As automation libraries grow, duplication becomes a problem. Sub-workflows let you extract common patterns (send formatted Slack message, validate customer data, sync to database) into standalone workflows that others can call. This creates reusable components, reduces maintenance (update once, affect all callers), and lets you build complex automations by composing smaller, tested pieces. It's the difference between scripts and a well-architected system.

### 9. Binary Data & File Processing
**What it is:** Handling non-JSON data like images, PDFs, CSVs, or other files that flow through workflows alongside regular data.

**Role in the system:** Many automations involve files—processing uploaded documents, generating reports, manipulating images. n8n's binary data system lets nodes pass files between steps: download attachments, process with code, convert formats, and upload to storage. You can extract text from PDFs, resize images, parse CSVs, or generate documents—all within visual workflows. This makes n8n suitable for document automation, data migration, and content processing pipelines.

### 10. LLM/AI Integration & Smart Workflows
**What it is:** Nodes that integrate language models (OpenAI, local LLMs) for text generation, analysis, classification, and intelligent decision-making in workflows.

**Role in the system:** AI nodes turn n8n into an intelligent automation platform. You can classify support tickets, generate personalized responses, extract structured data from unstructured text, or build conversational agents. Combine LLMs with other nodes to create AI-powered workflows: analyze customer feedback sentiment, auto-route based on intent, generate reports from data, or build RAG systems that query knowledge bases. This merges traditional automation with AI capabilities for next-generation workflows.

---

## How to Use This Guide

1. **Beginners:** Master workflows, data flow, triggers, and expressions to build basic automations
2. **Professionals:** Add HTTP requests, code nodes, and error handling for production reliability
3. **Masters:** Build modular systems with sub-workflows, file processing, and AI integration

Each concept folder (professional/master) contains practical examples showing these concepts in action.

Note: n8n focuses on professional and master concepts as it's designed for users with some technical background.
