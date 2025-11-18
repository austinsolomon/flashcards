# Code Node (JavaScript Execution) - Advanced

## Concept Overview

The Code Node is where n8n transforms from a no-code tool into a full programming environment. While intermediate users write basic transformations, **advanced users leverage async/await, external libraries, streaming data processing, complex algorithms, and maintain stateful computations** across workflow executions.

The mastery indicator: advanced users treat Code Nodes as microservices within workflows, implementing production-grade algorithms with proper error boundaries, type safety patterns, and performance optimization.

## Sophisticated Example: Real-Time Anomaly Detection Engine

This example implements a sophisticated streaming anomaly detection system using statistical methods (z-score, moving averages, and Isolation Forest approximation) to identify unusual patterns in IoT sensor data.

```json
{
  "name": "IoT Anomaly Detection Engine",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "sensor-data",
        "responseMode": "responseNode"
      },
      "name": "Sensor Data Stream",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [250, 400]
    },
    {
      "parameters": {
        "jsCode": "/**\n * Advanced Anomaly Detection Engine\n * Implements multiple detection algorithms:\n * 1. Statistical Z-Score (standard deviations from mean)\n * 2. Moving Average Convergence Divergence (MACD)\n * 3. Isolation Forest approximation (simplified)\n * 4. Rate-of-change detection\n */\n\n// ============= CONFIGURATION =============\nconst CONFIG = {\n  zScoreThreshold: 3.0,           // Standard deviations for outlier\n  macdShortWindow: 12,            // Fast EMA period\n  macdLongWindow: 26,             // Slow EMA period\n  macdSignalWindow: 9,            // Signal line period\n  historicalWindow: 100,          // Number of points to maintain\n  rateOfChangeWindow: 5,          // Window for derivative calculation\n  isolationTreeDepth: 8,          // Depth for isolation scoring\n  anomalyScoreThreshold: 0.7      // Combined score threshold (0-1)\n};\n\n// ============= HELPER FUNCTIONS =============\n\n/**\n * Calculate Exponential Moving Average\n */\nfunction calculateEMA(data, period) {\n  const k = 2 / (period + 1);\n  let ema = data[0];\n  const result = [ema];\n  \n  for (let i = 1; i < data.length; i++) {\n    ema = data[i] * k + ema * (1 - k);\n    result.push(ema);\n  }\n  \n  return result;\n}\n\n/**\n * Calculate statistical metrics\n */\nfunction calculateStats(values) {\n  const n = values.length;\n  const mean = values.reduce((a, b) => a + b, 0) / n;\n  const variance = values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / n;\n  const stdDev = Math.sqrt(variance);\n  \n  return { mean, stdDev, variance };\n}\n\n/**\n * Z-Score anomaly detection\n */\nfunction detectZScoreAnomaly(value, historicalValues, threshold) {\n  const stats = calculateStats(historicalValues);\n  const zScore = Math.abs((value - stats.mean) / stats.stdDev);\n  \n  return {\n    isAnomaly: zScore > threshold,\n    score: Math.min(zScore / threshold, 1.0),\n    mean: stats.mean,\n    stdDev: stats.stdDev,\n    zScore: zScore\n  };\n}\n\n/**\n * MACD-based trend anomaly detection\n */\nfunction detectMACD(values) {\n  if (values.length < CONFIG.macdLongWindow) {\n    return { isAnomaly: false, score: 0, signal: 'insufficient_data' };\n  }\n  \n  const shortEMA = calculateEMA(values, CONFIG.macdShortWindow);\n  const longEMA = calculateEMA(values, CONFIG.macdLongWindow);\n  \n  // Calculate MACD line\n  const macdLine = shortEMA.map((val, i) => val - longEMA[i]);\n  \n  // Calculate signal line (EMA of MACD)\n  const signalLine = calculateEMA(macdLine.slice(-CONFIG.macdSignalWindow), CONFIG.macdSignalWindow);\n  \n  const currentMACD = macdLine[macdLine.length - 1];\n  const currentSignal = signalLine[signalLine.length - 1];\n  const divergence = Math.abs(currentMACD - currentSignal);\n  \n  // Normalize divergence to 0-1 score\n  const maxDivergence = Math.max(...macdLine.map((m, i) => \n    Math.abs(m - (signalLine[i] || 0))\n  ));\n  const score = maxDivergence > 0 ? divergence / maxDivergence : 0;\n  \n  return {\n    isAnomaly: score > 0.6,\n    score: score,\n    macd: currentMACD,\n    signal: currentSignal,\n    divergence: divergence\n  };\n}\n\n/**\n * Rate of change anomaly (sudden spikes/drops)\n */\nfunction detectRateOfChange(values, window) {\n  if (values.length < window + 1) {\n    return { isAnomaly: false, score: 0 };\n  }\n  \n  const recent = values.slice(-window);\n  const derivatives = [];\n  \n  for (let i = 1; i < recent.length; i++) {\n    derivatives.push(Math.abs(recent[i] - recent[i-1]));\n  }\n  \n  const currentDerivative = Math.abs(values[values.length - 1] - values[values.length - 2]);\n  const stats = calculateStats(derivatives);\n  const rateScore = stats.stdDev > 0 ? \n    Math.min((currentDerivative - stats.mean) / stats.stdDev / 3, 1.0) : 0;\n  \n  return {\n    isAnomaly: rateScore > 0.7,\n    score: Math.max(0, rateScore),\n    derivative: currentDerivative,\n    avgDerivative: stats.mean\n  };\n}\n\n/**\n * Simplified Isolation Forest score\n * Approximates isolation depth based on value position in distribution\n */\nfunction calculateIsolationScore(value, historicalValues, maxDepth) {\n  const sorted = [...historicalValues].sort((a, b) => a - b);\n  const position = sorted.findIndex(v => v >= value);\n  const normalizedPosition = position / sorted.length;\n  \n  // Values in tails (close to 0 or 1) are more isolated\n  const tailDistance = Math.min(\n    normalizedPosition,\n    1 - normalizedPosition\n  );\n  \n  // Convert to isolation score (higher = more anomalous)\n  const isolationScore = 1 - (tailDistance * 2);\n  \n  return {\n    isAnomaly: isolationScore > 0.8,\n    score: isolationScore,\n    percentilePosition: normalizedPosition\n  };\n}\n\n// ============= MAIN PROCESSING =============\n\n// Parse incoming sensor data\nconst payload = $input.item.json;\nconst sensorId = payload.sensor_id;\nconst reading = parseFloat(payload.value);\nconst timestamp = payload.timestamp || new Date().toISOString();\nconst metadata = payload.metadata || {};\n\n// Retrieve historical data from workflow static data (or initialize)\nconst historicalKey = `sensor_${sensorId}_history`;\nlet historicalData = $workflow.staticData[historicalKey] || [];\n\n// Add current reading to history\nhistoricalData.push({\n  value: reading,\n  timestamp: timestamp\n});\n\n// Maintain sliding window\nif (historicalData.length > CONFIG.historicalWindow) {\n  historicalData = historicalData.slice(-CONFIG.historicalWindow);\n}\n\n// Update static data\n$workflow.staticData[historicalKey] = historicalData;\n\n// Extract values for analysis\nconst values = historicalData.map(d => d.value);\n\n// ============= RUN DETECTION ALGORITHMS =============\n\nlet detectionResults = {\n  timestamp: timestamp,\n  sensorId: sensorId,\n  currentValue: reading,\n  metadata: metadata\n};\n\n// Only run detection if we have sufficient historical data\nif (values.length >= 30) {\n  const zScoreResult = detectZScoreAnomaly(reading, values.slice(0, -1), CONFIG.zScoreThreshold);\n  const macdResult = detectMACD(values);\n  const rateResult = detectRateOfChange(values, CONFIG.rateOfChangeWindow);\n  const isolationResult = calculateIsolationScore(reading, values.slice(0, -1), CONFIG.isolationTreeDepth);\n  \n  // Calculate weighted composite anomaly score\n  const compositeScore = (\n    zScoreResult.score * 0.30 +\n    macdResult.score * 0.25 +\n    rateResult.score * 0.25 +\n    isolationResult.score * 0.20\n  );\n  \n  const isAnomaly = compositeScore >= CONFIG.anomalyScoreThreshold;\n  \n  // Determine anomaly type\n  let anomalyType = 'normal';\n  if (isAnomaly) {\n    if (rateResult.score > 0.8) anomalyType = 'sudden_change';\n    else if (zScoreResult.score > 0.8) anomalyType = 'outlier';\n    else if (macdResult.score > 0.7) anomalyType = 'trend_divergence';\n    else anomalyType = 'composite_anomaly';\n  }\n  \n  detectionResults = {\n    ...detectionResults,\n    \n    // Overall results\n    isAnomaly: isAnomaly,\n    anomalyType: anomalyType,\n    compositeScore: compositeScore,\n    confidence: compositeScore,\n    \n    // Individual algorithm results\n    algorithms: {\n      zScore: {\n        detected: zScoreResult.isAnomaly,\n        score: zScoreResult.score,\n        value: zScoreResult.zScore,\n        mean: zScoreResult.mean,\n        stdDev: zScoreResult.stdDev\n      },\n      macd: {\n        detected: macdResult.isAnomaly,\n        score: macdResult.score,\n        macd: macdResult.macd,\n        signal: macdResult.signal,\n        divergence: macdResult.divergence\n      },\n      rateOfChange: {\n        detected: rateResult.isAnomaly,\n        score: rateResult.score,\n        currentRate: rateResult.derivative,\n        avgRate: rateResult.avgDerivative\n      },\n      isolation: {\n        detected: isolationResult.isAnomaly,\n        score: isolationResult.score,\n        percentile: isolationResult.percentilePosition\n      }\n    },\n    \n    // Statistical context\n    statistics: {\n      historicalCount: values.length,\n      ...calculateStats(values)\n    },\n    \n    // Processing metadata\n    processingTime: new Date().toISOString(),\n    configUsed: CONFIG\n  };\n} else {\n  detectionResults = {\n    ...detectionResults,\n    isAnomaly: false,\n    anomalyType: 'insufficient_data',\n    message: `Need at least 30 data points, currently have ${values.length}`,\n    historicalCount: values.length\n  };\n}\n\nreturn { json: detectionResults };"
      },
      "name": "Anomaly Detection Engine",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [450, 400]
    },
    {
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{ $json.isAnomaly }}",
              "value2": true
            }
          ]
        }
      },
      "name": "Is Anomaly?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [650, 400]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "alert",
              "name": "alert",
              "value": "={{ {\n  severity: $json.compositeScore > 0.9 ? 'critical' : ($json.compositeScore > 0.8 ? 'high' : 'medium'),\n  title: `Anomaly detected on sensor ${$json.sensorId}`,\n  description: `${$json.anomalyType}: value ${$json.currentValue} (score: ${$json.compositeScore.toFixed(3)})`,\n  sensorId: $json.sensorId,\n  value: $json.currentValue,\n  timestamp: $json.timestamp,\n  algorithms: Object.keys($json.algorithms).filter(k => $json.algorithms[k].detected).join(', '),\n  context: {\n    mean: $json.statistics.mean.toFixed(2),\n    stdDev: $json.statistics.stdDev.toFixed(2),\n    zScore: $json.algorithms.zScore.value.toFixed(2)\n  }\n} }}",
              "type": "object"
            }
          ]
        },
        "options": {}
      },
      "name": "Build Alert",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3,
      "position": [850, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.pagerduty.com/incidents",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "pagerDutyApi",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({\n  incident: {\n    type: 'incident',\n    title: $json.alert.title,\n    service: { id: $env('PAGERDUTY_SERVICE_ID'), type: 'service_reference' },\n    urgency: $json.alert.severity === 'critical' ? 'high' : 'low',\n    body: {\n      type: 'incident_body',\n      details: $json.alert.description + '\\n\\nContext: ' + JSON.stringify($json.alert.context, null, 2)\n    }\n  }\n}) }}"
      },
      "name": "Alert PagerDuty",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1050, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO sensor_anomalies (sensor_id, timestamp, value, anomaly_type, composite_score, algorithms, statistics, created_at)\nVALUES ($1, $2, $3, $4, $5, $6, $7, NOW())",
        "options": {
          "queryReplacement": "={{ [\n  $json.sensorId,\n  $json.timestamp,\n  $json.currentValue,\n  $json.anomalyType,\n  $json.compositeScore,\n  JSON.stringify($json.algorithms),\n  JSON.stringify($json.statistics)\n] }}"
        }
      },
      "name": "Log Anomaly",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2,
      "position": [850, 500]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO sensor_readings (sensor_id, timestamp, value, is_anomaly, composite_score, created_at)\nVALUES ($1, $2, $3, $4, $5, NOW())",
        "options": {
          "queryReplacement": "={{ [$json.sensorId, $json.timestamp, $json.currentValue, $json.isAnomaly, $json.compositeScore || 0] }}"
        }
      },
      "name": "Store Reading",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2,
      "position": [850, 600]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ {\n  received: true,\n  sensorId: $('Anomaly Detection Engine').item.json.sensorId,\n  timestamp: $('Anomaly Detection Engine').item.json.timestamp,\n  isAnomaly: $('Anomaly Detection Engine').item.json.isAnomaly,\n  score: $('Anomaly Detection Engine').item.json.compositeScore,\n  message: $('Anomaly Detection Engine').item.json.isAnomaly ? 'Anomaly detected and alert triggered' : 'Normal reading processed'\n} }}",
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
    "Sensor Data Stream": {
      "main": [
        [
          {
            "node": "Anomaly Detection Engine",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Anomaly Detection Engine": {
      "main": [
        [
          {
            "node": "Is Anomaly?",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Is Anomaly?": {
      "main": [
        [
          {
            "node": "Build Alert",
            "type": "main",
            "index": 0
          },
          {
            "node": "Log Anomaly",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Store Reading",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Build Alert": {
      "main": [
        [
          {
            "node": "Alert PagerDuty",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Alert PagerDuty": {
      "main": [
        [
          {
            "node": "Respond",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Log Anomaly": {
      "main": [
        [
          {
            "node": "Respond",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Store Reading": {
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

1. **Production-Grade Algorithms**: Implements multiple statistical methods (Z-Score, MACD, Rate-of-Change, Isolation Forest approximation)
2. **Stateful Processing**: Uses `$workflow.staticData` to maintain rolling historical data across executions
3. **Composite Scoring**: Combines multiple detection algorithms with weighted averaging for robust detection
4. **Comprehensive Documentation**: Includes detailed JSDoc comments explaining algorithm choices and parameters
5. **Performance Optimization**: Maintains sliding windows instead of unbounded growth
6. **Type Safety Patterns**: Defensive programming with null checks and fallback values

## Best Practices for Code Node Mastery

1. **Use workflow.staticData for cross-execution state** - Store rolling windows, counters, or caches in `$workflow.staticData` to maintain state; implement proper cleanup and size limits to prevent memory bloat
2. **Structure complex code with clear sections** - Use comments, helper functions, and configuration objects; treat Code Nodes as mini-modules with defined inputs/outputs and error boundaries
3. **Implement proper error handling with context** - Wrap risky operations in try-catch; throw errors with descriptive messages including input context; never fail silently
4. **Optimize for n8n's execution model** - Minimize loops over `$input.all()`; prefer vectorized operations; use lazy evaluation; remember Code Node runs once per item unless you access $input.all()
5. **Leverage external libraries strategically** - Use `require()` for specialized algorithms (moment, lodash, mathjs) but be aware of cold start costs; prefer native JavaScript for simple operations; cache library imports in static data
