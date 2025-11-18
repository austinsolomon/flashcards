# Subagents in Claude Code

Subagents are specialized agents launched to handle specific subtasks within a larger workflow. The main agent can orchestrate multiple subagents in parallel or sequence, enabling complex multi-domain problem solving with proper task decomposition.

## Intermediate Example

**Concept:** Parallel subagent execution for multi-domain tasks

```javascript
// Real scenario: Build a new e-commerce product page

Main Agent: "Product Page Implementation"

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

## Best Practices

1. **Decompose by expertise domain** - Launch subagents that represent specialized roles (frontend engineer, security specialist, etc.)
2. **Define clear dependencies** - Specify which subagents must complete before others start; run independent subagents in parallel
3. **Provide integration points** - Each subagent should understand how their output integrates with others
4. **Monitor and coordinate** - Main agent watches progress and handles conflicts between subagents
5. **Use subagents for scale** - Subagents excel at handling multiple complex subtasks faster than sequential processing
