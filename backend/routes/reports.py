"""
Reports routes - list, view, delete, and download PDF reports
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import Response
from slowapi import Limiter
from slowapi.util import get_remote_address

from routes.dependencies import get_current_user
from services.document_service import (
    get_user_documents,
    get_document_by_id,
    delete_document,
)
from utils.pdf_report import generate_pdf_report

logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/reports")
async def list_reports(
    request: Request,
    search: Optional[str] = Query(None, description="Search by filename"),
    date_from: Optional[str] = Query(None, description="Filter from date (ISO format)"),
    date_to: Optional[str] = Query(None, description="Filter to date (ISO format)"),
    current_user: dict = Depends(get_current_user),
):
    """Get all reports for the authenticated user."""
    docs = await get_user_documents(
        user_id=str(current_user["_id"]),
        search=search,
        date_from=date_from,
        date_to=date_to,
    )
    return {"reports": docs, "total": len(docs)}


@router.get("/report/{report_id}")
async def get_report(
    report_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a single report by ID."""
    doc = await get_document_by_id(report_id, str(current_user["_id"]))
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    return doc


@router.delete("/report/{report_id}", status_code=204)
async def delete_report(
    report_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a report by ID."""
    deleted = await delete_document(report_id, str(current_user["_id"]))
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    return None


@router.get("/report/{report_id}/download")
async def download_report_pdf(
    report_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Download a report as a PDF file."""
    doc = await get_document_by_id(report_id, str(current_user["_id"]))
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    try:
        pdf_bytes = generate_pdf_report(doc)
    except Exception as e:
        logger.error(f"PDF generation failed for report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PDF report",
        )

    safe_name = doc.get("filename", "report").replace(" ", "_")
    filename = f"legal_analysis_{safe_name}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
