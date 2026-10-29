"""Seed Legal Knowledge Module for Nilaayam AI.

Populates the knowledge base with statutory references from Tamil Nadu Rent Control & Tenancy Laws,
the Registration Act 1908, Tamil Nadu Registration Department guidelines, and model agreement clauses.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def seed_legal_knowledge(kb: Optional[object] = None) -> int:
    """Populates the knowledge base with statutory references, registration rules, and model clauses.
    
    Returns the total number of references added.
    """
    if kb is None:
        from legal_rag.retriever import get_knowledge_base
        kb = get_knowledge_base()

    references_data = [
        # 1. Tamil Nadu Rent Control & Tenancy Provisions
        {
            "title": "Tamil Nadu Buildings (Lease and Rent Control) Act, 1960 - Determination of Standard Rent",
            "authority": "Government of Tamil Nadu / Tamil Nadu Legislative Assembly",
            "url": "https://www.indiacode.nic.in/handle/123456789/10189",
            "section": "Section 4",
            "text": (
                "Section 4 of the Tamil Nadu Buildings (Lease and Rent Control) Act provides the framework "
                "for fixation of fair rent based on the market value of the site, construction cost, and statutory "
                "percentage returns (typically 9% for residential buildings and 12% for non-residential buildings). "
                "Any agreement to pay rent in excess of fair rent determined is legally unenforceable."
            ),
            "is_binding": True,
            "publication_date": "1960-09-30",
            "last_verified": "2024-01-15",
            "verification_note": (
                "CRITICAL: The Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017 "
                "has superseded older fair rent provisions for new tenancies. Parties must verify current applicability "
                "with an advocate, as modern tenancy law leaves rent revision primarily to mutual written contract."
            ),
            "doc_type": "rental_agreement",
        },
        {
            "title": "Tamil Nadu Buildings (Lease and Rent Control) Act, 1960 - Grounds for Eviction",
            "authority": "Government of Tamil Nadu / Rent Controller Jurisdiction",
            "url": "https://www.indiacode.nic.in/handle/123456789/10189",
            "section": "Section 10",
            "text": (
                "Section 10 stipulates that a tenant shall not be evicted, whether in execution of a decree or otherwise, "
                "except in accordance with the provisions of this Section. Grounds for eviction include: willful default in "
                "payment of rent, subletting without written consent, using building for purpose other than authorized, "
                "acts of waste impairing building value, nuisance to neighbors, or bona fide own occupation requirement."
            ),
            "is_binding": True,
            "publication_date": "1960-09-30",
            "last_verified": "2024-01-15",
            "verification_note": (
                "Eviction can only occur through due judicial process before the designated Rent Court / Tribunal. "
                "Any lease clause permitting summary physical eviction or utility disconnection without court order is void."
            ),
            "doc_type": "rental_agreement",
        },
        {
            "title": "Tamil Nadu Tenancy Laws - Security Deposit Limits and Deductions",
            "authority": "Tamil Nadu Tenancy Regulatory Framework",
            "url": "https://www.indiacode.nic.in/handle/123456789/10189",
            "section": "Section 12 (Historic) & Tenancy Act 2017 Chapter III",
            "text": (
                "Historically under Section 12 of the 1960 Act, landlords commonly received up to a maximum of "
                "one to ten months' rent as advance deposit in Tamil Nadu urban markets. However, under the Model Tenancy Act "
                "and modern regulatory reforms, security deposits for residential premises are capped at not more than "
                "two to three months' rent, refundable within one month of vacating the premises after agreed adjustments."
            ),
            "is_binding": True,
            "publication_date": "2017-08-04",
            "last_verified": "2024-01-15",
            "verification_note": (
                "Requires verification: While prevailing urban practice in Chennai/Tamil Nadu often demands 6 to 10 months "
                "advance rent, modern statutory guidelines cap residential deposits at 2 to 3 months. Confirm terms before signing."
            ),
            "doc_type": "rental_agreement",
        },

        # 2. Registration Act 1908 Provisions
        {
            "title": "Registration Act, 1908 - Documents Compulsorily Registrable",
            "authority": "Legislative Department, Ministry of Law and Justice, Government of India",
            "url": "https://www.indiacode.nic.in/handle/123456789/2202",
            "section": "Section 17",
            "text": (
                "Section 17(1) mandates compulsory registration for: (b) other non-testamentary instruments which purport "
                "or operate to create, declare, assign, limit or extinguish any right, title or interest of value of Rs. 100 "
                "and upwards to or in immovable property; and (d) leases of immovable property from year to year, or for any term "
                "exceeding one year, or reserving a yearly rent. Rental agreements of 11 months are traditionally executed to "
                "avoid mandatory registration, though Tamil Nadu Tenancy Act 2017 requires all tenancy agreements to be registered."
            ),
            "is_binding": True,
            "publication_date": "1908-12-18",
            "last_verified": "2024-01-15",
            "verification_note": (
                "Mandatory statutory provision. In Tamil Nadu, under the 2017 Tenancy Act, all rental agreements "
                "must be registered with the Rent Authority regardless of duration."
            ),
            "doc_type": "registration",
        },
        {
            "title": "Registration Act, 1908 - Effect of Non-Registration of Mandatory Documents",
            "authority": "Legislative Department, Ministry of Law and Justice, Government of India",
            "url": "https://www.indiacode.nic.in/handle/123456789/2202",
            "section": "Section 49",
            "text": (
                "Section 49 provides that no document required by Section 17 or by any provision of the Transfer of Property "
                "Act, 1882 to be registered shall affect any immovable property comprised therein, or be received as evidence "
                "of any transaction affecting such property, unless it has been registered. An unregistered lease exceeding "
                "one year cannot be produced as substantive evidence of lease terms in legal proceedings."
            ),
            "is_binding": True,
            "publication_date": "1908-12-18",
            "last_verified": "2024-01-15",
            "verification_note": (
                "Supreme Court precedent allows unregistered documents to be used only for collateral purposes "
                "(such as proving nature of possession), but not to enforce lease clauses or covenants."
            ),
            "doc_type": "registration",
        },

        # 3. Tamil Nadu Registration Department Guidance
        {
            "title": "Tamil Nadu Registration Department - Mandatory Documents for Property Sale Registration",
            "authority": "Inspector General of Registration, Government of Tamil Nadu (TNREGINET)",
            "url": "https://tnreginet.gov.in",
            "section": "Sale Deed Registration Checklist",
            "text": (
                "Mandatory documents required at the Sub-Registrar Office for registration of sale deed: "
                "1. Original draft Sale Deed with stamp duty paid. "
                "2. Revenue Patta / Chitta in the name of the vendor (Record of Rights). "
                "3. Encumbrance Certificate (EC) for a minimum period of 30 years. "
                "4. Parent title deeds / chain of ownership documents. "
                "5. Government guideline valuation printout from TNREGINET portal. "
                "6. PAN cards of vendor and purchaser (or Form 60/61). "
                "7. Aadhaar / Photo ID proof of buyer, seller, and two identifying witnesses. "
                "8. Property tax paid receipt and electricity bill."
            ),
            "is_binding": True,
            "publication_date": "2023-04-01",
            "last_verified": "2024-01-15",
            "verification_note": (
                "Guidelines issued by TN Registration Department. SRO offices may mandate additional revenue "
                "or layout approvals (DTCP/CMDA) depending on whether the property is an unapproved plot or agricultural land."
            ),
            "doc_type": "property_verification",
        },
        {
            "title": "Tamil Nadu Registration Department - Encumbrance Certificate (EC) Requirements",
            "authority": "Inspector General of Registration, Government of Tamil Nadu (TNREGINET)",
            "url": "https://tnreginet.gov.in",
            "section": "EC Inspection & Search Guidelines",
            "text": (
                "An Encumbrance Certificate (Villangam Sanrithaazh) reflects registered transactions, mortgages, "
                "charges, and court attachments over the surveyed property. For clean title verification in Tamil Nadu: "
                "1. Search must cover a minimum uninterrupted period of 30 years up to the date of registration. "
                "2. Survey number, subdivision number, village, and boundaries must precisely match the Patta and Sale Deed. "
                "3. A nil encumbrance EC indicates no registered encumbrance, but unrecorded oral family partitions, "
                "undisclosed litigation, or bank equitable mortgages without registered memo may not be reflected."
            ),
            "is_binding": True,
            "publication_date": "2023-04-01",
            "last_verified": "2024-01-15",
            "verification_note": (
                "An EC is an official record of registered transactions but does not guarantee marketable title against "
                "unregistered legal heirs' claims, minor rights, or tax liens."
            ),
            "doc_type": "property_verification",
        },
        {
            "title": "Tamil Nadu Stamp Duty and Registration Fee Schedule",
            "authority": "Commercial Taxes and Registration Department, Government of Tamil Nadu",
            "url": "https://tnreginet.gov.in",
            "section": "Stamp Duty Schedule - Conveyance (Sale)",
            "text": (
                "In Tamil Nadu, the effective charges for registration of a deed of conveyance (Sale Deed) of immovable property "
                "are computed on the market guideline value or consideration (whichever is higher): "
                "Stamp Duty: 7% of property market value; "
                "Registration Fee: 4% of property market value (or revised rate as per Tamil Nadu Budget notifications); "
                "Total government charges typically equal approximately 11% (or 7% + 2% for specific subsidized categories). "
                "Stamp duty for lease agreements varies between 1% to 4% depending on lease term."
            ),
            "is_binding": True,
            "publication_date": "2023-07-10",
            "last_verified": "2024-01-15",
            "verification_note": (
                "Stamp duty and registration fee rates are periodically revised by the Tamil Nadu State Budget and Finance Bills. "
                "Always generate an official e-payment challan on TNREGINET to verify exact current percentage and fees."
            ),
            "doc_type": "registration",
        },

        # 4. Model Rental Agreement Clauses (ILLUSTRATIVE - NOT BINDING)
        {
            "title": "Model Clause - Standard Mutual Notice Period [ILLUSTRATIVE]",
            "authority": "Model Tenancy Guidelines / Legal Drafting Benchmark",
            "url": None,
            "section": "Clause Benchmark: Notice Period",
            "text": (
                "ILLUSTRATIVE BENCHMARK: Either party shall be entitled to terminate this tenancy by giving not less "
                "than two (2) full calendar months' notice in writing to the other party, or by paying two months' rent in "
                "lieu of notice. Upon expiry of such notice period, the Tenant shall peacefully vacate and hand over vacant "
                "possession of the premises to the Landlord."
            ),
            "is_binding": False,
            "publication_date": "2022-01-01",
            "last_verified": "2024-01-15",
            "verification_note": (
                "ILLUSTRATIVE ONLY - Not legally binding statutory text. Represents balanced drafting benchmark to prevent "
                "immediate unilateral forfeiture or sudden eviction."
            ),
            "doc_type": "rental_agreement",
        },
        {
            "title": "Model Clause - Security Deposit and Deduction Timeline [ILLUSTRATIVE]",
            "authority": "Model Tenancy Guidelines / Legal Drafting Benchmark",
            "url": None,
            "section": "Clause Benchmark: Security Deposit",
            "text": (
                "ILLUSTRATIVE BENCHMARK: The Tenant deposits an interest-free refundable sum equivalent to three (3) months' rent. "
                "The Landlord shall inspect the premises jointly with the Tenant on the day of vacation and shall refund the entire "
                "deposit amount within fifteen (15) days of vacation, deducting only proven unpaid electricity/water utility bills "
                "and actual cost of repairing structural damages caused beyond fair wear and tear."
            ),
            "is_binding": False,
            "publication_date": "2022-01-01",
            "last_verified": "2024-01-15",
            "verification_note": (
                "ILLUSTRATIVE ONLY - Not legally binding statutory text. Parties can customize deposit amount and refund window "
                "by mutual consent."
            ),
            "doc_type": "rental_agreement",
        },
        {
            "title": "Model Clause - Annual Rent Escalation Cap [ILLUSTRATIVE]",
            "authority": "Model Tenancy Guidelines / Legal Drafting Benchmark",
            "url": None,
            "section": "Clause Benchmark: Rent Escalation",
            "text": (
                "ILLUSTRATIVE BENCHMARK: The monthly rent agreed herein shall remain fixed for the initial term of eleven (11) months. "
                "In the event of renewal of the tenancy by mutual written agreement, the monthly rent may be escalated by not more "
                "than five percent (5%) to seven percent (7%) of the then-current monthly rent."
            ),
            "is_binding": False,
            "publication_date": "2022-01-01",
            "last_verified": "2024-01-15",
            "verification_note": (
                "ILLUSTRATIVE ONLY - Not legally binding statutory text. Rent increases are governed by contractual consensus "
                "unless capped by local rent control legislation."
            ),
            "doc_type": "rental_agreement",
        },
        {
            "title": "Model Clause - Division of Maintenance Responsibilities [ILLUSTRATIVE]",
            "authority": "Model Tenancy Guidelines / Legal Drafting Benchmark",
            "url": None,
            "section": "Clause Benchmark: Maintenance and Repairs",
            "text": (
                "ILLUSTRATIVE BENCHMARK: The Landlord shall be responsible for all major structural repairs, dampness/seepage, "
                "roof waterproofing, municipal property taxes, and replacement of main water pump/pipes. The Tenant shall be "
                "responsible for day-to-day internal upkeep, replacing light fixtures and bulbs, minor tap leakage repairs, "
                "and regular payment of consumption electricity, internet, and monthly resident association maintenance fees."
            ),
            "is_binding": False,
            "publication_date": "2022-01-01",
            "last_verified": "2024-01-15",
            "verification_note": (
                "ILLUSTRATIVE ONLY - Not legally binding statutory text. Clearly demarcates structural vs. cosmetic liabilities "
                "to prevent landlord-tenant friction."
            ),
            "doc_type": "rental_agreement",
        },
    ]

    total_added = 0
    for ref in references_data:
        try:
            chunk_ids = kb.add_document(
                title=ref["title"],
                authority=ref["authority"],
                url=ref["url"],
                section=ref["section"],
                text=ref["text"],
                is_binding=ref["is_binding"],
                publication_date=ref["publication_date"],
                last_verified=ref["last_verified"],
                verification_note=ref["verification_note"],
                doc_type=ref.get("doc_type", "general"),
            )
            total_added += len(chunk_ids)
        except Exception as e:
            logger.error(f"Error seeding reference '{ref['title']}': {e}")

    logger.info(f"Seeded {total_added} legal reference chunks into knowledge base.")
    return total_added
