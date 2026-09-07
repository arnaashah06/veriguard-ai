# build_assets_pdf.py
import os
import subprocess

DESKTOP_DIR = r"C:\Users\pc\Desktop"
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PDF_DEST = os.path.join(DESKTOP_DIR, "VeriGuard_AI_Temp_and_Test_Assets_Guide.pdf")

# Data specification for temp and test_assets
sections = [
    {
        "title": "1. Ephemeral Staging Directory (temp/ and backend/temp/)",
        "desc": "Transient storage utilized during file upload processing and test executions. Operates under a Zero Permanent Data Retention policy.",
        "files": [
            {
                "file": "doc_{idx}_{uuid}.jpg / .png",
                "sample": "doc_1_76d86076-34c5-486d-b1f3-e02ce795c7b2.jpg (626 KB)",
                "ext": ".jpg / .png",
                "folder": "temp/ & backend/temp/",
                "purpose": "Ephemeral staging buffer for citizen identity documents during API ingestion.",
                "logic": "When multipart documents are streamed to /verify or /verify-multiple, they are temporarily staged on disk with UUID v4 filenames so Tesseract OCR, OpenCV, and dlib can read them. Immediately after processing, they are deleted via os.remove() in main.py's finally block to guarantee user privacy."
            },
            {
                "file": "selfie_{uuid}.jpg / .png",
                "sample": "selfie_289280bd-212a-4554-a8f2-a4a2c72b1cf9.jpg (555 KB)",
                "ext": ".jpg / .png",
                "folder": "temp/ & backend/temp/",
                "purpose": "Ephemeral staging buffer for cardholder webcam selfie captures.",
                "logic": "Saved transiently to disk to allow face_verification.py to extract 128-dimensional ResNet facial embeddings. Automatically scrubbed upon request completion."
            },
            {
                "file": "test_document.jpg & test_selfie.jpg",
                "sample": "test_document.jpg, test_selfie.jpg",
                "ext": ".jpg",
                "folder": "backend/temp/",
                "purpose": "Transient test fixtures created during standalone unit test executions.",
                "logic": "Used by test_face.py and test_full_pipeline.py to verify missing file handling, corrupted file fallbacks, and cleanup verification."
            }
        ]
    },
    {
        "title": "2. Benchmark Biometric Test Assets (backend/test_assets/)",
        "desc": "Standardized, high-resolution photographic identity test assets used across all automated test suites to rigorously validate facial recognition accuracy.",
        "files": [
            {
                "file": "doc_portrait.jpg",
                "sample": "doc_portrait.jpg (626,899 bytes)",
                "ext": ".jpg",
                "folder": "backend/test_assets/",
                "purpose": "Authentic cardholder document portrait benchmark image.",
                "logic": "Represents the passport/ID portrait photo extracted from an authentic credential. Serves as the baseline biometric reference vector (v1) for automated similarity scoring."
            },
            {
                "file": "selfie_match.jpg",
                "sample": "selfie_match.jpg (555,941 bytes)",
                "ext": ".jpg",
                "folder": "backend/test_assets/",
                "purpose": "Genuine matching live selfie portrait of the authentic cardholder.",
                "logic": "Pictured individual is identical to doc_portrait.jpg. FaceVerifier computes 128D ResNet embeddings resulting in Euclidean distance D = 0.2945 (<= 0.40 threshold), producing an 80.4% match score and driving an automated APPROVE verdict."
            },
            {
                "file": "selfie_mismatch.jpg",
                "sample": "selfie_mismatch.jpg (725,804 bytes)",
                "ext": ".jpg",
                "folder": "backend/test_assets/",
                "purpose": "Biometric imposter / identity fraud simulation portrait.",
                "logic": "Pictured individual is distinctly different from doc_portrait.jpg. FaceVerifier computes Euclidean distance D = 0.9291 (> 0.40 threshold), generating a low 27.1% similarity score and triggering an automated REJECT verdict with a +25 risk penalty."
            }
        ]
    },
    {
        "title": "3. 1-Click Interactive Demo Assets (backend/test_assets/demo/)",
        "desc": "Programmatically rendered synthetic credential and selfie assets powering the 1-click demonstration scenarios on the frontend HUD.",
        "files": [
            {
                "file": "demo_aadhaar_clean.png",
                "sample": "demo_aadhaar_clean.png (125 KB)",
                "ext": ".png",
                "folder": "backend/test_assets/demo/",
                "purpose": "Authentic Aadhaar credential for Rahul Kumar Sharma.",
                "logic": "Contains 12-digit UID 3675 9834 5212, which mathematically satisfies the Verhoeff Dihedral Group D5 checksum. Grants 0 risk penalty."
            },
            {
                "file": "demo_aadhaar_counterfeit.png",
                "sample": "demo_aadhaar_counterfeit.png (125 KB)",
                "ext": ".png",
                "folder": "backend/test_assets/demo/",
                "purpose": "Counterfeit Aadhaar credential with tampered check digit.",
                "logic": "Contains altered UID 3675 9834 5216 where the 12th check digit violates the Verhoeff permutation multiplication algorithm, immediately triggering a +35 risk penalty."
            },
            {
                "file": "demo_aadhaar_person_a.png",
                "sample": "demo_aadhaar_person_a.png (125 KB)",
                "ext": ".png",
                "folder": "backend/test_assets/demo/",
                "purpose": "Aadhaar credential for Person A (Rajesh Kumar).",
                "logic": "Used in Scenario 3 (Synthetic Identity Fraud) alongside Person B's PAN to demonstrate cross-document demographic divergence detection."
            },
            {
                "file": "demo_pan_clean.png",
                "sample": "demo_pan_clean.png (124 KB)",
                "ext": ".png",
                "folder": "backend/test_assets/demo/",
                "purpose": "Authentic PAN credential for Rahul Kumar Sharma.",
                "logic": "Contains PAN ABCPP1234F. Validates 4th character 'P' (Individual) and 5th character 'P' (matches surname Patel/Sharma), passing Section 139AA statutory linkage."
            },
            {
                "file": "demo_pan_person_b.png",
                "sample": "demo_pan_person_b.png (159 KB)",
                "ext": ".png",
                "folder": "backend/test_assets/demo/",
                "purpose": "PAN credential for Person B (Vikram Singh, ABCPV5678G).",
                "logic": "Paired with Person A's Aadhaar in Scenario 3. Triggers 0% name similarity, conflicting birth dates, and a statutory Section 139AA violation (+40 penalty points)."
            },
            {
                "file": "demo_selfie_match.jpg",
                "sample": "demo_selfie_match.jpg (555 KB)",
                "ext": ".jpg",
                "folder": "backend/test_assets/demo/",
                "purpose": "Matching selfie asset for Scenario 1 (Clean Indian KYC).",
                "logic": "Provides matching biometric feature vector for Rahul Kumar Sharma, confirming 80.4% - 82.9% biometric similarity."
            },
            {
                "file": "demo_selfie_imposter.jpg",
                "sample": "demo_selfie_imposter.jpg (725 KB)",
                "ext": ".jpg",
                "folder": "backend/test_assets/demo/",
                "purpose": "Imposter selfie asset for Scenario 3 (Synthetic Conflict).",
                "logic": "Provides non-matching biometric vector for Vikram Singh vs. Rahul Sharma, resulting in a face mismatch alert and Tier 1 priority queue escalation."
            }
        ]
    }
]

html_sections = ""
table_rows = ""
counter = 1

for sec in sections:
    html_sections += f"""
    <div class="section-title">
        <h2>{sec['title']}</h2>
        <p class="section-desc">{sec['desc']}</p>
    </div>
    """
    for f in sec['files']:
        html_sections += f"""
        <div class="card">
            <div class="card-header">
                <span class="badge-num">#{counter}</span>
                <span class="file-name">{f['file']}</span>
                <span class="badge-ext">{f['ext']}</span>
                <span class="badge-folder">{f['folder']}</span>
            </div>
            <div class="card-body">
                <p><strong>Sample / Size:</strong> {f['sample']}</p>
                <p><strong>Purpose:</strong> {f['purpose']}</p>
                <p><strong>Underlying Logic:</strong> {f['logic']}</p>
            </div>
        </div>
        """
        table_rows += f"""
        <tr>
            <td style="text-align:center; font-weight:bold;">{counter}</td>
            <td><code>{f['file']}</code></td>
            <td>{f['ext']}</td>
            <td><code>{f['folder']}</code></td>
            <td><strong>{f['purpose']}</strong></td>
            <td>{f['logic'][:110]}...</td>
        </tr>
        """
        counter += 1

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>VeriGuard AI - Temp & Test Assets Technical Reference Guide</title>
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
            border-bottom: 3px solid #0d9488;
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
            background: #f0fdfa;
            border-left: 4px solid #0d9488;
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
            background: #0d9488;
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
            font-size: 12.5px;
        }}
        .badge-ext {{
            background: #ccfbf1;
            color: #0f766e;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            font-family: monospace;
        }}
        .badge-folder {{
            margin-left: auto;
            color: #64748b;
            font-size: 11px;
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
            color: #0f766e;
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
        <h1>VeriGuard AI — Temp & Test Assets Technical Reference Guide</h1>
        <p class="subtitle">Complete Catalog of Ephemeral Staging Files, Benchmark Biometrics & 1-Click Demo Credentials</p>
    </div>

    <div class="meta-box">
        <strong>Directory Roles & Security Architecture:</strong><br>
        &bull; <strong>temp/ & backend/temp/:</strong> Ephemeral upload buffer designed for streaming multipart document and selfie data to OCR and computer vision engines. Operates under a strict <em>Zero Permanent Data Retention</em> policy where all files are purged in <code>finally:</code> blocks immediately after response synthesis.<br>
        &bull; <strong>backend/test_assets/:</strong> Permanent high-resolution reference photographic fixtures utilized by automated regression test suites (<code>test_real_vs_fake.py</code>, <code>test_full_pipeline.py</code>, <code>test_cross_document.py</code>).<br>
        &bull; <strong>backend/test_assets/demo/:</strong> Pre-rendered synthetic credentials and matching/imposter selfies powering the 1-click evaluation scenarios on the frontend HUD.
    </div>

    {html_sections}

    <div style="page-break-before: always;"></div>
    <h2>Quick Reference Matrix: All 13 Assets</h2>
    <table>
        <thead>
            <tr>
                <th style="width: 4%;">#</th>
                <th style="width: 24%;">File Name</th>
                <th style="width: 8%;">Ext</th>
                <th style="width: 18%;">Directory</th>
                <th style="width: 20%;">Purpose</th>
                <th style="width: 26%;">Key Algorithmic Logic</th>
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

html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets_guide.html")
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
