"""
OCR and document text extraction utilities
Supports PDF, DOCX, PNG, JPG formats
"""

import io
import logging
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    if not text:
        return ""
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)
    # Remove non-printable characters (keep newlines)
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)
    # Collapse multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file using pdfplumber."""
    try:
        import pdfplumber

        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                logger.debug(f"Extracted page {page_num}/{len(pdf.pages)}")

        full_text = "\n\n".join(text_parts)
        cleaned = clean_text(full_text)
        logger.info(f"PDF extraction: {len(cleaned)} characters extracted")
        return cleaned

    except ImportError:
        logger.error("pdfplumber not installed")
        raise RuntimeError("PDF processing library not available")
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise RuntimeError(f"Failed to extract text from PDF: {str(e)}")


def extract_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document

        doc = Document(io.BytesIO(file_bytes))
        paragraphs = []

        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text.strip())

        # Also extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(
                    cell.text.strip() for cell in row.cells if cell.text.strip()
                )
                if row_text:
                    paragraphs.append(row_text)

        full_text = "\n".join(paragraphs)
        cleaned = clean_text(full_text)
        logger.info(f"DOCX extraction: {len(cleaned)} characters extracted")
        return cleaned

    except ImportError:
        logger.error("python-docx not installed")
        raise RuntimeError("DOCX processing library not available")
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        raise RuntimeError(f"Failed to extract text from DOCX: {str(e)}")


def extract_from_image(file_bytes: bytes) -> str:
    """Extract text from an image using pytesseract OCR."""
    try:
        import pytesseract
        from PIL import Image

        image = Image.open(io.BytesIO(file_bytes))

        # Convert to RGB if needed
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        # OCR with English language
        text = pytesseract.image_to_string(image, lang="eng")
        cleaned = clean_text(text)
        logger.info(f"Image OCR: {len(cleaned)} characters extracted")
        return cleaned

    except ImportError:
        logger.error("pytesseract not installed - image OCR unavailable")
        raise RuntimeError(
            "Image OCR is not available on this server. "
            "Please upload a PDF or DOCX file instead."
        )
    except Exception as e:
        # Tesseract binary not found
        if "tesseract" in str(e).lower():
            raise RuntimeError(
                "Tesseract OCR is not installed on this server. "
                "Please upload a PDF or DOCX file instead."
            )
        logger.error(f"Image OCR error: {e}")
        raise RuntimeError(f"Failed to extract text from image: {str(e)}")


def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Route to the correct extractor based on file extension.
    Returns cleaned extracted text.
    """
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        return extract_from_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        return extract_from_docx(file_bytes)
    elif ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
        return extract_from_image(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def get_document_type(filename: str) -> str:
    """Return a human-readable document type label."""
    ext = Path(filename).suffix.lower()
    type_map = {
        ".pdf": "PDF",
        ".docx": "DOCX",
        ".doc": "DOC",
        ".png": "Image (PNG)",
        ".jpg": "Image (JPG)",
        ".jpeg": "Image (JPEG)",
    }
    return type_map.get(ext, "Unknown")
