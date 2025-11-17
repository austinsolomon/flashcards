# Retrieval and Vector Stores - Intermediate

## Concept Overview

Vector stores enable semantic search by converting text into high-dimensional embeddings and finding similar content through vector similarity. Retrievers provide a unified interface to query these stores, supporting various search strategies (similarity, MMR, threshold-based). Together, they power RAG systems that augment LLMs with relevant context from large knowledge bases.

**Why it matters:** Simple keyword search misses semantically similar content. Vector search finds "automobile maintenance" when you search for "car repair." Advanced retrieval strategies like Maximum Marginal Relevance (MMR), hybrid search, and metadata filtering dramatically improve RAG accuracy. This is the difference between a chatbot that hallucinates and one that provides accurate, cited answers.

## Real-World Example: Multi-Tenant Legal Document Search System

This example demonstrates a production-grade legal research system with advanced retrieval, metadata filtering, and hybrid search strategies.

```python
from langchain_community.vectorstores import Chroma, Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.retrievers import (
    BaseRetriever,
    EnsembleRetriever,
    MultiQueryRetriever,
    ContextualCompressionRetriever
)
from langchain.retrievers import BM25Retriever
from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain.retrievers.document_compressors import (
    DocumentCompressorPipeline,
    EmbeddingsFilter
)
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any
import chromadb
from datetime import datetime, timedelta

# ========== ADVANCED VECTOR STORE SETUP ==========
class LegalDocumentVectorStore:
    """Production vector store with multi-tenant support and advanced indexing."""

    def __init__(self, collection_name: str = "legal_docs"):
        # Initialize embeddings with caching for performance
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            chunk_size=1000
        )

        # Persistent Chroma with custom settings
        self.client = chromadb.PersistentClient(path="./chroma_db")

        # Create or get collection with metadata indexes
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings,
            collection_metadata={
                "hnsw:space": "cosine",  # Cosine similarity
                "hnsw:construction_ef": 200,  # Higher = better quality, slower indexing
                "hnsw:M": 16  # Number of connections per layer
            }
        )

    def add_documents_with_metadata(self, documents: List[Dict[str, Any]]):
        """Add documents with rich metadata for filtering."""
        docs = []

        for doc_data in documents:
            doc = Document(
                page_content=doc_data['content'],
                metadata={
                    'tenant_id': doc_data['tenant_id'],  # Multi-tenant isolation
                    'document_type': doc_data['doc_type'],  # contract, case_law, statute
                    'jurisdiction': doc_data.get('jurisdiction', 'federal'),
                    'practice_area': doc_data.get('practice_area'),  # IP, corporate, litigation
                    'date_filed': doc_data.get('date_filed'),
                    'case_number': doc_data.get('case_number'),
                    'authority_level': doc_data.get('authority_level', 0),  # 0-10 precedential value
                    'citation': doc_data.get('citation'),
                    'is_current': doc_data.get('is_current', True),
                    'indexed_date': datetime.now().isoformat()
                }
            )
            docs.append(doc)

        # Batch insert for performance
        self.vectorstore.add_documents(docs)
        return len(docs)

# ========== SAMPLE LEGAL DOCUMENTS ==========
sample_legal_docs = [
    {
        'tenant_id': 'firm_abc',
        'content': 'In a dispute over software licensing agreements, the court held that implied warranties under UCC §2-314 apply to software products when sold as goods rather than services. The defendant\'s attempt to disclaim merchantability through EULA was found procedurally unconscionable.',
        'doc_type': 'case_law',
        'jurisdiction': 'california',
        'practice_area': 'technology',
        'date_filed': '2023-08-15',
        'case_number': 'CV-2023-12345',
        'authority_level': 8,
        'citation': 'TechCorp v. SoftwareCo, 234 Cal.App.5th 567 (2023)'
    },
    {
        'tenant_id': 'firm_abc',
        'content': 'Delaware courts consistently apply the business judgment rule to board decisions regarding M&A transactions. Directors must demonstrate they acted on an informed basis, in good faith, and in the honest belief that action taken was in the best interests of shareholders. Enhanced scrutiny under Revlon applies when sale of company is inevitable.',
        'doc_type': 'case_law',
        'jurisdiction': 'delaware',
        'practice_area': 'corporate',
        'date_filed': '2024-01-10',
        'case_number': 'CA-2024-001',
        'authority_level': 10,
        'citation': 'In re MegaCorp Shareholders Litigation, 289 A.3d 123 (Del. Ch. 2024)'
    },
    {
        'tenant_id': 'firm_abc',
        'content': 'Patent claims must satisfy the written description requirement of 35 U.S.C. §112(a). The specification must clearly allow persons of ordinary skill in the art to recognize that the inventor invented what is claimed. Generic claim language covering future innovations not actually invented fails this requirement.',
        'doc_type': 'case_law',
        'jurisdiction': 'federal',
        'practice_area': 'intellectual_property',
        'date_filed': '2023-11-20',
        'authority_level': 9,
        'citation': 'Innovate Inc. v. GenericTech, Fed. Cir. 2023'
    },
    {
        'tenant_id': 'firm_xyz',  # Different tenant
        'content': 'Employment agreements containing non-compete clauses must be reasonable in duration, geographic scope, and scope of prohibited activities. California Business and Professions Code §16600 renders most non-compete agreements void, with narrow exceptions for sale of business or dissolution of partnership.',
        'doc_type': 'statute',
        'jurisdiction': 'california',
        'practice_area': 'employment',
        'authority_level': 10,
        'citation': 'Cal. Bus. & Prof. Code §16600'
    },
]

# Initialize and populate vector store
print("Initializing legal document vector store...")
legal_vs = LegalDocumentVectorStore(collection_name="legal_research_v1")
docs_added = legal_vs.add_documents_with_metadata(sample_legal_docs)
print(f"Added {docs_added} legal documents to vector store\n")

# ========== ADVANCED RETRIEVAL STRATEGIES ==========

# Strategy 1: Metadata-Filtered Similarity Search
def filtered_similarity_search(
    vectorstore: Chroma,
    query: str,
    tenant_id: str,
    practice_area: str = None,
    jurisdiction: str = None,
    min_authority: int = 5
) -> List[Document]:
    """Search with multi-level metadata filtering for multi-tenant isolation."""

    # Build filter expression
    filter_dict = {
        "tenant_id": tenant_id,  # Mandatory tenant isolation
        "is_current": True,
        "authority_level": {"$gte": min_authority}
    }

    if practice_area:
        filter_dict["practice_area"] = practice_area

    if jurisdiction:
        filter_dict["jurisdiction"] = jurisdiction

    results = vectorstore.similarity_search(
        query,
        k=5,
        filter=filter_dict
    )

    return results

# Test filtered search
print("=== Strategy 1: Metadata-Filtered Search ===")
filtered_results = filtered_similarity_search(
    legal_vs.vectorstore,
    query="software licensing warranty issues",
    tenant_id="firm_abc",
    practice_area="technology",
    min_authority=7
)

for i, doc in enumerate(filtered_results):
    print(f"\n[{i+1}] {doc.metadata.get('citation', 'Unknown')}")
    print(f"    Authority: {doc.metadata.get('authority_level')}/10")
    print(f"    Preview: {doc.page_content[:150]}...")

# Strategy 2: MMR (Maximum Marginal Relevance) for Diversity
print("\n\n=== Strategy 2: MMR for Diverse Results ===")

mmr_retriever = legal_vs.vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 20,  # Fetch more candidates
        "lambda_mult": 0.7,  # 0 = max diversity, 1 = max relevance
        "filter": {"tenant_id": "firm_abc"}
    }
)

mmr_results = mmr_retriever.invoke("corporate governance and board duties")

print("MMR returns diverse results across practice areas:")
for i, doc in enumerate(mmr_results):
    print(f"\n[{i+1}] {doc.metadata.get('practice_area')} - {doc.metadata.get('citation')}")
    print(f"    {doc.page_content[:120]}...")

# Strategy 3: Similarity Score Threshold
print("\n\n=== Strategy 3: Similarity Score Threshold ===")

threshold_retriever = legal_vs.vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "score_threshold": 0.8,  # Only return very relevant results
        "k": 10,
        "filter": {"tenant_id": "firm_abc"}
    }
)

threshold_results = threshold_retriever.invoke("patent claim requirements 112")

print(f"Found {len(threshold_results)} results above 0.8 similarity threshold")
for doc in threshold_results:
    print(f"  - {doc.metadata.get('citation')}")

# Strategy 4: Hybrid Search (Semantic + Keyword)
print("\n\n=== Strategy 4: Hybrid Search (BM25 + Vector) ===")

# Create BM25 retriever for keyword search
all_docs = legal_vs.vectorstore.get()['documents']
all_doc_objects = [
    Document(page_content=content, metadata=meta)
    for content, meta in zip(
        legal_vs.vectorstore.get()['documents'],
        legal_vs.vectorstore.get()['metadatas']
    )
]

bm25_retriever = BM25Retriever.from_documents(all_doc_objects)
bm25_retriever.k = 3

# Combine with vector search
vector_retriever = legal_vs.vectorstore.as_retriever(search_kwargs={"k": 3})

ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.4, 0.6]  # Favor semantic search slightly
)

hybrid_results = ensemble_retriever.invoke("UCC section 2-314 warranty merchantability")

print("Hybrid search combines exact term matching with semantic understanding:")
for i, doc in enumerate(hybrid_results):
    print(f"\n[{i+1}] {doc.metadata.get('citation', 'Unknown')}")
    print(f"    {doc.page_content[:100]}...")

# Strategy 5: Multi-Query Retrieval with LLM
print("\n\n=== Strategy 5: Multi-Query Retrieval ===")

llm = ChatOpenAI(model="gpt-4", temperature=0)

multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=legal_vs.vectorstore.as_retriever(
        search_kwargs={"k": 2, "filter": {"tenant_id": "firm_abc"}}
    ),
    llm=llm
)

# This will generate multiple query variations and combine results
multi_query_results = multi_query_retriever.invoke(
    "What are the legal requirements for software warranties?"
)

print("Multi-query generates variations for comprehensive search:")
for i, doc in enumerate(multi_query_results):
    print(f"\n[{i+1}] {doc.metadata.get('citation', 'Unknown')}")

# Strategy 6: Contextual Compression
print("\n\n=== Strategy 6: Contextual Compression ===")

# Filter to only relevant portions of retrieved documents
embeddings_filter = EmbeddingsFilter(
    embeddings=legal_vs.embeddings,
    similarity_threshold=0.75
)

redundant_filter = EmbeddingsRedundantFilter(embeddings=legal_vs.embeddings)

compression_pipeline = DocumentCompressorPipeline(
    transformers=[embeddings_filter, redundant_filter]
)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=compression_pipeline,
    base_retriever=legal_vs.vectorstore.as_retriever(search_kwargs={"k": 5})
)

compressed_results = compression_retriever.invoke(
    "board of directors fiduciary duties in merger transactions"
)

print("Compressed results contain only relevant portions:")
for i, doc in enumerate(compressed_results):
    print(f"\n[{i+1}] {doc.metadata.get('citation', 'Unknown')}")
    print(f"    Compressed content ({len(doc.page_content)} chars):")
    print(f"    {doc.page_content[:200]}...")

# ========== PRODUCTION RETRIEVAL ANALYTICS ==========
print("\n\n=== Retrieval Quality Metrics ===")

def analyze_retrieval_quality(results: List[Document], query: str) -> Dict:
    """Analyze quality metrics for retrieval results."""
    if not results:
        return {"error": "No results returned"}

    return {
        "total_results": len(results),
        "unique_jurisdictions": len(set(d.metadata.get('jurisdiction') for d in results)),
        "unique_practice_areas": len(set(d.metadata.get('practice_area') for d in results)),
        "avg_authority_level": sum(d.metadata.get('authority_level', 0) for d in results) / len(results),
        "date_range": {
            "oldest": min((d.metadata.get('date_filed', '') for d in results if d.metadata.get('date_filed')), default="N/A"),
            "newest": max((d.metadata.get('date_filed', '') for d in results if d.metadata.get('date_filed')), default="N/A")
        }
    }

quality_metrics = analyze_retrieval_quality(filtered_results, "software licensing")
print("Quality metrics for filtered search:")
for metric, value in quality_metrics.items():
    print(f"  {metric}: {value}")
```

### Why This Example Shows Retrieval/Vector Store Power:

1. **Multi-Tenant Isolation**: Secure filtering ensures clients only see their documents
2. **Advanced Search Strategies**: MMR, hybrid, threshold, and multi-query for different use cases
3. **Metadata-Rich Indexing**: Enables precise filtering by jurisdiction, practice area, authority
4. **Contextual Compression**: Reduces noise by extracting only relevant portions
5. **Production Analytics**: Built-in quality metrics to monitor retrieval performance

## Best Practices for Mastering Retrieval and Vector Stores

1. **Always use metadata filtering for multi-tenant systems**: Never rely on embedding similarity alone for security. Use hard filters on tenant_id, user_id, or access_control fields at the vector store level before any similarity search occurs.

2. **Tune MMR lambda for your use case**: Start with λ=0.5 for balanced results. Increase toward 1.0 when precision matters more (legal research, medical queries). Decrease toward 0.0 when you need diverse perspectives (brainstorming, research surveys).

3. **Implement hybrid search for domain-specific terminology**: Pure semantic search misses exact term matches that matter in technical domains (legal citations, medical codes, product SKUs). Combine BM25 (keyword) with vector search using 40/60 or 30/70 weights.

4. **Set fetch_k to 3-5x your target k for MMR and reranking**: When using MMR or compression retrievers, fetch many candidates (fetch_k=20-50) and let the algorithm select the best subset (k=5-10). This dramatically improves diversity and relevance.

5. **Monitor and log retrieval quality metrics continuously**: Track average similarity scores, null result rates, metadata coverage, and user feedback. Set alerts when metrics degrade - this often indicates embedding model drift, data quality issues, or changing user behavior.

## Common Pitfalls to Avoid

- **Don't ignore similarity score thresholds**: Raw k-based retrieval returns junk when nothing is relevant
- **Avoid storing huge chunks**: Embeddings work best on 200-1000 character chunks; larger chunks dilute signal
- **Don't skip metadata indexes**: Filtering on unindexed fields kills performance at scale
- **Remember embedding model lock-in**: Changing embedding models requires complete re-indexing
- **Don't use default HNSW parameters**: Tune `M` and `ef` for your latency/accuracy tradeoff
