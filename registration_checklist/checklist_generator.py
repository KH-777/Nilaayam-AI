"""Registration Checklist Generator Module for Nilaayam AI.

Generates statutory document checklists for property sales and rental registrations in Tamil Nadu,
providing bilingual English and Tamil descriptions, official sources, and statutory notes.
"""

import logging
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

LAST_VERIFIED_DATE = "2024-01-15"
TNREGINET_URL = "https://tnreginet.gov.in"
TN_REVENUE_URL = "https://eservices.tn.gov.in"


def _get_sale_checklist(property_type: str = "residential") -> List[Dict[str, Any]]:
    """Returns statutory checklist items for property conveyance (Sale Deed) in Tamil Nadu."""
    is_rural = "rural" in property_type.lower() or "agricultural" in property_type.lower()
    is_plot = "plot" in property_type.lower() or "land" in property_type.lower()

    items = [
        {
            "item_id": "chk_sale_patta",
            "requirement": "Patta (Record of Rights / பட்டா)",
            "requirement_ta": "பட்டா (வருவாய்த்துறை உரிமை ஆவணம்)",
            "why_needed": (
                "Proves legal title and mutation in the state revenue records. The Sub-Registrar requires the vendor "
                "to hold a valid Patta in their name under Section 22-A/guidelines of the Registration Department."
            ),
            "why_needed_ta": "நிலத்தின் வருவாய்த்துறை உரிமையை நிரூபிக்கவும், விற்பனையாளர் பெயரில் பட்டா உள்ளதை உறுதிப்படுத்தவும் தேவை.",
            "official_source_url": TN_REVENUE_URL,
            "official_source_name": "Government of Tamil Nadu - AnyGov / e-Services",
            "last_verified": LAST_VERIFIED_DATE,
            "is_mandatory": True,
            "depends_on": None,
            "notes": "Verify that the Patta number, survey number, and owner name match the vendor's identity exactly.",
        },
        {
            "item_id": "chk_sale_ec",
            "requirement": "Encumbrance Certificate (EC / வில்லங்கச் சான்றிதழ்) - 30 Years",
            "requirement_ta": "வில்லங்கச் சான்றிதழ் (குறைந்தபட்சம் 30 ஆண்டுகள்)",
            "why_needed": (
                "Confirms whether the property is free from registered mortgages, court attachments, prior sales, "
                "or liens over the last 30 years up to the date of registration."
            ),
            "why_needed_ta": "சொத்தின் மீது அடமானம், நீதிமன்ற வழக்கு அல்லது பிற வில்லங்கங்கள் எதுவும் இல்லை என்பதை அறிய.",
            "official_source_url": TNREGINET_URL,
            "official_source_name": "Registration Department, Tamil Nadu (TNREGINET)",
            "last_verified": LAST_VERIFIED_DATE,
            "is_mandatory": True,
            "depends_on": None,
            "notes": "Ensure search extends without gap up to the current date and all surveyed sub-divisions are included.",
        },
        {
            "item_id": "chk_sale_draft",
            "requirement": "Sale Deed (Draft / விற்பனைப் பத்திரம்)",
            "requirement_ta": "விற்பனைப் பத்திரம் (அசல் மற்றும் வரைவு)",
            "why_needed": (
                "The core conveyancing instrument that transfers title, ownership, and possession from the vendor "
                "to the purchaser. Must be printed on stamp paper or accompanied by an e-stamp certificate."
            ),
            "why_needed_ta": "சொத்து உரிமையை வாங்குபவருக்கு முழுமையாக மாற்றும் முதன்மை சட்ட ஆவணம்.",
            "official_source_url": TNREGINET_URL,
            "official_source_name": "Registration Act 1908 & TN Registration Rules",
            "last_verified": LAST_VERIFIED_DATE,
            "is_mandatory": True,
            "depends_on": None,
            "notes": "Must include precise boundary schedules (East, West, North, South) and consideration details.",
        },
        {
            "item_id": "chk_sale_valuation",
            "requirement": "Government Guideline Valuation Report (வழிகாட்டி மதிப்பு சான்று)",
            "requirement_ta": "அரசு வழிகாட்டி மதிப்பு விவர அறிக்கை",
            "why_needed": (
                "Determines the statutory minimum market value on which stamp duty and registration fees are calculated "
                "under Section 47-A of the Indian Stamp Act (TN Amendment)."
            ),
            "why_needed_ta": "முத்திரைக் கட்டணம் மற்றும் பதிவுக் கட்டணத்தை துல்லியமாக கணக்கிட அரசு வழிகாட்டி மதிப்பு தேவை.",
            "official_source_url": f"{TNREGINET_URL}/guidelinevalue",
            "official_source_name": "TNREGINET Guideline Valuation Service",
            "last_verified": LAST_VERIFIED_DATE,
            "is_mandatory": True,
            "depends_on": None,
            "notes": "Printout generated directly from TNREGINET portal matching the exact survey number/street.",
        },
        {
            "item_id": "chk_sale_stamp_duty",
            "requirement": "Stamp Duty and Registration Fee Payment Receipt",
            "requirement_ta": "முத்திரைத் தாள் கட்டணம் மற்றும் பதிவுக் கட்டண ரசீது",
            "why_needed": (
                "Proof of government tax payment. In Tamil Nadu, current conveyance charges are generally 7% Stamp Duty "
                "and 4% Registration Fee calculated on the higher of guideline value or agreed consideration."
            ),
            "why_needed_ta": "அரசுக்கு செலுத்த வேண்டிய முத்திரைக் கட்டணம் (7%) மற்றும் பதிவுக் கட்டணம் (4%) செலுத்தியதற்கான ரசீது.",
            "official_source_url": TNREGINET_URL,
            "official_source_name": "Commercial Taxes and Registration Department, Government of Tamil Nadu",
            "last_verified": LAST_VERIFIED_DATE,
            "is_mandatory": True,
            "depends_on": "chk_sale_valuation",
            "notes": "VERIFY CURRENT RATES: Rates may vary based on recent State Budget amendments. E-challan must be generated through TNREGINET.",
        },
        {
            "item_id": "chk_sale_pan",
            "requirement": "PAN Cards of Buyer and Seller (or Form 60/61)",
            "requirement_ta": "வாங்குபவர் மற்றும் விற்பனையாளரின் பான் (PAN) கார்டு",
            "why_needed": (
                "Mandatory under Section 139A of the Income Tax Act for property transactions valued over Rs. 5 Lakhs. "
                "TDS (1%) deduction is applicable under Section 194-IA if consideration exceeds Rs. 50 Lakhs."
            ),
            "why_needed_ta": "வருமான வரித்துறை விதிகளின்படி ரூ. 5 லட்சத்திற்கு மேற்பட்ட சொத்து பரிவர்த்தனைகளுக்கு பான் கார்டு கட்டாயம்.",
            "official_source_url": "https://www.incometax.gov.in",
            "official_source_name": "Income Tax Department of India",
            "last_verified": LAST_VERIFIED_DATE,
            "is_mandatory": True,
            "depends_on": None,
            "notes": "Form 60 must be filled with agricultural income proof if a party does not possess a PAN card.",
        },
        {
            "item_id": "chk_sale_witness_id",
            "requirement": "Identity Proofs of Two Identifying Witnesses",
            "requirement_ta": "இரண்டு சாட்சிகளின் அடையாளச் சான்றுகள் (ஆதார் / வாக்காளர் அட்டை)",
            "why_needed": (
                "Section 32 of the Registration Act mandates that two adult witnesses must be present before the Sub-Registrar "
                "to identify the parties executing the deed."
            ),
            "why_needed_ta": "பதிவு செய்யும் போது இரு தரப்பினரையும் அடையாளம் காட்ட இரண்டு சாட்சிகள் நேரில் ஆஜராக வேண்டும்.",
            "official_source_url": TNREGINET_URL,
            "official_source_name": "Registration Department, Tamil Nadu",
            "last_verified": LAST_VERIFIED_DATE,
            "is_mandatory": True,
            "depends_on": None,
            "notes": "Witnesses must carry original Aadhaar / Voter ID and passport-sized photographs.",
        },
        {
            "item_id": "chk_sale_chitta",
            "requirement": "Chitta Extract / ‘A’ Register Extract",
            "requirement_ta": "சிட்டா / ‘அ’ பதிவேடு சான்று",
            "why_needed": (
                "Provides classification of land (Nanjai/Punjai, wet/dry land) and land revenue assessment details, "
                "crucial for rural and suburban properties."
            ),
            "why_needed_ta": "நிலத்தின் வகைப்பாடு (நஞ்சை / புஞ்சை) மற்றும் வருவாய் மதிப்பீட்டை அறிய உதவுகிறது.",
            "official_source_url": TN_REVENUE_URL,
            "official_source_name": "Tamil Nadu Land Records (e-District)",
            "last_verified": LAST_VERIFIED_DATE,
            "is_mandatory": is_rural,
            "depends_on": "chk_sale_patta",
            "notes": "Mandatory for rural/agricultural land parcels; highly recommended for all plotted layouts.",
        },
        {
            "item_id": "chk_sale_approval",
            "requirement": "Building Plan Approval / Layout Approval (CMDA / DTCP / LPA)",
            "requirement_ta": "கட்டிட அனுமதி / மனைப்பிரிவு அங்கீகார ஆவணம் (CMDA / DTCP)",
            "why_needed": (
                "In Tamil Nadu, unapproved plots or unapproved layouts cannot be registered without regularization "
                "frameworks under Section 22-A of the Registration Act."
            ),
            "why_needed_ta": "அங்கீகரிக்கப்படாத மனைகள் மற்றும் விதிமீறல் கட்டிடங்கள் பதிவு செய்யப்படுவதை தடுக்க இந்த அனுமதி அவசியம்.",
            "official_source_url": "https://www.cmdachennai.gov.in",
            "official_source_name": "CMDA / Directorate of Town and Country Planning (DTCP)",
            "last_verified": LAST_VERIFIED_DATE,
            "is_mandatory": not is_rural,
            "depends_on": None,
            "notes": "Check DTCP or CMDA approval order number and ensure local body building sanction is valid.",
        },
        {
            "item_id": "chk_sale_tax_receipts",
            "requirement": "Property Tax & Utility Paid Receipts",
            "requirement_ta": "சொத்து வரி மற்றும் குடிநீர்/மின் கட்டணம் செலுத்திய ரசீதுகள்",
            "why_needed": (
                "Confirms that municipal taxes, water charges, and electricity dues are up to date and there are "
                "no outstanding municipal arrears against the property."
            ),
            "why_needed_ta": "உள்ளாட்சி அமைப்புகளுக்கு சொத்து வரி பாக்கிகள் எதுவும் இல்லை என்பதை உறுதிப்படுத்த.",
            "official_source_url": "https://chennaicorporation.gov.in",
            "official_source_name": "Greater Chennai Corporation / Municipal Administration",
            "last_verified": LAST_VERIFIED_DATE,
            "is_mandatory": True,
            "depends_on": None,
            "notes": "Latest half-yearly property tax assessment receipt and TANGEDCO electricity card/receipt.",
        },
    ]

    return items


def _get_lease_checklist(property_type: str = "residential") -> List[Dict[str, Any]]:
    """Returns statutory checklist items for residential tenancy / lease registration in Tamil Nadu."""
    return [
        {
            "item_id": "chk_lease_agreement",
            "requirement": "Tenancy Agreement (Original & Duplicate Copies)",
            "requirement_ta": "வாடகை ஒப்பந்தம் (அசல் மற்றும் நகல்கள்)",
            "why_needed": (
                "Required for execution and registration before the Sub-Registrar / Tenancy Authority under the "
                "Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017."
            ),
            "why_needed_ta": "தமிழ்நாடு வாடகை சட்டத்தின் கீழ் வாடகை அதிகாரியிடம் பதிவு செய்ய அசல் ஒப்பந்தம் தேவை.",
            "official_source_url": "https://www.tenancy.tn.gov.in",
            "official_source_name": "Tamil Nadu Tenancy Portal / Registration Dept",
            "last_verified": LAST_VERIFIED_DATE,
            "is_mandatory": True,
            "depends_on": None,
            "notes": "Must contain clear tenancy period, monthly consideration, advance deposit, and termination rules.",
        },
        {
            "item_id": "chk_lease_id_proofs",
            "requirement": "Identity & Address Proofs of Landlord and Tenant",
            "requirement_ta": "உரிமையாளர் மற்றும் வாடகைதாரரின் அடையாள மற்றும் முகவரிச் சான்றுகள்",
            "why_needed": (
                "Statutory identity verification to confirm legal capacity of parties executing the lease. "
                "Aadhaar card, Passport, Voter ID, or Driving License."
            ),
            "why_needed_ta": "இரு தரப்பினரின் சட்டப்பூர்வ அடையாளத்தை உறுதிப்படுத்த ஆதார் அல்லது வாக்காளர் அட்டை அவசியம்.",
            "official_source_url": TNREGINET_URL,
            "official_source_name": "Registration Department, Tamil Nadu",
            "last_verified": LAST_VERIFIED_DATE,
            "is_mandatory": True,
            "depends_on": None,
            "notes": "Both parties must carry original ID documents along with self-attested photocopies.",
        },
        {
            "item_id": "chk_lease_ownership_proof",
            "requirement": "Proof of Ownership of Leased Premises (Patta / Sale Deed)",
            "requirement_ta": "சொத்து உரிமையாளர் என்பதற்கான சான்று (பட்டா / விற்பனை பத்திரம்)",
            "why_needed": (
                "Establishes that the lessor has the lawful right to grant leasehold rights and collect rent for the property."
            ),
            "why_needed_ta": "வாடகைக்கு விடும் நபருக்கு அந்த சொத்தை வாடகைக்கு விட உரிமை உள்ளதா என்பதை நிரூபிக்க.",
            "official_source_url": TN_REVENUE_URL,
            "official_source_name": "Revenue Department, Tamil Nadu",
            "last_verified": LAST_VERIFIED_DATE,
            "is_mandatory": True,
            "depends_on": None,
            "notes": "Copy of recent revenue Patta or registered title deed along with latest property tax receipt.",
        },
        {
            "item_id": "chk_lease_photos",
            "requirement": "Passport Size Photographs (Landlord & Tenant)",
            "requirement_ta": "பாஸ்போர்ட் அளவு புகைப்படங்கள் (உரிமையாளர் மற்றும் வாடகைதாரர்)",
            "why_needed": (
                "Affixed to the tenancy agreement and registration ledger at the registration office."
            ),
            "why_needed_ta": "பதிவு அலுவலக ஆவணங்கள் மற்றும் ஒப்பந்தத்தில் ஒட்டுவதற்கு தேவை.",
            "official_source_url": TNREGINET_URL,
            "official_source_name": "Registration Department Guidelines",
            "last_verified": LAST_VERIFIED_DATE,
            "is_mandatory": True,
            "depends_on": None,
            "notes": "Recent color passport photos with plain background.",
        },
        {
            "item_id": "chk_lease_stamp_paper",
            "requirement": "Non-Judicial Stamp Paper / E-Stamp Certificate",
            "requirement_ta": "முத்திரைத்தாள் அல்லது மின்-முத்திரை சான்றிதழ் (E-Stamp)",
            "why_needed": (
                "Ensures agreement is duly stamped as per the Indian Stamp Act and Tamil Nadu Stamp Schedule. "
                "Unstamped or insufficiently stamped agreements are inadmissible in legal proceedings."
            ),
            "why_needed_ta": "சட்டப்படி முத்திரைக் கட்டணம் செலுத்தி செல்லுபடியாகும் ஆவணமாக மாற்ற முத்திரைத்தாள் தேவை.",
            "official_source_url": TNREGINET_URL,
            "official_source_name": "Commercial Taxes and Registration Department",
            "last_verified": LAST_VERIFIED_DATE,
            "is_mandatory": True,
            "depends_on": None,
            "notes": (
                "VERIFICATION NOTE: Stamp paper value varies depending on the monthly rent amount, advance deposit, "
                "and tenancy duration (typically 1% of total rent for leases up to 5 years). Verify current schedule on TNREGINET."
            ),
        },
    ]


def generate_registration_checklist(
    property_type: str = "residential",
    transaction_type: str = "sale",
    language: str = "en",
) -> List[Dict[str, Any]]:
    """Generates an authoritative checklist of registration requirements for Tamil Nadu property transactions.
    
    Supports 'sale' (10 items) and 'lease' / 'rental' (5 items).
    """
    ttype = (transaction_type or "").lower().strip()

    if "lease" in ttype or "rent" in ttype or "tenancy" in ttype:
        items = _get_lease_checklist(property_type=property_type)
    else:
        items = _get_sale_checklist(property_type=property_type)

    return items
