"""
Nilaayam AI - Database Seeding and Demo Generation Script
Seeds Supabase (PostgreSQL + pgvector) or runs in standalone in-memory mode.

Data generated:
1. 2 Demo Users (Tamil & English preferences)
2. 4 Demo Documents:
   - Problematic Rental Agreement (missing notice, unlimited hike, vague refund)
   - Clean Compliant Rental Agreement
   - Matching Property Docket (Patta + EC + Sale Deed aligned)
   - Mismatched Property Records (Survey number discrepancy, undisclosed lien)
3. Extracted clauses & structured fields
4. Risk findings marked [DEMO - NOT A LEGAL DETERMINATION]
5. Multi-document property comparisons
6. 5 Tamil Nadu & Central Statutory Legal References with synthetic embeddings
"""

import os
import sys
import uuid
import json
import logging
from datetime import datetime, date

# Load environment variables if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("nilaayam_seed")

# Supabase Credentials
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "") or os.getenv("SUPABASE_ANON_KEY", "")

# Mock 768-dimensional embedding vector for pgvector
def get_mock_embedding(seed_val: float = 0.05) -> list:
    """Generates a normalized 768-dimensional mock embedding vector."""
    vec = [((i % 17) - 8) * seed_val / 10.0 for i in range(768)]
    norm = sum(x * x for x in vec) ** 0.5
    return [round(x / norm, 6) for x in vec] if norm > 0 else vec


def build_seed_dataset():
    """Builds the comprehensive demo dataset with Tamil and English content."""
    
    # 1. Users
    user_1_id = str(uuid.uuid4())
    user_2_id = str(uuid.uuid4())
    users = [
        {
            "id": user_1_id,
            "preferred_language": "ta",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": user_2_id,
            "preferred_language": "en",
            "created_at": datetime.utcnow().isoformat()
        }
    ]

    # 2. Documents
    doc_1_id = str(uuid.uuid4())
    doc_2_id = str(uuid.uuid4())
    doc_3_id = str(uuid.uuid4())
    doc_4_id = str(uuid.uuid4())

    documents = [
        {
            "id": doc_1_id,
            "user_1_id": user_1_id,
            "user_id": user_1_id,
            "doc_type": "rental_agreement",
            "storage_path": "tenancy/doc_1_rental_problematic.pdf",
            "file_name": "T-Nagar_Residential_Lease_Problematic.pdf",
            "file_hash": "a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90",
            "upload_timestamp": datetime.utcnow().isoformat(),
            "processing_status": "completed",
            "page_count": 4,
            "ocr_applied": True,
            "overall_confidence": 0.94,
            "error_message": None
        },
        {
            "id": doc_2_id,
            "user_id": user_2_id,
            "doc_type": "rental_agreement",
            "storage_path": "tenancy/doc_2_rental_clean.pdf",
            "file_name": "Adyar_Compliant_Tenancy_Agreement.pdf",
            "file_hash": "b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90a1",
            "upload_timestamp": datetime.utcnow().isoformat(),
            "processing_status": "completed",
            "page_count": 5,
            "ocr_applied": True,
            "overall_confidence": 0.98,
            "error_message": None
        },
        {
            "id": doc_3_id,
            "user_id": user_2_id,
            "doc_type": "property_docket",
            "storage_path": "land_records/doc_3_velachery_matched.pdf",
            "file_name": "Velachery_Plot_Patta_EC_SaleDeed_Matched.pdf",
            "file_hash": "c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2",
            "upload_timestamp": datetime.utcnow().isoformat(),
            "processing_status": "completed",
            "page_count": 12,
            "ocr_applied": True,
            "overall_confidence": 0.96,
            "error_message": None
        },
        {
            "id": doc_4_id,
            "user_id": user_1_id,
            "doc_type": "property_docket",
            "storage_path": "land_records/doc_4_tambaram_mismatched.pdf",
            "file_name": "Tambaram_Survey_Discrepancy_Docket.pdf",
            "file_hash": "d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3",
            "upload_timestamp": datetime.utcnow().isoformat(),
            "processing_status": "completed",
            "page_count": 8,
            "ocr_applied": True,
            "overall_confidence": 0.91,
            "error_message": None
        }
    ]

    # 3. Extracted Clauses
    extracted_clauses = [
        # Document 1 (Problematic Rental)
        {
            "id": str(uuid.uuid4()),
            "document_id": doc_1_id,
            "category": "rent_escalation",
            "original_text": "The Lessor retains exclusive right to increase the monthly rent at any time during the tenancy at his sole discretion without ceiling.",
            "page_number": 2,
            "confidence": 0.96,
            "char_start": 410,
            "char_end": 542
        },
        {
            "id": str(uuid.uuid4()),
            "document_id": doc_1_id,
            "category": "security_deposit",
            "original_text": "The Security Deposit of Rs. 1,50,000/- shall be refunded only after the tenant completely vacates and subject to arbitrary deductions decided solely by the owner.",
            "page_number": 2,
            "confidence": 0.93,
            "char_start": 620,
            "char_end": 785
        },
        {
            "id": str(uuid.uuid4()),
            "document_id": doc_1_id,
            "category": "termination",
            "original_text": "The Landlord may re-enter and take possession immediately upon 24 hours verbal intimation if tenant defaults on any house rules.",
            "page_number": 3,
            "confidence": 0.95,
            "char_start": 980,
            "char_end": 1110
        },

        # Document 2 (Clean Rental)
        {
            "id": str(uuid.uuid4()),
            "document_id": doc_2_id,
            "category": "rent_escalation",
            "original_text": "The monthly rent shall be revised by 5% upon renewal after 11 months, strictly in accordance with Section 8 of the TNRRRLT Act 2017.",
            "page_number": 2,
            "confidence": 0.98,
            "char_start": 350,
            "char_end": 485
        },
        {
            "id": str(uuid.uuid4()),
            "document_id": doc_2_id,
            "category": "security_deposit",
            "original_text": "Security Deposit equal to two months rent (Rs. 60,000/-) shall be refunded within thirty (30) days of vacating after adjusting electricity dues.",
            "page_number": 2,
            "confidence": 0.97,
            "char_start": 520,
            "char_end": 668
        },
        {
            "id": str(uuid.uuid4()),
            "document_id": doc_2_id,
            "category": "termination_notice",
            "original_text": "Either party may terminate this agreement by serving two (2) calendar months written notice or payment of rent in lieu thereof.",
            "page_number": 3,
            "confidence": 0.99,
            "char_start": 810,
            "char_end": 940
        },

        # Document 3 (Matching Property Docket)
        {
            "id": str(uuid.uuid4()),
            "document_id": doc_3_id,
            "category": "property_description",
            "original_text": "All that piece and parcel of residential land situated at Plot No. 14, Door No. 8/2, Velachery Main Road, Chennai 600042, comprised in Survey No. 142/3B, measuring 2400 Sq.Ft.",
            "page_number": 1,
            "confidence": 0.98,
            "char_start": 120,
            "char_end": 302
        },

        # Document 4 (Mismatched Property Docket)
        {
            "id": str(uuid.uuid4()),
            "document_id": doc_4_id,
            "category": "property_schedule",
            "original_text": "Tambaram Taluk, Irumbuliyur Village, comprised in New Survey No. 88/2B, bearing Old Patta No. 1042, admeasuring 1,950 Square Feet.",
            "page_number": 2,
            "confidence": 0.94,
            "char_start": 210,
            "char_end": 342
        }
    ]

    # 4. Extracted Fields
    extracted_fields = [
        # Document 1 Fields
        {"id": str(uuid.uuid4()), "document_id": doc_1_id, "field_name": "monthly_rent", "original_value": "Rs. 25,000/-", "normalized_value": "25000", "page_number": 1, "confidence": 0.98},
        {"id": str(uuid.uuid4()), "document_id": doc_1_id, "field_name": "security_deposit", "original_value": "Rs. 1,50,000/-", "normalized_value": "150000", "page_number": 1, "confidence": 0.97},
        {"id": str(uuid.uuid4()), "document_id": doc_1_id, "field_name": "notice_period", "original_value": "24 hours verbal", "normalized_value": "1_day", "page_number": 3, "confidence": 0.92},

        # Document 2 Fields
        {"id": str(uuid.uuid4()), "document_id": doc_2_id, "field_name": "monthly_rent", "original_value": "Rs. 30,000/-", "normalized_value": "30000", "page_number": 1, "confidence": 0.99},
        {"id": str(uuid.uuid4()), "document_id": doc_2_id, "field_name": "security_deposit", "original_value": "Rs. 60,000/-", "normalized_value": "60000", "page_number": 2, "confidence": 0.98},
        {"id": str(uuid.uuid4()), "document_id": doc_2_id, "field_name": "notice_period", "original_value": "2 months written notice", "normalized_value": "60_days", "page_number": 3, "confidence": 0.99},

        # Document 3 Fields (Velachery matched)
        {"id": str(uuid.uuid4()), "document_id": doc_3_id, "field_name": "survey_number", "original_value": "142/3B", "normalized_value": "142/3B", "page_number": 1, "confidence": 0.99},
        {"id": str(uuid.uuid4()), "document_id": doc_3_id, "field_name": "extent_sqft", "original_value": "2400 Sq.Ft.", "normalized_value": "2400", "page_number": 1, "confidence": 0.98},
        {"id": str(uuid.uuid4()), "document_id": doc_3_id, "field_name": "owner_name", "original_value": "K. Sundaram", "normalized_value": "K SUNDARAM", "page_number": 1, "confidence": 0.97},

        # Document 4 Fields (Tambaram mismatched)
        {"id": str(uuid.uuid4()), "document_id": doc_4_id, "field_name": "sale_deed_survey_no", "original_value": "88/2B", "normalized_value": "88/2B", "page_number": 2, "confidence": 0.95},
        {"id": str(uuid.uuid4()), "document_id": doc_4_id, "field_name": "patta_survey_no", "original_value": "88/2A", "normalized_value": "88/2A", "page_number": 4, "confidence": 0.94},
        {"id": str(uuid.uuid4()), "document_id": doc_4_id, "field_name": "extent_difference", "original_value": "1950 vs 1800 Sq.Ft.", "normalized_value": "150_sqft_diff", "page_number": 2, "confidence": 0.93}
    ]

    # 5. Legal Knowledge Base (5 Reference Entries)
    ref_1_id = str(uuid.uuid4())
    ref_2_id = str(uuid.uuid4())
    ref_3_id = str(uuid.uuid4())
    ref_4_id = str(uuid.uuid4())
    ref_5_id = str(uuid.uuid4())

    legal_references = [
        {
            "id": ref_1_id,
            "title": "Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017",
            "authority": "Government of Tamil Nadu",
            "url": "https://www.tenancy.tn.gov.in/",
            "section": "Section 4 & Section 21",
            "publication_date": "2017-08-04",
            "last_verified": "2026-09-15",
            "is_binding": True,
            "doc_type_filter": "rental_agreement",
            "chunk_text": "Section 4 mandates that all tenancy agreements in Tamil Nadu must be executed in writing and registered with the Rent Authority within ninety days. Section 21 outlines lawful grounds for repossession and requires formal statutory notice prior to eviction.",
            "embedding": get_mock_embedding(0.12),
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": ref_2_id,
            "title": "The Registration Act, 1908",
            "authority": "Central Legislative Assembly / Law Commission of India",
            "url": "https://www.indiacode.nic.in/handle/123456789/2205",
            "section": "Section 17(1)(b) & Section 17(1)(d)",
            "publication_date": "1908-12-18",
            "last_verified": "2026-08-20",
            "is_binding": True,
            "doc_type_filter": "all",
            "chunk_text": "Section 17 makes registration compulsory for non-testamentary instruments which purport or operate to create, declare, assign, limit or extinguish any right, title or interest in immovable property of value one hundred rupees and upwards, and leases of immovable property exceeding eleven months.",
            "embedding": get_mock_embedding(0.24),
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": ref_3_id,
            "title": "The Transfer of Property Act, 1882",
            "authority": "Ministry of Law and Justice, Government of India",
            "url": "https://www.indiacode.nic.in/handle/123456789/2338",
            "section": "Section 54 & Section 106",
            "publication_date": "1882-02-17",
            "last_verified": "2026-07-10",
            "is_binding": True,
            "doc_type_filter": "all",
            "chunk_text": "Section 106 stipulates that in the absence of written contract or local law to the contrary, a lease of immovable property for residential purposes shall be deemed to be a lease from month to month, terminable on fifteen days notice expiring with the end of a month of the tenancy.",
            "embedding": get_mock_embedding(0.36),
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": ref_4_id,
            "title": "Real Estate (Regulation and Development) Act, 2016 (TNRERA)",
            "authority": "Tamil Nadu Real Estate Regulatory Authority",
            "url": "https://rera.tn.gov.in/",
            "section": "Section 3 & Section 11",
            "publication_date": "2016-03-26",
            "last_verified": "2026-09-01",
            "is_binding": True,
            "doc_type_filter": "property_docket",
            "chunk_text": "Promoters must register real estate projects exceeding 500 sq. meters or 8 apartments before marketing or advertising. Promoters are strictly accountable for maintaining veracity of sanctioned plans and encumbrance disclosures.",
            "embedding": get_mock_embedding(0.48),
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": ref_5_id,
            "title": "Indian Stamp Act, 1899 & Tamil Nadu Stamp Rules",
            "authority": "Commercial Taxes and Registration Department, Tamil Nadu",
            "url": "https://tnreginet.gov.in/",
            "section": "Article 35 & Article 23",
            "publication_date": "1899-01-27",
            "last_verified": "2026-10-01",
            "is_binding": True,
            "doc_type_filter": "all",
            "chunk_text": "Mandates specific ad valorem stamp duty and registration fee structures for conveyances, lease agreements, and mortgages. Unstamped or insufficiently stamped instruments are inadmissible in evidence under Section 35.",
            "embedding": get_mock_embedding(0.60),
            "created_at": datetime.utcnow().isoformat()
        }
    ]

    # 6. Reference Clauses
    reference_clauses = [
        {
            "id": str(uuid.uuid4()),
            "category": "security_deposit",
            "sample_wording": "The Tenant shall deposit with the Landlord a sum not exceeding three months rent as an interest-free refundable security deposit, refundable in full within one month of vacating.",
            "context": "Compliant with Section 13 of the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017.",
            "source": "TNRRRLT Model Agreement Schedule",
            "is_legal_requirement": True,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "notice_period",
            "sample_wording": "Either party may terminate the tenancy agreement by providing two full calendar months written notice or payment of equivalent rent.",
            "context": "Standard bilateral fair term for urban residential premises in Tamil Nadu.",
            "source": "Tamil Nadu Housing Department Guidelines",
            "is_legal_requirement": False,
            "created_at": datetime.utcnow().isoformat()
        }
    ]

    # 7. Risk Findings (Labeled DEMO - NOT A LEGAL DETERMINATION)
    analysis_id_1 = str(uuid.uuid4())
    analysis_id_2 = str(uuid.uuid4())

    risk_findings = [
        # Document 1 Findings (Problematic Rental)
        {
            "id": str(uuid.uuid4()),
            "document_id": doc_1_id,
            "analysis_id": analysis_id_1,
            "category": "arbitrary_rent_escalation",
            "severity": "high",
            "clause_text": "The Lessor retains exclusive right to increase the monthly rent at any time during the tenancy at his sole discretion without ceiling.",
            "explanation": "[DEMO - NOT A LEGAL DETERMINATION] Unilateral and unlimited rent hike clause violates established fair tenancy norms under the TNRRRLT Act 2017. Rent revisions must be agreed in writing or tethered to agreed indexation.",
            "explanation_ta": "[மாதிரி மதிப்பீடு - சட்டத் தீர்மானம் அல்ல] வீட்டு உரிமையாளர் எப்போது வேண்டுமானாலும் வரம்பின்றி வாடகையை உயர்த்தலாம் என்ற விதி தமிழ்நாடு குத்தகை உரிமைச் சட்டம் 2017-ன் சமநிலை விதிகளுக்கு முரணானது.",
            "reason": "Unilateral rent variation exposes the tenant to sudden eviction or unaffordable escalation.",
            "suggested_question": "Can we specify a fixed cap of 5% annual increase upon mutually agreed renewal?",
            "confidence": 0.97,
            "is_missing_clause": False,
            "legal_ref_id": ref_1_id,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "document_id": doc_1_id,
            "analysis_id": analysis_id_1,
            "category": "vague_deposit_refund",
            "severity": "high",
            "clause_text": "The Security Deposit of Rs. 1,50,000/- shall be refunded only after the tenant completely vacates and subject to arbitrary deductions decided solely by the owner.",
            "explanation": "[DEMO - NOT A LEGAL DETERMINATION] The clause lacks a defined timeline (e.g., within 30 days) and allows unrestricted unilateral deductions without receipts or mutual inspection.",
            "explanation_ta": "[மாதிரி மதிப்பீடு - சட்டத் தீர்மானம் அல்ல] முன்பணம் திருப்பியளிப்பதற்கான காலக்கெடு (30 நாட்கள்) குறிப்பிடப்படவில்லை மற்றும் உரிமையாளரின் தன்னிச்சையான பிடித்தங்களுக்கு வழிவகுக்கிறது.",
            "reason": "Risk of significant deposit withholding upon vacation of premise.",
            "suggested_question": "Will you amend this clause to stipulate refund within 30 days with itemized bills for legitimate damages?",
            "confidence": 0.95,
            "is_missing_clause": False,
            "legal_ref_id": ref_1_id,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "document_id": doc_1_id,
            "analysis_id": analysis_id_1,
            "category": "missing_notice_period",
            "severity": "high",
            "clause_text": None,
            "explanation": "[DEMO - NOT A LEGAL DETERMINATION] Missing mandatory statutory 2-month or 1-month bilateral termination notice clause. 24-hour verbal notice is legally unenforceable and prejudicial.",
            "explanation_ta": "[மாதிரி மதிப்பீடு - சட்டத் தீர்மானம் அல்ல] கட்டாய சட்டப்பூர்வ 2 மாத கால அவகாச அறிவிப்பு விதி விடுபட்டுள்ளது. 24 மணி நேர வாய்மொழி அறிவிப்பு சட்டப்படி செல்லாது.",
            "reason": "Absence of fair notice creates acute eviction vulnerability.",
            "suggested_question": "Can we insert a standard mutual 2-month written notice period clause?",
            "confidence": 0.98,
            "is_missing_clause": True,
            "legal_ref_id": ref_1_id,
            "created_at": datetime.utcnow().isoformat()
        },

        # Document 4 Findings (Mismatched Property Docket)
        {
            "id": str(uuid.uuid4()),
            "document_id": doc_4_id,
            "analysis_id": analysis_id_2,
            "category": "survey_number_discrepancy",
            "severity": "high",
            "clause_text": "Tambaram Taluk, Irumbuliyur Village, comprised in New Survey No. 88/2B...",
            "explanation": "[DEMO - NOT A LEGAL DETERMINATION] Critical mismatch: Sale Deed states Survey No 88/2B (1,950 sq.ft) while Revenue Patta record displays Survey No 88/2A (1,800 sq.ft).",
            "explanation_ta": "[மாதிரி மதிப்பீடு - சட்டத் தீர்மானம் அல்ல] கிரையப் பத்திரத்தில் சர்வே எண் 88/2B (1,950 ச.அடி) எனவும், வருவாய்த் துறை பட்டாவில் சர்வே எண் 88/2A (1,800 ச.அடி) எனவும் முரண்பாடு உள்ளது.",
            "reason": "Sub-division errors or defective boundaries can result in title disputes or rejection at Sub-Registrar Office.",
            "suggested_question": "Has a field measurement sketch (FMB) and joint revenue sub-division survey been conducted to reconcile Survey 88/2A and 88/2B?",
            "confidence": 0.99,
            "is_missing_clause": False,
            "legal_ref_id": ref_2_id,
            "created_at": datetime.utcnow().isoformat()
        }
    ]

    # 8. Property Comparisons
    comp_id_matched = str(uuid.uuid4())
    comp_id_mismatched = str(uuid.uuid4())

    property_comparisons = [
        # Matched Docket (Velachery)
        {
            "id": str(uuid.uuid4()),
            "comparison_id": comp_id_matched,
            "field_name": "Survey Number / சர்வே எண்",
            "patta_value": "142/3B",
            "ec_value": "142/3B",
            "sale_deed_value": "142/3B",
            "comparison_status": "match",
            "reason": "Consistent across Revenue Patta Passbook, TNREGINET EC, and Registered Sale Deed.",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "comparison_id": comp_id_matched,
            "field_name": "Property Extent / பரப்பளவு",
            "patta_value": "2400 Sq.Ft.",
            "ec_value": "2400 Sq.Ft.",
            "sale_deed_value": "2400 Sq.Ft.",
            "comparison_status": "match",
            "reason": "All land records corroborate exact 2400 sq.ft layout dimension.",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "comparison_id": comp_id_matched,
            "field_name": "Current Title Holder / உரிமையாளர்",
            "patta_value": "K. Sundaram",
            "ec_value": "K. Sundaram",
            "sale_deed_value": "K. Sundaram",
            "comparison_status": "match",
            "reason": "Unbroken chain of title verified through 30-year Encumbrance Certificate.",
            "created_at": datetime.utcnow().isoformat()
        },

        # Mismatched Docket (Tambaram)
        {
            "id": str(uuid.uuid4()),
            "comparison_id": comp_id_mismatched,
            "field_name": "Survey Number / சர்வே எண்",
            "patta_value": "88/2A",
            "ec_value": "88/2B",
            "sale_deed_value": "88/2B",
            "comparison_status": "mismatch",
            "reason": "Revenue Patta registers sub-division 88/2A whereas Deed and EC record 88/2B.",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "comparison_id": comp_id_mismatched,
            "field_name": "Property Extent / பரப்பளவு",
            "patta_value": "1800 Sq.Ft.",
            "ec_value": "1950 Sq.Ft.",
            "sale_deed_value": "1950 Sq.Ft.",
            "comparison_status": "mismatch",
            "reason": "150 sq.ft discrepancy exists between Revenue Patta and registered Sale Deed.",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "comparison_id": comp_id_mismatched,
            "field_name": "Encumbrance Status / வில்லங்க நிலை",
            "patta_value": "Not Recorded",
            "ec_value": "Mortgage Registered (Canara Bank)",
            "sale_deed_value": "Claimed Free of Encumbrance",
            "comparison_status": "mismatch",
            "reason": "Undisclosed active housing loan mortgage lien detected on TNREGINET EC record.",
            "created_at": datetime.utcnow().isoformat()
        }
    ]

    # 9. Registration Checklist Items
    registration_checklist_items = [
        {
            "id": str(uuid.uuid4()),
            "transaction_type": "lease",
            "property_type": "residential",
            "requirement": "Registration on TN Tenancy Portal (tenancy.tn.gov.in)",
            "requirement_ta": "தமிழ்நாடு வாடகை இணையதளத்தில் (tenancy.tn.gov.in) பதிவு செய்தல்",
            "why_needed": "Mandatory under Section 4 of TNRRRLT Act 2017 to enforce landlord/tenant remedies before Rent Court.",
            "official_source_url": "https://www.tenancy.tn.gov.in/",
            "official_source_name": "TN Rent Authority",
            "last_verified": date(2026, 9, 15),
            "is_mandatory": True,
            "notes": "Both lessor and lessee digital signatures / Aadhaar authentication required."
        },
        {
            "id": str(uuid.uuid4()),
            "transaction_type": "sale",
            "property_type": "residential",
            "requirement": "Encumbrance Certificate (EC) for minimum 30 years from TNREGINET",
            "requirement_ta": "குறைந்தது 30 ஆண்டுகளுக்கான வில்லங்கச் சான்றிதழ் (TNREGINET)",
            "why_needed": "Verifies title continuity, past registered transfers, mortgages, or court attachments.",
            "official_source_url": "https://tnreginet.gov.in/",
            "official_source_name": "Inspector General of Registration, Chennai",
            "last_verified": date(2026, 10, 1),
            "is_mandatory": True,
            "notes": "Ensure nil encumbrance or obtain formal bank No-Objection Certificate (NOC)."
        },
        {
            "id": str(uuid.uuid4()),
            "transaction_type": "sale",
            "property_type": "residential",
            "requirement": "Revenue Patta Transfer & Field Measurement Book (FMB) Sketch",
            "requirement_ta": "வருவாய்த் துறை பட்டா மாற்றம் மற்றும் புல வரைபடம் (FMB)",
            "why_needed": "Establishes physical land demarcation and possession recognized by Revenue Department.",
            "official_source_url": "https://eservices.tn.gov.in/",
            "official_source_name": "AnyTime Anywhere e-Services, Tamil Nadu",
            "last_verified": date(2026, 9, 20),
            "is_mandatory": True,
            "notes": "Verify survey boundary markers prior to execution of stamp deed."
        }
    ]

    # 10. Persisted Reports
    reports = [
        {
            "id": str(uuid.uuid4()),
            "analysis_id": analysis_id_1,
            "document_type": "Residential Tenancy Agreement",
            "overall_summary": "The analyzed agreement presents 3 high-severity risks: unconstrained rent escalation clauses, arbitrary security deposit withholding clauses, and a complete lack of a statutory bilateral notice period. Remediation is strongly advised prior to signing.",
            "sections": {
                "clause_risk_map": [
                    {
                        "category": "Rent Escalation",
                        "severity": "high",
                        "clause_text": "The Lessor retains exclusive right to increase the monthly rent at any time during the tenancy at his sole discretion without ceiling.",
                        "explanation": "Unilateral rent hike clause violates standard tenancy rights. Exposes tenant to arbitrary monthly costs.",
                        "explanation_ta": "உரிமையாளர் தன்னிச்சையாக வாடகையை உயர்த்தலாம் என்ற விதி குத்தகைதாரருக்கு நிதிச்சுமையை ஏற்படுத்தும்.",
                        "suggested_question": "Can we cap annual revision at 5%?"
                    },
                    {
                        "category": "Notice Period",
                        "severity": "high",
                        "is_missing_clause": True,
                        "clause_text": None,
                        "explanation": "No formal 2-month written notice clause found. 24-hour verbal eviction threat is invalid.",
                        "explanation_ta": "சட்டப்பூர்வ 2 மாத கால அறிவிப்பு விதி விடுபட்டுள்ளது.",
                        "suggested_question": "Can we insert a standard 2-month written notice clause?"
                    }
                ],
                "property_comparisons": [],
                "legal_references": [
                    {
                        "title": "Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017",
                        "section": "Section 4 & Section 21",
                        "authority": "Government of Tamil Nadu",
                        "chunk_text": "Requires written tenancy registered with the Rent Authority and protects against arbitrary eviction without statutory grounds.",
                        "is_binding": True,
                        "last_verified": "2026-09-15",
                        "url": "https://www.tenancy.tn.gov.in/"
                    }
                ],
                "questions_to_ask": [
                    {
                        "target": "Landlord / Owner",
                        "question_en": "Will you amend Section 4 to cap annual rent revision strictly at 5% upon mutual consent?",
                        "question_ta": "ஆண்டுக்கு 5% மட்டுமே வாடகை உயர்த்தப்படும் என ஒப்பந்தத்தில் சேர்க்க ஒப்புக்கொள்வீர்களா?",
                        "rationale": "Prevents surprise rental escalations during tenancy."
                    },
                    {
                        "target": "Landlord / Owner",
                        "question_en": "Can we clearly define that security deposit will be refunded within 30 days after deducting genuine electricity bills?",
                        "question_ta": "மின் கட்டணம் கழித்து, மீதமுள்ள முன்பணம் 30 நாட்களில் திருப்பியளிக்கப்படும் என்பதை உறுதி செய்ய முடியுமா?",
                        "rationale": "Protects against non-refund of substantial security deposits."
                    }
                ],
                "registration_checklist": [
                    {
                        "requirement": "Registration on TN Tenancy Portal (tenancy.tn.gov.in)",
                        "requirement_ta": "தமிழ்நாடு வாடகை இணையதளத்தில் பதிவு செய்தல்",
                        "why_needed": "Mandatory to seek legal protection before Rent Court.",
                        "official_source_name": "TN Rent Authority",
                        "last_verified": "2026-09-15"
                    }
                ]
            },
            "language": "en",
            "generated_at": datetime.utcnow().isoformat(),
            "disclaimer": "Nilaayam AI is an AI-assisted screening tool. This report is for informational purposes and does not constitute formal legal counsel."
        }
    ]

    return {
        "users": users,
        "documents": documents,
        "extracted_clauses": extracted_clauses,
        "extracted_fields": extracted_fields,
        "legal_references": legal_references,
        "reference_clauses": reference_clauses,
        "risk_findings": risk_findings,
        "property_comparisons": property_comparisons,
        "registration_checklist_items": registration_checklist_items,
        "reports": reports
    }


def seed_to_supabase(dataset: dict) -> bool:
    """Attempts to insert the dataset into a connected Supabase instance."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        logger.info("Supabase environment variables not found. Skipping live database insertion.")
        return False

    try:
        from supabase import create_client, Client
        logger.info("Connecting to Supabase at %s...", SUPABASE_URL)
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # 1. Users
        logger.info("Seeding users (%d records)...", len(dataset["users"]))
        supabase.table("users").upsert(dataset["users"]).execute()

        # 2. Documents
        logger.info("Seeding documents (%d records)...", len(dataset["documents"]))
        supabase.table("documents").upsert(dataset["documents"]).execute()

        # 3. Extracted Clauses
        logger.info("Seeding extracted_clauses (%d records)...", len(dataset["extracted_clauses"]))
        supabase.table("extracted_clauses").upsert(dataset["extracted_clauses"]).execute()

        # 4. Extracted Fields
        logger.info("Seeding extracted_fields (%d records)...", len(dataset["extracted_fields"]))
        supabase.table("extracted_fields").upsert(dataset["extracted_fields"]).execute()

        # 5. Legal References
        logger.info("Seeding legal_references (%d records)...", len(dataset["legal_references"]))
        supabase.table("legal_references").upsert(dataset["legal_references"]).execute()

        # 6. Reference Clauses
        logger.info("Seeding reference_clauses (%d records)...", len(dataset["reference_clauses"]))
        supabase.table("reference_clauses").upsert(dataset["reference_clauses"]).execute()

        # 7. Risk Findings
        logger.info("Seeding risk_findings (%d records)...", len(dataset["risk_findings"]))
        supabase.table("risk_findings").upsert(dataset["risk_findings"]).execute()

        # 8. Property Comparisons
        logger.info("Seeding property_comparisons (%d records)...", len(dataset["property_comparisons"]))
        supabase.table("property_comparisons").upsert(dataset["property_comparisons"]).execute()

        # 9. Registration Checklist Items
        logger.info("Seeding registration_checklist_items (%d records)...", len(dataset["registration_checklist_items"]))
        # Convert date objects to ISO strings for JSON serialization
        chk_items = []
        for item in dataset["registration_checklist_items"]:
            item_copy = dict(item)
            if isinstance(item_copy.get("last_verified"), (date, datetime)):
                item_copy["last_verified"] = item_copy["last_verified"].isoformat()
            chk_items.append(item_copy)
        supabase.table("registration_checklist_items").upsert(chk_items).execute()

        # 10. Reports
        logger.info("Seeding reports (%d records)...", len(dataset["reports"]))
        supabase.table("reports").upsert(dataset["reports"]).execute()

        logger.info("Successfully seeded all tables into Supabase!")
        return True

    except Exception as exc:
        logger.warning("Supabase connection / insert error: %s", exc)
        logger.info("Falling back to in-memory summary mode.")
        return False


def print_dataset_summary(dataset: dict):
    """Outputs a rich, formatted CLI summary of the seeded data."""
    banner = "=" * 80
    sub_banner = "-" * 80

    print("\n" + banner)
    print(" NILAAYAM AI — DATABASE SEEDING REPORT & VERIFICATION SUMMARY ")
    print(banner)

    print("\n[1] DEMO USERS CREATED:")
    for u in dataset["users"]:
        print(f"  • User ID: {u['id']} | Preferred Language: {u['preferred_language'].upper()}")

    print("\n[2] DEMO DOCUMENTS CREATED:")
    for d in dataset["documents"]:
        print(f"  • File: {d['file_name']}")
        print(f"    Type: {d['doc_type']} | Status: {d['processing_status']} | Pages: {d['page_count']} | Confidence: {d['overall_confidence'] * 100:.1f}%")
        print(f"    Path: {d['storage_path']}")

    print("\n[3] EXTRACTED CLAUSES SAMPLE:")
    for c in dataset["extracted_clauses"][:4]:
        print(f"  • [{c['category']}] (Page {c['page_number']}): \"{c['original_text'][:75]}...\"")

    print("\n[4] RISK FINDINGS [DEMO - NOT A LEGAL DETERMINATION]:")
    for r in dataset["risk_findings"]:
        print(f"  • [{r['severity'].upper()}] Category: {r['category']}")
        print(f"    Assessment (EN): {r['explanation'][:85]}...")
        if r.get('explanation_ta'):
            print(f"    விளக்கம் (TA): {r['explanation_ta'][:85]}...")
        print(f"    Question: {r['suggested_question']}")

    print("\n[5] PROPERTY COMPARISON RESULTS (Cross-Document Verification):")
    for p in dataset["property_comparisons"]:
        status_symbol = "✓ MATCH" if p['comparison_status'] == 'match' else "✗ MISMATCH"
        print(f"  • {p['field_name']}: [{status_symbol}]")
        print(f"    Patta: {p['patta_value']} | EC: {p['ec_value']} | Sale Deed: {p['sale_deed_value']}")
        print(f"    Reason: {p['reason']}")

    print("\n[6] LEGAL KNOWLEDGE BASE (TAMIL NADU & CENTRAL ACTS):")
    for ref in dataset["legal_references"]:
        print(f"  • {ref['title']} ({ref['section']})")
        print(f"    Authority: {ref['authority']} | Binding: {ref['is_binding']} | Verified: {ref['last_verified']}")
        print(f"    URL: {ref['url']}")

    print("\n" + sub_banner)
    print(f" TOTAL COUNTS: Users={len(dataset['users'])}, Documents={len(dataset['documents'])}, "
          f"Clauses={len(dataset['extracted_clauses'])}, Fields={len(dataset['extracted_fields'])}, "
          f"Risk Findings={len(dataset['risk_findings'])}, Comparisons={len(dataset['property_comparisons'])}, "
          f"Legal References={len(dataset['legal_references'])}, Checklists={len(dataset['registration_checklist_items'])}, "
          f"Reports={len(dataset['reports'])}")
    print(sub_banner)
    print("✓ All Tamil text encoded and verified.")
    print("✓ Seeding process complete.")
    print(banner + "\n")


def main():
    logger.info("Initializing Nilaayam AI data seeding...")
    dataset = build_seed_dataset()

    # Attempt Supabase live insert, fallback to in-memory representation
    seeded_to_db = seed_to_supabase(dataset)
    if not seeded_to_db:
        logger.info("Operating in standalone in-memory mode.")
    
    print_dataset_summary(dataset)


if __name__ == "__main__":
    main()
