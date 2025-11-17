# Memory Systems - Intermediate

## Concept Overview

Memory systems enable LLM conversations to maintain context across multiple turns by storing and retrieving conversation history. LangChain provides various memory types: simple buffer memory, summary memory, vector-based memory, and entity memory. Advanced memory systems combine storage backends (Redis, Postgres), retrieval strategies, and summarization to manage long conversations efficiently.

**Why it matters:** Without memory, every LLM call is stateless and can't reference previous interactions. But naive memory approaches hit context limits quickly and become expensive. Production memory systems must balance completeness (remembering important details), efficiency (staying within token limits), and relevance (surfacing the right history for each query).

## Real-World Example: Multi-Session Customer Support System

This example demonstrates a sophisticated customer support chatbot with persistent memory, entity tracking, and intelligent context management across multiple sessions.

```python
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationBufferWindowMemory,
    ConversationEntityMemory,
    VectorStoreRetrieverMemory,
    CombinedMemory
)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.chains import ConversationChain
from datetime import datetime
import json
from typing import Dict, List, Any
import redis

# ========== PRODUCTION MEMORY WITH REDIS BACKEND ==========
class PersistentCustomerMemory:
    """Production-grade memory system with Redis persistence and multi-session support."""

    def __init__(self, customer_id: str, redis_client=None):
        self.customer_id = customer_id
        self.redis_client = redis_client or redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)

        # Memory key for this customer
        self.memory_key = f"customer_memory:{customer_id}"
        self.entity_key = f"customer_entities:{customer_id}"
        self.summary_key = f"customer_summary:{customer_id}"

    def save_interaction(self, human_msg: str, ai_msg: str, metadata: Dict = None):
        """Save interaction to Redis with timestamp and metadata."""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'human': human_msg,
            'ai': ai_msg,
            'metadata': metadata or {}
        }

        # Append to conversation history
        self.redis_client.lpush(
            self.memory_key,
            json.dumps(interaction)
        )

        # Keep only last 100 interactions
        self.redis_client.ltrim(self.memory_key, 0, 99)

    def get_recent_history(self, n: int = 10) -> List[Dict]:
        """Retrieve n most recent interactions."""
        history = self.redis_client.lrange(self.memory_key, 0, n-1)
        return [json.loads(h) for h in history]

    def get_conversation_summary(self) -> str:
        """Get or generate conversation summary."""
        summary = self.redis_client.get(self.summary_key)

        if not summary:
            # Generate summary from history
            history = self.get_recent_history(50)
            if history:
                summary = self._generate_summary(history)
                self.redis_client.setex(
                    self.summary_key,
                    3600,  # Cache for 1 hour
                    summary
                )

        return summary or "No previous conversation history."

    def _generate_summary(self, history: List[Dict]) -> str:
        """Generate concise summary of conversation history."""
        conversation_text = "\n".join([
            f"Customer: {h['human']}\nAgent: {h['ai']}"
            for h in reversed(history)
        ])

        summary_prompt = f"""Summarize this customer support conversation, highlighting:
1. Customer's main issues/requests
2. Solutions provided
3. Unresolved issues
4. Customer sentiment

Conversation:
{conversation_text}

Summary:"""

        summary = self.llm.predict(summary_prompt)
        return summary

    def clear_memory(self):
        """Clear all memory for this customer."""
        self.redis_client.delete(self.memory_key, self.entity_key, self.summary_key)

# ========== ENTITY MEMORY FOR TRACKING CUSTOMER DETAILS ==========
class CustomerEntityTracker:
    """Track and update customer entities (products owned, issues, preferences)."""

    def __init__(self, customer_id: str, redis_client=None):
        self.customer_id = customer_id
        self.redis_client = redis_client or redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        self.entity_key = f"customer_entities:{customer_id}"
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)

    def extract_and_update_entities(self, conversation: str):
        """Extract entities from conversation and update store."""
        extraction_prompt = f"""Extract structured information about this customer from the conversation:

Conversation: {conversation}

Extract and return JSON with:
{{
  "products_owned": ["list of products mentioned"],
  "issues_reported": ["list of problems/issues"],
  "preferences": ["stated preferences"],
  "contact_info": {{"email": "", "phone": ""}},
  "account_details": {{"account_id": "", "subscription_tier": ""}}
}}

Only include information explicitly stated. Use null for unknown values.
"""

        response = self.llm.predict(extraction_prompt)

        try:
            entities = json.loads(response)
            # Merge with existing entities
            self._merge_entities(entities)
        except json.JSONDecodeError:
            print("Failed to parse entity extraction")

    def _merge_entities(self, new_entities: Dict):
        """Merge new entities with existing ones."""
        existing = self.get_entities()

        for key, value in new_entities.items():
            if isinstance(value, list):
                # Merge lists and deduplicate
                existing_list = existing.get(key, [])
                existing[key] = list(set(existing_list + value))
            elif isinstance(value, dict):
                # Merge dicts
                existing[key] = {**existing.get(key, {}), **value}
            else:
                existing[key] = value

        self.redis_client.set(self.entity_key, json.dumps(existing))

    def get_entities(self) -> Dict:
        """Get all tracked entities for this customer."""
        data = self.redis_client.get(self.entity_key)
        return json.loads(data) if data else {}

    def get_context_string(self) -> str:
        """Get entities formatted as context string."""
        entities = self.get_entities()
        if not entities:
            return "No customer information available."

        context_parts = []

        if entities.get('products_owned'):
            context_parts.append(f"Products: {', '.join(entities['products_owned'])}")

        if entities.get('issues_reported'):
            context_parts.append(f"Previous Issues: {', '.join(entities['issues_reported'])}")

        if entities.get('preferences'):
            context_parts.append(f"Preferences: {', '.join(entities['preferences'])}")

        return " | ".join(context_parts) if context_parts else "No customer information available."

# ========== VECTOR MEMORY FOR SEMANTIC RECALL ==========
class VectorSemanticMemory:
    """Vector-based memory for semantic retrieval of past conversations."""

    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        self.embeddings = OpenAIEmbeddings()

        # Create persistent vector store for this customer
        self.vectorstore = Chroma(
            collection_name=f"memory_{customer_id}",
            embedding_function=self.embeddings,
            persist_directory=f"./memory_db/{customer_id}"
        )

    def add_interaction(self, human_msg: str, ai_msg: str, metadata: Dict = None):
        """Add interaction to vector memory."""
        # Store as combined context for better retrieval
        combined = f"Customer: {human_msg}\nAgent: {ai_msg}"

        self.vectorstore.add_texts(
            texts=[combined],
            metadatas=[{
                'timestamp': datetime.now().isoformat(),
                'type': 'interaction',
                **(metadata or {})
            }]
        )

    def get_relevant_history(self, query: str, k: int = 3) -> List[str]:
        """Retrieve semantically similar past interactions."""
        results = self.vectorstore.similarity_search(query, k=k)
        return [doc.page_content for doc in results]

# ========== COMBINED MEMORY SYSTEM ==========
class AdvancedCustomerMemorySystem:
    """Production memory combining multiple strategies."""

    def __init__(self, customer_id: str, redis_client=None):
        self.customer_id = customer_id

        # Initialize all memory components
        self.persistent_memory = PersistentCustomerMemory(customer_id, redis_client)
        self.entity_tracker = CustomerEntityTracker(customer_id, redis_client)
        self.vector_memory = VectorSemanticMemory(customer_id)

        # LLM for conversation
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    def process_message(self, human_msg: str, metadata: Dict = None) -> str:
        """Process incoming message with full memory context."""

        # 1. Get conversation summary
        summary = self.persistent_memory.get_conversation_summary()

        # 2. Get relevant past interactions via semantic search
        relevant_history = self.vector_memory.get_relevant_history(human_msg, k=3)

        # 3. Get entity context
        entity_context = self.entity_tracker.get_context_string()

        # 4. Get recent conversation (last 5 turns)
        recent_history = self.persistent_memory.get_recent_history(5)
        recent_formatted = "\n".join([
            f"Customer: {h['human']}\nAgent: {h['ai']}"
            for h in reversed(recent_history)
        ])

        # 5. Build comprehensive prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""You are a helpful customer support agent.

CUSTOMER INFORMATION:
{entity_context}

CONVERSATION SUMMARY:
{summary}

RELEVANT PAST INTERACTIONS:
{chr(10).join(relevant_history) if relevant_history else 'None'}

RECENT CONVERSATION:
{recent_formatted if recent_formatted else 'This is the first message.'}
"""),
            HumanMessage(content=human_msg)
        ])

        # 6. Generate response
        response = self.llm.invoke(prompt.format_messages())
        ai_msg = response.content

        # 7. Save interaction to all memory systems
        self.persistent_memory.save_interaction(human_msg, ai_msg, metadata)
        self.vector_memory.add_interaction(human_msg, ai_msg, metadata)

        # 8. Update entities asynchronously (in production, use task queue)
        full_interaction = f"Customer: {human_msg}\nAgent: {ai_msg}"
        self.entity_tracker.extract_and_update_entities(full_interaction)

        return ai_msg

    def get_memory_stats(self) -> Dict:
        """Get statistics about memory usage."""
        return {
            'customer_id': self.customer_id,
            'total_interactions': len(self.persistent_memory.get_recent_history(100)),
            'entities_tracked': len(self.entity_tracker.get_entities()),
            'has_summary': bool(self.persistent_memory.get_conversation_summary()),
        }

# ========== PRODUCTION USAGE EXAMPLE ==========
def simulate_customer_support_session():
    """Simulate multi-turn customer support conversation."""

    # Initialize memory system for customer
    memory_system = AdvancedCustomerMemorySystem(
        customer_id="CUST_12345",
        redis_client=None  # Use in-memory for demo; use real Redis in production
    )

    print("=== Customer Support Session ===\n")

    # Conversation turn 1
    msg1 = "Hi, I'm having trouble with my XL-2000 printer. It keeps jamming."
    response1 = memory_system.process_message(msg1, metadata={'channel': 'chat', 'priority': 'medium'})
    print(f"Customer: {msg1}")
    print(f"Agent: {response1}\n")

    # Conversation turn 2
    msg2 = "I've tried that already. The paper tray seems fine. Could it be a hardware issue?"
    response2 = memory_system.process_message(msg2)
    print(f"Customer: {msg2}")
    print(f"Agent: {response2}\n")

    # Conversation turn 3
    msg3 = "Also, I noticed my ink levels seem wrong. Shows full but prints are faded."
    response3 = memory_system.process_message(msg3)
    print(f"Customer: {msg3}")
    print(f"Agent: {response3}\n")

    # Show tracked entities
    entities = memory_system.entity_tracker.get_entities()
    print("\n=== Tracked Entities ===")
    print(json.dumps(entities, indent=2))

    # Show memory stats
    stats = memory_system.get_memory_stats()
    print("\n=== Memory Statistics ===")
    print(json.dumps(stats, indent=2))

    # Simulate new session later - memory persists
    print("\n\n=== New Session (3 days later) ===\n")

    msg4 = "Hi, I'm back. The printer issue was resolved but now I need help with setup."
    response4 = memory_system.process_message(msg4, metadata={'session': 'new'})
    print(f"Customer: {msg4}")
    print(f"Agent: {response4}")
    print("\n[Notice how the agent remembers the printer model and previous issues!]")

# Run simulation
# simulate_customer_support_session()

# ========== MEMORY COMPRESSION STRATEGY ==========
class CompressedMemoryManager:
    """Manages memory compression to stay within token limits."""

    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)

    def compress_if_needed(self, history: List[Dict]) -> List[Dict]:
        """Compress old history if token count exceeds limit."""

        total_tokens = self._estimate_tokens(history)

        if total_tokens <= self.max_tokens:
            return history

        # Keep recent 5 turns verbatim, summarize the rest
        recent = history[-5:]
        old = history[:-5]

        if old:
            summary = self._summarize_interactions(old)
            # Return summary + recent messages
            return [{
                'timestamp': old[0]['timestamp'],
                'human': 'SUMMARY',
                'ai': summary,
                'metadata': {'compressed': True}
            }] + recent

        return recent

    def _estimate_tokens(self, history: List[Dict]) -> int:
        """Rough token estimation (4 chars ≈ 1 token)."""
        total_chars = sum(len(h['human']) + len(h['ai']) for h in history)
        return total_chars // 4

    def _summarize_interactions(self, interactions: List[Dict]) -> str:
        """Summarize old interactions."""
        text = "\n".join([
            f"Customer: {h['human']}\nAgent: {h['ai']}"
            for h in interactions
        ])

        prompt = f"Summarize this conversation history concisely:\n\n{text}\n\nSummary:"
        return self.llm.predict(prompt)

print("\n=== Example: Compressed Memory Manager ===")
compressor = CompressedMemoryManager(max_tokens=100)  # Very low for demo

demo_history = [
    {'timestamp': '2024-01-01', 'human': 'Hello', 'ai': 'Hi there!', 'metadata': {}},
    {'timestamp': '2024-01-01', 'human': 'I need help', 'ai': 'What can I help with?', 'metadata': {}},
    {'timestamp': '2024-01-02', 'human': 'My order is late', 'ai': 'Let me check that', 'metadata': {}},
]

# compressed = compressor.compress_if_needed(demo_history)
# print(f"Original: {len(demo_history)} interactions")
# print(f"Compressed: {len(compressed)} interactions")
```

### Why This Example Shows Memory System Power:

1. **Multi-Backend Persistence**: Redis for fast access, vector store for semantic search
2. **Entity Tracking**: Automatically extracts and maintains customer context
3. **Layered Context**: Combines summary, recent history, and relevant past interactions
4. **Session Continuity**: Remembers across sessions days/weeks apart
5. **Compression Strategy**: Manages token limits while preserving important context

## Best Practices for Mastering Memory Systems

1. **Use layered memory with different retention strategies**: Keep the last 5-10 turns verbatim (buffer), summarize 10-50 turns back (summary), and use vector search for older relevant context. This balances recency, completeness, and token efficiency.

2. **Extract and track entities separately from conversation flow**: Use LLMs to extract structured facts (names, products, preferences, issues) and store them in a separate entity store. This prevents important details from being compressed away and enables precise retrieval.

3. **Always add timestamps and metadata to memory**: Tag each interaction with timestamp, channel (chat/email/phone), session ID, and user ID. This enables time-based filtering, cross-session analysis, and debugging of memory-related issues.

4. **Implement memory compression before hitting token limits**: Don't wait until you're at the context limit. Set a threshold at 70-80% of max tokens and compress old history into summaries. Keep recent turns verbatim for coherent conversation flow.

5. **Use vector memory for semantic recall in long conversations**: When conversations span days or have multiple topics, BM25 or recency-based recall fails. Vector memory retrieves contextually relevant history regardless of when it occurred, dramatically improving multi-session coherence.

## Common Pitfalls to Avoid

- **Don't store raw messages without structure**: Always parse and extract entities
- **Avoid unbounded memory growth**: Set retention policies and compression thresholds
- **Don't ignore metadata**: Session IDs, timestamps, and user IDs are critical for debugging
- **Remember token counting**: Memory is the #1 cause of unexpected token limit errors
- **Don't skip persistence**: In-memory-only memory breaks across restarts
