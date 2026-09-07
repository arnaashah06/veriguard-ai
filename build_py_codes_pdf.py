# build_py_codes_pdf.py
import os
import subprocess

DESKTOP_DIR = r"C:\Users\pc\Desktop"
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PDF_DEST = os.path.join(DESKTOP_DIR, "VeriGuard_AI_Backend_Source_Code_Guide.pdf")

categories = [
    {
        "cat_name": "1. Core Backend Architecture & Analysis Engines",
        "desc": "The primary operational modules responsible for document ingestion, OCR, biometric comparison, cross-document reconciliation, explainability, and audit logging.",
        "files": [
            {
                "file": "main.py",
                "lines": "713 lines (28.6 KB)",
                "purpose": "Central FastAPI REST API Orchestrator & Request Dispatcher",
                "logic": "Exposes /verify and /verify-multiple endpoints. Solves Starlette/Python 3.13 metaclass nuances with duck-typing payload normalizers. Implements defensive guards (10MB limits, format checks, PIL image verification). Dispatches OCR, validators, forensics, biometrics, and cross-reconciliation. Ensures zero data retention via ephemeral temp file scrubbing in finally blocks."
            },
            {
                "file": "validators.py",
                "lines": "964 lines (39.4 KB)",
                "purpose": "Mathematical & Statutory Indian Document Validation Rules",
                "logic": "Implements the Verhoeff Dihedral Group D5 check digit algorithm for 12-digit Aadhaar cards (+35 penalty if invalid). Validates 10-char PAN entity types and checks that 5th char matches surname initial (+20 penalty). Validates 37 Indian State RTO codes for DLs. Validates ICAO 9303 TD3 44-char MRZ cyclic (7,3,1) check digits for Passports. Enforces lifetime validity for Aadhaar/PAN/Voter ID (0 expiry penalty)."
            },
            {
                "file": "cross_document.py",
                "lines": "757 lines (31.6 KB)",
                "purpose": "Cross-Document Demographic Reconciliation & Section 139AA Engine",
                "logic": "Performs pairwise multi-document comparison across N uploaded cards: honorific-stripped token-sorted name matching (Levenshtein & Jaro-Winkler >= 85%), multi-format DOB normalization, statutory Section 139AA Aadhaar-PAN linkage verification (+40 penalty on mismatch), and pairwise portrait-to-portrait facial biometric comparison."
            },
            {
                "file": "face_verification.py",
                "lines": "467 lines (19.6 KB)",
                "purpose": "128D Deep Facial Biometric Comparison & Image Quality Engine",
                "logic": "Auto-mounts virtualenv site-packages to eliminate IDE lint errors. Implements multi-stage face detection: Standard HOG fast-pass + CLAHE contrast recovery fallback for dim/laminated cards + 4-angle rotation search. Assesses face quality via Laplacian blur variance (>=80.0) and illumination clipping. Selects primary face using area/centrality weighting. Computes calibrated Euclidean distance mapped to similarity percentages."
            },
            {
                "file": "ocr_tesseract.py",
                "lines": "550 lines (20.7 KB)",
                "purpose": "High-Precision Dual-Pass OCR & Regex Demographic Parsing",
                "logic": "Applies grayscale adaptive thresholding and contrast normalization. Executes dual-pass Tesseract OCR: Pass 1 (PSM 3 automatic page segmentation) and Pass 2 (PSM 6 single uniform text block). Applies regex extractors for Aadhaar, PAN, Voter ID, Driving Licence, and ICAO 9303 MRZ lines."
            },
            {
                "file": "why_flagged.py",
                "lines": "416 lines (16.2 KB)",
                "purpose": "4-Domain Risk Decomposition & 3-Tier Officer Priority Queue",
                "logic": "Deconstructs unified risk scores (0-100) into 4 distinct domains: Forensics, Biometrics, Cross-Document Consistency, and Compliance. Maps cases to Tier 1 (Immediate Escalation, >=70), Tier 2 (Standard Review, 30-69), or Tier 3 (Fast-Track Clearance, <30) accompanied by actionable next steps."
            },
            {
                "file": "identity_story.py",
                "lines": "278 lines (11.6 KB)",
                "purpose": "Explainable AI (XAI) Natural Language Case Narrative Generator",
                "logic": "Translates complex mathematical checksum outcomes, OCR extraction findings, and biometric distance metrics into plain English, human-readable executive narratives for compliance officers."
            },
            {
                "file": "audit_trail.py",
                "lines": "105 lines (3.5 KB)",
                "purpose": "Tamper-Evident Chronological Event Logging & Session Sealing",
                "logic": "Maintains an immutable event ledger recording pipeline stages with ISO-8601 UTC timestamps and previous-entry hash chaining. Computes an immutable SHA-256 Session Seal Digest over all events and uploaded document hashes for legal admissibility under the Indian IT Act, 2000."
            },
            {
                "file": "forensics.py",
                "lines": "22 lines (463 bytes)",
                "purpose": "Digital Image Tampering & Forgery Detection Routine",
                "logic": "Executes Error Level Analysis (ELA) by re-compressing document scans at 90% JPEG quality, computing pixel delta matrices to spot spliced text, altered numbers, or pasted photo patches."
            },
            {
                "file": "ocr.py",
                "lines": "180 lines (6.8 KB)",
                "purpose": "Backward-Compatible Legacy OCR Routing Interface",
                "logic": "Provides an abstraction layer connecting raw image inputs to Tesseract preprocessing routines for legacy API callers."
            }
        ]
    },
    {
        "cat_name": "2. Environment Setup, Diagnostics & Asset Generation",
        "desc": "Utility scripts that configure binary paths, check system dependencies, and programmatically generate realistic synthetic credential graphics.",
        "files": [
            {
                "file": "generate_demo_assets.py",
                "lines": "195 lines (7.1 KB)",
                "purpose": "Synthetic Credential Graphics & Demo Asset Generator",
                "logic": "Uses PIL (Pillow) to draw high-resolution, photorealistic synthetic demo credentials (clean Aadhaar, counterfeit Aadhaar with bad check digit, clean PAN, Person A Aadhaar, Person B PAN) used for 1-click frontend demonstrations."
            },
            {
                "file": "tesseract_config.py",
                "lines": "55 lines (1.7 KB)",
                "purpose": "Automated Windows Tesseract Binary Path Resolver",
                "logic": "Scans default Windows installation locations ('C:\\Program Files\\Tesseract-OCR\\tesseract.exe') and sets pytesseract.tesseract_cmd dynamically to prevent path misconfigurations across developer machines."
            },
            {
                "file": "tesseract_setup.py",
                "lines": "85 lines (2.7 KB)",
                "purpose": "OCR Diagnostic & Environment Setup Verification Tool",
                "logic": "Executes version checks ('tesseract --version'), tests read permissions, and outputs diagnostic guidance if the Tesseract binary is missing from the system."
            }
        ]
    },
    {
        "cat_name": "3. Automated Test Suites & Regression Harnesses",
        "desc": "Automated test suites covering 100% of mathematical rules, statutory compliance, edge cases, cross-document reconciliation, and end-to-end API pipelines.",
        "files": [
            {
                "file": "test_real_vs_fake.py",
                "lines": "632 lines (27.3 KB)",
                "purpose": "Master 18-Scenario Real vs. Fake Truth Table Verification Suite",
                "logic": "Evaluates 18 comprehensive real and fake identity scenarios: authentic Aadhaar, corrupted Verhoeff UID, leading zero violation, truncated digits, PAN surname mismatch, DL jurisdiction, expired cards, multi-doc pairs, and biometric imposter attacks (100% pass rate)."
            },
            {
                "file": "test_full_pipeline.py",
                "lines": "388 lines (15.1 KB)",
                "purpose": "13-Scenario End-to-End API Pipeline Integration Suite",
                "logic": "Tests full lifecycle via FastAPI TestClient: OCR extraction, MRZ parsing, face matching, single/multi-doc uploads, error handling, and verifies zero temporary files remain in temp/ upon completion."
            },
            {
                "file": "test_edge_cases.py",
                "lines": "315 lines (11.9 KB)",
                "purpose": "10-Scenario Defensive Edge Cases & Malformed Input Test Suite",
                "logic": "Validates system resilience against 0-byte files, non-image files, corrupt JPGs, >10MB oversized files, unsupported formats, blank images, and non-face selfies."
            },
            {
                "file": "test_indian_documents.py",
                "lines": "230 lines (8.3 KB)",
                "purpose": "Dedicated Indian Credential Statutory Rules Test Suite",
                "logic": "Focuses specifically on Verhoeff D5 check digit math, PAN entity/surname validation, RTO state codes, and statutory lifetime validity for Indian credentials."
            },
            {
                "file": "test_cross_document.py",
                "lines": "225 lines (8.4 KB)",
                "purpose": "Cross-Document Reconciliation & Section 139AA Test Suite",
                "logic": "Tests fuzzy name matching across token reordering/honorific omission, DOB cross-format equality, Section 139AA linkage, and portrait-to-portrait face comparison."
            },
            {
                "file": "test_advanced_features.py",
                "lines": "205 lines (7.7 KB)",
                "purpose": "Explainable AI, Queue & Cryptographic Audit Unit Tests",
                "logic": "Verifies that Identity Story narratives generate properly, Why-Flagged 4 domains decompose risk accurately, and SHA-256 session seals chain monotonically."
            },
            {
                "file": "test_face.py",
                "lines": "32 lines (808 bytes)",
                "purpose": "Standalone Face Verification Test Harness",
                "logic": "Instantiates FaceVerifier and executes sanity checks on mock portrait image pairs and missing file fallbacks."
            },
            {
                "file": "test_forensics.py",
                "lines": "22 lines (536 bytes)",
                "purpose": "Standalone Error Level Analysis (ELA) Test Harness",
                "logic": "Tests TamperingDetector initialization and confirms ELA difference matrix calculation runs without exceptions."
            },
            {
                "file": "test_opencv_face.py",
                "lines": "45 lines (1.3 KB)",
                "purpose": "OpenCV Vision Fallback Test Harness",
                "logic": "Exercises OpenCV matrix conversions, CLAHE adaptive equalization, and Laplacian variance calculations."
            },
            {
                "file": "test.py",
                "lines": "12 lines (274 bytes)",
                "purpose": "Quick Developer Environment Smoke Test",
                "logic": "Executes minimal import checks to confirm the local virtual environment and libraries load cleanly."
            }
        ]
    }
]

html_sections = ""
table_rows = ""
counter = 1

for sec in categories:
    html_sections += f"""
    <div class="section-title">
        <h2>{sec['cat_name']}</h2>
        <p class="section-desc">{sec['desc']}</p>
    </div>
    """
    for f in sec['files']:
        html_sections += f"""
        <div class="card">
            <div class="card-header">
                <span class="badge-num">#{counter}</span>
                <span class="file-name">{f['file']}</span>
                <span class="badge-lines">{f['lines']}</span>
            </div>
            <div class="card-body">
                <p><strong>Purpose:</strong> {f['purpose']}</p>
                <p><strong>Underlying Algorithmic Logic:</strong> {f['logic']}</p>
            </div>
        </div>
        """
        table_rows += f"""
        <tr>
            <td style="text-align:center; font-weight:bold;">{counter}</td>
            <td><code>{f['file']}</code></td>
            <td>{f['lines']}</td>
            <td><strong>{f['purpose']}</strong></td>
            <td>{f['logic'][:115]}...</td>
        </tr>
        """
        counter += 1

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>VeriGuard AI - Backend Python Source Code Architecture Guide</title>
    <style>
        @page {{
            size: A4;
            margin: 16mm 14mm 16mm 14mm;
            @bottom-right {{
                content: counter(page);
            }}
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            color: #1e293b;
            line-height: 1.45;
            font-size: 12.5px;
            background: #ffffff;
            margin: 0;
            padding: 0;
        }}
        .header {{
            border-bottom: 3px solid #3b82f6;
            padding-bottom: 12px;
            margin-bottom: 18px;
        }}
        .header h1 {{
            margin: 0 0 6px 0;
            color: #0f172a;
            font-size: 22px;
            letter-spacing: -0.5px;
        }}
        .header .subtitle {{
            color: #475569;
            font-size: 13px;
            margin: 0;
        }}
        .meta-box {{
            background: #eff6ff;
            border-left: 4px solid #3b82f6;
            padding: 10px 14px;
            margin-bottom: 20px;
            border-radius: 4px;
            font-size: 12px;
        }}
        .meta-box strong {{
            color: #0f172a;
        }}
        .section-title {{
            margin-top: 24px;
            margin-bottom: 12px;
            border-bottom: 1px solid #cbd5e1;
            padding-bottom: 4px;
            page-break-after: avoid;
        }}
        .section-title h2 {{
            margin: 0 0 4px 0;
            font-size: 15px;
            color: #0f172a;
        }}
        .section-desc {{
            margin: 0;
            font-size: 12px;
            color: #64748b;
        }}
        .card {{
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            margin-bottom: 10px;
            page-break-inside: avoid;
            background: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }}
        .card-header {{
            background: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
            padding: 7px 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .badge-num {{
            background: #3b82f6;
            color: #ffffff;
            padding: 1px 7px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 700;
        }}
        .file-name {{
            font-family: "JetBrains Mono", Consolas, monospace;
            font-weight: 700;
            color: #0f172a;
            font-size: 13px;
        }}
        .badge-lines {{
            margin-left: auto;
            background: #dbeafe;
            color: #1e40af;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            font-family: monospace;
        }}
        .card-body {{
            padding: 8px 12px;
        }}
        .card-body p {{
            margin: 3px 0;
        }}
        code {{
            font-family: Consolas, monospace;
            background: #f1f5f9;
            padding: 1px 5px;
            border-radius: 3px;
            font-size: 11.5px;
            color: #1d4ed8;
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
            margin-top: 24px;
            border-top: 1px solid #cbd5e1;
            padding-top: 8px;
            text-align: center;
            font-size: 11px;
            color: #64748b;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>VeriGuard AI — Backend Python Source Code Guide</h1>
        <p class="subtitle">Complete Technical Catalog of All 23 Backend Python Modules (<code>backend/*.py</code>)</p>
    </div>

    <div class="meta-box">
        <strong>Overview of Backend Architecture:</strong><br>
        The <code>backend/</code> directory contains 23 Python source files structured into 3 distinct functional tiers: (1) Core Ingestion, OCR, Biometric & Validation Engines, (2) Environment Setup & Asset Generators, and (3) Comprehensive Automated Test Suites. All modules adhere strictly to Python 3.13 standards and integrate seamlessly into the FastAPI ASGI pipeline.
    </div>

    {html_sections}

    <div style="page-break-before: always;"></div>
    <h2>Quick Reference Matrix: All 23 Backend Python Files</h2>
    <table>
        <thead>
            <tr>
                <th style="width: 4%;">#</th>
                <th style="width: 25%;">File Name</th>
                <th style="width: 16%;">Lines / Size</th>
                <th style="width: 25%;">Architectural Purpose</th>
                <th style="width: 30%;">Core Algorithmic Logic</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>

    <div class="footer">
        VeriGuard AI &copy; 2026 | Real-Time Identity Fraud Detection & Cross-Document Reconciliation Engine
    </div>
</body>
</html>
"""

html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "py_codes_guide.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(full_html)

print(f"[*] Generated HTML: {html_path}")
print(f"[*] Printing to PDF: {PDF_DEST}")

cmd = [
    EDGE_EXE,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={PDF_DEST}",
    html_path
]

res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0 and os.path.isfile(PDF_DEST):
    print(f"[OK] Successfully generated: {PDF_DEST} ({os.path.getsize(PDF_DEST)} bytes)")
else:
    print(f"[!] Error: {res.stderr}")
