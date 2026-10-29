# Nilaayam AI (நிலாயம்)
### Intelligent Land, Tenancy, and Property Document Intelligence for Tamil Nadu

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Database: Supabase](https://img.shields.io/badge/Database-Supabase%20%7C%20pgvector-3ecf8e.svg)](https://supabase.com/)
[![LLM: Google Gemini](https://img.shields.io/badge/LLM-Gemini%201.5%20Flash-orange.svg)](https://ai.google.dev/)
[![OCR: Tesseract](https://img.shields.io/badge/OCR-Tesseract%20(tam%2Beng)-lightgrey.svg)](https://github.com/tesseract-ocr/tesseract)

---

## 1. Project Overview

### The Problem
In Tamil Nadu and across India, property transactions and tenancy agreements present significant hurdles for citizens, tenants, and homebuyers:
- **Linguistic and Terminological Complexity**: Real estate deeds and rental agreements are written in archaic legal English, colloquial Tamil, or classical revenue Tamil (e.g., *நன்செய்*, *புன்செய்*, *வில்லங்கம்*, *கிரையப் பத்திரம்*, *பட்டா*).
- **Asymmetric Knowledge & Unfair Clauses**: Tenants frequently sign agreements containing severe clauses—such as unilateral, uncapped rent escalations, arbitrary forfeiture of security deposits, or zero-notice eviction clauses that violate the **Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act (TNRRRLT Act, 2017)**.
- **Title and Boundary Discrepancies**: Property buyers encounter mismatches between Revenue Department records (**Patta / Chitta**), Sub-Registrar Office encumbrance records (**TNREGINET EC**), and registered **Sale Deeds** (e.g., conflicting survey sub-division numbers, missing boundary extents, undisclosed bank mortgages).
- **High Legal Consultation Costs**: Everyday citizens often cannot afford full advocate review for basic leases, leaving them vulnerable to litigation, fraud, or loss of life savings.

### The Solution: Nilaayam AI
**Nilaayam AI (நிலாயம்)** is an automated, AI-driven legal document intelligence platform tailored specifically to the statutory and administrative reality of Tamil Nadu. It provides:
1. **Automated Clause Risk Mapping**: Color-coded risk assessment (Red / Yellow / Green / Grey) of tenancy agreements against statutory benchmarks.
2. **Cross-Document Entity Alignment**: Three-way reconciliation across **Patta**, **Encumbrance Certificate (EC)**, and **Sale Deed** to detect survey number conflicts, extent discrepancies, and undisclosed mortgages.
3. **Bilingual Explanations & Actionable Questions**: Generates plain-language English and natural Tamil explanations alongside concrete clarification questions for counterparties.
4. **Statutory Checklists & Printable Reports**: Official Sub-Registrar Office (TNREGINET / TN Tenancy) registration checklists and print-ready formal PDF/HTML reports.

---

## 2. Architecture Diagram

```
+----------------------------------------------------------------------------------------------------+
|                                         NILAAYAM AI SYSTEM ARCHITECTURE                            |
+----------------------------------------------------------------------------------------------------+

       +---------------------------+                     +---------------------------+
       |   Client / Web Frontend   | <=================> |     FastAPI REST API      |
       |  (Tailwind + Jinja2 / UI) |   HTTP / Multipart  |  (Python Backend Engine)  |
       +---------------------------+                     +-------------+-------------+
                                                                       |
           +-----------------------------------------------------------+------------------------+
           |                                                           |                        |
           v                                                           v                        v
+---------------------+                                     +--------------------+   +--------------------+
|  Document Ingestion |                                     | Bilingual OCR Engine|   |  RAG / Vector DB   |
|  & Hash Validation  |                                     | (Tesseract Engine) |   | (Supabase pgvector)|
+----------+----------+                                     +----------+---------+   +----------+---------+
           | SHA-256                                                   |                        |
           | Deduplication                                             | tam + eng Preprocess   | 768-dim Embeddings
           v                                                           v                        v
+---------------------+                                     +--------------------+   +--------------------+
|  Supabase Storage   |                                     | Clause Parser &    |   | Statutory Knowledge|
| (Encrypted Buckets) |                                     | NER Normalization  |   | Base (TN Statutes) |
+---------------------+                                     +----------+---------+   +----------+---------+
                                                                       |                        |
                                                                       +------------+-----------+
                                                                                    |
                                                                                    v
                                                                    +-------------------------------+
                                                                    |     Gemini 1.5 LLM Engine     |
                                                                    |  - Clause Risk Classification |
                                                                    |  - 3-Way Cross-Doc Matching   |
                                                                    |  - Bilingual Explanation Gen  |
                                                                    +---------------+---------------+
                                                                                    |
                                            +---------------------------------------+---------------------------------------+
                                            |                                                                               |
                                            v                                                                               v
                             +-------------------------------+                                               +-------------------------------+
                             |    Relational DB / RLS        |                                               |    Report Generation Engine   |
                             |  - users / documents          |                                               |  - HTML / Print Template      |
                             |  - risk_findings              | ============================================> |  - Color-Coded Risk Badges    |
                             |  - property_comparisons       |                                               |  - Tamil Noto Typography      |
                             +-------------------------------+                                               +-------------------------------+
```

---

## 3. AI/ML Components

| Component | Technology | Role & Functionality |
| :--- | :--- | :--- |
| **Document Parser** | `pypdf`, `pdfplumber`, `PyMuPDF` | Native digital text extraction, table boundary detection, and metadata extraction. |
| **Bilingual OCR** | `pytesseract` + OpenCV Preprocessing | Optical Character Recognition for scanned photocopies, stamp papers, and bilingual Tamil/English deeds. |
| **LLM Engine** | Google Gemini (`gemini-1.5-flash`) | Contextual reasoning, legal nuance extraction, clause semantic classification, and natural language synthesis. |
| **Vector Embeddings** | `models/text-embedding-004` (768-dim) | Dense vector representations for legal sections, judicial interpretations, and statutory clauses. |
| **Vector Database** | Supabase `pgvector` with `ivfflat` | Approximate nearest neighbor (ANN) cosine similarity search for sub-50ms RAG retrieval. |
| **Clause Classifier** | Multi-class Prompt Taxonomy | Categorizes clauses into Rent Escalation, Security Deposit, Maintenance, Notice, Force Majeure, etc. |
| **Risk Analyzer** | Rule-Guided Verification | Evaluates clause legality against mandatory legislative benchmarks (e.g., Section 4, 13, 21 of TNRRRLT Act). |

---

## 4. Supported Document Types

1. **Residential & Commercial Rental Agreements (*வாடகை ஒப்பந்தம்*)**
   - Registered and unregistered tenancy agreements (11-month and multi-year leases).
   - Identification of unilateral rent escalations, arbitrary deposit retention, maintenance duties, lock-in clauses, and eviction notices.
2. **Sale Deeds & Conveyance Instruments (*கிரையப் பத்திரம்*)**
   - Property schedule details, vendor/vendee representations, consideration amounts, survey sub-divisions, encumbrance indemnities, and boundary coordinates.
3. **Revenue Patta & Chitta (*பட்டா / சிட்டா*)**
   - District, Taluk, Village, Patta number, Survey number (*சர்வே எண்*), Sub-division, land category (*நன்செய் / புன்செய் / நத்தம்*), and registered owner name (*பட்டாதாரர் பெயர்*).
4. **Encumbrance Certificates (EC / *வில்லங்கம்*)**
   - Records issued by the Tamil Nadu Registration Department (TNREGINET). Tracking 15 to 30+ years of transactions, registered mortgages, gift deeds, discharge receipts, and court attachments.

---

## 5. Tamil OCR Approach

Tamil document processing requires specialized handling due to compound graphemes, varying font styles, and poor-quality photocopies common in Sub-Registrar Offices:

```
[Raw Scanned Image / PDF Page]
              |
              v
[OpenCV Preprocessing Pipeline]
  1. Grayscale Conversion
  2. Gaussian Blur (Noise suppression)
  3. Otsu / Adaptive Thresholding (Binarization)
  4. Deskewing via Hough Line Transform
  5. DPI Normalization (Scaled to 300 DPI)
              |
              v
[Tesseract OCR Engine]
  - Parameter: -l tam+eng --oem 1 --psm 3
  - Dual language character whitelist
              |
              v
[Post-Processing & Tamil Normalization]
  - Unicode Normalization (NFC/NFD canonical reconciliation)
  - Tamil Legal Regex (Matches patterns like "சர்வே எண்", "கதவு எண்", "விஸ்தீர்ணம்")
  - Confidence scoring per text block
```

---

## 6. RAG Implementation

### Chunking Strategy
- **Granular Statutory Chunking**: Legal statutes cannot be arbitrarily cut by character counts without severing preconditions from their consequences. Sections are chunked by structural boundaries:
  - Header: Act Name, Section Number, Sub-section.
  - Body: Substantive rule, exceptions, and statutory penalties.
  - Average chunk size: 250–450 tokens with 50-token contextual overlaps.

### pgvector Similarity Search
Embeddings generated via Gemini's `text-embedding-004` (768 dimensions) are indexed in Supabase:
```sql
SELECT title, section, chunk_text, 1 - (embedding <=> query_embedding) AS similarity
FROM legal_references
WHERE 1 - (embedding <=> query_embedding) > 0.72
ORDER BY similarity DESC
LIMIT 4;
```

### Source Tracking & Hallucination Prevention
1. **Strict Context Grounding**: The LLM system prompt is explicitly barred from generating legal claims without linking an authoritative reference ID from the retrieved database chunks.
2. **Extracted Clause Citation**: Every flagged risk must directly quote the input document’s exact clause text (`clause_text`) and character coordinates (`char_start`, `char_end`). If a clause is missing, it is explicitly classified with `is_missing_clause: true`.

---

## 7. Legal Source Strategy

### Categorization of Legal Authorities
- **Binding Statutory Requirements (`is_binding: true`)**: Acts passed by Parliament or the Tamil Nadu Legislative Assembly (e.g., TNRRRLT Act 2017, Registration Act 1908). Failure to comply can render an agreement void or invite statutory penalties.
- **Illustrative / Guidance References (`is_binding: false`)**: Judicial precedents, High Court rulings, model agreement templates from the Housing & Urban Development Department, and advisory guidelines.

### Verification Dates & Disclaimer
- Every legal entry retains a `last_verified` date. In an active legal system with statutory amendments, stale regulations are flagged for scheduled re-indexing.
- **Prominent Red-Border Disclaimer**: Reports feature an immutable disclaimer explicitly clarifying that Nilaayam AI is an assistive technology and **does not constitute legal advocacy or representation under the Advocates Act, 1961**.

---

## 8. Security & Privacy

1. **Row Level Security (RLS)**: Enabled across all database tables. Documents and analysis records are scoped to `auth.uid() = user_id`. No user can access or view another user's documents.
2. **Encrypted Storage & Signed URLs**: Files are stored in Supabase private buckets (`nilaayam-documents`). Direct public URLs are disabled; documents can only be accessed via short-lived cryptographic signed URLs (15-minute expiration).
3. **SHA-256 File Hash Validation**: Documents are hashed immediately upon upload. Prevents redundant reprocessing and guards against file corruption or tampering.
4. **Data Minimization**: Extracted personally identifiable information (PII) is processed in-memory and can be sanitized upon report generation.

---

## 9. Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Tesseract OCR with Tamil language pack (`tesseract-ocr`, `tesseract-ocr-tam`)
- Supabase account (Free tier or self-hosted)
- Google Gemini API key

### Step 1: Clone Repository & Create Virtual Environment
```bash
git clone https://github.com/nilaayam-ai/nilaayam-ai.git
cd nilaayam-ai

# Create virtual environment
python -m venv venv

# Activate on Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Activate on Linux/macOS:
source venv/bin/activate
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```
*(If `requirements.txt` is being initialized, install core packages: `pip install fastapi uvicorn supabase python-dotenv google-generativeai pytesseract pillow jinja2 pydantic`)*

### Step 3: Install Tesseract with Tamil Language Pack
- **Windows**:
  1. Download the installer from UB-Mannheim: https://github.com/UB-Mannheim/tesseract/wiki
  2. In the installer, check the box for **"Additional script data" -> "Tamil"** and **"Additional language data" -> "Tamil"**.
  3. Ensure `C:\Program Files\Tesseract-OCR` is added to your system `PATH`.
- **Ubuntu/Debian**:
  ```bash
  sudo apt-get update
  sudo apt-get install -y tesseract-ocr tesseract-ocr-tam
  ```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env` and fill in your keys:
```bash
cp .env.example .env
```
Fill in:
```ini
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...
GEMINI_API_KEY=AIzaSy...
```

### Step 5: Execute Database Migrations
1. Open your Supabase Dashboard -> **SQL Editor**.
2. Open `scripts/setup_db.sql`.
3. Paste and run the entire SQL script. This enables `pgvector`, initializes all 10 tables, creates performance indexes, and enables RLS policies.

### Step 6: Run Seeding Script
Populate your database with the demo dataset (or run in fallback in-memory mode):
```bash
python scripts/seed.py
```

### Step 7: Run Backend API
```bash
uvicorn main:app --reload --port 8000
```
API Documentation will be accessible at: `http://localhost:8000/docs`

---

## 10. Frontend Setup

The Nilaayam AI web dashboard is designed for ease of use by both English and Tamil-speaking users.

1. **Standalone Template Rendering**:
   The Jinja2 report template (`reports/templates/report.html`) can be compiled directly via the backend or previewed with demo payloads.
2. **Building the Frontend**:
   If utilizing the companion React/Next.js interface:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Access the dashboard at `http://localhost:3000`.

---

## 11. Deployment Instructions

### Production Backend (Docker / Render / AWS)
A production-ready `Dockerfile`:
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-tam libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Supabase Production Setup
- Ensure `pgvector` index lists parameter matches database size:
  `WITH (lists = 100)` for < 100,000 vectors; adjust higher as statutory chunking grows.
- Enable automated backups and point storage buckets to secure regions (e.g., AWS Mumbai `ap-south-1`).

---

## 12. Known Limitations

1. **Handwritten Deeds**: While modern computerized Patta and registered typed deeds achieve >95% OCR accuracy, 50-year-old cursive handwritten Tamil deeds (*பழைய கைப்பட எழுதப்பட்ட பத்திரங்கள்*) may exhibit lower OCR fidelity and require manual transcription fallback.
2. **Complex Title Lineage (Court Litigations)**: Nilaayam AI identifies encumbrance entries on EC records; however, pending un-registered civil suits (*lis pendens*) in local sub-courts without entry in the Sub-Registrar’s register cannot be automatically detected without court e-filing integrations.
3. **Regulatory Evolution**: Amendments issued via Government Orders (G.O.s) require periodic synchronization with the knowledge base.

---

## 13. Demo Script (Hackathon Presentation)

Follow this 3-minute presentation script for pitching Nilaayam AI to judges:

| Time | Stage | Action & Talking Point |
| :--- | :--- | :--- |
| **0:00 - 0:30** | **The Hook** | *"Judges, over 80% of urban residents in Tamil Nadu rent homes or buy plots using agreements they cannot understand. Landlords insert unlawful clauses, and buyers discover survey number mismatches only after paying lakhs."* |
| **0:30 - 1:15** | **Problem Demo** | Upload `T-Nagar_Residential_Lease_Problematic.pdf`. Show how traditional review misses subtle terms. Nilaayam AI extracts clauses in seconds. |
| **1:15 - 2:00** | **Risk Map & Tamil AI** | Highlight the **Clause Risk Map**: 3 Red Cards (Uncapped rent escalation, 24-hr verbal notice, ambiguous deposit refund). Show the toggle to **Tamil explanation**: *"உரிமையாளர் தன்னிச்சையாக வாடகையை உயர்த்தலாம் என்ற விதி..."* |
| **2:00 - 2:30** | **3-Way Property Match** | Open the **Property Field Comparison Table**: Demo `Tambaram_Discrepancy_Docket.pdf`. Point out the instantaneous **Red Mismatch Badge**: Patta says `88/2A` (1800 sq.ft), but Sale Deed says `88/2B` (1950 sq.ft) with an undisclosed Canara Bank lien! |
| **2:30 - 3:00** | **Resolution & Print** | Click **"Download Verified Report"**. Show the print-ready executive PDF with registration checklist, statutory references, and the formal disclaimer. |

---

## 14. Work Split

| Team Member | Core Focus | Key Deliverables |
| :--- | :--- | :--- |
| **Person A** | **AI / ML & Intelligence Pipeline** | - Tesseract bilingual (tam+eng) OCR pipeline with OpenCV adaptive binarization.<br>- Gemini prompt engineering for legal taxonomy & clause classification.<br>- RAG embedding generation (`text-embedding-004`) and pgvector similarity search.<br>- Tamil legal glossary normalization and translation quality assurance. |
| **Person B** | **Backend, Database & UI/UX** | - Supabase relational schema with pgvector and Row Level Security (RLS).<br>- FastAPI asynchronous REST endpoints and file upload validation.<br>- Jinja2 printable report engine with deep navy/forest green theme and Noto Sans Tamil typography.<br>- Database migration scripts, seeding fixtures, and demo scenario scripts. |

---

<div align="center">
  <sub>Built with ❤️ for the citizens, tenants, and property owners of Tamil Nadu.</sub><br>
  <sub><strong>Nilaayam AI (நிலாயம்)</strong> • Empowering transparency in Indian real estate.</sub>
</div>
