# Expressions & Data Linking - Intermediate

## Concept Overview

Expressions are n8n's templating language that transforms static configurations into dynamic, data-driven workflows. While beginners use simple `{{ $json.field }}` references, **intermediate users master complex expressions with $node(), $runIndex, DateTime manipulation, conditional logic, array operations, and cross-node data merging**.

The key differentiator: intermediate users understand the expression execution context (which nodes are available, item vs all items, previous vs specific node references) and use expressions to eliminate the need for many Code nodes.

## Sophisticated Example: Dynamic Multi-Source Report Generator

This example demonstrates building a weekly executive report that pulls data from multiple APIs, uses expressions for data transformation, conditional formatting, date range calculations, aggregations, and cross-node data merging - all without Code nodes.

```json
{
  "name": "Executive Report Generator",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 8 * * MON"
            }
          ]
        }
      },
      "name": "Weekly Monday 8 AM",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1,
      "position": [250, 500]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "report_week_start",
              "name": "weekStart",
              "value": "={{ $now.minus({ days: 7 }).startOf('week').toISO() }}",
              "type": "string"
            },
            {
              "id": "report_week_end",
              "name": "weekEnd",
              "value": "={{ $now.minus({ days: 1 }).endOf('day').toISO() }}",
              "type": "string"
            },
            {
              "id": "report_title",
              "name": "reportTitle",
              "value": "={{ 'Executive Report - Week of ' + $now.minus({ days: 7 }).toFormat('MMM dd, yyyy') }}",
              "type": "string"
            },
            {
              "id": "fiscal_quarter",
              "name": "fiscalQuarter",
              "value": "={{ 'Q' + Math.ceil($now.month / 3) + ' ' + $now.year }}",
              "type": "string"
            },
            {
              "id": "week_number",
              "name": "weekNumber",
              "value": "={{ $now.weekNumber }}",
              "type": "number"
            }
          ]
        }
      },
      "name": "Calculate Report Period",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3,
      "position": [450, 500]
    },
    {
      "parameters": {
        "method": "GET",
        "url": "https://api.stripe.com/v1/charges",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "stripeApi",
        "sendQuery": true,
        "queryParameters": {
          "parameters": [
            {
              "name": "created[gte]",
              "value": "={{ Math.floor(DateTime.fromISO($('Calculate Report Period').item.json.weekStart).toSeconds()) }}"
            },
            {
              "name": "created[lte]",
              "value": "={{ Math.floor(DateTime.fromISO($('Calculate Report Period').item.json.weekEnd).toSeconds()) }}"
            },
            {
              "name": "limit",
              "value": "100"
            }
          ]
        }
      },
      "name": "Fetch Stripe Revenue",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [650, 300]
    },
    {
      "parameters": {
        "method": "GET",
        "url": "https://api.hubspot.com/crm/v3/objects/deals",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "hubspotApi",
        "sendQuery": true,
        "queryParameters": {
          "parameters": [
            {
              "name": "properties",
              "value": "dealname,amount,dealstage,closedate,pipeline"
            },
            {
              "name": "filterGroups[0][filters][0][propertyName]",
              "value": "closedate"
            },
            {
              "name": "filterGroups[0][filters][0][operator]",
              "value": "GTE"
            },
            {
              "name": "filterGroups[0][filters][0][value]",
              "value": "={{ $('Calculate Report Period').item.json.weekStart }}"
            }
          ]
        }
      },
      "name": "Fetch HubSpot Deals",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [650, 500]
    },
    {
      "parameters": {
        "method": "GET",
        "url": "https://api.intercom.io/conversations/search",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "intercomApi",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "query",
              "value": "={{ {\n  field: 'created_at',\n  operator: '>',\n  value: Math.floor(DateTime.fromISO($('Calculate Report Period').item.json.weekStart).toSeconds())\n} }}"
            }
          ]
        }
      },
      "name": "Fetch Support Tickets",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [650, 700]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "total_revenue",
              "name": "totalRevenue",
              "value": "={{ $json.data.reduce((sum, charge) => sum + (charge.amount / 100), 0) }}",
              "type": "number"
            },
            {
              "id": "successful_charges",
              "name": "successfulCharges",
              "value": "={{ $json.data.filter(c => c.status === 'succeeded').length }}",
              "type": "number"
            },
            {
              "id": "failed_charges",
              "name": "failedCharges",
              "value": "={{ $json.data.filter(c => c.status === 'failed').length }}",
              "type": "number"
            },
            {
              "id": "success_rate",
              "name": "successRate",
              "value": "={{ ($json.data.length > 0 ? ($json.data.filter(c => c.status === 'succeeded').length / $json.data.length * 100).toFixed(2) : 0) }}",
              "type": "number"
            },
            {
              "id": "avg_transaction",
              "name": "avgTransaction",
              "value": "={{ ($json.data.length > 0 ? ($json.data.reduce((sum, c) => sum + c.amount, 0) / $json.data.length / 100).toFixed(2) : 0) }}",
              "type": "number"
            },
            {
              "id": "unique_customers",
              "name": "uniqueCustomers",
              "value": "={{ [...new Set($json.data.map(c => c.customer))].length }}",
              "type": "number"
            },
            {
              "id": "revenue_by_day",
              "name": "revenueByDay",
              "value": "={{ $json.data.reduce((acc, charge) => {\n  const day = DateTime.fromSeconds(charge.created).toFormat('yyyy-MM-dd');\n  acc[day] = (acc[day] || 0) + (charge.amount / 100);\n  return acc;\n}, {}) }}",
              "type": "object"
            }
          ]
        }
      },
      "name": "Analyze Revenue Metrics",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3,
      "position": [850, 300]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "total_deals",
              "name": "totalDeals",
              "value": "={{ $json.results?.length || 0 }}",
              "type": "number"
            },
            {
              "id": "total_deal_value",
              "name": "totalDealValue",
              "value": "={{ ($json.results || []).reduce((sum, deal) => sum + (parseFloat(deal.properties.amount) || 0), 0) }}",
              "type": "number"
            },
            {
              "id": "closed_won",
              "name": "closedWon",
              "value": "={{ ($json.results || []).filter(d => d.properties.dealstage === 'closedwon').length }}",
              "type": "number"
            },
            {
              "id": "closed_lost",
              "name": "closedLost",
              "value": "={{ ($json.results || []).filter(d => d.properties.dealstage === 'closedlost').length }}",
              "type": "number"
            },
            {
              "id": "win_rate",
              "name": "winRate",
              "value": "={{ (() => {\n  const closed = ($json.results || []).filter(d => d.properties.dealstage?.startsWith('closed'));\n  const won = closed.filter(d => d.properties.dealstage === 'closedwon');\n  return closed.length > 0 ? (won.length / closed.length * 100).toFixed(2) : 0;\n})() }}",
              "type": "number"
            },
            {
              "id": "avg_deal_size",
              "name": "avgDealSize",
              "value": "={{ (() => {\n  const results = $json.results || [];\n  const total = results.reduce((sum, d) => sum + (parseFloat(d.properties.amount) || 0), 0);\n  return results.length > 0 ? (total / results.length).toFixed(2) : 0;\n})() }}",
              "type": "number"
            },
            {
              "id": "pipeline_breakdown",
              "name": "pipelineBreakdown",
              "value": "={{ ($json.results || []).reduce((acc, deal) => {\n  const pipeline = deal.properties.pipeline || 'Unknown';\n  acc[pipeline] = (acc[pipeline] || 0) + 1;\n  return acc;\n}, {}) }}",
              "type": "object"
            }
          ]
        }
      },
      "name": "Analyze Sales Metrics",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3,
      "position": [850, 500]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "total_tickets",
              "name": "totalTickets",
              "value": "={{ $json.conversations?.length || 0 }}",
              "type": "number"
            },
            {
              "id": "open_tickets",
              "name": "openTickets",
              "value": "={{ ($json.conversations || []).filter(c => c.state === 'open').length }}",
              "type": "number"
            },
            {
              "id": "closed_tickets",
              "name": "closedTickets",
              "value": "={{ ($json.conversations || []).filter(c => c.state === 'closed').length }}",
              "type": "number"
            },
            {
              "id": "avg_response_time",
              "name": "avgResponseTime",
              "value": "={{ (() => {\n  const convos = $json.conversations || [];\n  if (convos.length === 0) return 0;\n  const totalSeconds = convos.reduce((sum, c) => {\n    return sum + (c.statistics?.time_to_first_response || 0);\n  }, 0);\n  const avgSeconds = totalSeconds / convos.length;\n  return (avgSeconds / 3600).toFixed(2);\n})() }}",
              "type": "number"
            },
            {
              "id": "satisfaction_score",
              "name": "satisfactionScore",
              "value": "={{ (() => {\n  const rated = ($json.conversations || []).filter(c => c.rating?.rating);\n  if (rated.length === 0) return 'N/A';\n  const sum = rated.reduce((s, c) => s + c.rating.rating, 0);\n  return (sum / rated.length).toFixed(2);\n})() }}",
              "type": "string"
            },
            {
              "id": "tickets_by_priority",
              "name": "ticketsByPriority",
              "value": "={{ ($json.conversations || []).reduce((acc, ticket) => {\n  const priority = ticket.priority || 'normal';\n  acc[priority] = (acc[priority] || 0) + 1;\n  return acc;\n}, {}) }}",
              "type": "object"
            }
          ]
        }
      },
      "name": "Analyze Support Metrics",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3,
      "position": [850, 700]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "report",
              "name": "executiveReport",
              "value": "={{ {\n  // Report metadata\n  title: $('Calculate Report Period').item.json.reportTitle,\n  period: {\n    start: $('Calculate Report Period').item.json.weekStart,\n    end: $('Calculate Report Period').item.json.weekEnd,\n    weekNumber: $('Calculate Report Period').item.json.weekNumber,\n    fiscalQuarter: $('Calculate Report Period').item.json.fiscalQuarter\n  },\n  generatedAt: $now.toISO(),\n  \n  // Revenue section\n  revenue: {\n    total: $('Analyze Revenue Metrics').item.json.totalRevenue,\n    formatted: '$' + $('Analyze Revenue Metrics').item.json.totalRevenue.toLocaleString('en-US', {minimumFractionDigits: 2}),\n    successfulCharges: $('Analyze Revenue Metrics').item.json.successfulCharges,\n    failedCharges: $('Analyze Revenue Metrics').item.json.failedCharges,\n    successRate: $('Analyze Revenue Metrics').item.json.successRate + '%',\n    avgTransaction: $('Analyze Revenue Metrics').item.json.avgTransaction,\n    uniqueCustomers: $('Analyze Revenue Metrics').item.json.uniqueCustomers,\n    revenueByDay: $('Analyze Revenue Metrics').item.json.revenueByDay,\n    trend: (() => {\n      const days = Object.values($('Analyze Revenue Metrics').item.json.revenueByDay);\n      const firstHalf = days.slice(0, Math.ceil(days.length/2)).reduce((a,b) => a+b, 0);\n      const secondHalf = days.slice(Math.ceil(days.length/2)).reduce((a,b) => a+b, 0);\n      return secondHalf > firstHalf ? '📈 Increasing' : '📉 Decreasing';\n    })()\n  },\n  \n  // Sales section\n  sales: {\n    totalDeals: $('Analyze Sales Metrics').item.json.totalDeals,\n    totalValue: '$' + $('Analyze Sales Metrics').item.json.totalDealValue.toLocaleString('en-US'),\n    closedWon: $('Analyze Sales Metrics').item.json.closedWon,\n    closedLost: $('Analyze Sales Metrics').item.json.closedLost,\n    winRate: $('Analyze Sales Metrics').item.json.winRate + '%',\n    avgDealSize: '$' + parseFloat($('Analyze Sales Metrics').item.json.avgDealSize).toLocaleString('en-US'),\n    pipelineBreakdown: $('Analyze Sales Metrics').item.json.pipelineBreakdown,\n    performance: $('Analyze Sales Metrics').item.json.winRate >= 50 ? '✅ Exceeds Target' : '⚠️ Below Target'\n  },\n  \n  // Support section\n  support: {\n    totalTickets: $('Analyze Support Metrics').item.json.totalTickets,\n    openTickets: $('Analyze Support Metrics').item.json.openTickets,\n    closedTickets: $('Analyze Support Metrics').item.json.closedTickets,\n    closeRate: ($('Analyze Support Metrics').item.json.totalTickets > 0 ? ($('Analyze Support Metrics').item.json.closedTickets / $('Analyze Support Metrics').item.json.totalTickets * 100).toFixed(2) : 0) + '%',\n    avgResponseTime: $('Analyze Support Metrics').item.json.avgResponseTime + ' hours',\n    satisfactionScore: $('Analyze Support Metrics').item.json.satisfactionScore,\n    ticketsByPriority: $('Analyze Support Metrics').item.json.ticketsByPriority,\n    slaCompliance: parseFloat($('Analyze Support Metrics').item.json.avgResponseTime) <= 4 ? '✅ Met SLA' : '❌ Missed SLA'\n  },\n  \n  // Executive summary (cross-metric insights)\n  summary: {\n    keyWins: [\n      $('Analyze Revenue Metrics').item.json.successRate >= 95 ? 'Payment success rate above 95%' : null,\n      $('Analyze Sales Metrics').item.json.winRate >= 50 ? 'Win rate exceeds 50%' : null,\n      parseFloat($('Analyze Support Metrics').item.json.avgResponseTime) <= 4 ? 'Support response time under 4 hours' : null\n    ].filter(w => w !== null),\n    concerns: [\n      $('Analyze Revenue Metrics').item.json.successRate < 90 ? 'Payment success rate below 90%' : null,\n      $('Analyze Sales Metrics').item.json.winRate < 40 ? 'Win rate below 40%' : null,\n      parseFloat($('Analyze Support Metrics').item.json.avgResponseTime) > 8 ? 'Support response time over 8 hours' : null\n    ].filter(c => c !== null),\n    revenuePerTicket: $('Analyze Support Metrics').item.json.totalTickets > 0 ? \n      '$' + ($('Analyze Revenue Metrics').item.json.totalRevenue / $('Analyze Support Metrics').item.json.totalTickets).toFixed(2) : 'N/A',\n    customersPerDeal: $('Analyze Sales Metrics').item.json.totalDeals > 0 ?\n      ($('Analyze Revenue Metrics').item.json.uniqueCustomers / $('Analyze Sales Metrics').item.json.totalDeals).toFixed(2) : 'N/A'\n  }\n} }}",
              "type": "object"
            }
          ]
        }
      },
      "name": "Merge Report Data",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3,
      "position": [1050, 500]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.sendgrid.com/v3/mail/send",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "sendGridApi",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({\n  personalizations: [{\n    to: [\n      { email: 'ceo@company.com', name: 'CEO' },\n      { email: 'cfo@company.com', name: 'CFO' },\n      { email: 'coo@company.com', name: 'COO' }\n    ],\n    dynamic_template_data: $json.executiveReport\n  }],\n  from: { email: 'reports@company.com', name: 'Executive Reporting' },\n  template_id: 'd-executive-report-template',\n  attachments: [{\n    content: Buffer.from(JSON.stringify($json.executiveReport, null, 2)).toString('base64'),\n    filename: `executive-report-week-${$('Calculate Report Period').item.json.weekNumber}.json`,\n    type: 'application/json',\n    disposition: 'attachment'\n  }]\n}) }}"
      },
      "name": "Send Executive Report",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1250, 500]
    }
  ],
  "connections": {
    "Weekly Monday 8 AM": {
      "main": [
        [
          {
            "node": "Calculate Report Period",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Calculate Report Period": {
      "main": [
        [
          {
            "node": "Fetch Stripe Revenue",
            "type": "main",
            "index": 0
          },
          {
            "node": "Fetch HubSpot Deals",
            "type": "main",
            "index": 0
          },
          {
            "node": "Fetch Support Tickets",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Fetch Stripe Revenue": {
      "main": [
        [
          {
            "node": "Analyze Revenue Metrics",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Fetch HubSpot Deals": {
      "main": [
        [
          {
            "node": "Analyze Sales Metrics",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Fetch Support Tickets": {
      "main": [
        [
          {
            "node": "Analyze Support Metrics",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Analyze Revenue Metrics": {
      "main": [
        [
          {
            "node": "Merge Report Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Analyze Sales Metrics": {
      "main": [
        [
          {
            "node": "Merge Report Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Analyze Support Metrics": {
      "main": [
        [
          {
            "node": "Merge Report Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Merge Report Data": {
      "main": [
        [
          {
            "node": "Send Executive Report",
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

1. **DateTime Manipulation**: Uses `$now.minus()`, `.startOf()`, `.toFormat()`, `.weekNumber` for complex date calculations
2. **Cross-Node References**: Final merge node uses `$('Node Name').item.json.field` to pull data from multiple upstream nodes
3. **Array Operations**: Uses `.filter()`, `.reduce()`, `.map()` within expressions for aggregations and transformations
4. **Conditional Logic**: Implements ternary operators, null coalescing, and complex conditionals for dynamic values
5. **IIFE Patterns**: Uses immediately-invoked function expressions `(() => { ... })()` for multi-step calculations within expressions
6. **Object Construction**: Builds complex nested objects entirely in expressions, eliminating need for Code nodes
7. **Data Formatting**: Number formatting, string interpolation, emoji indicators - all in expressions

## Best Practices for Expression Mastery

1. **Master node reference patterns** - Use `$json` for current item, `$node['Name'].json` for specific node, `$('Name').all()` for all items from a node; understand execution context and which nodes are available
2. **Leverage DateTime for all date operations** - Use `$now`, `.plus()`, `.minus()`, `.startOf()`, `.endOf()`, `.toFormat()` instead of native JS Date; supports timezones and complex manipulations
3. **Use array methods instead of Code nodes** - `.filter()`, `.map()`, `.reduce()`, `.find()`, `.some()`, `.every()` can handle most transformations; combine with spread operator and destructuring
4. **Implement defensive null-checking** - Use optional chaining `?.`, null coalescing `||`, and ternaries to handle missing data; always provide fallback values for robustness
5. **Break complex expressions into multiple Set nodes** - Don't create unreadable mega-expressions; use intermediate Set nodes to build up complexity step-by-step; improves debuggability and maintainability
