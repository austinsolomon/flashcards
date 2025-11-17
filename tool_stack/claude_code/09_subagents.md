# Subagents in Claude Code

Subagents are specialized agents launched to handle specific subtasks within a larger workflow. The main agent can orchestrate multiple subagents in parallel or sequence, enabling complex multi-domain problem solving with proper task decomposition.

## Beginner Example

**Concept:** One main agent launching a focused subagent

```
Main Task: Deploy a new feature and generate documentation

Main Agent Flow:
1. Review changes
2. Run tests
3. Launch Subagent: Document Generator
   → Subagent generates README updates
4. Deploy
5. Confirm completion
```

## Intermediate Example

**Concept:** Parallel subagent execution for multi-domain tasks

```javascript
// Real scenario: Build a new e-commerce product page

Main Agent: \"Product Page Implementation\"

Task: Create product page with SEO, performance optimization, and analytics

Main Agent Flow:
1. Understand requirements
2. Launch 3 Subagents in PARALLEL:

   ╔════════════════════════════════════════╗
   ║ Subagent 1: Frontend Developer        ║
   ║ Task: Build React components          ║
   ║ Tools: Edit, Read, Write              ║
   ║ Expected: Components, styling         ║
   ║ Timeline: 30 min                      ║
   ╚════════════════════════════════════════╝
         ↓
   ╔════════════════════════════════════════╗
   ║ Subagent 2: SEO Specialist            ║
   ║ Task: Optimize SEO elements           ║
   ║ Tools: Edit, Grep, Read               ║
   ║ Expected: Meta tags, structured data  ║
   ║ Timeline: 20 min                      ║
   ╚════════════════════════════════════════╝
         ↓
   ╔════════════════════════════════════════╗
   ║ Subagent 3: Performance Engineer      ║
   ║ Task: Optimize assets and loading     ║
   ║ Tools: Edit, Bash, Read               ║
   ║ Expected: Lazy loading, compression   ║
   ║ Timeline: 25 min                      ║
   ╚════════════════════════════════════════╝

3. Wait for all subagents to complete
4. Main Agent: Integrate results
5. Run comprehensive tests
6. Deploy product page
```

## Advanced Example

**Concept:** Hierarchical subagent orchestration with complex dependencies

```javascript
// Real scenario: Full system redesign with multiple specialized teams

const MainAgent = {
  goal: \"Redesign authentication and payment systems\",
  complexity: \"Very High\",

  executionStrategy: `
Main Agent: Project Orchestrator
├── Manages overall timeline
├── Resolves cross-team dependencies
├── Handles critical decisions
└── Ensures consistency

Tier 1 Subagents (run in sequence):
│
├─ Subagent: Architecture Designer
│  ├── Goal: Design new system architecture
│  ├── Scope:
│  │   • Database schema redesign
│  │   • API contract definition
│  │   • Integration points
│  │   • Scaling considerations
│  ├── Tools: Glob, Read, Grep (analysis only)
│  └── Output: Architecture docs, schemas
│
├─ Subagent: Auth System Specialist
│  ├── Goal: Implement OAuth2 + SAML support
│  ├── Dependencies: Requires architecture docs
│  ├── Scope:
│  │   • OAuth2 provider integration
│  │   • Token management system
│  │   • User session handling
│  │   • Backward compatibility
│  ├── Subtasks:
│  │   • Backend implementation
│  │   • Database migrations
│  │   • API endpoints
│  │   • Unit tests
│  ├── Tools: Edit, Read, Write, Bash, Grep
│  └── Output: Auth service code + tests
│
├─ Subagent: Payment System Specialist
│  ├── Goal: Implement Stripe + cryptocurrency support
│  ├── Dependencies: Requires architecture docs
│  ├── Scope:
│  │   • Payment processor integration
│  │   • Transaction logging
│  │   • Refund handling
│  │   • PCI compliance
│  ├── Subtasks:
│  │   • Backend implementation
│  │   • Database schema
│  │   • Security hardening
│  │   • Integration tests
│  ├── Tools: Edit, Read, Write, Bash, Grep
│  └── Output: Payment service code + tests

Tier 2 Subagents (run in parallel):
│
├─ Subagent: Integration Tester
│  ├── Goal: Test auth + payment integration
│  ├── Dependencies: Both services must be ready
│  ├── Scope:
│  │   • End-to-end flows
│  │   • Cross-service interactions
│  │   • Edge cases
│  │   • Performance under load
│  ├── Tools: Bash, Read, Write
│  └── Output: Integration test suite + report
│
├─ Subagent: Security Auditor
│  ├── Goal: Security review of new systems
│  ├── Dependencies: Both services must be ready
│  ├── Scope:
│  │   • OWASP Top 10 review
│  │   • Authentication vulnerabilities
│  │   • Data protection review
│  │   • Compliance validation
│  ├── Tools: Read, Grep, Bash (static analysis)
│  └── Output: Security audit report + fixes
│
├─ Subagent: Performance Optimizer
│  ├── Goal: Optimize performance of new systems
│  ├── Dependencies: Both services must be ready
│  ├── Scope:
│  │   • Database query optimization
│  │   • API response times
│  │   • Caching strategy
│  │   • Load testing results
│  ├── Tools: Read, Bash, Edit
│  └── Output: Performance tuning + benchmarks

Tier 3 Subagent (run after all above):
│
└─ Subagent: Documentation & Deployment
   ├── Goal: Create docs and prepare deployment
   ├── Dependencies: All systems tested and optimized
   ├── Scope:
   │   • API documentation
   │   • Deployment guides
   │   • Migration strategies
   │   • Runbooks for ops
   ├── Tools: Write, Edit, Bash
   └── Output: Complete documentation + deployment plan

Coordination Points:
1. Architecture docs released → Auth & Payment start
2. Services complete → Integration starts
3. All testing done → Documentation starts
4. All done → Ready for deployment

Main Agent Responsibilities:
- Monitor progress of all subagents
- Resolve cross-team conflicts (e.g., API design disagreement)
- Handle critical issues that require reconsideration
- Manage timeline and adjustments
- Conduct final quality review
  `,

  expectedOutcomes: {
    code: \"Both auth and payment systems fully implemented\",
    tests: \"100+ integration tests passing\",
    security: \"Security audit passed, no critical issues\",
    performance: \"Auth: <50ms, Payment: <200ms\",
    documentation: \"Complete API docs, deployment runbooks\",
    timelineSavings: \"30% faster than sequential implementation\"
  }
};
```

## Best Practices

1. **Decompose by expertise domain** - Launch subagents that represent specialized roles (frontend engineer, security specialist, etc.)
2. **Define clear dependencies** - Specify which subagents must complete before others start; run independent subagents in parallel
3. **Provide integration points** - Each subagent should understand how their output integrates with others
4. **Monitor and coordinate** - Main agent watches progress and handles conflicts between subagents
5. **Use subagents for scale** - Subagents excel at handling multiple complex subtasks faster than sequential processing
