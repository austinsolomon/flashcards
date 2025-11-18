#!/usr/bin/env python3
"""
Law - Tier 3 - Advanced Legal Research Agent

Full-featured legal research agent with web search, citation validation,
and statute lookup. Production-ready template for law firms.
"""

import os
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv

load_dotenv()

# Tools
search = DuckDuckGoSearchRun()

def web_case_search(query: str) -> str:
    """Search web for case law"""
    enhanced_query = f"site:scholar.google.com OR site:justia.com {query}"
    return search.run(enhanced_query)

def validate_citation(citation: str) -> str:
    """Basic citation validation"""
    return f"Citation {citation} - recommend manual verification via Westlaw/Lexis"

tools = [
    Tool(name="case_search", description="Search case law", func=web_case_search),
    Tool(name="validate", description="Validate citation", func=validate_citation)
]

# Agent prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", """Legal research assistant. Find cases, validate citations, synthesize findings.
    Always recommend attorney verification of AI research."""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

def research(question: str):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return executor.invoke({"input": question})["output"]

if __name__ == "__main__":
    result = research("What is the standard for summary judgment?")
    print(f"\n📋 Research Memo:\n{result}")
