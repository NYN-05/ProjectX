from pymongo import MongoClient, errors, TEXT
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne
from datetime import datetime, timedelta
import json
import logging
import os
import threading
from app.config import settings

logger = logging.getLogger(__name__)

ARTICLE_RETENTION_DAYS = int(os.getenv("ARTICLE_RETENTION_DAYS", "30"))
_json_lock = threading.Lock()


class DatabaseHandler:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.json_file = settings.CACHE_DIR
        self._connected = False

    def connect(self) -> bool:
        """
        Connect to MongoDB with text index for search.
        Returns True if connected, False otherwise.
        """
        os.makedirs(os.path.dirname(self.json_file), exist_ok=True)

        try:
            self.client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[settings.MONGODB_DATABASE]
            self.collection = self.db[settings.MONGODB_COLLECTION]

            # Create text index for search
            try:
                self.collection.create_index([("title", TEXT), ("description", TEXT), ("content", TEXT)], name="text_index")
                logger.info("Text index created for search")
            except Exception as e:
                logger.debug(f"Text index already exists or error: {e}")

            # Create other useful indexes
            try:
                self.collection.create_index("url", unique=True, background=True)
                self.collection.create_index("category", background=True)
                self.collection.create_index("publishedAt", background=True)
                self.collection.create_index("country_code", background=True)
                self.collection.create_index([("country_code", 1), ("publishedAt", -1)], background=True)
                logger.info("Database indexes created")
            except Exception as e:
                logger.debug(f"Index creation warning: {e}")

            # Create TTL index for automatic article cleanup
            try:
                self.collection.create_index(
                    "publishedAt",
                    expireAfterSeconds=ARTICLE_RETENTION_DAYS * 86400,
                    background=True,
                    name="article_ttl"
                )
                logger.info(f"TTL index set: articles expire after {ARTICLE_RETENTION_DAYS} days")
            except Exception as e:
                logger.debug(f"TTL index creation warning: {e}")

            logger.info(f"Successfully connected to MongoDB: {settings.MONGODB_URI}")
            logger.info(f"Database: {settings.MONGODB_DATABASE}, Collection: {settings.MONGODB_COLLECTION}")
            self._connected = True
            return True
        except Exception as e:
            logger.warning(f"MongoDB connection failed: {e}")
            logger.info(f"Falling back to JSON storage: {self.json_file}")
            self.client = None
            self.collection = None
            self._connected = False
            return False

    def is_connected(self) -> bool:
        """Check if MongoDB connection is established."""
        if self.client is not None and self._connected:
            try:
                self.client.admin.command('ping')
                return True
            except Exception:
                self._connected = False
        return False

    def store_article(self, article: dict) -> bool:
        """
        Store a single article in MongoDB or JSON fallback.
        :param article: Article dictionary
        :return: True if stored successfully
        """
        if self.collection is not None and self.is_connected():
            try:
                result = self.collection.update_one(
                    {"url": article.get("url", "")},
                    {"$set": article},
                    upsert=True
                )
                return True
            except Exception as e:
                logger.error(f"MongoDB store error: {e}")
                self._store_json(article)
                return True
        else:
            self._store_json(article)
            return True

    def store_articles_batch(self, articles: list) -> int:
        """
        Store multiple articles with bulk write and duplicate detection.
        :param articles: List of article dictionaries
        :return: Number of articles stored
        """
        if not articles:
            return 0

        if self.collection is not None and self.is_connected():
            try:
                operations = []
                seen_keys = set()
                for article in articles:
                    url = article.get("url", "")
                    pub_date = article.get("publishedAt", "")[:10]
                    unique_key = f"{url}|{pub_date}"
                    if url and unique_key not in seen_keys:
                        operations.append(
                            UpdateOne(
                                {"url": url, "publishedAt": {"$regex": f"^{pub_date}"}},
                                {"$set": article},
                                upsert=True
                            )
                        )
                        seen_keys.add(unique_key)

                if operations:
                    result = self.collection.bulk_write(operations, ordered=False)
                    count = result.upserted_count + result.modified_count
                    logger.info(f"Bulk wrote {count} articles")
                    return count
                return 0
            except BulkWriteError as e:
                logger.warning(f"Some writes failed: {e.details}")
                return e.details.get("nUpserted", 0) + e.details.get("nModified", 0)
            except Exception as e:
                logger.error(f"Bulk write error: {e}")
                for article in articles:
                    self.store_article(article)
                return len(articles)
        else:
            for article in articles:
                self._store_json(article)
            return len(articles)

    def get_all_articles(self, limit: int = 50, sort_by: str = "-publishedAt", skip: int = 0,
                         category: str = None, from_date: str = None, to_date: str = None) -> list:
        """
        Retrieve articles with filtering and pagination support.
        :param limit: Maximum number of articles
        :param sort_by: Sort field
        :param skip: Number of articles to skip
        :param category: Optional category filter
        :param from_date: Start date filter (ISO format)
        :param to_date: End date filter (ISO format)
        :return: List of articles
        """
        query = {}

        if category:
            query["category"] = category

        if from_date or to_date:
            query["publishedAt"] = {}
            if from_date:
                query["publishedAt"]["$gte"] = from_date
            if to_date:
                query["publishedAt"]["$lte"] = to_date

        articles = []

        if self.collection is not None and self.is_connected():
            try:
                sort_field = sort_by.lstrip("-")
                sort_order = -1 if sort_by.startswith("-") else 1

                cursor = self.collection.find(query).sort(sort_field, sort_order).skip(skip).limit(limit)
                for doc in cursor:
                    doc["_id"] = str(doc["_id"])
                    articles.append(doc)
            except Exception as e:
                logger.error(f"MongoDB fetch error: {e}")
                articles = self._read_json()
        else:
            articles = self._read_json()

        return articles

    def _read_json(self) -> list:
        """Read articles from JSON file with error handling."""
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            return []
        except Exception as e:
            logger.error(f"JSON read error: {e}")
            return []

    def _store_json(self, article: dict):
        """Write article to JSON file with thread-level locking (safe for same-process threads)."""
        with _json_lock:
            try:
                articles = self._read_json()
                url = article.get("url", "")
                pub_date = article.get("publishedAt", "")[:10]
                
                should_add = True
                for a in articles:
                    if a.get("url") == url:
                        a_pub = a.get("publishedAt", "")[:10]
                        if a_pub == pub_date:
                            should_add = False
                            break
                        else:
                            a.update(article)
                            should_add = False
                            break
                
                if should_add:
                    articles.append(article)
                
                with open(self.json_file, 'w', encoding='utf-8') as f:
                    json.dump(articles, f, indent=2, default=str)
            except Exception as e:
                logger.error(f"JSON write error: {e}")

    def search_articles(self, query: str, limit: int = 50, skip: int = 0) -> list:
        """
        Search articles by keyword with text index support.
        :param query: Search query string
        :param limit: Maximum results
        :param skip: Number of results to skip
        :return: List of matching articles
        """
        if not query or len(query.strip()) < 1:
            return []

        articles = []

        if self.collection is not None and self.is_connected():
            try:
                search_query = {"$text": {"$search": query[:100]}}
                cursor = self.collection.find(search_query).skip(skip).limit(limit)
                for doc in cursor:
                    doc["_id"] = str(doc["_id"])
                    articles.append(doc)
                logger.info(f"Search found {len(articles)} results for '{query}'")
            except Exception as e:
                logger.error(f"MongoDB search error: {e}")

        if not articles:
            # Fallback to JSON search
            articles = self._read_json()
            query_lower = query.lower()
            articles = [a for a in articles if query_lower in a.get("title", "").lower()
                       or query_lower in a.get("description", "").lower()]

        return articles[:limit]

    def get_by_category(self, category: str, limit: int = 50, skip: int = 0) -> list:
        """
        Get articles by category with pagination.
        :param category: Category name
        :param limit: Maximum results
        :param skip: Number of results to skip
        :return: List of articles
        """
        return self.get_all_articles(limit=limit, skip=skip, category=category)

    def get_recent_articles(self, days: int = 7, limit: int = 50) -> list:
        """
        Get articles from the last N days.
        :param days: Number of days
        :param limit: Maximum results
        :return: List of articles
        """
        if self.collection is not None and self.is_connected():
            cutoff = datetime.now() - timedelta(days=days)
            return self.get_all_articles(limit=limit, from_date=cutoff.isoformat())
        else:
            articles = self.get_all_articles(limit=limit)
            cutoff = datetime.now() - timedelta(days=days)
            return [a for a in articles
                    if self._parse_date(a.get("publishedAt", "")) > cutoff]

    def _parse_date(self, date_str: str) -> datetime:
        """Parse various date formats safely."""
        formats = [
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d"
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str.replace('Z', ''), fmt)
            except Exception:
                continue
        return datetime.now()

    def get_stats(self) -> dict:
        """
        Get statistics about the news data.
        :return: Dictionary with counts and distribution
        """
        if self.collection is not None and self.is_connected():
            try:
                total = self.collection.count_documents({})
                category_pipeline = [
                    {"$group": {"_id": "$category", "count": {"$sum": 1}}}
                ]
                sentiment_pipeline = [
                    {"$group": {"_id": "$sentiment.score", "count": {"$sum": 1}}}
                ]
                
                category_counts = {}
                for doc in self.collection.aggregate(category_pipeline):
                    category_counts[doc["_id"] or "general"] = doc["count"]
                
                sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
                for doc in self.collection.aggregate(sentiment_pipeline):
                    score = doc["_id"] or "neutral"
                    if score in sentiment_counts:
                        sentiment_counts[score] = doc["count"]
                
                return {
                    "total_articles": total,
                    "categories": category_counts,
                    "sentiment": sentiment_counts,
                    "storage_mode": "mongodb"
                }
            except Exception as e:
                logger.error(f"MongoDB stats error: {e}")
        
        articles = self.get_all_articles(limit=5000)
        total = len(articles)
        category_counts = {}
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}

        for a in articles:
            cat = a.get("category", "general") or "general"
            category_counts[cat] = category_counts.get(cat, 0) + 1

            sent = a.get("sentiment", {}).get("score", "neutral")
            sentiment_counts[sent] = sentiment_counts.get(sent, 0) + 1

        return {
            "total_articles": total,
            "categories": category_counts,
            "sentiment": sentiment_counts,
            "storage_mode": "mongodb" if self.is_connected() else "json_fallback"
        }

    def get_article_by_id(self, article_id: str) -> dict:
        """
        Get a specific article by its MongoDB ObjectId or URL.
        :param article_id: Article ID (ObjectId string or URL)
        :return: Article dictionary or None
        """
        if not article_id:
            return None

        try:
            if self.collection is not None and self.is_connected():
                # Try as ObjectId
                try:
                    from bson.objectid import ObjectId
                    article = self.collection.find_one({"_id": ObjectId(article_id)})
                    if article:
                        article["_id"] = str(article["_id"])
                        return article
                except Exception:
                    pass

                # Try as URL
                article = self.collection.find_one({"url": article_id})
                if article:
                    article["_id"] = str(article["_id"])
                    return article

        except Exception as e:
            logger.error(f"Error fetching article {article_id}: {e}")

        return None

    def get_unique_categories(self) -> list:
        """
        Get all unique categories from the database.
        :return: List of category names
        """
        if self.collection is not None and self.is_connected():
            try:
                pipeline = [
                    {"$group": {"_id": "$category"}},
                    {"$sort": {"_id": 1}}
                ]
                cursor = self.collection.aggregate(pipeline)
                return [doc["_id"] for doc in cursor if doc["_id"]]
            except Exception as e:
                logger.error(f"Error getting categories: {e}")

        # Fallback
        articles = self.get_all_articles(limit=100)
        categories = set()
        for a in articles:
            cat = a.get("category") or "general"
            categories.add(cat)
        return sorted(list(categories))

    def disconnect(self):
        """Close MongoDB connection."""
        if self.client is not None:
            try:
                self.client.close()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
        self._connected = False

    def get_articles_by_country(self, country_code: str = None, limit: int = 100) -> list:
        """Get articles filtered by country code."""
        query = {"country_code": country_code} if country_code else {}
        
        articles = []
        if self.collection is not None and self.is_connected():
            try:
                cursor = self.collection.find(query).sort("publishedAt", -1).limit(limit)
                for doc in cursor:
                    doc["_id"] = str(doc["_id"])
                    articles.append(doc)
            except Exception as e:
                logger.error(f"MongoDB fetch error: {e}")
                articles = self._read_json()
        else:
            articles = self._read_json()
            if country_code:
                articles = [a for a in articles if a.get("country_code") == country_code]
        
        return articles[:limit]

    def get_country_distribution(self) -> dict:
        """Get article count by country."""
        articles = self.get_all_articles(limit=1000)
        
        country_counts = {}
        for article in articles:
            code = article.get("country_code", "US")
            country_counts[code] = country_counts.get(code, 0) + 1
        
        return country_counts
