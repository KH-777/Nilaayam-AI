from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class RiskSeverity(str, Enum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    GREY = "grey"

class LegalReference(BaseModel):
    ref_id: str
    title: str
    authority: str
    url: Optional[str] = None
    section: Optional[str] = None
    publication_date: Optional[str] = None
    last_verified: Optional[str] = None
    is_binding: bool = True
    excerpt: Optional[str] = None

class RiskFinding(BaseModel):
    finding_id: str
    document_id: str
    clause_text: str
    clause_category: str
    page_number: int
    severity: RiskSeverity
    explanation: str
    explanation_ta: Optional[str] = None
    reason: str
    legal_references: List[LegalReference] = []
    reference_comparison: Optional[str] = None
    suggested_question: str
    confidence: float
    is_missing_clause: bool = False

class AgreementAnalysisRequest(BaseModel):
    document_id: str
    language: str = "en"

class AgreementAnalysisResponse(BaseModel):
    analysis_id: str
    document_id: str
    overall_status: str
    red_count: int
    yellow_count: int
    green_count: int
    grey_count: int
    findings: List[RiskFinding]
    questions: List[str]
    language: str
    generated_at: str
    disclaimer: str
