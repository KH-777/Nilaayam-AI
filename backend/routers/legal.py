import logging
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

# App configuration
from backend.config import settings

# Graceful DB imports
try:
    from backend.database import get_supabase_client, supabase
except ImportError:
    get_supabase_client = None
    supabase = None

logger = logging.getLogger("nilaayam.routers.legal")

router = APIRouter(tags=["legal"])


class LegalReference(BaseModel):
    id: str
    act_name: str
    act_name_tamil: Optional[str] = None
    section: str
    title: str
    title_tamil: Optional[str] = None
    description: str
    description_tamil: Optional[str] = None
    doc_type: str = Field(..., description="Primary document type (e.g. rental_agreement, sale_deed, patta)")
    applicable_document_types: List[str] = Field(default_factory=list)
    key_provisions: List[str] = Field(default_factory=list)
    penalties_or_remedies: Optional[str] = None
    year: int
    jurisdiction: str = "Tamil Nadu, India"
    is_demo: bool = False


# Curated demo dataset of 5 foundational Tamil Nadu / Indian real estate laws
DEMO_LEGAL_REFERENCES: List[LegalReference] = [
    LegalReference(
        id="REF-TNRRRLT-2017",
        act_name="Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017",
        act_name_tamil="தமிழ்நாடு நில உரிமையாளர் மற்றும் வாடகைதாரர் உரிமைகள் மற்றும் பொறுப்புகள் ஒழுங்குமுறை சட்டம், 2017",
        section="Section 4, Section 9, Section 13 & Section 21",
        title="Mandatory Tenancy Registration, Security Deposit Capping & Grounds for Repossession",
        title_tamil="கட்டாய வாடகை ஒப்பந்த பதிவு, முன்பண வரம்பு மற்றும் சட்டப்படியான வீட்டை மீட்பதற்கான வழிமுறைகள்",
        description=(
            "Mandates compulsory registration of all tenancy agreements in writing with the Rent Authority within 90 days. "
            "Caps refundable security deposits at a maximum of three months' rent for residential premises. "
            "Requires deposit refund within one month of vacating, and strictly restrains eviction to statutory grounds before the Rent Court."
        ),
        description_tamil=(
            "அனைத்து வாடகை ஒப்பந்தங்களும் 90 நாட்களுக்குள் வாடகை ஆணையத்திடம் கட்டாயம் பதிவு செய்யப்பட வேண்டும். "
            "முன்பணம் அதிகபட்சம் 3 மாத வாடகைக்கு மேல் இருக்கக்கூடாது. வீட்டை காலி செய்த ஒரு மாதத்திற்குள் முன்பணம் திருப்பித் தரப்பட வேண்டும்."
        ),
        doc_type="rental_agreement",
        applicable_document_types=["rental_agreement", "lease_deed"],
        key_provisions=[
            "Tenancy must be registered with the Rent Authority within 90 days of execution",
            "Security deposit capped at maximum 3 times monthly rent for residential properties",
            "Refund of security deposit within 1 month after deduction of agreed lawful dues",
            "Revision of rent only according to written agreement terms",
            "Eviction prohibited without Rent Court decree on grounds defined in Section 21",
        ],
        penalties_or_remedies="Unregistered tenancy agreements cannot be relied upon in Rent Court; landlord cannot execute eviction without registration.",
        year=2017,
        jurisdiction="Tamil Nadu, India",
        is_demo=True,
    ),
    LegalReference(
        id="REF-TPA-1882",
        act_name="Transfer of Property Act, 1882",
        act_name_tamil="சொத்து பரிமாற்றச் சட்டம், 1882",
        section="Section 54 & Section 106",
        title="Statutory Notice Period for Month-to-Month Leases & Transfer of Immovable Property",
        title_tamil="குத்தகையை முடிவுக்கு கொண்டுவருவதற்கான முன்னறிவிப்பு காலம் மற்றும் சொத்து பரிமாற்ற விதிகள்",
        description=(
            "Section 106 provides that in the absence of a written contract to the contrary, a lease of immovable property for residential "
            "purposes shall be deemed to be month-to-month, terminable by 15 days' notice expiring with the end of a tenancy month. "
            "Section 54 defines sale and transfer of ownership in exchange for a price paid or promised."
        ),
        description_tamil=(
            "எழுத்துப்பூர்வ ஒப்பந்தத்தில் குறிப்பிடப்படாத போது, குடியிருப்பு வாடகையை முடிக்க 15 நாட்கள் முன்னறிவிப்பு கால அவகாசம் சட்டப்பூர்வமாக அவசியமாகும். "
            "பிரிவு 54 சொத்து விற்பனை மற்றும் உரிமை மாற்றத்தை வரையறுக்கிறது."
        ),
        doc_type="rental_agreement",
        applicable_document_types=["rental_agreement", "lease_deed", "sale_deed"],
        key_provisions=[
            "15 days statutory notice for month-to-month tenancies expiring with end of tenancy month",
            "Notice must be in writing, signed, and tendered or delivered to the party",
            "Transfer of tangible immovable property of value above Rs. 100 must be by registered instrument",
            "Implied covenant for quiet enjoyment and lessor disclosure of latent defects",
        ],
        penalties_or_remedies="Eviction suits filed without valid statutory notice under Section 106 are fatally defective and dismissible.",
        year=1882,
        jurisdiction="India (Applicable to Tamil Nadu)",
        is_demo=True,
    ),
    LegalReference(
        id="REF-REG-1908-TN",
        act_name="The Registration Act, 1908 (Tamil Nadu State Amendments)",
        act_name_tamil="பதிவுச் சட்டம், 1908 (தமிழ்நாடு மாநில திருத்தங்கள்)",
        section="Section 17 & Section 22-A",
        title="Compulsory Registration of Immovable Property Deeds & Prohibition on Unapproved Layouts",
        title_tamil="சொத்து ஆவணங்கள் கட்டாயப் பதிவு மற்றும் அங்கீகாரமற்ற வீட்டுமனைகள் பதிவுத் தடை",
        description=(
            "Section 17 makes registration compulsory for all non-testamentary instruments transferring immovable property. "
            "Tamil Nadu Section 22-A explicitly prohibits registering transfers of unapproved layouts, plots without DTCP/CMDA approvals, "
            "and public/temple/waqf lands without prior statutory clearances."
        ),
        description_tamil=(
            "சொத்து விற்பனை, தானம், பாகப்பிரிவினை மற்றும் 11 மாதங்களுக்கு மேற்பட்ட குத்தகை ஆவணங்கள் கட்டாயம் பதிவு செய்யப்பட வேண்டும். "
            "DTCP/CMDA அங்கீகாரமற்ற மனைகளை பத்திரப்பதிவு செய்ய பிரிவு 22-A கீழ் முழு தடை விதிக்கப்பட்டுள்ளது."
        ),
        doc_type="sale_deed",
        applicable_document_types=["sale_deed", "patta", "gift_deed", "settlement_deed", "lease_deed"],
        key_provisions=[
            "Mandatory registration for conveyance of immovable property exceeding Rs. 100 in value",
            "Section 22-A bar on registration of unauthorized layouts and converted agricultural lands",
            "Compulsory biometric verification of parties and two witnesses at Sub-Registrar Office",
            "Section 49: Unregistered documents cannot create or transfer right, title, or interest in land",
        ],
        penalties_or_remedies="Refusal of registration by Sub-Registrar; unregistered deeds are legally inadmissible to prove title ownership.",
        year=1908,
        jurisdiction="Tamil Nadu, India",
        is_demo=True,
    ),
    LegalReference(
        id="REF-STAMP-1899-TN",
        act_name="Indian Stamp Act, 1899 & Tamil Nadu Stamp Rules",
        act_name_tamil="இந்திய முத்திரைச் சட்டம், 1899 மற்றும் தமிழ்நாடு முத்திரை விதிகள்",
        section="Schedule I, Article 25 (Conveyance) & Article 35 (Lease)",
        title="Tamil Nadu Real Estate Stamp Duty & Registration Fee Schedules",
        title_tamil="தமிழ்நாட்டில் சொத்து கிரையம் மற்றும் வாடகைக்கான முத்திரைத்தாள் கட்டண அட்டவணை",
        description=(
            "Sets out the ad-valorem stamp duty and registration fees in Tamil Nadu. For Sale Deeds, the current fee is 7% stamp duty "
            "plus 2% registration fee (total 9%) on guideline value or market consideration. For residential tenancy agreements under 5 years, "
            "stamp duty is 1% on total rent/advance payable."
        ),
        description_tamil=(
            "தமிழ்நாட்டில் சொத்து கிரையப் பத்திரங்களுக்கு 7% முத்திரைத்தாள் + 2% பதிவுக் கட்டணம் (மொத்தம் 9%) வசூலிக்கப்படுகிறது. "
            "5 ஆண்டுகளுக்கு உட்பட்ட வாடகை ஒப்பந்தங்களுக்கு 1% முத்திரைத்தாள் கட்டணம் செலுத்த வேண்டும்."
        ),
        doc_type="sale_deed",
        applicable_document_types=["sale_deed", "rental_agreement", "mortgage_deed", "settlement_deed"],
        key_provisions=[
            "7% Stamp duty + 2% Registration fee on guideline or consideration value for Sale Deeds",
            "1% Stamp duty on advance plus rent for tenancy agreements up to 5 years duration",
            "Section 47-A inquiry by District Collector (Revenue) for undervaluation of market consideration",
            "Section 33 power to impound insufficiently stamped instruments",
        ],
        penalties_or_remedies="Impounding of documents and levy of deficit stamp duty plus penalty up to ten times the deficit amount.",
        year=1899,
        jurisdiction="Tamil Nadu, India",
        is_demo=True,
    ),
    LegalReference(
        id="REF-PATTA-1983-TN",
        act_name="Tamil Nadu Patta Pass Book Act, 1983 & Rules 1987",
        act_name_tamil="தமிழ்நாடு பட்டா மாறுதல் சட்டம், 1983 மற்றும் விதிகள் 1987",
        section="Section 3, Section 5 & Section 10",
        title="Patta Pass Book as Prima Facie Record of Rights & Automatic Mutation Post-Registration",
        title_tamil="பட்டா ஆவணம் மற்றும் பத்திரப் பதிவுக்குப் பின் தானியங்கி பட்டா பெயர் மாற்றம்",
        description=(
            "Establishes Patta issued by the Tahsildar as authoritative prima facie evidence of lawful possession and revenue assessment. "
            "Section 5 mandates automatic intimation from the Sub-Registrar to the Revenue Department upon registration of any sale, "
            "enabling seamless digital Patta name transfer through the AnyWhere AnyTime e-Services portal."
        ),
        description_tamil=(
            "பட்டா என்பது நில உரிமை மற்றும் உடைமையை உறுதி செய்யும் முதன்மையான வருவாய்த்துறை ஆவணமாகும். "
            "பத்திரப்பதிவு முடிந்தவுடன் சார்பதிவாளர் அலுவலகத்திலிருந்து வட்டாட்சியருக்கு பட்டா பெயர் மாற்றத்திற்கான தகவல் தானாக அனுப்பப்படும்."
        ),
        doc_type="patta",
        applicable_document_types=["patta", "title_verification", "sale_deed"],
        key_provisions=[
            "Patta serves as authoritative government record of land holding and ownership",
            "Mandatory updating of revenue entries following registered sale or succession",
            "Discrepancies in survey number or extent must be rectified before the Tahsildar",
            "Verification of online e-Patta with QR code against TN Land Records e-District database",
        ],
        penalties_or_remedies="Sale deeds without corresponding Patta face rejection for bank home loans, municipal approvals, and utility connections.",
        year=1983,
        jurisdiction="Tamil Nadu, India",
        is_demo=True,
    ),
]


def is_supabase_enabled() -> bool:
    """Check if Supabase credentials are configured."""
    return bool(
        settings.supabase_url
        and (settings.supabase_service_role_key or settings.supabase_anon_key)
    )


@router.get(
    "/legal-references",
    response_model=List[LegalReference],
    summary="Get Legal References",
)
@router.get(
    "/legal-references/",
    response_model=List[LegalReference],
    include_in_schema=False,
)
async def get_legal_references(
    response: Response,
    doc_type: Optional[str] = Query(
        None,
        description="Filter references by document type (e.g. 'rental_agreement', 'sale_deed', 'patta', 'ec')",
    ),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return (default 20)"),
    offset: int = Query(0, ge=0, description="Offset for pagination (default 0)"),
):
    """
    Returns list of all LegalReference records from DB (or demo list of 5 references if DB not configured).
    Supports optional doc_type filtering and pagination.
    """
    # 1. Query Supabase DB if enabled
    if is_supabase_enabled():
        try:
            client = get_supabase_client() if callable(get_supabase_client) else supabase
            if client:
                query = client.table("legal_references").select("*", count="exact")
                if doc_type:
                    query = query.or_(
                        f"doc_type.eq.{doc_type.strip().lower()},applicable_document_types.cs.{{{doc_type.strip().lower()}}}"
                    )
                query = query.range(offset, offset + limit - 1)
                res = query.execute()

                if res.data is not None and len(res.data) > 0:
                    total_count = res.count if res.count is not None else len(res.data)
                    response.headers["X-Total-Count"] = str(total_count)
                    return [LegalReference(**row) for row in res.data]
        except Exception as e:
            logger.warning(f"Error querying legal_references from Supabase: {str(e)}. Using demo fallback.")

    # 2. Demo fallback list of 5 references
    results = DEMO_LEGAL_REFERENCES

    if doc_type:
        target = doc_type.strip().lower()
        results = [
            ref
            for ref in results
            if ref.doc_type.lower() == target
            or any(target in dt.lower() for dt in ref.applicable_document_types)
        ]

    total_count = len(results)
    response.headers["X-Total-Count"] = str(total_count)
    paginated = results[offset : offset + limit]

    return paginated
