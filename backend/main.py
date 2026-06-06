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
    logger.info("Shutting down.")


app = FastAPI(title="Legal Documentation Assistant API", version="1.0.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    os.makedirs("uploads", exist_ok=True)
except Exception:
    pass

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
        db_status = f"disconnected: {str(e)[:80]}"
    return {"status": "healthy", "database": db_status}


@app.get("/debug")
async def debug():
    from config import settings
    groq_key = (settings.GROQ_API_KEY or "").strip()
    gemini_key = (settings.GEMINI_API_KEY or "").strip()
    openai_key = (settings.OPENAI_API_KEY or "").strip()
    url = "".join(c for c in settings.SUPABASE_URL if c.isprintable()).strip()
    return {
        "supabase_url_set": "supabase" in url,
        "supabase_key_set": len(settings.SUPABASE_KEY) > 10,
        "groq_key_prefix": groq_key[:6] if groq_key else "NOT SET",
        "groq_key_valid": len(groq_key) > 10 and groq_key.startswith("gsk_"),
        "gemini_key_prefix": gemini_key[:8] if gemini_key else "NOT SET",
        "gemini_key_valid": len(gemini_key) > 10 and gemini_key.startswith("AIzaSy"),
        "openai_key_valid": len(openai_key) > 20 and not openai_key.startswith("sk-your"),
        "ai_configured": (
            (len(groq_key) > 10) or
            (len(gemini_key) > 10) or
            (len(openai_key) > 20 and not openai_key.startswith("sk-your"))
        ),
    }


@app.get("/test-groq")
async def test_groq():
    """Directly test Groq API with the configured key."""
    from config import settings
    key = (settings.GROQ_API_KEY or "").strip()

    if not key:
        return {"status": "error", "detail": "GROQ_API_KEY is not set on Render"}

    if len(key) < 10:
        return {"status": "error", "detail": f"GROQ_API_KEY too short: {len(key)} chars"}

    try:
        from groq import Groq
        client = Groq(api_key=key)
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": "Say OK"}],
            max_tokens=5,
        )
        return {
            "status": "ok",
            "groq_working": True,
            "key_prefix": key[:8],
            "response": response.choices[0].message.content,
        }
    except Exception as e:
        return {
            "status": "error",
            "groq_working": False,
            "key_prefix": key[:8],
            "detail": str(e),
        }
async def test_db():
    try:
        from database import get_supabase
        sb = get_supabase()
        result = sb.table("users").select("id").limit(1).execute()
        return {"status": "ok", "users_table": "accessible", "data": result.data}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
