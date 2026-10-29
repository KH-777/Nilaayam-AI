-- ============================================================================
-- Nilaayam AI - Database Schema Definition for Supabase (PostgreSQL + pgvector)
-- Platform: Land & Tenancy Legal Intelligence for Tamil Nadu
-- ============================================================================

-- 1. Enable Required Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Drop Tables if Needed (Safe Re-run ordering)
DROP TABLE IF EXISTS reports CASCADE;
DROP TABLE IF EXISTS registration_checklist_items CASCADE;
DROP TABLE IF EXISTS property_comparisons CASCADE;
DROP TABLE IF EXISTS risk_findings CASCADE;
DROP TABLE IF EXISTS reference_clauses CASCADE;
DROP TABLE IF EXISTS legal_references CASCADE;
DROP TABLE IF EXISTS extracted_fields CASCADE;
DROP TABLE IF EXISTS extracted_clauses CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================================================
-- Table: users
-- Stores end-users and language preferences
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    preferred_language TEXT NOT NULL DEFAULT 'en', -- 'en' or 'ta'
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE users IS 'User profiles and interface preferences for Nilaayam AI.';

-- ============================================================================
-- Table: documents
-- Uploaded property / tenancy legal files and processing telemetry
-- ============================================================================
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    doc_type TEXT NOT NULL, -- 'rental_agreement', 'sale_deed', 'patta', 'encumbrance_certificate', etc.
    storage_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_hash TEXT,
    upload_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    processing_status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    page_count INT DEFAULT 1,
    ocr_applied BOOLEAN NOT NULL DEFAULT false,
    overall_confidence FLOAT DEFAULT 0.0,
    error_message TEXT
);

COMMENT ON TABLE documents IS 'Metadata and tracking for uploaded land and lease documents.';

-- ============================================================================
-- Table: extracted_clauses
-- Atomic clauses parsed from legal contracts
-- ============================================================================
CREATE TABLE extracted_clauses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    category TEXT NOT NULL, -- e.g., 'rent_amount', 'security_deposit', 'termination_notice', 'maintenance'
    original_text TEXT NOT NULL,
    page_number INT DEFAULT 1,
    confidence FLOAT DEFAULT 0.0,
    char_start INT,
    char_end INT
);

COMMENT ON TABLE extracted_clauses IS 'Individual clauses parsed and segmented from documents.';

-- ============================================================================
-- Table: extracted_fields
-- Structured entities and key-value attributes (survey numbers, amounts, dates)
-- ============================================================================
CREATE TABLE extracted_fields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    field_name TEXT NOT NULL, -- e.g., 'survey_number', 'monthly_rent', 'lessor_name', 'guideline_value'
    original_value TEXT,
    normalized_value TEXT,
    page_number INT DEFAULT 1,
    confidence FLOAT DEFAULT 0.0
);

COMMENT ON TABLE extracted_fields IS 'Key structured property/lease attributes extracted by OCR & LLM.';

-- ============================================================================
-- Table: legal_references
-- Knowledge base of Tamil Nadu acts, central acts, and statutory rules with embeddings
-- ============================================================================
CREATE TABLE legal_references (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    authority TEXT NOT NULL,
    url TEXT,
    section TEXT,
    publication_date DATE,
    last_verified DATE,
    is_binding BOOLEAN NOT NULL DEFAULT true,
    doc_type_filter TEXT, -- target doc filter: 'rental_agreement', 'sale_deed', 'all'
    chunk_text TEXT NOT NULL,
    embedding VECTOR(768), -- Gemini text-embedding-004 representation
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE legal_references IS 'Statutory database supporting RAG retrieval and compliance verification.';

-- ============================================================================
-- Table: reference_clauses
-- Model legal clauses and standard drafting templates under Tamil Nadu regulations
-- ============================================================================
CREATE TABLE reference_clauses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category TEXT NOT NULL,
    sample_wording TEXT NOT NULL,
    context TEXT,
    source TEXT,
    is_legal_requirement BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE reference_clauses IS 'Standard benchmarking clauses compliant with TN statutory norms.';

-- ============================================================================
-- Table: risk_findings
-- Identified contractual risks, deviations, missing clauses, and mitigation recommendations
-- ============================================================================
CREATE TABLE risk_findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    analysis_id UUID NOT NULL,
    category TEXT NOT NULL,
    severity TEXT NOT NULL, -- 'high', 'medium', 'low', 'neutral'
    clause_text TEXT,
    explanation TEXT NOT NULL,
    explanation_ta TEXT,
    reason TEXT,
    suggested_question TEXT,
    confidence FLOAT DEFAULT 0.0,
    is_missing_clause BOOLEAN NOT NULL DEFAULT false,
    legal_ref_id UUID REFERENCES legal_references(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE risk_findings IS 'AI risk detections, statutory non-compliances, and bilingual mitigations.';

-- ============================================================================
-- Table: property_comparisons
-- Cross-document consistency verification (Patta vs EC vs Sale Deed)
-- ============================================================================
CREATE TABLE property_comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comparison_id UUID NOT NULL,
    field_name TEXT NOT NULL,
    patta_value TEXT,
    ec_value TEXT,
    sale_deed_value TEXT,
    comparison_status TEXT NOT NULL, -- 'match', 'mismatch', 'missing', 'unverified'
    reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE property_comparisons IS 'Multi-document entity alignment matrix across Revenue & Registration records.';

-- ============================================================================
-- Table: registration_checklist_items
-- Mandatory procedural requirements for TN Sub-Registrar Office execution
-- ============================================================================
CREATE TABLE registration_checklist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_type TEXT NOT NULL, -- 'lease', 'sale', 'gift', 'mortgage'
    property_type TEXT NOT NULL, -- 'residential', 'commercial', 'agricultural'
    requirement TEXT NOT NULL,
    requirement_ta TEXT,
    why_needed TEXT,
    official_source_url TEXT,
    official_source_name TEXT,
    last_verified DATE,
    is_mandatory BOOLEAN NOT NULL DEFAULT true,
    notes TEXT
);

COMMENT ON TABLE registration_checklist_items IS 'Statutory checklist for registration under TN Registration Department.';

-- ============================================================================
-- Table: reports
-- Synthesized legal analysis reports (persisting generated summaries & sections)
-- ============================================================================
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL,
    document_type TEXT NOT NULL,
    overall_summary TEXT NOT NULL,
    sections JSONB NOT NULL DEFAULT '{}'::jsonb,
    language TEXT NOT NULL DEFAULT 'en',
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    disclaimer TEXT NOT NULL
);

COMMENT ON TABLE reports IS 'Persisted compiled analytical reports with bilingual payload.';

-- ============================================================================
-- Performance Indexes
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_extracted_clauses_document_id ON extracted_clauses(document_id);
CREATE INDEX IF NOT EXISTS idx_extracted_fields_document_id ON extracted_fields(document_id);
CREATE INDEX IF NOT EXISTS idx_risk_findings_doc_analysis ON risk_findings(document_id, analysis_id);
CREATE INDEX IF NOT EXISTS idx_property_comparisons_comp_id ON property_comparisons(comparison_id);
CREATE INDEX IF NOT EXISTS idx_reports_analysis_id ON reports(analysis_id);

-- Vector Similarity Index for Fast RAG Retrieval (Cosine Distance)
CREATE INDEX IF NOT EXISTS idx_legal_references_embedding 
ON legal_references USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- ============================================================================
-- Row Level Security (RLS) Policies
-- Ensures documents and extracted data are strictly owner-scoped
-- ============================================================================

-- Enable RLS across all sensitive tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE extracted_clauses ENABLE ROW LEVEL SECURITY;
ALTER TABLE extracted_fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE property_comparisons ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_references ENABLE ROW LEVEL SECURITY;
ALTER TABLE reference_clauses ENABLE ROW LEVEL SECURITY;
ALTER TABLE registration_checklist_items ENABLE ROW LEVEL SECURITY;

-- 1. Users Policy
CREATE POLICY "Users can only access their own user row"
    ON users FOR ALL
    USING (auth.uid() = id);

-- 2. Documents Policy
CREATE POLICY "Users can view and manage their own documents"
    ON documents FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- 3. Extracted Clauses Policy
CREATE POLICY "Users can view clauses of their own documents"
    ON extracted_clauses FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM documents 
            WHERE documents.id = extracted_clauses.document_id 
            AND documents.user_id = auth.uid()
        )
    );

-- 4. Extracted Fields Policy
CREATE POLICY "Users can view fields of their own documents"
    ON extracted_fields FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM documents 
            WHERE documents.id = extracted_fields.document_id 
            AND documents.user_id = auth.uid()
        )
    );

-- 5. Risk Findings Policy
CREATE POLICY "Users can view risk findings of their own documents"
    ON risk_findings FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM documents 
            WHERE documents.id = risk_findings.document_id 
            AND documents.user_id = auth.uid()
        )
    );

-- 6. Property Comparisons Policy
CREATE POLICY "Authenticated users can access their property comparisons"
    ON property_comparisons FOR ALL
    USING (auth.role() = 'authenticated');

-- 7. Reports Policy
CREATE POLICY "Users can view their own reports"
    ON reports FOR ALL
    USING (auth.role() = 'authenticated');

-- 8. Public Knowledge Base Policies (Read-only for authenticated & anon clients)
CREATE POLICY "Anyone can read statutory legal references"
    ON legal_references FOR SELECT
    USING (true);

CREATE POLICY "Anyone can read reference model clauses"
    ON reference_clauses FOR SELECT
    USING (true);

CREATE POLICY "Anyone can read registration checklist items"
    ON registration_checklist_items FOR SELECT
    USING (true);

-- Allow service role full administrative access
CREATE POLICY "Service role has complete access to legal_references"
    ON legal_references FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role has complete access to reference_clauses"
    ON reference_clauses FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role has complete access to registration_checklist_items"
    ON registration_checklist_items FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');
