from pydantic import BaseModel
from typing import Optional, List, Any

class ReportSection(BaseModel):
    section_id: str
    title: str
    content: Any
    section_type: str

class ReportResponse(BaseModel):
    report_id: str
    analysis_id: str
    document_type: str
    overall_summary: str
    sections: List[ReportSection]
    language: str
    generated_at: str
    disclaimer: str
    ai_interpretation_notice: str

class ExportRequest(BaseModel):
    format: str = "pdf"
    language: str = "en"
    include_tamil: bool = False
