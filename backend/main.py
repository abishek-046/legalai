"""
Legal Documentation Assistant - FastAPI Backend
Main application entry point
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import settings
from database import connect_db, disconnect_db
from routes import auth, documents, reports

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    logger.info("Starting Legal Assistant API...")
    try:
        await connect_db()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.warning("Starting without database - some features will be unavailable")
    yield
    logger.info("Shutting down Legal Assistant API...")
    await disconnect_db()


app = FastAPI(
    title="Legal Documentation Assistant API",
    description="AI-powered legal document analysis platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Static files for uploads - handle gracefully if directory not writable
import os
try:
    os.makedirs("uploads", exist_ok=True)
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    logger.info("Uploads directory mounted successfully")
except Exception as e:
    logger.warning(f"Could not mount uploads directory: {e}")

# Include routers
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
        db_status = f"disconnected: {str(e)}"
    return {"status": "healthy", "database": db_status}


@app.get("/debug")
async def debug():
    from config import settings
    return {
        "supabase_url_set": bool(settings.SUPABASE_URL and "supabase" in settings.SUPABASE_URL),
        "supabase_key_set": bool(settings.SUPABASE_KEY and len(settings.SUPABASE_KEY) > 10),
        "supabase_service_key_set": bool(settings.SUPABASE_SERVICE_KEY and len(settings.SUPABASE_SERVICE_KEY) > 10),
        "openai_key_set": bool(settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY) > 5),
        "secret_key_set": bool(settings.SECRET_KEY),
        "allowed_origins": settings.origins_list,
    }
