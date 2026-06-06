"""
AI Legal Document Analyzer using Groq (free)
Model: llama3-70b-8192
Get your free API key at: https://console.groq.com
"""

import json
import re
import logging
from config import settings

logger = logging.getLogger(__name__)

PROMPT = """You are a senior legal analyst with 20 years of experience. Analyze the legal document below.

Return ONLY a valid JSON object. No markdown, no code blocks, no explanation outside the JSON.

{{
  "documentStatus": "Legal" or "Illegal" or "Needs Review",
  "confidenceScore": <integer 0-100>,
  "summary": "<5-8 sentence plain English summary of this document, its purpose, parties, and key obligations>",
  "riskLevel": "Low" or "Medium" or "High",
  "riskReason": "<explain why this risk level, referencing specific clauses>",
  "documentIssues": ["<issue 1>", "<issue 2>"],
  "suspiciousClauses": ["<clause 1>", "<clause 2>"],
  "missingClauses": ["<missing 1>", "<missing 2>"],
  "financialRisks": ["<risk 1>"],
  "expiryRisks": ["<deadline 1>"],
  "unfairConditions": ["<unfair condition 1>"],
  "complianceIssues": ["<compliance 1>"],
  "privacyRisks": ["<privacy risk 1>"],
  "legalLoopholes": ["<loophole 1>"],
  "warnings": ["<warning 1>", "<warning 2>"],
  "recommendations": ["<recommendation 1>", "<recommendation 2>", "<recommendation 3>"],
  "finalVerdict": "<2-3 sentence professional conclusion>",
  "safeToSign": <true or false>
}}

Rules:
- Reference actual content from the document
- safeToSign is true ONLY if documentStatus is "Legal" AND riskLevel is "Low"
- Use plain English
- Every array must have at least 1 real item if applicable

Document:
{text}"""


async def analyze_legal_document(extracted_text: str) -> dict:
    """Analyze legal document using available AI key."""
    import os

    # Check all possible env var names for Groq
    groq_key = (
        os.environ.get("GROQ_API_KEY", "") or
        os.environ.get("GROQ_KEY", "") or
        os.environ.get("groq_api_key", "") or
        ""
    ).strip()
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()

    logger.info(f"ENV CHECK — GROQ_API_KEY: {'SET' if groq_key else 'NOT SET'}, all keys with GROQ: {[k for k in os.environ if 'GROQ' in k.upper()]}")

    # Try Groq
    if groq_key and len(groq_key) > 10:
        try:
            return await _analyze_groq(extracted_text, groq_key)
        except Exception as e:
            logger.error(f"Groq failed: {e}")

    # Use OpenAI
    if openai_key and len(openai_key) > 10:
        try:
            return await _analyze_openai(extracted_text, openai_key)
        except Exception as e:
            logger.error(f"OpenAI failed: {type(e).__name__}: {e}")
            # Return error details instead of generic message
            return _error_response(str(e))

    return _no_key_response()


async def _analyze_groq(extracted_text: str, key: str) -> dict:
    from groq import Groq
    client = Groq(api_key=key)
    text = extracted_text[:5000] if len(extracted_text) > 5000 else extracted_text
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a senior legal analyst. Respond with valid JSON only. No markdown."},
            {"role": "user", "content": PROMPT.format(text=text)}
        ],
        temperature=0.2,
        max_tokens=2000,
    )
    raw = response.choices[0].message.content.strip()
    result = _parse(raw)
    if result:
        logger.info(f"Groq OK — {result.get('documentStatus')} / {result.get('riskLevel')}")
        return result
    raise ValueError("Groq returned unparseable JSON")


async def _analyze_openai(extracted_text: str, key: str) -> dict:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=key, timeout=25.0)
    text = extracted_text[:3000] if len(extracted_text) > 3000 else extracted_text
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a senior legal analyst. Respond with valid JSON only."},
            {"role": "user", "content": PROMPT.format(text=text)},
        ],
        temperature=0.2,
        max_tokens=2000,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    result = _parse(raw)
    if result:
        logger.info(f"OpenAI OK — {result.get('documentStatus')} / {result.get('riskLevel')}")
        return result
    raise ValueError("OpenAI returned unparseable JSON")


def _parse(raw: str) -> dict:
    """Extract and validate JSON from Groq response."""
    try:
        cleaned = raw.strip()

        # Strip markdown code blocks
        if "```" in cleaned:
            cleaned = re.sub(r"```(?:json)?\n?", "", cleaned).strip()

        # Find JSON object
        if not cleaned.startswith("{"):
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                cleaned = match.group()

        analysis = json.loads(cleaned)
        return _validate(analysis)

    except Exception as e:
        logger.error(f"Parse failed: {e} | raw[:100]: {raw[:100]}")
        return None


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
        "confidenceScore": 75,
        "summary": "Analysis completed.",
        "riskLevel": "Medium",
        "riskReason": "Standard assessment applied.",
        "finalVerdict": "Please review this document carefully.",
        "safeToSign": False,
        **{f: [] for f in list_fields},
    }

    for k, v in defaults.items():
        if k not in a or a[k] is None:
            a[k] = v

    for f in list_fields:
        if not isinstance(a[f], list):
            a[f] = [str(a[f])] if a[f] else []

    if a["documentStatus"] not in ["Legal", "Illegal", "Needs Review"]:
        a["documentStatus"] = "Needs Review"
    if a["riskLevel"] not in ["Low", "Medium", "High"]:
        a["riskLevel"] = "Medium"
    try:
        a["confidenceScore"] = max(0, min(100, int(a["confidenceScore"])))
    except Exception:
        a["confidenceScore"] = 75

    return a


def _error_response(error_detail: str) -> dict:
    return {**_no_key_response(),
        "summary": f"AI analysis failed: {error_detail[:200]}",
        "documentIssues": [f"AI error: {error_detail[:200]}"],
    }


def _no_key_response() -> dict:
    return {
        "documentStatus": "Needs Review",
        "confidenceScore": 0,
        "summary": (
            "AI analysis is not available. "
            "Add your free GROQ_API_KEY on Render to enable analysis. "
            "Get a free key at https://console.groq.com"
        ),
        "riskLevel": "Medium",
        "riskReason": "Cannot assess without AI. Add GROQ_API_KEY on Render.",
        "documentIssues": ["GROQ_API_KEY not configured on Render"],
        "suspiciousClauses": [],
        "missingClauses": [],
        "financialRisks": [],
        "expiryRisks": [],
        "unfairConditions": [],
        "complianceIssues": [],
        "privacyRisks": [],
        "legalLoopholes": [],
        "warnings": ["Add GROQ_API_KEY on Render to enable free AI analysis"],
        "recommendations": [
            "Get free API key at https://console.groq.com",
            "Add GROQ_API_KEY to Render environment variables",
            "Redeploy after adding the key",
        ],
        "finalVerdict": "Configure GROQ_API_KEY on Render to enable free AI analysis.",
        "safeToSign": False,
    }
