"""Field extractor for Nilaayam AI.

Extracts structured domain-specific fields from legal real estate documents
(Rental Agreements, Patta/Chitta, Encumbrance Certificates, and Sale Deeds).
Combines high-precision regex matching with Gemini LLM fallbacks for missing fields,
and normalizes extracted values (names, dates, survey numbers, currencies, areas).
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Optional Google Generative AI import
try:
    import google.generativeai as genai
except ImportError:
    genai = None
    logger.warning("google.generativeai is not installed; LLM field extraction fallback will be disabled.")


# Configuration helper
def _get_gemini_config() -> Tuple[Optional[str], str]:
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


# ============================================================================
# Value Normalizers
# ============================================================================

def _normalize_name(value: str) -> str:
    """Normalize human names by removing honorifics, prefixes, and formatting in title case."""
    text = value.strip()
    # Remove honorifics and relational prefixes
    prefix_pattern = (
        r"^(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Thiru\.?|Tmt\.?|Selvi\.?|Shri\.?|Smt\.?|"
        r"Son\s+of|Daughter\s+of|Wife\s+of|S/o|D/o|W/o)\s+"
    )
    text = re.sub(prefix_pattern, "", text, flags=re.IGNORECASE)
    # Remove trailing punctuation or qualifiers
    text = re.sub(r"[,;:\.-]+$", "", text).strip()
    text = re.sub(r"\s+", " ", text)
    return text.title()


def _normalize_survey_number(value: str) -> str:
    """Standardize survey numbers by removing extra whitespace around slashes/hyphens."""
    text = value.strip()
    # Strip leading descriptors like "S.No", "Sy.No", "புல எண்"
    text = re.sub(r"^(?:s\.?no\.?|sy\.?no\.?|survey\s*no\.?|புல\s*எண்)\s*[:\-]?\s*", "", text, flags=re.IGNORECASE)
    # Remove spaces around separators
    text = re.sub(r"\s*([/\-])\s*", r"\1", text)
    # Remove trailing punctuation
    text = re.sub(r"[,;:\.]+$", "", text).strip()
    return text.upper()


def _normalize_date(value: str) -> str:
    """Normalize various date formats into standard YYYY-MM-DD format."""
    raw = value.strip()
    # Strip ordinal suffixes (1st, 2nd, 3rd, 4th)
    cleaned = re.sub(r"(\d+)(?:st|nd|rd|th)", r"\1", raw, flags=re.IGNORECASE)
    cleaned = re.sub(r"[,.]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d %m %Y",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d %B %Y",
        "%d %b %Y",
        "%B %d %Y",
        "%b %d %Y",
        "%d-%b-%Y",
        "%d-%B-%Y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(cleaned, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Fallback regex for DD-MM-YYYY or DD/MM/YYYY
    match = re.search(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})", raw)
    if match:
        d, m, y = match.groups()
        try:
            dt = datetime(int(y), int(m), int(d))
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    return raw


def _normalize_area(value: str) -> str:
    """Convert property area to square meters while preserving original unit representation.

    Conversion constants:
      - 1 sq ft = 0.092903 sq.m
      - 1 cent = 40.4686 sq.m (435.6 sq ft)
      - 1 ground = 222.967 sq.m (2400 sq ft)
      - 1 acre = 4046.86 sq.m
      - 1 hectare / ஹெக்டேர் = 10000 sq.m
      - 1 are = 100 sq.m
      - 1 sq yard = 0.836127 sq.m
      - 1 kuzhi / குழி = 13.378 sq.m
    """
    raw = value.strip()
    match = re.search(
        r"([\d,]+(?:\.\d+)?)\s*"
        r"(sq\.?\s*ft|square\s*feet|cents?|சென்ட்|grounds?|acres?|ஏக்கர்|hectares?|ஹெக்டேர்|ares?|sq\.?\s*m|sq\.?\s*meters?|sq\.?\s*yards?|குழி)",
        raw,
        flags=re.IGNORECASE,
    )
    if not match:
        return raw

    num_str, unit = match.groups()
    try:
        num = float(num_str.replace(",", ""))
    except ValueError:
        return raw

    unit_lower = unit.lower().replace(".", "").replace(" ", "")

    conversion_factors = {
        "sqft": 0.092903,
        "squarefeet": 0.092903,
        "cent": 40.4686,
        "cents": 40.4686,
        "சென்ட்": 40.4686,
        "ground": 222.967,
        "grounds": 222.967,
        "acre": 4046.86,
        "acres": 4046.86,
        "ஏக்கர்": 4046.86,
        "hectare": 10000.0,
        "hectares": 10000.0,
        "ஹெக்டேர்": 10000.0,
        "are": 100.0,
        "ares": 100.0,
        "sqyard": 0.836127,
        "sqyards": 0.836127,
        "குழி": 13.378,
        "sqm": 1.0,
        "sqmeters": 1.0,
    }

    factor = conversion_factors.get(unit_lower)
    if factor is not None:
        sq_m = round(num * factor, 2)
        if unit_lower in ("sqm", "sqmeters"):
            return f"{num} sq.m"
        return f"{num_str} {unit} ({sq_m} sq.m)"

    return raw


def _normalize_currency(value: str) -> str:
    """Normalize currency amounts to plain numbers without symbols or separators."""
    cleaned = re.sub(r"[^\d.]", "", value.replace(",", ""))
    if cleaned.endswith(".00"):
        cleaned = cleaned[:-3]
    return cleaned


def _normalize_notice_period(value: str) -> str:
    """Convert notice periods (e.g. '1 month', '30 days') to standard number of days."""
    raw = value.strip().lower()
    month_match = re.search(r"(\d+)\s*months?", raw)
    if month_match:
        return str(int(month_match.group(1)) * 30)
    day_match = re.search(r"(\d+)\s*days?", raw)
    if day_match:
        return day_match.group(1)
    digits = re.sub(r"[^\d]", "", raw)
    return digits if digits else raw


def _normalize_lease_duration(value: str) -> str:
    """Convert lease duration (e.g. '11 months', '1 year') to standard number of months."""
    raw = value.strip().lower()
    year_match = re.search(r"(\d+)\s*years?", raw)
    if year_match:
        return str(int(year_match.group(1)) * 12)
    month_match = re.search(r"(\d+)\s*months?", raw)
    if month_match:
        return month_match.group(1)
    digits = re.sub(r"[^\d]", "", raw)
    return digits if digits else raw


def _normalize_percentage(value: str) -> str:
    """Ensure percentage format retains standard '%' sign."""
    cleaned = re.sub(r"[^\d.]", "", value)
    return f"{cleaned}%" if cleaned else value.strip()


def _normalize_value(field_name: str, value: str) -> str:
    """Normalize an extracted field value according to its semantics.

    Args:
        field_name: Name of the field.
        value: Raw extracted string value.

    Returns:
        Clean, standardized string value.
    """
    if not value or not str(value).strip():
        return ""

    val = str(value).strip()

    # 1. Names
    if any(k in field_name for k in ("name", "vendor", "vendee", "landlord", "tenant", "owner")):
        return _normalize_name(val)

    # 2. Survey Numbers
    if "survey" in field_name or "subdivision" in field_name:
        return _normalize_survey_number(val)

    # 3. Areas
    if "area" in field_name or "extent" in field_name:
        return _normalize_area(val)

    # 4. Dates
    if "date" in field_name or "period_from" in field_name or "period_to" in field_name:
        return _normalize_date(val)

    # 5. Currency / Consideration
    if any(k in field_name for k in ("rent", "deposit", "consideration", "duty", "penalty", "fee")):
        # Only normalize as currency if digits are present
        if re.search(r"\d", val):
            return _normalize_currency(val)
        return val

    # 6. Notice period
    if "notice_period" in field_name:
        return _normalize_notice_period(val)

    # 7. Lease duration
    if "duration" in field_name:
        return _normalize_lease_duration(val)

    # 8. Percentage
    if "percent" in field_name:
        return _normalize_percentage(val)

    # Clean general strings
    val = re.sub(r"\s+", " ", val)
    return val.strip()


def _estimate_page_number(text: str, char_idx: int) -> int:
    """Estimate page number based on character offset in document (approx 2000 chars per page)."""
    if char_idx <= 0:
        return 1
    return (char_idx // 2000) + 1


# ============================================================================
# LLM Extraction Helper
# ============================================================================

def _llm_extract_fields(
    text: str,
    doc_type: str,
    missing_fields: List[str],
) -> List[Dict[str, Any]]:
    """Use Gemini with structured JSON output to extract fields not found by regex.

    Args:
        text: Document text content.
        doc_type: Document category.
        missing_fields: List of missing field names to extract.

    Returns:
        List of extracted field dictionaries.
    """
    if not missing_fields:
        return []

    if genai is None:
        logger.warning("google.generativeai is not installed; skipping LLM field extraction.")
        return []

    api_key, model_name = _get_gemini_config()
    if not api_key:
        logger.warning("GEMINI_API_KEY is not configured; skipping LLM field extraction.")
        return []

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)

        # Truncate text to relevant context window
        snippet = text[:7000] if len(text) > 7000 else text

        fields_list_str = ", ".join(f"'{f}'" for f in missing_fields)
        prompt = (
            f"You are a legal document parsing expert analyzing a {doc_type} from Tamil Nadu, India.\n"
            f"Extract ONLY the following missing fields from the document text: [{fields_list_str}].\n\n"
            "Respond ONLY with a JSON array of objects, each containing:\n"
            "  - 'name': the exact field name requested\n"
            "  - 'value': the extracted verbatim value from the text (or empty string if not found)\n"
            "  - 'page_estimate': estimated page number (integer, default 1)\n"
            "  - 'confidence': confidence score between 0.0 and 1.0 (default 0.85 if found, 0.0 if not found)\n\n"
            f"--- DOCUMENT TEXT ---\n{snippet}\n--- END DOCUMENT TEXT ---"
        )

        response = model.generate_content(prompt)
        raw_output = response.text.strip()

        # Clean JSON markdown if wrapped in ```json ... ```
        if "```" in raw_output:
            raw_output = re.sub(r"^```(?:json)?\s*", "", raw_output)
            raw_output = re.sub(r"\s*```$", "", raw_output)

        items = json.loads(raw_output)
        if not isinstance(items, list):
            return []

        results: List[Dict[str, Any]] = []
        for item in items:
            name = item.get("name", "").strip()
            val = str(item.get("value", "")).strip()
            if name in missing_fields and val:
                normalized = _normalize_value(name, val)
                page = int(item.get("page_estimate", 1))
                conf = float(item.get("confidence", 0.85))
                results.append(
                    {
                        "name": name,
                        "value": val,
                        "normalized_value": normalized,
                        "page": page,
                        "page_estimate": page,
                        "confidence": conf,
                    }
                )

        return results

    except Exception as exc:
        logger.warning("LLM field extraction failed: %s", exc)
        return []


# ============================================================================
# Type-Specific Field Extractors
# ============================================================================

def _extract_rental_fields(text: str) -> List[Dict[str, Any]]:
    """Extract 12 standard rental agreement fields using regex, then LLM fallback."""
    fields: Dict[str, Dict[str, Any]] = {}

    patterns = {
        "monthly_rent": [
            r"(?:monthly\s+rent(?:al)?|rent\s+per\s+month|monthly\s+sum\s+of|மாத\s+வாடகை)[^\d\n\r]*(?:Rs\.?|INR|₹)?\s*([\d,]+(?:\.\d{2})?)",
            r"(?:Rs\.?|INR|₹)\s*([\d,]+(?:\.\d{2})?)\s*(?:per\s+month|/\s*month|monthly)",
        ],
        "security_deposit": [
            r"(?:security\s+deposit|caution\s+deposit|advance\s+amount|முன்பணம்|interest[\s-]free\s+advance)[^\d\n\r]*(?:Rs\.?|INR|₹)?\s*([\d,]+(?:\.\d{2})?)",
            r"(?:sum\s+of)\s*(?:Rs\.?|INR|₹)\s*([\d,]+(?:\.\d{2})?)\s*(?:as\s+(?:security\s+)?deposit)",
        ],
        "notice_period_days": [
            r"(\d+)\s*(?:days?|months?)\s+(?:prior\s+)?notice",
            r"notice\s+period\s+(?:of\s+)?(\d+\s*(?:days?|months?))",
        ],
        "lease_duration_months": [
            r"(\d+)\s*(?:months?|years?)\s+(?:tenure|period|duration|lease\s+period)",
            r"period\s+of\s+(\d+\s*(?:months?|years?))",
            r"duration\s+of\s+(\d+\s*(?:months?|years?))",
        ],
        "rent_increase_percent": [
            r"(?:increase|escalation|increment)\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*%",
            r"(\d+(?:\.\d+)?)\s*%\s*(?:increase|escalation|increment|annual\s+hike)",
        ],
        "landlord_name": [
            r"(?:landlord|lessor|house\s+owner|உரிமையாளர்)\s*[:\-]?\s*(?:Mr\.?|Mrs\.?|Ms\.?|Thiru\.?|Tmt\.?)?\s*([A-Za-z\s\.\u0B80-\u0BFF]{3,40}?)(?:,|\n|hereinafter|residing|son of|daughter of|wife of)",
            r"BETWEEN\s+(?:Mr\.?|Mrs\.?|Ms\.?|Thiru\.?)?\s*([A-Za-z\s\.\u0B80-\u0BFF]{3,40}?)(?:,|\n|hereinafter|residing)",
        ],
        "tenant_name": [
            r"(?:tenant|lessee|வாடகைதாரர்)\s*[:\-]?\s*(?:Mr\.?|Mrs\.?|Ms\.?|Thiru\.?|Tmt\.?)?\s*([A-Za-z\s\.\u0B80-\u0BFF]{3,40}?)(?:,|\n|hereinafter|residing|son of|daughter of|wife of)",
            r"AND\s+(?:Mr\.?|Mrs\.?|Ms\.?|Thiru\.?)?\s*([A-Za-z\s\.\u0B80-\u0BFF]{3,40}?)(?:,|\n|hereinafter|residing)",
        ],
        "property_address": [
            r"(?:schedule\s+(?:of\s+)?property|demised\s+premises|premises\s+situated\s+at|property\s+address|situated\s+at|சொத்து\s+விவரம்)\s*[:\-]?\s*([\s\S]{15,180}?)(?:\n\s*\n|WHEREAS|NOW\s+THIS|IN\s+WITNESS|TENANT|LANDLORD)",
        ],
        "start_date": [
            r"(?:commencing\s+from|effective\s+from|with\s+effect\s+from|start\s+date)\s*[:\-]?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+[,\s]+\d{4})",
        ],
        "end_date": [
            r"(?:expir(?:y|ing)\s+on|ending\s+on|valid\s+upto|till|until|end\s+date)\s*[:\-]?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+[,\s]+\d{4})",
        ],
        "maintenance_responsibility": [
            r"(?:maintenance\s+charges?\s+(?:shall\s+be\s+borne|paid\s+by|payable\s+by))\s*[:\-]?\s*(tenant|landlord|lessee|lessor)",
            r"(tenant|landlord|lessee|lessor)\s+(?:shall\s+pay|responsible\s+for)\s+(?:the\s+)?maintenance",
        ],
        "late_payment_penalty": [
            r"(?:late\s+payment|delayed\s+payment|penalty|late\s+fee)\s*[:\-]?\s*([^\n\r,.;]{4,50})",
            r"interest\s+@\s*(\d+(?:\.\d+)?\s*%)",
        ],
    }

    for name, regex_list in patterns.items():
        for pat in regex_list:
            match = re.search(pat, text, flags=re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                norm = _normalize_value(name, val)
                page = _estimate_page_number(text, match.start())
                fields[name] = {
                    "name": name,
                    "value": val,
                    "normalized_value": norm,
                    "page": page,
                    "page_estimate": page,
                    "confidence": 0.95,
                }
                break

    # Determine missing fields and invoke LLM fallback
    all_required = list(patterns.keys())
    missing = [f for f in all_required if f not in fields]
    if missing:
        llm_results = _llm_extract_fields(text, "rental_agreement", missing)
        for item in llm_results:
            fields[item["name"]] = item

    return list(fields.values())


def _extract_patta_fields(text: str) -> List[Dict[str, Any]]:
    """Extract 10 standard Patta/Chitta revenue fields using regex, then LLM fallback."""
    fields: Dict[str, Dict[str, Any]] = {}

    patterns = {
        "owner_name": [
            r"(?:பெயர்|பட்டாதாரர்\s*பெயர்|owner\s*name|pattadar\s*name)\s*[:\-]?\s*([A-Za-z\s\.\u0B80-\u0BFF]{3,40})",
            r"(?:திரு/திருமதி|Thiru/Tmt)\s*[:\-]?\s*([A-Za-z\s\.\u0B80-\u0BFF]{3,40})",
        ],
        "survey_number": [
            r"(?:புல\s*எண்|survey\s*no(?:\.|\s*number)?|s\.no|sy\.no)\s*[:\-]?\s*([0-9]+(?:\s*[/]\s*[0-9A-Za-z]+)?)",
        ],
        "subdivision_number": [
            r"(?:உட்பிரிவு\s*எண்|sub[\s-]*division\s*no(?:\.|\s*number)?)\s*[:\-]?\s*([0-9A-Za-z]+)",
        ],
        "taluk": [
            r"(?:வட்டம்|taluk)\s*[:\-]?\s*([A-Za-z\s\u0B80-\u0BFF]{3,30})",
        ],
        "village": [
            r"(?:கிராமம்|village)\s*[:\-]?\s*([A-Za-z\s\u0B80-\u0BFF]{3,30})",
        ],
        "district": [
            r"(?:மாவட்டம்|district)\s*[:\-]?\s*([A-Za-z\s\u0B80-\u0BFF]{3,30})",
        ],
        "property_area": [
            r"(?:விஸ்தீரணம்|பரப்பளவு|extent|area)\s*[:\-]?\s*([0-9.,]+\s*(?:ஹெக்டேர்|ஏக்கர்|சென்ட்|குழி|hectares?|acres?|cents?|sq\.?\s*ft|sq\.?\s*m|ares?))",
            r"([0-9.,]+\s*(?:ஹெக்டேர்|ஏக்கர்|சென்ட்|குழி|hectares?|acres?|cents?))",
        ],
        "patta_number": [
            r"(?:பட்டா\s*எண்|patta\s*no(?:\.|\s*number)?)\s*[:\-]?\s*([0-9]+)",
        ],
        "land_type": [
            r"(?:நிலத்தின்\s*வகை|வகைப்பாடு|land\s*type|classification)\s*[:\-]?\s*(நன்செய்|புன்செய்|நஞ்சை|புஞ்சை|manai|dry|wet|nanjai|punjai|residential)",
        ],
        "chitta_extent": [
            r"(?:சிட்டா\s*விவரம்|chitta\s*extent|extent\s*as\s*per\s*chitta)\s*[:\-]?\s*([^\n\r,;]{3,50})",
        ],
    }

    for name, regex_list in patterns.items():
        for pat in regex_list:
            match = re.search(pat, text, flags=re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                norm = _normalize_value(name, val)
                page = _estimate_page_number(text, match.start())
                fields[name] = {
                    "name": name,
                    "value": val,
                    "normalized_value": norm,
                    "page": page,
                    "page_estimate": page,
                    "confidence": 0.95,
                }
                break

    # If survey number has a slash (e.g. 123/4A) and subdivision_number wasn't matched separately
    if "survey_number" in fields and "subdivision_number" not in fields:
        s_val = fields["survey_number"]["value"]
        if "/" in s_val:
            parts = s_val.split("/")
            if len(parts) == 2 and parts[1].strip():
                fields["subdivision_number"] = {
                    "name": "subdivision_number",
                    "value": parts[1].strip(),
                    "normalized_value": parts[1].strip().upper(),
                    "page": fields["survey_number"]["page"],
                    "page_estimate": fields["survey_number"]["page_estimate"],
                    "confidence": 0.90,
                }

    all_required = list(patterns.keys())
    missing = [f for f in all_required if f not in fields]
    if missing:
        llm_results = _llm_extract_fields(text, "patta", missing)
        for item in llm_results:
            fields[item["name"]] = item

    return list(fields.values())


def _extract_ec_fields(text: str) -> List[Dict[str, Any]]:
    """Extract 9 standard Encumbrance Certificate fields using regex, then LLM fallback."""
    fields: Dict[str, Dict[str, Any]] = {}

    patterns = {
        "property_owner_name": [
            r"(?:claimant|executant|owner|சொந்தக்காரர்|பெயர்)\s*[:\-]?\s*([A-Za-z\s\.\u0B80-\u0BFF]{3,40})",
        ],
        "survey_number": [
            r"(?:survey\s*no(?:\.|\s*number)?|s\.no|sy\.no|புல\s*எண்)\s*[:\-]?\s*([0-9]+(?:\s*[/]\s*[0-9A-Za-z]+)?)",
        ],
        "property_address": [
            r"(?:village\s*/\s*street|property\s*description|boundaries|அமைவிடம்|சொத்து\s*விவரம்)\s*[:\-]?\s*([^\n\r]{10,150})",
        ],
        "ec_period_from": [
            r"(?:period\s*from|search\s*period\s*from|from\s*date|காலம்\s*முதல்)\s*[:\-]?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})",
        ],
        "ec_period_to": [
            r"(?:period\s*to|search\s*period\s*to|to\s*date|வரை)\s*[:\-]?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})",
        ],
        "registered_transactions": [
            r"(?:total\s*entries|no\s*of\s*entries|transactions|பதிவுகள்)\s*[:\-]?\s*([0-9]+|NIL|Nil|nil)",
            r"(nil\s+encumbrance|no\s+transactions\s+registered)",
        ],
        "mortgage_entries": [
            r"(?:mortgage\s*entries|mortgage\s*details|அடமானம்)\s*[:\-]?\s*([^\n\r,;]{3,60}|NIL|Nil|None)",
        ],
        "property_area": [
            r"(?:extent|area|பரப்பளவு)\s*[:\-]?\s*([0-9.,]+\s*(?:sq\.?\s*ft|sq\.?\s*m|cents?|acres?|grounds?))",
        ],
        "sub_registrar_office": [
            r"(?:sub[\s-]*registrar\s*office|sro|சார்பதிவாளர்\s*அலுவலகம்)\s*[:\-]?\s*([A-Za-z\s\u0B80-\u0BFF]{3,35})",
        ],
    }

    for name, regex_list in patterns.items():
        for pat in regex_list:
            match = re.search(pat, text, flags=re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                norm = _normalize_value(name, val)
                page = _estimate_page_number(text, match.start())
                fields[name] = {
                    "name": name,
                    "value": val,
                    "normalized_value": norm,
                    "page": page,
                    "page_estimate": page,
                    "confidence": 0.95,
                }
                break

    # If "nil encumbrance" is detected in the whole document, set registered_transactions and mortgage_entries to NIL
    if re.search(r"nil\s+encumbrance|சுமை\s+இல்லை|வில்லங்கம்\s+இல்லை", text, flags=re.IGNORECASE):
        if "registered_transactions" not in fields:
            fields["registered_transactions"] = {
                "name": "registered_transactions",
                "value": "NIL",
                "normalized_value": "NIL",
                "page": 1,
                "page_estimate": 1,
                "confidence": 0.95,
            }
        if "mortgage_entries" not in fields:
            fields["mortgage_entries"] = {
                "name": "mortgage_entries",
                "value": "NIL",
                "normalized_value": "NIL",
                "page": 1,
                "page_estimate": 1,
                "confidence": 0.95,
            }

    all_required = list(patterns.keys())
    missing = [f for f in all_required if f not in fields]
    if missing:
        llm_results = _llm_extract_fields(text, "encumbrance_certificate", missing)
        for item in llm_results:
            fields[item["name"]] = item

    return list(fields.values())


def _extract_sale_deed_fields(text: str) -> List[Dict[str, Any]]:
    """Extract 10 standard Sale Deed conveyance fields using regex, then LLM fallback."""
    fields: Dict[str, Dict[str, Any]] = {}

    patterns = {
        "vendor_name": [
            r"(?:vendor|seller|விற்பனையாளர்|கிரயதாரர்|first\s*party)\s*[:\-]?\s*(?:Mr\.?|Mrs\.?|Ms\.?|Thiru\.?)?\s*([A-Za-z\s\.\u0B80-\u0BFF]{3,40}?)(?:,|\n|hereinafter|residing|son of|daughter of)",
        ],
        "vendee_name": [
            r"(?:vendee|purchaser|buyer|வாங்குபவர்|second\s*party)\s*[:\-]?\s*(?:Mr\.?|Mrs\.?|Ms\.?|Thiru\.?)?\s*([A-Za-z\s\.\u0B80-\u0BFF]{3,40}?)(?:,|\n|hereinafter|residing|son of|daughter of)",
        ],
        "survey_number": [
            r"(?:survey\s*no(?:\.|\s*number)?|s\.no|sy\.no|புல\s*எண்)\s*[:\-]?\s*([0-9]+(?:\s*[/]\s*[0-9A-Za-z]+)?)",
        ],
        "property_area": [
            r"(?:extent|area|measuring\s*an\s*extent\s*of|பரப்பளவு)\s*[:\-]?\s*([0-9.,]+\s*(?:sq\.?\s*ft|sq\.?\s*m|cents?|acres?|grounds?|sq\.?\s*yards?))",
        ],
        "sale_consideration": [
            r"(?:sale\s*consideration|total\s*consideration|sale\s*amount|கிரயத்\s*தொகை)[^\d\n\r]*(?:Rs\.?|INR|₹)?\s*([\d,]+(?:\.\d{2})?)",
        ],
        "registration_date": [
            r"(?:date\s*of\s*registration|registered\s*on|தேதி)\s*[:\-]?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})",
        ],
        "document_number": [
            r"(?:document\s*no(?:\.|\s*number)?|doc\s*no|ஆவண\s*எண்)\s*[:\-]?\s*([0-9]+(?:\s*[/]\s*[0-9]{4})?)",
        ],
        "sub_registrar_office": [
            r"(?:sub[\s-]*registrar\s*office|sro|சார்பதிவாளர்\s*அலுவலகம்|registered\s*at\s*sro)\s*[:\-]?\s*([A-Za-z\s\u0B80-\u0BFF]{3,35})",
        ],
        "property_address": [
            r"(?:schedule\s+(?:of\s+)?property|property\s+situated\s+at|demised\s+premises|சொத்து\s+விவரம்)\s*[:\-]?\s*([\s\S]{15,180}?)(?:\n\s*\n|WHEREAS|NOW\s+THIS|IN\s+WITNESS)",
        ],
        "stamp_duty_paid": [
            r"(?:stamp\s*duty|முத்திரைத்தாள்\s*கட்டணம்)[^\d\n\r]*(?:Rs\.?|INR|₹)?\s*([\d,]+(?:\.\d{2})?)",
        ],
    }

    for name, regex_list in patterns.items():
        for pat in regex_list:
            match = re.search(pat, text, flags=re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                norm = _normalize_value(name, val)
                page = _estimate_page_number(text, match.start())
                fields[name] = {
                    "name": name,
                    "value": val,
                    "normalized_value": norm,
                    "page": page,
                    "page_estimate": page,
                    "confidence": 0.95,
                }
                break

    all_required = list(patterns.keys())
    missing = [f for f in all_required if f not in fields]
    if missing:
        llm_results = _llm_extract_fields(text, "sale_deed", missing)
        for item in llm_results:
            fields[item["name"]] = item

    return list(fields.values())


# ============================================================================
# Main Dispatcher
# ============================================================================

def extract_fields(
    text: str,
    doc_type: str,
    language: str = "en",
) -> Dict[str, Any]:
    """Extract structured legal fields based on the classified document type.

    Args:
        text: Full plain text extracted from the document.
        doc_type: 'rental_agreement', 'patta', 'encumbrance_certificate', 'sale_deed', or 'unknown'.
        language: Language code ('en' or 'tam').

    Returns:
        Dict[str, Any]:
            - fields: List of dicts, each with keys [name, value, normalized_value, page, confidence].
            - warnings: List of warning strings if any fields are missing or doc type is unhandled.
    """
    warnings: List[str] = []
    clean_type = doc_type.lower().strip()

    # Map variations
    if clean_type in ("ec", "encumbrance"):
        clean_type = "encumbrance_certificate"

    if clean_type == "rental_agreement":
        field_list = _extract_rental_fields(text)
    elif clean_type == "patta":
        field_list = _extract_patta_fields(text)
    elif clean_type == "encumbrance_certificate":
        field_list = _extract_ec_fields(text)
    elif clean_type == "sale_deed":
        field_list = _extract_sale_deed_fields(text)
    else:
        warnings.append(
            f"Unknown or unsupported document type '{doc_type}'. Field extraction skipped."
        )
        field_list = []

    # Check for missing critical fields and append warnings
    critical_fields_map = {
        "rental_agreement": ["monthly_rent", "security_deposit", "landlord_name", "tenant_name"],
        "patta": ["owner_name", "survey_number", "patta_number"],
        "encumbrance_certificate": ["survey_number", "ec_period_from", "ec_period_to"],
        "sale_deed": ["vendor_name", "vendee_name", "sale_consideration", "survey_number"],
    }

    found_names = {f["name"] for f in field_list}
    expected = critical_fields_map.get(clean_type, [])
    for exp in expected:
        if exp not in found_names:
            warnings.append(f"Critical field '{exp}' could not be identified.")

    return {
        "fields": field_list,
        "warnings": warnings,
    }
