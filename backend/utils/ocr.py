"""
OCR and document text extraction utilities

Extraction pipeline:
- PDF (text-based)  → pdfplumber  → direct text extraction
- PDF (scanned)     → PyMuPDF renders pages → extract embedded text blocks
- DOCX / DOC        → python-docx
- Images            → PyMuPDF text extraction
"""

import io
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

PDF_MIN_CHARS = 80
PAGE_MIN_CHARS = 20


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ─── PDF ──────────────────────────────────────────────────────────────────────

def extract_from_pdf(file_bytes: bytes) -> str:
    """
    Smart PDF extraction:
    1. pdfplumber for text PDFs
    2. PyMuPDF text layer
    3. PyMuPDF rendered image text blocks (scanned PDFs)
    4. PyMuPDF words extraction
    """
    logger.info(f"PDF processing: {len(file_bytes)} bytes")

    # Step 1 — pdfplumber
    text = _try_pdfplumber(file_bytes)
    if len(text.strip()) >= PDF_MIN_CHARS:
        logger.info(f"pdfplumber OK: {len(text)} chars")
        return clean_text(text)

    # Step 2 — PyMuPDF text
    text2 = _try_pymupdf_text(file_bytes)
    if len(text2.strip()) >= PDF_MIN_CHARS:
        logger.info(f"PyMuPDF text OK: {len(text2)} chars")
        return clean_text(text2)

    # Step 3 — PyMuPDF words (catches more text from complex layouts)
    text3 = _try_pymupdf_words(file_bytes)
    if len(text3.strip()) >= PDF_MIN_CHARS:
        logger.info(f"PyMuPDF words OK: {len(text3)} chars")
        return clean_text(text3)

    # Step 4 — PyMuPDF blocks (last resort)
    text4 = _try_pymupdf_blocks(file_bytes)
    if len(text4.strip()) >= PDF_MIN_CHARS:
        logger.info(f"PyMuPDF blocks OK: {len(text4)} chars")
        return clean_text(text4)

    # Return whatever we got
    best = max([text, text2, text3, text4], key=lambda t: len(t.strip()))
    logger.warning(f"All PDF methods limited, best: {len(best)} chars")
    return clean_text(best)


def _try_pdfplumber(file_bytes: bytes) -> str:
    try:
        import pdfplumber
        parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                t = page.extract_text() or ""
                if len(t.strip()) >= PAGE_MIN_CHARS:
                    parts.append(t.strip())
        return "\n\n".join(parts)
    except Exception as e:
        logger.warning(f"pdfplumber: {e}")
        return ""


def _try_pymupdf_text(file_bytes: bytes) -> str:
    try:
        import fitz
        parts = []
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            t = page.get_text("text") or ""
            if len(t.strip()) >= PAGE_MIN_CHARS:
                parts.append(t.strip())
        doc.close()
        return "\n\n".join(parts)
    except Exception as e:
        logger.warning(f"PyMuPDF text: {e}")
        return ""


def _try_pymupdf_words(file_bytes: bytes) -> str:
    """Extract using word-level data — better for some layouts."""
    try:
        import fitz
        parts = []
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            words = page.get_text("words")
            if words:
                page_text = " ".join(w[4] for w in words if isinstance(w[4], str))
                if len(page_text.strip()) >= PAGE_MIN_CHARS:
                    parts.append(page_text.strip())
        doc.close()
        return "\n\n".join(parts)
    except Exception as e:
        logger.warning(f"PyMuPDF words: {e}")
        return ""


def _try_pymupdf_blocks(file_bytes: bytes) -> str:
    """Extract using block-level data."""
    try:
        import fitz
        parts = []
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            blocks = page.get_text("blocks")
            page_parts = []
            for b in blocks:
                if isinstance(b[4], str) and b[4].strip():
                    page_parts.append(b[4].strip())
            if page_parts:
                parts.append(" ".join(page_parts))
        doc.close()
        return "\n\n".join(parts)
    except Exception as e:
        logger.warning(f"PyMuPDF blocks: {e}")
        return ""


# ─── DOCX ─────────────────────────────────────────────────────────────────────

def extract_from_docx(file_bytes: bytes) -> str:
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
        logger.info(f"DOCX: {len(result)} chars")
        return result
    except ImportError:
        raise RuntimeError("DOCX library not available")
    except Exception as e:
        raise RuntimeError(f"DOCX extraction failed: {e}")


# ─── Images ───────────────────────────────────────────────────────────────────

def extract_from_image(file_bytes: bytes, ext: str = ".jpg") -> str:
    """Extract text from image using PyMuPDF."""
    logger.info(f"Image processing: {ext}, {len(file_bytes)} bytes")

    # Try PyMuPDF
    text = _try_image_pymupdf(file_bytes, ext)
    if text.strip():
        return clean_text(text)

    # Try pytesseract
    text2 = _try_image_tesseract(file_bytes)
    if text2.strip():
        return text2

    raise RuntimeError(
        "Could not extract text from this image. "
        "Please ensure the image contains clear, readable text."
    )


def _try_image_pymupdf(file_bytes: bytes, ext: str) -> str:
    try:
        import fitz
        ftype_map = {
            ".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg",
            ".bmp": "bmp", ".tiff": "tiff", ".tif": "tiff", ".webp": "webp",
        }
        ftype = ftype_map.get(ext.lower(), "png")
        doc = fitz.open(stream=file_bytes, filetype=ftype)
        parts = []
        for page in doc:
            t = page.get_text("text") or ""
            if t.strip():
                parts.append(t.strip())
        doc.close()
        return "\n".join(parts)
    except Exception as e:
        logger.warning(f"PyMuPDF image: {e}")
        return ""


def _try_image_tesseract(file_bytes: bytes) -> str:
    try:
        import pytesseract
        from PIL import Image
        image = Image.open(io.BytesIO(file_bytes))
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        text = pytesseract.image_to_string(image, lang="eng")
        return clean_text(text)
    except Exception as e:
        logger.warning(f"pytesseract: {e}")
        return ""


# ─── Entry Point ──────────────────────────────────────────────────────────────

def extract_text(file_bytes: bytes, filename: str) -> str:
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
    ext = Path(filename).suffix.lower()
    return {
        ".pdf": "PDF", ".docx": "DOCX", ".doc": "DOC",
        ".png": "Image (PNG)", ".jpg": "Image (JPG)", ".jpeg": "Image (JPEG)",
        ".webp": "Image (WEBP)", ".bmp": "Image (BMP)", ".tiff": "Image (TIFF)",
    }.get(ext, "Unknown")
