"""
AI Legal Document Analyzer
Uses Google Gemini (free tier) with OpenAI as fallback.
Get free Gemini key at: https://aistudio.google.com/apikey
"""

import json
import logging
from config import settings

logger = logging.getLogger(__name__)

PROMPT = """You are a senior legal analyst. Analyze this legal document and return ONLY a valid JSON object.

Return this exact JSON structure (no markdown, no code blocks, just JSON):
{{
  "documentStatus": "Legal" or "Illegal" or "Needs Review",
  "confidenceScore": <integer 0-100>,
  "summary": "<5-8 sentence plain English summary>",
  "riskLevel": "Low" or "Medium" or "High",
  "riskReason": "<why this risk level>",
  "documentIssues": ["<missing signatures>", "<missing dates>", "<incomplete terms>"],
  "suspiciousClauses": ["<clause 1>", "<clause 2>"],
  "missingClauses": ["<missing clause 1>"],
  "financialRisks": ["<financial risk 1>"],
  "expiryRisks": ["<deadline risk 1>"],
  "unfairConditions": ["<unfair condition 1>"],
  "complianceIssues": ["<compliance issue 1>"],
  "privacyRisks": ["<privacy risk 1>"],
  "legalLoopholes": ["<loophole 1>"],
  "warnings": ["<important warning 1>"],
  "recommendations": ["<recommendation 1>", "<recommendation 2>"],
  "finalVerdict": "<2-3 sentence professional conclusion>",
  "safeToSign": <true or false>
}}

Rules:
- Be specific, reference actual document content
- Use plain English
- safeToSign: true only if documentStatus is Legal AND riskLevel is Low
- Every list must have at least 1 real item if applicable

Document text:
{text}"""


async def analyze_legal_document(extracted_text: str) -> dict:
    """Analyze document using Gemini (free) or OpenAI (paid) fallback."""

    # Try Gemini first (free)
    gemini_key = (settings.GEMINI_API_KEY or "").strip()
    if gemini_key and len(gemini_key) > 10:
        result = await _analyze_with_gemini(extracted_text, gemini_key)
        if result:
            return result

    # Try OpenAI fallback (paid)
    openai_key = (settings.OPENAI_API_KEY or "").strip()
    if openai_key and len(openai_key) > 10 and not openai_key.startswith("sk-your"):
        result = await _analyze_with_openai(extracted_text, openai_key)
        if result:
            return result

    logger.warning("No valid AI API key configured")
    return _no_key_response()


async def _analyze_with_gemini(text: str, api_key: str) -> dict:
    """Use Google Gemini API (free tier)."""
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Gemini is fast — can handle more text
        text_to_analyze = text[:5000] if len(text) > 5000 else text

        response = model.generate_content(
            PROMPT.format(text=text_to_analyze),
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 2000,
            }
        )

        raw = response.text.strip()

        # Clean markdown code blocks if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        analysis = json.loads(raw)
        logger.info(f"Gemini analysis OK — status: {analysis.get('documentStatus')}")
        return _validate(analysis)

    except json.JSONDecodeError as e:
        logger.error(f"Gemini JSON parse error: {e}")
        # Try to extract JSON from response
        try:
            import re
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return _validate(analysis)
        except Exception:
            pass
        return None
    except Exception as e:
        logger.error(f"Gemini error: {type(e).__name__}: {e}")
        return None


async def _analyze_with_openai(text: str, api_key: str) -> dict:
    """Use OpenAI API (paid fallback)."""
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key, timeout=20.0)

        text_to_analyze = text[:2000] if len(text) > 2000 else text

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a legal analyst. Respond with valid JSON only."},
                {"role": "user", "content": PROMPT.format(text=text_to_analyze)},
            ],
            temperature=0.2,
            max_tokens=1500,
            response_format={"type": "json_object"},
        )

        analysis = json.loads(response.choices[0].message.content)
        logger.info("OpenAI analysis OK")
        return _validate(analysis)

    except Exception as e:
        logger.error(f"OpenAI error: {type(e).__name__}: {e}")
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
        "confidenceScore": 70,
        "summary": "Analysis completed.",
        "riskLevel": "Medium",
        "riskReason": "Standard risk assessment applied.",
        "finalVerdict": "Please review this document carefully.",
        "safeToSign": False,
        **{f: [] for f in list_fields},
    }

    for key, default in defaults.items():
        if key not in a or a[key] is None:
            a[key] = default

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
        a["confidenceScore"] = 70

    return a


def _no_key_response() -> dict:
    return {
        "documentStatus": "Needs Review",
        "confidenceScore": 0,
        "summary": (
            "No AI API key is configured. "
            "Get a FREE Gemini API key at https://aistudio.google.com/apikey "
            "and add it as GEMINI_API_KEY on Render."
        ),
        "riskLevel": "Medium",
        "riskReason": "Cannot assess risk without AI. Add GEMINI_API_KEY on Render (free).",
        "documentIssues": ["AI key not configured — add GEMINI_API_KEY on Render"],
        "suspiciousClauses": [],
        "missingClauses": [],
        "financialRisks": [],
        "expiryRisks": [],
        "unfairConditions": [],
        "complianceIssues": [],
        "privacyRisks": [],
        "legalLoopholes": [],
        "warnings": ["Add your free Gemini API key to get real AI analysis"],
        "recommendations": [
            "Get free API key at https://aistudio.google.com/apikey",
            "Add GEMINI_API_KEY to Render environment variables",
        ],
        "finalVerdict": "Configure GEMINI_API_KEY on Render to enable free AI analysis.",
        "safeToSign": False,
    }
