# Rate Limits in Claude Code

Rate limits are constraints on how frequently you can call Claude APIs or execute certain operations. Understanding and designing around rate limits is critical for building reliable automation that doesn't get throttled or blocked.

## Beginner Example

**Concept:** Basic awareness of rate limits

```
Rate Limit Type: API Requests Per Minute

Free Tier: 5 requests/minute
Paid Tier: 100 requests/minute

What counts:
- Every API call to Claude counts toward the limit
- Tool calls are batched in one request
- Parallel tool execution still counts as one request

Example:
Task: Run 100 file searches in sequence
Problem: At 5 req/min, this takes 20 minutes

Solution: Batch searches or use Glob with patterns
Result: Reduces to 1-2 API calls instead of 100
```

## Best Practices

1. **Batch operations** - Combine multiple tool calls into one API request to reduce rate limit usage
2. **Implement queuing** - Use priority queues to ensure critical tasks execute while deferring less important ones
3. **Use adaptive backoff** - Exponential backoff with jitter when hitting rate limits (don't hammer the API)
4. **Monitor and log** - Track rate limit usage patterns to optimize cost and performance
5. **Implement circuit breakers** - Stop sending requests temporarily if repeatedly hitting limits; auto-recover
