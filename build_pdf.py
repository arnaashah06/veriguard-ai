# build_pdf.py
import os
import subprocess
import sys

DESKTOP_DIR = r"C:\Users\pc\Desktop"
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# ---------------------------------------------------------------------------
# 1. Pycache Reference Guide HTML
# ---------------------------------------------------------------------------
pycache_modules = [
    {
        "file": "audit_trail.cpython-313.pyc",
        "source": "backend/audit_trail.py",
        "size": "4,885 bytes",
        "purpose": "Tamper-Evident Chronological Event Logging & Cryptographic Sealing",
        "logic": "Records pipeline events (INGESTION, OCR, VALIDATION, FORENSICS, BIOMETRICS, CROSS_DOC, DECISION) with ISO-8601 UTC timestamps. Maintains a monotonically chained hash list and computes an immutable SHA-256 Session Seal Digest over all events and uploaded document hashes for legal admissibility under the Indian IT Act, 2000."
    },
    {
        "file": "cross_document.cpython-313.pyc",
        "source": "backend/cross_document.py",
        "size": "25,126 bytes",
        "purpose": "Multi-Document Ingestion & Cross-Reconciliation Intelligence",
        "logic": "Executes pairwise demographic reconciliation across N documents: honorific-stripped token-sorted name matching (Levenshtein/Jaro-Winkler >= 85%), multi-format DOB normalization, Section 139AA Income-tax Act statutory linkage verification (Aadhaar-PAN cross-check), and pairwise portrait-to-portrait face comparison."
    },
    {
        "file": "face_verification.cpython-313.pyc",
        "source": "backend/face_verification.py",
        "size": "19,724 bytes",
        "purpose": "128D Deep Facial Biometric Comparison & Image Quality Engine",
        "logic": "Auto-mounts virtualenv site-packages. Implements multi-stage face detection (Standard HOG + CLAHE contrast recovery fallback for laminated/dim ID cards + 4-angle rotation search). Assesses image quality via Laplacian blur variance (>=80.0) and illumination clipping. Isolates primary face using area/centrality weighting. Computes calibrated Euclidean distance mapped to similarity percentages."
    },
    {
        "file": "forensics.cpython-313.pyc",
        "source": "backend/forensics.py",
        "size": "954 bytes",
        "purpose": "Digital Image Tampering & Forgery Detection",
        "logic": "Executes Error Level Analysis (ELA) by re-compressing document scans at a fixed 90% JPEG quality level and computing pixel-wise delta matrices to highlight inconsistencies in compression rates, identifying spliced text or altered photo stamps."
    },
    {
        "file": "identity_story.cpython-313.pyc",
        "source": "backend/identity_story.py",
        "size": "12,548 bytes",
        "purpose": "Explainable AI (XAI) Natural Language Case Narrative",
        "logic": "Translates complex mathematical checksums, OCR extraction findings, and biometric distance metrics into plain English, human-readable executive narratives for verification officers, detailing exactly which checks passed, failed, and why."
    },
    {
        "file": "main.cpython-313.pyc",
        "source": "backend/main.py",
        "size": "30,147 bytes",
        "purpose": "FastAPI ASGI Application, API Routing & Pipeline Dispatcher",
        "logic": "Exposes /verify and /verify-multiple endpoints. Employs duck-typing normalizers for upload payloads, enforces defensive guards (10MB size limit, filetype verification, PIL image integrity), orchestrates parallel extraction and validation, and guarantees zero data retention via ephemeral temp file scrubbing in finally blocks."
    },
    {
        "file": "ocr.cpython-313.pyc",
        "source": "backend/ocr.py",
        "size": "7,396 bytes",
        "purpose": "Backward-Compatible Legacy OCR Routing Interface",
        "logic": "Serves as an abstraction layer for earlier API integrations, redirecting raw image inputs into Tesseract preprocessing pipelines."
    },
    {
        "file": "ocr_tesseract.cpython-313.pyc",
        "source": "backend/ocr_tesseract.py",
        "size": "23,910 bytes",
        "purpose": "High-Precision Dual-Pass OCR & Regex Field Parsing",
        "logic": "Applies grayscale adaptive thresholding and runs dual-pass Tesseract OCR: Pass 1 (PSM 3 full automatic page) and Pass 2 (PSM 6 uniform text block). Applies regex extractors for 12-digit Aadhaar, 10-char PAN, 10-char Voter ID, 15-char Driving Licence, and ICAO 9303 MRZ lines."
    },
    {
        "file": "tesseract_config.cpython-313.pyc",
        "source": "backend/tesseract_config.py",
        "size": "2,547 bytes",
        "purpose": "Dynamic Windows Tesseract Binary Path Discovery",
        "logic": "Scans standard Windows installation directories ('C:\\Program Files\\Tesseract-OCR\\tesseract.exe') and sets pytesseract.tesseract_cmd dynamically to prevent path misconfigurations across teammate environments."
    },
    {
        "file": "tesseract_setup.cpython-313.pyc",
        "source": "backend/tesseract_setup.py",
        "size": "3,693 bytes",
        "purpose": "Environment Health Diagnostic & OCR Verification Tool",
        "logic": "Checks for executable permissions, runs 'tesseract --version', and outputs diagnostic troubleshooting guides if Tesseract is uninstalled or unmapped on PATH."
    },
    {
        "file": "test.cpython-313.pyc",
        "source": "backend/test.py",
        "size": "407 bytes",
        "purpose": "Quick Developer Scratchpad Diagnostic",
        "logic": "Performs minimal smoke tests verifying basic Python interpreter execution and local library import resolution."
    },
    {
        "file": "test_face.cpython-313.pyc",
        "source": "backend/test_face.py",
        "size": "1,284 bytes",
        "purpose": "Standalone Biometric Face Verification Test Harness",
        "logic": "Tests FaceVerifier instantiation, mock portrait handling, missing file edge cases, and distance-to-score calculation mechanics."
    },
    {
        "file": "test_forensics.cpython-313.pyc",
        "source": "backend/test_forensics.py",
        "size": "813 bytes",
        "purpose": "Standalone Image Forensics Test Harness",
        "logic": "Validates ELA difference matrix calculation and tampering score thresholds on controlled sample images."
    },
    {
        "file": "test_full_pipeline.cpython-313.pyc",
        "source": "backend/test_full_pipeline.py",
        "size": "20,244 bytes",
        "purpose": "13-Scenario End-to-End Automated Pipeline Integration Suite",
        "logic": "Automates complete end-to-end flow: MRZ parsing, Aadhaar/PAN field extraction, face match/rejection, FastAPI test client requests, and verifies zero files remain in temp/ after request completion."
    },
    {
        "file": "test_opencv_face.cpython-313.pyc",
        "source": "backend/test_opencv_face.py",
        "size": "2,268 bytes",
        "purpose": "OpenCV Vision Fallback Test Harness",
        "logic": "Exercises OpenCV matrix transformations, color space conversions (cv2.COLOR_RGB2GRAY), CLAHE equalization, and Laplacian variance calculations."
    },
    {
        "file": "validators.cpython-313.pyc",
        "source": "backend/validators.py",
        "size": "39,817 bytes",
        "purpose": "Mathematical & Statutory Indian Document Verification Rules",
        "logic": "Implements Verhoeff Dihedral Group D5 non-commutative check digits for Aadhaar (+35 penalty if invalid). Validates PAN 4th char entity and 5th char surname initial (+20 penalty if mismatched). Validates 37 Indian State RTO codes for DLs. Validates ICAO 9303 TD3 44-char MRZ cyclic (7,3,1) check digits for Passports. Recognizes lifetime statutory validity for Aadhaar, PAN, and Voter IDs."
    },
    {
        "file": "why_flagged.cpython-313.pyc",
        "source": "backend/why_flagged.py",
        "size": "11,914 bytes",
        "purpose": "4-Domain Risk Decomposition & 3-Tier Officer Priority Queue",
        "logic": "Decomposes total risk score (0-100) into 4 distinct domains: Forensics, Biometrics, Cross-Document Consistency, and Compliance. Assigns cases to Tier 1 (Immediate Escalation, >=70), Tier 2 (Standard Review, 30-69), or Tier 3 (Fast-Track Clearance, <30) with actionable next steps."
    }
]

html_cards = ""
html_table_rows = ""

for i, m in enumerate(pycache_modules, 1):
    html_cards += f"""
    <div class="card">
        <div class="card-header">
            <span class="badge-num">#{i}</span>
            <span class="file-name">{m['file']}</span>
            <span class="badge-ext">.pyc</span>
            <span class="badge-size">{m['size']}</span>
        </div>
        <div class="card-body">
            <p><strong>Source Module:</strong> <code>{m['source']}</code></p>
            <p><strong>Purpose:</strong> {m['purpose']}</p>
            <p><strong>Underlying Logic:</strong> {m['logic']}</p>
        </div>
    </div>
    """
    html_table_rows += f"""
    <tr>
        <td style="text-align:center; font-weight:bold;">{i}</td>
        <td><code>{m['file']}</code></td>
        <td>.pyc</td>
        <td><strong>{m['purpose']}</strong></td>
        <td>{m['logic'][:120]}...</td>
    </tr>
    """

full_pycache_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>VeriGuard AI - Backend Pycache Technical Reference</title>
    <style>
        @page {{
            size: A4;
            margin: 18mm 16mm 18mm 16mm;
            @bottom-right {{
                content: counter(page);
            }}
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            color: #1e293b;
            line-height: 1.5;
            font-size: 13px;
            background: #ffffff;
            margin: 0;
            padding: 0;
        }}
        .header {{
            border-bottom: 3px solid #0284c7;
            padding-bottom: 12px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0 0 6px 0;
            color: #0f172a;
            font-size: 24px;
            letter-spacing: -0.5px;
        }}
        .header .subtitle {{
            color: #475569;
            font-size: 14px;
            margin: 0;
        }}
        .meta-box {{
            background: #f1f5f9;
            border-left: 4px solid #0284c7;
            padding: 10px 14px;
            margin-bottom: 20px;
            border-radius: 4px;
            font-size: 12px;
        }}
        .meta-box strong {{
            color: #0f172a;
        }}
        .card {{
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            margin-bottom: 12px;
            page-break-inside: avoid;
            background: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .card-header {{
            background: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
            padding: 8px 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .badge-num {{
            background: #0284c7;
            color: #ffffff;
            padding: 2px 7px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 700;
        }}
        .file-name {{
            font-family: "JetBrains Mono", Consolas, monospace;
            font-weight: 700;
            color: #0f172a;
            font-size: 13px;
        }}
        .badge-ext {{
            background: #e0f2fe;
            color: #0369a1;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            font-family: monospace;
        }}
        .badge-size {{
            margin-left: auto;
            color: #64748b;
            font-size: 11px;
        }}
        .card-body {{
            padding: 10px 12px;
        }}
        .card-body p {{
            margin: 4px 0;
        }}
        code {{
            font-family: Consolas, monospace;
            background: #f1f5f9;
            padding: 1px 5px;
            border-radius: 3px;
            font-size: 12px;
            color: #be185d;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 11px;
            page-break-inside: avoid;
        }}
        th, td {{
            border: 1px solid #cbd5e1;
            padding: 6px 8px;
            text-align: left;
        }}
        th {{
            background: #f1f5f9;
            color: #0f172a;
            font-weight: 700;
        }}
        tr:nth-child(even) {{
            background: #f8fafc;
        }}
        .footer {{
            margin-top: 30px;
            border-top: 1px solid #cbd5e1;
            padding-top: 10px;
            text-align: center;
            font-size: 11px;
            color: #64748b;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>VeriGuard AI — Backend Pycache Technical Reference</h1>
        <p class="subtitle">Comprehensive Analysis of all 17 Compiled Python Bytecode Modules (<code>backend/__pycache__/*.pyc</code>)</p>
    </div>

    <div class="meta-box">
        <strong>What is <code>__pycache__</code> and <code>.pyc</code>?</strong><br>
        When Python imports a module, it compiles the human-readable source code (<code>.py</code>) into intermediate bytecode instructions (<code>.pyc</code>) tailored to the specific Python interpreter version (e.g. CPython 3.13). These cached files eliminate parsing overhead on subsequent runs, speeding up server boot time and request throughput significantly.
    </div>

    <h2>Catalog of All 17 Cached Backend Modules</h2>
    {html_cards}

    <div style="page-break-before: always;"></div>
    <h2>Quick Reference Matrix</h2>
    <table>
        <thead>
            <tr>
                <th style="width: 5%;">#</th>
                <th style="width: 28%;">File Name</th>
                <th style="width: 8%;">Ext</th>
                <th style="width: 25%;">Purpose</th>
                <th style="width: 34%;">Core Algorithmic Logic</th>
            </tr>
        </thead>
        <tbody>
            {html_table_rows}
        </tbody>
    </table>

    <div class="footer">
        VeriGuard AI &copy; 2026 | Real-Time Identity Fraud Detection & Cross-Document Reconciliation Engine
    </div>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Write HTML to temporary file and convert to PDF via Edge
# ---------------------------------------------------------------------------
html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pycache_guide.html")
pdf_dest = os.path.join(DESKTOP_DIR, "VeriGuard_AI_Backend_Pycache_Guide.pdf")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(full_pycache_html)

print(f"[*] Generated HTML: {html_path}")
print(f"[*] Converting to PDF: {pdf_dest}")

edge_cmd = [
    EDGE_EXE,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_dest}",
    html_path
]

res = subprocess.run(edge_cmd, capture_output=True, text=True)
if res.returncode == 0 and os.path.isfile(pdf_dest):
    print(f"[OK] Successfully created: {pdf_dest} ({os.path.getsize(pdf_dest)} bytes)")
else:
    print(f"[!] Error creating PDF: {res.stderr}")
