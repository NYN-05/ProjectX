import logging

from fastapi import APIRouter, HTTPException, Query, Path, Request
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.database import DatabaseHandler
from app.fetcher import NewsFetcher
from app.utils import process_articles_batch
from app.config import settings
from app.limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter()
db = DatabaseHandler()

# Pydantic models for request/response validation
class ArticleResponse(BaseModel):
    title: str
    description: str
    url: str
    urlToImage: Optional[str] = None
    publishedAt: str
    source: dict
    author: Optional[str] = None
    content: Optional[str] = None
    sentiment: Optional[dict] = None
    keywords: Optional[List[str]] = None
    category: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    total: int
    results: List[dict]

class StatsResponse(BaseModel):
    total_articles: int
    categories: dict
    sentiment: dict
    storage_mode: str

class ErrorResponse(BaseModel):
    detail: str

@router.on_event("startup")
def startup_db_client():
    """Initialize database connection on startup."""
    try:
        db.connect()
        logger.info("Database connection initialized")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")

@router.on_event("shutdown")
def shutdown_db_client():
    """Close database connection on shutdown."""
    try:
        db.disconnect()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    status = "healthy" if db.is_connected() else "degraded"
    return {
        "status": status,
        "database": "connected" if db.is_connected() else "using_json_fallback",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/news")
@limiter.limit("60/minute")
async def get_news(request: Request,
    country: str = Query(default="us", min_length=2, max_length=2, description="Country code"),
    limit: int = Query(default=50, ge=1, le=100, description="Number of articles"),
    skip: int = Query(default=0, ge=0, description="Number of articles to skip"),
    category: Optional[str] = Query(default=None, description="Category filter"),
    from_date: Optional[str] = Query(default=None, description="Start date (ISO format)"),
    to_date: Optional[str] = Query(default=None, description="End date (ISO format)")
):
    """
    Get latest news articles with filtering and pagination.
    Returns articles from MongoDB or fetches from NewsAPI if DB is empty.
    """
    try:
        articles = db.get_all_articles(
            limit=limit,
            skip=skip,
            category=category,
            from_date=from_date,
            to_date=to_date
        )

        if not articles:
            # If DB is empty, fetch fresh data
            fetcher = NewsFetcher()
            articles = fetcher.get_top_headlines(country=country)
            if articles:
                processed = process_articles_batch(articles)
                db.store_articles_batch(processed)
                articles = processed[:limit]

        return {
            "success": True,
            "total": len(articles),
            "skip": skip,
            "limit": limit,
            "data": articles
        }

    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/news/{article_id}")
async def get_article(
    article_id: str = Path(..., description="Article ID (MongoDB ObjectId or URL)")
):
    """
    Get a specific article by ID.
    Accepts either MongoDB ObjectId or URL as identifier.
    """
    article = db.get_article_by_id(article_id)

    if not article:
        raise HTTPException(
            status_code=404,
            detail=f"Article not found: {article_id}"
        )

    return {
        "success": True,
        "data": article
    }


@router.get("/search")
@limiter.limit("30/minute")
async def search_news(request: Request,
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    limit: int = Query(default=50, ge=1, le=100),
    skip: int = Query(default=0, ge=0)
):
    """
    Search for news articles by keyword.
    Uses MongoDB text index if available.
    """
    if not q or not q.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    try:
        articles = db.search_articles(q=q, limit=limit, skip=skip)

        return {
            "success": True,
            "query": q,
            "total": len(articles),
            "skip": skip,
            "limit": limit,
            "data": articles
        }

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/categories")
async def get_categories():
    """
    Get list of available categories from the database.
    """
    try:
        categories = db.get_unique_categories()

        if not categories:
            # Fallback to hardcoded list
            categories = [
                "business", "technology", "health", "sports",
                "entertainment", "science", "politics", "crime", "general"
            ]

        return {
            "success": True,
            "total": len(categories),
            "data": categories
        }

    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch categories")


@router.get("/category/{category_name}")
async def get_by_category(
    category_name: str,
    limit: int = Query(default=50, ge=1, le=100),
    skip: int = Query(default=0, ge=0)
):
    """
    Get news articles filtered by category.
    """
    # Validate category exists
    all_categories = db.get_unique_categories()
    category_lower = category_name.lower()
    valid_categories = [c.lower() for c in all_categories]

    if category_lower not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Available: {', '.join(all_categories[:10])}"
        )

    try:
        articles = db.get_by_category(category=category_name, limit=limit, skip=skip)

        return {
            "success": True,
            "category": category_name,
            "total": len(articles),
            "skip": skip,
            "limit": limit,
            "data": articles
        }

    except Exception as e:
        logger.error(f"Category fetch error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch category: {str(e)}")


@router.get("/stats")
@limiter.limit("30/minute")
async def get_stats(request: Request):
    """
    Get comprehensive statistics about the news data.
    """
    try:
        stats = db.get_stats()

        return {
            "success": True,
            "data": stats
        }

    except Exception as e:
        logger.error(f"Stats fetch error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")


@router.get("/fetch")
@limiter.limit("5/minute")
async def fetch_news_now(request: Request):
    """
    Trigger a one-time news fetch from NewsAPI and RSS feeds.
    Returns immediately with fetch status.
    """
    try:
        fetcher = NewsFetcher()

        # Fetch top headlines
        articles = fetcher.get_top_headlines(country="us", language="en")
        rss_articles = fetcher.fetch_rss_feeds()

        all_articles = articles + rss_articles

        if all_articles:
            processed = process_articles_batch(all_articles)
            count = db.store_articles_batch(processed)

            return {
                "success": True,
                "message": f"Fetched and stored {count} articles",
                "newsapi_count": len(articles),
                "rss_count": len(rss_articles),
                "total_stored": count
            }
        else:
            return {
                "success": False,
                "message": "No articles fetched",
                "newsapi_count": 0,
                "rss_count": 0
            }

    except Exception as e:
        logger.error(f"Fetch error: {e}")
        raise HTTPException(status_code=500, detail=f"Fetch failed: {str(e)}")


@router.get("/rss/status")
async def rss_status():
    """
    Get status of RSS feed sources.
    """
    feeds_status = []
    for source_name, url in settings.RSS_FEEDS.items():
        feeds_status.append({
            "source": source_name,
            "url": url,
            "enabled": True,
            "last_check": None,
            "status": "configured"
        })

    return {
        "success": True,
        "total_feeds": len(feeds_status),
        "data": feeds_status
    }