# Wait/Resume (Asynchronous Handling) - Advanced

## Concept Overview

Wait nodes transform n8n from a synchronous automation tool into an **asynchronous orchestration platform** capable of handling long-running processes that span hours, days, or weeks. While beginners might use simple time delays, **advanced users build state machines, approval workflows, SLA monitors, and conditional resumption logic** with multiple resume paths.

The mastery indicator: advanced users understand that Wait nodes create execution pauses where workflows can be resumed by time, webhooks, or external triggers - enabling complex multi-actor processes with human-in-the-loop decision points.

## Sophisticated Example: Multi-Stage Content Approval Workflow with SLA Tracking

This example implements a content publishing pipeline where drafts require sequential approval from editor → legal → CMO, each with different SLA timeouts, escalation paths, and the ability to reject/request changes at any stage.

```json
{
  "name": "Content Approval Workflow with SLA",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "content-submit",
        "responseMode": "responseNode"
      },
      "name": "Submit Content",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [250, 400]
    },
    {
      "parameters": {
        "jsCode": "// Initialize content submission with metadata\nconst submission = $input.item.json;\n\n// Validate required fields\nif (!submission.content_id || !submission.author_id || !submission.content_type) {\n  throw new Error('Missing required fields: content_id, author_id, content_type');\n}\n\n// Determine approval chain based on content type\nconst approvalChains = {\n  'blog_post': ['editor', 'legal'],\n  'whitepaper': ['editor', 'legal', 'cmo'],\n  'press_release': ['editor', 'legal', 'cmo', 'ceo'],\n  'social_media': ['editor']\n};\n\nconst approvalChain = approvalChains[submission.content_type] || ['editor'];\n\n// Set SLA times (in minutes)\nconst slaMinutes = {\n  'editor': 240,      // 4 hours\n  'legal': 1440,      // 24 hours\n  'cmo': 2880,        // 48 hours\n  'ceo': 2880         // 48 hours\n};\n\nreturn {\n  json: {\n    // Content details\n    contentId: submission.content_id,\n    authorId: submission.author_id,\n    authorEmail: submission.author_email,\n    contentType: submission.content_type,\n    title: submission.title,\n    contentUrl: submission.content_url,\n    \n    // Workflow state\n    approvalChain: approvalChain,\n    currentStage: 0,\n    currentApprover: approvalChain[0],\n    slaMinutes: slaMinutes[approvalChain[0]],\n    \n    // Tracking\n    submittedAt: new Date().toISOString(),\n    approvalHistory: [],\n    escalationCount: 0,\n    \n    // Status\n    status: 'pending_' + approvalChain[0],\n    workflowId: $workflow.id\n  }\n};"
      },
      "name": "Initialize Approval Workflow",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [450, 400]
    },
    {
      "parameters": {
        "jsCode": "// Generate unique approval token for this stage\nconst crypto = require('crypto');\nconst data = $input.item.json;\n\nconst approvalToken = crypto\n  .createHash('sha256')\n  .update(`${data.contentId}-${data.currentApprover}-${Date.now()}`)\n  .digest('hex')\n  .substring(0, 32);\n\n// Store token mapping (in production, use database)\n$workflow.staticData[approvalToken] = {\n  contentId: data.contentId,\n  approver: data.currentApprover,\n  createdAt: new Date().toISOString()\n};\n\nconst baseUrl = $env('N8N_WEBHOOK_BASE_URL') || 'https://n8n.company.com';\n\nreturn {\n  json: {\n    ...data,\n    approvalToken: approvalToken,\n    approveUrl: `${baseUrl}/webhook/approve/${approvalToken}?action=approve`,\n    rejectUrl: `${baseUrl}/webhook/approve/${approvalToken}?action=reject`,\n    changesUrl: `${baseUrl}/webhook/approve/${approvalToken}?action=request_changes`\n  }\n};"
      },
      "name": "Generate Approval Token",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [650, 400]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.sendgrid.com/v3/mail/send",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "sendGridApi",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({\n  personalizations: [{\n    to: [{ email: $('Get Approver Email').item.json.approverEmail }],\n    dynamic_template_data: {\n      contentTitle: $json.title,\n      contentType: $json.contentType,\n      authorEmail: $json.authorEmail,\n      contentUrl: $json.contentUrl,\n      approver: $json.currentApprover,\n      slaHours: Math.round($json.slaMinutes / 60),\n      approveUrl: $json.approveUrl,\n      rejectUrl: $json.rejectUrl,\n      changesUrl: $json.changesUrl\n    }\n  }],\n  from: { email: 'workflow@company.com', name: 'Content Workflow' },\n  template_id: 'd-approval-request'\n}) }}"
      },
      "name": "Send Approval Request",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [850, 400]
    },
    {
      "parameters": {
        "jsCode": "// Lookup approver email based on role\nconst approverRoles = {\n  'editor': 'editor@company.com',\n  'legal': 'legal@company.com',\n  'cmo': 'cmo@company.com',\n  'ceo': 'ceo@company.com'\n};\n\nconst data = $input.item.json;\nconst approverEmail = approverRoles[data.currentApprover];\n\nif (!approverEmail) {\n  throw new Error(`Unknown approver role: ${data.currentApprover}`);\n}\n\nreturn {\n  json: {\n    ...data,\n    approverEmail: approverEmail\n  }\n};"
      },
      "name": "Get Approver Email",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [650, 300]
    },
    {
      "parameters": {
        "unit": "minutes",
        "amount": "={{ $json.slaMinutes }}",
        "resume": "webhook",
        "options": {\n          "webhookSuffix": "={{ 'approve/' + $json.approvalToken }}"\n        }
      },
      "name": "Wait for Approval",
      "type": "n8n-nodes-base.wait",
      "typeVersion": 1,
      "position": [1050, 400],
      "webhookId": "content-approval-wait"
    },
    {
      "parameters": {
        "conditions": {
          "options": {
            "caseSensitive": false,
            "leftValue": "",
            "typeValidation": "loose"
          },
          "conditions": [
            {
              "id": "approved",
              "leftValue": "={{ $json.query.action }}",
              "rightValue": "approve",
              "operator": {
                "type": "string",
                "operation": "equals"
              }
            },
            {
              "id": "rejected",
              "leftValue": "={{ $json.query.action }}",
              "rightValue": "reject",
              "operator": {
                "type": "string",
                "operation": "equals"
              }
            },
            {
              "id": "changes",
              "leftValue": "={{ $json.query.action }}",
              "rightValue": "request_changes",
              "operator": {
                "type": "string",
                "operation": "equals"
              }
            }\n          ],
          "combinator": "or"
        }
      },
      "name": "Check Response",
      "type": "n8n-nodes-base.switch",
      "typeVersion": 3,
      "position": [1250, 400]
    },
    {
      "parameters": {
        "jsCode": "// Handle approval - move to next stage or publish\nconst originalData = $('Wait for Approval').item.json;\nconst response = $input.item.json;\n\n// Record approval in history\nconst approvalRecord = {\n  approver: originalData.currentApprover,\n  action: 'approved',\n  timestamp: new Date().toISOString(),\n  comments: response.body?.comments || ''\n};\n\nconst approvalHistory = [...originalData.approvalHistory, approvalRecord];\nconst nextStage = originalData.currentStage + 1;\n\n// Check if there are more approvers in the chain\nif (nextStage < originalData.approvalChain.length) {\n  // Move to next approval stage\n  const nextApprover = originalData.approvalChain[nextStage];\n  const slaMinutes = {\n    'editor': 240,\n    'legal': 1440,\n    'cmo': 2880,\n    'ceo': 2880\n  };\n  \n  return {\n    json: {\n      ...originalData,\n      currentStage: nextStage,\n      currentApprover: nextApprover,\n      slaMinutes: slaMinutes[nextApprover],\n      approvalHistory: approvalHistory,\n      status: 'pending_' + nextApprover,\n      requiresNextApproval: true\n    }\n  };\n} else {\n  // All approvals complete - ready to publish\n  return {\n    json: {\n      ...originalData,\n      approvalHistory: approvalHistory,\n      status: 'approved',\n      approvedAt: new Date().toISOString(),\n      requiresNextApproval: false,\n      readyToPublish: true\n    }\n  };\n}"
      },
      "name": "Process Approval",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1450, 200]
    },
    {
      "parameters": {
        "jsCode": "// Handle rejection - notify author and end workflow\nconst originalData = $('Wait for Approval').item.json;\nconst response = $input.item.json;\n\nconst rejectionRecord = {\n  approver: originalData.currentApprover,\n  action: 'rejected',\n  timestamp: new Date().toISOString(),\n  reason: response.body?.reason || 'No reason provided',\n  comments: response.body?.comments || ''\n};\n\nreturn {\n  json: {\n    ...originalData,\n    approvalHistory: [...originalData.approvalHistory, rejectionRecord],\n    status: 'rejected',\n    rejectedAt: new Date().toISOString(),\n    rejectedBy: originalData.currentApprover,\n    rejectionReason: rejectionRecord.reason\n  }\n};"
      },
      "name": "Process Rejection",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1450, 400]
    },
    {
      "parameters": {
        "jsCode": "// Handle change request - send back to author\nconst originalData = $('Wait for Approval').item.json;\nconst response = $input.item.json;\n\nconst changeRequestRecord = {\n  approver: originalData.currentApprover,\n  action: 'changes_requested',\n  timestamp: new Date().toISOString(),\n  requestedChanges: response.body?.changes || 'No specific changes listed',\n  comments: response.body?.comments || ''\n};\n\nreturn {\n  json: {\n    ...originalData,\n    approvalHistory: [...originalData.approvalHistory, changeRequestRecord],\n    status: 'changes_requested',\n    changesRequestedAt: new Date().toISOString(),\n    changesRequestedBy: originalData.currentApprover,\n    requestedChanges: changeRequestRecord.requestedChanges\n  }\n};"
      },
      "name": "Process Change Request",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1450, 600]
    },
    {
      "parameters": {
        "jsCode": "// Handle SLA timeout - escalate to manager\nconst originalData = $input.item.json;\n\n// This runs when Wait node times out without webhook response\nconst escalationRecord = {\n  approver: originalData.currentApprover,\n  action: 'sla_timeout',\n  timestamp: new Date().toISOString(),\n  slaMinutes: originalData.slaMinutes\n};\n\nconst escalationCount = originalData.escalationCount + 1;\n\nreturn {\n  json: {\n    ...originalData,\n    approvalHistory: [...originalData.approvalHistory, escalationRecord],\n    escalationCount: escalationCount,\n    status: 'escalated',\n    lastEscalationAt: new Date().toISOString(),\n    requiresEscalation: true\n  }\n};"
      },
      "name": "Handle SLA Timeout",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1250, 600]
    },
    {
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{ $json.requiresNextApproval }}",
              "value2": true
            }
          ]
        }
      },
      "name": "Need Next Approval?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [1650, 200]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.cms.company.com/publish",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "cmsApi",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "content_id",
              "value": "={{ $json.contentId }}"
            },
            {
              "name": "approved_by",
              "value": "={{ $json.approvalHistory.map(a => a.approver).join(', ') }}"
            },
            {
              "name": "publish_immediately",
              "value": "true"
            }
          ]
        }
      },
      "name": "Publish Content",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1850, 100]
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
              "value": "#escalations"
            },
            {
              "name": "text",
              "value": "={{ `⚠️ SLA Breach: ${$json.title} awaiting ${$json.currentApprover} approval for ${$json.slaMinutes} min (Escalation #${$json.escalationCount})` }}"
            }
          ]
        }
      },
      "name": "Send Escalation Alert",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1450, 800]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ {\n  success: true,\n  message: 'Content submission received and approval workflow started',\n  contentId: $('Initialize Approval Workflow').item.json.contentId,\n  approvalChain: $('Initialize Approval Workflow').item.json.approvalChain,\n  currentApprover: $('Initialize Approval Workflow').item.json.currentApprover\n} }}",
        "options": {
          "responseCode": 202
        }
      },
      "name": "Respond to Submission",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [850, 600]
    }
  ],
  "connections": {
    "Submit Content": {
      "main": [
        [
          {
            "node": "Initialize Approval Workflow",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Initialize Approval Workflow": {
      "main": [
        [
          {
            "node": "Generate Approval Token",
            "type": "main",
            "index": 0
          },
          {
            "node": "Respond to Submission",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Generate Approval Token": {
      "main": [
        [
          {
            "node": "Get Approver Email",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Get Approver Email": {
      "main": [
        [
          {
            "node": "Send Approval Request",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Send Approval Request": {
      "main": [
        [
          {
            "node": "Wait for Approval",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Wait for Approval": {
      "main": [
        [
          {
            "node": "Check Response",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Handle SLA Timeout",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Check Response": {
      "main": [
        [
          {
            "node": "Process Approval",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Process Rejection",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Process Change Request",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Process Approval": {
      "main": [
        [
          {
            "node": "Need Next Approval?",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Need Next Approval?": {
      "main": [
        [
          {
            "node": "Generate Approval Token",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Publish Content",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Handle SLA Timeout": {
      "main": [
        [
          {
            "node": "Send Escalation Alert",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Send Escalation Alert": {
      "main": [
        [
          {
            "node": "Generate Approval Token",
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

1. **Webhook Resume Pattern**: Uses Wait node with custom webhook suffix for user-triggered resumption (approve/reject/changes)
2. **Dual Resume Paths**: Wait node has TWO outputs - webhook response (user action) and timeout (SLA breach) - demonstrates handling both scenarios
3. **Stateful Loop**: After timeout escalation, workflow loops back to re-request approval with incremented escalation counter
4. **Sequential State Machine**: After approval, checks if more approvals needed and loops back through approval flow for next approver
5. **Security**: Generates cryptographic tokens for approval URLs to prevent unauthorized approvals
6. **Rich Decision Tree**: Switch node routes to approve/reject/changes handlers based on webhook query parameter

## Best Practices for Wait/Resume Mastery

1. **Always handle BOTH timeout and webhook paths** - Wait nodes have two outputs: main path (webhook/timer triggered) and timeout path (SLA exceeded); design workflows to handle both gracefully
2. **Use unique webhook suffixes for tracking** - Generate unique tokens/IDs for webhook resume URLs; store mapping in staticData or database to validate requests and prevent replay attacks
3. **Implement idempotency for resume webhooks** - Check if workflow already resumed before processing; prevent duplicate approvals if user clicks link multiple times; use execution IDs to track state
4. **Design for workflow restarts and failures** - Store critical state in external systems (DB), not just workflow variables; enable recovery if n8n restarts during long wait periods
5. **Set realistic timeouts with escalation paths** - Don't wait indefinitely; implement SLA timeouts that trigger escalations; build retry/reminder logic before final timeout; provide clear paths for stuck workflows
