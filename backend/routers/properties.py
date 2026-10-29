import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

# App configuration
from backend.config import settings

# Graceful imports
try:
    from backend.database import get_supabase_client, supabase
except ImportError:
    get_supabase_client = None
    supabase = None

try:
    from backend.services.analysis_orchestrator import (
        run_property_comparison,
    )
except ImportError:
    run_property_comparison = None

logger = logging.getLogger("nilaayam.routers.properties")

router = APIRouter(prefix="/properties", tags=["properties"])


# Pydantic Schemas
class PropertyCompareRequest(BaseModel):
    patta_document_id: str = Field(..., description="UUID of uploaded Patta / Chitta document")
    ec_document_id: str = Field(..., description="UUID of uploaded Encumbrance Certificate (EC)")
    sale_deed_document_id: str = Field(..., description="UUID of uploaded Parent Sale Deed document")
    language: str = Field(default="en", description="Preferred output language ('en', 'ta')")


class ComparisonFieldResult(BaseModel):
    field_name: str
    field_name_tamil: Optional[str] = None
    status: str = Field(..., description="'MATCH', 'MISMATCH', 'PARTIAL_MATCH', or 'MISSING'")
    patta_value: Optional[str] = None
    ec_value: Optional[str] = None
    sale_deed_value: Optional[str] = None
    severity: Optional[str] = Field(default=None, description="'CRITICAL', 'WARNING', or 'LOW'")
    explanation: str
    explanation_tamil: Optional[str] = None
    action_required: Optional[str] = None


class PropertyComparisonResponse(BaseModel):
    comparison_id: str
    patta_document_id: str
    ec_document_id: str
    sale_deed_document_id: str
    status: str
    language: str
    overall_status: str = Field(..., description="'Verified', 'Warning - Discrepancy Detected', or 'Failed'")
    match_count: int
    mismatch_count: int
    comparison_fields: List[ComparisonFieldResult]
    legal_summary: str
    legal_summary_tamil: Optional[str] = None
    next_steps: List[str]
    is_demo: bool = False
    created_at: str


class ChecklistRequest(BaseModel):
    property_type: str = Field(default="residential", description="'residential', 'commercial', 'agricultural', 'plot'")
    transaction_type: str = Field(default="sale", description="'sale', 'lease', 'gift', 'mortgage'")
    language: str = Field(default="en", description="Output language ('en', 'ta')")


class ChecklistItem(BaseModel):
    item_number: int
    title: str
    title_tamil: str
    description: str
    description_tamil: str
    issuing_authority: str
    is_mandatory: bool = True
    timeline_estimate: str
    applicable_law: str
    tips_for_buyer: str


class ChecklistResponse(BaseModel):
    checklist_id: str
    property_type: str
    transaction_type: str
    language: str
    jurisdiction: str = "Tamil Nadu, India"
    total_items: int
    mandatory_count: int
    items: List[ChecklistItem]
    is_demo: bool = False
    created_at: str


# In-memory store for demo mode
DEMO_COMPARISON_STORE: Dict[str, PropertyComparisonResponse] = {}


def is_supabase_enabled() -> bool:
    """Check if Supabase credentials are configured."""
    return bool(
        settings.supabase_url
        and (settings.supabase_service_role_key or settings.supabase_anon_key)
    )


def validate_uuid(val: str, field_name: str = "id") -> str:
    """Validate that the string conforms to UUID format."""
    try:
        return str(uuid.UUID(str(val).strip()))
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name}: '{val}'. Must be a valid UUID.",
        )


def build_sample_property_comparison(
    comparison_id: str,
    patta_id: str,
    ec_id: str,
    sale_deed_id: str,
    language: str = "en",
) -> PropertyComparisonResponse:
    """
    Constructs realistic cross-verification comparison:
    - 1 mismatch: survey number differs between Patta and sale deed
    - 2 matches: owner name, property area
    """
    fields: List[ComparisonFieldResult] = [
        # MATCH 1: Owner Name
        ComparisonFieldResult(
            field_name="Owner Name",
            field_name_tamil="உரிமையாளர் பெயர்",
            status="MATCH",
            patta_value="K. Ramaswamy (கே. ராமசுவாமி)",
            ec_value="K. Ramaswamy",
            sale_deed_value="K. Ramaswamy, S/o Late Krishnan",
            severity=None,
            explanation="The owner's full legal name matches consistently across the Patta register, Encumbrance Certificate entry, and registered Sale Deed.",
            explanation_tamil="உரிமையாளர் பெயர் பட்டா, வில்லங்கச் சான்றிதழ் மற்றும் கிரையப் பத்திரம் ஆகிய மூன்றிலும் ஒத்துப் போகிறது.",
            action_required="No rectification required for owner identity.",
        ),
        # MATCH 2: Property Area / Extent
        ComparisonFieldResult(
            field_name="Property Extent / Area",
            field_name_tamil="சொத்தின் பரப்பளவு",
            status="MATCH",
            patta_value="0.05.5 Hectares (approx. 2,400 sq.ft / 1 Ground)",
            ec_value="2,400 sq.ft (Plot No. 12, Orchid Enclave)",
            sale_deed_value="2,400 sq.ft (East-West 60 ft, North-South 40 ft) / 1 Ground",
            severity=None,
            explanation="The property extent of 2,400 sq.ft (1 Ground) matches precisely between the revenue conversion in Patta and measurements in the registered Sale Deed and EC.",
            explanation_tamil="சொத்தின் மொத்த பரப்பளவு 2,400 சதுர அடி (1 கிரவுண்ட்) என்பது பட்டா, பத்திரப்பதிவு மற்றும் வில்லங்கச் சான்றிதழில் சீராக பொருந்துகிறது.",
            action_required="Ensure physical boundaries on site match the four-boundary description (East, West, North, South) given in the deed.",
        ),
        # MISMATCH 1: Survey Number Discrepancy
        ComparisonFieldResult(
            field_name="Survey Number / Sub-Division",
            field_name_tamil="புல எண் மற்றும் உட்பிரிவு (Survey No)",
            status="MISMATCH",
            patta_value="Survey No. 142/3B",
            ec_value="Survey No. 142/3B (New) & 142/2 (Old Parent S.No.)",
            sale_deed_value="Old Survey No. 142/2 only (missing updated S.No. 142/3B)",
            severity="CRITICAL",
            explanation=(
                "Critical Discrepancy: The e-Patta and EC reference modern sub-division Survey No. 142/3B, "
                "whereas the registered Parent Sale Deed only cites ancestral Old Survey No. 142/2. "
                "Without an official Sub-Division Certificate (FMB Sketch) or Rectification Deed tracing 142/2 to 142/3B, "
                "the Sub-Registrar may object to registration or future bank loans may be blocked."
            ),
            explanation_tamil=(
                "முக்கிய முரண்பாடு: பட்டா மற்றும் வில்லங்கச் சான்றிதழில் புதிய சர்வே எண் 142/3B என குறிப்பிடப்பட்டுள்ளது. "
                "ஆனால் முந்தைய விற்பனைப் பத்திரத்தில் பழைய சர்வே எண் 142/2 மட்டுமே உள்ளது. "
                "துணை நில அளவை வரைபடம் (FMB Sketch) அல்லது உட்பிரிவு சான்றிதழ் இல்லாமல் பத்திரப்பதிவு செய்வதில் சிக்கல் ஏற்படலாம்."
            ),
            action_required=(
                "Obtain a certified Village Field Measurement Book (FMB) Sketch and a Sub-Division Certificate from the "
                "Zonal Tahsildar / VAO establishing that S.No. 142/3B was legally sub-divided out of ancestral S.No. 142/2. "
                "Alternatively, incorporate a recital or execute a Rectification Deed prior to final sale registration."
            ),
        ),
    ]

    summary_en = (
        "Property Cross-Verification identified 1 CRITICAL MISMATCH and 2 VERIFIED MATCHES. "
        "The owner name ('K. Ramaswamy') and total land area (2,400 sq.ft) are confirmed across all three documents. "
        "However, there is a material discrepancy in the Survey Number: the Patta registers modern S.No. 142/3B while the Sale Deed "
        "only cites parent S.No. 142/2. A revenue sub-division certificate or VAO link certificate is mandatory prior to registration."
    )
    summary_ta = (
        "ஆவணங்கள் சரிபார்ப்பில் 1 முக்கிய முரண்பாடு மற்றும் 2 பொருத்தங்கள் கண்டறியப்பட்டன. "
        "உரிமையாளர் பெயர் (கே. ராமசுவாமி) மற்றும் 2,400 சதுர அடி நிலப்பரப்பு சரியாக பொருந்துகிறது. "
        "ஆனால் சர்வே எண்ணில் முரண்பாடு உள்ளது: பட்டாவில் சர்வே எண் 142/3B என்றும், கிரையப் பத்திரத்தில் பழைய எண் 142/2 என்றும் உள்ளது. "
        "வட்டாட்சியரிடம் இருந்து உட்பிரிவு சான்றிதழ் (FMB Sketch) பெற்ற பிறகே கிரையப் பதிவு செய்ய வேண்டும்."
    )

    next_steps = [
        "Request certified Field Measurement Book (FMB) extract for S.No. 142/3B from Tamil Nadu e-District portal.",
        "Obtain Village Administrative Officer (VAO) Certificate confirming that S.No. 142/3B is the exact sub-division of Old S.No. 142/2.",
        "Ensure the draft Sale Deed explicitly recites both Old Survey No. 142/2 and New Sub-division Survey No. 142/3B.",
        "Verify latest online Encumbrance Certificate up to the exact date of registration on TNREGINET portal.",
    ]

    return PropertyComparisonResponse(
        comparison_id=comparison_id,
        patta_document_id=patta_id,
        ec_document_id=ec_id,
        sale_deed_document_id=sale_deed_id,
        status="completed",
        language=language,
        overall_status="Warning - Discrepancy Detected",
        match_count=2,
        mismatch_count=1,
        comparison_fields=fields,
        legal_summary=summary_en,
        legal_summary_tamil=summary_ta,
        next_steps=next_steps,
        is_demo=True,
        created_at=datetime.utcnow().isoformat(),
    )


def build_tamil_nadu_registration_checklist(
    checklist_id: str,
    property_type: str = "residential",
    transaction_type: str = "sale",
    language: str = "en",
) -> ChecklistResponse:
    """
    Constructs a realistic 8-item registration checklist for residential sale in Tamil Nadu.
    """
    items = [
        ChecklistItem(
            item_number=1,
            title="Original Parent Deed & Link Documents (30-Year Chain)",
            title_tamil="தாய் பத்திரம் மற்றும் 30 வருட மூல ஆவணங்கள்",
            description=(
                "Original registered Sale Deed, Settlement Deed, or Partition Deed in favor of current seller, "
                "along with prior link documents establishing an unbroken 30-year chain of title ownership."
            ),
            description_tamil=(
                "விற்பனையாளரின் பெயரில் உள்ள அசல் கிரையப் பத்திரம் அல்லது தான பத்திரம், மற்றும் கடந்த 30 ஆண்டுகளுக்கான "
                "தொடர்ச்சியான தாய் பத்திரங்கள் சமர்ப்பிக்கப்பட வேண்டும்."
            ),
            issuing_authority="Sub-Registrar Office (SRO) / TNREGINET",
            is_mandatory=True,
            timeline_estimate="Immediate (to be produced by Seller)",
            applicable_law="Section 17, Registration Act, 1908 & Section 54, Transfer of Property Act, 1882",
            tips_for_buyer="Inspect the physical original deeds; never rely solely on photocopies or certified copies.",
        ),
        ChecklistItem(
            item_number=2,
            title="Encumbrance Certificate (EC) for 30 Years (Form 15)",
            title_tamil="வில்லங்கச் சான்றிதழ் (படிவம் 15 - 30 ஆண்டுகள்)",
            description=(
                "Form 15 Encumbrance Certificate issued by TNREGINET verifying that the property is free from "
                "undisclosed mortgages, court attachments, government dues, or third-party claims for the past 30 years."
            ),
            description_tamil=(
                "சொத்தின் மீது வங்கி கடன், அடமானம், நீதிமன்ற வழக்குகள் அல்லது வில்லங்கம் எதுவும் இல்லை என்பதை உறுதி செய்யும் "
                "30 ஆண்டுகளுக்கான படிவம் 15 வில்லங்கச் சான்றிதழ்."
            ),
            issuing_authority="Tamil Nadu Registration Department (TNREGINET)",
            is_mandatory=True,
            timeline_estimate="1 - 3 business days online",
            applicable_law="Tamil Nadu Registration Rules, Rule 130",
            tips_for_buyer="Apply for EC up to the immediate preceding day of the registration date to catch last-minute entries.",
        ),
        ChecklistItem(
            item_number=3,
            title="Patta / Chitta / TSLR Extract in Seller's Name",
            title_tamil="விற்பனையாளர் பெயரிலான பட்டா / சிட்டா / நகர நில அளவை ஆவணம்",
            description=(
                "Official computer-generated e-Patta / Chitta issued by Tamil Nadu Revenue Department "
                "confirming that the seller is recorded as the registered landholder in government revenue archives."
            ),
            description_tamil=(
                "தமிழக அரசின் வருவாய்த்துறை மூலம் வழங்கப்பட்ட டிஜிட்டல் e-பட்டா, இதில் விற்பனையாளரின் பெயர் பதிவாகி இருக்க வேண்டும்."
            ),
            issuing_authority="Revenue Department (Tahsildar / Village Administrative Officer)",
            is_mandatory=True,
            timeline_estimate="1 - 2 business days via e-Services Portal",
            applicable_law="Tamil Nadu Patta Pass Book Act, 1983, Section 3",
            tips_for_buyer="Verify the digital QR code on the e-Patta through the Tamil Nadu e-District portal.",
        ),
        ChecklistItem(
            item_number=4,
            title="Approved Building Plan & Completion Certificate",
            title_tamil="கட்டிட வரைபட அனுமதி மற்றும் நிறைவுச் சான்றிதழ்",
            description=(
                "Sanctioned building plan from CMDA (Chennai Metropolitan Development Authority) or DTCP (Directorate of Town & Country Planning), "
                "alongside Local Body Completion Certificate ensuring structure adheres to building bye-laws."
            ),
            description_tamil=(
                "CMDA அல்லது DTCP அங்கீகரிக்கப்பட்ட கட்டிட வரைபடம் மற்றும் உள்ளாட்சி அமைப்பால் வழங்கப்பட்ட பணி நிறைவுச் சான்றிதழ் (Completion Certificate)."
            ),
            issuing_authority="CMDA / DTCP / Greater Chennai Corporation / Local Municipality",
            is_mandatory=True,
            timeline_estimate="Available with seller / developer",
            applicable_law="Tamil Nadu Combined Development and Building Rules, 2019",
            tips_for_buyer="Unapproved constructions or deviation over statutory limits are liable to disconnection of power/water.",
        ),
        ChecklistItem(
            item_number=5,
            title="Latest Property Tax & Utility Clearance Receipts",
            title_tamil="சமீபத்திய சொத்து வரி மற்றும் குடிநீர்/மின்வாரிய ரசீதுகள்",
            description=(
                "Latest paid property tax assessment receipt from Greater Chennai Corporation / Municipality, "
                "Metro Water & Sewerage assessment card, and TANGEDCO Electricity Board consumer card in seller's name."
            ),
            description_tamil=(
                "சென்னை மாநகராட்சி/நகராட்சி சொத்து வரி ரசீது, குடிநீர் வாரிய கட்டண ரசீது மற்றும் TANGEDCO மின் கட்டண அட்டை."
            ),
            issuing_authority="Local Municipal Corporation / CMWSSB / TANGEDCO",
            is_mandatory=True,
            timeline_estimate="Immediate",
            applicable_law="Tamil Nadu District Municipalities Act, 1920",
            tips_for_buyer="Ensure no outstanding tax or water arrears exist, as unpaid municipal dues transfer with property ownership.",
        ),
        ChecklistItem(
            item_number=6,
            title="Aadhaar Card and PAN Card of Both Parties",
            title_tamil="வாங்குபவர் மற்றும் விற்பனையாளரின் ஆதார் மற்றும் பான் அட்டை",
            description=(
                "Original Aadhaar cards and PAN cards of both buyer and seller. Mandatory for biometric fingerprint verification, "
                "facial photography at Sub-Registrar Office, and income tax compliance."
            ),
            description_tamil=(
                "இரு தரப்பினரின் அசல் ஆதார் அட்டை மற்றும் பான் அட்டை. சார்பதிவாளர் அலுவலகத்தில் கைரேகை மற்றும் புகைப்பட பதிவுக்கு கட்டாயம்."
            ),
            issuing_authority="UIDAI / Income Tax Department of India",
            is_mandatory=True,
            timeline_estimate="Immediate (Personal Documents)",
            applicable_law="Registration Act 1908 Section 32A & Income Tax Act Section 139A",
            tips_for_buyer="Names on Aadhaar and PAN must match the names drafted in the Sale Deed verbatim.",
        ),
        ChecklistItem(
            item_number=7,
            title="TDS Payment Challan (Form 26QB Verification)",
            title_tamil="1% வருமான வரி பிடித்தம் சலான் (படிவம் 26QB)",
            description=(
                "If sale consideration or guideline value exceeds Rs. 50 Lakhs, buyer must deduct 1% TDS "
                "under Section 194-IA and deposit via Form 26QB on the Income Tax TIN-NSDL / e-filing portal."
            ),
            description_tamil=(
                "சொத்தின் மதிப்பு ₹50 லட்சத்திற்கு மேல் இருந்தால், வாங்குபவர் 1% TDS பிடித்தம் செய்து படிவம் 26QB சலான் சமர்ப்பிக்க வேண்டும்."
            ),
            issuing_authority="Income Tax Department of India",
            is_mandatory=True,
            timeline_estimate="1 - 2 business days online",
            applicable_law="Section 194-IA, Income Tax Act, 1961",
            tips_for_buyer="Carry Form 26QB receipt and Form 16B certificate to the registration desk.",
        ),
        ChecklistItem(
            item_number=8,
            title="Two Independent Witnesses with Government Photo IDs",
            title_tamil="அரசு அடையாள அட்டையுடன் இரண்டு சாட்சிகள்",
            description=(
                "Two independent, adult witnesses who know the parties personally, each carrying original Aadhaar Card or Voter ID, "
                "who will physically testify and append signatures before the Sub-Registrar."
            ),
            description_tamil=(
                "இரு தரப்பினரையும் தனிப்பட்ட முறையில் அறிந்த இரண்டு வயது வந்த சாட்சிகள் (அசல் ஆதார் அல்லது வாக்காளர் அடையாள அட்டையுடன்) ஆஜராக வேண்டும்."
            ),
            issuing_authority="Sub-Registrar Office (Registration Process)",
            is_mandatory=True,
            timeline_estimate="Required on day of registration",
            applicable_law="Registration Act, 1908, Section 34 & 35",
            tips_for_buyer="Witnesses should not be direct parties or beneficiaries under the deed.",
        ),
    ]

    return ChecklistResponse(
        checklist_id=checklist_id,
        property_type=property_type,
        transaction_type=transaction_type,
        language=language,
        jurisdiction="Tamil Nadu, India",
        total_items=len(items),
        mandatory_count=sum(1 for i in items if i.is_mandatory),
        items=items,
        is_demo=True,
        created_at=datetime.utcnow().isoformat(),
    )


@router.post(
    "/compare",
    response_model=PropertyComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare Patta, EC, and Sale Deed Documents",
)
@router.post(
    "/compare/",
    response_model=PropertyComparisonResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def compare_property_documents(request: PropertyCompareRequest):
    """
    Accepts PropertyCompareRequest with 3 document IDs (Patta, EC, Sale Deed):
    - Validates document IDs
    - Runs cross-verification pipeline comparing survey numbers, extents, and ownership
    - Returns PropertyComparisonResponse with matches, mismatches, and actionable advice
    """
    valid_patta = validate_uuid(request.patta_document_id, "patta_document_id")
    valid_ec = validate_uuid(request.ec_document_id, "ec_document_id")
    valid_sale_deed = validate_uuid(request.sale_deed_document_id, "sale_deed_document_id")

    comparison_id = str(uuid.uuid4())

    # If Supabase and orchestrator are available, run actual comparison
    if is_supabase_enabled() and callable(run_property_comparison):
        try:
            res = await run_property_comparison(
                patta_id=valid_patta,
                ec_id=valid_ec,
                sale_deed_id=valid_sale_deed,
                language=request.language,
                comparison_id=comparison_id,
            )
            if res:
                return res
        except Exception as e:
            logger.warning(f"Property comparison orchestrator failed: {str(e)}. Using demo fallback.")

    # Fallback demo mode
    demo_res = build_sample_property_comparison(
        comparison_id=comparison_id,
        patta_id=valid_patta,
        ec_id=valid_ec,
        sale_deed_id=valid_sale_deed,
        language=request.language,
    )
    DEMO_COMPARISON_STORE[comparison_id] = demo_res
    return demo_res


@router.get(
    "/{comparison_id}/comparison",
    response_model=PropertyComparisonResponse,
    summary="Get Stored Property Comparison Result",
)
async def get_property_comparison(comparison_id: str):
    """
    Returns stored comparison result by comparison_id.
    """
    valid_id = validate_uuid(comparison_id, "comparison_id")

    # 1. Check demo store
    if valid_id in DEMO_COMPARISON_STORE:
        return DEMO_COMPARISON_STORE[valid_id]

    # 2. Check Supabase DB
    if is_supabase_enabled():
        try:
            client = get_supabase_client() if callable(get_supabase_client) else supabase
            if client:
                res = client.table("property_comparisons").select("*").eq("id", valid_id).execute()
                if res.data and len(res.data) > 0:
                    row = res.data[0]
                    return PropertyComparisonResponse(**row)
        except Exception as e:
            logger.error(f"Error fetching comparison from Supabase: {str(e)}")

    # 3. Fallback synthesis for demo
    if not is_supabase_enabled():
        mock_res = build_sample_property_comparison(
            comparison_id=valid_id,
            patta_id=str(uuid.uuid4()),
            ec_id=str(uuid.uuid4()),
            sale_deed_id=str(uuid.uuid4()),
            language="en",
        )
        DEMO_COMPARISON_STORE[valid_id] = mock_res
        return mock_res

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Property comparison '{valid_id}' not found.",
    )


@router.post(
    "/checklist",
    response_model=ChecklistResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Property Registration Checklist",
)
@router.post(
    "/checklist/",
    response_model=ChecklistResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def generate_checklist(request: ChecklistRequest):
    """
    Accepts ChecklistRequest (property_type, transaction_type, language):
    - Generates realistic, legally backed checklist for registration in Tamil Nadu
    - Returns ChecklistResponse with 8 statutory items, tips, and authorities
    """
    checklist_id = str(uuid.uuid4())
    checklist = build_tamil_nadu_registration_checklist(
        checklist_id=checklist_id,
        property_type=request.property_type,
        transaction_type=request.transaction_type,
        language=request.language,
    )
    return checklist
