# build_frontend_docs_pdf.py
import os
import subprocess

DESKTOP_DIR = r"C:\Users\pc\Desktop"
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PDF_DEST = os.path.join(DESKTOP_DIR, "VeriGuard_AI_Frontend_Docs_and_Tests_Guide.pdf")

frontend_sections = [
    {
        "cat_title": "1. Frontend Application Pages (frontend/src/pages/)",
        "desc": "The primary user interface views managing officer authentication, multi-document ingestion, scanning telemetry, and forensic results reporting.",
        "files": [
            {
                "name": "ResultsPage.jsx",
                "type": "React Component / View",
                "ext": ".jsx",
                "path": "frontend/src/pages/ResultsPage.jsx",
                "size": "74.3 KB (1,600+ lines)",
                "purpose": "Master Forensic Intelligence Dossier & Officer Adjudication Dashboard",
                "logic": "Renders the interactive compliance dossier: Circular Risk Score Gauge (0-100), Section 139AA statutory compliance badge, Natural Language Identity Story, Why-Flagged 4-domain risk decomposition, 3-Tier Officer Priority Queue (Tier 1 Escalate, Tier 2 Review, Tier 3 Clear), Cross-Document Discrepancy Matrix, Biometric Face Match side-by-side comparison, and SHA-256 Cryptographic Audit Seal."
            },
            {
                "name": "UploadPage.jsx",
                "type": "React Component / View",
                "ext": ".jsx",
                "path": "frontend/src/pages/UploadPage.jsx",
                "size": "21.2 KB",
                "purpose": "Multi-Document Ingestion Dropzone & 1-Click Scenario Trigger Interface",
                "logic": "Provides a drag-and-drop file dropzone supporting multiple document uploads simultaneously with document chip badges. Features webcam selfie capture or file upload toggle, client-side pre-flight image quality validation, and 3 preloaded 1-click test scenario buttons (Clean Indian KYC, Counterfeit Aadhaar, Synthetic Identity Conflict)."
            },
            {
                "name": "ProcessingPage.jsx",
                "type": "React Component / View",
                "ext": ".jsx",
                "path": "frontend/src/pages/ProcessingPage.jsx",
                "size": "5.5 KB",
                "purpose": "Real-Time Holographic Scanning Telemetry & Progress Visualizer",
                "logic": "Renders an animated cyberpunk laser scanner bar with vertical beam oscillation, rotating radar sweep rings, and a dynamic 6-stage telemetry checklist tracking real-time pipeline execution from ingestion through cryptographic sealing."
            },
            {
                "name": "Loginpage.jsx",
                "type": "React Component / View",
                "ext": ".jsx",
                "path": "frontend/src/pages/Loginpage.jsx",
                "size": "3.2 KB",
                "purpose": "Officer Authentication & Compliance Session Initialization",
                "logic": "Provides an officer login portal with badge ID verification and compliance credentials simulation, establishing session context for audit logging."
            }
        ]
    },
    {
        "cat_title": "2. Frontend Core Controllers, API & Utilities (frontend/src/)",
        "desc": "The foundational React state machine, layout components, HTTP communication clients, and client-side image quality guards.",
        "files": [
            {
                "name": "App.jsx",
                "type": "React Master Controller",
                "ext": ".jsx",
                "path": "frontend/src/App.jsx",
                "size": "15.3 KB",
                "purpose": "Master State Machine, Screen Navigation & Scenario Dispatcher",
                "logic": "Manages global application state transitions (login -> upload -> processing -> results). Coordinates 1-click scenario execution by fetching pre-rendered demo assets from public/demo_assets/, converting them into File blobs, and dispatching multipart HTTP verification requests."
            },
            {
                "name": "App.css",
                "type": "Vanilla CSS Stylesheet",
                "ext": ".css",
                "path": "frontend/src/App.css",
                "size": "40.9 KB (1,200+ lines)",
                "purpose": "Master Cybernetic Glassmorphic Design System",
                "logic": "Zero Tailwind dependencies; hand-crafted Dark Glassmorphic styling (rgba(15, 23, 42, 0.75), backdrop-filter blur(16px)), HSL color tokens (Cyber Cyan #06b6d4, Emerald #10b981, Amber #f59e0b, Crimson #ef4444), fluid responsive Grid/Flexbox breakpoints, and keyframe animations for laser sweeps."
            },
            {
                "name": "imageQuality.js",
                "type": "Client Utility Module",
                "ext": ".js",
                "path": "frontend/src/utils/imageQuality.js",
                "size": "4.0 KB",
                "purpose": "Client-Side Pre-Flight Image Quality & Blur Guard",
                "logic": "Uses an in-memory HTML5 Canvas to inspect uploaded images before submission. Computes pixel luminance histograms to detect severe underexposure, overexposure, and high-frequency edge degradation, warning users if an image is too blurry for reliable OCR."
            },
            {
                "name": "verification.js",
                "type": "API Client Module",
                "ext": ".js",
                "path": "frontend/src/api/verification.js",
                "size": "2.2 KB",
                "purpose": "Axios HTTP REST Gateway Client",
                "logic": "Constructs FormData multipart/form-data payloads streaming multi-document arrays and selfie blobs to the FastAPI backend (/verify and /verify-multiple). Handles timeout configurations and standardizes error responses."
            },
            {
                "name": "TopBar.jsx",
                "type": "Layout Component",
                "ext": ".jsx",
                "path": "frontend/src/components/Layout/TopBar.jsx",
                "size": "1.2 KB",
                "purpose": "Cyberpunk Navigation Header & Engine Status Indicator",
                "logic": "Renders the VeriGuard AI shield emblem, active microservice status badge (LIVE), officer credential profile, and session navigation buttons."
            },
            {
                "name": "index.css",
                "type": "Global Stylesheet",
                "ext": ".css",
                "path": "frontend/src/index.css",
                "size": "2.1 KB",
                "purpose": "CSS Reset, Typography Tokens & Root Variables",
                "logic": "Sets up baseline box-sizing, custom scrollbars, and loads Google Webfonts (Rajdhani for headers, Inter for body copy, JetBrains Mono for code)."
            },
            {
                "name": "main.jsx",
                "type": "DOM Mount Entrypoint",
                "ext": ".jsx",
                "path": "frontend/src/main.jsx",
                "size": "229 bytes",
                "purpose": "React 19 Virtual DOM Mounting Script",
                "logic": "Mounts the root App component to the DOM element with id 'root' using ReactDOM.createRoot()."
            }
        ]
    },
    {
        "cat_title": "3. Frontend Build & Static Assets (frontend/ & public/)",
        "desc": "Build configurations, package manifests, and static demo assets served directly to the browser.",
        "files": [
            {
                "name": "vite.config.js",
                "type": "Bundler Configuration",
                "ext": ".js",
                "path": "frontend/vite.config.js",
                "size": "514 bytes",
                "purpose": "Vite 8 Build & Development Server Configuration",
                "logic": "Configures @vitejs/plugin-react, defines the local development server to run on port 5173, and specifies production bundling optimizations."
            },
            {
                "name": "package.json",
                "type": "NPM Manifest",
                "ext": ".json",
                "path": "frontend/package.json",
                "size": "648 bytes",
                "purpose": "Frontend Dependencies & Scripts Specification",
                "logic": "Registers React 19.2.0, Lucide React (cyberpunk icons), Axios (HTTP client), Vite (bundler), and ESLint. Defines 'npm run dev', 'npm run build', and 'npm run lint' scripts."
            },
            {
                "name": "eslint.config.js",
                "type": "Linting Configuration",
                "ext": ".js",
                "path": "frontend/eslint.config.js",
                "size": "568 bytes",
                "purpose": "JavaScript & React Code Quality Linter",
                "logic": "Enforces ECMAScript 2022+ syntax, React Hooks rules of hooks, and prevents common frontend code smells (0 errors / 0 warnings verified)."
            },
            {
                "name": "index.html",
                "type": "HTML5 Entrypoint",
                "ext": ".html",
                "path": "frontend/index.html",
                "size": "360 bytes",
                "purpose": "Single Page Application (SPA) Host Document",
                "logic": "Declares viewport meta tags, document title ('VeriGuard AI - Real-Time Identity Fraud Detection'), and loads main.jsx as an ES module."
            },
            {
                "name": "public/demo_assets/ (7 files)",
                "type": "Static Pre-Rendered Assets",
                "ext": ".png / .jpg",
                "path": "frontend/public/demo_assets/",
                "size": "Total ~2.3 MB",
                "purpose": "Pre-Rendered Benchmark Identity Documents & Selfies",
                "logic": "Contains demo_aadhaar_clean.png, demo_aadhaar_counterfeit.png, demo_aadhaar_person_a.png, demo_pan_clean.png, demo_pan_person_b.png, demo_selfie_match.jpg, and demo_selfie_imposter.jpg directly accessible by the frontend for 1-click evaluations."
            },
            {
                "name": "favicon.svg & icons.svg",
                "type": "Vector Graphics",
                "ext": ".svg",
                "path": "frontend/public/favicon.svg",
                "size": "14.5 KB",
                "purpose": "Application Branding & SVG Icon Sprites",
                "logic": "Provides scalable vector shield graphics and security icons rendered across the navigation bar and browser tab."
            }
        ]
    },
    {
        "cat_title": "4. Root-Level Directories: temp/, docs/, and tests/",
        "desc": "Root workspace directories fulfilling specific operational, documentation, and testing functions.",
        "files": [
            {
                "name": "temp/ (Root Directory)",
                "type": "Transient Upload Buffer",
                "ext": "Directory",
                "path": "temp/",
                "size": "~1.2 MB active",
                "purpose": "Root Ephemeral Document Staging Directory",
                "logic": "Holds transient identity document uploads (e.g. doc_1_76d86076-*.jpg) when requests originate from root-level test scripts. Subject to the exact same Zero Permanent Data Retention auto-scrubbing policy."
            },
            {
                "name": "docs/ (Root Directory)",
                "type": "Documentation Folder",
                "ext": "Directory",
                "path": "docs/",
                "size": "Empty Directory",
                "purpose": "Project Architectural Documentation Staging",
                "logic": "Reserved folder for storing compiled system diagrams, regulatory compliance whitepapers, and exported PDF documentation."
            },
            {
                "name": "tests/ (Root Directory)",
                "type": "Test Staging Folder",
                "ext": "Directory",
                "path": "tests/",
                "size": "Empty Directory",
                "purpose": "Global Integration Test Staging Folder",
                "logic": "Reserved root-level directory for cross-platform CI/CD test runners; active production test suites are centralized inside backend/ and test_full_pipeline.py."
            }
        ]
    }
]

html_sections = ""
table_rows = ""
counter = 1

for sec in frontend_sections:
    html_sections += f"""
    <div class="section-title">
        <h2>{sec['cat_title']}</h2>
        <p class="section-desc">{sec['desc']}</p>
    </div>
    """
    for f in sec['files']:
        html_sections += f"""
        <div class="card">
            <div class="card-header">
                <span class="badge-num">#{counter}</span>
                <span class="file-name">{f['name']}</span>
                <span class="badge-type">{f['type']}</span>
                <span class="badge-path">{f['path']}</span>
            </div>
            <div class="card-body">
                <p><strong>Extension & Size:</strong> <code>{f['ext']}</code> &bull; {f['size']}</p>
                <p><strong>Purpose:</strong> {f['purpose']}</p>
                <p><strong>Underlying Logic:</strong> {f['logic']}</p>
            </div>
        </div>
        """
        table_rows += f"""
        <tr>
            <td style="text-align:center; font-weight:bold;">{counter}</td>
            <td><code>{f['name']}</code></td>
            <td>{f['type']}</td>
            <td><code>{f['path']}</code></td>
            <td><strong>{f['purpose']}</strong></td>
            <td>{f['logic'][:115]}...</td>
        </tr>
        """
        counter += 1

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>VeriGuard AI - Frontend, Docs, Temp & Tests Technical Reference Guide</title>
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
            border-bottom: 3px solid #0284c7;
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
            background: #f0f9ff;
            border-left: 4px solid #0284c7;
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
            background: #0284c7;
            color: #ffffff;
            padding: 1px 7px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 700;
        }}
        .badge-type {{
            background: #e0f2fe;
            color: #0369a1;
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
            color: #0284c7;
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
        <h1>VeriGuard AI — Frontend, Docs, Temp & Tests Architecture Guide</h1>
        <p class="subtitle">Complete Technical Catalog of React 19 Frontend Components, Styling, Build Configuration & Root Directories</p>
    </div>

    <div class="meta-box">
        <strong>Architectural Scope:</strong><br>
        This reference document covers the entirety of VeriGuard AI's presentation layer (React 19 + Vite 8), client-side telemetry utilities, pre-rendered synthetic demo assets, and the operational roles of the root-level <code>temp/</code>, <code>docs/</code>, and <code>tests/</code> workspace folders.
    </div>

    {html_sections}

    <div style="page-break-before: always;"></div>
    <h2>Quick Reference Matrix: All Frontend, Docs, Temp & Tests Items</h2>
    <table>
        <thead>
            <tr>
                <th style="width: 4%;">#</th>
                <th style="width: 22%;">Component / File</th>
                <th style="width: 16%;">Type</th>
                <th style="width: 20%;">Relative Path</th>
                <th style="width: 20%;">Primary Role</th>
                <th style="width: 18%;">Key Algorithmic Logic</th>
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

html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend_docs_guide.html")
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
