# Rate Limits in Claude Code

Rate limits are constraints on how frequently you can call Claude APIs or execute certain operations. Understanding and designing around rate limits is critical for building reliable automation that doesn't get throttled or blocked.

## Intermediate Example

**Concept:** Designing workflows to respect rate limits

```javascript
// Real scenario: Automating daily code reviews for 50 pull requests

// NAIVE APPROACH (WILL HIT RATE LIMITS)
for (let i = 0; i < 50; i++) {
  const pr = prs[i];
  // This makes a separate API call for each PR
  const review = await claude.analyzeCode(pr.code);  // 50 API calls!
  await saveReview(review);
}
// Result: Needs 50 API calls = 10 minutes at 5 req/min

// BETTER APPROACH (RESPECTS RATE LIMITS)
// Batch PRs by size and complexity
const batches = {
  small: prs.filter(p => p.lines < 100),    // 30 PRs
  medium: prs.filter(p => p.lines < 500),   // 15 PRs
  large: prs.filter(p => p.lines >= 500)    // 5 PRs
};

// Process in parallel within limits
for (const [size, batch] of Object.entries(batches)) {
  // Send batch of 5 PRs in one prompt
  const reviews = await claude.analyzeBatch(batch);
  // This is ONE API call for 5 PRs
  await saveReviews(reviews);
}
// Result: Needs ~3 API calls total (amazing!)

// OPTIMAL APPROACH (WITH QUEUING)
const reviewQueue = new Queue({
  concurrency: 5,              // Max 5 concurrent reviews
  rateLimit: 2000,             // 1 API call every 2 seconds (respects 5 req/min)
  batchSize: 10,               // Batch 10 reviews per API call
});

for (const pr of prs) {
  await reviewQueue.add(() => analyzeAndSaveReview(pr));
}

// Result: All 50 PRs processed with zero rate limit issues
```

## Best Practices

1. **Batch operations** - Combine multiple tool calls into one API request to reduce rate limit usage
2. **Implement queuing** - Use priority queues to ensure critical tasks execute while deferring less important ones
3. **Use adaptive backoff** - Exponential backoff with jitter when hitting rate limits (don't hammer the API)
4. **Monitor and log** - Track rate limit usage patterns to optimize cost and performance
5. **Implement circuit breakers** - Stop sending requests temporarily if repeatedly hitting limits; auto-recover
