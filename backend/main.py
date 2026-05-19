"""
Legal Documentation Assistant - FastAPI Backend
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from routes import auth, documents, reports

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Legal Assistant API...")
    yield
    logger.info("Shutting down Legal Assistant API...")


app = FastAPI(
    title="Legal Documentation Assistant API",
    version="1.0.0",
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — allow all origins to fix deployment issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uploads directory
try:
    os.makedirs("uploads", exist_ok=True)
except Exception:
    pass

# Routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(documents.router, prefix="/api", tags=["Documents"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])


@app.get("/")
async def root():
    return {"message": "Legal Documentation Assistant API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health_check():
    try:
        from database import get_supabase
        sb = get_supabase()
        sb.table("users").select("id").limit(1).execute()
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)[:100]}"
    return {"status": "healthy", "database": db_status}


@app.get("/debug")
async def debug():
    from config import settings
    url = "".join(c for c in settings.SUPABASE_URL if c.isprintable()).strip()
    return {
        "supabase_url_preview": url[:40] if url else "NOT SET",
        "supabase_url_set": "supabase" in url,
        "supabase_key_set": len(settings.SUPABASE_KEY) > 10,
        "secret_key_set": bool(settings.SECRET_KEY),
        "openai_key_set": len(settings.OPENAI_API_KEY) > 5,
    }
