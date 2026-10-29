"""Risk Analyzer Module for Nilaayam AI.

Evaluates legal agreement clauses against statutory benchmarks, assigns risk severities
(RED, YELLOW, GREEN, GREY), extracts explanations with hallucination guards, and flags missing clauses.
"""

import os
import re
import uuid
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

from legal_rag.retriever import retrieve_legal_references, get_reference_clauses
from agreement_analysis.clause_classifier import identify_missing_clauses

logger = logging.getLogger(__name__)


def _evaluate_rule_severity(clause_text: str, category: str) -> tuple[str, str]:
    """Applies rule-based heuristic tests to determine severity and initial rationale.
    
    Returns (severity, rule_reason).
    Severities: 'red', 'yellow', 'green', 'grey'.
    """
    text_lower = clause_text.lower()

    # Check for garbled or unreadable text
    clean_alpha = re.sub(r"[^a-zA-Z\u0B80-\u0BFF]", "", clause_text)
    if len(clause_text.strip()) < 15 or len(clean_alpha) < 8:
        return "grey", "Clause text appears corrupted, incomplete, or unreadable."

    if category == "rent_increase":
        # Extract percentage numbers
        pct_matches = re.findall(r"(\d+(?:\.\d+)?)\s*%", clause_text)
        if pct_matches:
            pct_val = float(pct_matches[0])
            if pct_val > 10.0:
                return "red", f"Rent increase of {pct_val}% per annum exceeds standard 5-10% benchmark."
            elif pct_val <= 10.0:
                return "green", f"Rent increase of {pct_val}% per annum is within the acceptable 5-10% standard."
        if any(w in text_lower for w in ["sole discretion", "unilateral", "without cap", "any amount", "at will"]):
            return "red", "Rent increase is at the sole discretion of the landlord without an agreed ceiling."
        if any(w in text_lower for w in ["mutual consent", "mutual agreement", "mutually agreed"]):
            return "green", "Rent increase requires mutual written consent of both parties."
        return "yellow", "Rent revision mechanism is mentioned but lacks an explicit cap or clear formula."

    elif category == "security_deposit":
        # Check deposit months
        month_matches = re.findall(r"(\d+)\s*(?:months?|மாத)", text_lower)
        if month_matches:
            months = int(month_matches[0])
            if months > 3:
                return "red", f"Security deposit of {months} months' rent exceeds modern statutory guideline of 2-3 months."
            elif months <= 3:
                return "green", f"Security deposit of {months} months' rent is reasonable and compliant with modern guidelines."
        if "non-refundable" in text_lower or "non refundable" in text_lower or "forfeited" in text_lower:
            return "red", "Security deposit is designated as non-refundable or liable to arbitrary forfeiture."
        if "refundable" in text_lower and any(w in text_lower for w in ["within", "days", "handover", "vacat"]):
            return "green", "Security deposit is explicitly stated as refundable with return conditions."
        return "yellow", "Security deposit terms do not clearly state refund conditions or return timeline."

    elif category == "deposit_refund":
        if any(w in text_lower for w in ["sole discretion", "no refund", "forfeited entirely", "arbitrary"]):
            return "red", "Deposit refund conditions grant unilateral deduction powers to landlord."
        if any(w in text_lower for w in ["within 15 days", "within 30 days", "within one month", "simultaneously with key handover"]):
            return "green", "Deposit refund timeline is clearly specified (within 15-30 days)."
        return "yellow", "Refund conditions are vague regarding exact timeline or inspection process."

    elif category == "notice_period":
        if any(w in text_lower for w in ["without notice", "zero notice", "immediate eviction", "forthwith", "24 hours"]):
            return "red", "Immediate termination or notice period under 15 days provides no security of tenure."
        month_matches = re.findall(r"(\d+)\s*(?:months?|மாத)", text_lower)
        day_matches = re.findall(r"(\d+)\s*(?:days?|நாட்கள்)", text_lower)
        if month_matches and int(month_matches[0]) >= 1:
            return "green", f"Notice period of {month_matches[0]} month(s) provides adequate advance transition time."
        if day_matches and int(day_matches[0]) >= 30:
            return "green", f"Notice period of {day_matches[0]} days is fair and standard."
        if any(w in text_lower for w in ["only the lessor", "only the landlord", "tenant shall not have right"]):
            return "red", "Notice right is one-sided and denied to the tenant."
        return "yellow", "Notice period duration or mode of delivery is ambiguous."

    elif category == "eviction":
        if any(w in text_lower for w in ["forcible", "lock out", "cut electricity", "disconnect water", "without court", "summary"]):
            return "red", "Self-help eviction or cutting essential services is illegal under Indian tenancy jurisprudence."
        if any(w in text_lower for w in ["court order", "rent court", "due process", "statutory notice", "30 days cure"]):
            return "green", "Eviction provisions respect due process and require prior statutory default notice."
        return "yellow", "Eviction clause lacks specified cure periods for minor non-monetary breaches."

    elif category == "penalties":
        if any(w in text_lower for w in ["compound interest", "5% per day", "10% per day", "forfeit all", "double the rent"]):
            return "red", "Exorbitant penalty or penal compounding interest clause may be deemed unconscionable."
        if any(w in text_lower for w in ["reasonable", "simple interest", "1% per month", "nominal"]):
            return "green", "Late payment penalty is capped and follows reasonable standard interest rates."
        return "yellow", "Late fee terms exist but exact rate or calculation method is unspecified."

    elif category == "maintenance":
        if any(w in text_lower for w in ["tenant shall bear all structural", "tenant shall pay all major", "landlord not responsible for anything"]):
            return "red", "Clause unbalanceably shifts heavy structural maintenance and capital liabilities onto tenant."
        if any(w in text_lower for w in ["landlord responsible for structural", "major repairs by lessor", "day to day by tenant"]):
            return "green", "Fair and balanced division between structural repairs (landlord) and day-to-day upkeep (tenant)."
        return "yellow", "Maintenance responsibility is broadly phrased without clear division of structural vs. minor repairs."

    elif category == "termination":
        if any(w in text_lower for w in ["unilateral right to cancel without reason", "no compensation"]):
            return "red", "One-sided immediate cancellation right heavily favors one party."
        if any(w in text_lower for w in ["mutual consent", "mutual agreement", "either party may terminate"]):
            return "green", "Mutual termination right with reciprocal rights."
        return "yellow", "Termination conditions or exit procedures are ambiguous."

    elif category == "rent_amount":
        if any(w in text_lower for w in ["subject to arbitrary addition", "landlord may unilaterally increase"]):
            return "red", "Base rent amount is subject to unilateral or unpredictable additions."
        if any(w in text_lower for w in ["rs.", "inr", "rupees", "/-", "payable on or before"]):
            return "green", "Rent consideration and monthly payment due date are explicitly defined."
        return "yellow", "Rent amount or payment due date is not clearly specified."

    # General default
    return "yellow", "Clause warrants careful legal verification."


def _generate_template_explanation(
    clause_text: str,
    category: str,
    severity: str,
    reason: str,
    has_ref: bool,
    language: str = "en"
) -> Dict[str, str]:
    """Generates structured explanation, Tamil translation, and suggested questions via robust templates."""
    
    base_explanations = {
        "rent_increase": {
            "red": (
                "This clause allows a steep or uncapped rent increase. In Tamil Nadu, rent increases are generally "
                "capped between 5% and 10% per year upon renewal. An uncapped or excessive increase creates financial instability."
            ),
            "yellow": "The rent increase clause mentions revision but does not clearly fix an annual percentage cap or formula.",
            "green": "The rent increase is well-defined and aligns with prevailing fair market standards.",
            "grey": "Rent escalation terms are absent or unreadable.",
        },
        "security_deposit": {
            "red": (
                "The required security deposit is excessive (greater than 3 months) or lacks clear refund guarantees. "
                "Under modern tenancy norms, residential deposits should not exceed 2-3 months' rent."
            ),
            "yellow": "Security deposit amount is mentioned, but exact deductions and refund conditions require clarification.",
            "green": "Security deposit is within reasonable limits and includes standard refund terms.",
            "grey": "Security deposit terms are missing from the agreement.",
        },
        "notice_period": {
            "red": (
                "The notice period is either absent, one-sided, or dangerously short. Both parties should have "
                "a mutual written notice period of at least 1 to 2 months."
            ),
            "yellow": "Notice period details are ambiguous regarding delivery method or timeline.",
            "green": "Notice period provides adequate mutual advance warning for both landlord and tenant.",
            "grey": "Mandatory notice period clause is missing from the document.",
        },
        "eviction": {
            "red": (
                "This clause allows unilateral or summary eviction without due process. In India, eviction requires "
                "statutory cause and formal judicial/tribunal proceedings under applicable tenancy law."
            ),
            "yellow": "Eviction terms do not explicitly provide a statutory cure period for minor non-monetary breaches.",
            "green": "Eviction clause complies with statutory due process requirements.",
            "grey": "Eviction terms are missing or unclear.",
        },
        "maintenance": {
            "red": "This clause places major structural or municipal liabilities on the tenant, which is unfair.",
            "yellow": "Responsibility for major repairs versus minor day-to-day maintenance is vaguely drafted.",
            "green": "Clause provides a fair and clear division between structural and day-to-day repairs.",
            "grey": "Maintenance obligations are not defined.",
        },
        "penalties": {
            "red": "Late payment penalties or interest rates are unreasonably punitive.",
            "yellow": "Penalty mechanisms exist but computation parameters are not fully detailed.",
            "green": "Late payment fees are nominal, capped, and reasonable.",
            "grey": "Penalty provisions are unspecified.",
        },
        "termination": {
            "red": "Termination clause is heavily one-sided, exposing one party to sudden lease termination.",
            "yellow": "Grounds for termination and procedure for handover are partially ambiguous.",
            "green": "Mutual termination rights are clearly and equitably documented.",
            "grey": "Termination clause is missing.",
        },
        "deposit_refund": {
            "red": "Deposit refund terms permit arbitrary deductions or lack a binding return timeline.",
            "yellow": "Return timeline for the security deposit is not explicitly committed.",
            "green": "Deposit refund timeline (15-30 days) and inspection mechanism are explicitly defined.",
            "grey": "Deposit refund terms are omitted.",
        },
        "rent_amount": {
            "red": "Rent amount is indeterminate or subject to unilateral alteration.",
            "yellow": "Rent amount is specified but payment mode or grace period is ambiguous.",
            "green": "Monthly rent amount and payment schedule are clearly stated.",
            "grey": "Monthly rent consideration is missing from the agreement.",
        },
    }

    tamil_explanations = {
        "rent_increase": {
            "red": "வாடகை உயர்வு விகிதம் 10% க்கும் அதிகமாக உள்ளது அல்லது வரம்பற்றதாக உள்ளது. இது குத்தகைதாரருக்கு நிதிச்சுமையை ஏற்படுத்தும்.",
            "yellow": "வாடகை உயர்வு பற்றிய விதி தெளிவான உச்சவரம்பு இல்லாமல் குறிப்பிடப்பட்டுள்ளது.",
            "green": "வாடகை உயர்வு விதிமுறை நியாயமான வரம்பிற்குள் (5-10%) உள்ளது.",
            "grey": "வாடகை உயர்வு பற்றிய நிபந்தனை தெளிவாக இல்லை.",
        },
        "security_deposit": {
            "red": "முன்பணத் தொகை 3 மாத வாடகைக்கு மேல் அதிகமாக உள்ளது அல்லது திரும்பப் பெறுவது பற்றிய பாதுகாப்பு இல்லை.",
            "yellow": "முன்பணம் திரும்பப் பெறுவதற்கான கால அவகாசம் தெளிவாக குறிப்பிடப்படவில்லை.",
            "green": "முன்பணத் தொகை நியாயமான வரம்பிற்குள் உள்ளது.",
            "grey": "முன்பணம் பற்றிய விதி விடுபட்டுள்ளது.",
        },
        "notice_period": {
            "red": "முன்னறிவிப்பு காலம் மிகக் குறைவாக உள்ளது அல்லது ஒருதலைப்பட்சமாக உள்ளது. குறைந்தபட்சம் 1-2 மாத முன்னறிவிப்பு தேவை.",
            "yellow": "முன்னறிவிப்பு காலம் பற்றிய விவரங்கள் தெளிவின்றி உள்ளன.",
            "green": "முன்னறிவிப்பு காலம் இரு தரப்பினருக்கும் போதுமான அவகாசத்தை வழங்குகிறது.",
            "grey": "முன்னறிவிப்பு விதி ஒப்பந்தத்தில் விடுபட்டுள்ளது.",
        },
        "eviction": {
            "red": "நீதிமன்ற உத்தரவின்றி திடீரென வெளியேற்ற வழிவகுக்கும் விதி சட்டப்படி செல்லாது.",
            "yellow": "வெளியேற்றுதல் நடைமுறையில் குறைபாடுகளை சரிசெய்ய போதிய அவகாசம் குறிப்பிடப்படவில்லை.",
            "green": "வெளியேற்றுதல் விதிமுறை சட்ட நடைமுறைகளுக்கு உட்பட்டுள்ளது.",
            "grey": "வெளியேற்றுதல் விதிமுறை விடுபட்டுள்ளது.",
        },
        "maintenance": {
            "red": "கட்டிடத்தின் முக்கிய பழுதுபார்ப்பு பொறுப்பை குத்தகைதாரர் மீது சுமத்துவது முறையற்றது.",
            "yellow": "பராமரிப்பு பொறுப்புகள் தெளிவாக பிரிக்கப்படவில்லை.",
            "green": "பராமரிப்பு பொறுப்பு இரு தரப்பினருக்கும் நியாயமாக பிரிக்கப்பட்டுள்ளது.",
            "grey": "பராமரிப்பு பொறுப்புகள் குறிப்பிடப்படவில்லை.",
        },
    }

    questions = {
        "rent_increase": "Can we specify that any annual rent increase will be capped at a maximum of 5% upon mutual agreement?",
        "security_deposit": "Can the agreement specify that the security deposit will be fully refunded within 15-30 days of vacating?",
        "notice_period": "Can we include a clause requiring at least 2 months' written notice by either party prior to termination?",
        "eviction": "Can the agreement confirm that eviction will follow statutory due process with a 30-day written rectification notice?",
        "maintenance": "Can we clarify that major structural repairs are the owner's responsibility while day-to-day minor upkeep is by the tenant?",
        "penalties": "Can any late fee be capped at a reasonable simple interest rate of 1% per month?",
        "termination": "Can both parties have equal and mutual rights to terminate the agreement with standard notice?",
        "deposit_refund": "What is the exact deadline and joint inspection procedure for refunding the security deposit?",
        "rent_amount": "Can the exact monthly rent amount and grace period be explicitly specified?",
    }

    cat_map = base_explanations.get(category, {})
    exp = cat_map.get(severity, f"Analysis for {category}: {reason}")
    
    cat_ta_map = tamil_explanations.get(category, {})
    exp_ta = cat_ta_map.get(severity, f"{category} பிரிவு பற்றிய சட்ட ஆலோசனை தேவைப்படுகிறது.")

    sug_q = questions.get(category, f"Can we review and clarify the specific terms of the {category} clause?")

    # Hallucination Guard
    if not has_ref:
        exp += " (Requires verification - consult a qualified legal professional)."
        exp_ta += " (சரிபார்ப்பு தேவை - தகுதியான வழக்கறிஞரை அணுகவும்)."

    return {
        "explanation": exp,
        "explanation_ta": exp_ta,
        "reason": reason,
        "suggested_question": sug_q,
    }


def _generate_explanation_llm(
    clause_text: str,
    category: str,
    severity: str,
    reference: str,
    language: str = "en"
) -> Dict[str, str]:
    """Uses Google Gemini with structured JSON output to generate refined explanations.
    
    Falls back gracefully to template explanation on any error or missing key.
    """
    has_ref = bool(reference and len(reference.strip()) > 10)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key and settings and getattr(settings, "gemini_api_key", None):
        api_key = settings.gemini_api_key

    if not (HAS_GENAI and api_key):
        return _generate_template_explanation(clause_text, category, severity, f"Evaluated under {category} standards.", has_ref, language)

    try:
        genai.configure(api_key=api_key)
        model_name = getattr(settings, "llm_model", "gemini-1.5-flash") if settings else "gemini-1.5-flash"
        model = genai.GenerativeModel(model_name)

        prompt = f"""You are Nilaayam AI, a legal document assistant specializing in Tamil Nadu real estate and tenancy agreements.
Analyze the following clause and produce a clear, plain-language risk assessment in English and Tamil.

Clause Category: {category}
Assigned Severity: {severity.upper()}
Clause Text: "{clause_text}"
Statutory Reference Available: "{reference if has_ref else 'None'}"

Instructions:
1. Explain clearly WHY this clause is classified as {severity}.
2. Provide a simple Tamil translation/explanation of the risk.
3. Suggest 1 practical, actionable negotiation question for the user to ask the landlord or drafter.
4. If no statutory reference was provided, explicitly include: "Requires verification - consult a legal professional".

Output format: Return ONLY a JSON object with keys:
{{
  "explanation": "<plain English explanation>",
  "explanation_ta": "<clear Tamil explanation>",
  "reason": "<concise 1-sentence legal reason>",
  "suggested_question": "<specific question to negotiate>"
}}
"""
        response = model.generate_content(prompt)
        text_resp = response.text.strip()
        if text_resp.startswith("```json"):
            text_resp = text_resp[7:]
        if text_resp.startswith("```"):
            text_resp = text_resp[3:]
        if text_resp.endswith("```"):
            text_resp = text_resp[:-3]

        parsed = json.loads(text_resp.strip())
        exp = parsed.get("explanation", "")
        exp_ta = parsed.get("explanation_ta", "")
        reason = parsed.get("reason", "")
        sug_q = parsed.get("suggested_question", "")

        # Enforce Hallucination Guard
        if not has_ref and "Requires verification" not in exp:
            exp += " Requires verification - consult a legal professional."
            exp_ta += " சரிபார்ப்பு தேவை - சட்ட வல்லுநரை அணுகவும்."

        return {
            "explanation": exp,
            "explanation_ta": exp_ta,
            "reason": reason or f"Assessed as {severity} under {category} guidelines.",
            "suggested_question": sug_q or f"Can we clarify the {category} terms?",
        }
    except Exception as e:
        logger.warning(f"LLM explanation generation failed: {e}. Using template.")
        return _generate_template_explanation(clause_text, category, severity, f"Evaluated under {category} standards.", has_ref, language)


def _analyze_clause(
    clause: Dict[str, Any],
    refs: List[Dict[str, Any]],
    language: str = "en"
) -> Dict[str, Any]:
    """Analyzes a single classified clause, determines risk severity, and attaches legal references."""
    clause_text = clause.get("clause_text", "")
    category = clause.get("category", "other")
    page_number = clause.get("page_number", 1)

    severity, rule_reason = _evaluate_rule_severity(clause_text, category)

    ref_excerpt = ""
    if refs:
        ref_excerpt = f"{refs[0].get('title', '')} ({refs[0].get('section', '')}): {refs[0].get('excerpt', '')}"

    llm_content = _generate_explanation_llm(
        clause_text=clause_text,
        category=category,
        severity=severity,
        reference=ref_excerpt,
        language=language
    )

    finding_id = f"fnd_{uuid.uuid4().hex[:12]}"

    return {
        "finding_id": finding_id,
        "document_id": clause.get("document_id", "doc_default"),
        "clause_text": clause_text,
        "clause_category": category,
        "page_number": page_number,
        "severity": severity,
        "explanation": llm_content["explanation"],
        "explanation_ta": llm_content["explanation_ta"],
        "reason": llm_content["reason"] or rule_reason,
        "legal_references": refs,
        "reference_comparison": ref_excerpt if ref_excerpt else None,
        "suggested_question": llm_content["suggested_question"],
        "confidence": clause.get("confidence", 0.8),
        "is_missing_clause": False,
    }


def analyze_agreement(
    clauses: List[Dict[str, Any]],
    references: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    language: str = "en"
) -> List[Dict[str, Any]]:
    """Performs end-to-end risk analysis on agreement clauses.
    
    1. Evaluates each extracted clause and maps severity (RED, YELLOW, GREEN, GREY).
    2. Identifies missing mandatory clauses and synthesizes GREY findings.
    3. Attaches retrieved statutory references and hallucination guards.
    """
    findings: List[Dict[str, Any]] = []
    found_categories = [c.get("category", "other") for c in clauses]

    for clause in clauses:
        cat = clause.get("category", "other")
        clause_text = clause.get("clause_text", "")

        # Get relevant references from pre-supplied dict or retrieve on the fly
        clause_refs: List[Dict[str, Any]] = []
        if references and cat in references:
            clause_refs = references[cat]
        elif len(clause_text.strip()) > 10:
            clause_refs = retrieve_legal_references(clause_text, doc_type="rental_agreement", top_k=2)

        finding = _analyze_clause(clause, clause_refs, language=language)
        findings.append(finding)

    # Check for missing required clauses and add GREY findings
    missing_cats = identify_missing_clauses(found_categories)
    for missing_cat in missing_cats:
        missing_refs = retrieve_legal_references(f"mandatory {missing_cat} requirement", doc_type="rental_agreement", top_k=1)
        ref_excerpt = ""
        if missing_refs:
            ref_excerpt = f"{missing_refs[0].get('title', '')}: {missing_refs[0].get('excerpt', '')}"

        missing_explanation = (
            f"The agreement completely omits a '{missing_cat.replace('_', ' ').title()}' clause. "
            f"Having an explicit clause for {missing_cat.replace('_', ' ')} is essential to protect both parties and prevent future disputes."
        )
        missing_explanation_ta = f"இந்த ஒப்பந்தத்தில் '{missing_cat}' பற்றிய முக்கிய விதி விடுபட்டுள்ளது. இது குறித்து முன்கூட்டியே முடிவு செய்ய வேண்டும்."

        if not missing_refs:
            missing_explanation += " Requires verification - consult a legal professional."
            missing_explanation_ta += " சரிபார்ப்பு தேவை - சட்ட வல்லுநரை அணுகவும்."

        benchmarks = get_reference_clauses(missing_cat)
        model_clause = benchmarks[0]["clause_text"] if benchmarks else "Standard mutual clause."

        findings.append({
            "finding_id": f"fnd_missing_{uuid.uuid4().hex[:8]}",
            "document_id": clauses[0].get("document_id", "doc_default") if clauses else "doc_default",
            "clause_text": f"[MISSING CLAUSE: {missing_cat.upper()}] - No clause found for {missing_cat.replace('_', ' ')}.",
            "clause_category": missing_cat,
            "page_number": 1,
            "severity": "grey",
            "explanation": missing_explanation,
            "explanation_ta": missing_explanation_ta,
            "reason": f"Mandatory standard provision for {missing_cat.replace('_', ' ')} was not detected in the document.",
            "legal_references": missing_refs,
            "reference_comparison": f"Recommended Benchmark: {model_clause}",
            "suggested_question": f"Can we include a standard balanced clause defining {missing_cat.replace('_', ' ')}?",
            "confidence": 0.9,
            "is_missing_clause": True,
        })

    return findings
