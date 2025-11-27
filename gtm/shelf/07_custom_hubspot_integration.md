# Build a Custom HubSpot Integration (Deal Governance)

## Objective

Prevent sales conflicts by using a custom API call to check if a company has an "Active Deal" in HubSpot (which standard integrations often miss) before approving them for outreach.

## Tool Stack

- **HubSpot** - Enterprise CRM
- **HubSpot Private App** - Custom Read-Access Token
- **Clay** - HTTP API Request Module

## Workflow Summary

This automation prevents territory conflicts and duplicate outreach by:
1. Creating a HubSpot Private App with custom read permissions
2. Configuring Clay to make HTTP API requests to HubSpot
3. Checking for active deals associated with target companies
4. Querying deal status, owner, and stage information
5. Blocking or flagging contacts that already have active sales engagement
6. Ensuring deal governance that standard integrations can't provide
