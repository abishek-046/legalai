"""
Document service - handles document storage and retrieval from MongoDB
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List
from bson import ObjectId

from database import get_database

logger = logging.getLogger(__name__)


def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict."""
    if doc is None:
        return None
    doc["id"] = str(doc.pop("_id"))
    if "userId" in doc and isinstance(doc["userId"], ObjectId):
        doc["userId"] = str(doc["userId"])
    return doc


async def save_document(
    user_id: str,
    filename: str,
    document_type: str,
    extracted_text: str,
    analysis: dict,
) -> dict:
    """Save a document and its AI analysis to MongoDB."""
    db = get_database()

    doc = {
        "userId": ObjectId(user_id),
        "filename": filename,
        "documentType": document_type,
        "extractedText": extracted_text[:5000],  # Store first 5000 chars
        "summary": analysis.get("summary", ""),
        "riskLevel": analysis.get("riskLevel", "Medium"),
        "warnings": analysis.get("warnings", []),
        "suspiciousClauses": analysis.get("suspiciousClauses", []),
        "missingClauses": analysis.get("missingClauses", []),
        "financialRisks": analysis.get("financialRisks", []),
        "expiryRisks": analysis.get("expiryRisks", []),
        "unfairConditions": analysis.get("unfairConditions", []),
        "recommendations": analysis.get("recommendations", []),
        "safeToSign": analysis.get("safeToSign", False),
        "createdAt": datetime.now(timezone.utc),
    }

    result = await db.documents.insert_one(doc)
    doc["_id"] = result.inserted_id
    logger.info(f"Document saved: {filename} for user {user_id}")
    return serialize_doc(doc)


async def get_user_documents(
    user_id: str,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[dict]:
    """Get all documents for a user with optional filters."""
    db = get_database()

    query = {"userId": ObjectId(user_id)}

    if search:
        query["filename"] = {"$regex": search, "$options": "i"}

    if date_from or date_to:
        date_filter = {}
        if date_from:
            date_filter["$gte"] = datetime.fromisoformat(date_from)
        if date_to:
            date_filter["$lte"] = datetime.fromisoformat(date_to)
        query["createdAt"] = date_filter

    cursor = db.documents.find(
        query,
        {"extractedText": 0}  # Exclude large text field from list
    ).sort("createdAt", -1)

    docs = []
    async for doc in cursor:
        docs.append(serialize_doc(doc))

    return docs


async def get_document_by_id(doc_id: str, user_id: str) -> Optional[dict]:
    """Get a single document by ID, ensuring it belongs to the user."""
    db = get_database()
    try:
        doc = await db.documents.find_one(
            {"_id": ObjectId(doc_id), "userId": ObjectId(user_id)}
        )
        return serialize_doc(doc) if doc else None
    except Exception as e:
        logger.error(f"Error fetching document {doc_id}: {e}")
        return None


async def delete_document(doc_id: str, user_id: str) -> bool:
    """Delete a document by ID, ensuring it belongs to the user."""
    db = get_database()
    try:
        result = await db.documents.delete_one(
            {"_id": ObjectId(doc_id), "userId": ObjectId(user_id)}
        )
        if result.deleted_count > 0:
            logger.info(f"Document deleted: {doc_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting document {doc_id}: {e}")
        return False
