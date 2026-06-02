"""
Document upload and analysis routes
"""

import logging
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from config import settings
from routes.dependencies import get_current_user
from services.document_service import save_document
from utils.ocr import extract_text_async, get_document_type
from ai.analyzer import analyze_legal_document

logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".doc",
    ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"
}
MAX_FILE_SIZE = settings.MAX_FILE_SIZE_MB * 1024 * 1024


@router.post("/analyze")
@limiter.limit("5/minute")
async def analyze_document(
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload a document, extract text (text PDF / scanned PDF / image),
    run AI legal analysis, save to database, and return the full report.
    """
    # ── Validate file extension ──────────────────────────────────────────────
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"File type '{ext}' is not supported. "
                "Accepted types: PDF, DOCX, DOC, PNG, JPG, JPEG, WEBP, BMP, TIFF"
            ),
        )

    # ── Read file ────────────────────────────────────────────────────────────
    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty.",
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File is too large. Maximum allowed size is {settings.MAX_FILE_SIZE_MB}MB.",
        )

    logger.info(
        f"Processing document: '{file.filename}' "
        f"({len(file_bytes)} bytes) for user {current_user['id']}"
    )

    # ── Extract text ─────────────────────────────────────────────────────────
    try:
        extracted_text = await extract_text_async(file_bytes, file.filename)
    except ValueError as e:
        # Unsupported file type
        logger.warning(f"Unsupported file type '{file.filename}': {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        # Extraction failed
        logger.error(f"Text extraction failed for '{file.filename}': {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected extraction error for '{file.filename}': {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process document: {str(e)}",
        )

    # ── Validate extracted text ──────────────────────────────────────────────
    if not extracted_text or len(extracted_text.strip()) < 20:
        logger.warning(
            f"Insufficient text extracted from '{file.filename}': "
            f"{len(extracted_text.strip()) if extracted_text else 0} chars"
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Could not extract readable text from this document. "
                "The file may be a scanned image or protected PDF. "
                "Please try a different file or ensure the document contains readable text."
            ),
        )

    logger.info(f"Extracted {len(extracted_text)} characters from '{file.filename}'")

    # ── AI Analysis ──────────────────────────────────────────────────────────
    try:
        analysis = await analyze_legal_document(extracted_text)
    except Exception as e:
        logger.error(f"AI analysis failed for '{file.filename}': {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI analysis service is temporarily unavailable. Please try again.",
        )

    # ── Save to database ─────────────────────────────────────────────────────
    try:
        doc_type = get_document_type(file.filename)
        saved_doc = await save_document(
            user_id=str(current_user["id"]),
            filename=file.filename,
            document_type=doc_type,
            extracted_text=extracted_text,
            analysis=analysis,
        )
    except Exception as e:
        logger.error(f"Failed to save document '{file.filename}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis complete but failed to save report. Please try again.",
        )

    logger.info(f"Document '{file.filename}' analyzed and saved as report {saved_doc['id']}")
    return saved_doc
