# build_venv_pdf.py
import os
import subprocess

DESKTOP_DIR = r"C:\Users\pc\Desktop"
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PDF_DEST = os.path.join(DESKTOP_DIR, "VeriGuard_AI_Venv_and_Dependencies_Guide.pdf")

venv_structure = [
    {
        "name": "pyvenv.cfg",
        "type": "Configuration File",
        "ext": ".cfg",
        "path": "backend/venv/pyvenv.cfg",
        "purpose": "Virtual Environment Configuration & Isolation Boundary",
        "logic": "Instructs Python to isolate package imports from the global system ('include-system-site-packages = false'). Directs binary resolution to CPython 3.13."
    },
    {
        "name": "python.exe & pythonw.exe",
        "type": "Executable Binary",
        "ext": ".exe",
        "path": "backend/venv/Scripts/python.exe",
        "purpose": "Virtualized CPython 3.13 Interpreter",
        "logic": "Provides a sandboxed execution runtime configured with sys.prefix targeting backend/venv, ensuring all dependency lookups hit local site-packages."
    },
    {
        "name": "pip.exe, pip3.exe, pip3.13.exe",
        "type": "Package Manager",
        "ext": ".exe",
        "path": "backend/venv/Scripts/pip.exe",
        "purpose": "Isolated Python Package Installer",
        "logic": "Manages library installation, version constraints, and wheels strictly inside backend/venv without modifying system-wide packages."
    },
    {
        "name": "uvicorn.exe",
        "type": "ASGI Server Binary",
        "ext": ".exe",
        "path": "backend/venv/Scripts/uvicorn.exe",
        "purpose": "Asynchronous Server Gateway Interface Web Server",
        "logic": "Hosts the FastAPI application on 127.0.0.1:8000. Provides event-loop request multiplexing, HTTP parsing, and live reload watchers."
    },
    {
        "name": "activate.bat & Activate.ps1",
        "type": "Shell Script",
        "ext": ".bat / .ps1",
        "path": "backend/venv/Scripts/activate.bat",
        "purpose": "Shell Environment Variable Modifier",
        "logic": "Prepends backend/venv/Scripts to the system %PATH% variable and sets VIRTUAL_ENV environment markers for command prompt or PowerShell."
    },
    {
        "name": "deactivate.bat",
        "type": "Shell Script",
        "ext": ".bat",
        "path": "backend/venv/Scripts/deactivate.bat",
        "purpose": "Environment Restoration Hook",
        "logic": "Restores original shell %PATH% and unsets virtual environment variables."
    }
]

core_packages = [
    {
        "name": "face-recognition (v1.3.0) & dlib (v20.0.1)",
        "category": "Biometric Deep Learning",
        "ext": ".py / C++ .pyd",
        "purpose": "128-Dimensional Deep Facial Biometric Vector Extraction",
        "logic": "Employs dlib's C++ ResNet-34 model to detect facial landmarks and project face geometry into a normalized 128D embedding space, enabling Euclidean distance similarity computation."
    },
    {
        "name": "opencv-python-headless (v5.0.0.93)",
        "category": "Computer Vision & Processing",
        "ext": "C++ .pyd / .py",
        "purpose": "High-Performance Image Preprocessing & Forensics",
        "logic": "Executes color space conversions (RGB/BGR/Gray), CLAHE (Contrast Limited Adaptive Histogram Equalization) for dim/laminated cards, and Laplacian second-order derivative blur variance calculation."
    },
    {
        "name": "fastapi (v0.141.1) & starlette (v1.6.0)",
        "category": "Web Framework & Routing",
        "ext": ".py",
        "purpose": "Asynchronous REST API Gateway & Microservice Routing",
        "logic": "Defines endpoints (/verify, /verify-multiple, /health), parses multipart/form-data upload streams, executes schema validation, and handles HTTP response serialization."
    },
    {
        "name": "uvicorn (v0.52.4)",
        "category": "ASGI Web Server",
        "ext": ".py",
        "purpose": "Asynchronous HTTP Server Protocol Engine",
        "logic": "Implements uvloop/asyncio socket listeners, handling concurrent network requests between React frontend and FastAPI backend with sub-millisecond overhead."
    },
    {
        "name": "pytesseract (v0.3.13)",
        "category": "Optical Character Recognition",
        "ext": ".py",
        "purpose": "Tesseract OCR Integration Wrapper",
        "logic": "Bridges Python with the system Tesseract OCR binary, passing image byte buffers and retrieving text under Page Segmentation Modes (PSM 3 & 6)."
    },
    {
        "name": "pillow / PIL (v12.3.0)",
        "category": "Image File Manipulation",
        "ext": "C .pyd / .py",
        "purpose": "EXIF Transposition, Format Decoding & Synthetic Rendering",
        "logic": "Corrects mobile camera EXIF orientation tags, validates image file integrity, enforces aspect-ratio preserving downscaling, and renders synthetic demo credential graphics."
    },
    {
        "name": "numpy (v2.5.2) & scipy (v1.18.1)",
        "category": "Scientific Computing & Linear Algebra",
        "ext": "C .pyd / .py",
        "purpose": "Vectorized Matrix Calculations & Euclidean Norms",
        "logic": "Computes Euclidean distances between 128D embedding vectors, gradient edge maps, and image delta matrices for Error Level Analysis (ELA) tampering detection."
    },
    {
        "name": "pydantic (v2.13.5) & pydantic-core (v2.46.5)",
        "category": "Data Validation & Modeling",
        "ext": "Rust .pyd / .py",
        "purpose": "Strict Type Safety & Response Serialization",
        "logic": "Enforces type contracts and generates OpenAPI/Swagger schemas for all verification request models and analytical output payloads."
    },
    {
        "name": "python-multipart (v0.0.32)",
        "category": "HTTP Streaming Parser",
        "ext": ".py",
        "purpose": "Multipart/Form-Data File Ingestion",
        "logic": "Streams incoming document scans and webcam selfies from frontend multipart HTTP POST requests directly into in-memory file buffers."
    },
    {
        "name": "torch (v2.14.0) & torchvision (v0.29.0)",
        "category": "Deep Learning Framework",
        "ext": "C++ .pyd / .py",
        "purpose": "Tensor Computing & Neural Network Vision Backends",
        "logic": "Powers tensor mathematical operations and neural vision layers for advanced pattern recognition tasks."
    },
    {
        "name": "scikit-image (v0.26.0)",
        "category": "Image Analysis Algorithms",
        "ext": "Cython .pyd / .py",
        "purpose": "Scientific Image Analysis & Structural Similarity",
        "logic": "Provides mathematical functions for image segmentation, noise filtering, and structural comparisons."
    }
]

html_venv = ""
for item in venv_structure:
    html_venv += f"""
    <div class="card">
        <div class="card-header">
            <span class="badge-type">{item['type']}</span>
            <span class="file-name">{item['name']}</span>
            <span class="badge-ext">{item['ext']}</span>
            <span class="badge-path">{item['path']}</span>
        </div>
        <div class="card-body">
            <p><strong>Purpose:</strong> {item['purpose']}</p>
            <p><strong>Underlying Logic:</strong> {item['logic']}</p>
        </div>
    </div>
    """

html_pkg = ""
table_pkg = ""
for i, p in enumerate(core_packages, 1):
    html_pkg += f"""
    <div class="card">
        <div class="card-header">
            <span class="badge-num">#{i}</span>
            <span class="file-name">{p['name']}</span>
            <span class="badge-category">{p['category']}</span>
            <span class="badge-ext">{p['ext']}</span>
        </div>
        <div class="card-body">
            <p><strong>Purpose:</strong> {p['purpose']}</p>
            <p><strong>Underlying Logic:</strong> {p['logic']}</p>
        </div>
    </div>
    """
    table_pkg += f"""
    <tr>
        <td style="text-align:center; font-weight:bold;">{i}</td>
        <td><strong>{p['name']}</strong></td>
        <td>{p['category']}</td>
        <td><code>{p['ext']}</code></td>
        <td>{p['purpose']}</td>
    </tr>
    """

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>VeriGuard AI - Virtual Environment (venv) & Dependencies Technical Reference Guide</title>
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
            border-bottom: 3px solid #6366f1;
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
            background: #eef2ff;
            border-left: 4px solid #6366f1;
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
        .badge-type, .badge-num {{
            background: #6366f1;
            color: #ffffff;
            padding: 1px 7px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 700;
        }}
        .badge-category {{
            background: #ede9fe;
            color: #6d28d9;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }}
        .file-name {{
            font-family: "JetBrains Mono", Consolas, monospace;
            font-weight: 700;
            color: #0f172a;
            font-size: 12.5px;
        }}
        .badge-ext {{
            background: #e0e7ff;
            color: #3730a3;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            font-family: monospace;
        }}
        .badge-path {{
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
            color: #4338ca;
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
        <h1>VeriGuard AI — Virtual Environment (venv) & Dependencies Guide</h1>
        <p class="subtitle">Complete Technical Blueprint of CPython 3.13 Isolation Layer, Binaries & Core Scientific Libraries</p>
    </div>

    <div class="meta-box">
        <strong>Role of <code>backend/venv</code>:</strong><br>
        Provides a self-contained, isolated Python 3.13 runtime environment. This guarantees that VeriGuard AI's deep learning, computer vision, and cryptographic libraries execute with deterministic package versions across all developer machines, isolated completely from Windows Store or global Python installations.
    </div>

    <div class="section-title">
        <h2>1. Virtual Environment Structural Components & Executables</h2>
        <p class="section-desc">Key configuration files, binaries, and shell hooks in <code>backend/venv/</code> and <code>backend/venv/Scripts/</code>.</p>
    </div>
    {html_venv}

    <div style="page-break-before: always;"></div>
    <div class="section-title">
        <h2>2. Core Installed Libraries in <code>backend/venv/Lib/site-packages/</code></h2>
        <p class="section-desc">Deep learning, vision, web server, and scientific packages powering VeriGuard AI's verification pipeline.</p>
    </div>
    {html_pkg}

    <div style="page-break-before: always;"></div>
    <h2>Quick Reference Matrix: Core Installed Packages</h2>
    <table>
        <thead>
            <tr>
                <th style="width: 5%;">#</th>
                <th style="width: 30%;">Package & Version</th>
                <th style="width: 20%;">Category</th>
                <th style="width: 15%;">Extension</th>
                <th style="width: 30%;">Primary Role in Pipeline</th>
            </tr>
        </thead>
        <tbody>
            {table_pkg}
        </tbody>
    </table>

    <div class="footer">
        VeriGuard AI &copy; 2026 | Real-Time Identity Fraud Detection & Cross-Document Reconciliation Engine
    </div>
</body>
</html>
"""

html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv_guide.html")
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
