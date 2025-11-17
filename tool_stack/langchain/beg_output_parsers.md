# Output Parsers - Beginner

## Concept Overview

Output parsers transform raw LLM text outputs into structured data formats (JSON, lists, dates, Pydantic models). They also provide format instructions that can be injected into prompts, ensuring the LLM generates parseable output. This bridges the gap between unstructured LLM responses and the structured data your application needs.

**Why it matters:** Without parsers, you'd need to write brittle regex or string manipulation code for every LLM output. Parsers provide type safety, validation, error handling, and automatic retry logic when outputs don't match the expected schema.

## Real-World Example: Structured Product Review Analysis System

This example demonstrates a production-grade review analysis system that extracts structured insights from unstructured customer reviews.

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import (
    PydanticOutputParser,
    JsonOutputParser,
    StructuredOutputParser,
    CommaSeparatedListOutputParser
)
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum

# Define structured output schema with validation
class SentimentEnum(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

class ProductAspect(BaseModel):
    """Specific aspect of the product mentioned in review."""
    aspect: str = Field(description="Product feature or aspect (e.g., 'battery life', 'camera quality')")
    sentiment: SentimentEnum = Field(description="Sentiment about this specific aspect")
    confidence: float = Field(description="Confidence score 0-1", ge=0.0, le=1.0)
    quote: str = Field(description="Relevant quote from review supporting this assessment")

class ReviewAnalysis(BaseModel):
    """Comprehensive analysis of a product review."""
    overall_sentiment: SentimentEnum = Field(description="Overall sentiment of the review")
    overall_rating: int = Field(description="Inferred rating 1-5 stars", ge=1, le=5)
    aspects: List[ProductAspect] = Field(description="List of product aspects mentioned")
    key_themes: List[str] = Field(description="Main themes or topics in the review")
    is_verified_purchase: bool = Field(description="Whether review mentions verified purchase")
    actionable_feedback: Optional[str] = Field(description="Specific actionable feedback for product team")
    customer_segment: str = Field(description="Likely customer segment (e.g., 'professional photographer', 'casual user')")

    @validator('aspects')
    def validate_aspects(cls, v):
        if len(v) < 1:
            raise ValueError('At least one aspect must be identified')
        return v

# Initialize parser and LLM
parser = PydanticOutputParser(pydantic_object=ReviewAnalysis)
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Create prompt with format instructions
analysis_prompt = ChatPromptTemplate.from_template("""
You are an expert product analyst. Analyze the following product review and extract structured insights.

Review:
{review_text}

Product Category: {product_category}

{format_instructions}

Be thorough and extract all mentioned aspects with specific quotes from the review.
""")

# Build the chain
review_analysis_chain = (
    analysis_prompt.partial(format_instructions=parser.get_format_instructions())
    | llm
    | parser
)

# Test with a real-world review
test_review = """
I've been using this mirrorless camera for 3 months as a professional wedding photographer.
The image quality is absolutely stunning - the colors are vibrant and the low-light performance
is better than my old DSLR. However, the battery life is disappointing; I have to carry
4 batteries to make it through a full wedding day. The autofocus is incredibly fast and accurate,
which is crucial for capturing those quick moments. The menu system is a bit confusing at first,
but once you learn it, it's powerful. For the price point ($2,499), I expected better build quality -
the body feels a bit plasticky. Overall, I'd recommend this to other professionals who don't mind
the battery limitations and are willing to invest time learning the system. Definitely worth it
for the image quality alone. Purchased from authorized dealer.
"""

result = review_analysis_chain.invoke({
    "review_text": test_review,
    "product_category": "Mirrorless Camera"
})

print(f"Overall Sentiment: {result.overall_sentiment}")
print(f"Rating: {result.overall_rating}/5 stars")
print(f"\nCustomer Segment: {result.customer_segment}")
print(f"Verified Purchase: {result.is_verified_purchase}")
print(f"\nKey Themes: {', '.join(result.key_themes)}")

print("\n=== Detailed Aspect Analysis ===")
for aspect in result.aspects:
    print(f"\n{aspect.aspect.upper()} [{aspect.sentiment}] (confidence: {aspect.confidence})")
    print(f"  Quote: \"{aspect.quote}\"")

print(f"\n=== Actionable Feedback ===")
print(result.actionable_feedback)
```

### Advanced Multi-Parser Workflow:

```python
from langchain_core.runnables import RunnableParallel

# Define different parsers for different analysis types
competitive_parser = JsonOutputParser()
keywords_parser = CommaSeparatedListOutputParser()

competitive_prompt = ChatPromptTemplate.from_template("""
Analyze this review for competitive intelligence:
{review_text}

Return JSON with:
- competitor_mentions: list of competitor products mentioned
- comparison_points: what they compared
- switching_likelihood: "high"/"medium"/"low"
""")

keywords_prompt = ChatPromptTemplate.from_template("""
Extract important keywords and phrases from this review that should trigger alerts:
{review_text}

Return as comma-separated list. Include brand names, feature names, and strong sentiment words.
{format_instructions}
""")

# Parallel analysis with different parsers
multi_analysis_chain = RunnableParallel({
    "detailed_analysis": review_analysis_chain,
    "competitive_intel": competitive_prompt | llm | competitive_parser,
    "alert_keywords": (
        keywords_prompt.partial(format_instructions=keywords_parser.get_format_instructions())
        | llm
        | keywords_parser
    )
})

comprehensive_result = multi_analysis_chain.invoke({
    "review_text": test_review,
    "product_category": "Mirrorless Camera"
})

print("\n=== Comprehensive Analysis ===")
print(f"\nPrimary Analysis: {comprehensive_result['detailed_analysis'].overall_sentiment}")
print(f"Competitive Intel: {comprehensive_result['competitive_intel']}")
print(f"Alert Keywords: {comprehensive_result['alert_keywords']}")
```

### Custom Parser for Domain-Specific Needs:

```python
from langchain_core.output_parsers import BaseOutputParser
import re

class PriceExtractorParser(BaseOutputParser):
    """Custom parser to extract and normalize price mentions from reviews."""

    def parse(self, text: str) -> dict:
        # Find price patterns
        price_patterns = [
            r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $1,299.99
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*dollars?',  # 1299 dollars
            r'USD\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # USD 1299
        ]

        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            prices.extend([float(m.replace(',', '')) for m in matches])

        # Find value indicators
        value_positive = bool(re.search(r'\b(worth it|great value|bargain|steal|reasonable price)\b', text, re.IGNORECASE))
        value_negative = bool(re.search(r'\b(overpriced|expensive|not worth|too much|waste of money)\b', text, re.IGNORECASE))

        return {
            "prices_mentioned": prices,
            "average_price": sum(prices) / len(prices) if prices else None,
            "value_perception": "positive" if value_positive else ("negative" if value_negative else "neutral"),
            "price_sensitivity_high": value_negative or len(prices) > 2
        }

    def get_format_instructions(self) -> str:
        return "Mention specific prices with dollar signs or 'USD' prefix. Include your opinion on value/price."

price_parser = PriceExtractorParser()

price_extraction_prompt = ChatPromptTemplate.from_template("""
Discuss the pricing and value of this product based on the review:

Review: {review_text}

{format_instructions}
""")

price_chain = (
    price_extraction_prompt.partial(format_instructions=price_parser.get_format_instructions())
    | llm
    | price_parser
)

price_analysis = price_chain.invoke({"review_text": test_review})
print(f"\nPrice Analysis: {price_analysis}")
```

### Why This Example Shows Output Parser Power:

1. **Type Safety**: Pydantic models catch errors at parse time, not runtime
2. **Validation**: Custom validators ensure data quality (e.g., confidence scores 0-1)
3. **Multiple Formats**: Different parsers for different needs (JSON, lists, custom)
4. **Format Instructions**: Parsers automatically generate prompt instructions for LLMs
5. **Error Handling**: Built-in retry logic when parsing fails

## Best Practices for Mastering Output Parsers

1. **Use PydanticOutputParser for complex schemas**: When you need nested objects, validation, and type safety, Pydantic parsers are the gold standard. They provide automatic retry with error feedback to the LLM and integrate perfectly with type hints.

2. **Add validation to your Pydantic models**: Use Field constraints (`ge`, `le`, `max_length`) and custom validators to ensure data quality. The parser will automatically ask the LLM to retry if validation fails, creating a feedback loop that improves output quality.

3. **Always include format_instructions in your prompts**: Call `parser.get_format_instructions()` and inject it into your prompt template. This tells the LLM exactly how to format its response, dramatically reducing parsing errors.

4. **Create custom parsers for domain-specific formats**: When you need to parse specialized formats (prices, dates, technical specs), extend `BaseOutputParser`. This encapsulates your parsing logic in a reusable component that works seamlessly with LCEL chains.

5. **Use JsonOutputParser for flexible schemas**: When your schema varies or you need maximum flexibility, JsonOutputParser is more forgiving than Pydantic. It's perfect for exploratory work or when the LLM output structure might change based on input.

## Common Pitfalls to Avoid

- **Don't skip format instructions**: Always use `get_format_instructions()` in prompts
- **Avoid overly complex schemas**: Keep nested structures under 3-4 levels deep
- **Don't ignore validation errors**: Log parser failures to improve prompts over time
- **Remember streaming limitations**: Some parsers don't support streaming; use `JsonOutputParser` or `StrOutputParser` if you need streaming
- **Test with real LLM output**: Don't assume the LLM will always follow the schema perfectly
