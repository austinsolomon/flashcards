# Sub-Workflows (Callable Workflows) - Advanced

## Concept Overview

Sub-workflows transform n8n from a tool for building individual automations into a **composable automation platform**. While intermediate users might create a few reusable workflows, **advanced users architect entire automation ecosystems** with shared libraries, versioned modules, parameter passing, and dynamic workflow selection.

The mastery indicator: advanced users design workflow architectures like software systems - with separation of concerns, reusable components, and abstraction layers that allow different workflows to call common business logic.

## Sophisticated Example: Multi-Tenant SaaS Notification Engine

This example demonstrates an enterprise notification system where different tenant workflows call a centralized notification sub-workflow that handles channel routing (email, SMS, Slack, webhook), template rendering, delivery tracking, and retry logic - all configurable per tenant.

### Main Workflow: Tenant Event Processor

```json
{
  "name": "Tenant Event Processor",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "tenant-event",
        "responseMode": "responseNode"
      },
      "name": "Tenant Event Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [250, 400]
    },
    {
      "parameters": {
        "jsCode": "// Parse and validate incoming event\nconst event = $input.item.json;\n\n// Validate required fields\nconst required = ['tenant_id', 'event_type', 'event_data'];\nfor (const field of required) {\n  if (!event[field]) {\n    throw new Error(`Missing required field: ${field}`);\n  }\n}\n\n// Fetch tenant configuration (in real scenario, from database)\nconst tenantConfigs = {\n  'tenant-001': {\n    name: 'Acme Corp',\n    notificationChannels: ['email', 'slack'],\n    emailDomain: 'acme.com',\n    slackWebhook: 'https://hooks.slack.com/services/XXX/YYY/ZZZ',\n    adminEmail: 'admin@acme.com',\n    timezone: 'America/New_York',\n    features: ['advanced_analytics', 'priority_support']\n  },\n  'tenant-002': {\n    name: 'TechStart Inc',\n    notificationChannels: ['email', 'sms', 'webhook'],\n    emailDomain: 'techstart.io',\n    smsNumber: '+15555551234',\n    webhookUrl: 'https://api.techstart.io/notifications',\n    adminEmail: 'ops@techstart.io',\n    timezone: 'America/Los_Angeles',\n    features: ['basic']\n  }\n};\n\nconst tenantConfig = tenantConfigs[event.tenant_id];\nif (!tenantConfig) {\n  throw new Error(`Unknown tenant: ${event.tenant_id}`);\n}\n\nreturn {\n  json: {\n    event: event,\n    tenantConfig: tenantConfig,\n    processedAt: new Date().toISOString()\n  }\n};"
      },
      "name": "Load Tenant Config",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [450, 400]
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
              "id": "payment_success",
              "leftValue": "={{ $json.event.event_type }}",
              "rightValue": "payment.success",
              "operator": {
                "type": "string",
                "operation": "equals"
              }
            },
            {
              "id": "user_signup",
              "leftValue": "={{ $json.event.event_type }}",
              "rightValue": "user.signup",
              "operator": {
                "type": "string",
                "operation": "equals"
              }
            },
            {
              "id": "quota_exceeded",
              "leftValue": "={{ $json.event.event_type }}",
              "rightValue": "quota.exceeded",
              "operator": {
                "type": "string",
                "operation": "equals"
              }
            },
            {
              "id": "system_alert",
              "leftValue": "={{ $json.event.event_type }}",
              "rightValue": "system.alert",
              "operator": {
                "type": "string",
                "operation": "equals"
              }
            }
          ],
          "combinator": "or"
        }
      },
      "name": "Route Event Type",
      "type": "n8n-nodes-base.switch",
      "typeVersion": 3,
      "position": [650, 400]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "notification_params",
              "name": "notificationRequest",
              "value": "={{ {\n  tenantId: $json.event.tenant_id,\n  tenantName: $json.tenantConfig.name,\n  channels: $json.tenantConfig.notificationChannels,\n  \n  templateId: 'payment_success',\n  subject: `Payment Successful - ${$json.tenantConfig.name}`,\n  \n  recipients: {\n    email: [$json.event.event_data.customer_email, $json.tenantConfig.adminEmail],\n    slack: $json.tenantConfig.slackWebhook,\n    sms: null\n  },\n  \n  templateData: {\n    customerName: $json.event.event_data.customer_name,\n    amount: $json.event.event_data.amount,\n    currency: $json.event.event_data.currency,\n    transactionId: $json.event.event_data.transaction_id,\n    timestamp: $json.event.event_data.timestamp\n  },\n  \n  priority: 'normal',\n  metadata: {\n    eventType: $json.event.event_type,\n    tenantId: $json.event.tenant_id,\n    eventId: $json.event.event_id\n  }\n} }}",
              "type": "object"
            }
          ]
        }
      },
      "name": "Build Payment Notification",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3,
      "position": [850, 200]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "notification_params",
              "name": "notificationRequest",
              "value": "={{ {\n  tenantId: $json.event.tenant_id,\n  tenantName: $json.tenantConfig.name,\n  channels: $json.tenantConfig.notificationChannels,\n  \n  templateId: 'user_signup',\n  subject: `Welcome to ${$json.tenantConfig.name}!`,\n  \n  recipients: {\n    email: [$json.event.event_data.user_email],\n    slack: $json.tenantConfig.slackWebhook,\n    sms: null\n  },\n  \n  templateData: {\n    userName: $json.event.event_data.user_name,\n    userEmail: $json.event.event_data.user_email,\n    signupDate: $json.event.event_data.signup_date,\n    accountType: $json.event.event_data.account_type\n  },\n  \n  priority: 'normal',\n  metadata: {\n    eventType: $json.event.event_type,\n    tenantId: $json.event.tenant_id\n  }\n} }}",
              "type": "object"
            }
          ]
        }
      },
      "name": "Build Signup Notification",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3,
      "position": [850, 300]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "notification_params",
              "name": "notificationRequest",
              "value": "={{ {\n  tenantId: $json.event.tenant_id,\n  tenantName: $json.tenantConfig.name,\n  channels: ['email', 'slack'],\n  \n  templateId: 'quota_alert',\n  subject: `⚠️ Quota Exceeded - ${$json.tenantConfig.name}`,\n  \n  recipients: {\n    email: [$json.tenantConfig.adminEmail],\n    slack: $json.tenantConfig.slackWebhook,\n    sms: $json.tenantConfig.smsNumber\n  },\n  \n  templateData: {\n    resourceType: $json.event.event_data.resource_type,\n    currentUsage: $json.event.event_data.current_usage,\n    quota: $json.event.event_data.quota,\n    percentUsed: $json.event.event_data.percent_used\n  },\n  \n  priority: 'high',\n  metadata: {\n    eventType: $json.event.event_type,\n    tenantId: $json.event.tenant_id,\n    alertLevel: 'warning'\n  }\n} }}",
              "type": "object"
            }
          ]
        }
      },
      "name": "Build Quota Alert",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3,
      "position": [850, 400]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "notification_params",
              "name": "notificationRequest",
              "value": "={{ {\n  tenantId: $json.event.tenant_id,\n  tenantName: $json.tenantConfig.name,\n  channels: ['email', 'slack', 'sms'],\n  \n  templateId: 'system_alert',\n  subject: `🚨 CRITICAL ALERT - ${$json.event.event_data.alert_type}`,\n  \n  recipients: {\n    email: [$json.tenantConfig.adminEmail, 'oncall@platform.com'],\n    slack: $json.tenantConfig.slackWebhook,\n    sms: $json.tenantConfig.smsNumber\n  },\n  \n  templateData: {\n    alertType: $json.event.event_data.alert_type,\n    severity: $json.event.event_data.severity,\n    message: $json.event.event_data.message,\n    affectedServices: $json.event.event_data.affected_services\n  },\n  \n  priority: 'critical',\n  metadata: {\n    eventType: $json.event.event_type,\n    tenantId: $json.event.tenant_id,\n    alertLevel: 'critical',\n    requiresAck: true\n  }\n} }}",
              "type": "object"
            }
          ]
        }
      },
      "name": "Build System Alert",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3,
      "position": [850, 500]
    },
    {
      "parameters": {
        "workflowId": "={{ $workflow.id === '<MAIN_WORKFLOW_ID>' ? '<SUB_WORKFLOW_ID>' : 'notification-delivery-engine' }}",
        "options": {
          "waitForCompletion": true\n        }
      },
      "name": "Call Notification Engine",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1,
      "position": [1050, 400]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ {\n  success: true,\n  eventProcessed: $('Load Tenant Config').item.json.event.event_id,\n  notificationsSent: $json.deliveryResults,\n  timestamp: new Date().toISOString()\n} }}",
        "options": {
          "responseCode": 200
        }
      },
      "name": "Respond",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [1250, 400]
    }
  ],
  "connections": {
    "Tenant Event Webhook": {
      "main": [
        [
          {
            "node": "Load Tenant Config",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Load Tenant Config": {
      "main": [
        [
          {
            "node": "Route Event Type",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Route Event Type": {
      "main": [
        [
          {
            "node": "Build Payment Notification",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Build Signup Notification",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Build Quota Alert",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Build System Alert",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Build Payment Notification": {
      "main": [
        [
          {
            "node": "Call Notification Engine",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Build Signup Notification": {
      "main": [
        [
          {
            "node": "Call Notification Engine",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Build Quota Alert": {
      "main": [
        [
          {
            "node": "Call Notification Engine",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Build System Alert": {
      "main": [
        [
          {
            "node": "Call Notification Engine",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Call Notification Engine": {
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

### Sub-Workflow: Notification Delivery Engine

```json
{
  "name": "Notification Delivery Engine (Sub-Workflow)",
  "nodes": [
    {
      "parameters": {},
      "name": "Workflow Input",
      "type": "n8n-nodes-base.executeWorkflowTrigger",
      "typeVersion": 1,
      "position": [250, 400]
    },
    {
      "parameters": {
        "jsCode": "// Validate and parse notification request\nconst request = $input.item.json.notificationRequest || $input.item.json;\n\n// Validate required parameters\nif (!request.tenantId || !request.channels || !request.recipients) {\n  throw new Error('Invalid notification request: missing required fields');\n}\n\n// Load template (in production, fetch from database/CMS)\nconst templates = {\n  payment_success: {\n    email: {\n      subject: 'Payment Received - {{amount}} {{currency}}',\n      body: 'Hello {{customerName}},\\n\\nYour payment of {{amount}} {{currency}} has been successfully processed.\\n\\nTransaction ID: {{transactionId}}\\nDate: {{timestamp}}\\n\\nThank you!'\n    },\n    slack: {\n      text: '💰 Payment received: {{customerName}} paid {{amount}} {{currency}} ({{transactionId}})'\n    }\n  },\n  user_signup: {\n    email: {\n      subject: 'Welcome to {{tenantName}}!',\n      body: 'Hi {{userName}},\\n\\nWelcome aboard! Your account ({{userEmail}}) has been created.\\n\\nAccount type: {{accountType}}\\nSignup date: {{signupDate}}'\n    },\n    slack: {\n      text: '👋 New user signup: {{userName}} ({{userEmail}}) - {{accountType}} account'\n    }\n  },\n  quota_alert: {\n    email: {\n      subject: '⚠️ Quota Alert - {{resourceType}}',\n      body: 'WARNING: Your {{resourceType}} usage has exceeded the quota.\\n\\nCurrent: {{currentUsage}}\\nQuota: {{quota}}\\nPercent: {{percentUsed}}%'\n    },\n    slack: {\n      text: ':warning: QUOTA ALERT: {{resourceType}} at {{percentUsed}}% ({{currentUsage}}/{{quota}})'\n    },\n    sms: {\n      text: 'ALERT: {{resourceType}} quota exceeded - {{percentUsed}}% used'\n    }\n  },\n  system_alert: {\n    email: {\n      subject: '🚨 CRITICAL: {{alertType}}',\n      body: 'CRITICAL SYSTEM ALERT\\n\\nType: {{alertType}}\\nSeverity: {{severity}}\\nMessage: {{message}}\\nAffected: {{affectedServices}}'\n    },\n    slack: {\n      text: ':rotating_light: CRITICAL ALERT: {{alertType}} ({{severity}})\\n{{message}}\\nAffected services: {{affectedServices}}'\n    },\n    sms: {\n      text: 'CRITICAL: {{alertType}} - {{severity}} - {{message}}'\n    }\n  }\n};\n\nconst template = templates[request.templateId];\nif (!template) {\n  throw new Error(`Unknown template: ${request.templateId}`);\n}\n\n// Render templates with data\nfunction renderTemplate(templateStr, data) {\n  return templateStr.replace(/\\{\\{(\\w+)\\}\\}/g, (match, key) => data[key] || match);\n}\n\nconst renderedTemplates = {};\nfor (const channel of Object.keys(template)) {\n  renderedTemplates[channel] = {};\n  for (const key of Object.keys(template[channel])) {\n    renderedTemplates[channel][key] = renderTemplate(\n      template[channel][key],\n      { ...request.templateData, tenantName: request.tenantName }\n    );\n  }\n}\n\nreturn {\n  json: {\n    request: request,\n    renderedTemplates: renderedTemplates,\n    processingStarted: new Date().toISOString()\n  }\n};"
      },
      "name": "Load & Render Templates",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [450, 400]
    },
    {
      "parameters": {
        "jsCode": "// Create separate items for each notification channel\nconst data = $input.item.json;\nconst request = data.request;\nconst templates = data.renderedTemplates;\n\nconst notificationJobs = [];\n\n// Email notifications\nif (request.channels.includes('email') && request.recipients.email && request.recipients.email.length > 0) {\n  notificationJobs.push({\n    json: {\n      channel: 'email',\n      recipients: request.recipients.email,\n      subject: templates.email?.subject || request.subject,\n      body: templates.email?.body,\n      priority: request.priority,\n      metadata: request.metadata,\n      tenantId: request.tenantId\n    }\n  });\n}\n\n// Slack notifications\nif (request.channels.includes('slack') && request.recipients.slack) {\n  notificationJobs.push({\n    json: {\n      channel: 'slack',\n      webhookUrl: request.recipients.slack,\n      text: templates.slack?.text,\n      priority: request.priority,\n      metadata: request.metadata,\n      tenantId: request.tenantId\n    }\n  });\n}\n\n// SMS notifications\nif (request.channels.includes('sms') && request.recipients.sms) {\n  notificationJobs.push({\n    json: {\n      channel: 'sms',\n      phoneNumber: request.recipients.sms,\n      text: templates.sms?.text || templates.email?.subject,\n      priority: request.priority,\n      metadata: request.metadata,\n      tenantId: request.tenantId\n    }\n  });\n}\n\n// Custom webhook notifications\nif (request.channels.includes('webhook') && request.recipients.webhook) {\n  notificationJobs.push({\n    json: {\n      channel: 'webhook',\n      url: request.recipients.webhook,\n      payload: {\n        event: request.metadata.eventType,\n        tenant: request.tenantId,\n        data: request.templateData\n      },\n      priority: request.priority,\n      metadata: request.metadata,\n      tenantId: request.tenantId\n    }\n  });\n}\n\nif (notificationJobs.length === 0) {\n  throw new Error('No valid notification channels configured');\n}\n\nreturn notificationJobs;"
      },
      "name": "Split by Channel",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [650, 400]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "id": "email",
              "value1": "={{ $json.channel }}",
              "value2": "email",
              "operation": "equals"
            }
          ]
        }
      },
      "name": "Route: Email",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [850, 200]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.channel }}",
              "value2": "slack"
            }
          ]
        }
      },
      "name": "Route: Slack",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [850, 400]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.channel }}",
              "value2": "sms"
            }
          ]
        }
      },
      "name": "Route: SMS",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [850, 600]
    },
    {
      "parameters": {
        "fromEmail": "notifications@platform.com",
        "toEmail": "={{ $json.recipients.join(',') }}",
        "subject": "={{ $json.subject }}",
        "text": "={{ $json.body }}",
        "options": {
          "allowUnauthorizedCerts": false\n        }
      },
      "name": "Send Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 2,
      "position": [1050, 200]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "={{ $json.webhookUrl }}",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ text: $json.text, username: 'NotificationBot', icon_emoji: ':bell:' }) }}",
        "options": {
          "retry": {
            "retry": {
              "maxRetries": 3,
              "retryInterval": 1000
            }
          }
        }
      },
      "name": "Send Slack",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1050, 400]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.twilio.com/2010-04-01/Accounts/{{ $env('TWILIO_ACCOUNT_SID') }}/Messages.json",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpBasicAuth",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "To",
              "value": "={{ $json.phoneNumber }}"
            },
            {
              "name": "From",
              "value": "={{ $env('TWILIO_PHONE_NUMBER') }}"
            },
            {
              "name": "Body",
              "value": "={{ $json.text }}"
            }
          ]
        }
      },
      "name": "Send SMS",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1050, 600]
    },
    {
      "parameters": {
        "jsCode": "// Aggregate delivery results from all channels\nconst allResults = $input.all();\n\nconst deliveryResults = {\n  totalSent: allResults.length,\n  successful: 0,\n  failed: 0,\n  byChannel: {},\n  details: []\n};\n\nfor (const item of allResults) {\n  const channel = item.json.channel;\n  const success = item.json.statusCode ? item.json.statusCode >= 200 && item.json.statusCode < 300 : true;\n  \n  if (success) {\n    deliveryResults.successful++;\n  } else {\n    deliveryResults.failed++;\n  }\n  \n  if (!deliveryResults.byChannel[channel]) {\n    deliveryResults.byChannel[channel] = { sent: 0, success: 0, failed: 0 };\n  }\n  \n  deliveryResults.byChannel[channel].sent++;\n  if (success) {\n    deliveryResults.byChannel[channel].success++;\n  } else {\n    deliveryResults.byChannel[channel].failed++;\n  }\n  \n  deliveryResults.details.push({\n    channel: channel,\n    success: success,\n    timestamp: new Date().toISOString()\n  });\n}\n\nreturn { json: { deliveryResults } };"
      },
      "name": "Aggregate Results",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1250, 400]
    }
  ],
  "connections": {
    "Workflow Input": {
      "main": [
        [
          {
            "node": "Load & Render Templates",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Load & Render Templates": {
      "main": [
        [
          {
            "node": "Split by Channel",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Split by Channel": {
      "main": [
        [
          {
            "node": "Route: Email",
            "type": "main",
            "index": 0
          },
          {
            "node": "Route: Slack",
            "type": "main",
            "index": 0
          },
          {
            "node": "Route: SMS",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Route: Email": {
      "main": [
        [
          {
            "node": "Send Email",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Route: Slack": {
      "main": [
        [
          {
            "node": "Send Slack",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Route: SMS": {
      "main": [
        [
          {
            "node": "Send SMS",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Send Email": {
      "main": [
        [
          {
            "node": "Aggregate Results",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Send Slack": {
      "main": [
        [
          {
            "node": "Aggregate Results",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Send SMS": {
      "main": [
        [
          {
            "node": "Aggregate Results",
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

1. **True Separation of Concerns**: Main workflow handles business logic (event routing), sub-workflow handles delivery infrastructure
2. **Reusability at Scale**: Multiple workflows (payment, signup, alerts, etc.) all call the same notification engine
3. **Parameter Passing**: Demonstrates complex object passing with templates, channels, recipients, and metadata
4. **Wait for Completion**: Main workflow waits for sub-workflow to complete and receives delivery results
5. **Multi-Channel Orchestration**: Sub-workflow splits into parallel channels (email/Slack/SMS) then aggregates results
6. **Template Engine**: Shows how sub-workflows can act as microservices with their own internal logic

## Best Practices for Sub-Workflow Mastery

1. **Design for reusability across multiple callers** - Create generic, parameterized sub-workflows that solve one problem well; avoid hard-coding tenant/user-specific logic inside sub-workflows
2. **Use clear input/output contracts** - Document expected input structure and output format; validate inputs at sub-workflow entry; return structured results with success/failure indicators
3. **Implement proper error handling and return codes** - Use try-catch in sub-workflows; return error details to caller; let caller decide how to handle failures rather than failing silently
4. **Version your sub-workflows like APIs** - When changing sub-workflow logic, create v2 instead of modifying v1; allows gradual migration; prevents breaking existing callers
5. **Leverage waitForCompletion strategically** - Use `waitForCompletion: true` when caller needs results (synchronous); use `false` for fire-and-forget async operations; design workflows based on whether results are needed immediately
