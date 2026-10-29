"""Document classifier for Nilaayam AI.

Classifies legal documents into 'rental_agreement', 'patta', 'encumbrance_certificate',
'sale_deed', or 'unknown' using a two-tier approach: rule-based keyword matching first,
falling back to Gemini LLM classification when confidence is below 0.7.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Optional Google Generative AI import
try:
    import google.generativeai as genai
except ImportError:
    genai = None
    logger.warning("google.generativeai is not installed; LLM classification fallback will be disabled.")


# Configuration helper
def _get_gemini_config() -> tuple[Optional[str], str]:
    """Retrieve Gemini API key and model name from backend config or environment."""
    api_key = os.environ.get("GEMINI_API_KEY")
    model_name = "gemini-1.5-flash"

    try:
        from backend.config import settings
        if not api_key:
            api_key = getattr(settings, "gemini_api_key", "")
        model_name = getattr(settings, "llm_model", "gemini-1.5-flash")
    except Exception:
        pass

    return api_key, model_name


# Keyword dictionary for Tamil Nadu real estate documents
CLASSIFICATION_RULES: Dict[str, Dict[str, Any]] = {
    "rental_agreement": {
        "keywords": [
            "lease agreement",
            "rental agreement",
            "tenancy agreement",
            "tenant",
            "landlord",
            "monthly rent",
            "security deposit",
            "lessor",
            "lessee",
            "demised premises",
            "premises situated",
            "rent per month",
            "குத்தகை",
            "வாடகை",
            "வாடகை ஒப்பந்தம்",
            "குத்தகை பத்திரம்",
        ],
        "strong_phrases": [
            "rental agreement",
            "lease agreement",
            "tenancy agreement",
            "security deposit",
            "monthly rent",
            "வாடகை ஒப்பந்தம்",
        ],
        "filename_tokens": ["rental", "lease", "tenant", "rent", "agreement", "வாடகை"],
    },
    "patta": {
        "keywords": [
            "patta",
            "பட்டா",
            "chitta",
            "சிட்டா",
            "survey number",
            "புல எண்",
            "taluk",
            "வட்டம்",
            "village",
            "கிராமம்",
            "revenue department",
            "வருவாய்த்துறை",
            "subdivision",
            "உட்பிரிவு",
            "pattadar",
            "பட்டாதாரர்",
            "நில உரிமை",
        ],
        "strong_phrases": [
            "patta",
            "chitta",
            "பட்டா",
            "சிட்டா",
            "புல எண்",
            "பட்டாதாரர்",
            "revenue department",
        ],
        "filename_tokens": ["patta", "chitta", "பட்டா", "சிட்டா"],
    },
    "encumbrance_certificate": {
        "keywords": [
            "encumbrance certificate",
            "EC",
            "வில்லங்க சான்று",
            "வில்லங்கம்",
            "transactions",
            "mortgage",
            "sub-registrar",
            "sub registrar office",
            "registration department",
            "nil encumbrance",
            "search period",
            "பதிவுத்துறை",
            "சுமை விவரம்",
        ],
        "strong_phrases": [
            "encumbrance certificate",
            "வில்லங்க சான்று",
            "nil encumbrance",
            "sub registrar office",
            "search period",
        ],
        "filename_tokens": ["encumbrance", "ec", "வில்லங்கம்", "வில்லங்க"],
    },
    "sale_deed": {
        "keywords": [
            "sale deed",
            "விற்பனை பத்திரம்",
            "கிரய பத்திரம்",
            "vendor",
            "vendee",
            "sale consideration",
            "registered",
            "absolute sale",
            "purchaser",
            "conveyance deed",
            "title deed",
            "stamp duty",
            "முத்திரைத்தாள்",
            "விற்பனையாளர்",
            "கிரயதாரர்",
        ],
        "strong_phrases": [
            "sale deed",
            "விற்பனை பத்திரம்",
            "கிரய பத்திரம்",
            "sale consideration",
            "absolute sale",
            "conveyance deed",
        ],
        "filename_tokens": ["sale", "deed", "sale_deed", "விற்பனை", "கிரய"],
    },
}


def _rule_based_classify(text: str, filename: str = "") -> Dict[str, Any]:
    """Perform rule-based classification using keywords and regex matching.

    Args:
        text: Plain text content of the document.
        filename: Optional filename of the uploaded document.

    Returns:
        Dict[str, Any]:
            - doc_type: 'rental_agreement'|'patta'|'encumbrance_certificate'|'sale_deed'|'unknown'
            - confidence: float between 0.0 and 1.0
            - method: 'rule_based'
            - indicators: List of matched keywords / phrases
    """
    clean_text = (text or "").lower()
    clean_filename = (filename or "").lower()

    if not clean_text and not clean_filename:
        return {
            "doc_type": "unknown",
            "confidence": 0.0,
            "method": "rule_based",
            "indicators": [],
        }

    scores: Dict[str, float] = {}
    matched_indicators: Dict[str, List[str]] = {}

    for doc_type, rules in CLASSIFICATION_RULES.items():
        score = 0.0
        found_indicators: List[str] = []

        # Check filename tokens
        for token in rules["filename_tokens"]:
            token_pattern = r"\b" + re.escape(token) + r"\b"
            if re.search(token_pattern, clean_filename):
                score += 2.5
                found_indicators.append(f"filename:{token}")

        # Check strong phrases in text
        for phrase in rules["strong_phrases"]:
            if phrase.lower() in clean_text:
                score += 3.0
                if phrase not in found_indicators:
                    found_indicators.append(phrase)

        # Check general keywords
        for kw in rules["keywords"]:
            # Use word boundary for short acronyms like 'ec'
            if len(kw) <= 3:
                pattern = r"\b" + re.escape(kw) + r"\b"
                if re.search(pattern, clean_text, flags=re.IGNORECASE):
                    score += 1.5
                    if kw not in found_indicators:
                        found_indicators.append(kw)
            else:
                if kw.lower() in clean_text:
                    score += 1.0
                    if kw not in found_indicators:
                        found_indicators.append(kw)

        scores[doc_type] = score
        matched_indicators[doc_type] = found_indicators

    # Identify top scoring document type
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best_type, top_score = sorted_scores[0]
    runner_up_type, runner_up_score = sorted_scores[1]

    if top_score <= 0.0:
        return {
            "doc_type": "unknown",
            "confidence": 0.0,
            "method": "rule_based",
            "indicators": [],
        }

    # Calculate confidence based on score magnitude and margin over runner-up
    indicators = matched_indicators.get(best_type, [])
    unique_count = len(indicators)

    # Base confidence from unique indicators
    if unique_count >= 5 or top_score >= 8.0:
        base_conf = 0.88
    elif unique_count >= 3 or top_score >= 5.0:
        base_conf = 0.75
    elif unique_count >= 2:
        base_conf = 0.60
    elif unique_count == 1:
        base_conf = 0.40
    else:
        base_conf = 0.20

    # Margin bonus if top score clearly separates from runner-up
    margin = top_score - runner_up_score
    if margin > 3.0:
        base_conf += 0.08
    elif margin < 1.0 and runner_up_score > 0:
        # Ambiguous between top two categories
        base_conf -= 0.15

    confidence = round(max(0.1, min(0.98, base_conf)), 2)

    return {
        "doc_type": best_type,
        "confidence": confidence,
        "method": "rule_based",
        "indicators": indicators,
    }


def _llm_classify(text: str) -> Dict[str, Any]:
    """Classify document using Gemini LLM when rule-based confidence is inconclusive.

    Args:
        text: Plain text content of the document (truncated if large).

    Returns:
        Dict[str, Any]:
            - doc_type: One of 'rental_agreement', 'patta', 'encumbrance_certificate',
                        'sale_deed', or 'unknown'
            - confidence: float (0.8 on successful LLM identification)
            - method: 'llm'
            - indicators: List of key phrases or evidence identified by the LLM
    """
    fallback_res: Dict[str, Any] = {
        "doc_type": "unknown",
        "confidence": 0.0,
        "method": "llm",
        "indicators": [],
    }

    if genai is None:
        logger.warning("google.generativeai is not installed; skipping LLM classification.")
        return fallback_res

    api_key, model_name = _get_gemini_config()
    if not api_key:
        logger.warning("GEMINI_API_KEY is not configured; skipping LLM classification.")
        return fallback_res

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)

        # Truncate text to header/body context (first 4000 chars is sufficient for legal classifications)
        snippet = text[:4000] if len(text) > 4000 else text

        prompt = (
            "You are an expert Tamil Nadu property legal document classifier.\n"
            "Analyze the document text snippet below and classify it into exactly one of these categories:\n"
            "  1. 'rental_agreement' (lease/rental agreement, tenancy)\n"
            "  2. 'patta' (land revenue record, patta/chitta)\n"
            "  3. 'encumbrance_certificate' (EC, registration department encumbrance certificate, nil encumbrance)\n"
            "  4. 'sale_deed' (property conveyance, sale deed, absolute sale deed, கிரய பத்திரம்)\n"
            "  5. 'unknown' (if it does not fit any of the above)\n\n"
            "Respond ONLY with a valid JSON object in this format:\n"
            "{\n"
            '  "doc_type": "rental_agreement" | "patta" | "encumbrance_certificate" | "sale_deed" | "unknown",\n'
            '  "indicators": ["string1", "string2"],\n'
            '  "reasoning": "brief explanation"\n'
            "}\n\n"
            f"--- DOCUMENT SNIPPET ---\n{snippet}\n--- END SNIPPET ---"
        )

        response = model.generate_content(prompt)
        raw_output = response.text.strip()

        # Clean JSON markdown if wrapped in ```json ... ```
        if "```" in raw_output:
            raw_output = re.sub(r"^```(?:json)?\s*", "", raw_output)
            raw_output = re.sub(r"\s*```$", "", raw_output)

        data = json.loads(raw_output)
        doc_type = data.get("doc_type", "unknown").strip().lower()
        valid_types = {
            "rental_agreement",
            "patta",
            "encumbrance_certificate",
            "sale_deed",
            "unknown",
        }

        # Normalize common variations
        if doc_type == "ec":
            doc_type = "encumbrance_certificate"
        elif doc_type not in valid_types:
            doc_type = "unknown"

        indicators = data.get("indicators", [])
        if not isinstance(indicators, list):
            indicators = [str(indicators)]

        confidence = 0.8 if doc_type != "unknown" else 0.0

        return {
            "doc_type": doc_type,
            "confidence": confidence,
            "method": "llm",
            "indicators": indicators,
        }

    except Exception as exc:
        logger.warning("LLM classification failed: %s", exc)
        return fallback_res


def classify_document(text: str, filename: str = "") -> Dict[str, Any]:
    """Classify a document into one of the known document types.

    Attempts rule-based classification first. If rule confidence is < 0.7,
    invokes Gemini LLM classification as a fallback.

    Args:
        text: Extracted text of the document.
        filename: Optional filename of the document.

    Returns:
        Dict[str, Any]:
            - doc_type: 'rental_agreement'|'patta'|'encumbrance_certificate'|'sale_deed'|'unknown'
            - confidence: float between 0.0 and 1.0
            - method: 'rule_based' or 'llm'
            - indicators: list of matching evidence keywords or phrases
    """
    rule_result = _rule_based_classify(text, filename)

    if rule_result["confidence"] >= 0.7:
        logger.debug(
            "Rule-based classification succeeded with confidence %.2f: %s",
            rule_result["confidence"],
            rule_result["doc_type"],
        )
        return rule_result

    logger.info(
        "Rule-based confidence (%.2f) < 0.7; invoking LLM classification fallback.",
        rule_result["confidence"],
    )
    llm_result = _llm_classify(text)

    # Use LLM result if it provided a decisive answer
    if llm_result["doc_type"] != "unknown" and llm_result["confidence"] > rule_result["confidence"]:
        return llm_result

    # Otherwise return best available rule result
    if rule_result["doc_type"] != "unknown" and rule_result["confidence"] > 0.0:
        return rule_result

    return llm_result
