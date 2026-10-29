"""Clause Classifier Module for Nilaayam AI.

Splits legal agreement text into individual clauses and classifies them into standard
categories using hybrid rule-based keyword matching and LLM zero-shot classification.
"""

import re
import os
import json
import logging
from typing import List, Dict, Optional, Any

# Try importing Google Generative AI
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    genai = None
    HAS_GENAI = False

try:
    from backend.config import settings
except ImportError:
    settings = None

logger = logging.getLogger(__name__)

VALID_CATEGORIES = [
    "rent_increase",
    "security_deposit",
    "notice_period",
    "eviction",
    "maintenance",
    "penalties",
    "registration",
    "termination",
    "rent_amount",
    "deposit_refund",
    "other",
]

REQUIRED_CATEGORIES = [
    "rent_amount",
    "security_deposit",
    "notice_period",
    "termination",
]

# Rule-based dictionary containing English and Tamil legal indicators
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "rent_increase": [
        "rent increase", "increase in rent", "annual increase", "rent escalation",
        "escalation clause", "hike in rent", "revision of rent", "rent shall be increased",
        "enhance the rent", "percentage increase", "per annum increase",
        "வாடகை உயர்வு", "வாடகை அதிகரிப்பு", "வாடகை மறுஆய்வு", "ஆண்டுதோறும் வாடகை"
    ],
    "deposit_refund": [
        "refund of deposit", "deposit refund", "refund of the security", "refund the deposit",
        "return of deposit", "return the security", "deposit shall be refunded", "deduction from deposit",
        "refund within", "deposit balance", "repay the deposit",
        "முன்பணம் திரும்ப", "முன்பணத்தை திருப்பி", "முன்பணம் ஒப்படைக்க", "முன்பணத் தொகை திரும்ப"
    ],
    "security_deposit": [
        "security deposit", "caution deposit", "rental advance", "interest-free deposit",
        "advance amount", "deposit amount", "initial deposit", "earnest money", "token advance",
        "பாதுகாப்பு வைப்புத்தொகை", "முன்பணம்", "அட்வான்ஸ்", "முன்பணத் தொகை", "வைப்புத் தொகை"
    ],
    "notice_period": [
        "notice period", "months' notice", "month notice", "prior notice",
        "written notice", "days notice", "notice in writing", "serve notice",
        "calendar months notice", "advance notice",
        "முன்னறிவிப்பு", "மாத அறிவிப்பு", "முன் அறிவிப்பு", "எழுத்துப்பூர்வ அறிவிப்பு", "அறிவிப்புக் காலம்"
    ],
    "eviction": [
        "eviction", "vacate the premises", "re-enter", "re-entry", "take possession",
        "quit notice", "summary eviction", "forcible entry", "handover possession",
        "dispossess", "default in vacating",
        "காலி செய்ய", "வெளியேற்ற", "வளாகத்தை காலி", "சுவாதீனம் எடுக்க", "வெளியேற்றுதல்"
    ],
    "maintenance": [
        "maintenance", "repairs", "structural repair", "white wash", "painting",
        "plumbing", "electrical repairs", "fixtures and fittings", "running maintenance",
        "leakage", "wear and tear", "day to day repairs", "water charges", "electricity bill",
        "பராமரிப்பு", "பழுதுபார்ப்பு", "சுண்ணாம்பு பூசுதல்", "மின் கட்டணம்", "குடிநீர் கட்டணம்"
    ],
    "penalties": [
        "penalty", "penalties", "late fee", "delayed payment", "interest per month",
        "per day fine", "forfeiture", "default interest", "liquidated damages",
        "levied at", "penal interest",
        "அபராதம்", "தாமதக் கட்டணம்", "தாமத வட்டி", "இழப்பீடு", "பறிமுதல்"
    ],
    "registration": [
        "registration", "registration act", "sub-registrar", "stamp duty", "stamp paper",
        "registered at", "duly registered", "notary", "notarized", "non-judicial stamp",
        "பதிவு", "சார்பதிவாளர்", "முத்திரைத்தாள்", "முத்திரைக் கட்டணம்", "பதிவு செய்தல்"
    ],
    "termination": [
        "termination", "terminate this agreement", "determination of lease", "lock-in period",
        "breach of terms", "right to terminate", "cancel this agreement", "expiry of lease",
        "force majeure", "premature termination",
        "ஒப்பந்த ரத்து", "முடிவுக்கு வர", "ரத்து செய்தல்", "ஒப்பந்த காலம் முடிவு", "ஒப்பந்த மீறல்"
    ],
    "rent_amount": [
        "monthly rent", "rent of rs", "payable on or before", "rent per month",
        "sum of rs", "payment of rent", "monthly consideration", "rent shall be paid",
        "மாத வாடகை", "வாடகையாக", "மாதம் தோறும்", "ரூபாய் வாடகை"
    ],
}


def _split_into_clauses(text: str, pages: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Splits full document text into numbered clauses or logical paragraphs.
    
    Returns list of dicts: {text, page_estimate, char_start, char_end}.
    """
    if not text or not text.strip():
        return []

    # Regex targeting clause headers:
    # 1. / 1) / (1) / Clause 1 / Section 1 / பிரிவு 1 / விதி 1 / etc.
    clause_pattern = re.compile(
        r"(?:(?<=\n)|(?<=^))\s*"
        r"(?:"
        r"(?:CLAUSE|SECTION|ARTICLE|PARAGRAPH|SCHEDULE|பிரிவு|விதி|நிபந்தனை)\s*[\dIVXLCDMivxlcdm\.]+"
        r"|"
        r"\b\d+[\.\)]\s+"
        r"|"
        r"\([a-zA-Z0-9]{1,3}\)\s+"
        r")",
        re.IGNORECASE
    )

    matches = list(clause_pattern.finditer(text))
    clauses: List[Dict[str, Any]] = []

    if matches:
        # Pre-clause preamble if present
        first_start = matches[0].start()
        if first_start > 0:
            preamble = text[:first_start].strip()
            if len(preamble) > 40:
                clauses.append({
                    "text": preamble,
                    "char_start": 0,
                    "char_end": first_start,
                })

        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            clause_str = text[start:end].strip()
            if clause_str:
                clauses.append({
                    "text": clause_str,
                    "char_start": start,
                    "char_end": end,
                })
    else:
        # Fallback: split on double newlines or large paragraph breaks
        raw_paras = re.split(r"\n\s*\n+", text)
        curr_offset = 0
        for p in raw_paras:
            clean_p = p.strip()
            if not clean_p:
                curr_offset += len(p) + 2
                continue
            idx = text.find(clean_p, curr_offset)
            if idx == -1:
                idx = curr_offset
            clauses.append({
                "text": clean_p,
                "char_start": idx,
                "char_end": idx + len(clean_p),
            })
            curr_offset = idx + len(clean_p)

    # Estimate or resolve page numbers
    avg_chars_per_page = 2000
    for clause in clauses:
        c_start = clause["char_start"]
        page_num = 1
        if pages and isinstance(pages, list):
            for p_info in pages:
                p_start = p_info.get("char_start", 0)
                p_end = p_info.get("char_end", p_start + len(p_info.get("text", "")))
                if p_start <= c_start <= p_end:
                    page_num = p_info.get("page_number", 1)
                    break
        else:
            page_num = max(1, (c_start // avg_chars_per_page) + 1)
        clause["page_estimate"] = page_num

    return clauses


def _rule_classify(clause_text: str) -> Dict[str, Any]:
    """Classifies a clause using domain keyword heuristics.
    
    Returns {category, confidence}.
    """
    lower_text = clause_text.lower()
    
    category_scores: Dict[str, float] = {}
    for cat, kws in CATEGORY_KEYWORDS.items():
        score = 0.0
        for kw in kws:
            kw_lower = kw.lower()
            if kw_lower in lower_text:
                # Direct match weight
                score += 1.0
                # Exact word boundary match gets extra weight
                if re.search(r"\b" + re.escape(kw_lower) + r"\b", lower_text):
                    score += 0.5
        if score > 0:
            category_scores[cat] = score

    if not category_scores:
        return {"category": "other", "confidence": 0.3}

    sorted_cats = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    best_cat, best_score = sorted_cats[0]

    # Specific disambiguation rules
    # E.g., if clause talks about refunding deposit, classify as deposit_refund rather than rent_amount
    if "refund" in lower_text and "deposit" in lower_text:
        best_cat = "deposit_refund"
        best_score = max(best_score, 2.5)

    if "rent" in lower_text and ("escalat" in lower_text or "increase" in lower_text or "hike" in lower_text or "%" in lower_text):
        best_cat = "rent_increase"
        best_score = max(best_score, 2.5)

    # Map raw score to confidence in [0.4, 0.95]
    confidence = min(0.95, 0.45 + (best_score * 0.15))
    return {"category": best_cat, "confidence": round(confidence, 2)}


def _llm_classify(clause_text: str) -> Dict[str, Any]:
    """Uses Google Gemini to classify ambiguous clauses with confidence < 0.6."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key and settings and getattr(settings, "gemini_api_key", None):
        api_key = settings.gemini_api_key

    if not (HAS_GENAI and api_key):
        return {"category": "other", "confidence": 0.4}

    try:
        genai.configure(api_key=api_key)
        model_name = getattr(settings, "llm_model", "gemini-1.5-flash") if settings else "gemini-1.5-flash"
        model = genai.GenerativeModel(model_name)

        prompt = f"""You are a specialized legal document analyzer for rental agreements and property contracts in India.
Classify the following agreement clause into EXACTLY ONE of the following valid categories:
{json.dumps(VALID_CATEGORIES)}

Clause text:
"{clause_text}"

Respond with ONLY a valid JSON object in this format:
{{
  "category": "<one_of_valid_categories>",
  "confidence": <float between 0.0 and 1.0>,
  "reason": "<short 1-line justification>"
}}
"""
        response = model.generate_content(prompt)
        text_resp = response.text.strip()
        # Clean markdown formatting if present
        if text_resp.startswith("```json"):
            text_resp = text_resp[7:]
        if text_resp.startswith("```"):
            text_resp = text_resp[3:]
        if text_resp.endswith("```"):
            text_resp = text_resp[:-3]

        parsed = json.loads(text_resp.strip())
        cat = parsed.get("category", "other")
        conf = float(parsed.get("confidence", 0.75))
        if cat not in VALID_CATEGORIES:
            cat = "other"
        return {"category": cat, "confidence": round(conf, 2)}
    except Exception as e:
        logger.warning(f"LLM clause classification fallback error: {e}")
        return {"category": "other", "confidence": 0.45}


def identify_missing_clauses(found_categories: List[str]) -> List[str]:
    """Checks the list of detected categories against mandatory agreement clauses.
    
    Required categories: rent_amount, security_deposit, notice_period, termination.
    Returns list of missing required categories.
    """
    found_set = set(found_categories)
    missing = [req for req in REQUIRED_CATEGORIES if req not in found_set]
    return missing


def classify_clauses(text: str, pages: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Splits text into clauses and classifies each into standard legal categories.
    
    Uses rule-based classification first; falls back to LLM if confidence < 0.6.
    Returns list of {clause_text, category, page_number, confidence, char_start, char_end}.
    """
    raw_clauses = _split_into_clauses(text, pages=pages)
    classified: List[Dict[str, Any]] = []

    for item in raw_clauses:
        clause_str = item["text"]
        rule_res = _rule_classify(clause_str)
        category = rule_res["category"]
        confidence = rule_res["confidence"]

        # If confidence is low and clause is substantial, consult LLM
        if confidence < 0.6 and len(clause_str.split()) >= 8:
            llm_res = _llm_classify(clause_str)
            if llm_res["confidence"] > confidence:
                category = llm_res["category"]
                confidence = llm_res["confidence"]

        classified.append({
            "clause_text": clause_str,
            "category": category,
            "page_number": item.get("page_estimate", 1),
            "confidence": confidence,
            "char_start": item.get("char_start", 0),
            "char_end": item.get("char_end", len(clause_str)),
        })

    return classified
