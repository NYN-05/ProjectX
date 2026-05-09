import re
from datetime import datetime
from textblob import TextBlob
from app.config import settings
from app.services.geolocation_service import geolocation_processor as GeoProcessor


class TextCleaner:
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean raw text by removing noise and normalizing.
        :param text: Raw text to clean
        :return: Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters except common punctuation
        text = re.sub(r'[^\w\s.,!?;:\'\"\-\(\)]', '', text)
        
        # Strip leading/trailing whitespace
        return text.strip()

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for processing.
        :param text: Text to normalize
        :return: Normalized lowercase text
        """
        cleaned = TextCleaner.clean_text(text)
        return cleaned.lower()


class DuplicateRemover:
    @staticmethod
    def deduplicate_articles(articles: list, threshold: float = 0.85) -> list:
        """
        Remove duplicate articles based on title similarity.
        :param articles: List of article dictionaries
        :param threshold: Similarity threshold (0.0 to 1.0)
        :return: Deduplicated list
        """
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            title = article.get("title", "")
            url = article.get("url", "")
            
            # Keep if both title AND URL are new (not duplicates)
            if title not in seen_titles and url not in seen_titles:
                unique_articles.append(article)
                seen_titles.add(title)
                seen_titles.add(url)
        
        return unique_articles


class SentimentAnalyzer:
    def analyze_sentiment(self, text: str) -> dict:
        """
        Analyze sentiment using TextBlob.
        :param text: Text to analyze
        :return: Dictionary with polarity, subjectivity, and score
        """
        if not text:
            return {"polarity": 0.0, "subjectivity": 0.0, "score": "neutral"}
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            if polarity > 0.1:
                score = "positive"
            elif polarity < -0.1:
                score = "negative"
            else:
                score = "neutral"
            
            return {
                "polarity": polarity,
                "subjectivity": subjectivity,
                "score": score,
                "confidence": round(abs(polarity) * 0.5 + 0.5, 2)
            }
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return {"polarity": 0.0, "subjectivity": 0.0, "score": "neutral", "confidence": 0.5}

    def get_sentiment_score(self, article: dict) -> dict:
        """
        Get sentiment for an article.
        :param article: Article dictionary
        :return: Sentiment analysis result
        """
        description = article.get("description", "")
        content = article.get("content", "")
        title = article.get("title", "")
        full_text = f"{title} {description} {content}".strip()
        return self.analyze_sentiment(full_text)


class KeywordExtractor:
    @staticmethod
    def extract_keywords(text: str, top_n: int = 5) -> list:
        """
        Extract top keywords from text.
        :param text: Text to analyze
        :param top_n: Number of keywords to extract
        :return: List of keywords
        """
        if not text:
            return []
        
        # Tokenize and normalize
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter short words and common stopwords
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                     'could', 'should', 'may', 'might', 'must'}
        
        filtered_words = [word for word in words if len(word) > 3 and word not in stopwords]
        
        # Count frequencies
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return [word for word, _ in top_keywords]


class CategoryClassifier:
    @staticmethod
    def classify_category(article: dict) -> str:
        """
        Classify article into a category based on keywords.
        :param article: Article dictionary
        :return: Category name
        """
        text = f"{article.get('title', '')} {article.get('description', '')}"
        
        category_keywords = {
            "business": ["stock", "market", "finance", "trade", "economy", "company", 
                        "investment", "bank", "money", "revenue", "profit", "business"],
            "technology": ["tech", "software", "ai", "artificial intelligence", "computer",
                          "digital", "internet", "app", "mobile", "coding", "developer",
                          "cybersecurity", "cloud", "data", "algorithm"],
            "health": ["health", "medical", "hospital", "doctor", "treatment", "disease",
                      "medicine", "patient", "wellness", "therapy", "vaccine"],
            "sports": ["sports", "team", "athlete", "game", "score", "match", "championship",
                      "football", "basketball", "soccer", "tennis", "olympics"],
            "entertainment": ["movie", "movie", "celebrity", "actor", "entertainment",
                             "music", "concert", "television", "award", "show"],
            "science": ["science", "research", "experiment", "discovery", "universe",
                       "physics", "chemistry", "biology", "space", "astronomy"],
            "politics": ["politics", "government", "election", "policy", "president",
                        "parliament", "senate", "congress", "minister", "law"],
            "crime": ["crime", "police", "arrest", "court", "trial", "murder", "robbery"]
        }
        
        text_lower = text.lower()
        best_category = "general"
        best_score = 0
        
        for category, keywords in category_keywords.items():
            category_score = sum(1 for keyword in keywords if keyword in text_lower)
            if category_score > best_score:
                best_score = category_score
                best_category = category
        
        return best_category


class GeolocationProcessor:
    @staticmethod
    def add_geolocation(article: dict) -> dict:
        """Add geolocation metadata to an article."""
        return GeoProcessor.process_article(article)
