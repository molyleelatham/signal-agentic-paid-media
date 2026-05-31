# Tavily Research for Gymshark

## Overview

The Tavily Research service performs comprehensive web research for Gymshark media planning. It scrapes multiple sources to gather data for Reddit discussions, SEO keywords, Google bidding keywords, Thrad BERT inputs, and content ideas.

## Features

### 1. Reddit Scraping
Scrapes Reddit for Gymshark-related discussions from fitness subreddits:
- r/fitness
- r/bodyweight
- r/Gymshark
- Custom subreddits

Extracts:
- Post titles and content
- Upvotes and comments
- Keywords and sentiment
- Relevance scores

### 2. SEO Page Scraping
Scrapes SEO authority sites for keyword research:
- Moz.com
- Ahrefs.com
- Semrush.com
- SearchEngineLand.com

Extracts:
- SEO keywords
- Search intent (informational, transactional, navigational)
- Keyword difficulty estimates
- Confidence scores

### 3. Google Keyword Extraction
Extracts Google keywords for bidding from research data:
- Biddable keywords from Reddit and SEO data
- Match type suggestions (broad, phrase, exact)
- Bid suggestions in GBP
- Competition assessment
- Relevance to Gymshark
- Search intent classification

### 4. Thrad BERT Input Generation
Generates inputs for Thrad BERT classification:
- Query and category (H/G/A for High/Growth/Awareness)
- Confidence scores
- Source attribution
- Context information

### 5. Content Idea Generation
Generates content ideas from research findings:
- Topics and angles
- Target audience
- Platform recommendations
- Content type (video, image, carousel, text)
- Relevant keywords
- Opportunity scores

## API Endpoints

### Comprehensive Research
```bash
POST /api/v1/intelligence/gymshark-research
```

Performs all research in one call:
- Reddit scraping
- SEO keyword extraction
- Google keyword generation
- Thrad input generation
- Content idea generation

**Parameters:**
- `query`: Research query (default: "Gymshark fitness apparel")
- `max_results`: Max results per source (default: 10)
- `time_range`: Time range (day, week, month, year, default: month)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/intelligence/gymshark-research?query=Gymshark%20fitness&max_results=5&time_range=month"
```

### Reddit Scraping
```bash
GET /api/v1/intelligence/gymshark-reddit
```

Scrapes Reddit for Gymshark discussions.

**Parameters:**
- `query`: Search query (default: "Gymshark")
- `max_results`: Max results (default: 10)
- `time_range`: Time range (default: "month")

### SEO Keywords
```bash
GET /api/v1/intelligence/gymshark-seo-keywords
```

Scrapes SEO pages for keywords.

**Parameters:**
- `query`: Search query (default: "Gymshark fitness")
- `max_results`: Max results (default: 10)
- `time_range`: Time range (default: "month")

### Google Keywords
```bash
GET /api/v1/intelligence/gymshark-google-keywords
```

Extracts Google keywords for bidding.

**Parameters:**
- `query`: Search query (default: "Gymshark fitness")
- `max_results`: Max results (default: 10)

### Thrad Inputs
```bash
GET /api/v1/intelligence/gymshark-thrad-inputs
```

Generates Thrad BERT inputs.

**Parameters:**
- `query`: Search query (default: "Gymshark fitness")
- `max_results`: Max results (default: 10)

### Content Ideas
```bash
GET /api/v1/intelligence/gymshark-content-ideas
```

Generates content ideas from research.

**Parameters:**
- `query`: Search query (default: "Gymshark fitness")
- `max_results`: Max results (default: 10)

## Configuration

### Required Environment Variable
```bash
TAVILY_API_KEY=tvly-your-key-here
```

### Install Dependencies
```bash
pip install tavily-python
```

## Usage Examples

### Example 1: Comprehensive Research
```python
from services.intelligence.tavily_research import GymsharkTavilyResearch

research_service = GymsharkTavilyResearch(tavily_api_key="your-key")

result = research_service.perform_comprehensive_research(
    base_query="Gymshark fitness apparel",
    max_results_per_source=10,
    time_range="month"
)

print(f"Reddit posts: {len(result.reddit_posts)}")
print(f"SEO keywords: {len(result.seo_keywords)}")
print(f"Google keywords: {len(result.google_keywords)}")
print(f"Thrad inputs: {len(result.thrad_inputs)}")
print(f"Content ideas: {len(result.content_ideas)}")
```

### Example 2: Reddit Scraping Only
```python
reddit_posts = research_service.scrape_reddit(
    query="Gymshark leggings",
    max_results=10,
    subreddits=["fitness", "Gymshark"]
)

for post in reddit_posts:
    print(f"r/{post.subreddit}: {post.title}")
    print(f"Score: {post.score}, Keywords: {post.keywords}")
```

### Example 3: Google Keywords for Bidding
```python
google_keywords = research_service.extract_google_keywords(
    research_data=reddit_posts,
    seo_keywords=seo_keywords,
    max_keywords=20
)

for kw in google_keywords:
    print(f"{kw.keyword} - {kw.match_type} - £{kw.bid_suggestion}")
```

### Example 4: Thrad BERT Inputs
```python
thrad_inputs = research_service.generate_thrad_inputs(
    research_data=reddit_posts,
    google_keywords=google_keywords
)

for inp in thrad_inputs:
    print(f"{inp.query} - Category: {inp.category} - Confidence: {inp.confidence}")
```

### Example 5: Content Ideas
```python
content_ideas = research_service.generate_content_ideas(
    research_data=reddit_posts,
    seo_keywords=seo_keywords,
    google_keywords=google_keywords
)

for idea in content_ideas:
    print(f"{idea.topic} for {idea.platform} ({idea.content_type})")
    print(f"Score: {idea.opportunity_score}")
```

## Data Models

### RedditPost
```python
@dataclass
class RedditPost:
    subreddit: str
    title: str
    author: str
    score: int
    comments_count: int
    url: str
    content: str
    keywords: List[str]
    sentiment: str
    relevance_score: float
```

### SEOKeyword
```python
@dataclass
class SEOKeyword:
    keyword: str
    search_volume: Optional[int]
    difficulty: Optional[float]
    intent: str  # informational, transactional, navigational
    source: str
    confidence: float
```

### GoogleKeyword
```python
@dataclass
class GoogleKeyword:
    keyword: str
    match_type: str  # broad, phrase, exact
    bid_suggestion: float
    competition: str  # low, medium, high
    relevance_to_gymshark: float
    search_intent: str
```

### ThradInput
```python
@dataclass
class ThradInput:
    query: str
    category: str  # H, G, A (High intent, Growth, Awareness)
    confidence: float
    source: str
    context: str
```

### ContentIdea
```python
@dataclass
class ContentIdea:
    topic: str
    angle: str
    target_audience: str
    platform: str
    content_type: str  # video, image, carousel, text
    keywords: List[str]
    reasoning: str
    opportunity_score: float
```

## Testing

Run the test script:
```bash
python3 scripts/test_tavily_research.py
```

Or use the Makefile:
```bash
make test-tavily-research
```

## Integration with Media Planning

This research service integrates with the media planning flow:

1. **Planning Phase**: Use research to inform strategy
   - Reddit discussions → Audience insights
   - SEO keywords → Content strategy
   - Google keywords → Bidding strategy

2. **Content Generation**: Use content ideas
   - Topics and angles → Creative briefs
   - Platform recommendations → Channel strategy
   - Keywords → SEO optimization

3. **Thrad Integration**: Use Thrad inputs
   - BERT classification → Keyword categorization
   - H/G/A categories → Funnel stage targeting
   - Confidence scores → Prioritization

## Media Planning Workflow

```python
# 1. Perform research
research = research_service.perform_comprehensive_research(
    base_query="Gymshark summer campaign"
)

# 2. Extract Google keywords for bidding
google_keywords = research.google_keywords
# Use these in media buying service

# 3. Generate content ideas
content_ideas = research.content_ideas
# Use these in content brief agent

# 4. Generate Thrad inputs for BERT
thrad_inputs = research.thrad_inputs
# Use these in Thrad BERT classifier
```

## Best Practices

1. **Time Range**: Use "week" for trending topics, "month" for stable insights
2. **Max Results**: 5-10 for quick tests, 15-20 for comprehensive research
3. **Query Specificity**: More specific queries yield better results
4. **Subreddit Selection**: Customize subreddits for your target audience
5. **Keyword Filtering**: Review and filter keywords before bidding

## Troubleshooting

### Error: TAVILY_API_KEY not configured
**Solution**: Set TAVILY_API_KEY in .env.local

### Error: Tavily not available
**Solution**: Install with `pip install tavily-python`

### No Reddit posts found
**Solution**: Check query and try broader terms or different subreddits

### No SEO keywords extracted
**Solution**: SEO pages may not have keyword data in expected format

### Low opportunity scores
**Solution**: Increase max_results or use different time range

## Future Enhancements

- Database persistence for research results
- Scheduled research automation
- Multi-language support
- Competitor comparison
- Trend analysis over time
- Integration with Google Ads API for real keyword data
- Image content analysis from Reddit posts
- Sentiment analysis with ML models