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
    groq_key = os.environ.get("GROQ_API_KEY", "").strip()
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    from config import settings
    url = "".join(c for c in (settings.SUPABASE_URL or "") if c.isprintable()).strip()
    return {
        "supabase_url_set": "supabase" in url,
        "supabase_key_set": len(settings.SUPABASE_KEY or "") > 10,
        "groq_key_set": bool(groq_key),
        "groq_key_prefix": groq_key[:8] if groq_key else "NOT SET",
        "groq_key_valid": groq_key.startswith("gsk_") if groq_key else False,
        "openai_key_set": bool(openai_key),
        "openai_key_prefix": openai_key[:8] if openai_key else "NOT SET",
        "all_env_keys": sorted([k for k in os.environ.keys()]),
    }


@app.get("/test-groq")
async def test_groq():
    """Test Groq API connection."""
    groq_key = os.environ.get("GROQ_API_KEY", "").strip()
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()

    result = {
        "groq_key_set": bool(groq_key),
        "groq_key_prefix": groq_key[:8] if groq_key else "NOT SET",
        "openai_key_set": bool(openai_key),
        "all_api_keys": [k for k in os.environ.keys() if "KEY" in k or "API" in k or "SECRET" in k],
    }

    # Test Groq
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=5,
            )
            result["groq_working"] = True
            result["groq_response"] = response.choices[0].message.content
        except Exception as e:
            result["groq_working"] = False
            result["groq_error"] = str(e)

    # Test OpenAI
    if openai_key:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=openai_key, timeout=10.0)
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=5,
            )
            result["openai_working"] = True
        except Exception as e:
            result["openai_working"] = False
            result["openai_error"] = str(e)[:100]

    return result


@app.get("/test-db")
async def test_db():
    try:
        from database import get_supabase
        sb = get_supabase()
        res = sb.table("users").select("id").limit(1).execute()
        return {"status": "ok", "users_table": "accessible", "data": res.data}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
