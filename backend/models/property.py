from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class FieldComparisonStatus(str, Enum):
    MATCH = "match"
    MISMATCH = "mismatch"
    LIKELY_OCR_ERROR = "likely_ocr_error"
    NOT_AVAILABLE = "not_available"
    SINGLE_SOURCE = "single_source"

class FieldComparison(BaseModel):
    field_name: str
    patta_value: Optional[str] = None
    ec_value: Optional[str] = None
    sale_deed_value: Optional[str] = None
    status: FieldComparisonStatus
    reason: Optional[str] = None
    patta_page: Optional[int] = None
    ec_page: Optional[int] = None
    sale_deed_page: Optional[int] = None
    patta_confidence: Optional[float] = None
    ec_confidence: Optional[float] = None
    sale_deed_confidence: Optional[float] = None

class RedFlag(BaseModel):
    flag_id: str
    description: str
    severity: str
    field_name: Optional[str] = None
    recommendation: str
    requires_official_verification: bool = True

class PropertyCompareRequest(BaseModel):
    patta_document_id: Optional[str] = None
    ec_document_id: Optional[str] = None
    sale_deed_document_id: Optional[str] = None
    language: str = "en"

class PropertyComparisonResponse(BaseModel):
    comparison_id: str
    field_comparisons: List[FieldComparison]
    red_flags: List[RedFlag]
    match_count: int
    mismatch_count: int
    not_available_count: int
    language: str
    generated_at: str
    disclaimer: str

class ChecklistRequest(BaseModel):
    property_type: str = "residential"
    transaction_type: str = "sale"
    language: str = "en"

class ChecklistItem(BaseModel):
    item_id: str
    requirement: str
    requirement_ta: Optional[str] = None
    why_needed: str
    why_needed_ta: Optional[str] = None
    official_source_url: Optional[str] = None
    official_source_name: Optional[str] = None
    last_verified: Optional[str] = None
    is_mandatory: bool = True
    depends_on: Optional[str] = None
    notes: Optional[str] = None

class ChecklistResponse(BaseModel):
    checklist_id: str
    property_type: str
    transaction_type: str
    items: List[ChecklistItem]
    total_items: int
    mandatory_count: int
    language: str
    generated_at: str
    disclaimer: str
    last_rule_verification: str
