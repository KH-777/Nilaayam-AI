import os
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from pydantic import BaseModel, Field

# App configuration
from backend.config import settings

# Attempt imports from sibling modules with graceful fallbacks
try:
    from backend.models.document import (
        DocumentUploadResponse,
        DocumentStatusResponse,
        ExtractedDataResponse,
        ClauseItem,
        ExtractedField,
    )
except ImportError:
    # Fallback model definitions if backend.models.document is being authored
    class ClauseItem(BaseModel):
        clause_number: Optional[str] = None
        title: str
        text: str
        category: str
        confidence: float = 0.95

    class ExtractedField(BaseModel):
        field_name: str
        field_value: Any
        confidence: float = 0.95
        source_clause: Optional[str] = None

    class DocumentUploadResponse(BaseModel):
        document_id: str
        filename: str
        file_size: int
        status: str
        is_demo: bool = False
        message: str
        uploaded_at: str

    class DocumentStatusResponse(BaseModel):
        document_id: str
        filename: Optional[str] = None
        status: str
        progress: int = 100
        is_demo: bool = False
        error: Optional[str] = None
        created_at: Optional[str] = None
        updated_at: Optional[str] = None

    class ExtractedDataResponse(BaseModel):
        document_id: str
        document_type: str = "rental_agreement"
        raw_text: str
        clauses: List[ClauseItem]
        fields: Dict[str, Any]
        metadata: Dict[str, Any] = Field(default_factory=dict)
        is_demo: bool = False

try:
    from backend.database import get_supabase
except ImportError:
    get_supabase = None

try:
    from backend.services.storage_service import (
        upload_file_to_storage,
        delete_file_from_storage,
        get_file_url,
    )
except ImportError:
    upload_file_to_storage = None
    delete_file_from_storage = None
    get_file_url = None

try:
    from backend.services.analysis_orchestrator import (
        get_document_store,
        orchestrate_document_analysis,
    )
except ImportError:
    get_document_store = None
    orchestrate_document_analysis = None

logger = logging.getLogger("nilaayam.routers.documents")

router = APIRouter(prefix="/documents", tags=["documents"])

# In-memory store for processed documents when Supabase is not configured
DOCUMENT_STORE: Dict[str, Dict[str, Any]] = {}

ALLOWED_EXTENSIONS = {ext.lower() for ext in settings.allowed_extensions}
MAX_FILE_SIZE_BYTES = settings.max_upload_size_mb * 1024 * 1024


def is_supabase_enabled() -> bool:
    """Check if Supabase credentials are valid and configured."""
    return bool(
        settings.supabase_url
        and (settings.supabase_service_role_key or settings.supabase_anon_key)
    )


def validate_uuid(val: str) -> str:
    """Validate that the given string conforms to UUID format."""
    try:
        return str(uuid.UUID(str(val).strip()))
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document_id: '{val}'. Expected valid UUID.",
        )


def generate_mock_extracted_data(doc_id: str, filename: str, doc_type: str) -> Dict[str, Any]:
    """Generate realistic sample Tamil Nadu legal extracted clauses and fields."""
    return {
        "document_id": doc_id,
        "document_type": doc_type or "rental_agreement",
        "raw_text": (
            "வாடகை ஒப்பந்தம் (RENTAL AGREEMENT)\n"
            "This Deed of Rental Agreement is executed on this 1st day of November 2024 at Chennai, Tamil Nadu.\n"
            "BETWEEN:\n"
            "Thiru. K. Ramaswamy, residing at No. 12, 4th Cross Street, Anna Nagar West, Chennai - 600040 (LESSOR)\n"
            "AND:\n"
            "Thiru. S. Karthik, residing at No. 45, Gandhi Road, T. Nagar, Chennai - 600017 (LESSEE)\n\n"
            "1. PREMISES: Flat No. 3B, Third Floor, Orchid Heights, Plot No. 142/3B, Anna Nagar West, Chennai.\n"
            "2. PERIOD: 11 months commencing from 01-11-2024 to 30-09-2025.\n"
            "3. RENT: Monthly rent fixed at Rs. 22,000/- payable on or before 5th of every English calendar month.\n"
            "4. SECURITY DEPOSIT: Rs. 1,50,000/- paid as interest-free security deposit refundable upon vacating.\n"
            "5. RENT ESCALATION: Lessor reserves right to increase rent arbitrarily as per market rates.\n"
            "6. REPAIRS: All maintenance and repairs shall be borne solely by the Lessee.\n"
            "7. PENALTY: Late rent attracts 18% monthly interest; Lessor may lock premises after 7 days delay."
        ),
        "clauses": [
            ClauseItem(
                clause_number="Clause 1",
                title="Parties and Demised Premises",
                text="Thiru. K. Ramaswamy (Lessor) leases to Thiru. S. Karthik (Lessee) Flat No. 3B, Orchid Heights, Anna Nagar West, Chennai 600040.",
                category="parties_and_property",
                confidence=0.98,
            ),
            ClauseItem(
                clause_number="Clause 2",
                title="Tenure of Tenancy",
                text="The tenancy shall be for an 11-month period commencing from 01-11-2024.",
                category="duration",
                confidence=0.96,
            ),
            ClauseItem(
                clause_number="Clause 3",
                title="Monthly Rent Consideration",
                text="Monthly rent is fixed at Rs. 22,000/- payable on or before 5th of each month.",
                category="financial_rent",
                confidence=0.99,
            ),
            ClauseItem(
                clause_number="Clause 4",
                title="Security Deposit & Deductions",
                text="Lessee has deposited Rs. 1,50,000/- as interest-free deposit refundable upon vacating subject to Lessor assessment.",
                category="security_deposit",
                confidence=0.94,
            ),
            ClauseItem(
                clause_number="Clause 5",
                title="Rent Escalation & Discretion",
                text="Lessor reserves unilateral right to increase rent arbitrarily at any time during tenancy.",
                category="escalation",
                confidence=0.92,
            ),
            ClauseItem(
                clause_number="Clause 6",
                title="Maintenance Responsibilities",
                text="All maintenance, repairs, and structural damages shall be borne exclusively by the Lessee.",
                category="maintenance",
                confidence=0.91,
            ),
            ClauseItem(
                clause_number="Clause 7",
                title="Default & Lockout Penalty",
                text="Late rent attracts 18% monthly interest; Lessor may lock premises without notice after 7 days non-payment.",
                category="penalties",
                confidence=0.95,
            ),
        ],
        "fields": {
            "lessor_name": "K. Ramaswamy",
            "lessor_name_tamil": "கே. ராமசுவாமி",
            "lessee_name": "S. Karthik",
            "property_address": "Flat No. 3B, Orchid Heights, Plot No. 142/3B, Anna Nagar West, Chennai - 600040",
            "district": "Chennai",
            "state": "Tamil Nadu",
            "monthly_rent": 22000,
            "security_deposit": 150000,
            "tenancy_period_months": 11,
            "commencement_date": "2024-11-01",
            "rent_due_day": 5,
            "notice_period_specified": False,
        },
        "metadata": {
            "filename": filename,
            "ocr_applied": True,
            "primary_language": "en+tam",
            "pages_processed": 3,
        },
        "is_demo": True,
    }


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Document",
)
@router.post(
    "/",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def upload_document(
    file: UploadFile = File(..., description="Document file (PDF, DOCX, PNG, JPG, JPEG, TIFF)"),
    document_type: Optional[str] = Form(None, description="Optional type: rental_agreement, sale_deed, patta, ec"),
):
    """
    Accepts multipart file upload:
    - Validates file type against allowed extensions
    - Validates file size (max 20MB)
    - Extracts text and clauses from the uploaded file
    - Stores the extraction in memory, and in Supabase when configured
    - Returns DocumentUploadResponse with UUID
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing.",
        )

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Read and validate size
    try:
        content = await file.read()
    except Exception as e:
        logger.error(f"Failed to read uploaded file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not read uploaded file content.",
        )

    file_size = len(content)
    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size ({file_size / (1024*1024):.2f} MB) exceeds maximum limit of {settings.max_upload_size_mb} MB.",
        )

    doc_id = str(uuid.uuid4())
    uploaded_at = datetime.utcnow().isoformat()
    storage_path = f"documents/{doc_id}/{file.filename}"
    doc_type_val = document_type or "rental_agreement"

    if not callable(orchestrate_document_analysis):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document analysis pipeline is unavailable.",
        )

    extracted = await orchestrate_document_analysis(
        document_id=doc_id,
        file_content=content,
        filename=file.filename,
        doc_type_hint=doc_type_val,
    )
    if not extracted.full_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "No readable text could be extracted from this file. Scanned documents require OCR support.",
                "warnings": extracted.warnings,
            },
        )

    DOCUMENT_STORE[doc_id] = {
        "id": doc_id,
        "filename": file.filename,
        "file_size": file_size,
        "mime_type": file.content_type,
        "storage_path": storage_path,
        "document_type": extracted.doc_type.value,
        "status": "completed",
        "progress": 100,
        "created_at": uploaded_at,
        "updated_at": datetime.utcnow().isoformat(),
        "extracted_data": extracted.model_dump(),
        "is_demo": False,
    }

    client = get_supabase() if callable(get_supabase) else None
    if client:
        try:
            if callable(upload_file_to_storage):
                await upload_file_to_storage(
                    file_bytes=content,
                    storage_path=storage_path,
                    content_type=file.content_type or "application/octet-stream",
                )
            else:
                client.storage.from_(settings.supabase_storage_bucket).upload(
                    path=storage_path,
                    file=content,
                    file_options={"content-type": file.content_type or "application/octet-stream"},
                )

            client.table("documents").insert({
                "id": doc_id,
                "filename": file.filename,
                "file_size": file_size,
                "mime_type": file.content_type,
                "storage_path": storage_path,
                "document_type": extracted.doc_type.value,
                "status": "completed",
                "created_at": uploaded_at,
                "updated_at": datetime.utcnow().isoformat(),
            }).execute()
        except Exception as e:
            logger.warning("Supabase persistence failed; keeping document in local memory: %s", e)

    return DocumentUploadResponse(
        document_id=doc_id,
        filename=file.filename,
        file_size=file_size,
        status="completed",
        doc_type=extracted.doc_type,
        is_demo=False,
        message="Document text and clauses extracted successfully.",
        uploaded_at=uploaded_at,
    )


@router.get(
    "/{document_id}/status",
    response_model=DocumentStatusResponse,
    summary="Get Document Processing Status",
)
async def get_document_status(document_id: str):
    """
    Returns DocumentStatusResponse with current processing status.
    """
    valid_id = validate_uuid(document_id)

    # 1. Check the in-memory store first.
    if valid_id in DOCUMENT_STORE:
        doc = DOCUMENT_STORE[valid_id]
        return DocumentStatusResponse(
            document_id=doc["id"],
            filename=doc.get("filename"),
            status=doc.get("status", "completed"),
            progress=doc.get("progress", 100),
            is_demo=False,
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
        )

    # 2. Check Supabase DB if enabled
    client = get_supabase() if callable(get_supabase) else None
    if client:
        try:
            res = client.table("documents").select("*").eq("id", valid_id).execute()
            if res.data and len(res.data) > 0:
                row = res.data[0]
                return DocumentStatusResponse(
                    document_id=row["id"],
                    filename=row.get("filename"),
                    status=row.get("status", "completed"),
                    progress=100 if row.get("status") == "completed" else 50,
                    is_demo=False,
                    created_at=row.get("created_at"),
                    updated_at=row.get("updated_at"),
                )
        except Exception as e:
            logger.error(f"Error querying Supabase for status: {str(e)}")

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Document with ID '{valid_id}' not found.",
    )


@router.get(
    "/{document_id}/extracted-data",
    response_model=ExtractedDataResponse,
    summary="Get Extracted Text, Clauses, and Fields",
)
async def get_extracted_data(document_id: str):
    """
    Returns ExtractedDataResponse with full extracted text, clauses, and structured fields.
    """
    valid_id = validate_uuid(document_id)

    # 1. Check the in-memory store.
    if valid_id in DOCUMENT_STORE:
        extracted = DOCUMENT_STORE[valid_id].get("extracted_data")
        if extracted:
            return ExtractedDataResponse(**extracted)

    # 2. Check Supabase DB
    client = get_supabase() if callable(get_supabase) else None
    if client:
        try:
            res = client.table("extracted_data").select("*").eq("document_id", valid_id).execute()
            if res.data and len(res.data) > 0:
                row = res.data[0]
                return ExtractedDataResponse(
                    document_id=row["document_id"],
                    doc_type=row.get("doc_type", row.get("document_type", "unknown")),
                    full_text=row.get("full_text", row.get("raw_text", "")),
                    clauses=row.get("clauses", []),
                    fields=row.get("fields", []),
                    page_count=row.get("page_count", 1),
                    ocr_applied=row.get("ocr_applied", False),
                    overall_confidence=row.get("overall_confidence", 0.0),
                    warnings=row.get("warnings", []),
                    is_demo=False,
                )
        except Exception as e:
            logger.error(f"Error querying Supabase for extracted data: {str(e)}")

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Extracted data for document '{valid_id}' not found.",
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Document",
)
async def delete_document(document_id: str):
    """
    Deletes document from storage and DB, returns 204.
    """
    valid_id = validate_uuid(document_id)
    found = False

    if valid_id in DOCUMENT_STORE:
        DOCUMENT_STORE.pop(valid_id, None)
        if callable(get_document_store):
            get_document_store().pop(valid_id, None)
        found = True

    # Remove from Supabase DB and Storage if configured
    client = get_supabase() if callable(get_supabase) else None
    if client:
        try:
            # Query storage path
            res = client.table("documents").select("storage_path").eq("id", valid_id).execute()
            if res.data and len(res.data) > 0:
                found = True
                storage_path = res.data[0].get("storage_path")
                if storage_path:
                    if callable(delete_file_from_storage):
                        await delete_file_from_storage(storage_path)
                    else:
                        client.storage.from_(settings.supabase_storage_bucket).remove([storage_path])

                # Delete records
                client.table("extracted_data").delete().eq("document_id", valid_id).execute()
                client.table("documents").delete().eq("id", valid_id).execute()
        except Exception as e:
            logger.error(f"Error deleting document from Supabase: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete document: {str(e)}",
            )

    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{valid_id}' not found.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
