"""
AI Legal Document Analyzer using OpenAI API
Generates structured legal analysis from extracted document text
"""

import json
import logging
from typing import Optional

from openai import AsyncOpenAI
from config import settings

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

LEGAL_ANALYSIS_PROMPT = """
You are an expert legal analyst. Analyze the following legal document text and provide a comprehensive analysis.

Return your response as a valid JSON object with EXACTLY this structure:
{{
  "summary": "A clear, simple English summary of what this document is about (2-4 sentences)",
  "riskLevel": "Low" | "Medium" | "High",
  "warnings": ["list of general warnings about this document"],
  "suspiciousClauses": ["list of specific suspicious or concerning clauses found in the text"],
  "missingClauses": ["list of important clauses that are missing from this document"],
  "financialRisks": ["list of financial or payment-related risks"],
  "expiryRisks": ["list of expiry, deadline, or time-sensitive risks"],
  "unfairConditions": ["list of unfair or one-sided conditions"],
  "recommendations": ["list of actionable recommendations for the user"],
  "safeToSign": true | false
}}

Guidelines:
- riskLevel: "Low" if document is standard and fair, "Medium" if some concerns exist, "High" if major risks found
- safeToSign: true only if riskLevel is Low and no major issues found
- Be specific and reference actual content from the document
- Use plain English that a non-lawyer can understand
- Each list should have 1-5 items (empty array [] if none found)
- Do NOT include any text outside the JSON object

Document text to analyze:
{text}
"""


async def analyze_legal_document(extracted_text: str) -> dict:
    """
    Send extracted document text to OpenAI and return structured analysis.
    Falls back to a mock analysis if OpenAI API key is not configured.
    """
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("sk-your"):
        logger.warning("OpenAI API key not configured - returning mock analysis")
        return _mock_analysis(extracted_text)

    # Truncate text to avoid token limits (keep first 6000 chars)
    text_to_analyze = extracted_text[:6000] if len(extracted_text) > 6000 else extracted_text

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert legal analyst. Always respond with valid JSON only.",
                },
                {
                    "role": "user",
                    "content": LEGAL_ANALYSIS_PROMPT.format(text=text_to_analyze),
                },
            ],
            temperature=0.3,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content
        analysis = json.loads(raw)
        logger.info("AI analysis completed successfully")
        return _validate_analysis(analysis)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        return _mock_analysis(extracted_text)
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise


def _validate_analysis(analysis: dict) -> dict:
    """Ensure all required fields exist with correct types."""
    defaults = {
        "summary": "Document analysis completed.",
        "riskLevel": "Medium",
        "warnings": [],
        "suspiciousClauses": [],
        "missingClauses": [],
        "financialRisks": [],
        "expiryRisks": [],
        "unfairConditions": [],
        "recommendations": [],
        "safeToSign": False,
    }
    for key, default in defaults.items():
        if key not in analysis:
            analysis[key] = default
        # Ensure lists are actually lists
        if isinstance(default, list) and not isinstance(analysis[key], list):
            analysis[key] = [str(analysis[key])] if analysis[key] else []

    # Normalize riskLevel
    if analysis["riskLevel"] not in ["Low", "Medium", "High"]:
        analysis["riskLevel"] = "Medium"

    return analysis


def _mock_analysis(text: str) -> dict:
    """
    Return a mock analysis when OpenAI is not configured.
    Useful for development and testing.
    """
    word_count = len(text.split())
    risk = "Low" if word_count < 200 else ("Medium" if word_count < 500 else "High")

    return {
        "summary": (
            "This document has been processed and analyzed. "
            "Please configure your OpenAI API key for a real AI-powered analysis. "
            f"The document contains approximately {word_count} words."
        ),
        "riskLevel": risk,
        "warnings": [
            "OpenAI API key not configured - this is a demo analysis",
            "Please review this document with a qualified legal professional",
        ],
        "suspiciousClauses": [
            "Demo mode: Suspicious clauses would appear here with a real API key"
        ],
        "missingClauses": [
            "Demo mode: Missing clauses would be identified here"
        ],
        "financialRisks": [
            "Demo mode: Financial risks would be analyzed here"
        ],
        "expiryRisks": [
            "Demo mode: Expiry and deadline risks would appear here"
        ],
        "unfairConditions": [
            "Demo mode: Unfair conditions would be flagged here"
        ],
        "recommendations": [
            "Configure your OpenAI API key in the .env file",
            "Consult a qualified legal professional before signing any document",
            "Review all clauses carefully before proceeding",
        ],
        "safeToSign": False,
    }
