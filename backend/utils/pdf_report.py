"""
PDF Report Generator using ReportLab
Generates downloadable PDF reports from AI analysis results
"""

import io
import logging
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

logger = logging.getLogger(__name__)

# Color palette
DARK_BLUE = colors.HexColor("#1e3a5f")
MEDIUM_BLUE = colors.HexColor("#2563eb")
LIGHT_BLUE = colors.HexColor("#dbeafe")
GREEN = colors.HexColor("#16a34a")
YELLOW = colors.HexColor("#d97706")
RED = colors.HexColor("#dc2626")
LIGHT_GRAY = colors.HexColor("#f8fafc")
BORDER_GRAY = colors.HexColor("#e2e8f0")


def _risk_color(risk_level: str):
    mapping = {"Low": GREEN, "Medium": YELLOW, "High": RED}
    return mapping.get(risk_level, YELLOW)


def generate_pdf_report(document: dict) -> bytes:
    """
    Generate a PDF report from a document analysis dict.
    Returns the PDF as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=DARK_BLUE,
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.gray,
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    section_header_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=DARK_BLUE,
        spaceBefore=16,
        spaceAfter=6,
        borderPad=4,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=16,
        spaceAfter=4,
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=styles["Normal"],
        fontSize=10,
        leading=16,
        leftIndent=16,
        spaceAfter=3,
    )

    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    story.append(Paragraph("⚖ Legal Document Analysis Report", title_style))
    story.append(Paragraph("AI-Powered Legal Documentation Assistant", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=DARK_BLUE))
    story.append(Spacer(1, 12))

    # ── Document Info Table ──────────────────────────────────────────────────
    risk_level = document.get("riskLevel", "Medium")
    risk_color = _risk_color(risk_level)
    safe_to_sign = document.get("safeToSign", False)
    created_at = document.get("createdAt", datetime.utcnow())
    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except Exception:
            created_at = datetime.utcnow()

    info_data = [
        ["Document Name", document.get("filename", "N/A")],
        ["Document Type", document.get("documentType", "N/A")],
        ["Analysis Date", created_at.strftime("%B %d, %Y at %H:%M UTC")],
        ["Risk Level", risk_level],
        ["Safe to Sign", "✓ Yes" if safe_to_sign else "✗ No"],
    ]

    info_table = Table(info_data, colWidths=[5 * cm, 12 * cm])
    info_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), LIGHT_BLUE),
                ("TEXTCOLOR", (0, 0), (0, -1), DARK_BLUE),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, LIGHT_GRAY]),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
                ("PADDING", (0, 0), (-1, -1), 8),
                ("TEXTCOLOR", (1, 3), (1, 3), risk_color),
                ("FONTNAME", (1, 3), (1, 3), "Helvetica-Bold"),
                ("TEXTCOLOR", (1, 4), (1, 4), GREEN if safe_to_sign else RED),
                ("FONTNAME", (1, 4), (1, 4), "Helvetica-Bold"),
            ]
        )
    )
    story.append(info_table)
    story.append(Spacer(1, 16))

    # ── Summary ──────────────────────────────────────────────────────────────
    story.append(Paragraph("Document Summary", section_header_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_GRAY))
    story.append(Spacer(1, 6))
    summary = document.get("summary", "No summary available.")
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 8))

    # ── Helper to render list sections ───────────────────────────────────────
    def add_list_section(title: str, items: list, bullet_color=DARK_BLUE):
        if not items:
            return
        story.append(Paragraph(title, section_header_style))
        story.append(HRFlowable(width="100%", thickness=1, color=BORDER_GRAY))
        story.append(Spacer(1, 6))
        for item in items:
            story.append(Paragraph(f"• {item}", bullet_style))
        story.append(Spacer(1, 8))

    # ── Sections ─────────────────────────────────────────────────────────────
    add_list_section("⚠ Warnings", document.get("warnings", []))
    add_list_section("🔍 Suspicious Clauses", document.get("suspiciousClauses", []))
    add_list_section("❌ Missing Clauses", document.get("missingClauses", []))
    add_list_section("💰 Financial & Payment Risks", document.get("financialRisks", []))
    add_list_section("⏰ Expiry & Deadline Risks", document.get("expiryRisks", []))
    add_list_section("⚖ Unfair Conditions", document.get("unfairConditions", []))
    add_list_section("✅ Recommendations", document.get("recommendations", []))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_GRAY))
    story.append(Spacer(1, 8))
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.gray,
        alignment=TA_CENTER,
    )
    story.append(
        Paragraph(
            "This report is generated by AI and is for informational purposes only. "
            "It does not constitute legal advice. Please consult a qualified legal professional.",
            footer_style,
        )
    )
    story.append(
        Paragraph(
            f"Generated on {datetime.utcnow().strftime('%B %d, %Y')} | Legal Documentation Assistant",
            footer_style,
        )
    )

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    logger.info(f"PDF report generated: {len(pdf_bytes)} bytes")
    return pdf_bytes
