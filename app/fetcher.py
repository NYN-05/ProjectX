import requests
import feedparser
import logging
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 2
MAX_RSS_WORKERS = 10


class NewsFetcher:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.NEWS_API_KEY
        self.base_url = settings.NEWS_API_URL
        self.session = requests.Session()
        if self.api_key and self.api_key != "demo_key":
            self.session.headers.update({
                "X-Api-Key": self.api_key
            })

    def _fetch_single_rss(self, source_name: str, url: str) -> tuple:
        """Fetch a single RSS feed, returns (source_name, list of articles, error)."""
        try:
            logger.info(f"Fetching RSS from {source_name}...")
            feed = feedparser.parse(url)

            if feed.get('bozo', 0) == 1:
                logger.warning(f"Malformed RSS from {source_name}: {feed.get('bozo_exception')}")

            articles = []
            for entry in feed.entries:
                article = {
                    "title": entry.get("title", "")[:500],
                    "description": entry.get("summary", "") or entry.get("description", "")[:1000],
                    "url": entry.get("link", "")[:500],
                    "urlToImage": self._extract_rss_image(entry),
                    "publishedAt": self._format_rss_date(entry),
                    "source": {"name": source_name[:100]},
                    "author": entry.get("author", "")[:100] if entry.get("author") else None,
                    "content": entry.get("content", [{"value": ""}])[0]["value"][:2000] if "content" in entry else ""
                }
                articles.append(article)
            return (source_name, articles, None)
        except Exception as e:
            logger.error(f"Failed to fetch RSS from {source_name}: {e}")
            return (source_name, [], str(e))

    def fetch_rss_feeds(self) -> list:
        """
        Fetch news from RSS feeds in parallel using ThreadPoolExecutor.
        :return: List of news articles
        """
        all_rss_articles = []
        failed_feeds = []

        with ThreadPoolExecutor(max_workers=MAX_RSS_WORKERS) as executor:
            futures = {
                executor.submit(self._fetch_single_rss, name, url): name
                for name, url in settings.RSS_FEEDS.items()
            }
            for future in as_completed(futures):
                source_name, articles, err in future.result()
                all_rss_articles.extend(articles)
                if err:
                    failed_feeds.append({"source": source_name, "error": err})

        if failed_feeds:
            logger.info(f"RSS fetch completed with {len(failed_feeds)} failures")

        return all_rss_articles

    def _extract_rss_image(self, entry) -> str:
        """Extract image URL from RSS entry if available."""
        try:
            if "media_content" in entry and len(entry.media_content) > 0:
                return entry.media_content[0].get("url", "")
            if "links" in entry:
                for link in entry.links:
                    if link.get("rel") == "enclosure" and "image" in link.get("type", ""):
                        return link.get("href", "")
        except Exception as e:
            logger.debug(f"Image extraction error: {e}")
        return ""

    def _format_rss_date(self, entry) -> str:
        """Format RSS date to ISO format with fallback handling."""
        try:
            if "published_parsed" in entry:
                dt = time.mktime(entry.published_parsed)
                return datetime.fromtimestamp(dt).isoformat()
            if "updated_parsed" in entry:
                dt = time.mktime(entry.updated_parsed)
                return datetime.fromtimestamp(dt).isoformat()
        except Exception:
            pass
        return ""

    def fetch_news(self, country: str = "us", language: str = "en", page: int = 1, category: str = None) -> list:
        """
        Fetch latest news from NewsAPI with proper error handling.
        :param country: Country code (e.g., 'us', 'in', 'gb')
        :param language: Language code (e.g., 'en', 'es', 'fr')
        :param page: Page number for pagination
        :param category: Optional category filter
        :return: List of news articles
        """
        if page < 1:
            page = 1

        try:
            params = {
                "country": country,
                "language": language,
                "page": page
            }
            if category:
                params["category"] = category
                params["sortBy"] = "category"

            for attempt in range(MAX_RETRIES):
                try:
                    response = self.session.get(self.base_url, params=params, timeout=15)
                    response.raise_for_status()
                    data = response.json()
                    break
                except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
                    if attempt == MAX_RETRIES - 1:
                        raise
                    logger.warning(f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                    time.sleep(RETRY_DELAY)

            if data.get("status") == "ok":
                articles = data.get("articles", [])
                return self._extract_articles(articles)
            else:
                logger.warning(f"NewsAPI returned status: {data.get('status')}")
                return []
        except requests.exceptions.Timeout:
            logger.error("NewsAPI request timed out")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
            return []
        except ValueError as e:
            logger.error(f"JSON parsing error: {e}")
            return []

    def fetch_by_category(self, category: str, country: str = "us", language: str = "en", page: int = 1) -> list:
        """
        Fetch news by category with proper pagination.
        :param category: Category name
        :param country: Country code
        :param language: Language code
        :param page: Page number
        :return: List of news articles
        """
        return self.fetch_news(country=country, language=language, page=page, category=category)

    def _extract_articles(self, articles: list) -> list:
        """
        Extract relevant fields from NewsAPI response with validation.
        :param articles: List of article objects from API
        :return: Cleaned list of articles
        """
        extracted = []
        for article in articles:
            try:
                source_name = article.get("source", {}).get("name", "Unknown")
                description = article.get("description", "")

                if not article.get("title"):
                    continue

                extracted_article = {
                    "title": article.get("title", "")[:500],
                    "description": description[:1000] if description else "No description available.",
                    "url": article.get("url", "")[:500],
                    "urlToImage": article.get("urlToImage", ""),
                    "publishedAt": article.get("publishedAt", ""),
                    "source": {"name": str(source_name)[:100]},
                    "author": article.get("author", "")[:100] if article.get("author") else None,
                    "content": article.get("content", "")[:2000]
                }
                extracted.append(extracted_article)
            except Exception as e:
                logger.debug(f"Error extracting article: {e}")
                continue
        return extracted

    def get_top_headlines(self, country: str = "us", language: str = "en", category: str = None) -> list:
        """
        Get top headlines with optional category filter.
        """
        return self.fetch_news(country, language, page=1, category=category)

    def get_everything(self, q: str, from_param: str = None, to: str = None,
                       lang: str = "en", sortBy: str = "relevancy", page: int = 1) -> list:
        """
        Search for news articles with comprehensive error handling.
        """
        if page < 1:
            page = 1

        try:
            params = {
                "q": q[:100],
                "language": lang,
                "sortBy": sortBy,
                "page": page
            }
            if from_param:
                params["from"] = from_param
            if to:
                params["to"] = to

            everything_url = "https://newsapi.org/v2/everything"

            for attempt in range(MAX_RETRIES):
                try:
                    response = self.session.get(everything_url, params=params, timeout=15)
                    response.raise_for_status()
                    data = response.json()
                    break
                except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
                    if attempt == MAX_RETRIES - 1:
                        raise
                    logger.warning(f"Everything search failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                    time.sleep(RETRY_DELAY)

            if data.get("status") == "ok":
                articles = data.get("articles", [])
                return self._extract_articles(articles)
            else:
                logger.warning(f"Everything search failed: {data.get('status')}")
                return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Everything search API request failed: {e}")
            return []
        except ValueError as e:
            logger.error(f"JSON parsing error in search: {e}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Everything search API request failed: {e}")
            return []
        except ValueError as e:
            logger.error(f"JSON parsing error in search: {e}")
            return []
