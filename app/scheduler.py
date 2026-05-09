import schedule
import time
import threading
from datetime import datetime, timedelta
from app.config import settings
from app.fetcher import NewsFetcher
from app.database import DatabaseHandler
from app.utils import process_articles_batch


def fetch_and_store_news():
    """
    Scheduled job to fetch and store latest news.
    """
    print(f"[{time.strftime('%H:%M:%S')}] Starting scheduled news fetch...")
    
    try:
        fetcher = NewsFetcher()
        db = DatabaseHandler()
        
        if not db.connect():
            print("Database not connected. Fetching will be stored in JSON only.")
        
        # Fetch articles from RSS feeds only
        rss_articles = fetcher.fetch_rss_feeds()
        
        # Use RSS articles only
        all_articles = rss_articles
        
        if all_articles:
            print(f"Found {len(articles)} NewsAPI articles and {len(rss_articles)} RSS articles.")
            
            # Process articles
            processed_articles = process_articles_batch(all_articles)
            
            # Store in database
            count = db.store_articles_batch(processed_articles)
            print(f"Stored {count} unique articles.")
            
        else:
            print("No articles fetched.")
        
    except Exception as e:
        print(f"Scheduled job error: {e}")


def cleanup_old_articles(days: int = None):
    """
    Scheduled job to clean up old articles from storage.
    Respects ARTICLE_RETENTION_DAYS from environment.
    """
    retention_days = int(__import__("os").getenv("ARTICLE_RETENTION_DAYS", "30"))
    print(f"[{time.strftime('%H:%M:%S')}] Running cleanup for articles older than {retention_days} days...")

    try:
        db = DatabaseHandler()
        db.connect()

        if db.is_connected():
            print("MongoDB cleanup is handled by TTL index — skipping JSON cleanup.")
        else:
            articles = db.get_all_articles()
            if articles:
                now = datetime.now()
                cutoff = now - timedelta(days=retention_days)
                new_articles = []
                removed = 0

                for article in articles:
                    try:
                        pub_date_str = article.get("publishedAt", "")[:19]
                        pub_date = datetime.fromisoformat(pub_date_str)
                        if pub_date > cutoff:
                            new_articles.append(article)
                        else:
                            removed += 1
                    except Exception:
                        new_articles.append(article)

                if removed > 0:
                    import json
                    with open(db.json_file, 'w', encoding='utf-8') as f:
                        json.dump(new_articles, f, indent=2, default=str)
                    print(f"Removed {removed} old articles from JSON storage.")

    except Exception as e:
        print(f"Cleanup error: {e}")


def run_scheduler(interval: int = 3600):
    """
    Start the scheduler with given interval in seconds.
    :param interval: Interval in seconds between fetches
    """
    # Convert seconds to minutes/hours
    minutes = interval // 60
    hours = interval // 3600
    
    schedule.every(minutes).minutes.do(fetch_and_store_news)
    
    # Optional cleanup job (less frequent)
    schedule.every(7).days.do(cleanup_old_articles)
    
    print(f"Scheduler started. News will be fetched every {interval} seconds.")
    print(f"Press Ctrl+C to stop.")
    
    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    """
    Entry point for running the scheduler.
    """
    run_scheduler(interval=settings.SCHEDULE_INTERVAL)


if __name__ == "__main__":
    main()
