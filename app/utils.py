from datetime import datetime
from app.processor import TextCleaner, DuplicateRemover, SentimentAnalyzer, KeywordExtractor, CategoryClassifier, GeolocationProcessor


def process_article(article: dict) -> dict:
    """
    Process a single article with all NLP pipelines.
    :param article: Raw article dictionary
    :return: Processed article with sentiment, keywords, category
    """
    cleaned_text = TextCleaner.normalize_text(article.get("description", ""))
    
    sentiment = SentimentAnalyzer().analyze_sentiment(
        f"{article.get('title', '')} {article.get('description', '')}"
    )
    
    sentiment["title"] = article.get("title", "")
    sentiment["source"] = article.get("source", {}).get("name", "Unknown")
    
    keywords = KeywordExtractor.extract_keywords(
        f"{article.get('title', '')} {article.get('description', '')}",
        top_n=5
    )
    
    category = CategoryClassifier.classify_category(article)
    
    processed = article.copy()
    processed["sentiment"] = sentiment
    processed["keywords"] = keywords
    processed["category"] = category
    processed["cleaned_description"] = cleaned_text
    
    processed = GeolocationProcessor.add_geolocation(processed)
    
    return processed


def process_articles_batch(articles: list) -> list:
    """
    Process a batch of articles.
    :param articles: List of raw article dictionaries
    :return: List of processed article dictionaries
    """
    return [process_article(article) for article in articles]


def get_formatted_date(date_str: str) -> str:
    """
    Format ISO date string for display.
    :param date_str: ISO date string
    :return: Formatted date string
    """
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return date_str


def parse_date(date_str: str) -> datetime:
    """
    Parse various date formats to datetime.
    :param date_str: Date string
    :return: datetime object
    """
    formats = [
        "%Y-%m-%dT%H:%M:%S.%f%Z",
        "%Y-%m-%dT%H:%M:%S%Z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.replace('Z', ''), fmt)
        except:
            continue
    
    return datetime.now()
