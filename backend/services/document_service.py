"""
Document service - Supabase version
Handles document storage and retrieval using Supabase (PostgreSQL).
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional, List

from database import get_supabase

logger = logging.getLogger(__name__)


def _serialize(doc: dict) -> dict:
    """Normalize Supabase row to match frontend expectations."""
    if not doc:
        return None
    # Map snake_case DB columns to camelCase for frontend
    return {
        "id": doc.get("id"),
        "userId": doc.get("user_id"),
        "filename": doc.get("filename"),
        "documentType": doc.get("document_type"),
        "summary": doc.get("summary"),
        "riskLevel": doc.get("risk_level"),
        "warnings": doc.get("warnings") or [],
        "suspiciousClauses": doc.get("suspicious_clauses") or [],
        "missingClauses": doc.get("missing_clauses") or [],
        "financialRisks": doc.get("financial_risks") or [],
        "expiryRisks": doc.get("expiry_risks") or [],
        "unfairConditions": doc.get("unfair_conditions") or [],
        "recommendations": doc.get("recommendations") or [],
        "safeToSign": doc.get("safe_to_sign"),
        "createdAt": doc.get("created_at"),
    }


async def save_document(
    user_id: str,
    filename: str,
    document_type: str,
    extracted_text: str,
    analysis: dict,
) -> dict:
    """Save a document and its AI analysis to Supabase."""
    sb = get_supabase()

    row = {
        "user_id": user_id,
        "filename": filename,
        "document_type": document_type,
        "extracted_text": extracted_text[:5000],
        "summary": analysis.get("summary", ""),
        "risk_level": analysis.get("riskLevel", "Medium"),
        "warnings": analysis.get("warnings", []),
        "suspicious_clauses": analysis.get("suspiciousClauses", []),
        "missing_clauses": analysis.get("missingClauses", []),
        "financial_risks": analysis.get("financialRisks", []),
        "expiry_risks": analysis.get("expiryRisks", []),
        "unfair_conditions": analysis.get("unfairConditions", []),
        "recommendations": analysis.get("recommendations", []),
        "safe_to_sign": analysis.get("safeToSign", False),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = sb.table("documents").insert(row).execute()
    if not result.data:
        raise RuntimeError("Failed to save document to database")

    logger.info(f"Document saved: {filename} for user {user_id}")
    return _serialize(result.data[0])


async def get_user_documents(
    user_id: str,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[dict]:
    """Get all documents for a user with optional filters."""
    sb = get_supabase()

    query = (
        sb.table("documents")
        .select("id,user_id,filename,document_type,risk_level,safe_to_sign,created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
    )

    if search:
        query = query.ilike("filename", f"%{search}%")
    if date_from:
        query = query.gte("created_at", date_from)
    if date_to:
        query = query.lte("created_at", date_to)

    result = query.execute()
    return [_serialize(doc) for doc in (result.data or [])]


async def get_document_by_id(doc_id: str, user_id: str) -> Optional[dict]:
    """Get a single document by ID, ensuring it belongs to the user."""
    sb = get_supabase()
    try:
        result = (
            sb.table("documents")
            .select("*")
            .eq("id", doc_id)
            .eq("user_id", user_id)
            .execute()
        )
        return _serialize(result.data[0]) if result.data else None
    except Exception as e:
        logger.error(f"Error fetching document {doc_id}: {e}")
        return None


async def delete_document(doc_id: str, user_id: str) -> bool:
    """Delete a document by ID, ensuring it belongs to the user."""
    sb = get_supabase()
    try:
        result = (
            sb.table("documents")
            .delete()
            .eq("id", doc_id)
            .eq("user_id", user_id)
            .execute()
        )
        deleted = len(result.data) > 0 if result.data else False
        if deleted:
            logger.info(f"Document deleted: {doc_id}")
        return deleted
    except Exception as e:
        logger.error(f"Error deleting document {doc_id}: {e}")
        return False
