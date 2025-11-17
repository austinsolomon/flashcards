# LCEL (LangChain Expression Language) - Beginner

## Concept Overview

LCEL is LangChain's declarative way to compose chains using the `|` operator. Instead of manually managing input/output between components, LCEL allows you to pipe components together in a readable, functional style. This is the foundation of modern LangChain development and replaces older imperative chain patterns.

**Why it matters:** LCEL chains are automatically optimized for streaming, parallelization, and async execution. They provide built-in support for batching, fallbacks, and retries without additional code.

## Real-World Example: Intelligent Document Q&A with Citations

This example demonstrates a production-ready Q&A system that not only answers questions but also provides source citations and confidence scores.

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from operator import itemgetter

# Initialize components
llm = ChatOpenAI(model="gpt-4", temperature=0)
vectorstore = Chroma.from_texts(
    texts=[
        "The company's Q4 revenue was $45.2M, a 23% increase YoY.",
        "Customer acquisition cost decreased from $127 to $98 per user.",
        "Our largest market segment is enterprise SaaS at 67% of revenue.",
        "Annual recurring revenue (ARR) reached $180M in 2024.",
    ],
    embedding=OpenAIEmbeddings()
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Define prompt templates
context_prompt = ChatPromptTemplate.from_template("""
You are a financial analyst. Use the following context to answer the question.
Provide specific numbers and cite which pieces of context you used.

Context:
{context}

Question: {question}

Answer with citations:
""")

confidence_prompt = ChatPromptTemplate.from_template("""
Based on this answer: {answer}

Rate the confidence level (high/medium/low) and explain why:
""")

# Build LCEL chain with parallel processing
def format_docs(docs):
    return "\n\n".join([f"[{i+1}] {doc.page_content}" for i, doc in enumerate(docs)])

# Main chain with parallel branches
chain = (
    # Step 1: Retrieve context and pass through the question
    RunnableParallel({
        "context": itemgetter("question") | retriever | format_docs,
        "question": itemgetter("question")
    })
    # Step 2: Generate answer
    | RunnableParallel({
        "answer": context_prompt | llm | StrOutputParser(),
        "context": itemgetter("context")
    })
    # Step 3: Add confidence assessment in parallel with passing through answer
    | RunnableParallel({
        "answer": itemgetter("answer"),
        "confidence": confidence_prompt | llm | StrOutputParser(),
        "sources": itemgetter("context")
    })
)

# Execute the chain
result = chain.invoke({
    "question": "What was our customer acquisition cost improvement?"
})

print(f"Answer: {result['answer']}\n")
print(f"Confidence: {result['confidence']}\n")
print(f"Sources:\n{result['sources']}")
```

### Why This Example Shows LCEL's Power:

1. **Automatic Parallelization**: The `RunnableParallel` executes independent branches simultaneously
2. **Clean Data Flow**: Each `|` operator clearly shows how data transforms through the pipeline
3. **Composability**: Easy to add new branches (e.g., sentiment analysis, fact-checking) without restructuring
4. **Type Safety**: The chain validates input/output schemas at each step
5. **Built-in Features**: Supports `.stream()`, `.batch()`, and `.ainvoke()` without code changes

### Streaming Example:

```python
# Same chain, but streaming the answer as it's generated
for chunk in chain.stream({"question": "What is our ARR?"}):
    if "answer" in chunk:
        print(chunk["answer"], end="", flush=True)
```

## Best Practices for Mastering LCEL

1. **Use RunnableParallel for independent operations**: Whenever you have operations that don't depend on each other (e.g., fetching different data sources, generating multiple outputs), wrap them in `RunnableParallel` to execute them concurrently and reduce latency.

2. **Leverage itemgetter for clean data routing**: Instead of writing lambda functions, use `operator.itemgetter` to extract specific keys from dictionaries. It's more readable and works seamlessly with LCEL's type checking.

3. **Keep chains focused and composable**: Build small, reusable chain components rather than monolithic chains. Use `|` to compose them. This makes testing, debugging, and maintenance much easier.

4. **Use RunnablePassthrough for side effects**: When you need to log, cache, or inspect data mid-chain without transforming it, use `RunnablePassthrough` with assignment to add data without breaking the flow.

5. **Design for streaming from the start**: Even if you don't need streaming initially, structure chains to support it. Use output parsers that work with streaming (like `StrOutputParser`), and avoid operations that require the full output before processing.

## Common Pitfalls to Avoid

- **Don't mix LCEL with legacy chains**: Stick to LCEL patterns; mixing with older `LLMChain` or `SequentialChain` loses LCEL benefits
- **Avoid heavy processing in lambdas**: Keep lambda functions light; move complex logic to dedicated Runnables
- **Don't ignore error handling**: Use `RunnableWithFallbacks` to add retry logic and backup models
- **Remember async support**: Use `.ainvoke()` and `.astream()` in async contexts for better performance
