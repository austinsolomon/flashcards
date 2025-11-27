# Build a 2-Way CRM Enrichment Workflow (Attio + Clay)

## Objective

Automatically keep CRM data clean by triggering a webhook for any contact missing a LinkedIn URL, finding it via search, and pushing the new data back to the CRM.

## Tool Stack

- **Attio** - CRM & Automation Trigger
- **Clay** - Enrichment Logic
- **Serper** - Google Search API
- **Webhooks** - 2-Way Communication

## Workflow Summary

This automation maintains data quality in your CRM by:
1. Detecting contacts with missing LinkedIn URLs via Attio triggers
2. Sending webhook to Clay for enrichment processing
3. Using Serper to search for the contact's LinkedIn profile
4. Pushing enriched data back to Attio via webhook
5. Creating a closed-loop system that keeps data fresh automatically
