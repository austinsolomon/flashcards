# Agent Patterns in Claude Code

Agent patterns are proven architectural approaches for structuring autonomous agents to solve complex problems. Different patterns excel at different scenarios, and understanding which pattern to use significantly impacts agent effectiveness.

## Advanced Example

**Concept:** Tree Search Pattern with Backtracking (complex problem solving)

```javascript
// Real scenario: System architecture redesign with multiple valid approaches

const ArchitectureRedesignAgent = {
  pattern: "Tree Search with Backtracking",
  complexity: "Very High",

  algorithm: `
GOAL: Redesign system to handle 10x scale with minimal cost increase

Initial State:
  - Current architecture: Monolith + legacy database
  - Constraints: Budget limit, no downtime, keep existing data
  - Success metrics: 10x scalability, <5% cost increase, <99.99% uptime

Search Tree:
              ┌─────────────────────────────────────┐
              │ Redesign Architecture Decision      │
              └─────────────────────────────────────┘
                      ↓
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
   Option A:    Option B:      Option C:
   Microservices Database Cache-Heavy
   Migration    Sharding       Edge CDN

BRANCH A: Microservices Migration
├─ Pros: Full scalability, team autonomy
├─ Cons: Complex, high coordination
├─ Risk Assessment: HIGH (coordination overhead)
├─ Cost Estimate: $500K
├─ Timeline: 12 months
├─ DECISION POINT → Score: 6/10 (not ideal for timeline)
│
└─ EXPLORATION: Can we mitigate risks?
   ├─ Option A1: Start with 3 critical services
   │   ├─ Cost: $200K
   │   ├─ Timeline: 4 months
   │   ├─ DECISION: Better, Score 7/10
   │   └─ Continue exploring...
   │
   └─ Option A2: Use managed service mesh
       ├─ Cost: $300K
       ├─ Timeline: 6 months
       ├─ DECISION: Score 7/10
       └─ Comparable to A1

BRANCH B: Database Sharding
├─ Pros: Handles scale, lower complexity
├─ Cons: Data consistency issues
├─ Risk Assessment: MEDIUM
├─ Cost Estimate: $150K
├─ Timeline: 6 months
├─ DECISION POINT → Score: 8/10
│
└─ EXPLORATION: Mitigate consistency issues?
   ├─ Option B1: Event-driven consistency
   │   ├─ Cost: +$50K
   │   ├─ Complexity: +20%
   │   ├─ DECISION: Score 9/10 (best so far!)
   │   └─ Continue exploring...
   │
   └─ Option B2: Eventual consistency model
       ├─ Cost: +$25K
       ├─ Complexity: +10%
       ├─ DECISION: Score 8/10

BRANCH C: Cache-Heavy + CDN
├─ Pros: Low complexity, quick wins
├─ Cons: Doesn't solve fundamental scaling
├─ Risk Assessment: LOW but insufficient
├─ Cost Estimate: $75K
├─ Timeline: 2 months
├─ DECISION POINT → Score: 5/10 (incomplete solution)
│
└─ Possible combo: C + B1
   ├─ Combined approach: Database sharding + edge caching
   ├─ Cost: $150K + $75K = $225K
   ├─ Timeline: Can run in parallel = 4 months
   ├─ DECISION: Final Score 9/10 (equals B1)
   └─ Additional benefit: Quick cache wins while sharding in progress

Final Evaluation (Scoring all paths):
┌────────────────────────────────────────────────────┐
│ PATH | APPROACH          | SCORE | DECISION       │
├────────────────────────────────────────────────────┤
│ A1   │ Microservices 3   │ 7/10  │ Continue       │
│ A2   │ Service Mesh      │ 7/10  │ Continue       │
│ B1   │ DB Shard + Events │ 9/10  │ TOP CHOICE     │
│ B2   │ DB Shard + EC     │ 8/10  │ Continue       │
│ C+B1 │ Cache + DB Shard  │ 9/10  │ TOP CHOICE     │
└────────────────────────────────────────────────────┘

BACKTRACKING EXAMPLE:
Suppose we explore B1 further and find:
- Event ordering issues make it impractical
- BACKTRACK: Revert to exploring B2
- B2 becomes the best path

Final Decision:
The agent has explored multiple paths, evaluated trade-offs,
and can now recommend the optimal architecture with full reasoning:

"I recommend Database Sharding with Event-Driven Consistency (B1) because:
- Achieves 10x scalability
- Within budget ($200K vs $500K limit)
- 6-month timeline (acceptable)
- Lower risk than microservices
- Can be implemented incrementally

Alternatively, Cache + Sharding (C+B1) provides quick wins while
sharding is in progress."
  `,

  characteristics: {
    goodFor: "Complex decisions with multiple valid paths, architecture design",
    advantages: "Explores all options, finds optimal solution, explains reasoning",
    limitations: "Higher cost, can be slow, may over-analyze simple problems"
  }
};
```

## Best Practices

1. **Match pattern to problem type** - Use reactive for simple tasks, loop for iterative problems, tree search for complex decisions
2. **Define clear termination conditions** - Know when to stop exploring and commit to a decision
3. **Implement pruning** - Cut off branches that clearly won't lead to good solutions to save time
4. **Provide early feedback** - For complex searches, show intermediate results so humans can redirect if needed
5. **Combine patterns** - Start simple (reactive), escalate to loop if needed, use tree search only for critical decisions
