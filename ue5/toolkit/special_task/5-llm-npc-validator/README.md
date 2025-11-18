# LLM NPC Behavior Validator

**Tier**: 3 (Autonomous Agent)
**Category**: Special Task - Massive Level Development

## Purpose

Validates NPC AI behavior trees and decision logic for compatibility with small LLM models. Ensures behavior complexity is appropriate for lightweight inference while maintaining believable NPC interactions.

## What It Does

- Analyzes behavior tree complexity and state count
- Validates prompt templates for small LLM models (1-7B parameters)
- Estimates inference latency for behavior decisions
- Checks context window usage
- Suggests behavior simplifications
- Tests NPC responses for consistency and quality
- Generates optimized prompts for resource-constrained models

## Use Case

When implementing LLM-driven NPC AI in a massive open world, you need to balance realistic behavior with performance constraints. Small models require carefully crafted prompts and simplified decision trees.

## Implementation

```yaml
# automation.yaml
name: llm-npc-validator
tier: 3

agent:
  model: claude-sonnet-4.5

  system_prompt: |
    You are an expert in AI behavior design and LLM optimization. Validate
    NPC behavior configurations for compatibility with small language models
    (1-7B parameters). Focus on prompt efficiency, context management, and
    maintaining performance in real-time game scenarios.

capabilities:
  - analyze_behavior_trees
  - validate_prompt_templates
  - estimate_inference_cost
  - test_response_quality
  - suggest_optimizations
  - generate_fallback_behaviors

validation_criteria:
  max_context_tokens: 2048
  max_inference_latency_ms: 100
  min_response_quality_score: 0.7
  max_behavior_states: 15
```

## Usage

```bash
# Validate single NPC behavior
python llm_npc_validator.py --npc "BP_Villager_Merchant"

# Batch validate all NPCs
python llm_npc_validator.py --batch --directory "Content/NPCs"

# Test with specific small model
python llm_npc_validator.py --npc "BP_Guard" --model "llama3-7b"

# Generate optimization report
python llm_npc_validator.py --npc "BP_QuestGiver" --optimize --report
```

## Example Analysis

**Input: NPC Behavior Configuration**
```json
{
  "npc_type": "Merchant",
  "behavior_tree": "BT_Merchant_Complex",
  "personality": "Shrewd trader, suspicious of strangers",
  "knowledge_base": [
    "local_economy",
    "trade_routes",
    "current_events",
    "player_reputation",
    "inventory_items"
  ],
  "llm_config": {
    "model": "phi-3-mini",
    "context_window": 4096,
    "prompt_template": "merchant_dialogue.txt"
  }
}
```

**Output: Validation Report**
```
LLM NPC Behavior Validation
NPC: BP_Villager_Merchant
Target Model: phi-3-mini (3.8B parameters)

BEHAVIOR TREE ANALYSIS
States: 12 ✅ (within 15 state limit)
Complexity Score: 7.2/10 ⚠️  (recommend simplifying)

Decision nodes requiring LLM: 6
├─ Greeting (simple)
├─ Negotiation (complex) ⚠️
├─ Quest dialogue (complex) ⚠️
├─ Gossip (moderate)
├─ Trade refusal (simple)
└─ Farewell (simple)

PROMPT ANALYSIS
Template: merchant_dialogue.txt
Base tokens: 450 ✅
Max context with history: 1,850 tokens ✅ (within 2048 limit)

⚠️  ISSUE: Prompt includes full inventory (200+ items)
   Recommendation: Summarize inventory to categories

⚠️  ISSUE: Includes extensive world lore (600 tokens)
   Recommendation: Use dynamic context injection only when relevant

INFERENCE PERFORMANCE
Estimated latency (phi-3-mini on RTX 3080):
├─ Simple responses: 45-60ms ✅
├─ Moderate responses: 75-95ms ✅
└─ Complex negotiations: 120-150ms ⚠️  (exceeds 100ms budget)

Concurrent NPC limit: ~8 NPCs @ 60 FPS

RESPONSE QUALITY TESTING
Test scenarios: 20
├─ Greeting strangers: 0.85 ✅
├─ Price negotiation: 0.72 ✅
├─ Quest hints: 0.68 ⚠️  (below 0.7 threshold)
├─ Reacting to theft: 0.79 ✅
└─ Small talk: 0.91 ✅

⚠️  QUALITY ISSUE: Quest hints sometimes too vague
   Recommendation: Add structured output format for quest dialogue

OPTIMIZATION RECOMMENDATIONS

1. PROMPT OPTIMIZATION (Est. -300 tokens)
   Before:
   "You are a shrewd merchant in the bustling city of Ironhaven. You've
   seen many travelers come and go. You know the local trade routes,
   economy, and have a deep suspicion of strangers until they prove
   themselves worthy. Your inventory includes: [200 items listed]..."

   After:
   "Merchant. Suspicious. Inventory: weapons, potions, supplies.
   Personality: shrewd trader. Context: {dynamic_context}"

   Benefit: 67% token reduction, similar quality

2. BEHAVIOR SIMPLIFICATION
   Complex negotiation node → Rule-based system
   ├─ Use LLM for dialogue flavor only
   ├─ Price calculations via traditional code
   └─ Save LLM tokens for interesting interactions

3. FALLBACK BEHAVIORS
   Implement canned responses for:
   ├─ Common greetings (no LLM needed)
   ├─ Standard transactions (rule-based)
   └─ LLM only for: custom requests, conversations, quests

   Est. LLM usage reduction: 60%

4. CONTEXT MANAGEMENT
   Dynamic context injection:
   - Load "local_economy" only during trade
   - Load "current_events" only during gossip
   - Load "player_reputation" always (small footprint)

   Token savings: ~400 tokens per interaction

5. MODEL-SPECIFIC TUNING
   Phi-3-mini performs better with:
   - Shorter, more direct prompts
   - Structured output formats (JSON)
   - Few-shot examples (2-3 max)
   - Clear role definition

OPTIMIZED CONFIGURATION

{
  "npc_type": "Merchant",
  "behavior_tree": "BT_Merchant_Optimized",
  "llm_triggers": [
    "custom_dialogue",
    "quest_interaction",
    "unique_situations"
  ],
  "fallback_behaviors": {
    "greeting": "canned_responses",
    "trade": "rule_based",
    "farewell": "canned_responses"
  },
  "llm_config": {
    "model": "phi-3-mini",
    "max_tokens": 150,
    "prompt_template": "merchant_dialogue_optimized.txt",
    "context_strategy": "dynamic_injection"
  },
  "performance_targets": {
    "max_latency_ms": 100,
    "max_context_tokens": 1500,
    "min_quality_score": 0.75
  }
}

ESTIMATED IMPROVEMENTS
✅ Inference latency: 120ms → 65ms (46% faster)
✅ Context usage: 1850 → 800 tokens (57% reduction)
✅ Quality score: 0.74 → 0.81 (maintained/improved)
✅ Concurrent NPCs: 8 → 15 (87% increase)

TESTING RECOMMENDATIONS
1. Profile on target hardware (console GPU may differ)
2. Test with 10+ concurrent NPC conversations
3. Monitor VRAM usage with model loaded
4. Implement graceful degradation if GPU busy
5. Consider model quantization (FP16 → INT8) for more NPCs
```

## Model Compatibility Matrix

| Model | Parameters | Recommended NPCs | Avg Latency | Quality |
|-------|-----------|------------------|-------------|---------|
| Phi-3-mini | 3.8B | 15-20 | 65ms | ⭐⭐⭐⭐ |
| Llama3-7B | 7B | 8-12 | 95ms | ⭐⭐⭐⭐⭐ |
| Gemma-2B | 2B | 25-30 | 40ms | ⭐⭐⭐ |
| TinyLlama | 1.1B | 40+ | 25ms | ⭐⭐ |

## Files

- `llm_npc_validator.py` - Main validation agent
- `model_configs/` - Small LLM model specifications
- `prompt_templates/` - Optimized prompt templates
- `test_scenarios/` - NPC interaction test cases
- `optimization_strategies.yaml` - Behavior optimization rules
- `fallback_behaviors/` - Rule-based fallback systems
