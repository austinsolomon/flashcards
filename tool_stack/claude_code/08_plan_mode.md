# Plan Mode in Claude Code

Plan mode is a collaborative planning phase where Claude analyzes requirements and creates a detailed implementation plan before executing any code changes. This mode separates thinking from doing, ensuring alignment before committing changes.

## Beginner Example

**Concept:** Simple planning before implementation

```
User: \"Add dark mode support to my React app\"

Plan Mode:
Claude: \"Here's my implementation plan:

1. Create a ThemeContext to manage dark/light mode state
2. Add CSS for dark mode (background colors, text colors)
3. Create a theme toggle component
4. Update existing components to use ThemeContext
5. Test in both light and dark modes

Shall I proceed with this approach?\"

User: \"Yes, but also update the localStorage to persist the choice\"

Plan refined:
Claude: \"Updated plan:

1. Create a ThemeContext with localStorage persistence
2. Add CSS for dark mode
3. Create toggle component
4. Update components to use context
5. Test persistence across page reloads

Ready to implement?\"
```

## Intermediate Example

**Concept:** Complex feature planning with multiple considerations

```
User: \"Refactor our authentication system from custom JWT to OAuth2\"

Plan Mode:
Claude: \"This is a significant migration. Here's my implementation plan:

## Phase 1: Preparation (No production impact)
- Review current JWT implementation
- Choose OAuth provider (Google, GitHub, Auth0)
- Design token mapping strategy
- Create feature branch

## Phase 2: Backend Implementation
- Add OAuth library
- Create OAuth configuration
- Implement token validation
- Create token refresh logic
- Add backward compatibility layer (support both JWT and OAuth)
- Write comprehensive tests

## Phase 3: Frontend Implementation
- Add OAuth login component
- Update authentication guards
- Implement logout
- Handle token refresh

## Phase 4: Migration
- Deploy with dual auth support (2 weeks monitoring)
- Gradually migrate existing users
- Monitor error rates and support requests
- Remove JWT support after 95% migration

## Phase 5: Cleanup
- Remove JWT dependencies
- Update documentation
- Perform security audit

## Risk Mitigation
- Maintain fallback to JWT for first 2 weeks
- Monitor authentication errors continuously
- Have rollback plan if issues occur
- Test extensively on staging first

Estimated effort: 4-6 weeks
Risks: User lock-out if not careful, third-party dependency risk

Should I proceed with this approach?\"

User: \"Can we do this in 2 weeks instead?\"

Plan refined:
Claude: \"Yes, with adjusted scope:

## Compressed Timeline (2 weeks)
- Week 1:
  * Implement OAuth backend
  * Add dual-auth support
  * Deploy to staging
  * Internal testing
  * User acceptance testing

- Week 2:
  * Gradual production rollout (5% → 25% → 100%)
  * Continuous monitoring
  * Support readiness
  * Quick rollback if needed

Trade-off: Less time for in-depth testing. I recommend running
chaos testing and load testing to catch edge cases.

Proceed with this timeline?\"
```

## Advanced Example

**Concept:** Architectural planning with technical depth and stakeholder alignment

```
User: \"We need to redesign our microservices architecture.
Currently we have 15 services that are tightly coupled and hard to deploy.
We want to reduce deployment coupling and improve team autonomy.\"

Plan Mode (Extensive Analysis):
Claude: \"I've analyzed your codebase and current architecture.
Here's my detailed implementation plan:

## Current State Analysis
- 15 microservices with:
  * Synchronous RPC calls (tightly coupled)
  * Shared database access (data coupling)
  * Complex inter-service dependencies
  * Deploy time: 45 minutes with high coordination cost

## Target State
- Loosely coupled services
- Each team owns service deployments independently
- Event-driven communication
- Deploy time: 5-10 minutes per service

## Phase 1: Foundation (Weeks 1-2)
### Message Queue Implementation
- Deploy Apache Kafka cluster
- Setup topics for domain events
- Create event schema registry
- Implement event publishing library

### Service Mesh (Optional but recommended)
- Deploy Istio/Linkerd
- Enable service-to-service mTLS
- Setup traffic policies

## Phase 2: Strangler Pattern (Weeks 3-6)
Gradually decouple services:
- Service A: Keep RPC, add event publishing
- Service B: Dual-write to events
- Service C: Add event consumption
[...detailed for each service]

## Phase 3: Data Decoupling (Weeks 7-9)
- Create independent databases per service
- Implement data synchronization via events
- Implement saga patterns for distributed transactions

## Phase 4: Testing & Hardening (Weeks 10-12)
- Chaos engineering tests
- Load testing at scale
- Disaster recovery drills
- Security audit

## Phase 5: Migration & Cutover (Weeks 13-16)
- Run parallel systems (old + new)
- Monitor, validate, and stabilize
- Gradual traffic migration
- Cutover decision point

## Success Metrics
- Deployment time per service: < 10 minutes
- Deployment frequency: daily or more
- Service dependency depth: < 3
- MTTR for failures: < 5 minutes
- Developer feedback: improved autonomy

## Risks & Mitigations
1. Event ordering issues
   → Use event versioning and compensation patterns

2. Monitoring complexity
   → Implement distributed tracing (Jaeger)

3. Team coordination overhead
   → Clear contracts, event schema governance

4. Data consistency challenges
   → Eventual consistency model, sagas for critical operations

## Stakeholder Alignment Needed
- Product: Timeline impact on new features
- Ops: Infrastructure investment and training
- Engineering: New patterns and tooling
- Security: Multi-tenant isolation, audit trails

## Estimated Effort
- Timeline: 16 weeks
- People: 2 architects, 6 engineers, 1 ops
- Cost: Infrastructure ~$20K/month, tooling ~$5K/month
- Benefit: 80% reduction in deployment coordination time

This is a transformational change. Key decision points:
1. Approve overall strategy?
2. Approve 16-week timeline?
3. Assign dedicated team?

Should I refine any sections or proceed with detailed technical design?\"

User: \"This looks good. I want to also address monitoring complexity.
Can you create a detailed monitoring strategy as part of Phase 4?\"

[Plan is refined with additional detail in monitoring strategy]
```

## Best Practices

1. **Use plan mode for non-trivial tasks** - Simple changes don't need formal plans, complex ones do
2. **Include risk analysis** - Always discuss what could go wrong and mitigation strategies
3. **Define success metrics** - How will you know when the implementation is complete and successful?
4. **Get alignment before executing** - Plan mode is where misunderstandings surface before wasting implementation effort
5. **Break into phases** - For large projects, structure as distinct phases with decision points between them
