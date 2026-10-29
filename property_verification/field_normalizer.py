"""Field Normalizer Module for Nilaayam AI.

Standardizes property document fields across Patta, Encumbrance Certificate (EC),
and Sale Deed. Normalizes names, survey numbers, land areas, and dates, with
fuzzy matching and OCR character substitution detection.
"""

import re
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Try importing thefuzz
try:
    from thefuzz import fuzz
    HAS_THEFUZZ = True
except ImportError:
    import difflib
    HAS_THEFUZZ = False

logger = logging.getLogger(__name__)


# Conversion factors to square meters (sqm)
SQM_CONVERSIONS = {
    "sqm": 1.0,
    "sq_m": 1.0,
    "sq meter": 1.0,
    "sq meters": 1.0,
    "square meter": 1.0,
    "square meters": 1.0,
    "சதுர மீட்டர்": 1.0,
    "sqft": 0.092903,
    "sq ft": 0.092903,
    "sq.ft": 0.092903,
    "sq.ft.": 0.092903,
    "sft": 0.092903,
    "square feet": 0.092903,
    "square foot": 0.092903,
    "சதுர அடி": 0.092903,
    "cent": 40.4686,
    "cents": 40.4686,
    "சென்ட்": 40.4686,
    "ground": 222.967,
    "grounds": 222.967,
    "கிரவுண்ட்": 222.967,
    "acre": 4046.86,
    "acres": 4046.86,
    "ஏக்கர்": 4046.86,
    "hectare": 10000.0,
    "hectares": 10000.0,
    "ha": 10000.0,
    "ஹெக்டேர்": 10000.0,
    "are": 100.0,
    "ares": 100.0,
    "ஏர்ஸ்": 100.0,
}


def normalize_name(name: str) -> str:
    """Normalizes person or entity name:
    - Trims whitespace and collapses multiple spaces.
    - Resolves typical OCR start-of-word number confusions (0->O, 1->I, 5->S, 8->B).
    - Removes common honorific prefixes (Thiru, Tmt, Mr, Mrs, Shri, Smt, Dr).
    - Converts to standard Title Case.
    """
    if not name:
        return ""

    cleaned = " ".join(name.strip().split())

    # Fix OCR numeric substitutions at beginning of words
    words = cleaned.split()
    corrected_words = []
    for w in words:
        if len(w) > 1:
            if w[0] == "0" and w[1].isalpha():
                w = "O" + w[1:]
            elif w[0] == "1" and w[1].isalpha():
                w = "I" + w[1:]
            elif w[0] == "5" and w[1].isalpha():
                w = "S" + w[1:]
            elif w[0] == "8" and w[1].isalpha():
                w = "B" + w[1:]
        corrected_words.append(w)
    cleaned = " ".join(corrected_words)

    # Strip honorifics
    honorific_pattern = r"^(?:Thiru|Tmt|Mr|Mrs|Ms|Miss|Dr|Shri|Smt|திரு|திருமதி)\.?\s+"
    cleaned = re.sub(honorific_pattern, "", cleaned, flags=re.IGNORECASE)

    # Convert to title case while preserving initials with dots (e.g. "S. Raman")
    parts = cleaned.split()
    titled_parts = [p.capitalize() if not (len(p) <= 2 and "." in p) else p.upper() for p in parts]
    return " ".join(titled_parts)


def normalize_survey_number(survey: str) -> str:
    """Standardizes cadastral survey and subdivision numbers:
    - Strips prefixes like 'S.No', 'Sy.No', 'Survey No', 'புல எண்'.
    - Removes spaces.
    - Standardizes separators (-, ., :) to '/'.
    - Uppercases alphabetic subdivision suffixes (e.g., '123/4a' -> '123/4A').
    """
    if not survey:
        return ""

    cleaned = survey.strip()

    # Remove labels
    label_pattern = r"^(?:s\.?\s*no\.?|sy\.?\s*no\.?|survey\s*no\.?|survey\s*number|புல\s*எண்|எஸ்\.எண்)\s*[:\.-]?\s*"
    cleaned = re.sub(label_pattern, "", cleaned, flags=re.IGNORECASE)

    # Remove all spaces
    cleaned = re.sub(r"\s+", "", cleaned)

    # Standardize delimiters
    cleaned = re.sub(r"[-–—\:]", "/", cleaned)

    # Replace multiple slashes
    cleaned = re.sub(r"/+", "/", cleaned)

    return cleaned.upper()


def normalize_area(area: str) -> Dict[str, Any]:
    """Extracts numeric area and unit, converting to square meters for standardized comparison.
    
    Returns:
        Dict: {"original": str, "value_sqm": Optional[float], "unit": str}
    """
    if not area:
        return {"original": "", "value_sqm": None, "unit": "unknown"}

    orig_str = area.strip()
    clean_lower = orig_str.lower().replace(",", "")

    # Identify matching unit from known dictionary
    matched_unit = None
    matched_factor = 1.0

    # Sort units by descending length to match "square meters" before "sqm"
    sorted_units = sorted(SQM_CONVERSIONS.keys(), key=lambda x: len(x), reverse=True)
    for unit_key in sorted_units:
        if unit_key in clean_lower:
            matched_unit = unit_key
            matched_factor = SQM_CONVERSIONS[unit_key]
            break

    # Extract numeric value
    num_match = re.search(r"(\d+(?:\.\d+)?)", clean_lower)
    if num_match:
        val = float(num_match.group(1))
        val_sqm = round(val * matched_factor, 3)
        return {
            "original": orig_str,
            "value_sqm": val_sqm,
            "unit": matched_unit or "sqft_assumed",
        }

    return {"original": orig_str, "value_sqm": None, "unit": "unparseable"}


def normalize_date(date_str: str) -> str:
    """Parses various date formats and converts to ISO standard YYYY-MM-DD.
    
    Returns original string if unparseable.
    """
    if not date_str:
        return ""

    cleaned = date_str.strip()

    # Common date formats in Indian registration records
    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d/%m/%y",
        "%d-%m-%y",
        "%d %B %Y",
        "%d %b %Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%Y/%m/%d",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(cleaned, fmt)
            # Two-digit year correction if past 2030 or before 1900
            if dt.year < 1920:
                dt = dt.replace(year=dt.year + 100)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Attempt regex extraction of DD/MM/YYYY
    match = re.search(r"(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})", cleaned)
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            dt = datetime(year, month, day)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    return cleaned


def normalize_field(field_name: str, value: str) -> str:
    """Dispatches to the appropriate normalizer based on field name."""
    if not value:
        return ""

    fname = field_name.lower().strip()

    if any(k in fname for k in ["name", "owner", "vendor", "purchaser", "buyer", "seller"]):
        return normalize_name(value)

    elif any(k in fname for k in ["survey", "subdivision", "sno", "sy_no", "dag"]):
        return normalize_survey_number(value)

    elif any(k in fname for k in ["area", "extent", "measurement", "dimension"]):
        norm_dict = normalize_area(value)
        if norm_dict["value_sqm"] is not None:
            return f"{norm_dict['value_sqm']} sqm ({norm_dict['original']})"
        return value.strip()

    elif any(k in fname for k in ["date", "registered_on", "execution"]):
        return normalize_date(value)

    elif any(k in fname for k in ["village", "taluk", "district"]):
        return normalize_name(value)

    return " ".join(value.strip().split())


def are_names_similar(name1: str, name2: str, threshold: float = 0.85) -> bool:
    """Checks whether two person/entity names match using fuzzy token comparison."""
    if not name1 or not name2:
        return False

    n1 = normalize_name(name1).lower()
    n2 = normalize_name(name2).lower()

    if n1 == n2:
        return True

    # Strip dots and commas
    c1 = re.sub(r"[\.,]", " ", n1).strip()
    c2 = re.sub(r"[\.,]", " ", n2).strip()
    c1_words = sorted(c1.split())
    c2_words = sorted(c2.split())

    # Exact token match regardless of order (e.g. "Raman S" vs "S Raman")
    if c1_words == c2_words:
        return True

    # Check initial expansion: e.g. "R. Kumar" vs "Raman Kumar"
    if len(c1_words) == len(c2_words) and len(c1_words) == 2:
        w1_a, w1_b = c1_words[0], c1_words[1]
        w2_a, w2_b = c2_words[0], c2_words[1]
        if (len(w1_a) == 1 and w2_a.startswith(w1_a) and w1_b == w2_b) or \
           (len(w2_a) == 1 and w1_a.startswith(w2_a) and w1_b == w2_b):
            return True

    if HAS_THEFUZZ:
        token_sort = fuzz.token_sort_ratio(c1, c2) / 100.0
        ratio = fuzz.ratio(c1, c2) / 100.0
        return max(token_sort, ratio) >= threshold
    else:
        matcher = difflib.SequenceMatcher(None, " ".join(c1_words), " ".join(c2_words))
        return matcher.ratio() >= threshold


def likely_ocr_error(val1: str, val2: str) -> bool:
    """Checks if the discrepancy between two values is primarily attributable to OCR misrecognition.
    
    Substitutions inspected: O/0, I/1/l/|, S/5, B/8, Z/2, U/V, and minor spacing/punctuation.
    """
    if not val1 or not val2:
        return False

    def canonicalize_ocr(s: str) -> str:
        s_clean = s.lower().strip()
        # Common OCR character substitutions
        ocr_map = {
            "0": "o",
            "1": "i",
            "l": "i",
            "|": "i",
            "/": "",
            "5": "s",
            "8": "b",
            "2": "z",
            "v": "u",
            "-": "",
            ".": "",
            ",": "",
            " ": "",
        }
        for src, dst in ocr_map.items():
            s_clean = s_clean.replace(src, dst)
        return s_clean

    c1 = canonicalize_ocr(val1)
    c2 = canonicalize_ocr(val2)

    if c1 == c2:
        return True

    # Check high similarity under canonical representation
    if HAS_THEFUZZ:
        return fuzz.ratio(c1, c2) >= 92
    else:
        import difflib
        return difflib.SequenceMatcher(None, c1, c2).ratio() >= 0.92
