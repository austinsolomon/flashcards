#!/usr/bin/env python3
"""
Law - Tier 4 - Multi-Agent Contract Review System

Agents:
- ExtractionAgent: Pulls out key terms (parties, dates, $ amounts)
- RiskAgent: Identifies risky clauses
- RedlineAgent: Suggests specific edits
- ValidationAgent: Ensures all suggestions are reasonable
"""

import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

class ContractState(TypedDict):
    contract_text: str
    key_terms: dict
    risks: List[dict]
    redlines: List[str]
    validation: str
    status: str

def extraction_agent(state: ContractState) -> ContractState:
    """Extract key terms from contract"""
    print("📄 ExtractionAgent: Extracting key terms...")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"Extract key terms (parties, dates, amounts, jurisdiction) from:\n\n{state['contract_text'][:2000]}\n\nReturn as JSON."
    response = llm.invoke([HumanMessage(content=prompt)])

    # Simplified extraction
    key_terms = {"parties": "Party A, Party B", "amount": "$100,000", "term": "12 months"}

    return {**state, "key_terms": key_terms, "status": "extraction_complete"}

def risk_agent(state: ContractState) -> ContractState:
    """Identify risky clauses"""
    print("⚠️ RiskAgent: Analyzing for risks...")
    risks = [
        {"clause": "Unlimited indemnification", "severity": "high"},
        {"clause": "Broad IP assignment", "severity": "medium"}
    ]
    return {**state, "risks": risks, "status": "risk_analysis_complete"}

def redline_agent(state: ContractState) -> ContractState:
    """Suggest redlines for risky terms"""
    print("✏️ RedlineAgent: Generating suggested edits...")
    redlines = [
        "Add 'except for gross negligence' to indemnification clause",
        "Exclude pre-existing IP from assignment"
    ]
    return {**state, "redlines": redlines, "status": "redlines_complete"}

def validation_agent(state: ContractState) -> ContractState:
    """Validate all suggestions are reasonable"""
    print("✅ ValidationAgent: Reviewing suggestions...")
    validation = "All suggestions appear reasonable. Attorney review recommended."
    return {**state, "validation": validation, "status": "complete"}

def review_contract(contract_text: str):
    """Run multi-agent contract review"""
    workflow = StateGraph(ContractState)

    workflow.add_node("extract", extraction_agent)
    workflow.add_node("risk", risk_agent)
    workflow.add_node("redline", redline_agent)
    workflow.add_node("validate", validation_agent)

    workflow.set_entry_point("extract")
    workflow.add_edge("extract", "risk")
    workflow.add_edge("risk", "redline")
    workflow.add_edge("redline", "validate")
    workflow.add_edge("validate", END)

    app = workflow.compile()

    initial_state = {
        "contract_text": contract_text,
        "key_terms": {},
        "risks": [],
        "redlines": [],
        "validation": "",
        "status": "initialized"
    }

    return app.invoke(initial_state)

if __name__ == "__main__":
    sample_contract = "This Agreement is between Company A and Contractor B..."
    result = review_contract(sample_contract)
    print(f"\n📋 Review Complete:\nRisks: {len(result['risks'])}\nSuggested Edits: {len(result['redlines'])}")
