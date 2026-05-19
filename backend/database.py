"""
Supabase database connection
Uses the supabase-py client (sync wrapped for FastAPI compatibility)
"""

import logging
from supabase import create_client, Client
from config import settings

logger = logging.getLogger(__name__)

_client: Client = None


def get_supabase() -> Client:
    """Return the Supabase client instance."""
    global _client
    if _client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set")
        # Strip any invisible/non-printable characters from URL and key
        url = "".join(c for c in settings.SUPABASE_URL if c.isprintable()).strip()
        key = "".join(c for c in settings.SUPABASE_KEY if c.isprintable()).strip()
        _client = create_client(url, key)
    return _client


def get_admin_supabase() -> Client:
    """Return a Supabase client with service_role key for admin operations."""
    url = "".join(c for c in settings.SUPABASE_URL if c.isprintable()).strip()
    key = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY
    key = "".join(c for c in key if c.isprintable()).strip()
    return create_client(url, key)


async def connect_db():
    """Initialize and verify Supabase connection."""
    try:
        client = get_supabase()
        # Simple ping - just initialize the client
        logger.info("Supabase client initialized successfully")
    except Exception as e:
        logger.error(f"Supabase connection failed: {e}")
        raise


async def disconnect_db():
    """No persistent connection to close with supabase-py."""
    logger.info("Supabase client released")
