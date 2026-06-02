"""
OCR and document text extraction utilities

Extraction pipeline:
- PDF (text-based)  → pdfplumber  → fast direct extraction
- PDF (scanned)     → PyMuPDF     → render page as image → extract text blocks
- DOCX / DOC        → python-docx → paragraph + table extraction
- Images (PNG/JPG/WEBP/BMP/TIFF) → PyMuPDF or pytesseract (fallback)
"""

import io
import logging
import re
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)

# Minimum characters to consider a page "text-based"
TEXT_PAGE_THRESHOLD = 30
# Minimum total characters to consider PDF extraction successful
PDF_MIN_CHARS = 100


def clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    if not text:
        return ""
    # Collapse whitespace
    text = re.sub(r"[ \t]+", " ", text)
    # Remove non-printable characters except newline
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ─── PDF Extraction ────────────────────────────────────────────────────────────

def _is_text_page(page_text: str) -> bool:
    """Return True if a page has enough selectable text."""
    return bool(page_text) and len(page_text.strip()) >= TEXT_PAGE_THRESHOLD


def _extract_pdf_pdfplumber(file_bytes: bytes) -> Tuple[str, int, int]:
    """
    Extract text from a PDF using pdfplumber.
    Returns (text, text_pages, total_pages).
    """
    try:
        import pdfplumber
        parts = []
        text_pages = 0
        total_pages = 0

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            total_pages = len(pdf.pages)
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if _is_text_page(page_text):
                    parts.append(page_text)
                    text_pages += 1

        return "\n\n".join(parts), text_pages, total_pages

    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}")
        return "", 0, 0


def _extract_pdf_pymupdf_text(file_bytes: bytes) -> Tuple[str, int, int]:
    """
    Extract text from a PDF using PyMuPDF's built-in text layer.
    Returns (text, text_pages, total_pages).
    """
    try:
        import fitz
        parts = []
        text_pages = 0
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        total_pages = len(doc)

        for page in doc:
            page_text = page.get_text("text") or ""
            if _is_text_page(page_text):
                parts.append(page_text.strip())
                text_pages += 1

        doc.close()
        return "\n\n".join(parts), text_pages, total_pages

    except Exception as e:
        logger.warning(f"PyMuPDF text extraction failed: {e}")
        return "", 0, 0


def _extract_pdf_pymupdf_ocr(file_bytes: bytes) -> str:
    """
    Extract text from a scanned PDF by rendering each page as an image
    and extracting text from the rendered image using PyMuPDF's textpage.
    Works for most scanned PDFs without requiring Tesseract.
    """
    try:
        import fitz
        parts = []
        doc = fitz.open(stream=file_bytes, filetype="pdf")

        for page_num, page in enumerate(doc):
            # Render page at 2x resolution for better OCR accuracy
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)

            # Convert pixmap to PNG bytes then back to fitz image for text extraction
            img_bytes = pix.tobytes("png")

            # Open as image document and extract text
            img_doc = fitz.open(stream=img_bytes, filetype="png")
            if img_doc.page_count > 0:
                img_page = img_doc[0]
                # Use textpage with OCR flag if available (PyMuPDF >= 1.21)
                try:
                    tp = img_page.get_textpage_ocr(flags=0, language="eng", dpi=300)
                    text = img_page.get_text(textpage=tp)
                except AttributeError:
                    # Fallback: extract whatever text blocks are embedded
                    text = img_page.get_text("text")

                if text and text.strip():
                    parts.append(text.strip())
            img_doc.close()

            logger.debug(f"Scanned page {page_num + 1}/{len(doc)} processed")

        doc.close()
        result = "\n\n".join(parts)
        logger.info(f"PyMuPDF scanned OCR: {len(result)} characters from {len(parts)} pages")
        return result

    except Exception as e:
        logger.error(f"PyMuPDF scanned OCR failed: {e}")
        return ""


def extract_from_pdf(file_bytes: bytes) -> str:
    """
    Smart PDF text extraction:
    1. Try pdfplumber (fast, accurate for text PDFs)
    2. Try PyMuPDF text layer
    3. Fall back to PyMuPDF scanned OCR for image-based PDFs
    """
    logger.info(f"Processing PDF ({len(file_bytes)} bytes)")

    # Step 1: pdfplumber
    text, text_pages, total_pages = _extract_pdf_pdfplumber(file_bytes)
    if len(text.strip()) >= PDF_MIN_CHARS:
        logger.info(f"pdfplumber success: {len(text)} chars, {text_pages}/{total_pages} text pages")
        return clean_text(text)

    # Step 2: PyMuPDF text layer
    logger.info("pdfplumber insufficient — trying PyMuPDF text layer")
    text2, text_pages2, total_pages2 = _extract_pdf_pymupdf_text(file_bytes)
    if len(text2.strip()) >= PDF_MIN_CHARS:
        logger.info(f"PyMuPDF text layer success: {len(text2)} chars")
        return clean_text(text2)

    # Step 3: Scanned PDF OCR
    logger.info("PDF appears to be scanned — running PyMuPDF OCR")
    text3 = _extract_pdf_pymupdf_ocr(file_bytes)
    if text3.strip():
        logger.info(f"PyMuPDF OCR success: {len(text3)} chars")
        return clean_text(text3)

    logger.warning("All PDF extraction methods returned insufficient text")
    return clean_text(text or text2 or text3)


# ─── DOCX Extraction ──────────────────────────────────────────────────────────

def extract_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        parts = []

        for para in doc.paragraphs:
            if para.text.strip():
                parts.append(para.text.strip())

        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(
                    c.text.strip() for c in row.cells if c.text.strip()
                )
                if row_text:
                    parts.append(row_text)

        result = clean_text("\n".join(parts))
        logger.info(f"DOCX extraction: {len(result)} characters")
        return result

    except ImportError:
        raise RuntimeError("DOCX processing library not available")
    except Exception as e:
        logger.error(f"DOCX extraction failed: {e}")
        raise RuntimeError(f"Failed to extract text from DOCX: {str(e)}")


# ─── Image Extraction ─────────────────────────────────────────────────────────

def _extract_image_pymupdf(file_bytes: bytes, ext: str) -> str:
    """Extract text from an image using PyMuPDF's OCR capability."""
    try:
        import fitz

        # Map extension to fitz filetype
        ftype_map = {
            ".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg",
            ".bmp": "bmp", ".tiff": "tiff", ".tif": "tiff",
            ".webp": "webp",
        }
        ftype = ftype_map.get(ext, "png")

        doc = fitz.open(stream=file_bytes, filetype=ftype)
        parts = []

        for page in doc:
            try:
                tp = page.get_textpage_ocr(flags=0, language="eng", dpi=300)
                text = page.get_text(textpage=tp)
            except AttributeError:
                text = page.get_text("text")

            if text and text.strip():
                parts.append(text.strip())

        doc.close()
        result = "\n\n".join(parts)
        logger.info(f"PyMuPDF image OCR: {len(result)} characters")
        return result

    except Exception as e:
        logger.warning(f"PyMuPDF image OCR failed: {e}")
        return ""


def _extract_image_pytesseract(file_bytes: bytes) -> str:
    """Extract text from an image using pytesseract (requires Tesseract binary)."""
    try:
        import pytesseract
        from PIL import Image

        image = Image.open(io.BytesIO(file_bytes))
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        text = pytesseract.image_to_string(image, lang="eng")
        result = clean_text(text)
        logger.info(f"pytesseract OCR: {len(result)} characters")
        return result

    except ImportError:
        logger.warning("pytesseract not installed")
        return ""
    except Exception as e:
        if "tesseract" in str(e).lower():
            logger.warning("Tesseract binary not found")
            return ""
        logger.error(f"pytesseract failed: {e}")
        return ""


def extract_from_image(file_bytes: bytes, ext: str = ".jpg") -> str:
    """
    Extract text from an image file.
    Tries PyMuPDF OCR first, then pytesseract as fallback.
    """
    logger.info(f"Processing image ({ext}, {len(file_bytes)} bytes)")

    # Try PyMuPDF first (no system dependency)
    text = _extract_image_pymupdf(file_bytes, ext)
    if text.strip():
        return clean_text(text)

    # Fallback: pytesseract
    logger.info("PyMuPDF image OCR insufficient — trying pytesseract")
    text2 = _extract_image_pytesseract(file_bytes)
    if text2.strip():
        return text2

    raise RuntimeError(
        "Could not extract text from this image. "
        "Please ensure the image contains clear, readable text."
    )


# ─── Main Entry Point ─────────────────────────────────────────────────────────

def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Route to the correct extractor based on file extension.
    Raises ValueError for unsupported types, RuntimeError for extraction failures.
    """
    ext = Path(filename).suffix.lower()

    if not file_bytes:
        raise ValueError("File is empty")

    if ext == ".pdf":
        return extract_from_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        return extract_from_docx(file_bytes)
    elif ext in (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"):
        return extract_from_image(file_bytes, ext)
    else:
        raise ValueError(
            f"Unsupported file type: '{ext}'. "
            "Supported: PDF, DOCX, DOC, PNG, JPG, JPEG, WEBP, BMP, TIFF"
        )


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
        ".webp": "Image (WEBP)",
        ".bmp": "Image (BMP)",
        ".tiff": "Image (TIFF)",
        ".tif": "Image (TIFF)",
    }.get(ext, "Unknown")
