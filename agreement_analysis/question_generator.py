"""Question Generator Module for Nilaayam AI.

Synthesizes tailored, actionable negotiation questions for agreement findings.
Prioritizes RED high-risk clauses, followed by YELLOW and missing GREY clauses.
"""

import re
import os
import json
import logging
from typing import List, Dict, Optional, Any

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


def _question_template(category: str, severity: str, clause_text: str) -> str:
    """Generates a context-aware question based on clause text and category."""
    cat = (category or "").lower().strip()
    text = clause_text.strip() if clause_text else ""

    # Rent Increase
    if cat == "rent_increase":
        pcts = re.findall(r"(\d+(?:\.\d+)?)\s*%", text)
        if pcts and float(pcts[0]) > 10:
            return f"The current clause specifies a {pcts[0]}% rent escalation. Can we cap the annual rent increase at 5% to 7% instead?"
        elif any(w in text.lower() for w in ["sole discretion", "unilateral", "any amount"]):
            return "Can we replace the landlord's unilateral rent revision with a fixed annual cap of 5% upon mutual written agreement?"
        return "Can the annual rent increase be capped at a specific percentage (such as 5% to 7%) upon mutual agreement?"

    # Security Deposit
    elif cat == "security_deposit":
        months = re.findall(r"(\d+)\s*(?:months?|மாத)", text.lower())
        if months and int(months[0]) > 3:
            return f"The agreement requires {months[0]} months' rent as deposit. Can we adjust this closer to the 2-3 months standard recommended by modern tenancy guidelines?"
        if "non-refundable" in text.lower():
            return "The clause terms the deposit non-refundable. Can it be clarified as a fully refundable security deposit?"
        return "Under what exact conditions and timeline will the deposit be refunded, and can deductions be limited to verified damages?"

    # Deposit Refund
    elif cat == "deposit_refund":
        return "Can we stipulate that the security deposit will be refunded in full within 15 to 30 days of vacation following a joint inspection?"

    # Notice Period
    elif cat == "notice_period":
        if any(w in text.lower() for w in ["without notice", "zero notice", "immediate", "forthwith"]):
            return "Can we include a standard mutual written notice period of at least 2 months prior to lease termination?"
        return "What is the required notice period for both the tenant and landlord, and can it be reciprocal for both parties?"

    # Eviction
    elif cat == "eviction":
        return "Can the agreement confirm that eviction will follow statutory due process under tenancy laws, with a mandatory 30-day written cure notice?"

    # Maintenance
    elif cat == "maintenance":
        return "Can the clause explicitly state that the landlord is responsible for structural repairs and main utilities, while the tenant handles minor day-to-day upkeep?"

    # Penalties
    elif cat == "penalties":
        rates = re.findall(r"(\d+(?:\.\d+)?)\s*%", text)
        if rates:
            return f"Can the late payment charge of {rates[0]}% be revised to a reasonable simple interest rate not exceeding 1% to 1.5% per month?"
        return "Can late payment interest be capped at a reasonable simple rate of 1% per month with a 5-day grace period?"

    # Termination
    elif cat == "termination":
        return "Can both parties be provided an equal and mutual right to terminate the agreement by serving advance written notice?"

    # Rent Amount
    elif cat == "rent_amount":
        return "Can the exact monthly rent consideration, payment mode, and monthly due date (e.g., 5th of each month) be explicitly specified?"

    # Registration
    elif cat == "registration":
        return "Will this agreement be registered with the Sub-Registrar / Rent Authority as required by law, and how will registration fees be shared?"

    # Fallback default
    if severity == "red":
        return f"Regarding the {cat.replace('_', ' ')} terms: Can this clause be revised to align with standard balanced tenancy protections?"
    elif severity == "yellow":
        return f"Regarding the {cat.replace('_', ' ')} terms: Can the specific timelines and mutual obligations be clarified in writing?"
    else:
        return f"Can we include a standard clause defining rights and responsibilities for {cat.replace('_', ' ')}?"


def _generate_llm_questions_for_finding(finding: Dict[str, Any]) -> List[str]:
    """Generates highly customized questions using Gemini for a high-risk finding."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key and settings and getattr(settings, "gemini_api_key", None):
        api_key = settings.gemini_api_key

    if not (HAS_GENAI and api_key):
        return []

    try:
        genai.configure(api_key=api_key)
        model_name = getattr(settings, "llm_model", "gemini-1.5-flash") if settings else "gemini-1.5-flash"
        model = genai.GenerativeModel(model_name)

        prompt = f"""You are an expert Indian tenancy and property contract negotiator.
Given this agreement finding, formulate 1 or 2 polite, highly specific, and firm negotiation questions for the user to present to the landlord/counterparty.

Clause Category: {finding.get('clause_category')}
Severity: {finding.get('severity')}
Clause Text: "{finding.get('clause_text')}"
Risk Reason: "{finding.get('reason')}"

Return ONLY a JSON array of strings, e.g. ["Question 1", "Question 2"].
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
        if isinstance(parsed, list):
            return [str(q).strip() for q in parsed if str(q).strip()]
    except Exception as e:
        logger.warning(f"LLM question generation failed: {e}")

    return []


def generate_questions(findings: List[Dict[str, Any]]) -> List[str]:
    """Generates a prioritized list of up to 10 specific negotiation questions based on findings.
    
    Priority order:
    1. RED findings (1-2 questions each)
    2. YELLOW findings (1 question each)
    3. GREY missing clauses (1 question each)
    """
    questions: List[str] = []
    seen_questions = set()

    def add_q(q: str):
        if not q or not q.strip():
            return
        clean_q = q.strip()
        # Simple deduplication key
        norm_key = re.sub(r"[^a-zA-Z0-9]", "", clean_q.lower())[:60]
        if norm_key not in seen_questions:
            seen_questions.add(norm_key)
            questions.append(clean_q)

    # 1. Process RED findings first
    red_findings = [f for f in findings if f.get("severity") == "red"]
    for f in red_findings:
        # Check if finding already has a good suggested question
        if f.get("suggested_question"):
            add_q(f["suggested_question"])

        # Try LLM or template for additional specific question
        llm_qs = _generate_llm_questions_for_finding(f)
        for q in llm_qs:
            add_q(q)

        tmpl_q = _question_template(f.get("clause_category", ""), "red", f.get("clause_text", ""))
        add_q(tmpl_q)

        if len(questions) >= 10:
            return questions[:10]

    # 2. Process YELLOW findings
    yellow_findings = [f for f in findings if f.get("severity") == "yellow"]
    for f in yellow_findings:
        if f.get("suggested_question"):
            add_q(f["suggested_question"])
        else:
            tmpl_q = _question_template(f.get("clause_category", ""), "yellow", f.get("clause_text", ""))
            add_q(tmpl_q)

        if len(questions) >= 10:
            return questions[:10]

    # 3. Process GREY (Missing clauses)
    grey_findings = [f for f in findings if f.get("severity") == "grey" or f.get("is_missing_clause")]
    for f in grey_findings:
        if f.get("suggested_question"):
            add_q(f["suggested_question"])
        else:
            tmpl_q = _question_template(f.get("clause_category", ""), "grey", f.get("clause_text", ""))
            add_q(tmpl_q)

        if len(questions) >= 10:
            return questions[:10]

    # 4. Process GREEN findings if fewer than 3 questions generated
    if len(questions) < 3:
        for f in findings:
            if f.get("severity") == "green" and f.get("suggested_question"):
                add_q(f["suggested_question"])
                if len(questions) >= 5:
                    break

    return questions[:10]
