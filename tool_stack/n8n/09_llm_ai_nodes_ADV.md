# LLM & AI Nodes (Claude/OpenAI/Gemini/Ollama) - Advanced

## Concept Overview

LLM nodes transform n8n from a deterministic automation platform into an **intelligent agent framework** capable of natural language understanding, content generation, classification, extraction, and reasoning. While beginners use LLMs for simple text generation, **advanced users build multi-agent systems, implement RAG (Retrieval Augmented Generation), chain reasoning steps, use structured outputs, and create self-improving workflows**.

The mastery indicator: advanced users understand prompt engineering, context window management, token optimization, model selection criteria, fallback strategies, and how to combine multiple LLMs for specialized tasks in production pipelines.

## Sophisticated Example: AI-Powered Customer Support Ticket Router & Resolver

This example demonstrates an intelligent support system that uses Claude for ticket classification and sentiment analysis, GPT-4 for knowledge base RAG search, Gemini for multilingual response generation, and implements a confidence-based escalation strategy with human-in-the-loop fallback.

```json
{
  "name": "AI Support Ticket Router & Resolver",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "support-ticket",
        "responseMode": "responseNode"
      },
      "name": "Receive Ticket",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [250, 500]
    },
    {
      "parameters": {
        "modelId": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "prompt": "=Analyze this customer support ticket and provide structured classification.\n\nTicket:\nSubject: {{ $json.subject }}\nBody: {{ $json.body }}\nCustomer: {{ $json.customer_email }}\n\nProvide your analysis in JSON format:\n{\n  \"category\": \"billing|technical|account|feature_request|bug_report|other\",\n  \"priority\": \"critical|high|medium|low\",\n  \"sentiment\": \"very_negative|negative|neutral|positive|very_positive\",\n  \"urgency_score\": 1-10,\n  \"requires_human\": true|false,\n  \"detected_language\": \"en|es|fr|de|ja|zh|other\",\n  \"key_entities\": [\"extracted entities like product names, error codes, etc\"],\n  \"suggested_tags\": [\"relevant tags\"],\n  \"summary\": \"one sentence summary\",\n  \"reasoning\": \"brief explanation of classification\"\n}",
        "options": {
          "temperature": 0.3,
          "maxTokens": 1000
        }
      },
      "name": "Claude: Classify Ticket",
      "type": "n8n-nodes-base.anthropic",
      "typeVersion": 1,
      "position": [450, 500]
    },
    {
      "parameters": {
        "jsCode": "// Parse Claude's JSON response and enrich with metadata\nconst ticketData = $('Receive Ticket').item.json;\nconst claudeResponse = $input.item.json.output;\n\n// Extract JSON from Claude's response (handles markdown code blocks)\nlet classification;\ntry {\n  const jsonMatch = claudeResponse.match(/```json\\n([\\s\\S]*?)\\n```/) || \n                    claudeResponse.match(/\\{[\\s\\S]*\\}/);\n  classification = JSON.parse(jsonMatch ? jsonMatch[1] || jsonMatch[0] : claudeResponse);\n} catch (e) {\n  // Fallback if parsing fails\n  classification = {\n    category: 'other',\n    priority: 'medium',\n    sentiment: 'neutral',\n    urgency_score: 5,\n    requires_human: true,\n    detected_language: 'en',\n    summary: 'Classification failed',\n    reasoning: 'Could not parse AI response'\n  };\n}\n\nreturn {\n  json: {\n    // Original ticket\n    ticket: ticketData,\n    \n    // AI classification\n    classification: classification,\n    \n    // Enrichment\n    metadata: {\n      receivedAt: new Date().toISOString(),\n      classifiedAt: new Date().toISOString(),\n      ticketId: ticketData.ticket_id || `TKT-${Date.now()}`,\n      slaDeadline: new Date(Date.now() + \n        (classification.priority === 'critical' ? 2 : \n         classification.priority === 'high' ? 8 : \n         classification.priority === 'medium' ? 24 : 48) * 3600000\n      ).toISOString()\n    },\n    \n    // Routing decision\n    routing: {\n      autoResolve: !classification.requires_human && \n                   classification.urgency_score <= 6 &&\n                   ['billing', 'account', 'feature_request'].includes(classification.category),\n      searchKnowledgeBase: ['technical', 'bug_report'].includes(classification.category),\n      escalateToHuman: classification.requires_human || \n                       classification.urgency_score >= 8 ||\n                       classification.sentiment === 'very_negative'\n    }\n  }\n};"
      },
      "name": "Parse Classification",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [650, 500]
    },
    {
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "id": "needs_kb_search",
              "value1": "={{ $json.routing.searchKnowledgeBase }}",
              "value2": true
            }
          ]
        }
      },
      "name": "Needs KB Search?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [850, 500]
    },
    {
      "parameters": {
        "model": "text-embedding-3-large",
        "input": "={{ $json.ticket.subject + ' ' + $json.ticket.body }}",
        "options": {
          "dimensions": 1024
        }
      },
      "name": "OpenAI: Generate Embedding",
      "type": "n8n-nodes-base.openAi",
      "typeVersion": 1,
      "position": [1050, 400]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT \n  id,\n  title,\n  content,\n  category,\n  1 - (embedding <=> $1::vector) as similarity\nFROM knowledge_base\nWHERE category = $2\nORDER BY embedding <=> $1::vector\nLIMIT 5",
        "options": {
          "queryReplacement": "={{ [\n  JSON.stringify($json.data[0].embedding),\n  $('Parse Classification').item.json.classification.category\n] }}"
        }
      },
      "name": "Vector Search KB",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2,
      "position": [1250, 400]
    },
    {
      "parameters": {
        "model": "gpt-4-turbo-preview",
        "prompt": "=You are a technical support expert. Answer the customer's question using ONLY the provided knowledge base articles.\n\nCustomer Question:\n{{ $('Parse Classification').item.json.ticket.body }}\n\nRelevant Knowledge Base Articles:\n{{ $json.map((article, i) => `${i+1}. ${article.title}\\n${article.content}\\nRelevance: ${(article.similarity * 100).toFixed(1)}%`).join('\\n\\n') }}\n\nProvide a helpful, accurate response. If the knowledge base doesn't contain enough information, say so and suggest escalation.\n\nFormat your response as JSON:\n{\n  \"answer\": \"your detailed response\",\n  \"confidence\": 0.0-1.0,\n  \"sources\": [\"article IDs used\"],\n  \"requires_escalation\": true|false,\n  \"reasoning\": \"why this answer was generated\"\n}",
        "options": {
          "temperature": 0.4,
          "maxTokens": 1500,
          "responseFormat": "json_object"
        }
      },
      "name": "GPT-4: Generate Answer",
      "type": "n8n-nodes-base.openAi",
      "typeVersion": 1,
      "position": [1450, 400]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "ai_answer",
              "name": "aiAnswer",
              "value": "={{ JSON.parse($json.choices[0].message.content) }}",
              "type": "object"
            }
          ]
        }
      },
      "name": "Extract AI Answer",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3,
      "position": [1650, 400]
    },
    {
      "parameters": {
        "conditions": {
          "options": {
            "caseSensitive": true,
            "leftValue": "",
            "typeValidation": "strict"
          },
          "conditions": [
            {
              "id": "high_confidence",
              "leftValue": "={{ $json.aiAnswer.confidence }}",
              "rightValue": 0.8,
              "operator": {
                "type": "number",
                "operation": "gt"
              }
            },
            {
              "id": "no_escalation",
              "leftValue": "={{ $json.aiAnswer.requires_escalation }}",
              "rightValue": false,
              "operator": {
                "type": "boolean",
                "operation": "equals"
              }
            }
          ],
          "combinator": "and"
        }
      },
      "name": "High Confidence?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [1850, 400]
    },
    {
      "parameters": {
        "model": "gemini-1.5-pro",
        "prompt": "=Translate and format this support response for the customer.\n\nOriginal ticket language: {{ $('Parse Classification').item.json.classification.detected_language }}\nCustomer sentiment: {{ $('Parse Classification').item.json.classification.sentiment }}\n\nTechnical Answer:\n{{ $json.aiAnswer.answer }}\n\nYour task:\n1. Translate to {{ $('Parse Classification').item.json.classification.detected_language }} if needed\n2. Adjust tone based on sentiment (more empathetic for negative sentiment)\n3. Format professionally with proper structure\n4. Add appropriate greeting and closing\n5. Include relevant article links: {{ $json.aiAnswer.sources.join(', ') }}\n\nProvide ONLY the final customer-facing response, ready to send.",
        "options": {
          "temperature": 0.6,
          "maxTokens": 2000
        }
      },
      "name": "Gemini: Format Response",
      "type": "n8n-nodes-base.google",
      "typeVersion": 1,
      "position": [2050, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.sendgrid.com/v3/mail/send",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "sendGridApi",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({\n  personalizations: [{\n    to: [{ email: $('Parse Classification').item.json.ticket.customer_email }],\n    dynamic_template_data: {\n      ticketId: $('Parse Classification').item.json.metadata.ticketId,\n      response: $json.output,\n      resolvedBy: 'AI Assistant',\n      confidence: ($('Extract AI Answer').item.json.aiAnswer.confidence * 100).toFixed(0) + '%'\n    }\n  }],\n  from: { email: 'support@company.com', name: 'Support Team' },\n  template_id: 'd-support-response',\n  categories: ['ai-resolved', $('Parse Classification').item.json.classification.category]\n}) }}"
      },
      "name": "Send Auto-Response",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [2250, 300]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "escalation_data",
              "name": "escalation",
              "value": "={{ {\n  ticketId: $json.metadata.ticketId,\n  priority: $json.classification.priority,\n  category: $json.classification.category,\n  sentiment: $json.classification.sentiment,\n  urgencyScore: $json.classification.urgency_score,\n  reason: $json.routing.escalateToHuman ? 'Required human review' : \n          $json.aiAnswer?.requires_escalation ? 'AI insufficient confidence' : \n          'Low AI confidence score',\n  aiSummary: $json.classification.summary,\n  suggestedTags: $json.classification.suggested_tags,\n  slaDeadline: $json.metadata.slaDeadline,\n  customerEmail: $json.ticket.customer_email\n} }}",
              "type": "object"
            }
          ]
        }
      },
      "name": "Build Escalation",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3,
      "position": [2050, 600]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.zendesk.com/api/v2/tickets",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "zendeskApi",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "ticket",
              "value": "={{ {\n  subject: $('Parse Classification').item.json.ticket.subject,\n  comment: { \n    body: $('Parse Classification').item.json.ticket.body + '\\n\\n---\\nAI Analysis:\\n' + $json.escalation.aiSummary \n  },\n  priority: $json.escalation.priority,\n  tags: ['ai-escalated', ...$json.escalation.suggestedTags],\n  custom_fields: [\n    { id: 'ai_confidence', value: 'low' },\n    { id: 'sentiment', value: $json.escalation.sentiment },\n    { id: 'urgency_score', value: $json.escalation.urgencyScore }\n  ]\n} }}"
            }
          ]
        }
      },
      "name": "Create Zendesk Ticket",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [2250, 600]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO ticket_analytics (\n  ticket_id,\n  category,\n  priority,\n  sentiment,\n  urgency_score,\n  detected_language,\n  auto_resolved,\n  ai_confidence,\n  resolution_time_seconds,\n  created_at\n) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())",
        "options": {
          "queryReplacement": "={{ [\n  $('Parse Classification').item.json.metadata.ticketId,\n  $('Parse Classification').item.json.classification.category,\n  $('Parse Classification').item.json.classification.priority,\n  $('Parse Classification').item.json.classification.sentiment,\n  $('Parse Classification').item.json.classification.urgency_score,\n  $('Parse Classification').item.json.classification.detected_language,\n  $('High Confidence?').item.json ? true : false,\n  $('Extract AI Answer').item.json?.aiAnswer?.confidence || 0,\n  (Date.now() - new Date($('Parse Classification').item.json.metadata.receivedAt).getTime()) / 1000\n] }}"
        }
      },
      "name": "Log Analytics",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2,
      "position": [2250, 450]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ {\n  success: true,\n  ticketId: $('Parse Classification').item.json.metadata.ticketId,\n  status: $('High Confidence?').item.json ? 'auto_resolved' : 'escalated_to_human',\n  category: $('Parse Classification').item.json.classification.category,\n  estimatedResolutionTime: $('High Confidence?').item.json ? 'immediate' : $('Parse Classification').item.json.metadata.slaDeadline\n} }}",
        "options": {
          "responseCode": 200
        }
      },
      "name": "Respond",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [2450, 450]
    }
  ],
  "connections": {
    "Receive Ticket": {
      "main": [
        [
          {
            "node": "Claude: Classify Ticket",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Claude: Classify Ticket": {
      "main": [
        [
          {
            "node": "Parse Classification",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Parse Classification": {
      "main": [
        [
          {
            "node": "Needs KB Search?",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Needs KB Search?": {
      "main": [
        [
          {
            "node": "OpenAI: Generate Embedding",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Build Escalation",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "OpenAI: Generate Embedding": {
      "main": [
        [
          {
            "node": "Vector Search KB",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Vector Search KB": {
      "main": [
        [
          {
            "node": "GPT-4: Generate Answer",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "GPT-4: Generate Answer": {
      "main": [
        [
          {
            "node": "Extract AI Answer",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Extract AI Answer": {
      "main": [
        [
          {
            "node": "High Confidence?",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "High Confidence?": {
      "main": [
        [
          {
            "node": "Gemini: Format Response",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Build Escalation",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Gemini: Format Response": {
      "main": [
        [
          {
            "node": "Send Auto-Response",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Send Auto-Response": {
      "main": [
        [
          {
            "node": "Log Analytics",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Build Escalation": {
      "main": [
        [
          {
            "node": "Create Zendesk Ticket",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Create Zendesk Ticket": {
      "main": [
        [
          {
            "node": "Log Analytics",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Log Analytics": {
      "main": [
        [
          {
            "node": "Respond",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

## Why This Example Demonstrates Mastery

1. **Multi-Model Strategy**: Uses Claude for classification (best at reasoning), OpenAI for embeddings (industry standard), GPT-4 for RAG (strong retrieval), Gemini for multilingual generation (strong translation)
2. **RAG Implementation**: Demonstrates vector search with embeddings against knowledge base, context injection into prompts
3. **Structured Outputs**: Uses JSON mode and careful prompt engineering to get parseable responses
4. **Confidence-Based Routing**: AI confidence scores determine auto-resolution vs human escalation
5. **Prompt Engineering**: Different prompt styles for each task (analytical for classification, instructive for generation, creative for formatting)
6. **Fallback Strategy**: Parse errors handled gracefully with fallback classifications
7. **Production Monitoring**: Logs AI confidence, resolution time, and auto-resolve rate for continuous improvement

## Best Practices for LLM/AI Mastery

1. **Choose models based on task-specific strengths** - Claude excels at reasoning/analysis, GPT-4 at knowledge retrieval, Gemini at multilingual tasks, Ollama for local/privacy; benchmark and measure performance per use case
2. **Implement confidence thresholds and human escalation** - Never trust AI 100%; set confidence thresholds (0.8+ for auto-action); build escalation paths for low-confidence or high-stakes scenarios; track false positive/negative rates
3. **Use structured outputs (JSON mode) for downstream processing** - Request JSON responses with schemas; validate and parse with error handling; enables reliable chaining of AI steps with deterministic systems
4. **Optimize prompts for token efficiency and context windows** - Keep prompts concise; use few-shot examples sparingly; truncate long inputs intelligently; monitor token usage and costs; implement caching for repeated contexts
5. **Build RAG pipelines for knowledge-intensive tasks** - Use vector databases (pgvector, Pinecone) for semantic search; chunk documents intelligently; rerank results before injection; measure retrieval quality and answer accuracy; version your knowledge base
