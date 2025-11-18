# HTTP Request Node - Intermediate

## Concept Overview

The HTTP Request node is n8n's Swiss Army knife for API integration. Beginners make simple GET requests; **intermediate users master authentication flows, retry logic, pagination handling, batch processing, and error recovery** to build resilient API integrations.

The critical distinction: intermediate users understand HTTP as a stateful protocol requiring context management, and they design workflows that handle rate limits, partial failures, and complex response transformations.

## Sophisticated Example: Multi-API Data Enrichment Pipeline with Rate Limiting

This example demonstrates fetching customer data from a CRM, enriching it with third-party APIs (company data, social profiles, credit scores), handling rate limits with exponential backoff, and aggregating results.

```json
{
  "name": "Customer Data Enrichment Pipeline",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "triggerAtHour": 2
            }
          ]
        }
      },
      "name": "Daily at 2 AM",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "method": "GET",
        "url": "https://api.crm.com/v2/customers",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "crmApi",
        "sendQuery": true,
        "queryParameters": {
          "parameters": [
            {
              "name": "status",
              "value": "active"
            },
            {
              "name": "created_after",
              "value": "={{ $now.minus({ days: 7 }).toISO() }}"
            },
            {
              "name": "limit",
              "value": "100"
            }
          ]
        },
        "options": {
          "response": {
            "response": {
              "fullResponse": true,
              "neverError": true
            }
          },
          "timeout": 30000,
          "retry": {
            "retry": {
              "maxRetries": 3,
              "retryInterval": 1000,
              "retryMultiplier": 2
            }
          }
        }
      },
      "name": "Fetch New Customers",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [450, 300]
    },
    {
      "parameters": {
        "jsCode": "// Parse paginated response and prepare for enrichment\nconst response = $input.item.json;\n\nif (response.statusCode !== 200) {\n  throw new Error(`CRM API failed: ${response.statusCode}`);\n}\n\nconst customers = response.body.data;\nconst outputItems = [];\n\n// Add metadata for rate limiting and batch processing\nfor (let i = 0; i < customers.length; i++) {\n  outputItems.push({\n    json: {\n      customerId: customers[i].id,\n      email: customers[i].email,\n      companyName: customers[i].company?.name,\n      companyDomain: customers[i].company?.domain,\n      linkedinUrl: customers[i].linkedin_url,\n      batchIndex: i,\n      batchSize: customers.length,\n      enrichmentStatus: {\n        companyData: 'pending',\n        creditScore: 'pending',\n        socialProfile: 'pending'\n      },\n      rateLimitDelay: Math.floor(i / 10) * 1000 // 10 requests per second max\n    }\n  });\n}\n\nreturn outputItems;"
      },
      "name": "Parse & Prepare Enrichment",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [650, 300]
    },
    {
      "parameters": {
        "batchSize": 10,
        "options": {
          "reset": false
        }
      },
      "name": "Batch 10 at a time",
      "type": "n8n-nodes-base.splitInBatches",
      "typeVersion": 3,
      "position": [850, 300]
    },
    {
      "parameters": {
        "amount": "={{ $json.rateLimitDelay }}",
        "unit": "ms"
      },
      "name": "Rate Limit Delay",
      "type": "n8n-nodes-base.wait",
      "typeVersion": 1,
      "position": [1050, 300]
    },
    {
      "parameters": {
        "method": "GET",
        "url": "https://api.clearbit.com/v2/companies/find",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendQuery": true,
        "queryParameters": {
          "parameters": [
            {
              "name": "domain",
              "value": "={{ $json.companyDomain }}"
            }
          ]
        },
        "options": {
          "response": {
            "response": {
              "fullResponse": true,
              "neverError": true
            }
          },
          "timeout": 15000,
          "retry": {
            "retry": {
              "maxRetries": 5,
              "retryInterval": 2000,
              "retryMultiplier": 1.5,
              "maxRetryInterval": 30000
            }
          }
        }
      },
      "name": "Enrich Company Data",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1250, 200]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.experian.com/business/credit-score",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "experianApi",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "business_name",
              "value": "={{ $json.companyName }}"
            },
            {
              "name": "domain",
              "value": "={{ $json.companyDomain }}"
            }
          ]
        },
        "options": {
          "response": {
            "response": {
              "fullResponse": true,
              "neverError": true
            }
          },
          "timeout": 20000,
          "allowUnauthorizedCerts": false
        }
      },
      "name": "Get Credit Score",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1250, 300]
    },
    {
      "parameters": {
        "method": "GET",
        "url": "https://api.linkedin.com/v2/people/{{ $json.linkedinUrl.split('/').pop() }}",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "linkedInOAuth2Api",
        "options": {
          "response": {
            "response": {
              "fullResponse": true,
              "neverError": true
            }
          },
          "timeout": 10000
        }
      },
      "name": "Fetch LinkedIn Profile",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1250, 400]
    },
    {
      "parameters": {
        "jsCode": "// Aggregate all enrichment data with intelligent error handling\nconst baseData = $('Rate Limit Delay').item.json;\nconst companyResponse = $('Enrich Company Data').item.json;\nconst creditResponse = $('Get Credit Score').item.json;\nconst linkedinResponse = $('Fetch LinkedIn Profile').item.json;\n\n// Helper function to extract data or set error status\nfunction processApiResponse(response, dataPath) {\n  if (!response || response.statusCode === 404) {\n    return { status: 'not_found', data: null };\n  }\n  if (response.statusCode === 429) {\n    return { status: 'rate_limited', retryAfter: response.headers['retry-after'] || 60 };\n  }\n  if (response.statusCode >= 500) {\n    return { status: 'server_error', code: response.statusCode };\n  }\n  if (response.statusCode === 200) {\n    return { status: 'success', data: response.body };\n  }\n  return { status: 'error', code: response.statusCode };\n}\n\nconst companyData = processApiResponse(companyResponse);\nconst creditData = processApiResponse(creditResponse);\nconst linkedinData = processApiResponse(linkedinResponse);\n\n// Build enriched customer profile\nconst enrichedProfile = {\n  customerId: baseData.customerId,\n  email: baseData.email,\n  \n  // Company enrichment\n  company: companyData.status === 'success' ? {\n    name: companyData.data.name,\n    domain: companyData.data.domain,\n    industry: companyData.data.category?.industry,\n    employees: companyData.data.metrics?.employees,\n    revenue: companyData.data.metrics?.annualRevenue,\n    description: companyData.data.description,\n    logo: companyData.data.logo,\n    location: companyData.data.geo\n  } : null,\n  \n  // Credit score\n  creditScore: creditData.status === 'success' ? {\n    score: creditData.data.score,\n    rating: creditData.data.rating,\n    riskLevel: creditData.data.risk_level,\n    assessmentDate: new Date().toISOString()\n  } : null,\n  \n  // Social profile\n  linkedin: linkedinData.status === 'success' ? {\n    headline: linkedinData.data.headline,\n    currentPosition: linkedinData.data.positions?.values?.[0],\n    connections: linkedinData.data.numConnections,\n    skills: linkedinData.data.skills?.values?.slice(0, 10)\n  } : null,\n  \n  // Enrichment metadata\n  enrichmentStatus: {\n    companyData: companyData.status,\n    creditScore: creditData.status,\n    socialProfile: linkedinData.status,\n    completedAt: new Date().toISOString()\n  },\n  \n  // Calculate enrichment quality score (0-100)\n  enrichmentQuality: (\n    (companyData.status === 'success' ? 40 : 0) +\n    (creditData.status === 'success' ? 35 : 0) +\n    (linkedinData.status === 'success' ? 25 : 0)\n  )\n};\n\nreturn { json: enrichedProfile };"
      },
      "name": "Aggregate Enrichment Data",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1450, 300]
    },
    {
      "parameters": {
        "conditions": {
          "number": [
            {
              "value1": "={{ $json.enrichmentQuality }}",
              "value2": 60,
              "operation": "larger"
            }
          ]
        }
      },
      "name": "Quality Check",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [1650, 300]
    },
    {
      "parameters": {
        "method": "PUT",
        "url": "https://api.crm.com/v2/customers/{{ $json.customerId }}/enrichment",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "crmApi",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify($json) }}",
        "options": {
          "batching": {
            "batch": {
              "batchSize": 50,
              "batchInterval": 1000
            }
          }
        }
      },
      "name": "Update CRM with Enriched Data",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1850, 250]
    }
  ],
  "connections": {
    "Daily at 2 AM": {
      "main": [
        [
          {
            "node": "Fetch New Customers",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Fetch New Customers": {
      "main": [
        [
          {
            "node": "Parse & Prepare Enrichment",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Parse & Prepare Enrichment": {
      "main": [
        [
          {
            "node": "Batch 10 at a time",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Batch 10 at a time": {
      "main": [
        [
          {
            "node": "Rate Limit Delay",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Rate Limit Delay": {
      "main": [
        [
          {
            "node": "Enrich Company Data",
            "type": "main",
            "index": 0
          },
          {
            "node": "Get Credit Score",
            "type": "main",
            "index": 0
          },
          {
            "node": "Fetch LinkedIn Profile",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Enrich Company Data": {
      "main": [
        [
          {
            "node": "Aggregate Enrichment Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Get Credit Score": {
      "main": [
        [
          {
            "node": "Aggregate Enrichment Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Fetch LinkedIn Profile": {
      "main": [
        [
          {
            "node": "Aggregate Enrichment Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Aggregate Enrichment Data": {
      "main": [
        [
          {
            "node": "Quality Check",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Quality Check": {
      "main": [
        [
          {
            "node": "Update CRM with Enriched Data",
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

1. **Parallel API Calls**: Splits from Rate Limit node to 3 enrichment APIs simultaneously for performance
2. **Intelligent Error Handling**: Uses `neverError: true` with custom status code parsing instead of workflow failures
3. **Rate Limit Management**: Implements batch processing with calculated delays to respect API quotas
4. **Exponential Backoff**: Configures retry logic with increasing intervals for transient failures
5. **Response Aggregation**: Code node intelligently merges multiple API responses with null handling
6. **Quality Scoring**: Calculates enrichment completeness to filter low-quality data

## Best Practices for HTTP Request Mastery

1. **Always use fullResponse + neverError for production** - Get complete HTTP metadata (status, headers) and handle errors gracefully rather than failing workflows; parse status codes explicitly
2. **Implement exponential backoff with jitter** - Configure retry strategies (maxRetries, retryInterval, retryMultiplier) to handle transient failures; add randomization to prevent thundering herd
3. **Respect rate limits proactively** - Use batching, delays, and header inspection (X-RateLimit-Remaining) to stay within quotas; implement circuit breakers for degraded APIs
4. **Batch requests when APIs support it** - Use request batching options to reduce API calls; check if APIs accept array inputs or provide batch endpoints
5. **Store credentials securely and rotate them** - Use n8n credential management; never hardcode API keys; implement credential rotation workflows and monitor for unauthorized access
