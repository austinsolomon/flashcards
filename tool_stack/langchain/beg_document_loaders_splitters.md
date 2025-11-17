# Document Loaders and Text Splitters - Beginner

## Concept Overview

Document loaders ingest data from various sources (PDFs, websites, databases, APIs) and convert them into LangChain's `Document` format. Text splitters then intelligently chunk these documents into smaller pieces that fit within LLM context windows while preserving semantic meaning. Together, they form the foundation of any RAG (Retrieval-Augmented Generation) system.

**Why it matters:** Raw documents are too large for LLM context windows and too unstructured for effective retrieval. Proper loading and splitting is critical for RAG accuracy - bad chunking leads to poor retrieval, which leads to wrong answers. This is where 80% of RAG systems fail.

## Real-World Example: Multi-Source Technical Documentation System

This example demonstrates a production-grade documentation ingestion pipeline that handles multiple formats and intelligently chunks technical content.

```python
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    GitHubIssuesLoader,
    WebBaseLoader,
    DirectoryLoader,
)
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    CodeTextSplitter,
    TokenTextSplitter
)
from langchain_core.documents import Document
from typing import List
import os

# ========== CUSTOM LOADER FOR API DOCUMENTATION ==========
class APIDocLoader:
    """Custom loader for API documentation with metadata enrichment."""

    def __init__(self, api_docs_path: str, api_version: str):
        self.api_docs_path = api_docs_path
        self.api_version = api_version

    def load(self) -> List[Document]:
        """Load API docs and enrich with structured metadata."""
        docs = []

        for root, dirs, files in os.walk(self.api_docs_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)

                    # Load markdown content
                    loader = UnstructuredMarkdownLoader(file_path)
                    file_docs = loader.load()

                    # Enrich with API-specific metadata
                    for doc in file_docs:
                        # Extract endpoint from filename (e.g., "POST_users_create.md")
                        parts = file.replace('.md', '').split('_')
                        method = parts[0] if parts else 'UNKNOWN'
                        endpoint = '/' + '/'.join(parts[1:]) if len(parts) > 1 else '/'

                        doc.metadata.update({
                            'source_type': 'api_documentation',
                            'api_version': self.api_version,
                            'http_method': method,
                            'endpoint': endpoint,
                            'file_path': file_path,
                            'category': os.path.basename(root)
                        })
                        docs.append(doc)

        return docs

# ========== MULTI-SOURCE LOADING ==========
def load_all_documentation(config: dict) -> List[Document]:
    """Load documentation from multiple sources with appropriate loaders."""
    all_docs = []

    # 1. Load PDF user guides
    if 'pdf_dir' in config:
        pdf_loader = DirectoryLoader(
            config['pdf_dir'],
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True
        )
        pdf_docs = pdf_loader.load()
        for doc in pdf_docs:
            doc.metadata['source_type'] = 'user_guide'
            doc.metadata['format'] = 'pdf'
        all_docs.extend(pdf_docs)
        print(f"Loaded {len(pdf_docs)} PDF documents")

    # 2. Load API documentation (custom loader)
    if 'api_docs_path' in config:
        api_loader = APIDocLoader(
            api_docs_path=config['api_docs_path'],
            api_version=config.get('api_version', 'v1')
        )
        api_docs = api_loader.load()
        all_docs.extend(api_docs)
        print(f"Loaded {len(api_docs)} API documentation pages")

    # 3. Load GitHub issues for troubleshooting knowledge
    if 'github_repo' in config:
        github_loader = GitHubIssuesLoader(
            repo=config['github_repo'],
            access_token=config.get('github_token'),
            state="closed",  # Only closed issues with solutions
            include_prs=False
        )
        github_docs = github_loader.load()
        for doc in github_docs:
            doc.metadata['source_type'] = 'github_issue'
        all_docs.extend(github_docs)
        print(f"Loaded {len(github_docs)} GitHub issues")

    # 4. Load changelog from website
    if 'changelog_url' in config:
        web_loader = WebBaseLoader([config['changelog_url']])
        web_docs = web_loader.load()
        for doc in web_docs:
            doc.metadata['source_type'] = 'changelog'
        all_docs.extend(web_docs)
        print(f"Loaded changelog documentation")

    return all_docs

# ========== INTELLIGENT SPLITTING STRATEGY ==========
class AdaptiveDocumentSplitter:
    """Adaptively split documents based on content type and structure."""

    def __init__(self):
        # Code splitter for technical content
        self.code_splitter = RecursiveCharacterTextSplitter.from_language(
            language="python",
            chunk_size=1000,
            chunk_overlap=200
        )

        # Markdown splitter that preserves headers as metadata
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "h1"),
                ("##", "h2"),
                ("###", "h3"),
            ]
        )

        # General text splitter with smart overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=True
        )

        # Token-based splitter for precise control
        self.token_splitter = TokenTextSplitter(
            chunk_size=512,
            chunk_overlap=50
        )

    def split_documents(self, docs: List[Document]) -> List[Document]:
        """Split documents using appropriate strategy based on content."""
        all_splits = []

        for doc in docs:
            source_type = doc.metadata.get('source_type', '')

            # Choose splitting strategy based on document type
            if source_type == 'api_documentation':
                # API docs: use markdown splitter to preserve structure
                md_splits = self.markdown_splitter.split_text(doc.page_content)

                # Then apply token splitter for final sizing
                for md_doc in md_splits:
                    token_splits = self.token_splitter.split_documents([md_doc])
                    for split in token_splits:
                        # Preserve original metadata and add header context
                        split.metadata.update(doc.metadata)
                    all_splits.extend(token_splits)

            elif 'code' in doc.page_content.lower() or '```' in doc.page_content:
                # Code-heavy content: use code-aware splitter
                code_splits = self.code_splitter.split_documents([doc])
                for split in code_splits:
                    split.metadata.update(doc.metadata)
                all_splits.extend(code_splits)

            elif source_type == 'github_issue':
                # Issues: keep conversation threads together
                # Use larger chunks with more overlap
                issue_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1500,
                    chunk_overlap=300
                )
                issue_splits = issue_splitter.split_documents([doc])
                for split in issue_splits:
                    split.metadata.update(doc.metadata)
                all_splits.extend(issue_splits)

            else:
                # Default: recursive character splitting
                default_splits = self.text_splitter.split_documents([doc])
                for split in default_splits:
                    split.metadata.update(doc.metadata)
                all_splits.extend(default_splits)

        return all_splits

# ========== PRODUCTION USAGE ==========
# Configuration
config = {
    'pdf_dir': './docs/user_guides',
    'api_docs_path': './docs/api',
    'api_version': 'v2.1',
    'github_repo': 'company/product',
    'github_token': os.getenv('GITHUB_TOKEN'),
    'changelog_url': 'https://company.com/changelog'
}

# Load all documentation
print("Loading documentation from multiple sources...")
raw_documents = load_all_documentation(config)
print(f"\nTotal documents loaded: {len(raw_documents)}")

# Analyze source distribution
source_counts = {}
for doc in raw_documents:
    source = doc.metadata.get('source_type', 'unknown')
    source_counts[source] = source_counts.get(source, 0) + 1

print("\nDocument distribution by source:")
for source, count in source_counts.items():
    print(f"  {source}: {count}")

# Split documents intelligently
print("\nSplitting documents...")
splitter = AdaptiveDocumentSplitter()
split_documents = splitter.split_documents(raw_documents)

print(f"\nTotal chunks created: {len(split_documents)}")
print(f"Average chunk size: {sum(len(d.page_content) for d in split_documents) / len(split_documents):.0f} characters")

# Analyze a sample split
sample_doc = split_documents[0]
print(f"\n=== Sample Document Chunk ===")
print(f"Source Type: {sample_doc.metadata.get('source_type')}")
print(f"Metadata: {sample_doc.metadata}")
print(f"Content Preview: {sample_doc.page_content[:200]}...")

# ========== QUALITY CHECKS ==========
def analyze_split_quality(splits: List[Document]) -> dict:
    """Analyze the quality of document splits."""
    chunk_sizes = [len(doc.page_content) for doc in splits]

    return {
        'total_chunks': len(splits),
        'avg_chunk_size': sum(chunk_sizes) / len(chunk_sizes),
        'min_chunk_size': min(chunk_sizes),
        'max_chunk_size': max(chunk_sizes),
        'chunks_too_small': sum(1 for size in chunk_sizes if size < 100),
        'chunks_too_large': sum(1 for size in chunk_sizes if size > 2000),
        'unique_sources': len(set(d.metadata.get('source_type') for d in splits))
    }

quality_metrics = analyze_split_quality(split_documents)
print("\n=== Split Quality Metrics ===")
for metric, value in quality_metrics.items():
    print(f"{metric}: {value}")

# Flag potential issues
if quality_metrics['chunks_too_small'] > len(split_documents) * 0.1:
    print("\n⚠️  WARNING: More than 10% of chunks are very small - consider adjusting chunk_size")

if quality_metrics['chunks_too_large'] > 0:
    print(f"\n⚠️  WARNING: {quality_metrics['chunks_too_large']} chunks exceed 2000 characters")
```

### Why This Example Shows Loader/Splitter Power:

1. **Multi-Source Integration**: Single pipeline handles PDFs, Markdown, web, and APIs
2. **Metadata Enrichment**: Each document carries context about its source and structure
3. **Adaptive Splitting**: Different strategies for different content types (code vs prose vs API docs)
4. **Header Preservation**: Markdown headers become searchable metadata
5. **Quality Monitoring**: Built-in metrics to ensure split quality

## Best Practices for Mastering Document Loaders and Splitters

1. **Choose chunk size based on your retrieval strategy**: For semantic search with embeddings, 500-1000 characters works well. For keyword search or when using small context windows, go smaller (200-500). Always test retrieval accuracy with your actual queries.

2. **Maximize chunk overlap in technical/reference content**: Use 20-25% overlap (200 chars for 1000 char chunks) to ensure concepts that span chunk boundaries are captured. This is especially critical for code, API docs, and step-by-step instructions.

3. **Enrich metadata aggressively during loading**: Add source type, timestamps, authors, categories, and any domain-specific tags. This metadata enables filtered retrieval and helps users assess source credibility. Good metadata is as important as good content.

4. **Use content-aware splitters for mixed documents**: Don't use one splitter for everything. Technical docs need code-aware splitting, markdown needs header preservation, and conversation threads need larger chunks. Build a router that selects the right splitter based on content type.

5. **Always validate split quality with metrics**: Track chunk size distribution, count of tiny/huge chunks, and metadata completeness. Set up automated alerts when quality metrics degrade - this often indicates upstream data issues before they impact retrieval.

## Common Pitfalls to Avoid

- **Don't ignore chunk overlap**: Zero overlap causes retrieval to miss content at boundaries
- **Avoid one-size-fits-all splitting**: Different content types need different strategies
- **Don't lose metadata**: Ensure all splits inherit metadata from parent documents
- **Don't skip quality checks**: Small chunks and metadata gaps kill RAG performance
- **Remember token limits**: Character counts ≠ token counts; use `TokenTextSplitter` for precision
