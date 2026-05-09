import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "demo_key")
    NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "news_db")
    MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "news")
    CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "news.json")
    SCHEDULE_INTERVAL = int(os.getenv("SCHEDULE_INTERVAL", "3600"))
    ARTICLE_RETENTION_DAYS = int(os.getenv("ARTICLE_RETENTION_DAYS", "30"))
    ALLOWED_ORIGINS = [h.strip() for h in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")]

    RSS_FEEDS = {
    # Global News
    "BBC News": "https://feeds.bbci.co.uk/news/rss.xml",

    "CNN": "http://rss.cnn.com/rss/edition.rss",

    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",

    "NY Times": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",

    "The Guardian": "https://www.theguardian.com/world/rss",

    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",

    "ABC News": "https://abcnews.go.com/abcnews/topstories",

    "Fox News": "https://moxie.foxnews.com/google-publisher/latest.xml",

    "WSJ": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",

    "Reuters": "https://feeds.reuters.com/reuters/topNews",


    # India News
    "NDTV": "https://feeds.feedburner.com/ndtvnews-top-stories",

    "The Times of India": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",

    "India Today": "https://www.indiatoday.in/rss",

    "The Hindu": "https://www.thehindu.com/news/national/feeder/default.rss",

    "The Indian Express": "https://indianexpress.com/feed/",

    "Hindustan Times": "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",

    "Zee News": "https://zeenews.india.com/rss/india-national-news.xml",

    "The Print": "https://theprint.in/feed/",

    "News18": "https://www.news18.com/commonfeeds/v1/eng/rss/india.xml",

    "Business Standard": "https://www.business-standard.com/rss/home_page_top_stories.rss"
}
settings = Settings()
