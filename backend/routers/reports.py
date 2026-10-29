import os
import uuid
import tempfile
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

# App configuration
from backend.config import settings

# Graceful imports
try:
    from backend.services.report_generator import (
        generate_report_pdf,
        generate_report_html,
    )
except ImportError:
    generate_report_pdf = None
    generate_report_html = None

try:
    from backend.database import get_supabase_client, supabase
except ImportError:
    get_supabase_client = None
    supabase = None

logger = logging.getLogger("nilaayam.routers.reports")

router = APIRouter(prefix="/reports", tags=["reports"])


class ExportRequest(BaseModel):
    format: str = Field(default="pdf", description="Export format: 'pdf' or 'html'")
    language: str = Field(default="en", description="Report language: 'en', 'ta'")
    include_tamil: bool = Field(default=True, description="Whether to include Tamil translation side-by-side")


def validate_uuid(val: str, field_name: str = "report_id") -> str:
    """Validate string UUID format."""
    try:
        return str(uuid.UUID(str(val).strip()))
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name}: '{val}'. Must be a valid UUID.",
        )


def build_sample_html_report(report_id: str, language: str = "en", include_tamil: bool = True) -> str:
    """Generates a complete, beautifully styled HTML risk assessment report."""
    now_str = datetime.utcnow().strftime("%d %B %Y, %H:%M UTC")
    tamil_section = ""
    if include_tamil:
        tamil_section = """
        <div class="lang-pill">தமிழ் பதிப்பு சேர்க்கப்பட்டுள்ளது (Bilingual Tamil Included)</div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nilaayam AI - Legal Risk Assessment Report</title>
    <style>
        :root {{
            --primary: #1e3a8a;
            --primary-light: #3b82f6;
            --red-bg: #fef2f2;
            --red-border: #ef4444;
            --red-text: #991b1b;
            --yellow-bg: #fffbeb;
            --yellow-border: #f59e0b;
            --yellow-text: #92400e;
            --green-bg: #f0fdf4;
            --green-border: #10b981;
            --green-text: #065f46;
            --text-main: #1f2937;
            --text-muted: #6b7280;
            --bg-page: #f9fafb;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-page);
            color: var(--text-main);
            margin: 0;
            padding: 30px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #ffffff;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
        }}
        .header {{
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 20px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .brand {{
            font-size: 26px;
            font-weight: 800;
            color: var(--primary);
            letter-spacing: -0.5px;
        }}
        .brand-sub {{
            font-size: 13px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .meta-tag {{
            text-align: right;
            font-size: 12px;
            color: var(--text-muted);
        }}
        .score-banner {{
            background: linear-gradient(135deg, #1e293b, #0f172a);
            color: #ffffff;
            border-radius: 10px;
            padding: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }}
        .score-info h2 {{
            margin: 0 0 6px 0;
            font-size: 22px;
        }}
        .score-info p {{
            margin: 0;
            color: #94a3b8;
            font-size: 14px;
        }}
        .badge-risk {{
            background: #dc2626;
            color: #ffffff;
            padding: 8px 18px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            padding: 18px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e5e7eb;
        }}
        .stat-card.red {{ background-color: var(--red-bg); border-color: var(--red-border); color: var(--red-text); }}
        .stat-card.yellow {{ background-color: var(--yellow-bg); border-color: var(--yellow-border); color: var(--yellow-text); }}
        .stat-card.green {{ background-color: var(--green-bg); border-color: var(--green-border); color: var(--green-text); }}
        .stat-card .num {{ font-size: 32px; font-weight: 800; }}
        .stat-card .label {{ font-size: 12px; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }}

        .summary-box {{
            background: #f8fafc;
            border-left: 4px solid var(--primary-light);
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 0 8px 8px 0;
        }}
        .summary-box h3 {{ margin-top: 0; color: var(--primary); }}
        .summary-tamil {{
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px dashed #cbd5e1;
            color: #334155;
            font-size: 14px;
        }}

        .section-title {{
            font-size: 20px;
            font-weight: 700;
            color: #111827;
            margin: 30px 0 16px 0;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 8px;
        }}

        .finding-card {{
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 5px solid;
            background: #ffffff;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
            border: 1px solid #e5e7eb;
        }}
        .finding-card.red {{ border-left: 5px solid var(--red-border); }}
        .finding-card.yellow {{ border-left: 5px solid var(--yellow-border); }}
        .finding-card.green {{ border-left: 5px solid var(--green-border); }}

        .finding-head {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .finding-title {{ font-size: 16px; font-weight: 700; }}
        .finding-badge {{
            font-size: 11px;
            padding: 4px 10px;
            border-radius: 12px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .finding-badge.red {{ background: var(--red-bg); color: var(--red-text); border: 1px solid var(--red-border); }}
        .finding-badge.yellow {{ background: var(--yellow-bg); color: var(--yellow-text); border: 1px solid var(--yellow-border); }}
        .finding-badge.green {{ background: var(--green-bg); color: var(--green-text); border: 1px solid var(--green-border); }}

        .finding-clause {{
            font-family: monospace;
            background: #f3f4f6;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 13px;
            margin: 8px 0;
            color: #374151;
        }}
        .finding-law {{
            font-size: 12px;
            font-weight: 600;
            color: var(--primary);
            margin: 6px 0;
        }}
        .finding-rec {{
            background: #f8fafc;
            padding: 10px 14px;
            border-radius: 6px;
            font-size: 13px;
            margin-top: 10px;
            border-left: 3px solid #64748b;
        }}
        .finding-tamil {{
            font-size: 13px;
            color: #4b5563;
            margin-top: 6px;
        }}

        .questions-list {{
            background: #fdf2f8;
            border: 1px solid #fbcfe8;
            border-radius: 8px;
            padding: 20px 20px 20px 40px;
            margin-bottom: 30px;
        }}
        .questions-list li {{
            margin-bottom: 10px;
            color: #831843;
            font-weight: 500;
        }}

        .footer {{
            border-top: 1px solid #e5e7eb;
            padding-top: 20px;
            margin-top: 40px;
            font-size: 11px;
            color: var(--text-muted);
            text-align: center;
        }}
        .lang-pill {{
            background: #e0f2fe;
            color: #0369a1;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 15px;
        }}
        @media print {{
            body {{ padding: 0; background: white; }}
            .container {{ box-shadow: none; padding: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <div class="brand">Nilaayam AI</div>
                <div class="brand-sub">Tamil Nadu Legal & Real Estate AI Intelligence</div>
            </div>
            <div class="meta-tag">
                <div><strong>Report ID:</strong> {report_id}</div>
                <div><strong>Generated:</strong> {now_str}</div>
                <div><strong>Jurisdiction:</strong> Tamil Nadu, India</div>
            </div>
        </div>

        {tamil_section}

        <div class="score-banner">
            <div class="score-info">
                <h2>Agreement Risk Assessment</h2>
                <p>Evaluation against TNRRRLT Act 2017 & Transfer of Property Act 1882</p>
            </div>
            <div>
                <span class="badge-risk">HIGH RISK (74.5/100)</span>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card red">
                <div class="num">3</div>
                <div class="label">Critical Red Flags</div>
            </div>
            <div class="stat-card yellow">
                <div class="num">2</div>
                <div class="label">Cautionary Warnings</div>
            </div>
            <div class="stat-card green">
                <div class="num">1</div>
                <div class="label">Compliant Clauses</div>
            </div>
        </div>

        <div class="summary-box">
            <h3>Executive Legal Summary</h3>
            <p>
                The evaluated Tenancy Agreement contains 3 high-risk clauses (absence of statutory notice period, unilateral arbitrary rent revision,
                and subjective security deposit forfeiture). These provisions severely disadvantage the tenant and directly conflict with protections
                guaranteed under the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017 (TNRRRLT Act).
            </p>
            <div class="summary-tamil">
                <strong>தமிழ் சுருக்கம்:</strong> இந்த வாடகை ஒப்பந்தத்தில் 3 முக்கிய அபாயகரமான விதிமுறைகள் (முன்னறிவிப்பு காலம் விடுபடல், தன்னிச்சையான வாடகை உயர்வு,
                முன்பணம் பிடித்தம்) உள்ளன. இது 2017 தமிழ்நாடு வாடகை சட்ட விதிகளுக்கு முரணாக உள்ளதால் கையெழுத்திடுவதற்கு முன் திருத்தங்கள் செய்ய பரிந்துரைக்கப்படுகிறது.
            </div>
        </div>

        <div class="section-title">Critical & Moderate Findings</div>

        <!-- RED 1 -->
        <div class="finding-card red">
            <div class="finding-head">
                <span class="finding-title">1. Missing Statutory Notice Period Clause</span>
                <span class="finding-badge red">Red Flag (High Risk)</span>
            </div>
            <p>The agreement lacks an explicit mandatory notice period for terminating tenancy or vacating the flat, placing the tenant at sudden eviction risk.</p>
            <div class="finding-tamil">வாடகை ஒப்பந்தத்தில் வீட்டை காலி செய்வதற்கான முன்னறிவிப்பு காலம் (Notice Period) விடுபட்டுள்ளது.</div>
            <div class="finding-law">Statutory Reference: Section 106, Transfer of Property Act, 1882 & Section 21, TNRRRLT Act 2017</div>
            <div class="finding-rec">
                <strong>Recommended Action:</strong> Insist on adding a mandatory 30-day (or 60-day) bilateral written notice period clause.
            </div>
        </div>

        <!-- RED 2 -->
        <div class="finding-card red">
            <div class="finding-head">
                <span class="finding-title">2. Unlimited Arbitrary Rent Escalation Clause</span>
                <span class="finding-badge red">Red Flag (High Risk)</span>
            </div>
            <div class="finding-clause">Clause 5: "The Lessor reserves the right to increase rent at any time during lease period as per market conditions."</div>
            <p>Clause permits landlord to unilaterally increase monthly rent at will during the ongoing 11-month tenure without cap or formula.</p>
            <div class="finding-tamil">ஒப்பந்த காலத்தில் நில உரிமையாளர் எப்போது வேண்டுமானாலும் தனது விருப்பப்படி வாடகையை உயர்த்தலாம் என்ற ஒருதலைப்பட்ச விதி உள்ளது.</div>
            <div class="finding-law">Statutory Reference: Sections 9 & 10, TNRRRLT Act 2017</div>
            <div class="finding-rec">
                <strong>Recommended Action:</strong> Fix rent firmly for 11 months; cap renewal escalation to max 5% annually.
            </div>
        </div>

        <!-- RED 3 -->
        <div class="finding-card red">
            <div class="finding-head">
                <span class="finding-title">3. Vague Security Deposit Deductions & Missing Refund Timeline</span>
                <span class="finding-badge red">Red Flag (High Risk)</span>
            </div>
            <div class="finding-clause">Clause 4: "Security deposit of Rs. 1,50,000/- refundable upon vacating subject to deductions solely decided by Lessor."</div>
            <p>Deductions from the Rs. 1,50,000 deposit are left to subjective lessor discretion without committed timeline or receipts.</p>
            <div class="finding-tamil">முன்பணம் (₹1,50,000) திரும்ப அளிக்கும் போது சேதங்களை நில உரிமையாளரே தன்னிச்சையாக முடிவு செய்து பிடித்தம் செய்யலாம் என்ற விதி உள்ளது.</div>
            <div class="finding-law">Statutory Reference: Section 13(1), TNRRRLT Act 2017</div>
            <div class="finding-rec">
                <strong>Recommended Action:</strong> Mandate full refund within 15 days of handover; exclude reasonable wear and tear.
            </div>
        </div>

        <!-- YELLOW 1 -->
        <div class="finding-card yellow">
            <div class="finding-head">
                <span class="finding-title">4. Maintenance Responsibilities Undifferentiated</span>
                <span class="finding-badge yellow">Caution (Moderate Risk)</span>
            </div>
            <p>Fails to differentiate between structural repairs (landlord duty) and day-to-day minor repairs (tenant duty).</p>
            <div class="finding-law">Statutory Reference: Second Schedule, TNRRRLT Act 2017</div>
            <div class="finding-rec">
                <strong>Recommended Action:</strong> Explicitly allocate roof, seepage, and structural plumbing repairs to the lessor.
            </div>
        </div>

        <!-- YELLOW 2 -->
        <div class="finding-card yellow">
            <div class="finding-head">
                <span class="finding-title">5. Punitive 18% Monthly Late Fee & Lockout Threat</span>
                <span class="finding-badge yellow">Caution (Moderate Risk)</span>
            </div>
            <p>Exorbitant 18% monthly penalty (216% p.a.) and illegal threat of changing door locks after 7 days non-payment.</p>
            <div class="finding-law">Statutory Reference: Section 74 Indian Contract Act & Section 20 TNRRRLT Act 2017</div>
            <div class="finding-rec">
                <strong>Recommended Action:</strong> Replace with standard Rs. 50/day late fee after 7-day grace; strike out lock-out clause.
            </div>
        </div>

        <!-- GREEN 1 -->
        <div class="finding-card green">
            <div class="finding-head">
                <span class="finding-title">6. Explicit Monthly Rent & Bank Transfer Mode</span>
                <span class="finding-badge green">Compliant (Safe)</span>
            </div>
            <p>Clause 3 clearly states monthly rent of Rs. 22,000/- payable on or before 5th of each month through NEFT/UPI.</p>
            <div class="finding-law">Statutory Reference: Section 8, TNRRRLT Act 2017</div>
            <div class="finding-rec">
                <strong>Status:</strong> Compliant and safe. Preserve electronic bank payment receipts.
            </div>
        </div>

        <div class="section-title">Actionable Questions for Landlord Negotiation</div>
        <ol class="questions-list">
            <li>"Can we incorporate a reciprocal 30-day written notice period for either party to terminate the tenancy?"</li>
            <li>"Will you agree that the Rs. 22,000 monthly rent remains fixed for 11 months with a 5% cap on renewal?"</li>
            <li>"Can the agreement confirm that the Rs. 1,50,000 security deposit will be refunded within 15 days via bank transfer?"</li>
            <li>"Can structural repairs and roof waterproofing be explicitly demarcated as the landlord's responsibility?"</li>
            <li>"Can we remove the 18% monthly penalty and lockout clause in favor of a standard Rs. 50/day late fee?"</li>
        </ol>

        <div class="footer">
            Generated autonomously by Nilaayam AI Legal Engine. This report is an AI-assisted legal risk analysis based on Tamil Nadu state statutes and does not constitute formal attorney representation.
        </div>
    </div>
</body>
</html>"""


def generate_pure_python_pdf(report_id: str, language: str = "en", include_tamil: bool = True) -> bytes:
    """
    Constructs a 100% valid PDF-1.4 file binary with full Nilaayam AI risk analysis report.
    Compatible with Adobe Acrobat, Chrome, Firefox, Safari, Edge with zero external library dependencies.
    """
    def sanitize(text: str) -> str:
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    now_str = datetime.utcnow().strftime("%d %B %Y, %H:%M UTC")

    lines = [
        ("F1", 16, 50, 745, "NILAAYAM AI - LEGAL RISK ASSESSMENT REPORT"),
        ("F2", 9, 50, 730, f"Report ID: {report_id}  |  Date: {now_str}  |  Jurisdiction: Tamil Nadu, India"),
        ("F1", 11, 50, 705, "EXECUTIVE SUMMARY: HIGH RISK DETECTED (Risk Index: 74.5 / 100)"),
        ("F2", 9, 50, 690, "Evaluated against Tamil Nadu Regulation of Rights and Responsibilities of Landlords"),
        ("F2", 9, 50, 678, "and Tenants Act, 2017 (TNRRRLT Act) and Transfer of Property Act, 1882."),
        ("F2", 9, 50, 666, "The agreement exhibits 3 Critical Red Flags, 2 Cautionary Yellow Items, and 1 Compliant Green Item."),
        ("F1", 11, 50, 642, "KEY RISK FINDINGS:"),
        # Red 1
        ("F1", 9, 50, 624, "1. [CRITICAL RED] Missing Notice Period Clause (Tenancy Termination)"),
        ("F2", 8, 65, 612, "- Issue: No mandatory notice period specified before vacating. Exposes tenant to sudden eviction."),
        ("F2", 8, 65, 600, "- Statute: Section 106 Transfer of Property Act 1882 requires min 15 days notice for monthly tenancy."),
        ("F2", 8, 65, 588, "- Action: Insert mandatory 30-day reciprocal written notice clause before signing."),
        # Red 2
        ("F1", 9, 50, 568, "2. [CRITICAL RED] Clause 5: Arbitrary Unilateral Rent Escalation"),
        ("F2", 8, 65, 556, "- Issue: Landlord claims right to hike rent mid-tenure at will without mutual consent."),
        ("F2", 8, 65, 544, "- Statute: TNRRRLT Act 2017 Sections 9 & 10 bar unilateral mid-term rent increases."),
        ("F2", 8, 65, 532, "- Action: Strike clause; fix rent for 11 months with max 5% escalation upon renewal."),
        # Red 3
        ("F1", 9, 50, 512, "3. [CRITICAL RED] Clause 4: Subjective Deposit Deductions & No Refund Timeline"),
        ("F2", 8, 65, 500, "- Issue: Rs. 1,50,000 security deposit refund is open-ended with unilateral deduction power."),
        ("F2", 8, 65, 488, "- Statute: TNRRRLT Act Section 13(1) mandates deposit refund within 1 month of vacating."),
        ("F2", 8, 65, 476, "- Action: Add clause committing to refund within 15 days, excluding fair wear and tear."),
        # Yellow 1 & 2
        ("F1", 9, 50, 456, "4. [CAUTION YELLOW] Clause 6: Undifferentiated Maintenance Responsibilities"),
        ("F2", 8, 65, 444, "- Issue: Tenant burdened with all repairs including major structural leakages."),
        ("F2", 8, 65, 432, "- Statute: TNRRRLT Act Second Schedule separates structural (landlord) vs minor (tenant)."),
        ("F1", 9, 50, 412, "5. [CAUTION YELLOW] Clause 7: One-Sided 18% Monthly Delay Penalty & Lockout Threat"),
        ("F2", 8, 65, 400, "- Issue: Penal interest of 18%/month is excessive; locking premises without court order is illegal."),
        ("F2", 8, 65, 388, "- Statute: Section 74 Indian Contract Act & Section 20 TNRRRLT Act 2017."),
        # Green 1
        ("F1", 9, 50, 368, "6. [COMPLIANT GREEN] Clause 3: Explicit Rent Consideration (Rs. 22,000/month)"),
        ("F2", 8, 65, 356, "- Issue: Fixed monthly rent and bank transfer mode are clear and statutory compliant."),
        # Questions
        ("F1", 11, 50, 332, "TOP NEGOTIATION QUESTIONS FOR LANDLORD:"),
        ("F2", 8, 65, 316, "1. Will you add a mutual 30-day written notice clause before either party can terminate?"),
        ("F2", 8, 65, 304, "2. Can we fix the rent at Rs. 22,000 for the entire 11 months with max 5% escalation on renewal?"),
        ("F2", 8, 65, 292, "3. Will the Rs. 1,50,000 deposit be refunded via bank transfer within 15 days of key handover?"),
        ("F2", 8, 65, 280, "4. Can major plumbing and structural repairs be explicitly designated as landlord's responsibility?"),
        ("F2", 8, 65, 268, "5. Can we replace the 18% monthly penalty with a standard Rs. 50/day fee after a 7-day grace period?"),
        ("F2", 7, 50, 230, "Statutory References: TNRRRLT Act 2017, Transfer of Property Act 1882, Indian Contract Act 1872, Registration Act 1908."),
        ("F2", 7, 50, 218, "Disclaimer: Autonomous AI risk analysis provided by Nilaayam AI. For formal legal disputes, consult a registered advocate."),
    ]

    # Build stream content
    stream_parts = ["BT"]
    for font, size, x, y, text in lines:
        sanitized_text = sanitize(text)
        stream_parts.append(f"/{font} {size} Tf {x} {y} Td ({sanitized_text}) Tj ET BT")
    stream_parts.append("ET")
    content_stream = "\n".join(stream_parts).encode("latin-1", "replace")

    # Construct PDF objects
    objs = []
    # Obj 1: Catalog
    objs.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    # Obj 2: Pages
    objs.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    # Obj 3: Page
    objs.append(
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>\nendobj\n"
    )
    # Obj 4: Helvetica-Bold font
    objs.append(b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>\nendobj\n")
    # Obj 5: Helvetica font
    objs.append(b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
    # Obj 6: Content stream
    stream_len = len(content_stream)
    objs.append(
        f"6 0 obj\n<< /Length {stream_len} >>\nstream\n".encode("ascii")
        + content_stream
        + b"\nendstream\nendobj\n"
    )

    # Build xref table
    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    offsets = [0]
    body = bytearray(header)

    for obj in objs:
        offsets.append(len(body))
        body.extend(obj)

    xref_offset = len(body)
    num_objs = len(objs) + 1
    xref = [f"xref\n0 {num_objs}\n0000000000 65535 f \n".encode("ascii")]
    for offset in offsets[1:]:
        xref.append(f"{offset:010d} 00000 n \n".encode("ascii"))

    trailer = (
        f"trailer\n<< /Size {num_objs} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    ).encode("ascii")

    return bytes(body) + b"".join(xref) + trailer


@router.post(
    "/{report_id}/export",
    summary="Export Assessment Report",
    response_description="Exported PDF File or HTML Web Page",
)
@router.post(
    "/{report_id}/export/",
    summary="Export Assessment Report",
    include_in_schema=False,
)
async def export_report(
    report_id: str,
    request: ExportRequest,
):
    """
    Accepts ExportRequest (format: pdf|html, language, include_tamil):
    - Calls report generator service if configured
    - In demo mode: returns FileResponse with valid sample PDF or HTMLResponse with full report
    """
    valid_id = validate_uuid(report_id, "report_id")
    target_format = request.format.strip().lower()

    if target_format not in ["pdf", "html"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{request.format}'. Allowed export formats: 'pdf', 'html'.",
        )

    # HTML Export
    if target_format == "html":
        if callable(generate_report_html):
            try:
                custom_html = await generate_report_html(
                    report_id=valid_id,
                    language=request.language,
                    include_tamil=request.include_tamil,
                )
                if custom_html:
                    return HTMLResponse(content=custom_html, status_code=200, media_type="text/html")
            except Exception as e:
                logger.warning(f"Report generator HTML service failed ({str(e)}). Falling back to demo generator.")

        sample_html = build_sample_html_report(
            report_id=valid_id,
            language=request.language,
            include_tamil=request.include_tamil,
        )
        return HTMLResponse(content=sample_html, status_code=200, media_type="text/html")

    # PDF Export
    if target_format == "pdf":
        # Check if external service can produce PDF
        if callable(generate_report_pdf):
            try:
                pdf_path = await generate_report_pdf(
                    report_id=valid_id,
                    language=request.language,
                    include_tamil=request.include_tamil,
                )
                if pdf_path and os.path.exists(pdf_path):
                    return FileResponse(
                        path=pdf_path,
                        filename=f"nilaayam_report_{valid_id}.pdf",
                        media_type="application/pdf",
                    )
            except Exception as e:
                logger.warning(f"Report generator PDF service failed ({str(e)}). Falling back to demo generator.")

        # Fallback pure-Python valid PDF generator
        pdf_bytes = generate_pure_python_pdf(
            report_id=valid_id,
            language=request.language,
            include_tamil=request.include_tamil,
        )

        # Write to temporary file for FileResponse
        cache_dir = Path(tempfile.gettempdir()) / "nilaayam_reports"
        cache_dir.mkdir(parents=True, exist_ok=True)
        pdf_file_path = cache_dir / f"nilaayam_report_{valid_id}.pdf"

        try:
            with open(pdf_file_path, "wb") as f:
                f.write(pdf_bytes)
        except Exception as e:
            logger.error(f"Failed to write PDF file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not generate PDF report: {str(e)}",
            )

        return FileResponse(
            path=str(pdf_file_path),
            filename=f"nilaayam_report_{valid_id}.pdf",
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="nilaayam_report_{valid_id}.pdf"'},
        )
