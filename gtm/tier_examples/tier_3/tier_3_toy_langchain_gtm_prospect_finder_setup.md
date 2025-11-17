# GTM - Tier 3 - Prospect Decision-Maker Finder (LangChain Agent)

**What It Does**: Given a company name, a LangChain agent autonomously finds the best decision-maker for sales outreach by using web search, LinkedIn lookup, and company research tools. The agent decides which tools to use and in what order based on available information.

**Tier Characteristics**:
- **Single agent**: One agent handles the entire task
- **Multiple tools**: web_search, linkedin_lookup, company_info
- **Autonomous decision-making**: Agent chooses which tools to use and when
- **Reasoning & synthesis**: Combines information from multiple sources
- **Tool chaining**: May use multiple tools in sequence

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│         LangChain Agent (Tier 3)                │
│                                                  │
│  Prompt: "Find decision-maker at Acme Corp"     │
│                                                  │
│  Agent Reasoning:                                │
│  1. "I need company info first"                 │
│     → Calls company_info("Acme Corp")           │
│                                                  │
│  2. "Found CEO Sarah Chen, let me verify"       │
│     → Calls web_search("Sarah Chen CEO Acme")   │
│                                                  │
│  3. "Get detailed LinkedIn profile"             │
│     → Calls linkedin_lookup("Sarah Chen, Acme") │
│                                                  │
│  4. "I have enough info, synthesize result"     │
│     → Returns: Recommendation + contact info    │
└─────────────────────────────────────────────────┘

Available Tools:
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│ web_search  │  │ linkedin_    │  │ company_info │
│             │  │   lookup     │  │              │
│ General web │  │ Profile data │  │ Company data │
│ searches    │  │ & contacts   │  │ & signals    │
└─────────────┘  └──────────────┘  └──────────────┘
```

**Key Tier 3 Element**: Agent autonomously decides tool usage order

---

## Installation

### **1. Create Virtual Environment**

```bash
cd gtm/tier_3/
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **2. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **3. Configure Environment**

```bash
cp .env.template .env
# Edit .env and add your OpenAI API key
```

### **4. Test the Agent**

```bash
python tier_3_toy_langchain_gtm_prospect_finder.py
```

---

## Expected Output

```
============================================================
🎯 TIER 3 AGENT: Finding decision-maker at Acme Corp
============================================================

> Entering new AgentExecutor chain...
I should start by gathering company information to understand the business better.

Action: company_info
Action Input: Acme Corp

🏢 [COMPANY_INFO] Looking up: Acme Corp

Observation:
Company Profile: Acme Corp
Industry: Enterprise SaaS - Workflow Automation
Size: 200-500 employees
Key Decision Makers:
- CEO: Sarah Chen (sarah.chen@acmecorp.com)
- VP Sales: James Patterson (james.patterson@acmecorp.com)
...

Thought: Sarah Chen (CEO) seems like the primary decision-maker. Let me verify with LinkedIn.

Action: linkedin_lookup
Action Input: Sarah Chen, Acme Corp

👔 [LINKEDIN_LOOKUP] Looking up: Sarah Chen at Acme Corp

Observation:
LinkedIn Profile Found:
Name: Sarah Chen
Title: CEO & Co-Founder
Bio: Building the future of workflow automation...

Thought: I have enough information to make a recommendation.

Final Answer:
**Best Decision-Maker: Sarah Chen**

Title: CEO & Co-Founder at Acme Corp
Email: sarah.chen@acmecorp.com
Location: San Francisco, CA

Why Sarah is the right contact:
- As CEO and co-founder, she has final decision authority
- Acme Corp is in workflow automation - perfect fit for analytics/integration platform
- Recent activity shows interest in AI features
- Company is actively hiring integration engineers (buying signal)

Recommended Talking Points:
1. Acme's recent AI feature launch - our platform could enhance analytics
2. EU expansion plans - our integration platform supports global compliance
3. Current tech stack (Salesforce, HubSpot) - we integrate seamlessly
4. Company growth (Series B funded) - scaling needs better analytics

============================================================
✅ AGENT COMPLETE
============================================================
```

---

## Code Walkthrough

### **Tools Definition**

```python
def web_search_tool(query: str) -> str:
    """Search the web for company/person information"""
    # In production: call Serper API, Brave Search, etc.
    # Toy example: simulated responses
    ...

def linkedin_lookup_tool(person_name: str, company_name: str) -> str:
    """Look up LinkedIn profile"""
    # In production: call LinkedIn Sales Navigator API
    # Toy example: simulated profile data
    ...

def company_info_tool(company_name: str) -> str:
    """Get company data"""
    # In production: call Clearbit, ZoomInfo API
    # Toy example: simulated company data
    ...
```

### **Agent Creation**

```python
# Define tools for agent
tools = [
    Tool(name="web_search", func=web_search_tool, ...),
    Tool(name="linkedin_lookup", func=linkedin_lookup_tool, ...),
    Tool(name="company_info", func=company_info_tool, ...)
]

# Create agent with tools
agent = create_openai_tools_agent(llm, tools, agent_prompt)

# Execute agent
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True  # Show reasoning
)
```

### **Running the Agent**

```python
result = agent_executor.invoke({
    "input": "Find the best decision-maker at Acme Corp for analytics platform outreach"
})

# Agent autonomously:
# 1. Chooses which tools to use
# 2. Determines order of operations
# 3. Synthesizes findings
# 4. Provides recommendation
```

---

## Customization

### **Add Real API Integrations**

Replace simulated tools with real API calls:

```python
def web_search_tool(query: str) -> str:
    import requests
    response = requests.get(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": os.getenv("SERPER_API_KEY")},
        json={"q": query}
    )
    return response.json()
```

### **Add More Tools**

```python
def email_finder_tool(name: str, company: str) -> str:
    """Find email address using Hunter.io or similar"""
    ...

def crm_lookup_tool(company: str) -> str:
    """Check if company exists in CRM"""
    ...
```

### **Enhance Agent Prompt**

```python
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a sales research agent...

    ADDITIONAL CONTEXT:
    - Our product: Analytics and integration platform
    - Target customers: 100-1000 employee SaaS companies
    - Ideal buyer: VP Sales, VP Operations, or CEO
    - Focus on companies with recent funding or growth signals

    Your research should prioritize...
    """),
    ...
])
```

---

## Why This Is Tier 3

### **Tier 3 Characteristics Demonstrated**:

1. **Single Agent**: One agent handles the entire prospect research task
2. **Multiple Tools**: web_search, linkedin_lookup, company_info
3. **Autonomous Decisions**: Agent chooses which tools to use based on context
4. **Reasoning Loop**: Agent thinks → acts → observes → thinks → acts
5. **Information Synthesis**: Combines data from multiple sources into recommendation

### **Contrast with Other Tiers**:

| Tier | Approach |
|------|----------|
| **Tier 2** | ONE Claude API call with company name → returns decision-maker (no tools, no research) |
| **Tier 3** ← | Single agent with multiple tools, autonomous research, reasoning loop |
| **Tier 4** | Multiple agents: ResearchAgent → QualificationAgent → OutreachAgent (coordination between agents) |
| **Tier 5** | Claude Code orchestrates: Agent research → Human review → CRM update → Email draft |
| **Tier 6** | Autonomous learning: Agent improves over time, learns from email responses, auto-adjusts strategy |

---

## Common Issues

### **Issue**: Agent doesn't use tools
- **Solution**: Improve tool descriptions in Tool() definitions
- **Solution**: Add examples to agent prompt
- **Solution**: Check OpenAI API key has function calling enabled

### **Issue**: Agent uses too many tools
- **Solution**: Add to prompt: "Be efficient, use minimum tools necessary"
- **Solution**: Set max_iterations limit lower
- **Solution**: Improve tool descriptions to reduce confusion

### **Issue**: OpenAI API errors**
- **Solution**: Verify OPENAI_API_KEY in .env
- **Solution**: Check API credits/quota
- **Solution**: Try with gpt-4o-mini (cheaper) instead of gpt-4o

### **Issue**: Agent gets stuck in loops
- **Solution**: Set max_iterations (default: 10)
- **Solution**: Improve agent prompt with clearer stopping criteria
- **Solution**: Add error handling in tools

---

## Production Enhancements

### **1. Add Real Data Sources**

Replace toy simulations with:
- **Serper API** for web search
- **LinkedIn Sales Navigator API** for profile data
- **Clearbit/ZoomInfo** for company data
- **Hunter.io** for email finding

### **2. Add CRM Integration**

```python
def check_crm_tool(company: str) -> str:
    """Check if company/person already in CRM"""
    # Call HubSpot/Salesforce API
    # Return existing relationship status
```

### **3. Add Scoring Logic**

```python
def score_prospect_tool(data: dict) -> int:
    """Score prospect based on fit"""
    # Company size, funding, tech stack, buying signals
    # Return 0-100 score
```

### **4. Save Results to Database**

```python
def save_prospect(result: dict):
    """Save to database/CRM"""
    # Write to PostgreSQL, push to HubSpot, etc.
```

---

## Next Steps: Moving to Tier 4

To upgrade this to **Tier 4** (multi-agent), you would:

1. **Create Multiple Specialized Agents**:
   - `ResearchAgent`: Gathers company/person data
   - `QualificationAgent`: Scores and qualifies the prospect
   - `OutreachAgent`: Drafts personalized email

2. **Add Agent Coordination**:
   - Use LangGraph to orchestrate agents
   - ResearchAgent output → QualificationAgent input
   - QualificationAgent decision → OutreachAgent or reject

3. **State Management**:
   - Track information across agents
   - Allow agents to request additional data
   - Handle agent failures gracefully

See `tier_4_toy_langgraph_gtm_cold_email.py` for multi-agent patterns.

---

## Learning Resources

- **LangChain Agents**: https://python.langchain.com/docs/modules/agents/
- **Tool Calling**: https://python.langchain.com/docs/modules/agents/tools/
- **OpenAI Function Calling**: https://platform.openai.com/docs/guides/function-calling
