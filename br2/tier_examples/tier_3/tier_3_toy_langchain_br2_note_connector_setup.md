# BR2 - Tier 3 - Smart Note Connector (LangChain Agent)

**What It Does**: Given a note, autonomously finds related notes using keyword search, semantic search, and tag search. Suggests bi-directional links to strengthen knowledge graph.

**Tier Characteristics**:
- **Single agent**: One agent finds all connections
- **Multiple search tools**: obsidian_search, semantic_search, tag_search
- **Autonomous strategy**: Agent decides which search methods to use
- **Multi-method discovery**: Combines different search approaches
- **Connection synthesis**: Curates high-value links

---

## Installation & Usage

```bash
cd br2/tier_3/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
# Edit .env with OPENAI_API_KEY
python tier_3_toy_langchain_br2_note_connector.py
```

---

## Why This Is Tier 3

**Tier 3 Characteristics**:
1. **Single Agent** discovers all connections
2. **Multiple Tools** for different search methods
3. **Autonomous Search** - agent chooses strategy
4. **Multi-Method** - combines keyword, semantic, tag searches
5. **Synthesis** - curates best connection recommendations

**Contrast**:
- **Tier 2**: ONE AI call suggests related topics (no actual searching)
- **Tier 3** ←: Single agent with tools, actively searches vault
- **Tier 4**: ResearchAgent → SynthesisAgent → LinkingAgent (multi-agent)
- **Tier 5**: Claude Code orchestrates agent + human review + auto-linking
- **Tier 6**: Autonomous learning of connection patterns over time

---

## Customization

### Add Real Obsidian Integration

```python
def obsidian_search_tool(query: str) -> str:
    import requests
    response = requests.post(
        f"{os.getenv('OBSIDIAN_API_URL')}/search/",
        headers={"Authorization": f"Bearer {os.getenv('OBSIDIAN_API_KEY')}"},
        json={"query": query}
    )
    return format_search_results(response.json())
```

### Add Vector Search

```python
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

def semantic_search_tool(concept: str) -> str:
    vectorstore = FAISS.load_local("obsidian_embeddings")
    results = vectorstore.similarity_search(concept, k=5)
    return format_semantic_results(results)
```

---

## Next Steps: Moving to Tier 4

For **Tier 4** (multi-agent), you would create:
- **ResearchAgent**: Finds candidate notes across all search methods
- **SynthesisAgent**: Analyzes connections and determines relevance
- **LinkingAgent**: Creates bi-directional links in vault

See `tier_4_toy_langgraph_br2_topic_synthesis.py` for multi-agent patterns.
