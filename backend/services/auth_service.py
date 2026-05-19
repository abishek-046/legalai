"""
Authentication service - Supabase version
Handles user registration, login, and JWT tokens using Supabase (PostgreSQL).
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from config import settings
from database import get_supabase

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def register_user(name: str, email: str, password: str) -> dict:
    """Register a new user in Supabase users table."""
    sb = get_supabase()
    email = email.lower().strip()

    # Check duplicate email
    existing = sb.table("users").select("id").eq("email", email).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user_data = {
        "name": name.strip(),
        "email": email,
        "hashed_password": hash_password(password),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = sb.table("users").insert(user_data).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

    user = result.data[0]
    logger.info(f"New user registered: {email}")
    return user


async def authenticate_user(email: str, password: str) -> dict:
    """Authenticate user by email and password."""
    sb = get_supabase()
    email = email.lower().strip()

    result = sb.table("users").select("*").eq("email", email).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    user = result.data[0]
    if not verify_password(password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return user


async def get_user_by_id(user_id: str) -> Optional[dict]:
    """Fetch a user by UUID."""
    sb = get_supabase()
    try:
        result = sb.table("users").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        return None
