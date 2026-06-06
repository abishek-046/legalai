"""
AI Legal Document Analyzer - Enhanced Version
Analyzes documents for legal status, risks, issues, and generates professional reports.
"""

import json
import logging
from openai import AsyncOpenAI
from config import settings

logger = logging.getLogger(__name__)

LEGAL_ANALYSIS_PROMPT = """
You are a senior legal analyst with 20+ years of experience. Analyze the following legal document thoroughly.

Return ONLY a valid JSON object with this EXACT structure (no markdown, no extra text):

{{
  "documentStatus": "Legal" | "Illegal" | "Needs Review",
  "confidenceScore": <integer 0-100>,
  "summary": "<5-10 sentence plain English summary of what this document is about, its purpose, parties involved, and key obligations>",
  "riskLevel": "Low" | "Medium" | "High",
  "riskReason": "<explain why this risk level was assigned, referencing specific clauses>",
  "documentIssues": [
    "<list specific mistakes: missing signatures, missing dates, incomplete terms, ambiguous language, contradictory clauses, invalid references>"
  ],
  "suspiciousClauses": [
    "<each item: specific clause name and why it is suspicious>"
  ],
  "missingClauses": [
    "<each item: name the missing clause and why it matters>"
  ],
  "financialRisks": [
    "<each item: specific financial or payment risk with amount/terms if present>"
  ],
  "expiryRisks": [
    "<each item: specific deadline, expiry date, or time-sensitive obligation>"
  ],
  "unfairConditions": [
    "<each item: specific unfair or one-sided condition>"
  ],
  "complianceIssues": [
    "<each item: specific legal compliance or regulatory issue>"
  ],
  "privacyRisks": [
    "<each item: data privacy or personal information risk>"
  ],
  "legalLoopholes": [
    "<each item: specific legal loophole or exploitable ambiguity>"
  ],
  "warnings": [
    "<each item: important general warning about this document>"
  ],
  "recommendations": [
    "<each item: specific actionable recommendation to improve this document>"
  ],
  "finalVerdict": "<2-4 sentence professional conclusion: should the user proceed, modify, or seek legal review? Be specific and direct.>",
  "safeToSign": <true | false>
}}

IMPORTANT RULES:
- documentStatus: "Legal" = valid and enforceable; "Illegal" = contains illegal terms; "Needs Review" = uncertain or risky
- confidenceScore: your confidence in the analysis (0-100)
- Every list must have at least 1 item if applicable, or [] if truly not applicable
- Be specific — reference actual text from the document, not generic statements
- safeToSign: true ONLY if documentStatus is Legal AND riskLevel is Low
- Do NOT use phrases like "Demo mode" or "would appear here"
- Always generate REAL analysis from the actual document content

Document to analyze:
{text}
"""


async def analyze_legal_document(extracted_text: str) -> dict:
    """Analyze a legal document using OpenAI and return structured results."""
    key = (settings.OPENAI_API_KEY or "").strip()

    if not key or key.startswith("sk-your") or key == "demo" or len(key) < 20:
        logger.warning("OpenAI API key not configured")
        return _no_key_response()

    # Limit text — Render free tier has 30s request timeout
    # Keep only 2000 chars for fast reliable analysis under timeout
    text = extracted_text[:2000] if len(extracted_text) > 2000 else extracted_text

    try:
        client = AsyncOpenAI(api_key=key, timeout=20.0)

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior legal analyst. "
                        "Always respond with a single valid JSON object only. "
                        "No markdown, no code blocks, no explanation outside JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": LEGAL_ANALYSIS_PROMPT.format(text=text),
                },
            ],
            temperature=0.2,
            max_tokens=1500,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content
        analysis = json.loads(raw)
        logger.info(f"AI analysis complete — status: {analysis.get('documentStatus')}, risk: {analysis.get('riskLevel')}")
        return _validate(analysis)

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return _no_key_response()
    except Exception as e:
        logger.error(f"OpenAI error: {type(e).__name__}: {e}")
        raise


def _validate(a: dict) -> dict:
    """Ensure all required fields exist with correct types."""
    list_fields = [
        "documentIssues", "suspiciousClauses", "missingClauses",
        "financialRisks", "expiryRisks", "unfairConditions",
        "complianceIssues", "privacyRisks", "legalLoopholes",
        "warnings", "recommendations",
    ]
    defaults = {
        "documentStatus": "Needs Review",
        "confidenceScore": 70,
        "summary": "Document analysis completed.",
        "riskLevel": "Medium",
        "riskReason": "Analysis completed with standard risk assessment.",
        "finalVerdict": "Please review this document carefully before proceeding.",
        "safeToSign": False,
        **{f: [] for f in list_fields},
    }

    for key, default in defaults.items():
        if key not in a or a[key] is None:
            a[key] = default

    # Ensure lists
    for f in list_fields:
        if not isinstance(a[f], list):
            a[f] = [str(a[f])] if a[f] else []

    # Normalize enums
    if a["documentStatus"] not in ["Legal", "Illegal", "Needs Review"]:
        a["documentStatus"] = "Needs Review"
    if a["riskLevel"] not in ["Low", "Medium", "High"]:
        a["riskLevel"] = "Medium"
    if not isinstance(a["confidenceScore"], int):
        try:
            a["confidenceScore"] = int(a["confidenceScore"])
        except Exception:
            a["confidenceScore"] = 70
    a["confidenceScore"] = max(0, min(100, a["confidenceScore"]))

    return a


def _no_key_response() -> dict:
    """Response when OpenAI key is not configured."""
    return {
        "documentStatus": "Needs Review",
        "confidenceScore": 0,
        "summary": (
            "OpenAI API key is not configured. "
            "Please add your OPENAI_API_KEY in the Render environment variables. "
            "Without a valid API key, real AI analysis cannot be performed."
        ),
        "riskLevel": "Medium",
        "riskReason": "Cannot assess risk without AI analysis. Configure your OpenAI API key.",
        "documentIssues": ["OpenAI API key not configured — real analysis unavailable"],
        "suspiciousClauses": [],
        "missingClauses": [],
        "financialRisks": [],
        "expiryRisks": [],
        "unfairConditions": [],
        "complianceIssues": [],
        "privacyRisks": [],
        "legalLoopholes": [],
        "warnings": [
            "AI analysis is disabled. Configure OPENAI_API_KEY on Render to enable real analysis."
        ],
        "recommendations": [
            "Go to Render → Environment → add OPENAI_API_KEY with your OpenAI key",
            "Get a key at https://platform.openai.com/api-keys",
        ],
        "finalVerdict": (
            "Analysis could not be performed. "
            "Please configure the OpenAI API key and re-upload the document."
        ),
        "safeToSign": False,
    }
