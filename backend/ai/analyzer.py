"""
AI Legal Document Analyzer
Primary: Groq (free, ultra-fast Llama 3)
Fallback: Gemini (free), OpenAI (paid)
Get free Groq key at: https://console.groq.com
"""

import json
import re
import logging
from config import settings

logger = logging.getLogger(__name__)

PROMPT = """You are a senior legal analyst with 20 years of experience. Analyze the legal document below.

IMPORTANT: Return ONLY a valid JSON object. No markdown, no code blocks, no explanation.

{{
  "documentStatus": "Legal" or "Illegal" or "Needs Review",
  "confidenceScore": <integer 0-100>,
  "summary": "<5-8 sentence plain English summary of this document>",
  "riskLevel": "Low" or "Medium" or "High",
  "riskReason": "<specific reason for this risk level referencing actual clauses>",
  "documentIssues": ["<missing signatures>", "<missing dates>", "<incomplete terms>", "<ambiguous language>"],
  "suspiciousClauses": ["<specific suspicious clause 1>", "<specific suspicious clause 2>"],
  "missingClauses": ["<important missing clause 1>", "<missing clause 2>"],
  "financialRisks": ["<specific financial risk 1>"],
  "expiryRisks": ["<deadline or expiry risk 1>"],
  "unfairConditions": ["<unfair condition 1>"],
  "complianceIssues": ["<compliance issue 1>"],
  "privacyRisks": ["<privacy or data risk 1>"],
  "legalLoopholes": ["<exploitable loophole 1>"],
  "warnings": ["<important warning 1>", "<important warning 2>"],
  "recommendations": ["<specific actionable recommendation 1>", "<recommendation 2>", "<recommendation 3>"],
  "finalVerdict": "<2-3 sentence professional conclusion: should the user proceed, modify, or seek legal review>",
  "safeToSign": <true or false>
}}

Rules:
- Be specific, reference actual content from the document
- safeToSign is true ONLY if documentStatus is Legal AND riskLevel is Low
- Every list must have real content, not generic placeholders
- Use plain English that a non-lawyer can understand

Document:
{text}"""


async def analyze_legal_document(extracted_text: str) -> dict:
    """Try Groq → Gemini → OpenAI in order."""

    # 1. Groq (free, fastest)
    groq_key = (settings.GROQ_API_KEY or "").strip()
    if groq_key and len(groq_key) > 10:
        result = await _analyze_groq(extracted_text, groq_key)
        if result:
            logger.info("Analysis completed via Groq")
            return result

    # 2. Gemini (free)
    gemini_key = (settings.GEMINI_API_KEY or "").strip()
    if gemini_key and len(gemini_key) > 10:
        result = await _analyze_gemini(extracted_text, gemini_key)
        if result:
            logger.info("Analysis completed via Gemini")
            return result

    # 3. OpenAI (paid fallback)
    openai_key = (settings.OPENAI_API_KEY or "").strip()
    if openai_key and len(openai_key) > 10 and not openai_key.startswith("sk-your"):
        result = await _analyze_openai(extracted_text, openai_key)
        if result:
            logger.info("Analysis completed via OpenAI")
            return result

    logger.warning("No valid AI API key found")
    return _no_key_response()


async def _analyze_groq(text: str, api_key: str) -> dict:
    """Groq API — free, ultra-fast Llama 3."""
    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        # Groq is very fast — can handle more text
        text_to_analyze = text[:5000] if len(text) > 5000 else text

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior legal analyst. Always respond with a single valid JSON object only. No markdown, no code blocks."
                },
                {
                    "role": "user",
                    "content": PROMPT.format(text=text_to_analyze)
                }
            ],
            temperature=0.2,
            max_tokens=2000,
        )

        raw = response.choices[0].message.content.strip()
        return _parse_and_validate(raw)

    except Exception as e:
        logger.error(f"Groq error: {type(e).__name__}: {e}")
        return None


async def _analyze_gemini(text: str, api_key: str) -> dict:
    """Google Gemini API — free tier."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        text_to_analyze = text[:5000] if len(text) > 5000 else text

        response = model.generate_content(
            PROMPT.format(text=text_to_analyze),
            generation_config={"temperature": 0.2, "max_output_tokens": 2000}
        )

        raw = response.text.strip()
        return _parse_and_validate(raw)

    except Exception as e:
        logger.error(f"Gemini error: {type(e).__name__}: {e}")
        return None


async def _analyze_openai(text: str, api_key: str) -> dict:
    """OpenAI — paid fallback."""
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

        raw = response.choices[0].message.content
        return _parse_and_validate(raw)

    except Exception as e:
        logger.error(f"OpenAI error: {type(e).__name__}: {e}")
        return None


def _parse_and_validate(raw: str) -> dict:
    """Parse JSON from AI response and validate all fields."""
    try:
        # Remove markdown code blocks if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)
        cleaned = cleaned.strip()

        # Extract JSON object
        if not cleaned.startswith("{"):
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                cleaned = match.group()

        analysis = json.loads(cleaned)
        return _validate(analysis)

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e} | Raw: {raw[:200]}")
        return None
    except Exception as e:
        logger.error(f"Parse error: {e}")
        return None


def _validate(a: dict) -> dict:
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
        "finalVerdict": "Please review this document carefully before proceeding.",
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
        a["confidenceScore"] = 75

    return a


def _no_key_response() -> dict:
    return {
        "documentStatus": "Needs Review",
        "confidenceScore": 0,
        "summary": (
            "No AI API key configured. "
            "Get a FREE Groq API key at https://console.groq.com "
            "and add it as GROQ_API_KEY on Render."
        ),
        "riskLevel": "Medium",
        "riskReason": "Cannot assess without AI. Add GROQ_API_KEY on Render.",
        "documentIssues": ["Add GROQ_API_KEY on Render to enable free AI analysis"],
        "suspiciousClauses": [],
        "missingClauses": [],
        "financialRisks": [],
        "expiryRisks": [],
        "unfairConditions": [],
        "complianceIssues": [],
        "privacyRisks": [],
        "legalLoopholes": [],
        "warnings": ["Configure GROQ_API_KEY on Render for free AI analysis"],
        "recommendations": [
            "Get free API key at https://console.groq.com",
            "Add GROQ_API_KEY to Render environment variables",
            "Redeploy after adding the key",
        ],
        "finalVerdict": "Add GROQ_API_KEY on Render to enable free AI analysis.",
        "safeToSign": False,
    }
