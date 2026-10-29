"""Legal Reference Retriever Module for Nilaayam AI.

Provides semantic retrieval of statutory provisions and regulatory references
for agreement clauses, along with standard benchmark model clauses.
"""

import logging
from typing import List, Dict, Optional, Any

from legal_rag.knowledge_base import LegalKnowledgeBase

logger = logging.getLogger(__name__)

# Global singleton instance of LegalKnowledgeBase
_kb_instance: Optional[LegalKnowledgeBase] = None


def get_knowledge_base() -> LegalKnowledgeBase:
    """Returns or initializes the singleton LegalKnowledgeBase instance.
    
    Automatically seeds verified reference data if the knowledge base is empty.
    """
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = LegalKnowledgeBase()
        try:
            from legal_rag.seed_knowledge import seed_legal_knowledge
            seed_legal_knowledge(_kb_instance)
        except Exception as e:
            logger.warning(f"Could not auto-seed knowledge base: {e}")
    return _kb_instance


def retrieve_legal_references(
    clause_text: str,
    doc_type: str = "rental_agreement",
    top_k: int = 3
) -> List[Dict[str, Any]]:
    """Builds a search query from clause_text and doc_type, searches the knowledge base,
    and returns relevant legal references with score >= 0.3.
    """
    kb = get_knowledge_base()
    
    # Construct targeted search query combining clause excerpt and document context
    clean_text = " ".join(clause_text.split()[:40])  # Use key tokens from clause
    query = f"{doc_type} {clean_text}"
    
    raw_results = kb.search(query=query, doc_type=doc_type, top_k=top_k * 2)
    
    filtered_results: List[Dict[str, Any]] = []
    for item in raw_results:
        score = item.get("relevance_score", 0.0)
        if score >= 0.3:
            filtered_results.append({
                "ref_id": item.get("ref_id", ""),
                "title": item.get("title", ""),
                "authority": item.get("authority", ""),
                "url": item.get("url"),
                "section": item.get("section"),
                "excerpt": item.get("excerpt", ""),
                "is_binding": item.get("is_binding", True),
                "publication_date": item.get("publication_date"),
                "last_verified": item.get("last_verified"),
                "relevance_score": score,
            })
            if len(filtered_results) >= top_k:
                break
                
    return filtered_results


def get_reference_clauses(category: str) -> List[Dict[str, Any]]:
    """Returns benchmark / model reference clauses for a given category.
    
    Used for comparing user agreement terms against balanced, standard statutory practices.
    """
    cat = (category or "").lower().strip()
    
    benchmarks: Dict[str, List[Dict[str, Any]]] = {
        "rent_increase": [
            {
                "standard": "Standard Market Practice (Tamil Nadu / Urban)",
                "clause_text": (
                    "The monthly rent may be revised upwards upon mutual written consent after completion "
                    "of 11 months, with such revision capped at a maximum of 5% to 7% per annum."
                ),
                "cap_percentage": 7.0,
                "frequency_months": 11,
                "is_balanced": True,
                "notes": "Uncapped rent escalation clauses or hikes exceeding 10% per annum are considered harsh."
            },
            {
                "standard": "Model Tenancy Act Reference",
                "clause_text": (
                    "The rent shall be revised as per the terms mutually agreed in the tenancy agreement. "
                    "The landlord shall give notice in writing three months before the revised rent takes effect."
                ),
                "cap_percentage": 10.0,
                "frequency_months": 12,
                "is_balanced": True,
                "notes": "Requires 3 months prior written notice before revised rent takes effect."
            }
        ],
        "security_deposit": [
            {
                "standard": "Modern Tenancy Practice (Tamil Nadu)",
                "clause_text": (
                    "The Tenant shall pay an interest-free refundable security deposit equivalent to 2 to 3 months' "
                    "rent. The said deposit shall be refunded in full within 15 to 30 days of vacation after handing "
                    "over peaceful possession and subject to deduction for arrears or verified physical damage."
                ),
                "max_months": 3,
                "refund_days": 30,
                "is_balanced": True,
                "notes": "Historically 10 months was common under old TN Rent Control Act, modern practice favors 2-3 months."
            }
        ],
        "notice_period": [
            {
                "standard": "Mutual Fair Notice Clause",
                "clause_text": (
                    "Either party may terminate this agreement by serving a prior written notice of not less than "
                    "two (2) months (or one month by mutual agreement) to the other party without assigning reasons."
                ),
                "notice_months": 2,
                "is_mutual": True,
                "is_balanced": True,
                "notes": "One-sided notice periods or immediate forfeiture without cure periods are unfair."
            }
        ],
        "eviction": [
            {
                "standard": "Due Process & Statutory Grounds",
                "clause_text": (
                    "The Landlord may terminate tenancy and re-enter premises only upon continuous default in rent "
                    "for two consecutive months, substantial unauthorized alterations, or subletting without written "
                    "consent, provided a 30-day statutory rectification notice has been served."
                ),
                "cure_period_days": 30,
                "is_balanced": True,
                "notes": "Summary eviction without judicial or rent tribunal recourse is legally void."
            }
        ],
        "maintenance": [
            {
                "standard": "Split Responsibility Model",
                "clause_text": (
                    "The Landlord shall be responsible for all major structural repairs, external seepage, electrical "
                    "mains, and municipal property taxes. The Tenant shall be responsible for day-to-day minor maintenance, "
                    "bulb replacements, and running electricity and water consumption charges."
                ),
                "landlord_scope": "Structural repairs, major plumbing/electrical mains, property tax",
                "tenant_scope": "Day-to-day internal fixtures, utility bills",
                "is_balanced": True,
                "notes": "Vague 'all maintenance by tenant' clauses impose unfair burdens on tenants."
            }
        ],
        "penalties": [
            {
                "standard": "Capped Late Payment Interest",
                "clause_text": (
                    "In the event of delay in payment of monthly rent beyond the 10th of the calendar month, "
                    "simple interest not exceeding 1% to 1.5% per month (or Rs. 50/day capped at 5% of monthly rent) "
                    "may be levied."
                ),
                "is_balanced": True,
                "notes": "Exorbitant compound interest or daily forfeitures exceeding 5-10% of monthly rent are punitive."
            }
        ],
        "registration": [
            {
                "standard": "Statutory Registration Compliance",
                "clause_text": (
                    "Any tenancy exceeding a term of 11 months must be compulsorily registered under Section 17 "
                    "of the Registration Act 1908. Registration fees and stamp duty shall be borne equally by both parties."
                ),
                "is_balanced": True,
                "notes": "Unregistered leases exceeding 11 months are inadmissible as direct evidence of lease terms under Section 49."
            }
        ],
        "termination": [
            {
                "standard": "Mutual Termination & Force Majeure",
                "clause_text": (
                    "This agreement shall terminate upon expiry of the agreed term, or earlier by mutual written agreement, "
                    "or upon two months' advance written notice by either party. Neither party shall be liable for termination "
                    "resulting from force majeure events rendering the premises uninhabitable."
                ),
                "is_balanced": True,
                "notes": "Ensures mutual exit rights and protection against catastrophic property damage."
            }
        ],
        "rent_amount": [
            {
                "standard": "Clear Monthly Consideration",
                "clause_text": (
                    "The Tenant shall pay a monthly rent of a fixed specified sum, payable on or before the 5th day "
                    "of each Gregorian calendar month via bank transfer / cheque / online payment."
                ),
                "is_balanced": True,
                "notes": "Rent amount, payment mode, and due date must be explicitly defined without ambiguous variable additions."
            }
        ],
        "deposit_refund": [
            {
                "standard": "Deposit Return Timeline & Inventory Inspection",
                "clause_text": (
                    "The entire interest-free security deposit shall be refunded simultaneously with the physical handover "
                    "of vacant keys, subject only to deductions agreed in writing following a joint walkthrough inspection."
                ),
                "is_balanced": True,
                "notes": "Requires mutual inspection and prohibits unilateral arbitrary deductions by landlord."
            }
        ]
    }
    
    return benchmarks.get(cat, [
        {
            "standard": "General Balanced Clause",
            "clause_text": f"Standard mutual provision defining rights, responsibilities and terms for {category}.",
            "is_balanced": True,
            "notes": "Terms should be mutual, unambiguous, and compliant with applicable local tenancy laws."
        }
    ])
