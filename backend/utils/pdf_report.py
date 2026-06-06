"""
PDF Report Generator - Enhanced Version with full analysis sections
"""

import io
import logging
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT

logger = logging.getLogger(__name__)

# Colors
DARK = colors.HexColor("#040d18")
GOLD = colors.HexColor("#f59e0b")
GOLD_LIGHT = colors.HexColor("#fbbf24")
WHITE = colors.white
GREEN = colors.HexColor("#16a34a")
YELLOW = colors.HexColor("#d97706")
RED = colors.HexColor("#dc2626")
ORANGE = colors.HexColor("#ea580c")
BLUE = colors.HexColor("#0ea5e9")
PURPLE = colors.HexColor("#9333ea")
GRAY = colors.HexColor("#94a3b8")
DARK_GRAY = colors.HexColor("#1e293b")


def _status_color(status):
    return {"Legal": GREEN, "Illegal": RED, "Needs Review": YELLOW}.get(status, YELLOW)


def _risk_color(risk):
    return {"Low": GREEN, "Medium": YELLOW, "High": RED}.get(risk, YELLOW)


def generate_pdf_report(document: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("Title", parent=styles["Title"],
        fontSize=20, textColor=GOLD, spaceAfter=4, alignment=TA_CENTER)
    sub_style = ParagraphStyle("Sub", parent=styles["Normal"],
        fontSize=10, textColor=GRAY, alignment=TA_CENTER, spaceAfter=16)
    divider_style = ParagraphStyle("Divider", parent=styles["Normal"],
        fontSize=9, textColor=GOLD, alignment=TA_CENTER, spaceBefore=14, spaceAfter=8,
        fontName="Helvetica-Bold")
    section_style = ParagraphStyle("Section", parent=styles["Heading2"],
        fontSize=12, textColor=WHITE, spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle("Body", parent=styles["Normal"],
        fontSize=10, leading=15, textColor=colors.HexColor("#cbd5e1"), spaceAfter=4)
    bullet_style = ParagraphStyle("Bullet", parent=styles["Normal"],
        fontSize=10, leading=15, leftIndent=14, textColor=colors.HexColor("#cbd5e1"), spaceAfter=3)

    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph("⚖ Legal Document Analysis Report", title_style))
    story.append(Paragraph("AI-Powered Legal Documentation Assistant", sub_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=GOLD))
    story.append(Spacer(1, 10))

    # ── Document Info ─────────────────────────────────────────────────────────
    status = document.get("documentStatus", "Needs Review")
    risk = document.get("riskLevel", "Medium")
    confidence = document.get("confidenceScore", 0)
    safe = document.get("safeToSign", False)
    created = document.get("createdAt", datetime.utcnow())
    if isinstance(created, str):
        try:
            created = datetime.fromisoformat(created.replace("Z", "+00:00"))
        except Exception:
            created = datetime.utcnow()

    info_data = [
        ["Document", document.get("filename", "N/A")],
        ["Type", document.get("documentType", "N/A")],
        ["Analyzed", created.strftime("%B %d, %Y at %H:%M UTC")],
        ["Document Status", status],
        ["Confidence Score", f"{confidence}%"],
        ["Risk Level", risk],
        ["Safe to Sign", "YES ✓" if safe else "NO — Review Required ✗"],
    ]
    info_table = Table(info_data, colWidths=[4.5*cm, 12.5*cm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), DARK_GRAY),
        ("TEXTCOLOR", (0, 0), (0, -1), GOLD_LIGHT),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (1, 0), (1, -1), WHITE),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#334155")),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("TEXTCOLOR", (1, 3), (1, 3), _status_color(status)),
        ("FONTNAME", (1, 3), (1, 3), "Helvetica-Bold"),
        ("TEXTCOLOR", (1, 5), (1, 5), _risk_color(risk)),
        ("FONTNAME", (1, 5), (1, 5), "Helvetica-Bold"),
        ("TEXTCOLOR", (1, 6), (1, 6), GREEN if safe else RED),
        ("FONTNAME", (1, 6), (1, 6), "Helvetica-Bold"),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10))

    def add_divider(title):
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#334155")))
        story.append(Paragraph(f"─── {title} ───", divider_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#334155")))
        story.append(Spacer(1, 6))

    def add_list(items, numbered=True):
        for i, item in enumerate(items or []):
            prefix = f"{i+1}." if numbered else "•"
            story.append(Paragraph(f"{prefix}  {item}", bullet_style))

    # ── Summary ───────────────────────────────────────────────────────────────
    add_divider("SIMPLE SUMMARY")
    story.append(Paragraph(document.get("summary", "No summary available."), body_style))
    story.append(Spacer(1, 8))

    # ── Risk ──────────────────────────────────────────────────────────────────
    add_divider("RISK LEVEL")
    story.append(Paragraph(f"<b>Level:</b> {risk}", body_style))
    if document.get("riskReason"):
        story.append(Paragraph(f"<b>Reason:</b> {document['riskReason']}", body_style))
    story.append(Spacer(1, 8))

    # ── Issues ────────────────────────────────────────────────────────────────
    sections = [
        ("DOCUMENT ISSUES FOUND", "documentIssues"),
        ("SUSPICIOUS CLAUSES", "suspiciousClauses"),
        ("MISSING CLAUSES", "missingClauses"),
        ("FINANCIAL RISKS", "financialRisks"),
        ("EXPIRY & DEADLINE RISKS", "expiryRisks"),
        ("UNFAIR CONDITIONS", "unfairConditions"),
        ("COMPLIANCE ISSUES", "complianceIssues"),
        ("PRIVACY RISKS", "privacyRisks"),
        ("LEGAL LOOPHOLES", "legalLoopholes"),
        ("IMPORTANT WARNINGS", "warnings"),
        ("RECOMMENDATIONS", "recommendations"),
    ]

    for title, key in sections:
        items = document.get(key, [])
        if items:
            add_divider(title)
            add_list(items)
            story.append(Spacer(1, 6))

    # ── Final Verdict ─────────────────────────────────────────────────────────
    add_divider("FINAL VERDICT")
    verdict = document.get("finalVerdict") or "Please review this document carefully."
    story.append(Paragraph(verdict, body_style))
    story.append(Spacer(1, 16))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#334155")))
    footer = ParagraphStyle("Footer", parent=styles["Normal"],
        fontSize=8, textColor=GRAY, alignment=TA_CENTER)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "This report is AI-generated and for informational purposes only. "
        "It does not constitute legal advice. Consult a qualified legal professional.",
        footer))
    story.append(Paragraph(
        f"Generated on {datetime.utcnow().strftime('%B %d, %Y')} | LegalAI",
        footer))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    logger.info(f"PDF generated: {len(pdf)} bytes")
    return pdf
