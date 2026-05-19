"""
Reports routes - Supabase version
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import Response
from slowapi import Limiter
from slowapi.util import get_remote_address

from routes.dependencies import get_current_user
from services.document_service import get_user_documents, get_document_by_id, delete_document
from utils.pdf_report import generate_pdf_report

logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/reports")
async def list_reports(
    request: Request,
    search: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    docs = await get_user_documents(
        user_id=str(current_user["id"]),
        search=search,
        date_from=date_from,
        date_to=date_to,
    )
    return {"reports": docs, "total": len(docs)}


@router.get("/report/{report_id}")
async def get_report(report_id: str, current_user: dict = Depends(get_current_user)):
    doc = await get_document_by_id(report_id, str(current_user["id"]))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return doc


@router.delete("/report/{report_id}", status_code=204)
async def delete_report(report_id: str, current_user: dict = Depends(get_current_user)):
    deleted = await delete_document(report_id, str(current_user["id"]))
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return None


@router.get("/report/{report_id}/download")
async def download_report_pdf(report_id: str, current_user: dict = Depends(get_current_user)):
    doc = await get_document_by_id(report_id, str(current_user["id"]))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    try:
        pdf_bytes = generate_pdf_report(doc)
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")

    safe_name = doc.get("filename", "report").replace(" ", "_")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="legal_analysis_{safe_name}.pdf"'},
    )
