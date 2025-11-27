# Automate Account Fit Scoring (AI Research Agents)

## Objective

Replace manual research with a "department" of 5 AI agents that each check specific ICP criteria (e.g., B2B vs B2C, VC-backed) to assign a numerical fit score to every new account.

## Tool Stack

- **Attio** - CRM Storage
- **Clay** - Agent Orchestration
- **OpenAI/Claude** - Research & Evaluation Bots
- **Crunchbase/Apollo** - Data Sources

## Workflow Summary

This automation creates a multi-agent research team by:
1. Triggering on new account creation in Attio
2. Deploying 5 specialized AI agents via Clay, each evaluating specific criteria:
   - B2B vs B2C business model
   - VC-backing status
   - Company size/growth signals
   - Tech stack compatibility
   - Market segment alignment
3. Aggregating scores from all agents
4. Calculating overall fit score
5. Writing results back to Attio for sales prioritization
