"""
Document service - Supabase version (Enhanced)
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List

from database import get_supabase

logger = logging.getLogger(__name__)


def _serialize(doc: dict) -> dict:
    if not doc:
        return None
    return {
        "id": doc.get("id"),
        "userId": doc.get("user_id"),
        "filename": doc.get("filename"),
        "documentType": doc.get("document_type"),
        "summary": doc.get("summary"),
        "riskLevel": doc.get("risk_level"),
        "riskReason": doc.get("risk_reason"),
        "documentStatus": doc.get("document_status"),
        "confidenceScore": doc.get("confidence_score"),
        "documentIssues": doc.get("document_issues") or [],
        "warnings": doc.get("warnings") or [],
        "suspiciousClauses": doc.get("suspicious_clauses") or [],
        "missingClauses": doc.get("missing_clauses") or [],
        "financialRisks": doc.get("financial_risks") or [],
        "expiryRisks": doc.get("expiry_risks") or [],
        "unfairConditions": doc.get("unfair_conditions") or [],
        "complianceIssues": doc.get("compliance_issues") or [],
        "privacyRisks": doc.get("privacy_risks") or [],
        "legalLoopholes": doc.get("legal_loopholes") or [],
        "recommendations": doc.get("recommendations") or [],
        "finalVerdict": doc.get("final_verdict"),
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
    sb = get_supabase()

    row = {
        "user_id": user_id,
        "filename": filename,
        "document_type": document_type,
        "extracted_text": extracted_text[:5000],
        "summary": analysis.get("summary", ""),
        "risk_level": analysis.get("riskLevel", "Medium"),
        "risk_reason": analysis.get("riskReason", ""),
        "document_status": analysis.get("documentStatus", "Needs Review"),
        "confidence_score": analysis.get("confidenceScore", 0),
        "document_issues": analysis.get("documentIssues", []),
        "warnings": analysis.get("warnings", []),
        "suspicious_clauses": analysis.get("suspiciousClauses", []),
        "missing_clauses": analysis.get("missingClauses", []),
        "financial_risks": analysis.get("financialRisks", []),
        "expiry_risks": analysis.get("expiryRisks", []),
        "unfair_conditions": analysis.get("unfairConditions", []),
        "compliance_issues": analysis.get("complianceIssues", []),
        "privacy_risks": analysis.get("privacyRisks", []),
        "legal_loopholes": analysis.get("legalLoopholes", []),
        "recommendations": analysis.get("recommendations", []),
        "final_verdict": analysis.get("finalVerdict", ""),
        "safe_to_sign": analysis.get("safeToSign", False),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = sb.table("documents").insert(row).execute()
    if not result.data:
        raise RuntimeError("Failed to save document to database")

    logger.info(f"Saved: {filename} — {analysis.get('documentStatus')} / {analysis.get('riskLevel')}")
    return _serialize(result.data[0])


async def get_user_documents(
    user_id: str,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[dict]:
    sb = get_supabase()
    query = (
        sb.table("documents")
        .select("id,user_id,filename,document_type,risk_level,document_status,confidence_score,safe_to_sign,created_at")
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
        logger.error(f"Error fetching {doc_id}: {e}")
        return None


async def delete_document(doc_id: str, user_id: str) -> bool:
    sb = get_supabase()
    try:
        result = (
            sb.table("documents")
            .delete()
            .eq("id", doc_id)
            .eq("user_id", user_id)
            .execute()
        )
        deleted = bool(result.data)
        if deleted:
            logger.info(f"Deleted: {doc_id}")
        return deleted
    except Exception as e:
        logger.error(f"Delete error {doc_id}: {e}")
        return False
