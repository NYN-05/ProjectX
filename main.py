import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from app.api import router
from app.database import DatabaseHandler
from app.scheduler import run_scheduler, fetch_and_store_news
from app.limiter import limiter
import uvicorn
import threading
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="News Intelligence API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[h.strip() for h in ALLOWED_ORIGINS] + ["localhost", "127.0.0.1"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    db = DatabaseHandler()
    db.connect()

    threading.Thread(target=fetch_and_store_news, daemon=True).start()
    threading.Thread(target=run_scheduler, daemon=True).start()

    print("News Intelligence API starting...")
    print("Dashboard available at: http://localhost:3000")
    print("API endpoints available at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop\n")

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
