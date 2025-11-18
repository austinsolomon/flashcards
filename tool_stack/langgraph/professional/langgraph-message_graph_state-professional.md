# LangGraph Message Graph State

## Concept Overview

Message Graph State is a specialized pattern in LangGraph where the primary state structure is built around conversation messages, with optional metadata and reducers to manage message history efficiently. This pattern is ideal for conversational AI, multi-turn dialogs, and systems that need to maintain rich conversation context. Understanding how to structure, reduce, and serialize message state is critical for building scalable conversational applications.

---

## Intermediate Level: Message State with Memory Tracking and Reducers

A customer support bot with message filtering, summarization, and metadata tracking to optimize context window usage.

```python
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from datetime import datetime
import operator

class MessageMetadata(BaseModel):
    """Metadata for each message."""
    timestamp: str
    source: str  # "customer" or "support"
    sentiment: Optional[str] = None
    category: Optional[str] = None
    tokens_estimate: int = 0

class ConversationState(BaseModel):
    """State with message reducer to manage token usage."""
    messages: Annotated[list[BaseMessage], add_messages]
    metadata: dict[str, MessageMetadata] = Field(default_factory=dict)
    summary: str = ""
    message_count: int = 0
    context_window_usage: int = 0
    customer_id: str = ""

def create_support_chatbot():
    llm = ChatOpenAI(model="gpt-4")
    summary_llm = ChatOpenAI(model="gpt-3.5-turbo")

    def analyze_sentiment(text: str) -> str:
        """Quick sentiment analysis."""
        if any(word in text.lower() for word in ["great", "excellent", "thanks"]):
            return "positive"
        elif any(word in text.lower() for word in ["bad", "terrible", "angry"]):
            return "negative"
        return "neutral"

    def should_summarize(state: ConversationState) -> bool:
        """Check if messages should be summarized to save context."""
        return state.message_count > 10 and state.context_window_usage > 2000

    def summarize_messages(state: ConversationState) -> dict:
        """Summarize older messages to preserve context efficiently."""
        if len(state.messages) > 5:
            # Keep only recent messages, summarize older ones
            messages_to_summarize = state.messages[:-5]
            recent_messages = state.messages[-5:]

            summary_prompt = f"""Summarize the following conversation in 2-3 sentences:
            {chr(10).join([m.content for m in messages_to_summarize])}"""

            summary = summary_llm.invoke([HumanMessage(content=summary_prompt)])
            new_summary = f"{state.summary}\n\n{summary.content}".strip()

            return {
                "messages": recent_messages + [SystemMessage(content=f"Previous conversation summary: {new_summary}")],
                "summary": new_summary,
                "message_count": len(recent_messages)
            }
        return state

    def support_agent_node(state: ConversationState):
        """Main support agent node."""
        response = llm.invoke(state.messages)

        # Update metadata
        msg_id = f"msg_{state.message_count + 1}"
        state.metadata[msg_id] = MessageMetadata(
            timestamp=datetime.now().isoformat(),
            source="support",
            sentiment=analyze_sentiment(response.content),
            tokens_estimate=len(response.content) // 4
        )

        return {
            "messages": [response],
            "context_window_usage": state.context_window_usage + len(response.content),
            "message_count": state.message_count + 1
        }

    # Build workflow
    workflow = StateGraph(ConversationState)
    workflow.add_node("analyze", lambda s: {"message_count": s.message_count + 1})
    workflow.add_node("support", support_agent_node)
    workflow.add_node("summarize", summarize_messages)

    workflow.add_edge(START, "analyze")
    workflow.add_conditional_edges(
        "analyze",
        lambda s: "summarize" if should_summarize(s) else "support",
        {"summarize": "summarize", "support": "support"}
    )
    workflow.add_edge("summarize", "support")
    workflow.add_edge("support", END)

    return workflow.compile()

# Usage
chatbot = create_support_chatbot()
state = ConversationState(
    messages=[SystemMessage(content="You are a helpful customer support agent.")],
    customer_id="cust_001"
)

for i in range(3):
    state = chatbot.invoke(state)
    if state.messages:
        print(f"Turn {i+1}: {state.messages[-1].content[:100]}...")
```

---

## Best Practices for Message Graph State Mastery

1. **Use Message Reducers Strategically**: Leverage `add_messages` reducer to append messages cleanly, preventing duplicates. For large conversations, implement token-aware reducers that summarize or trim older messages to stay within LLM context limits.

2. **Metadata Enrichment**: Attach rich metadata (sentiment, intent, channel, timestamp) to each message early. This enables intelligent routing, filtering, and auditing without re-analyzing messages later.

3. **Thread-Based Organization**: For multi-turn or multi-channel conversations, organize messages into threads. Each thread maintains its own context, enabling parallel processing and easier state isolation.

4. **Implement Message Indexing**: Maintain fast lookups via `message_index` dictionary. This prevents O(n) searches through message lists and enables efficient graph-based operations on message relationships.

5. **Version Control and Audit Trails**: Track state versions with timestamps and change types. This provides observability, enables rollback capabilities, and supports compliance requirements in enterprise systems.
