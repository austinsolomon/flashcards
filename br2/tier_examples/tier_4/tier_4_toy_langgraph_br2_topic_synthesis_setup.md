# BR2 - Tier 4 - Multi-Agent Topic Synthesis

**Multi-Agent Workflow**: ResearchAgent gathers related notes → SynthesisAgent creates comprehensive summary

## Installation
```bash
cd br2/tier_4/
pip install -r requirements.txt
cp .env.template .env
python tier_4_toy_langgraph_br2_topic_synthesis.py
```

## Tier 4: Coordinated Agents
- ResearchAgent: Finds and analyzes related notes
- SynthesisAgent: Creates synthesized summary note
- Sequential workflow with state passing
