import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

# Configuration
from backend.config import settings

# Attempt imports with graceful fallbacks
try:
    from backend.database import get_supabase
except ImportError:
    get_supabase = None

try:
    from backend.services.analysis_orchestrator import (
        get_document_store,
        orchestrate_agreement_analysis,
    )
except ImportError:
    get_document_store = None
    orchestrate_agreement_analysis = None

logger = logging.getLogger("nilaayam.routers.agreements")

router = APIRouter(prefix="/agreements", tags=["agreements"])


# Pydantic Schemas
class Finding(BaseModel):
    id: str
    clause_title: str
    clause_text: Optional[str] = None
    risk_level: str = Field(..., description="'red' (high risk), 'yellow' (caution), or 'green' (compliant)")
    category: str
    issue: str
    issue_tamil: Optional[str] = None
    legal_reference: str
    legal_provision_details: str
    recommendation: str
    recommendation_tamil: Optional[str] = None
    suggested_clause: Optional[str] = None


class AgreementAnalysisRequest(BaseModel):
    document_id: str
    language: str = Field(default="en", description="Preferred response language ('en', 'ta')")


class AgreementAnalysisResponse(BaseModel):
    analysis_id: str
    document_id: str
    status: str
    language: str
    risk_score: float = Field(..., description="Overall risk index from 0 (safe) to 100 (critical risk)")
    risk_level: str = Field(..., description="'High Risk', 'Medium Risk', or 'Low Risk'")
    findings: List[Finding]
    clauses_analyzed: int
    recommended_questions: List[str]
    summary: str
    summary_tamil: Optional[str] = None
    stats: Dict[str, int] = Field(default_factory=dict)
    questions_to_ask: List[str] = Field(default_factory=list)
    document_name: Optional[str] = None
    is_demo: bool = False
    created_at: str


class ReportResponse(BaseModel):
    report_id: str
    analysis_id: str
    document_id: str
    document_name: str
    property_type: str = "Residential Tenancy Agreement"
    risk_score: float
    risk_level: str
    summary: str
    summary_tamil: Optional[str] = None
    red_count: int
    yellow_count: int
    green_count: int
    findings: List[Finding]
    questions_for_landlord: List[str]
    legal_provisions_cited: List[str]
    is_demo: bool = False
    created_at: str


# In-memory stores for results when Supabase is not configured
DEMO_ANALYSIS_STORE: Dict[str, AgreementAnalysisResponse] = {}
DEMO_REPORT_STORE: Dict[str, ReportResponse] = {}


def is_supabase_enabled() -> bool:
    """Check if Supabase credentials are configured."""
    return bool(
        settings.supabase_url
        and (settings.supabase_service_role_key or settings.supabase_anon_key)
    )


def validate_uuid(val: str, field_name: str = "id") -> str:
    """Validate string UUID format."""
    try:
        return str(uuid.UUID(str(val).strip()))
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name} format: '{val}'. Expected valid UUID.",
        )


def build_sample_agreement_findings() -> List[Finding]:
    """
    Constructs realistic rental agreement findings:
    - 3 RED findings:
        1. missing notice period clause
        2. unlimited rent increase clause
        3. vague deposit refund condition
    - 2 YELLOW findings:
        1. maintenance responsibility unclear
        2. penalty clause one-sided
    - 1 GREEN finding:
        1. rent amount clearly stated
    """
    return [
        # RED 1: Missing notice period clause
        Finding(
            id="FINDING-RED-001",
            clause_title="Missing Notice Period Clause",
            clause_text="[Not specified in agreement]",
            risk_level="red",
            category="Tenancy Termination & Eviction",
            issue=(
                "The agreement lacks an explicit mandatory notice period for terminating tenancy or vacating the flat. "
                "Without a defined bilateral notice period, the tenant faces sudden eviction risk, and landlord can claim immediate forfeiture."
            ),
            issue_tamil=(
                "வாடகை ஒப்பந்தத்தில் வீட்டை காலி செய்வதற்கான முன்னறிவிப்பு காலம் (Notice Period) விடுபட்டுள்ளது. "
                "இதனால் நில உரிமையாளர் திடீரென காலி செய்ய வற்புறுத்த வாய்ப்புள்ளது."
            ),
            legal_reference="Section 106, Transfer of Property Act, 1882 & TNRRRLT Act 2017 Section 21",
            legal_provision_details=(
                "Under Section 106 of the Transfer of Property Act, 1882, month-to-month tenancies require at least 15 days "
                "prior written notice expiring with the end of a tenancy month. Furthermore, under the Tamil Nadu Regulation of "
                "Rights and Responsibilities of Landlords and Tenants Act, 2017 (TNRRRLT Act 2017), eviction is strictly restricted "
                "to defined statutory grounds and requires due process before the Rent Authority."
            ),
            recommendation="Insert a reciprocal 30-day (or 60-day) written notice clause binding on both lessor and lessee.",
            recommendation_tamil="இரு தரப்பினருக்கும் பொருந்தக்கூடிய 30 முதல் 60 நாட்கள் எழுத்துப்பூர்வ முன்னறிவிப்பு விதியை ஒப்பந்தத்தில் சேர்க்க வேண்டும்.",
            suggested_clause=(
                "Either party may terminate this agreement by providing a minimum of 30 (thirty) days written notice to the other party. "
                "The lessee shall deliver vacant and peaceful possession upon the expiry of said notice period."
            ),
        ),
        # RED 2: Unlimited rent increase clause
        Finding(
            id="FINDING-RED-002",
            clause_title="Clause 5: Arbitrary Rent Escalation",
            clause_text="The Lessor reserves the right to increase the monthly rent at any time during the lease period as per market conditions.",
            risk_level="red",
            category="Rent Revision & Commercial Terms",
            issue=(
                "Clause 5 permits the landlord to unilaterally increase the monthly rent at will during the 11-month lease term "
                "without any fixed cap, formula, or mutual agreement."
            ),
            issue_tamil=(
                "ஒப்பந்த காலத்தில் நில உரிமையாளர் எப்போது வேண்டுமானாலும் தனது விருப்பப்படி வாடகையை உயர்த்தலாம் என்ற ஒருதலைப்பட்ச விதி உள்ளது. "
                "இது வாடகைதாரருக்கு அதிக நிதிச்சுமையை ஏற்படுத்தும்."
            ),
            legal_reference="TNRRRLT Act 2017, Section 9 & Section 10",
            legal_provision_details=(
                "Sections 9 and 10 of the TNRRRLT Act 2017 explicitly mandate that revision of rent must follow strictly agreed terms "
                "recorded in writing. Unilateral increases during an ongoing lease tenure without agreed schedule are contrary to law."
            ),
            recommendation="Remove unilateral increase power; fix rent for the entire 11-month tenure with max 5% escalation upon renewal.",
            recommendation_tamil="11 மாத ஒப்பந்த காலத்தில் வாடகையை மாற்றக்கூடாது என்றும், புதுப்பிக்கும் போது 5% மட்டுமே உயர்த்தப்பட வேண்டும் என்றும் மாற்றவும்.",
            suggested_clause=(
                "The monthly rent shall remain fixed at Rs. 22,000/- for the entire 11-month tenure. In case of renewal by mutual consent, "
                "rent escalation shall not exceed 5% (five percent) per annum."
            ),
        ),
        # RED 3: Vague deposit refund condition
        Finding(
            id="FINDING-RED-003",
            clause_title="Clause 4: Vague Security Deposit Deductions",
            clause_text=(
                "The security deposit of Rs. 1,50,000/- shall be refunded without interest upon vacating, "
                "subject to deductions for repairs or renovations as determined solely by the Lessor."
            ),
            risk_level="red",
            category="Security Deposit Protection",
            issue=(
                "Refund of the substantial deposit (Rs. 1,50,000) has no committed timeline, and deductions are left to the landlord's "
                "sole subjective discretion without providing bills, estimates, or accounting for normal wear and tear."
            ),
            issue_tamil=(
                "முன்பணம் (₹1,50,000) திருப்பித் தரும் போது பழுதுபார்ப்புக்கான தொகையை நில உரிமையாளரே தன்னிச்சையாக முடிவு செய்து பிடித்தம் செய்யலாம் "
                "என்றும், எப்போது திருப்பித் தரவேண்டும் என்ற காலக்கெடுவும் இல்லை."
            ),
            legal_reference="TNRRRLT Act 2017, Section 13(1)",
            legal_provision_details=(
                "Under Section 13(1) of the TNRRRLT Act 2017, the security deposit must be refunded to the tenant within one month "
                "of vacating premises, after lawful deductions for documented arrears or damages caused by tenant negligence."
            ),
            recommendation="Specify that the security deposit must be refunded within 15 days of handover, excluding reasonable wear and tear, with itemized contractor bills.",
            recommendation_tamil="வீட்டை ஒப்படைத்த 15 நாட்களுக்குள் முன்பணம் திருப்பித் தரப்பட வேண்டும் எனவும், சாதாரண தேய்மானத்திற்கு பிடித்தம் செய்யக்கூடாது எனவும் சேர்க்கவும்.",
            suggested_clause=(
                "The Lessor shall refund the entire interest-free security deposit of Rs. 1,50,000/- within 15 (fifteen) calendar days of "
                "peaceful handover. Any deduction for damages (excluding normal wear and tear) must be supported by verifiable third-party receipts."
            ),
        ),
        # YELLOW 1: Maintenance responsibility unclear
        Finding(
            id="FINDING-YEL-001",
            clause_title="Clause 6: Ambiguous Maintenance Responsibilities",
            clause_text="All maintenance and repair charges arising during tenancy shall be borne exclusively by the Lessee.",
            risk_level="yellow",
            category="Maintenance & Repairs",
            issue=(
                "The clause fails to distinguish between minor day-to-day tenant repairs and major capital/structural repairs "
                "(e.g., roof leakage, internal conduit plumbing, external seepage), shifting structural burdens to the tenant."
            ),
            issue_tamil=(
                "வீட்டின் அனைத்து பழுதுபார்ப்பு செலவுகளையும் வாடகைதாரரே ஏற்க வேண்டும் என கூறப்பட்டுள்ளது. கட்டமைப்பு மற்றும் பெரும் பழுதுகள் "
                "நில உரிமையாளரின் பொறுப்பு என பிரிக்கப்படவில்லை."
            ),
            legal_reference="TNRRRLT Act 2017, Second Schedule (Division of Maintenance Responsibilities)",
            legal_provision_details=(
                "The Second Schedule of TNRRRLT Act 2017 bifurcates maintenance obligations: structural repairs, roof leakages, and external "
                "painting belong strictly to the landlord, while routine minor wear-and-tear items (washers, switches) belong to the tenant."
            ),
            recommendation="Clarify that structural and plumbing mainline repairs are landlord obligations; cap tenant repairs to minor items under Rs. 1,000.",
            recommendation_tamil="கட்டமைப்பு பழுதுகளை நில உரிமையாளரும், சிறு பழுதுகளை (ரூ. 1,000-க்குள்) வாடகைதாரரும் ஏற்பார்கள் என தெளிவாக பிரிக்க வேண்டும்.",
            suggested_clause=(
                "The Lessor shall bear all major repairs, structural defects, external seepage, and mainline plumbing. "
                "The Lessee shall be responsible only for minor routine repairs (faucets, fuses) not exceeding Rs. 1,000 per instance."
            ),
        ),
        # YELLOW 2: Penalty clause one-sided
        Finding(
            id="FINDING-YEL-002",
            clause_title="Clause 7: Disproportionate & One-Sided Penalty",
            clause_text="Late rent attracts 18% monthly interest; Lessor may lock premises without notice after 7 days non-payment.",
            risk_level="yellow",
            category="Penalties & Self-Help Remedies",
            issue=(
                "An exorbitant interest rate of 18% per month (216% per annum) is imposed solely on the tenant. Furthermore, the clause "
                "purports to authorize the landlord to lock premises extra-judicially, which is unlawful under Indian tenancy jurisprudence."
            ),
            issue_tamil=(
                "வாடகை தாமதத்திற்கு மாதம் 18% அபராத வட்டி மற்றும் வீட்டை பூட்டும் அதிகாரம் நில உரிமையாளருக்கு தரப்பட்டுள்ளது. இது சட்டவிரோதமானது."
            ),
            legal_reference="Section 74, Indian Contract Act, 1872 & Section 20, TNRRRLT Act 2017",
            legal_provision_details=(
                "Section 74 of the Indian Contract Act bars unreasonable penalty stipulations. Section 20 of the TNRRRLT Act 2017 "
                "strictly prohibits landlords from withholding essential supplies or dispossessing tenants without Rent Court process."
            ),
            recommendation="Remove the unilateral lock-out clause and revise the late fee to a standard reasonable rate (e.g., Rs. 50/day after a 7-day grace period).",
            recommendation_tamil="வீட்டை பூட்டும் விதியை நீக்க வேண்டும் மற்றும் தாமதக் கட்டணத்தை நியாயமான அளவில் (தினசரி ரூ. 50) நிர்ணயிக்க வேண்டும்.",
            suggested_clause=(
                "In case of rent payment delay beyond a 7-day grace period, a nominal late fee of Rs. 50/- per day shall be payable. "
                "Neither party shall disrupt essential services or resort to extra-legal self-help measures."
            ),
        ),
        # GREEN 1: Rent amount clearly stated
        Finding(
            id="FINDING-GRN-001",
            clause_title="Clause 3: Clear Monthly Rent & Payment Channel",
            clause_text="Monthly rent is fixed at Rs. 22,000/- payable on or before 5th of each English calendar month through NEFT/UPI/Bank Transfer.",
            risk_level="green",
            category="Rent Certainty & Payment Proof",
            issue="Monthly rent consideration, exact calendar due date, and verified digital payment channels are explicitly defined.",
            issue_tamil="மாதாந்திர வாடகை ₹22,000 மற்றும் செலுத்த வேண்டிய தேதி (ஒவ்வொரு மாதமும் 5-ஆம் தேதிக்குள்) தெளிவாகவும் வெளிப்படையாகவும் குறிப்பிடப்பட்டுள்ளது.",
            legal_reference="TNRRRLT Act 2017, Section 8",
            legal_provision_details=(
                "Complies with Section 8 requirements mandating clear identification of agreed rent and maintaining written/electronic "
                "records of payments made under the tenancy."
            ),
            recommendation="Clause is well-drafted and balanced. Ensure electronic bank transaction receipts are preserved as statutory payment evidence.",
            recommendation_tamil="இந்த விதிமுறை சட்டத்திற்கு உட்பட்டு சரியாக உள்ளது. வங்கி பரிவர்த்தனை ரசீதை பாதுகாப்பாக வைக்கவும்.",
            suggested_clause=None,
        ),
    ]


def build_sample_report(
    analysis_id: str,
    doc_id: str,
    language: str,
    findings: List[Finding],
) -> ReportResponse:
    """Builds a comprehensive ReportResponse object for the rental agreement."""
    red_count = sum(1 for f in findings if f.risk_level == "red")
    yellow_count = sum(1 for f in findings if f.risk_level == "yellow")
    green_count = sum(1 for f in findings if f.risk_level == "green")

    summary_en = (
        "The evaluated Residential Rental Agreement exhibits significant legal imbalance with 3 critical RED risks "
        "(lack of notice period, unchecked rent escalation, and unconstrained deposit deductions), alongside 2 YELLOW caution items "
        "(unclear maintenance division and punitive default terms). While the rent amount is clearly specified (GREEN), "
        "modifications are strongly recommended before signing to align with the mandatory protections of the TNRRRLT Act 2017."
    )
    summary_ta = (
        "இந்த வாடகை ஒப்பந்தத்தில் 3 முக்கிய அபாயகரமான சிவப்பு எச்சரிக்கைகள் (முன்னறிவிப்பு காலம் இன்மை, தன்னிச்சையான வாடகை உயர்வு, "
        "முன்பணம் பிடித்தம்) மற்றும் 2 மஞ்சள் எச்சரிக்கைகள் உள்ளன. வாடகை தொகை தெளிவாக உள்ளது என்றாலும், 2017 தமிழ்நாடு வாடகை சட்ட "
        "விதிகளுக்கு ஏற்ப திருத்தங்கள் செய்த பிறகே கையெழுத்திட பரிந்துரைக்கப்படுகிறது."
    )

    questions = [
        "Can we add a reciprocal 30-day written notice clause before either party can terminate the agreement?",
        "Will you agree to fix the monthly rent at Rs. 22,000 for the full 11 months with a max 5% escalation upon renewal?",
        "Can the agreement stipulate that the Rs. 1,50,000 security deposit be refunded within 15 days of key handover via bank transfer?",
        "Are structural defects, seepage, and mainline plumbing explicitly agreed to be the lessor's financial responsibility?",
        "Can we replace the 18% monthly penalty with a standard Rs. 50/day fee after a 7-day grace period and strike out the lock-out clause?",
    ]

    legal_provisions = [
        "TNRRRLT Act 2017, Section 4 (Mandatory Registration with Rent Authority)",
        "TNRRRLT Act 2017, Section 9 & 10 (Revision of Rent Regulations)",
        "TNRRRLT Act 2017, Section 13(1) (Security Deposit Refund Timeline)",
        "TNRRRLT Act 2017, Section 20 & 21 (Prohibition of Disconnection & Repossession Grounds)",
        "TNRRRLT Act 2017, Second Schedule (Division of Maintenance Responsibilities)",
        "Transfer of Property Act, 1882, Section 106 (Statutory Notice for Month-to-Month Tenancy)",
        "Indian Contract Act, 1872, Section 74 (Compensation for Breach & Bar on Unreasonable Penalties)",
    ]

    report_id = str(uuid.uuid4())
    return ReportResponse(
        report_id=report_id,
        analysis_id=analysis_id,
        document_id=doc_id,
        document_name="Rental_Agreement_Chennai.pdf",
        property_type="Residential Tenancy Agreement",
        risk_score=74.5,
        risk_level="High Risk",
        summary=summary_en,
        summary_tamil=summary_ta,
        red_count=red_count,
        yellow_count=yellow_count,
        green_count=green_count,
        findings=findings,
        questions_for_landlord=questions,
        legal_provisions_cited=legal_provisions,
        is_demo=True,
        created_at=datetime.utcnow().isoformat(),
    )


@router.post(
    "/analyze",
    response_model=AgreementAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Agreement Document",
)
@router.post(
    "/analyze/",
    response_model=AgreementAnalysisResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def analyze_agreement(request: AgreementAnalysisRequest):
    """
    Orchestrates the full agreement risk analysis pipeline:
    1. Retrieve document metadata and extracted text
    2. Classify clauses into legal categories
    3. Retrieve applicable Tamil Nadu / Indian legal references via RAG
    4. Analyze risk levels (Red / Yellow / Green) with reasoning
    5. Generate negotiation questions for landlord
    6. Stores results and returns AgreementAnalysisResponse
    """
    valid_doc_id = validate_uuid(request.document_id, "document_id")
    if not callable(orchestrate_agreement_analysis):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agreement analysis pipeline is unavailable.",
        )

    try:
        result = await orchestrate_agreement_analysis(
            document_id=valid_doc_id,
            language=request.language,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.exception("Agreement analysis failed for document %s", valid_doc_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agreement analysis failed: {e}",
        ) from e

    analysis_id = result.analysis_id
    created_at = result.generated_at
    mapped_findings = []
    cited_provisions = []
    for finding in result.findings:
        reference = finding.legal_references[0] if finding.legal_references else None
        reference_title = reference.title if reference else "Legal review recommended"
        reference_details = (
            reference.excerpt or reference.section or ""
            if reference
            else "No directly matching provision was found; consult a qualified legal professional."
        )
        mapped_findings.append(Finding(
            id=finding.finding_id,
            clause_title=finding.clause_category.replace("_", " ").title(),
            clause_text=finding.clause_text,
            risk_level=finding.severity.value,
            category=finding.clause_category,
            issue=finding.explanation,
            issue_tamil=finding.explanation_ta,
            legal_reference=reference_title,
            legal_provision_details=reference_details,
            recommendation=finding.reason,
            recommendation_tamil=finding.explanation_ta,
            suggested_clause=finding.reference_comparison,
        ))
        if reference:
            cited_provisions.append(f"{reference.title} {reference.section or ''}".strip())

    stats = {
        "red_count": result.red_count,
        "yellow_count": result.yellow_count,
        "green_count": result.green_count,
        "grey_count": result.grey_count,
    }
    risk_score = round(
        (result.red_count * 100 + result.yellow_count * 50 + result.green_count * 10)
        / max(len(result.findings), 1),
        1,
    )
    risk_level = "High Risk" if result.red_count else (
        "Medium Risk" if result.yellow_count else "Low Risk"
    )
    summary = (
        f"Analysis of the uploaded agreement found {result.red_count} high-risk, "
        f"{result.yellow_count} cautionary, and {result.green_count} standard clauses."
    )
    document_name = None
    if callable(get_document_store):
        document_name = get_document_store().get(valid_doc_id, {}).get("filename")

    analysis_response = AgreementAnalysisResponse(
        analysis_id=analysis_id,
        document_id=valid_doc_id,
        status="completed",
        language=request.language,
        risk_score=risk_score,
        risk_level=risk_level,
        findings=mapped_findings,
        clauses_analyzed=len(result.findings),
        recommended_questions=result.questions,
        summary=summary,
        stats=stats,
        questions_to_ask=result.questions,
        document_name=document_name,
        is_demo=False,
        created_at=created_at,
    )
    report = ReportResponse(
        report_id=analysis_id,
        analysis_id=analysis_id,
        document_id=valid_doc_id,
        document_name=document_name or "Uploaded Agreement",
        risk_score=risk_score,
        risk_level=risk_level,
        summary=summary,
        red_count=result.red_count,
        yellow_count=result.yellow_count,
        green_count=result.green_count,
        findings=mapped_findings,
        questions_for_landlord=result.questions,
        legal_provisions_cited=cited_provisions,
        is_demo=False,
        created_at=created_at,
    )
    DEMO_ANALYSIS_STORE[analysis_id] = analysis_response
    DEMO_REPORT_STORE[analysis_id] = report
    return analysis_response


@router.get(
    "/{analysis_id}/report",
    response_model=ReportResponse,
    summary="Get Agreement Risk Report",
)
async def get_agreement_report(analysis_id: str):
    """
    Returns the comprehensive agreement risk report as ReportResponse.
    """
    valid_analysis_id = validate_uuid(analysis_id, "analysis_id")

    # 1. Check demo store
    if valid_analysis_id in DEMO_REPORT_STORE:
        return DEMO_REPORT_STORE[valid_analysis_id]

    # 2. Check Supabase DB
    client = get_supabase() if callable(get_supabase) else None
    if client:
        try:
            res = client.table("agreement_reports").select("*").eq("analysis_id", valid_analysis_id).execute()
            if res.data and len(res.data) > 0:
                row = res.data[0]
                return ReportResponse(
                    report_id=row["id"],
                    analysis_id=row["analysis_id"],
                    document_id=row["document_id"],
                    document_name=row.get("document_name", "Agreement.pdf"),
                    property_type=row.get("property_type", "Residential Tenancy Agreement"),
                    risk_score=row.get("risk_score", 50.0),
                    risk_level=row.get("risk_level", "Medium Risk"),
                    summary=row.get("summary", ""),
                    summary_tamil=row.get("summary_tamil"),
                    red_count=row.get("red_count", 0),
                    yellow_count=row.get("yellow_count", 0),
                    green_count=row.get("green_count", 0),
                    findings=row.get("findings", []),
                    questions_for_landlord=row.get("questions_for_landlord", []),
                    legal_provisions_cited=row.get("legal_provisions_cited", []),
                    is_demo=False,
                    created_at=row.get("created_at", datetime.utcnow().isoformat()),
                )
        except Exception as e:
            logger.error(f"Error fetching agreement report from Supabase: {str(e)}")

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Report with analysis_id '{valid_analysis_id}' not found.",
    )
