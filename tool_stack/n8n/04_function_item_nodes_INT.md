# Function & Function-Item Nodes - Intermediate

## Concept Overview

Function and Function-Item nodes are n8n's original JavaScript execution tools (now largely replaced by Code node, but still valuable for understanding execution contexts). The **critical distinction**: Function processes ALL items together in one execution, while Function-Item runs separately for EACH item.

**Intermediate users master this distinction** to choose the right execution model: use Function-Item for transforming individual records, use Function (or Code with `$input.all()`) for aggregations, deduplication, and cross-item operations.

## Sophisticated Example: E-commerce Order Consolidation & Pricing Engine

This example demonstrates processing multiple order line items - using Function-Item to enrich each item individually, then Function to consolidate, apply bulk discounts, calculate shipping, and generate invoice totals.

```json
{
  "name": "Order Processing & Consolidation",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "process-order",
        "responseMode": "responseNode"
      },
      "name": "Receive Order",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [250, 400]
    },
    {
      "parameters": {
        "jsCode": "// Extract order items from incoming order\nconst order = $input.item.json;\nconst orderItems = order.items || [];\n\nif (!Array.isArray(orderItems) || orderItems.length === 0) {\n  throw new Error('Order must contain at least one item');\n}\n\n// Create separate item for each product in order\nconst outputItems = orderItems.map((item, index) => ({\n  json: {\n    orderId: order.order_id,\n    customerId: order.customer_id,\n    customerEmail: order.customer_email,\n    shippingAddress: order.shipping_address,\n    \n    // Line item details\n    lineItemId: `${order.order_id}-${index}`,\n    productId: item.product_id,\n    sku: item.sku,\n    quantity: item.quantity,\n    requestedPrice: item.price,\n    \n    // Processing metadata\n    itemIndex: index,\n    totalItems: orderItems.length,\n    orderTimestamp: order.timestamp || new Date().toISOString()\n  }\n}));\n\nreturn outputItems;"
      },
      "name": "Extract Line Items",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [450, 400]
    },
    {
      "parameters": {
        "functionCode": "/**\n * FUNCTION-ITEM: Runs once PER ITEM\n * Use case: Enrich each line item independently with product data,\n * inventory check, and individual pricing rules\n */\n\nconst item = $item(0).json;\n\n// Simulate fetching product details from database/cache\n// In real scenario, this would be an HTTP request or DB query\nconst productDatabase = {\n  'PROD-001': {\n    name: 'Ergonomic Office Chair',\n    category: 'furniture',\n    basePrice: 299.99,\n    weight: 25,\n    dimensions: { length: 30, width: 30, height: 48 },\n    inStock: 150,\n    supplier: 'ErgoSupplier Inc',\n    attributes: { color: 'black', material: 'mesh' }\n  },\n  'PROD-002': {\n    name: 'Standing Desk Converter',\n    category: 'furniture',\n    basePrice: 449.99,\n    weight: 40,\n    dimensions: { length: 36, width: 24, height: 20 },\n    inStock: 75,\n    supplier: 'DeskCo',\n    attributes: { adjustable: true, maxHeight: 20 }\n  },\n  'PROD-003': {\n    name: 'Wireless Keyboard',\n    category: 'electronics',\n    basePrice: 79.99,\n    weight: 1.5,\n    dimensions: { length: 17, width: 5, height: 1 },\n    inStock: 500,\n    supplier: 'TechParts LLC',\n    attributes: { backlit: true, wireless: true }\n  }\n};\n\nconst productInfo = productDatabase[item.productId] || null;\n\nif (!productInfo) {\n  throw new Error(`Product ${item.productId} not found`);\n}\n\n// Check inventory availability\nconst isAvailable = productInfo.inStock >= item.quantity;\nconst inventoryStatus = isAvailable ? 'available' : 'backorder';\n\n// Calculate individual item pricing (before order-level discounts)\nconst basePrice = productInfo.basePrice;\nlet unitPrice = basePrice;\n\n// Apply quantity-based discount for this item\nif (item.quantity >= 10) {\n  unitPrice = basePrice * 0.85; // 15% discount for 10+\n} else if (item.quantity >= 5) {\n  unitPrice = basePrice * 0.90; // 10% discount for 5-9\n}\n\nconst lineItemSubtotal = unitPrice * item.quantity;\n\n// Calculate dimensional weight for shipping\nconst dims = productInfo.dimensions;\nconst dimensionalWeight = (dims.length * dims.width * dims.height) / 166;\nconst chargeableWeight = Math.max(productInfo.weight, dimensionalWeight);\n\nreturn {\n  json: {\n    // Original line item data\n    orderId: item.orderId,\n    customerId: item.customerId,\n    customerEmail: item.customerEmail,\n    shippingAddress: item.shippingAddress,\n    lineItemId: item.lineItemId,\n    \n    // Enriched product information\n    productId: item.productId,\n    sku: item.sku,\n    productName: productInfo.name,\n    category: productInfo.category,\n    supplier: productInfo.supplier,\n    \n    // Pricing details\n    basePrice: basePrice,\n    unitPrice: unitPrice,\n    quantity: item.quantity,\n    quantityDiscount: ((basePrice - unitPrice) / basePrice * 100).toFixed(1),\n    lineItemSubtotal: lineItemSubtotal,\n    \n    // Inventory & fulfillment\n    inventoryStatus: inventoryStatus,\n    availableStock: productInfo.inStock,\n    estimatedShipDate: isAvailable ? \n      new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString() : \n      new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),\n    \n    // Shipping calculation inputs\n    itemWeight: productInfo.weight,\n    chargeableWeight: chargeableWeight,\n    dimensions: productInfo.dimensions,\n    \n    // Metadata\n    itemIndex: item.itemIndex,\n    totalItems: item.totalItems,\n    orderTimestamp: item.orderTimestamp,\n    processedAt: new Date().toISOString()\n  }\n};"
      },
      "name": "Enrich Each Line Item",
      "type": "n8n-nodes-base.functionItem",
      "typeVersion": 1,
      "position": [650, 400]
    },
    {
      "parameters": {
        "functionCode": "/**\n * FUNCTION: Runs ONCE for ALL ITEMS\n * Use case: Consolidate all line items, apply order-level discounts,\n * calculate shipping, taxes, and generate final invoice\n */\n\nconst items = $input.all();\n\nif (items.length === 0) {\n  throw new Error('No items to process');\n}\n\n// Extract order-level information (same across all items)\nconst firstItem = items[0].json;\nconst orderId = firstItem.orderId;\nconst customerId = firstItem.customerId;\nconst customerEmail = firstItem.customerEmail;\nconst shippingAddress = firstItem.shippingAddress;\nconst orderTimestamp = firstItem.orderTimestamp;\n\n// Aggregate line item totals\nconst lineItems = items.map(item => item.json);\nconst subtotal = lineItems.reduce((sum, item) => sum + item.lineItemSubtotal, 0);\nconst totalQuantity = lineItems.reduce((sum, item) => sum + item.quantity, 0);\nconst totalWeight = lineItems.reduce((sum, item) => sum + (item.chargeableWeight * item.quantity), 0);\n\n// Check if any items are on backorder\nconst hasBackorder = lineItems.some(item => item.inventoryStatus === 'backorder');\nconst latestShipDate = lineItems.reduce((latest, item) => {\n  const shipDate = new Date(item.estimatedShipDate);\n  return shipDate > new Date(latest) ? item.estimatedShipDate : latest;\n}, lineItems[0].estimatedShipDate);\n\n// Apply order-level discounts\nlet orderDiscount = 0;\nlet orderDiscountReason = 'none';\n\nif (subtotal >= 1000) {\n  orderDiscount = subtotal * 0.10; // 10% off orders over $1000\n  orderDiscountReason = 'bulk_order_discount';\n} else if (totalQuantity >= 20) {\n  orderDiscount = subtotal * 0.07; // 7% off for 20+ items\n  orderDiscountReason = 'quantity_discount';\n}\n\n// Calculate category-based discount (buy from multiple categories)\nconst uniqueCategories = new Set(lineItems.map(item => item.category));\nif (uniqueCategories.size >= 3) {\n  const categoryBonus = subtotal * 0.05;\n  orderDiscount = Math.max(orderDiscount, categoryBonus);\n  orderDiscountReason = 'multi_category_discount';\n}\n\nconst subtotalAfterDiscount = subtotal - orderDiscount;\n\n// Calculate shipping based on weight and destination\n// Simplified tiered shipping calculation\nlet shippingCost = 0;\nif (totalWeight <= 5) {\n  shippingCost = 9.99;\n} else if (totalWeight <= 20) {\n  shippingCost = 19.99;\n} else if (totalWeight <= 50) {\n  shippingCost = 39.99;\n} else {\n  shippingCost = 39.99 + ((totalWeight - 50) * 1.50);\n}\n\n// Free shipping for orders over $500 after discount\nif (subtotalAfterDiscount >= 500) {\n  shippingCost = 0;\n}\n\n// Calculate tax (simplified - would normally use tax service based on address)\nconst taxRate = 0.0825; // 8.25%\nconst taxAmount = subtotalAfterDiscount * taxRate;\n\n// Calculate final total\nconst total = subtotalAfterDiscount + shippingCost + taxAmount;\n\n// Group items by supplier for fulfillment routing\nconst itemsBySupplier = lineItems.reduce((acc, item) => {\n  if (!acc[item.supplier]) {\n    acc[item.supplier] = [];\n  }\n  acc[item.supplier].push({\n    lineItemId: item.lineItemId,\n    productId: item.productId,\n    productName: item.productName,\n    quantity: item.quantity,\n    inventoryStatus: item.inventoryStatus\n  });\n  return acc;\n}, {});\n\n// Generate invoice data structure\nconst invoice = {\n  // Order identification\n  orderId: orderId,\n  invoiceNumber: `INV-${orderId}`,\n  invoiceDate: new Date().toISOString(),\n  \n  // Customer information\n  customer: {\n    customerId: customerId,\n    email: customerEmail,\n    shippingAddress: shippingAddress\n  },\n  \n  // Line items detail\n  lineItems: lineItems.map(item => ({\n    lineItemId: item.lineItemId,\n    productId: item.productId,\n    sku: item.sku,\n    productName: item.productName,\n    category: item.category,\n    quantity: item.quantity,\n    unitPrice: item.unitPrice,\n    lineTotal: item.lineItemSubtotal,\n    inventoryStatus: item.inventoryStatus\n  })),\n  \n  // Financial summary\n  pricing: {\n    subtotal: subtotal,\n    orderDiscount: orderDiscount,\n    orderDiscountReason: orderDiscountReason,\n    subtotalAfterDiscount: subtotalAfterDiscount,\n    shippingCost: shippingCost,\n    taxRate: taxRate,\n    taxAmount: taxAmount,\n    total: total,\n    currency: 'USD'\n  },\n  \n  // Fulfillment information\n  fulfillment: {\n    totalItems: lineItems.length,\n    totalQuantity: totalQuantity,\n    totalWeight: totalWeight,\n    hasBackorder: hasBackorder,\n    estimatedShipDate: latestShipDate,\n    supplierBreakdown: itemsBySupplier\n  },\n  \n  // Analytics & metadata\n  analytics: {\n    uniqueCategories: uniqueCategories.size,\n    uniqueSuppliers: Object.keys(itemsBySupplier).length,\n    averageItemValue: subtotal / totalQuantity,\n    processingTime: new Date().toISOString()\n  },\n  \n  // Order metadata\n  orderTimestamp: orderTimestamp,\n  processedAt: new Date().toISOString()\n};\n\nreturn [{ json: invoice }];"
      },
      "name": "Consolidate & Calculate Invoice",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [850, 400]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.accounting-system.com/invoices",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "accountingApi",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify($json) }}"
      },
      "name": "Create Invoice",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1050, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.warehouse-system.com/fulfillment-orders",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "warehouseApi",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "orderId",
              "value": "={{ $json.orderId }}"
            },\n            {
              "name": "supplierOrders",
              "value": "={{ $json.fulfillment.supplierBreakdown }}"
            },
            {
              "name": "shippingAddress",
              "value": "={{ $json.customer.shippingAddress }}"
            },
            {
              "name": "estimatedShipDate",
              "value": "={{ $json.fulfillment.estimatedShipDate }}"
            }
          ]
        }
      },
      "name": "Create Fulfillment Orders",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [1050, 400]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ {\n  success: true,\n  orderId: $json.orderId,\n  invoiceNumber: $json.invoiceNumber,\n  total: $json.pricing.total,\n  currency: $json.pricing.currency,\n  estimatedShipDate: $json.fulfillment.estimatedShipDate,\n  message: $json.fulfillment.hasBackorder ? 'Order processed - some items on backorder' : 'Order processed successfully'\n} }}",
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
    "Receive Order": {
      "main": [
        [
          {
            "node": "Extract Line Items",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Extract Line Items": {
      "main": [
        [
          {
            "node": "Enrich Each Line Item",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Enrich Each Line Item": {
      "main": [
        [
          {
            "node": "Consolidate & Calculate Invoice",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Consolidate & Calculate Invoice": {
      "main": [
        [
          {
            "node": "Create Invoice",
            "type": "main",
            "index": 0
          },
          {
            "node": "Create Fulfillment Orders",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Create Invoice": {
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
    "Create Fulfillment Orders": {
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

1. **Proper Node Selection**: Uses Function-Item for per-item enrichment (parallel execution model), Function for aggregation (sees all items)
2. **Data Flow Understanding**: Demonstrates how items expand (1 order → N line items) then consolidate (N items → 1 invoice)
3. **Complex Business Logic**: Implements multi-tier pricing, category discounts, weight-based shipping, and tax calculation
4. **Supplier Routing**: Groups items by supplier for distributed fulfillment - real-world complexity
5. **Defensive Programming**: Validates inventory, handles backorders, calculates fallback dates

## Best Practices for Function/Function-Item Mastery

1. **Use Function-Item for independent transformations** - When each item needs enrichment but doesn't depend on other items; enables parallel processing and cleaner code per item
2. **Use Function (or Code with $input.all()) for aggregations** - When you need to see all items together for sum/avg/grouping/deduplication; outputs single consolidated result
3. **Understand the execution model deeply** - Function-Item runs N times (once per item); Function runs once (sees all items); choose based on whether items need context from each other
4. **Minimize data passing between nodes** - Only pass forward what downstream nodes need; use clear JSON structures; avoid carrying forward entire payloads when only a few fields are needed
5. **Document execution context in comments** - Clearly note whether code runs per-item or per-batch; explain why that execution model was chosen; helps future debugging and optimization
