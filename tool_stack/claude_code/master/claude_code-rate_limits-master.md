# Rate Limits in Claude Code

Rate limits are constraints on how frequently you can call Claude APIs or execute certain operations. Understanding and designing around rate limits is critical for building reliable automation that doesn't get throttled or blocked.

## Advanced Example

**Concept:** Sophisticated rate limit management with adaptive backoff and circuit breaking

```javascript
// Real scenario: Continuous automation service processing user requests

class RateLimitAwareAutomationService {
  constructor() {
    this.rateLimitManager = new RateLimitManager({
      tiersPerMinute: {
        free: 5,
        pro: 100,
        enterprise: 1000
      },
      baselineApiCall: 1,        // Calls cost 1 unit
      parallelToolCallCost: 0.5, // Multiple tools in 1 call = 0.5x cost
      cacheHitCost: 0.1          // Cache hits cost 0.1x
    });

    this.requestQueue = new PriorityQueue({
      // Priority levels
      critical: 10,              // Critical path (deployments, incidents)
      high: 5,                   // User requests
      normal: 1,                 // Background automation
      low: 0.1                   // Cleanup tasks
    });

    this.circuitBreaker = new CircuitBreaker({
      failureThreshold: 5,       // Fail after 5 rate limit errors
      timeout: 300000,           // 5 minute cooldown
      monitoringWindow: 60000    // 1 minute observation window
    });
  }

  async submitTask(task, priority = 'normal') {
    // Check circuit breaker status
    if (this.circuitBreaker.isOpen()) {
      return {
        status: 'deferred',
        reason: 'Service rate limited, deferring task',
        retryAfter: this.circuitBreaker.timeUntilRetry()
      };
    }

    // Check if we have capacity for this task
    const costEstimate = this.estimateCost(task);
    const availableCapacity = this.rateLimitManager.getAvailable();

    if (costEstimate > availableCapacity) {
      // Queue for later when capacity is available
      this.requestQueue.enqueue({
        task,
        priority,
        createdAt: Date.now()
      });

      return {
        status: 'queued',
        position: this.requestQueue.getPosition(),
        estimatedWait: this.rateLimitManager.estimateWait(costEstimate)
      };
    }

    // Execute the task with adaptive retry logic
    return await this.executeWithAdaptiveRetry(task);
  }

  async executeWithAdaptiveRetry(task) {
    let attempt = 0;
    const maxAttempts = 5;
    const baseDelay = 1000; // Start with 1 second

    while (attempt < maxAttempts) {
      try {
        // Record request
        this.rateLimitManager.recordRequest(task.estimatedCost);

        // Execute task
        const result = await claude.execute(task);

        // Success
        this.circuitBreaker.recordSuccess();
        return result;

      } catch (error) {
        if (error.code === 'RATE_LIMIT_EXCEEDED') {
          // Calculate exponential backoff
          const delayMs = baseDelay * Math.pow(2, attempt);

          // Update circuit breaker
          this.circuitBreaker.recordFailure();

          // Log and wait
          console.log(`Rate limited. Attempt ${attempt + 1}/${maxAttempts}, waiting ${delayMs}ms`);
          await sleep(delayMs);

          attempt++;

          // Get current rate limit status
          const status = this.rateLimitManager.getStatus();
          console.log(`Rate limit status: ${status.used}/${status.limit} requests used`);

          // If we're consistently hitting limits, open circuit breaker
          if (this.circuitBreaker.shouldOpen()) {
            throw new Error('Service rate limited repeatedly, circuit opened');
          }
        } else {
          // Non-rate-limit error, fail fast
          throw error;
        }
      }
    }

    throw new Error(`Failed after ${maxAttempts} attempts`);
  }

  getMetrics() {
    return {
      rateLimitStatus: this.rateLimitManager.getStatus(),
      queuedTasks: this.requestQueue.size(),
      circuitBreakerStatus: this.circuitBreaker.getStatus(),
      successRate: this.circuitBreaker.getSuccessRate(),
      averageResponseTime: this.rateLimitManager.getAverageResponseTime()
    };
  }

  // Background worker: Process queued tasks as capacity becomes available
  async startQueueProcessor() {
    while (true) {
      if (this.circuitBreaker.isOpen()) {
        await sleep(this.circuitBreaker.timeUntilRetry());
        continue;
      }

      const nextTask = this.requestQueue.dequeue();
      if (!nextTask) {
        await sleep(5000); // No tasks, wait 5 seconds
        continue;
      }

      // Check if we have capacity
      const available = this.rateLimitManager.getAvailable();
      const needed = this.estimateCost(nextTask.task);

      if (needed > available) {
        // Re-queue, not ready yet
        this.requestQueue.enqueue(nextTask);
        const waitTime = this.rateLimitManager.estimateWait(needed);
        await sleep(Math.min(waitTime, 30000)); // Wait max 30 seconds
        continue;
      }

      // Process the task
      try {
        await this.executeWithAdaptiveRetry(nextTask.task);
      } catch (error) {
        console.error('Failed to process queued task:', error);
        // Could implement dead letter queue here
      }
    }
  }

  estimateCost(task) {
    // Logic to estimate API call cost based on task complexity
    if (task.type === 'simple_query') return 1;
    if (task.type === 'file_analysis') return 1.5;
    if (task.type === 'full_codebase_refactor') return 5;
    return 1;
  }
}

// Usage:
const automation = new RateLimitAwareAutomationService();

// Critical path request
await automation.submitTask({
  type: 'deploy_production',
  priority: 'critical'
  // Executes immediately with priority
});

// User request
await automation.submitTask({
  type: 'file_analysis',
  priority: 'high'
  // Executes soon if capacity available, else queued
});

// Background task
await automation.submitTask({
  type: 'cleanup_old_logs',
  priority: 'low'
  // Deferred until low-priority time window
});
```

## Best Practices

1. **Batch operations** - Combine multiple tool calls into one API request to reduce rate limit usage
2. **Implement queuing** - Use priority queues to ensure critical tasks execute while deferring less important ones
3. **Use adaptive backoff** - Exponential backoff with jitter when hitting rate limits (don't hammer the API)
4. **Monitor and log** - Track rate limit usage patterns to optimize cost and performance
5. **Implement circuit breakers** - Stop sending requests temporarily if repeatedly hitting limits; auto-recover
