"""
Authentication routes - register, login
Supabase version - uses user["id"] (UUID) instead of MongoDB ObjectId.
"""

import logging
from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from models.user import UserCreate, UserLogin, TokenResponse, UserResponse
from services.auth_service import (
    register_user,
    authenticate_user,
    create_access_token,
)

logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit("10/minute")
async def register(request: Request, user_data: UserCreate):
    """Register a new user and return a JWT token."""
    try:
        user = await register_user(user_data.name, user_data.email, user_data.password)
        token = create_access_token({"sub": str(user["id"])})
        return TokenResponse(
            access_token=token,
            user=UserResponse(
                id=str(user["id"]),
                name=user["name"],
                email=user["email"],
                createdAt=user["created_at"],
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Register error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("20/minute")
async def login(request: Request, credentials: UserLogin):
    """Authenticate user and return a JWT token."""
    try:
        user = await authenticate_user(credentials.email, credentials.password)
        token = create_access_token({"sub": str(user["id"])})
        return TokenResponse(
            access_token=token,
            user=UserResponse(
                id=str(user["id"]),
                name=user["name"],
                email=user["email"],
                createdAt=user["created_at"],
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )
