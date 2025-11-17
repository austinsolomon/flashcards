# Binary Data & Global Context Management - Advanced

## Concept Overview

Binary data handling and global context (workflow static data) are n8n's mechanisms for working with **files, images, PDFs, and maintaining state across workflow executions**. While intermediate users might upload a file or store a simple counter, **advanced users build document processing pipelines, implement distributed locks, create caching layers, and manage complex stateful workflows with proper memory management and cleanup strategies**.

The mastery indicator: advanced users understand the binary data buffer system, know when to use staticData vs external storage, implement proper cleanup to prevent memory leaks, and build production-grade file processing with streaming, chunking, and multi-format support.

## Sophisticated Example: Document Intelligence Pipeline with State Management

This example demonstrates an enterprise document processing system that accepts PDFs, images, and Word docs, uses OCR and AI for extraction, implements caching to avoid reprocessing, maintains processing queues in staticData, and generates multi-format outputs (JSON, CSV, Excel).

```json
{
  "name": "Document Intelligence Pipeline",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "process-document",
        "responseMode": "responseNode",
        "options": {
          "rawBody": true
        }
      },
      "name": "Upload Document",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [250, 500],
      "webhookId": "doc-upload"
    },
    {
      "parameters": {
        "jsCode": "// Extract binary data and validate\nconst items = [];\n\n// Check if binary data exists\nif (!$input.item.binary) {\n  throw new Error('No file uploaded - binary data missing');\n}\n\n// Process each binary file\nfor (const [key, binaryData] of Object.entries($input.item.binary)) {\n  const mimeType = binaryData.mimeType;\n  const fileName = binaryData.fileName || 'unknown';\n  const fileSize = binaryData.fileSize || binaryData.data.length;\n  \n  // Validate file type\n  const supportedTypes = [\n    'application/pdf',\n    'image/jpeg',\n    'image/png',\n    'image/tiff',\n    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',\n    'application/msword'\n  ];\n  \n  if (!supportedTypes.includes(mimeType)) {\n    throw new Error(`Unsupported file type: ${mimeType}`);\n  }\n  \n  // Validate file size (max 50MB)\n  const maxSize = 50 * 1024 * 1024;\n  if (fileSize > maxSize) {\n    throw new Error(`File too large: ${(fileSize / 1024 / 1024).toFixed(2)}MB (max 50MB)`);\n  }\n  \n  // Generate document hash for deduplication\n  const crypto = require('crypto');\n  const fileBuffer = Buffer.from(binaryData.data, 'base64');\n  const documentHash = crypto.createHash('sha256').update(fileBuffer).digest('hex');\n  \n  // Check cache in staticData\n  const cacheKey = `doc_cache_${documentHash}`;\n  const cachedResult = $workflow.staticData[cacheKey];\n  \n  items.push({\n    json: {\n      documentId: `DOC-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,\n      fileName: fileName,\n      mimeType: mimeType,\n      fileSize: fileSize,\n      documentHash: documentHash,\n      uploadedAt: new Date().toISOString(),\n      cached: !!cachedResult,\n      cachedResult: cachedResult || null,\n      binaryKey: key\n    },\n    binary: {\n      document: binaryData\n    }\n  });\n}\n\nreturn items;"
      },
      "name": "Validate & Check Cache",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [450, 500]
    },
    {
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{ $json.cached }}",
              "value2": true
            }
          ]
        }
      },
      "name": "Is Cached?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [650, 500]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "result",
              "name": "processingResult",
              "value": "={{ $json.cachedResult }}",
              "type": "object"
            },
            {
              "id": "source",
              "name": "source",
              "value": "cache",
              "type": "string"
            }
          ]
        }
      },
      "name": "Return Cached Result",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3,
      "position": [850, 400]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.mimeType }}",
              "value2": "application/pdf"
            }
          ]
        }
      },
      "name": "Is PDF?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [850, 600]
    },
    {
      "parameters": {
        "jsCode": "// Extract text from PDF using pdf-parse\nconst pdfParse = require('pdf-parse');\n\nconst binaryData = $input.item.binary.document;\nconst pdfBuffer = Buffer.from(binaryData.data, 'base64');\n\n// Parse PDF\nconst pdfData = await pdfParse(pdfBuffer);\n\nreturn {\n  json: {\n    ...$input.item.json,\n    extraction: {\n      method: 'pdf-parse',\n      text: pdfData.text,\n      numPages: pdfData.numpages,\n      metadata: pdfData.info,\n      version: pdfData.version\n    }\n  },\n  binary: $input.item.binary\n};"
      },
      "name": "Extract PDF Text",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1050, 500]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://vision.googleapis.com/v1/images:annotate",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "googleCloudVisionApi",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({\n  requests: [{\n    image: { content: $binary.document.data },\n    features: [\n      { type: 'TEXT_DETECTION' },\n      { type: 'DOCUMENT_TEXT_DETECTION' },\n      { type: 'LABEL_DETECTION', maxResults: 10 }\n    ]\n  }]\n}) }}"
      },
      "name": "OCR Image",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1050, 700]
    },
    {
      "parameters": {
        "jsCode": "// Parse OCR results from Google Vision\nconst ocrResponse = $input.item.json;\nconst originalData = $('Is PDF?').item.json;\n\nconst textAnnotations = ocrResponse.responses[0].textAnnotations || [];\nconst fullText = textAnnotations[0]?.description || '';\nconst labels = ocrResponse.responses[0].labelAnnotations || [];\n\nreturn {\n  json: {\n    ...originalData,\n    extraction: {\n      method: 'google-vision-ocr',\n      text: fullText,\n      confidence: textAnnotations[0]?.confidence || 0,\n      detectedLabels: labels.map(l => ({ label: l.description, confidence: l.score })),\n      language: ocrResponse.responses[0].textAnnotations?.[0]?.locale || 'unknown'\n    }\n  },\n  binary: $('Is PDF?').item.binary\n};"
      },
      "name": "Parse OCR Results",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1250, 700]
    },
    {
      "parameters": {
        "model": "claude-3-5-sonnet-20241022",
        "prompt": "=Extract structured information from this document.\n\nDocument Text:\n{{ $json.extraction.text }}\n\nExtract and return JSON with:\n{\n  \"documentType\": \"invoice|receipt|contract|form|letter|report|other\",\n  \"entities\": {\n    \"dates\": [\"extracted dates\"],\n    \"amounts\": [\"monetary amounts with currency\"],\n    \"organizations\": [\"company names\"],\n    \"people\": [\"person names\"],\n    \"emails\": [\"email addresses\"],\n    \"phone_numbers\": [\"phone numbers\"],\n    \"addresses\": [\"physical addresses\"]\n  },\n  \"keyFields\": {\n    // Document-specific fields (e.g., for invoice: invoice_number, due_date, total)\n  },\n  \"summary\": \"one sentence summary\",\n  \"confidence\": 0.0-1.0,\n  \"language\": \"detected language code\"\n}",
        "options": {
          "temperature": 0.2,
          "maxTokens": 2000
        }
      },
      "name": "AI: Extract Entities",
      "type": "n8n-nodes-base.anthropic",
      "typeVersion": 1,
      "position": [1450, 600]
    },
    {
      "parameters": {
        "jsCode": "// Parse AI extraction and build final result\nconst extractionData = $input.item.json;\nconst aiResponse = extractionData.output || '{}';\n\n// Parse AI JSON response\nlet structuredData;\ntry {\n  const jsonMatch = aiResponse.match(/```json\\n([\\s\\S]*?)\\n```/) || \n                    aiResponse.match(/\\{[\\s\\S]*\\}/);\n  structuredData = JSON.parse(jsonMatch ? jsonMatch[1] || jsonMatch[0] : aiResponse);\n} catch (e) {\n  structuredData = {\n    documentType: 'unknown',\n    entities: {},\n    summary: 'Extraction failed',\n    confidence: 0\n  };\n}\n\n// Build comprehensive processing result\nconst result = {\n  documentId: extractionData.documentId,\n  fileName: extractionData.fileName,\n  metadata: {\n    fileSize: extractionData.fileSize,\n    mimeType: extractionData.mimeType,\n    documentHash: extractionData.documentHash,\n    uploadedAt: extractionData.uploadedAt,\n    processedAt: new Date().toISOString(),\n    processingTime: Date.now() - new Date(extractionData.uploadedAt).getTime()\n  },\n  extraction: {\n    method: extractionData.extraction.method,\n    rawText: extractionData.extraction.text,\n    textLength: extractionData.extraction.text.length,\n    numPages: extractionData.extraction.numPages || 1,\n    confidence: extractionData.extraction.confidence || 1\n  },\n  structured: structuredData,\n  analytics: {\n    entityCounts: {\n      dates: structuredData.entities?.dates?.length || 0,\n      amounts: structuredData.entities?.amounts?.length || 0,\n      organizations: structuredData.entities?.organizations?.length || 0,\n      people: structuredData.entities?.people?.length || 0,\n      emails: structuredData.entities?.emails?.length || 0,\n      phoneNumbers: structuredData.entities?.phone_numbers?.length || 0\n    },\n    quality: {\n      hasStructuredData: Object.keys(structuredData.entities || {}).length > 0,\n      confidence: structuredData.confidence,\n      completeness: Object.values(structuredData.entities || {}).filter(v => v && v.length > 0).length / 6\n    }\n  }\n};\n\n// Cache result in staticData\nconst cacheKey = `doc_cache_${extractionData.documentHash}`;\n$workflow.staticData[cacheKey] = result;\n$workflow.staticData[`${cacheKey}_timestamp`] = Date.now();\n\n// Implement cache cleanup - remove entries older than 7 days\nconst cacheMaxAge = 7 * 24 * 60 * 60 * 1000;\nfor (const key of Object.keys($workflow.staticData)) {\n  if (key.startsWith('doc_cache_') && key.endsWith('_timestamp')) {\n    const timestamp = $workflow.staticData[key];\n    if (Date.now() - timestamp > cacheMaxAge) {\n      const baseKey = key.replace('_timestamp', '');\n      delete $workflow.staticData[baseKey];\n      delete $workflow.staticData[key];\n    }\n  }\n}\n\nreturn {\n  json: {\n    processingResult: result,\n    source: 'processed'\n  },\n  binary: $input.item.binary\n};"
      },
      "name": "Build & Cache Result",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1650, 600]
    },
    {
      "parameters": {
        "jsCode": "// Generate multiple output formats\nconst data = $input.item.json.processingResult;\n\n// Generate JSON file\nconst jsonContent = JSON.stringify(data, null, 2);\nconst jsonBuffer = Buffer.from(jsonContent);\n\n// Generate CSV file (flattened entities)\nconst entities = data.structured.entities || {};\nconst csvRows = [];\ncsvRows.push(['Entity Type', 'Value']);\nfor (const [type, values] of Object.entries(entities)) {\n  if (Array.isArray(values)) {\n    values.forEach(v => csvRows.push([type, v]));\n  }\n}\nconst csvContent = csvRows.map(row => row.map(cell => `\"${cell}\"`).join(',')).join('\\n');\nconst csvBuffer = Buffer.from(csvContent);\n\n// Generate text summary\nconst summary = `Document Processing Report\n${'='.repeat(50)}\nDocument: ${data.fileName}\nType: ${data.structured.documentType}\nProcessed: ${data.metadata.processedAt}\nProcessing Time: ${data.metadata.processingTime}ms\n\nSummary: ${data.structured.summary}\n\nExtracted Entities:\n${Object.entries(data.analytics.entityCounts)\n  .filter(([_, count]) => count > 0)\n  .map(([type, count]) => `- ${type}: ${count}`)\n  .join('\\n')}\n\nConfidence: ${(data.structured.confidence * 100).toFixed(1)}%\nCompleteness: ${(data.analytics.quality.completeness * 100).toFixed(1)}%\n`;\nconst txtBuffer = Buffer.from(summary);\n\nreturn {\n  json: data,\n  binary: {\n    json_report: {\n      data: jsonBuffer.toString('base64'),\n      mimeType: 'application/json',\n      fileName: `${data.documentId}_report.json`,\n      fileSize: jsonBuffer.length\n    },\n    csv_entities: {\n      data: csvBuffer.toString('base64'),\n      mimeType: 'text/csv',\n      fileName: `${data.documentId}_entities.csv`,\n      fileSize: csvBuffer.length\n    },\n    text_summary: {\n      data: txtBuffer.toString('base64'),\n      mimeType: 'text/plain',\n      fileName: `${data.documentId}_summary.txt`,\n      fileSize: txtBuffer.length\n    },\n    original: $input.item.binary.document\n  }\n};"
      },
      "name": "Generate Output Formats",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1850, 500]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.aws.amazon.com/s3/documents",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "awsS3Api",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "bucket",
              "value": "processed-documents"
            },
            {
              "name": "key",
              "value": "={{ $json.documentId }}/report.json"
            },
            {
              "name": "body",
              "value": "={{ $binary.json_report.data }}"
            },
            {
              "name": "contentType",
              "value": "application/json"
            }
          ]
        }
      },
      "name": "Upload to S3: JSON",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [2050, 400]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.aws.amazon.com/s3/documents",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "awsS3Api",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "bucket",
              "value": "processed-documents"
            },
            {
              "name": "key",
              "value": "={{ $json.documentId }}/entities.csv"
            },
            {
              "name": "body",
              "value": "={{ $binary.csv_entities.data }}"
            },
            {
              "name": "contentType",
              "value": "text/csv"
            }
          ]
        }
      },
      "name": "Upload to S3: CSV",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [2050, 500]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO document_processing_log (\n  document_id,\n  file_name,\n  document_type,\n  file_size,\n  processing_time_ms,\n  extraction_method,\n  entity_count,\n  confidence,\n  cached,\n  created_at\n) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())",
        "options": {
          "queryReplacement": "={{ [\n  $json.documentId,\n  $json.fileName,\n  $json.structured.documentType,\n  $json.metadata.fileSize,\n  $json.metadata.processingTime,\n  $json.extraction.method,\n  Object.values($json.analytics.entityCounts).reduce((a,b) => a+b, 0),\n  $json.structured.confidence,\n  $input.item.json.source === 'cache'\n] }}"
        }
      },
      "name": "Log Processing",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2,
      "position": [2050, 600]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ {\n  success: true,\n  documentId: $json.documentId,\n  fileName: $json.fileName,\n  documentType: $json.structured.documentType,\n  processingTime: $json.metadata.processingTime + 'ms',\n  cached: $('Validate & Check Cache').item.json.source === 'cache',\n  extraction: {\n    method: $json.extraction.method,\n    confidence: ($json.structured.confidence * 100).toFixed(1) + '%',\n    entitiesFound: $json.analytics.entityCounts\n  },\n  outputs: {\n    json: `s3://processed-documents/${$json.documentId}/report.json`,\n    csv: `s3://processed-documents/${$json.documentId}/entities.csv`\n  },\n  summary: $json.structured.summary\n} }}",
        "options": {
          "responseCode": 200
        }
      },
      "name": "Respond with Results",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [2250, 500]
    }
  ],
  "connections": {
    "Upload Document": {
      "main": [
        [
          {
            "node": "Validate & Check Cache",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Validate & Check Cache": {
      "main": [
        [
          {
            "node": "Is Cached?",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Is Cached?": {
      "main": [
        [
          {
            "node": "Return Cached Result",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Is PDF?",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Return Cached Result": {
      "main": [
        [
          {
            "node": "Generate Output Formats",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Is PDF?": {
      "main": [
        [
          {
            "node": "Extract PDF Text",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "OCR Image",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Extract PDF Text": {
      "main": [
        [
          {
            "node": "AI: Extract Entities",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "OCR Image": {
      "main": [
        [
          {
            "node": "Parse OCR Results",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Parse OCR Results": {
      "main": [
        [
          {
            "node": "AI: Extract Entities",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "AI: Extract Entities": {
      "main": [
        [
          {
            "node": "Build & Cache Result",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Build & Cache Result": {
      "main": [
        [
          {
            "node": "Generate Output Formats",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Generate Output Formats": {
      "main": [
        [
          {
            "node": "Upload to S3: JSON",
            "type": "main",
            "index": 0
          },
          {
            "node": "Upload to S3: CSV",
            "type": "main",
            "index": 0
          },
          {
            "node": "Log Processing",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Upload to S3: JSON": {
      "main": [
        [
          {
            "node": "Respond with Results",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Upload to S3: CSV": {
      "main": [
        [
          {
            "node": "Respond with Results",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Log Processing": {
      "main": [
        [
          {
            "node": "Respond with Results",
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

1. **Binary Data Manipulation**: Extracts, validates, processes PDFs and images; converts between base64 and Buffer; handles multiple binary outputs
2. **Hash-Based Deduplication**: Uses SHA-256 hashing of file contents to detect duplicate uploads and return cached results
3. **Global Context Caching**: Stores processing results in `$workflow.staticData` indexed by document hash for instant retrieval
4. **Cache Cleanup Strategy**: Implements automatic cleanup of cached entries older than 7 days to prevent memory bloat
5. **Multi-Format Output**: Generates JSON, CSV, and TXT from same data; creates multiple binary outputs in single node
6. **Binary File Properties**: Properly sets mimeType, fileName, fileSize for all generated files
7. **Document Type Routing**: Different processing paths for PDFs (pdf-parse) vs images (OCR)

## Best Practices for Binary Data & Global Context Mastery

1. **Always validate binary data before processing** - Check mimeType, fileSize, and data existence; implement size limits; validate formats with magic bytes; prevent memory exhaustion from large uploads
2. **Use hash-based deduplication for expensive operations** - Hash file contents (SHA-256) before OCR/AI processing; cache results in staticData or external storage; dramatically reduces costs and latency
3. **Implement aggressive cache cleanup in staticData** - Set expiration timestamps; clean up old entries on every run; staticData persists forever and can grow indefinitely; monitor memory usage
4. **Prefer external storage for large binaries** - Use staticData for small metadata/results; upload large files (>10MB) to S3/GCS immediately; store only URLs in workflow; prevents workflow size bloat
5. **Generate multiple output formats in parallel** - Create JSON/CSV/Excel/PDF outputs from same data; use binary data system to attach multiple files; enables flexible downstream consumption; batch uploads to storage
