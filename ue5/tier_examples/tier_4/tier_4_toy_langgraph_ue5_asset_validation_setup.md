# UE5 - Tier 4 - Multi-Agent Asset Validation

**Multi-Agent Workflow**: ConceptAgent reviews artistic quality → TechAgent validates technical specs

## Installation
```bash
cd ue5/tier_4/
pip install -r requirements.txt
cp .env.template .env
python tier_4_toy_langgraph_ue5_asset_validation.py
```

## Tier 4: Coordinated Agents
- ConceptAgent: Artistic/design review
- TechAgent: Technical validation
- Both must approve for asset to pass
