from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    RENTAL_AGREEMENT = "rental_agreement"
    PATTA = "patta"
    ENCUMBRANCE_CERTIFICATE = "encumbrance_certificate"
    SALE_DEED = "sale_deed"
    UNKNOWN = "unknown"

class ProcessingStatus(str, Enum):
    UPLOADED = "uploaded"
    EXTRACTING = "extracting"
    EXTRACTED = "extracted"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"

class ClauseItem(BaseModel):
    clause_number: Optional[str] = None
    title: str
    text: str
    category: str
    confidence: float = 0.95
    page_number: int = 1

class DocumentUploadResponse(BaseModel):
    document_id: str
    status: str
    message: str
    filename: str
    file_size: int
    uploaded_at: str
    doc_type: Optional[DocumentType] = None
    is_demo: bool = False

class DocumentStatusResponse(BaseModel):
    document_id: str
    status: str
    doc_type: Optional[DocumentType] = None
    upload_timestamp: Optional[str] = None
    extraction_confidence: Optional[float] = None
    page_count: Optional[int] = None
    ocr_applied: bool = False
    error_message: Optional[str] = None
    filename: Optional[str] = None
    progress: int = 100
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_demo: bool = False

class ExtractedClause(BaseModel):
    clause_id: str
    document_id: str
    category: str
    original_text: str
    page_number: int
    confidence: float
    char_start: Optional[int] = None
    char_end: Optional[int] = None

class ExtractedField(BaseModel):
    field_id: str
    document_id: str
    field_name: str
    original_value: str
    normalized_value: str
    page_number: int
    confidence: float

class ExtractedDataResponse(BaseModel):
    document_id: str
    doc_type: DocumentType = DocumentType.UNKNOWN
    full_text: str = ""
    clauses: List[ExtractedClause] = []
    fields: List[ExtractedField] = []
    page_count: int = 1
    ocr_applied: bool = False
    overall_confidence: float = 0.0
    warnings: List[str] = []
    is_demo: bool = False
