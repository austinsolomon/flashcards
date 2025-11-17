# Error Workflows (Global Error Catching) - Advanced

## Concept Overview

Error Workflows are n8n's enterprise-grade error handling mechanism that transforms failures from workflow-ending events into **observable, categorized, and actionable incidents**. While intermediate users might set up basic error logging, **advanced users build comprehensive error taxonomies, intelligent retry strategies, dead-letter queues, and incident management integrations**.

The mastery indicator: advanced users treat errors as data - categorizing them by type, severity, recoverability, and business impact - then routing them to appropriate handlers (auto-retry, alert, manual intervention, or ignore).

## Sophisticated Example: Production Error Handling with Classification & Routing

This example demonstrates an enterprise error workflow that classifies errors by type (transient, configuration, data, external), determines recoverability, implements smart retry logic with exponential backoff, and routes to appropriate incident management systems.

### Global Error Workflow

```json
{
  "name": "Global Error Handler",
  "nodes": [
    {
      "parameters": {},
      "name": "Error Trigger",
      "type": "n8n-nodes-base.errorTrigger",
      "typeVersion": 1,
      "position": [250, 500]
    },
    {
      "parameters": {
        "jsCode": "/**\n * Advanced Error Classification Engine\n * Analyzes error details to determine:\n * - Error category (transient, config, data, external)\n * - Severity (critical, high, medium, low)\n * - Recoverability (auto-retry, manual, unrecoverable)\n * - Business impact (revenue, compliance, user-facing, internal)\n */\n\nconst errorData = $input.item.json;\n\n// Extract error details from different possible structures\nconst error = errorData.error || {};\nconst errorMessage = error.message || errorData.message || 'Unknown error';\nconst errorStack = error.stack || '';\nconst failedNode = errorData.node?.name || 'Unknown Node';\nconst failedWorkflow = errorData.workflow?.name || 'Unknown Workflow';\nconst executionId = errorData.execution?.id || 'Unknown';\n\n// ============= ERROR CLASSIFICATION =============\n\n/**\n * Classify error type based on message patterns\n */\nfunction classifyErrorType(message, stack) {\n  const patterns = {\n    transient: [\n      /timeout/i,\n      /ETIMEDOUT/i,\n      /ECONNREFUSED/i,\n      /ECONNRESET/i,\n      /socket hang up/i,\n      /network/i,\n      /rate limit/i,\n      /429/,\n      /503/,\n      /502/,\n      /504/\n    ],\n    configuration: [\n      /authentication/i,\n      /unauthorized/i,\n      /forbidden/i,\n      /401/,\n      /403/,\n      /invalid.*credential/i,\n      /api.*key/i,\n      /permission denied/i,\n      /access denied/i\n    ],\n    data_validation: [\n      /validation.*failed/i,\n      /invalid.*format/i,\n      /missing.*required/i,\n      /cannot.*null/i,\n      /undefined.*property/i,\n      /unexpected.*type/i,\n      /400/\n    ],\n    external_service: [\n      /api.*error/i,\n      /external.*service/i,\n      /third.*party/i,\n      /500/,\n      /internal.*server/i\n    ],\n    code_error: [\n      /TypeError/,\n      /ReferenceError/,\n      /SyntaxError/,\n      /RangeError/\n    ]\n  };\n  \n  for (const [type, regexList] of Object.entries(patterns)) {\n    for (const regex of regexList) {\n      if (regex.test(message) || regex.test(stack)) {\n        return type;\n      }\n    }\n  }\n  \n  return 'unknown';\n}\n\n/**\n * Determine severity based on error type and context\n */\nfunction calculateSeverity(errorType, workflow, node) {\n  // Critical workflows that affect revenue or compliance\n  const criticalWorkflows = ['payment processing', 'compliance reporting', 'customer onboarding'];\n  const isCriticalWorkflow = criticalWorkflows.some(w => \n    workflow.toLowerCase().includes(w.toLowerCase())\n  );\n  \n  if (isCriticalWorkflow) {\n    return errorType === 'code_error' ? 'critical' : 'high';\n  }\n  \n  const severityMap = {\n    'code_error': 'high',\n    'configuration': 'high',\n    'external_service': 'medium',\n    'data_validation': 'medium',\n    'transient': 'low',\n    'unknown': 'medium'\n  };\n  \n  return severityMap[errorType] || 'medium';\n}\n\n/**\n * Determine if error is recoverable and how\n */\nfunction determineRecoverability(errorType, errorMessage) {\n  // Transient errors should be retried\n  if (errorType === 'transient') {\n    // Check if we've already retried (look for retry markers in message)\n    const retryMatch = errorMessage.match(/retry attempt (\\d+)/);\n    const retryCount = retryMatch ? parseInt(retryMatch[1]) : 0;\n    \n    if (retryCount >= 5) {\n      return { recoverable: false, strategy: 'max_retries_exceeded', retryCount };\n    }\n    \n    return { recoverable: true, strategy: 'exponential_backoff', retryCount };\n  }\n  \n  // Configuration errors need manual intervention\n  if (errorType === 'configuration') {\n    return { recoverable: true, strategy: 'manual_config_fix', retryCount: 0 };\n  }\n  \n  // Data validation errors might need data cleanup\n  if (errorType === 'data_validation') {\n    return { recoverable: true, strategy: 'data_remediation', retryCount: 0 };\n  }\n  \n  // Code errors are unrecoverable without deployment\n  if (errorType === 'code_error') {\n    return { recoverable: false, strategy: 'requires_code_fix', retryCount: 0 };\n  }\n  \n  // External service errors - depends on status\n  if (errorType === 'external_service') {\n    return { recoverable: true, strategy: 'wait_and_retry', retryCount: 0 };\n  }\n  \n  return { recoverable: false, strategy: 'unknown', retryCount: 0 };\n}\n\n/**\n * Calculate business impact\n */\nfunction assessBusinessImpact(workflow, errorType, severity) {\n  const revenueWorkflows = ['payment', 'checkout', 'subscription', 'billing'];\n  const complianceWorkflows = ['audit', 'compliance', 'reporting', 'gdpr'];\n  const userFacingWorkflows = ['signup', 'login', 'notification', 'email'];\n  \n  const workflowLower = workflow.toLowerCase();\n  \n  if (revenueWorkflows.some(w => workflowLower.includes(w))) {\n    return { impact: 'revenue', priority: 'P1', affectsCustomers: true };\n  }\n  \n  if (complianceWorkflows.some(w => workflowLower.includes(w))) {\n    return { impact: 'compliance', priority: 'P1', affectsCustomers: false };\n  }\n  \n  if (userFacingWorkflows.some(w => workflowLower.includes(w))) {\n    return { impact: 'user_experience', priority: 'P2', affectsCustomers: true };\n  }\n  \n  return { impact: 'internal', priority: 'P3', affectsCustomers: false };\n}\n\n// ============= RUN CLASSIFICATION =============\n\nconst errorType = classifyErrorType(errorMessage, errorStack);\nconst severity = calculateSeverity(errorType, failedWorkflow, failedNode);\nconst recoverability = determineRecoverability(errorType, errorMessage);\nconst businessImpact = assessBusinessImpact(failedWorkflow, errorType, severity);\n\n// ============= BUILD ENRICHED ERROR OBJECT =============\n\nconst enrichedError = {\n  // Original error data\n  original: {\n    message: errorMessage,\n    stack: errorStack,\n    node: failedNode,\n    workflow: failedWorkflow,\n    workflowId: errorData.workflow?.id,\n    executionId: executionId,\n    timestamp: errorData.execution?.startedAt || new Date().toISOString()\n  },\n  \n  // Classification\n  classification: {\n    errorType: errorType,\n    severity: severity,\n    recoverable: recoverability.recoverable,\n    recoveryStrategy: recoverability.strategy,\n    retryCount: recoverability.retryCount\n  },\n  \n  // Business context\n  business: {\n    impact: businessImpact.impact,\n    priority: businessImpact.priority,\n    affectsCustomers: businessImpact.affectsCustomers,\n    estimatedRevenueLoss: businessImpact.impact === 'revenue' ? 'high' : 'none'\n  },\n  \n  // Routing decisions\n  routing: {\n    shouldRetry: recoverability.recoverable && recoverability.strategy === 'exponential_backoff',\n    shouldAlert: severity === 'critical' || severity === 'high',\n    shouldCreateIncident: businessImpact.priority === 'P1',\n    shouldDeadLetter: !recoverability.recoverable || recoverability.retryCount >= 5\n  },\n  \n  // Metadata\n  metadata: {\n    classifiedAt: new Date().toISOString(),\n    classifier: 'n8n-error-workflow-v2',\n    environment: $env('ENVIRONMENT') || 'production'\n  }\n};\n\nreturn { json: enrichedError };"
      },
      "name": "Classify Error",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [450, 500]
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
              "id": "retry",
              "leftValue": "={{ $json.routing.shouldRetry }}",
              "rightValue": true,
              "operator": {
                "type": "boolean",
                "operation": "equals"
              }
            },
            {
              "id": "alert",
              "leftValue": "={{ $json.routing.shouldAlert }}",
              "rightValue": true,
              "operator": {
                "type": "boolean",
                "operation": "equals"
              }
            },
            {
              "id": "incident",
              "leftValue": "={{ $json.routing.shouldCreateIncident }}",
              "rightValue": true,
              "operator": {
                "type": "boolean",
                "operation": "equals"
              }
            },
            {
              "id": "dead_letter",
              "leftValue": "={{ $json.routing.shouldDeadLetter }}",
              "rightValue": true,
              "operator": {
                "type": "boolean",
                "operation": "equals"
              }
            }
          ],
          "combinator": "or"
        }
      },
      "name": "Route Error",
      "type": "n8n-nodes-base.switch",
      "typeVersion": 3,
      "position": [650, 500]
    },
    {
      "parameters": {
        "jsCode": "// Implement exponential backoff retry\nconst error = $input.item.json;\nconst retryCount = error.classification.retryCount;\n\n// Calculate delay: 2^retryCount * 1000ms (1s, 2s, 4s, 8s, 16s)\nconst delayMs = Math.pow(2, retryCount) * 1000;\nconst maxDelay = 30000; // Cap at 30 seconds\nconst actualDelay = Math.min(delayMs, maxDelay);\n\n// Add jitter to prevent thundering herd (±20%)\nconst jitter = actualDelay * 0.2 * (Math.random() - 0.5);\nconst finalDelay = Math.round(actualDelay + jitter);\n\nreturn {\n  json: {\n    ...error,\n    retry: {\n      attempt: retryCount + 1,\n      delayMs: finalDelay,\n      nextRetryAt: new Date(Date.now() + finalDelay).toISOString(),\n      maxRetries: 5\n    }\n  }\n};"
      },
      "name": "Calculate Retry Delay",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [850, 200]
    },
    {
      "parameters": {
        "amount": "={{ $json.retry.delayMs }}",
        "unit": "ms"
      },
      "name": "Wait Before Retry",
      "type": "n8n-nodes-base.wait",
      "typeVersion": 1,
      "position": [1050, 200]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "={{ $json.original.workflow.retryWebhook || 'https://n8n.company.com/webhook/retry-execution' }}",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "workflowId",
              "value": "={{ $json.original.workflowId }}"
            },
            {
              "name": "executionId",
              "value": "={{ $json.original.executionId }}"
            },
            {
              "name": "retryAttempt",
              "value": "={{ $json.retry.attempt }}"
            },
            {
              "name": "originalError",
              "value": "={{ $json.original.message }}"
            }
          ]
        }
      },
      "name": "Trigger Retry",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1250, 200]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.pagerduty.com/incidents",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "pagerDutyApi",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({\n  incident: {\n    type: 'incident',\n    title: `[${$json.classification.severity.toUpperCase()}] ${$json.original.workflow} - ${$json.original.node}`,\n    service: {\n      id: $env('PAGERDUTY_SERVICE_ID'),\n      type: 'service_reference'\n    },\n    urgency: $json.business.priority === 'P1' ? 'high' : 'low',\n    body: {\n      type: 'incident_body',\n      details: `Error Type: ${$json.classification.errorType}\\nWorkflow: ${$json.original.workflow}\\nNode: ${$json.original.node}\\nMessage: ${$json.original.message}\\nBusiness Impact: ${$json.business.impact}\\nAffects Customers: ${$json.business.affectsCustomers}`\n    },\n    incident_key: $json.original.executionId\n  }\n}) }}"
      },
      "name": "Create PagerDuty Incident",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [850, 500]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.slack.com/api/chat.postMessage",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "slackApi",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "channel",
              "value": "={{ $json.classification.severity === 'critical' ? '#incidents' : '#alerts' }}"
            },
            {
              "name": "text",
              "value": "={{ `🚨 ${$json.classification.severity.toUpperCase()} Error in ${$json.original.workflow}` }}"
            },
            {
              "name": "blocks",
              "value": "={{ JSON.stringify([\n  {\n    type: 'header',\n    text: {\n      type: 'plain_text',\n      text: `${$json.classification.severity === 'critical' ? '🚨' : '⚠️'} ${$json.classification.errorType.toUpperCase()} Error`\n    }\n  },\n  {\n    type: 'section',\n    fields: [\n      { type: 'mrkdwn', text: `*Workflow:*\\n${$json.original.workflow}` },\n      { type: 'mrkdwn', text: `*Node:*\\n${$json.original.node}` },\n      { type: 'mrkdwn', text: `*Severity:*\\n${$json.classification.severity}` },\n      { type: 'mrkdwn', text: `*Priority:*\\n${$json.business.priority}` },\n      { type: 'mrkdwn', text: `*Impact:*\\n${$json.business.impact}` },\n      { type: 'mrkdwn', text: `*Affects Customers:*\\n${$json.business.affectsCustomers ? 'Yes' : 'No'}` }\n    ]\n  },\n  {\n    type: 'section',\n    text: {\n      type: 'mrkdwn',\n      text: `*Error Message:*\\n\`\`\`${$json.original.message}\`\`\``\n    }\n  },\n  {\n    type: 'context',\n    elements: [\n      {\n        type: 'mrkdwn',\n        text: `Execution ID: ${$json.original.executionId} | ${$json.metadata.classifiedAt}`\n      }\n    ]\n  }\n]) }}"
            }
          ]
        }
      },
      "name": "Send Alert to Slack",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [850, 350]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO error_dead_letter_queue (\n  execution_id,\n  workflow_id,\n  workflow_name,\n  failed_node,\n  error_type,\n  error_message,\n  severity,\n  business_impact,\n  recovery_strategy,\n  retry_count,\n  full_error_data,\n  created_at\n) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW())\nON CONFLICT (execution_id) DO UPDATE SET\n  retry_count = EXCLUDED.retry_count,\n  updated_at = NOW()",
        "options": {
          "queryReplacement": "={{ [\n  $json.original.executionId,\n  $json.original.workflowId,\n  $json.original.workflow,\n  $json.original.node,\n  $json.classification.errorType,\n  $json.original.message,\n  $json.classification.severity,\n  $json.business.impact,\n  $json.classification.recoveryStrategy,\n  $json.classification.retryCount,\n  JSON.stringify($json)\n] }}"
        }
      },
      "name": "Store in Dead Letter Queue",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2,
      "position": [850, 650]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO error_analytics (\n  error_type,\n  severity,\n  workflow_name,\n  node_name,\n  business_impact,\n  recoverable,\n  occurred_at\n) VALUES ($1, $2, $3, $4, $5, $6, $7)",
        "options": {
          "queryReplacement": "={{ [\n  $json.classification.errorType,\n  $json.classification.severity,\n  $json.original.workflow,\n  $json.original.node,\n  $json.business.impact,\n  $json.classification.recoverable,\n  $json.original.timestamp\n] }}"
        }
      },
      "name": "Log to Analytics",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2,
      "position": [850, 800]
    }
  ],
  "connections": {
    "Error Trigger": {
      "main": [
        [
          {
            "node": "Classify Error",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Classify Error": {
      "main": [
        [
          {
            "node": "Route Error",
            "type": "main",
            "index": 0
          },
          {
            "node": "Log to Analytics",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Route Error": {
      "main": [
        [
          {
            "node": "Calculate Retry Delay",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Send Alert to Slack",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Create PagerDuty Incident",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Store in Dead Letter Queue",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Calculate Retry Delay": {
      "main": [
        [
          {
            "node": "Wait Before Retry",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Wait Before Retry": {
      "main": [
        [
          {
            "node": "Trigger Retry",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "settings": {
    "errorWorkflow": true\n  }\n}
```

## Why This Example Demonstrates Mastery

1. **Error Taxonomy**: Classifies errors into actionable categories (transient, config, data, code, external) using pattern matching
2. **Multi-Dimensional Analysis**: Evaluates severity, recoverability, business impact, and customer affect independently
3. **Intelligent Routing**: Switch node routes to 4+ different handlers based on classification (retry, alert, incident, dead-letter)
4. **Exponential Backoff with Jitter**: Implements production-grade retry logic with randomization to prevent thundering herd
5. **Dead Letter Queue**: Unrecoverable errors stored in database for manual investigation and replay
6. **Analytics Integration**: Logs all errors for trend analysis and error rate monitoring
7. **Context-Aware Alerting**: Different Slack channels and PagerDuty urgency based on severity and business impact

## Best Practices for Error Workflow Mastery

1. **Classify errors by recoverability, not just type** - Distinguish between transient (retry), config (manual fix), data (remediation), and code (deploy required); route each category differently
2. **Implement dead letter queues for unrecoverable failures** - Store failed executions with full context in database; build admin UI to inspect and manually retry; prevent data loss
3. **Use structured error logging for analytics** - Log errors to time-series DB; track error rates by type/workflow/node; set up dashboards and anomaly detection; measure MTTR (mean time to resolution)
4. **Design error workflows to be non-failing** - Use `neverError: true` and try-catch; error workflows that fail create infinite loops; always handle edge cases gracefully
5. **Enrich errors with business context before alerting** - Add customer impact, revenue implications, SLA violations; route critical business-impacting errors to PagerDuty, low-severity to Slack; include runbook links in alerts
