"""Property Document Comparator Module for Nilaayam AI.

Compares extracted metadata fields across Patta, Encumbrance Certificate (EC),
and Sale Deed. Identifies matches, mismatches, OCR artifacts, and detects critical title red flags.
"""

import uuid
import logging
from typing import List, Dict, Optional, Any

from property_verification.field_normalizer import (
    normalize_name,
    normalize_survey_number,
    normalize_area,
    normalize_field,
    are_names_similar,
    likely_ocr_error,
)

logger = logging.getLogger(__name__)

TARGET_FIELDS = [
    "owner_name",
    "survey_number",
    "subdivision_number",
    "property_area",
    "property_address",
    "taluk",
    "village",
    "district",
]


def _index_doc_fields(fields: Optional[List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
    """Maps field list into a lookup dictionary keyed by normalized field name."""
    indexed: Dict[str, Dict[str, Any]] = {}
    if not fields:
        return indexed

    for f in fields:
        raw_name = f.get("field_name", "").lower().strip()
        # Canonicalize field name aliases
        canon_name = raw_name
        if raw_name in ["owner", "vendor_name", "purchaser_name", "holder_name", "patta_holder"]:
            canon_name = "owner_name"
        elif raw_name in ["survey_no", "sno", "sy_no", "survey"]:
            canon_name = "survey_number"
        elif raw_name in ["subdivision", "sub_division", "sub_no"]:
            canon_name = "subdivision_number"
        elif raw_name in ["area", "extent", "measurement"]:
            canon_name = "property_area"
        elif raw_name in ["address", "site_address"]:
            canon_name = "property_address"

        indexed[canon_name] = {
            "value": f.get("normalized_value") or f.get("original_value", ""),
            "original_value": f.get("original_value", ""),
            "page": f.get("page_number", 1),
            "confidence": f.get("confidence", 0.9),
        }
    return indexed


def _compare_field(field_name: str, values: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Compares field values across Patta, EC, and Sale Deed documents.
    
    Returns FieldComparison dict conforming to backend.models.property.FieldComparison.
    """
    patta_info = values.get("patta")
    ec_info = values.get("ec")
    sd_info = values.get("sale_deed")

    patta_val = patta_info.get("value") if patta_info else None
    ec_val = ec_info.get("value") if ec_info else None
    sd_val = sd_info.get("value") if sd_info else None

    # Available non-empty values
    active_sources = []
    if patta_val:
        active_sources.append(("Patta", patta_val))
    if ec_val:
        active_sources.append(("EC", ec_val))
    if sd_val:
        active_sources.append(("Sale Deed", sd_val))

    num_sources = len(active_sources)

    if num_sources == 0:
        return {
            "field_name": field_name,
            "patta_value": None,
            "ec_value": None,
            "sale_deed_value": None,
            "status": "not_available",
            "reason": f"Field '{field_name}' not found in any of the uploaded documents.",
            "patta_page": None,
            "ec_page": None,
            "sale_deed_page": None,
            "patta_confidence": None,
            "ec_confidence": None,
            "sale_deed_confidence": None,
        }

    if num_sources == 1:
        src_name, src_val = active_sources[0]
        return {
            "field_name": field_name,
            "patta_value": patta_val,
            "ec_value": ec_val,
            "sale_deed_value": sd_val,
            "status": "single_source",
            "reason": f"Value present only in {src_name} ('{src_val}'). Missing from other documents for cross-verification.",
            "patta_page": patta_info.get("page") if patta_info else None,
            "ec_page": ec_info.get("page") if ec_info else None,
            "sale_deed_page": sd_info.get("page") if sd_info else None,
            "patta_confidence": patta_info.get("confidence") if patta_info else None,
            "ec_confidence": ec_info.get("confidence") if ec_info else None,
            "sale_deed_confidence": sd_info.get("confidence") if sd_info else None,
        }

    # Multiple sources present - evaluate concordance
    vals = [s[1] for s in active_sources]
    names = [s[0] for s in active_sources]

    # Specific handling by field type
    if field_name == "owner_name":
        # Check all pairs for name similarity
        is_all_match = True
        is_all_ocr = True
        mismatches = []

        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                v1, v2 = vals[i], vals[j]
                if are_names_similar(v1, v2):
                    continue
                elif likely_ocr_error(v1, v2):
                    is_all_match = False
                else:
                    is_all_match = False
                    is_all_ocr = False
                    mismatches.append(f"{names[i]} ('{v1}') != {names[j]} ('{v2}')")

        if is_all_match:
            status = "match"
            reason = f"Owner name matches across {', '.join(names)}."
        elif is_all_ocr:
            status = "likely_ocr_error"
            reason = f"Minor spelling discrepancy likely caused by OCR scanning artifacts."
        else:
            status = "mismatch"
            reason = f"Owner name mismatch: {'; '.join(mismatches)}."

    elif field_name in ["survey_number", "subdivision_number"]:
        norm_vals = [normalize_survey_number(v) for v in vals]
        if all(nv == norm_vals[0] for nv in norm_vals):
            status = "match"
            reason = f"Survey number '{norm_vals[0]}' matches across all provided documents."
        elif all(likely_ocr_error(norm_vals[0], nv) for nv in norm_vals[1:]):
            status = "likely_ocr_error"
            reason = f"Survey number variance appears to be an OCR character misread (e.g. 0/O or 1/I)."
        else:
            status = "mismatch"
            reason = f"Discrepancy in survey number across documents: {dict(zip(names, norm_vals))}."

    elif field_name == "property_area":
        norm_areas = [normalize_area(v) for v in vals]
        valid_sqm = [a["value_sqm"] for a in norm_areas if a.get("value_sqm") is not None]

        if len(valid_sqm) >= 2:
            min_val = min(valid_sqm)
            max_val = max(valid_sqm)
            diff_pct = ((max_val - min_val) / max_val) * 100 if max_val > 0 else 0.0

            if diff_pct <= 5.0:
                status = "match"
                reason = f"Property areas match within 5% tolerance (variation: {round(diff_pct, 2)}%)."
            else:
                status = "mismatch"
                reason = f"Area discrepancy of {round(diff_pct, 2)}% exceeds the 5% tolerance threshold (values: {dict(zip(names, vals))})."
        else:
            # Fallback to textual comparison
            if all(v.strip().lower() == vals[0].strip().lower() for v in vals):
                status = "match"
                reason = "Area text matches across documents."
            else:
                status = "mismatch"
                reason = f"Unparseable or differing area values: {dict(zip(names, vals))}."

    else:
        # General address/taluk/village text comparison
        clean_vals = [v.strip().lower() for v in vals]
        if all(cv == clean_vals[0] for cv in clean_vals):
            status = "match"
            reason = f"Field '{field_name}' matches across {', '.join(names)}."
        elif all(likely_ocr_error(vals[0], v) for v in vals[1:]):
            status = "likely_ocr_error"
            reason = "Minor character differences consistent with OCR scanning noise."
        else:
            status = "mismatch"
            reason = f"Values differ between documents: {dict(zip(names, vals))}."

    return {
        "field_name": field_name,
        "patta_value": patta_val,
        "ec_value": ec_val,
        "sale_deed_value": sd_val,
        "status": status,
        "reason": reason,
        "patta_page": patta_info.get("page") if patta_info else None,
        "ec_page": ec_info.get("page") if ec_info else None,
        "sale_deed_page": sd_info.get("page") if sd_info else None,
        "patta_confidence": patta_info.get("confidence") if patta_info else None,
        "ec_confidence": ec_info.get("confidence") if ec_info else None,
        "sale_deed_confidence": sd_info.get("confidence") if sd_info else None,
    }


def _detect_red_flags(comparisons: List[Dict[str, Any]], all_fields: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Inspects comparison results and document dates to detect high-risk title red flags."""
    red_flags: List[Dict[str, Any]] = []

    comp_dict = {c["field_name"]: c for c in comparisons}

    # 1. Survey Number Mismatch
    survey_comp = comp_dict.get("survey_number")
    if survey_comp and survey_comp.get("status") == "mismatch":
        red_flags.append({
            "flag_id": f"rf_survey_{uuid.uuid4().hex[:8]}",
            "description": "Survey number mismatch across documents. Documents appear to refer to different cadastral land parcels.",
            "severity": "CRITICAL",
            "field_name": "survey_number",
            "recommendation": "Halt transaction until revenue authorities verify the correct survey/subdivision number via an official FMB sketch and Patta extract.",
            "requires_official_verification": True,
        })

    # 2. Owner Name Mismatch
    owner_comp = comp_dict.get("owner_name")
    if owner_comp and owner_comp.get("status") == "mismatch":
        red_flags.append({
            "flag_id": f"rf_owner_{uuid.uuid4().hex[:8]}",
            "description": "Owner / Vendor name discrepancy between Patta, Encumbrance Certificate, and Sale Deed.",
            "severity": "HIGH",
            "field_name": "owner_name",
            "recommendation": "Verify whether mutation of revenue records was carried out. Inquire for legal heir certificates or parent title documents showing transfer of title.",
            "requires_official_verification": True,
        })

    # 3. Property Area Discrepancy > 5%
    area_comp = comp_dict.get("property_area")
    if area_comp and area_comp.get("status") == "mismatch":
        red_flags.append({
            "flag_id": f"rf_area_{uuid.uuid4().hex[:8]}",
            "description": "Property area discrepancy exceeds the 5% acceptable variation threshold.",
            "severity": "HIGH",
            "field_name": "property_area",
            "recommendation": "Arrange an on-site physical measurement by a government-licensed surveyor and verify the boundary dimensions on the approved layout plan.",
            "requires_official_verification": True,
        })

    # 4. Encumbrance Certificate Date Coverage
    ec_start = all_fields.get("ec_start_date")
    ec_end = all_fields.get("ec_end_date")
    sd_date = all_fields.get("sale_deed_date")

    if sd_date and ec_end and ec_end < sd_date:
        red_flags.append({
            "flag_id": f"rf_ec_gap_{uuid.uuid4().hex[:8]}",
            "description": f"The Encumbrance Certificate search ends on {ec_end}, which is prior to the Sale Deed execution date ({sd_date}).",
            "severity": "HIGH",
            "field_name": "ec_period",
            "recommendation": "Obtain an updated Encumbrance Certificate covering the date of sale deed execution up to the present day.",
            "requires_official_verification": True,
        })

    return red_flags


def compare_property_documents(
    patta_fields: List[Dict[str, Any]],
    ec_fields: List[Dict[str, Any]],
    sale_deed_fields: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Compares extracted fields across Patta, EC, and Sale Deed.
    
    Returns structured dictionary matching backend.models.property.PropertyComparisonResponse:
    - field_comparisons: List[FieldComparison]
    - red_flags: List[RedFlag]
    - match_count: int
    - mismatch_count: int
    - not_available_count: int
    """
    patta_idx = _index_doc_fields(patta_fields)
    ec_idx = _index_doc_fields(ec_fields)
    sd_idx = _index_doc_fields(sale_deed_fields)

    # Collect union of all fields
    all_field_names = list(TARGET_FIELDS)
    for k in list(patta_idx.keys()) + list(ec_idx.keys()) + list(sd_idx.keys()):
        if k not in all_field_names and not k.startswith("_"):
            all_field_names.append(k)

    field_comparisons: List[Dict[str, Any]] = []
    match_count = 0
    mismatch_count = 0
    not_avail_count = 0

    for fname in all_field_names:
        values = {
            "patta": patta_idx.get(fname),
            "ec": ec_idx.get(fname),
            "sale_deed": sd_idx.get(fname),
        }
        comp = _compare_field(fname, values)
        field_comparisons.append(comp)

        st = comp.get("status")
        if st in ["match", "likely_ocr_error"]:
            match_count += 1
        elif st == "mismatch":
            mismatch_count += 1
        elif st == "not_available":
            not_avail_count += 1

    # Aggregate extracted dates for timeline check
    timeline_meta = {
        "ec_start_date": ec_idx.get("ec_start_date", {}).get("value"),
        "ec_end_date": ec_idx.get("ec_end_date", {}).get("value"),
        "sale_deed_date": sd_idx.get("registration_date", {}).get("value") or sd_idx.get("deed_date", {}).get("value"),
    }

    red_flags = _detect_red_flags(field_comparisons, timeline_meta)

    return {
        "field_comparisons": field_comparisons,
        "red_flags": red_flags,
        "match_count": match_count,
        "mismatch_count": mismatch_count,
        "not_available_count": not_avail_count,
    }
