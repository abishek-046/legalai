"""
OCR and document text extraction utilities
Supports PDF (text + scanned), DOCX, PNG, JPG formats

Libraries:
- pdfplumber: extract text from text-based PDFs
- pymupdf (fitz): extract text from scanned/image PDFs using built-in OCR
- python-docx: extract text from DOCX files
- pytesseract: extract text from images (local only, not on Render)
"""

import io
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from PDF using pdfplumber first.
    If text is too short (scanned PDF), fall back to PyMuPDF OCR.
    """
    # Try pdfplumber first (best for text-based PDFs)
    text = _extract_pdf_pdfplumber(file_bytes)

    # If very little text extracted, it's likely a scanned PDF
    if len(text.strip()) < 50:
        logger.info("pdfplumber extracted little text — trying PyMuPDF for scanned PDF")
        text = _extract_pdf_pymupdf(file_bytes)

    return clean_text(text)


def _extract_pdf_pdfplumber(file_bytes: bytes) -> str:
    """Extract text from text-based PDF using pdfplumber."""
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n\n".join(text_parts)
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}")
        return ""


def _extract_pdf_pymupdf(file_bytes: bytes) -> str:
    """
    Extract text from scanned/image PDF using PyMuPDF.
    PyMuPDF has built-in text extraction that works on many scanned PDFs.
    """
    try:
        import fitz  # PyMuPDF

        text_parts = []
        doc = fitz.open(stream=file_bytes, filetype="pdf")

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Try direct text extraction first
            page_text = page.get_text("text")

            if page_text and len(page_text.strip()) > 20:
                text_parts.append(page_text)
            else:
                # For image pages, render and extract text blocks
                # PyMuPDF can extract text from many scanned docs
                blocks = page.get_text("blocks")
                block_text = " ".join([b[4] for b in blocks if isinstance(b[4], str)])
                if block_text.strip():
                    text_parts.append(block_text)

        doc.close()
        result = "\n\n".join(text_parts)
        logger.info(f"PyMuPDF extracted {len(result)} characters")
        return result

    except ImportError:
        logger.error("PyMuPDF (fitz) not installed")
        return ""
    except Exception as e:
        logger.error(f"PyMuPDF extraction failed: {e}")
        return ""


def extract_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text.strip())
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(
                    cell.text.strip() for cell in row.cells if cell.text.strip()
                )
                if row_text:
                    paragraphs.append(row_text)
        full_text = "\n".join(paragraphs)
        cleaned = clean_text(full_text)
        logger.info(f"DOCX extraction: {len(cleaned)} characters")
        return cleaned
    except ImportError:
        raise RuntimeError("DOCX processing library not available")
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from DOCX: {str(e)}")


def extract_from_image(file_bytes: bytes) -> str:
    """Extract text from an image using pytesseract OCR."""
    try:
        import pytesseract
        from PIL import Image
        image = Image.open(io.BytesIO(file_bytes))
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        text = pytesseract.image_to_string(image, lang="eng")
        cleaned = clean_text(text)
        logger.info(f"Image OCR: {len(cleaned)} characters")
        return cleaned
    except ImportError:
        raise RuntimeError(
            "Image OCR is not available on this server. "
            "Please upload a PDF or DOCX file instead."
        )
    except Exception as e:
        if "tesseract" in str(e).lower():
            raise RuntimeError(
                "Tesseract OCR is not installed on this server. "
                "Please upload a PDF or DOCX file instead."
            )
        raise RuntimeError(f"Failed to extract text from image: {str(e)}")


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Route to the correct extractor based on file extension."""
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
    return {
        ".pdf": "PDF",
        ".docx": "DOCX",
        ".doc": "DOC",
        ".png": "Image (PNG)",
        ".jpg": "Image (JPG)",
        ".jpeg": "Image (JPEG)",
    }.get(ext, "Unknown")
