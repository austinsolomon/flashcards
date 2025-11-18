# LangGraph Message Graph State

## Concept Overview

Message Graph State is a specialized pattern in LangGraph where the primary state structure is built around conversation messages, with optional metadata and reducers to manage message history efficiently. This pattern is ideal for conversational AI, multi-turn dialogs, and systems that need to maintain rich conversation context. Understanding how to structure, reduce, and serialize message state is critical for building scalable conversational applications.

---

## Advanced Level: Enterprise Message Graph with Distributed State Management

A sophisticated system managing multi-channel conversations with branching threads, state versioning, and efficient message persistence.

```python
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Annotated, Optional, Literal
from datetime import datetime
import operator
from enum import Enum
import uuid
import json

class MessageRole(str, Enum):
    """Message roles for classification."""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    TOOL = "tool"

class MessageNode(BaseModel):
    """Enhanced message node with full metadata."""
    id: str
    content: str
    role: MessageRole
    timestamp: str
    channel: str  # "email", "chat", "phone", etc.
    parent_message_id: Optional[str] = None
    thread_id: str
    metadata: dict = Field(default_factory=dict)
    tokens: int
    sentiment: str
    intent: str

class ConversationThread(BaseModel):
    """Represents a conversation thread."""
    thread_id: str
    created_at: str
    customer_id: str
    messages: Annotated[list[MessageNode], add_messages]
    context: dict = Field(default_factory=dict)
    status: Literal["active", "resolved", "escalated"] = "active"
    priority: int = 0

class EnterpriseMessageState(BaseModel):
    """Enterprise-grade state with thread management."""
    active_threads: dict[str, ConversationThread]
    message_index: dict[str, MessageNode]  # Fast lookup
    conversation_graph: dict[str, list[str]]  # Message relationships
    state_versions: Annotated[list[dict], operator.add] = Field(default_factory=list)
    request_context: dict
    tenant_id: str
    audit_log: Annotated[list[dict], operator.add] = Field(default_factory=list)

class AdvancedMessageGraphManager:
    """Manages complex message graph operations."""
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4")
        self.classifier_llm = ChatOpenAI(model="gpt-3.5-turbo")

    async def classify_message(self, content: str) -> tuple[str, str]:
        """Classify message sentiment and intent."""
        classification = await self.classifier_llm.ainvoke([
            HumanMessage(content=f"Classify sentiment (positive/neutral/negative) and intent (inquiry/complaint/feedback) for: {content}")
        ])
        # Parse response
        return "neutral", "inquiry"  # Simplified

    def create_message_node(
        self,
        content: str,
        role: MessageRole,
        channel: str,
        thread_id: str,
        parent_id: Optional[str] = None
    ) -> MessageNode:
        """Create a message node with metadata."""
        sentiment, intent = "neutral", "inquiry"  # Would be async in production
        return MessageNode(
            id=str(uuid.uuid4()),
            content=content,
            role=role,
            timestamp=datetime.now().isoformat(),
            channel=channel,
            parent_message_id=parent_id,
            thread_id=thread_id,
            tokens=len(content) // 4,
            sentiment=sentiment,
            intent=intent,
            metadata={"processed": True, "version": 1}
        )

    def update_message_graph(
        self,
        state: EnterpriseMessageState,
        message: MessageNode
    ) -> dict:
        """Update graph structure with new message."""
        thread_id = message.thread_id

        # Update thread
        if thread_id not in state.active_threads:
            state.active_threads[thread_id] = ConversationThread(
                thread_id=thread_id,
                created_at=datetime.now().isoformat(),
                customer_id="",
                messages=[]
            )

        # Add to index
        state.message_index[message.id] = message

        # Update relationships
        if message.parent_message_id:
            if message.parent_message_id not in state.conversation_graph:
                state.conversation_graph[message.parent_message_id] = []
            state.conversation_graph[message.parent_message_id].append(message.id)

        # Create state version
        version = {
            "version_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "message_id": message.id,
            "thread_id": thread_id,
            "change_type": "message_added"
        }

        return {
            "active_threads": state.active_threads,
            "message_index": state.message_index,
            "conversation_graph": state.conversation_graph,
            "state_versions": [version]
        }

    def get_thread_context(
        self,
        state: EnterpriseMessageState,
        thread_id: str,
        max_depth: int = 3
    ) -> list[MessageNode]:
        """Get message context for a thread with depth limiting."""
        thread = state.active_threads.get(thread_id)
        if not thread:
            return []

        # Return last N messages to manage context window
        return thread.messages[-max_depth:]

    async def route_message(
        self,
        state: EnterpriseMessageState,
        message_id: str
    ) -> str:
        """Route message to appropriate handler."""
        message = state.message_index.get(message_id)
        if not message:
            return "error"

        if message.intent == "complaint":
            return "escalate"
        elif message.intent == "feedback":
            return "log"
        return "respond"

def create_enterprise_message_system():
    """Create enterprise message graph system."""
    manager = AdvancedMessageGraphManager()

    async def ingest_message(state: EnterpriseMessageState):
        """Ingest and process new message."""
        # Simplified ingestion
        return state

    async def route_handler(state: EnterpriseMessageState):
        """Route messages based on classification."""
        if not state.message_index:
            return state

        latest_msg_id = list(state.message_index.keys())[-1]
        route = await manager.route_message(state, latest_msg_id)

        return {"request_context": {"route": route}}

    async def respond_node(state: EnterpriseMessageState):
        """Generate response."""
        thread_id = list(state.active_threads.keys())[0] if state.active_threads else None
        if not thread_id:
            return state

        context_msgs = manager.get_thread_context(state, thread_id)
        response = await manager.llm.ainvoke([m.content for m in context_msgs])

        new_message = manager.create_message_node(
            content=response.content,
            role=MessageRole.AGENT,
            channel="chat",
            thread_id=thread_id
        )

        return manager.update_message_graph(state, new_message)

    # Build workflow
    workflow = StateGraph(EnterpriseMessageState)
    workflow.add_node("ingest", ingest_message)
    workflow.add_node("route", route_handler)
    workflow.add_node("respond", respond_node)

    workflow.add_edge(START, "ingest")
    workflow.add_edge("ingest", "route")
    workflow.add_conditional_edges(
        "route",
        lambda s: s.request_context.get("route", "respond"),
        {"respond": "respond", "escalate": END, "log": END, "error": END}
    )
    workflow.add_edge("respond", END)

    return workflow.compile()

# Usage
async def main():
    system = create_enterprise_message_system()
    thread_id = str(uuid.uuid4())

    initial_state = EnterpriseMessageState(
        active_threads={},
        message_index={},
        conversation_graph={},
        state_versions=[],
        request_context={},
        tenant_id="tenant_001",
        audit_log=[]
    )

    # Would execute with asyncio
    return initial_state
```

---

## Best Practices for Message Graph State Mastery

1. **Use Message Reducers Strategically**: Leverage `add_messages` reducer to append messages cleanly, preventing duplicates. For large conversations, implement token-aware reducers that summarize or trim older messages to stay within LLM context limits.

2. **Metadata Enrichment**: Attach rich metadata (sentiment, intent, channel, timestamp) to each message early. This enables intelligent routing, filtering, and auditing without re-analyzing messages later.

3. **Thread-Based Organization**: For multi-turn or multi-channel conversations, organize messages into threads. Each thread maintains its own context, enabling parallel processing and easier state isolation.

4. **Implement Message Indexing**: Maintain fast lookups via `message_index` dictionary. This prevents O(n) searches through message lists and enables efficient graph-based operations on message relationships.

5. **Version Control and Audit Trails**: Track state versions with timestamps and change types. This provides observability, enables rollback capabilities, and supports compliance requirements in enterprise systems.
