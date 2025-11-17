# Webhook Triggers - Intermediate

## Concept Overview

Webhook Triggers are the foundation of event-driven automation in n8n. While beginners use webhooks for simple data reception, **intermediate users leverage webhook authentication, payload validation, response customization, and intelligent routing** to build production-grade integrations.

The key differentiator: intermediate users understand that webhooks are bidirectional - they not only receive data but can provide immediate, contextual responses and enforce security constraints.

## Sophisticated Example: Stripe Payment Event Handler with Validation

This example demonstrates a production-ready Stripe webhook handler that validates signatures, processes different event types, updates a database, and sends real-time notifications.

```json
{
  "name": "Stripe Payment Event Handler",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "stripe-events",
        "responseMode": "responseNode",
        "options": {
          "rawBody": true
        }
      },
      "name": "Stripe Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [250, 300],
      "webhookId": "stripe-payment-webhook"
    },
    {
      "parameters": {
        "jsCode": "// Validate Stripe signature\nconst crypto = require('crypto');\n\nconst payload = $input.item.json.body;\nconst signature = $input.item.json.headers['stripe-signature'];\nconst webhookSecret = $env('STRIPE_WEBHOOK_SECRET');\n\n// Parse signature header\nconst signatureParts = signature.split(',').reduce((acc, part) => {\n  const [key, value] = part.split('=');\n  acc[key] = value;\n  return acc;\n}, {});\n\nconst timestamp = signatureParts.t;\nconst receivedSignature = signatureParts.v1;\n\n// Calculate expected signature\nconst signedPayload = `${timestamp}.${JSON.stringify(payload)}`;\nconst expectedSignature = crypto\n  .createHmac('sha256', webhookSecret)\n  .update(signedPayload)\n  .digest('hex');\n\n// Verify signature matches\nif (expectedSignature !== receivedSignature) {\n  throw new Error('Invalid signature - webhook rejected');\n}\n\n// Check timestamp is within 5 minutes to prevent replay attacks\nconst currentTime = Math.floor(Date.now() / 1000);\nif (Math.abs(currentTime - timestamp) > 300) {\n  throw new Error('Timestamp too old - possible replay attack');\n}\n\n// Parse event data\nconst eventType = payload.type;\nconst eventData = payload.data.object;\n\nreturn {\n  json: {\n    eventType,\n    eventId: payload.id,\n    customerId: eventData.customer,\n    amount: eventData.amount / 100, // Convert cents to dollars\n    currency: eventData.currency,\n    status: eventData.status,\n    paymentMethod: eventData.payment_method,\n    metadata: eventData.metadata,\n    timestamp: new Date(timestamp * 1000).toISOString(),\n    validated: true\n  }\n};"
      },
      "name": "Validate Stripe Signature",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [450, 300]
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
              "id": "payment_succeeded",
              "leftValue": "={{ $json.eventType }}",
              "rightValue": "payment_intent.succeeded",
              "operator": {
                "type": "string",
                "operation": "equals"
              }
            },
            {
              "id": "payment_failed",
              "leftValue": "={{ $json.eventType }}",
              "rightValue": "payment_intent.payment_failed",
              "operator": {
                "type": "string",
                "operation": "equals"
              }
            },
            {
              "id": "refund_updated",
              "leftValue": "={{ $json.eventType }}",
              "rightValue": "charge.refund.updated",
              "operator": {
                "type": "string",
                "operation": "equals"
              }
            },
            {
              "id": "subscription_updated",
              "leftValue": "={{ $json.eventType }}",
              "rightValue": "customer.subscription.updated",
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
      "position": [650, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO payments (event_id, customer_id, amount, currency, status, payment_method, metadata, created_at)\nVALUES ($1, $2, $3, $4, $5, $6, $7, $8)\nON CONFLICT (event_id) DO UPDATE SET\n  status = EXCLUDED.status,\n  updated_at = NOW()\nRETURNING *;",
        "options": {
          "queryReplacement": "={{ [$json.eventId, $json.customerId, $json.amount, $json.currency, $json.status, $json.paymentMethod, JSON.stringify($json.metadata), $json.timestamp] }}"
        }
      },
      "name": "Store Payment Success",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2,
      "position": [850, 200]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "UPDATE payments SET status = 'failed', failure_reason = $1, updated_at = NOW()\nWHERE event_id = $2\nRETURNING *;",
        "options": {
          "queryReplacement": "={{ [$json.metadata.failure_message || 'Payment failed', $json.eventId] }}"
        }
      },
      "name": "Update Payment Failed",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2,
      "position": [850, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.sendgrid.com/v3/mail/send",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "sendGridApi",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "personalizations",
              "value": "={{ [{ \"to\": [{ \"email\": $('Store Payment Success').item.json.customer_email }], \"dynamic_template_data\": { \"amount\": $json.amount, \"currency\": $json.currency, \"transaction_id\": $json.eventId } }] }}"
            },
            {
              "name": "from",
              "value": "={{ { \"email\": \"billing@company.com\", \"name\": \"Company Billing\" } }}"
            },
            {
              "name": "template_id",
              "value": "d-payment-success-template"
            }
          ]
        }
      },
      "name": "Send Success Email",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1050, 200]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ { \"received\": true, \"eventId\": $('Validate Stripe Signature').item.json.eventId, \"processed\": true, \"timestamp\": new Date().toISOString() } }}",
        "options": {
          "responseCode": 200,
          "responseHeaders": {
            "entries": [
              {
                "name": "Content-Type",
                "value": "application/json"
              }
            ]
          }
        }
      },
      "name": "Respond to Stripe",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [1250, 300]
    }
  ],
  "connections": {
    "Stripe Webhook": {
      "main": [
        [
          {
            "node": "Validate Stripe Signature",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Validate Stripe Signature": {
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
            "node": "Store Payment Success",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Update Payment Failed",
            "type": "main",
            "index": 0
          }
        ],
        [],
        []
      ]
    },
    "Store Payment Success": {
      "main": [
        [
          {
            "node": "Send Success Email",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Send Success Email": {
      "main": [
        [
          {
            "node": "Respond to Stripe",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Update Payment Failed": {
      "main": [
        [
          {
            "node": "Respond to Stripe",
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

1. **Cryptographic Validation**: Uses HMAC-SHA256 to verify webhook authenticity, preventing malicious requests
2. **Replay Attack Prevention**: Validates timestamp freshness (5-minute window)
3. **Event-Driven Routing**: Uses Switch node to handle multiple event types elegantly
4. **Idempotent Processing**: Uses `ON CONFLICT` to handle duplicate events gracefully
5. **Proper Response Handling**: Returns immediate acknowledgment to Stripe with custom response data
6. **Production Database Integration**: Demonstrates real database operations with parameterized queries

## Best Practices for Webhook Mastery

1. **Always validate webhook signatures** - Never trust incoming data; use HMAC validation with secrets stored in environment variables to prevent unauthorized webhook calls
2. **Implement idempotency** - Use unique event IDs to prevent duplicate processing when webhooks are retried; databases should use UPSERT patterns
3. **Respond quickly (<3s)** - Acknowledge webhooks immediately with 200 status, then process async; use responseNode mode to control timing and prevent timeouts
4. **Enable raw body mode** - For signature validation, you need the raw request body; enable `rawBody: true` option in webhook settings
5. **Log everything strategically** - Store event IDs, timestamps, and processing status for debugging and audit trails; build correlation between webhook events and downstream actions
