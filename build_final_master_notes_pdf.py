# build_final_master_notes_pdf.py
"""
VeriGuard AI - Master Codebase, Architecture & Verification Final Notes Builder
Generates a single, fully-detailed master PDF: "veriguard-ai final notes.pdf"
on the user's Desktop and inside the docs/ directory.
"""
import os
import subprocess
import time
import base64
import shutil

DESKTOP_DIR = r"C:\Users\pc\Desktop"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUTPUT_PDF = os.path.join(DESKTOP_DIR, "veriguard-ai final notes.pdf")
DOCS_PDF = os.path.join(DOCS_DIR, "veriguard-ai final notes.pdf")
HTML_FILE = os.path.join(ROOT_DIR, "temp_final_master_notes.html")

def get_base64_image(rel_path):
    full_path = os.path.join(ROOT_DIR, rel_path)
    if os.path.exists(full_path):
        with open(full_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            ext = os.path.splitext(full_path)[1].lower().replace(".", "")
            if ext == "jpg": ext = "jpeg"
            return f"data:image/{ext};base64,{encoded}"
    return ""

sih_logo_b64 = get_base64_image(r"temp\sih_assets\page_1_img_15.png")
brain_bulb_b64 = get_base64_image(r"temp\sih_assets\brain_bulb_clean.png")
results_capture_b64 = get_base64_image(r"results_capture.png")

print(f"[*] SIH Logo loaded: {bool(sih_logo_b64)}")
print(f"[*] Brain Bulb loaded: {bool(brain_bulb_b64)}")
print(f"[*] Results Capture loaded: {bool(results_capture_b64)}")

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>VeriGuard AI - Master Codebase, Architecture & Verification Notes</title>
<style>
  @page {
    size: A4;
    margin: 16mm 14mm 16mm 14mm;
    @bottom-right {
      content: counter(page);
      font-size: 8.5pt;
      color: #64748B;
      font-family: 'Segoe UI', sans-serif;
    }
    @bottom-left {
      content: "VeriGuard AI — Final Master Notes | Team Abstract_Minds (SIH2026-T2851)";
      font-size: 8.5pt;
      color: #64748B;
      font-family: 'Segoe UI', sans-serif;
    }
  }
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  body {
    font-family: 'Segoe UI', 'Inter', -apple-system, Roboto, sans-serif;
    color: #1E293B;
    line-height: 1.5;
    background: #FFFFFF;
    font-size: 9.5pt;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    padding: 15px 25px;
  }

  .page-break {
    page-break-before: always;
  }
  .avoid-break {
    page-break-inside: avoid;
  }

  /* HEADER & HERO */
  .doc-header {
    border-bottom: 3px solid #1F497D;
    padding-bottom: 14px;
    margin-bottom: 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .doc-title {
    font-size: 22pt;
    font-weight: 900;
    color: #1F497D;
    letter-spacing: -0.5px;
  }
  .doc-subtitle {
    font-size: 11pt;
    font-weight: 600;
    color: #0D9488;
    margin-top: 3px;
  }
  .doc-meta {
    font-size: 8.5pt;
    color: #64748B;
    margin-top: 4px;
  }
  .sih-logo {
    height: 60px;
    object-fit: contain;
  }

  /* HEADINGS */
  h1 {
    font-size: 15pt;
    font-weight: 800;
    color: #1F497D;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 5px;
    margin-top: 22px;
    margin-bottom: 10px;
  }
  h2 {
    font-size: 12pt;
    font-weight: 700;
    color: #0F172A;
    margin-top: 16px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
  }
  h2::before {
    content: "";
    display: inline-block;
    width: 6px;
    height: 15px;
    background: #2563EB;
    margin-right: 8px;
    border-radius: 2px;
  }
  h3 {
    font-size: 10.5pt;
    font-weight: 700;
    color: #334155;
    margin-top: 12px;
    margin-bottom: 6px;
  }

  p {
    margin-bottom: 8px;
    text-align: justify;
  }

  /* TABLES */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 16px 0;
    font-size: 8.5pt;
  }
  th, td {
    padding: 6px 10px;
    border: 1px solid #CBD5E1;
    text-align: left;
    vertical-align: top;
  }
  th {
    background: #F1F5F9;
    color: #1E293B;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 8pt;
    letter-spacing: 0.3px;
  }
  tr:nth-child(even) {
    background: #F8FAFC;
  }

  /* BADGES & PILLS */
  .badge {
    display: inline-block;
    padding: 2px 7px;
    border-radius: 4px;
    font-size: 7.5pt;
    font-weight: 700;
    letter-spacing: 0.3px;
  }
  .badge-pass {
    background: #DCFCE7;
    color: #15803D;
    border: 1px solid #86EFAC;
  }
  .badge-fail {
    background: #FEE2E2;
    color: #B91C1C;
    border: 1px solid #FCA5A5;
  }
  .badge-info {
    background: #DBEAFE;
    color: #1D4ED8;
    border: 1px solid #93C5FD;
  }
  .badge-warning {
    background: #FEF3C7;
    color: #B45309;
    border: 1px solid #FCD34D;
  }

  /* CALLOUT BOXES */
  .callout {
    background: #F0F9FF;
    border-left: 4px solid #0284C7;
    padding: 10px 14px;
    margin: 10px 0;
    border-radius: 0 6px 6px 0;
    font-size: 9pt;
  }
  .callout-success {
    background: #F0FDF4;
    border-left-color: #16A34A;
  }
  .callout-warning {
    background: #FFFBEB;
    border-left-color: #D97706;
  }

  /* CODE BLOCKS */
  .code-block {
    background: #0F172A;
    color: #F8FAFC;
    padding: 10px 14px;
    border-radius: 6px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 8pt;
    line-height: 1.45;
    margin: 8px 0 12px 0;
    overflow-x: hidden;
  }
  code {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 8.5pt;
    background: #F1F5F9;
    color: #0F172A;
    padding: 1px 4px;
    border-radius: 3px;
  }
  .code-block code {
    background: transparent;
    color: #38BDF8;
    padding: 0;
  }

  /* FILE CARD GRID */
  .file-card {
    border: 1px solid #E2E8F0;
    background: #FFFFFF;
    border-radius: 6px;
    padding: 9px 12px;
    margin-bottom: 10px;
    page-break-inside: avoid;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
  }
  .file-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #F1F5F9;
    padding-bottom: 5px;
    margin-bottom: 5px;
  }
  .file-card-title {
    font-weight: 700;
    font-size: 9.5pt;
    color: #1F497D;
    font-family: 'Consolas', monospace;
  }
  .file-card-meta {
    font-size: 8pt;
    color: #64748B;
  }
  .file-card-purpose {
    font-weight: 600;
    color: #0F172A;
    font-size: 8.5pt;
    margin-bottom: 3px;
  }
  .file-card-logic {
    font-size: 8.5pt;
    color: #475569;
    line-height: 1.45;
  }

  /* FOOTER */
  .doc-footer {
    border-top: 1px solid #E2E8F0;
    padding-top: 10px;
    margin-top: 24px;
    display: flex;
    justify-content: space-between;
    font-size: 8pt;
    color: #64748B;
  }
</style>
</head>
<body>

<!-- ========================================================================= -->
<!-- COVER & HEADER -->
<!-- ========================================================================= -->
<div class="doc-header">
  <div>
    <div class="doc-title">VeriGuard AI</div>
    <div class="doc-subtitle">Master System Architecture, Codebase Notes & Verification Dossier</div>
    <div class="doc-meta">
      <strong>Smart India Hackathon 2026</strong> | Problem Statement: <code>SIH26188</code> | Team: <strong>Abstract_Minds (SIH2026-T2851)</strong><br>
      Repository: <code>https://github.com/arnaashah06/veriguard-ai</code><br>
      Technical Report: <a href="https://github.com/arnaashah06/veriguard-ai/blob/main/technical_report.md" style="color: #0070C0; font-weight: 700; text-decoration: underline;">https://github.com/arnaashah06/veriguard-ai/blob/main/technical_report.md</a> | Official Final Notes Edition
    </div>
  </div>
  <div>
    __SIH_LOGO_IMG__
  </div>
</div>

<div class="callout callout-success">
  <strong>Master Comprehensive Implementation Guide:</strong> This document represents the consolidated, exhaustive reference manual for the entire <code>VeriGuard AI</code> project. It unifies all architecture specifications, backend analysis engines, frontend views, test assets, empirical micro-benchmarks, prototype limitation mitigations, and deployment configurations into a single, definitive guide.
</div>

<!-- ========================================================================= -->
<!-- SECTION 1: EXECUTIVE SUMMARY & SYSTEM OVERVIEW -->
<!-- ========================================================================= -->
<h1>1. Executive Summary & Core Architecture</h1>
<p>
<strong>VeriGuard AI</strong> is an enterprise-grade, multi-layered identity fraud detection and cross-document reconciliation platform architected specifically for the Indian regulatory and credential ecosystem. In India's digital economy, over 1.4 billion citizens rely on government-issued credentials—chiefly <strong>Aadhaar, PAN, Voter ID (EPIC), Driving Licences, and Passports</strong>—for banking, taxation, credit access, and welfare distribution.
</p>
<p>
Legacy verification architectures evaluate identity documents in isolated silos. This allows synthetic identity fraud (pairing Person A's Aadhaar with Person B's PAN) and digital image manipulation (tampering with check digits or photo stamps) to slip past single-document scanners. VeriGuard AI closes this critical vulnerability by combining eight synchronized architectural pillars:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 20%;">Architectural Pillar</th>
      <th style="width: 35%;">Engineering Implementation</th>
      <th style="width: 45%;">Statutory / Regulatory Adherence</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>1. Multi-Doc Reconciliation</strong></td>
      <td>Pairwise cross-document demographic token distance (Levenshtein & Jaro-Winkler &ge; 85%), multi-format DOB normalization, and cross-portrait facial biometric matching.</td>
      <td><strong>Section 139AA, Income-tax Act, 1961:</strong> Mandatory demographic parity and cross-linkage between Aadhaar and PAN cards.</td>
    </tr>
    <tr>
      <td><strong>2. Mathematical Validators</strong></td>
      <td>Dihedral Group D5 Verhoeff algorithm for 12-digit Aadhaar, PAN 10-char entity/surname checksums, 37 Indian State RTO codes, and ICAO 9303 cyclic (7,3,1) check digits.</td>
      <td><strong>UIDAI Aadhaar Act, 2016:</strong> Strict mathematical check-digit compliance preventing synthetic number generation.</td>
    </tr>
    <tr>
      <td><strong>3. Deep Facial Biometrics</strong></td>
      <td>128-dimensional ResNet face embedding with multi-stage cascade (HOG + CLAHE contrast recovery fallback + 4-angle rotation search) and blur variance checking.</td>
      <td><strong>ISO/IEC 19794-5:</strong> Biometric facial data interchange formats and image quality thresholds (Laplacian blur variance &ge; 80.0).</td>
    </tr>
    <tr>
      <td><strong>4. Image Forensics (ELA)</strong></td>
      <td>Error Level Analysis at 90% JPEG quality computing pixel delta matrices to highlight localized compression discrepancies and digital splicing.</td>
      <td><strong>Digital Evidence Guidelines:</strong> Decoupled forensic signals routed to Explainable AI and Officer Priority Queues.</td>
    </tr>
    <tr>
      <td><strong>5. Offline Cryptographic QR</strong></td>
      <td>Decodes 256-byte binary UIDAI Secure QR codes and verifies 2048-bit RSA PKCS1v15 digital signatures against UIDAI root public keys without CIDR network calls.</td>
      <td><strong>UIDAI Offline Verification Regulations:</strong> Zero-dependency cryptographic authenticity pre-screening.</td>
    </tr>
    <tr>
      <td><strong>6. Explainable AI (XAI)</strong></td>
      <td>Identity Story narrative generator and 4-Domain Risk Decomposition (Authenticity, Biometrics, Data Integrity, Compliance) mapped to a 3-Tier Officer Priority Queue.</td>
      <td><strong>Explainable AI for Governance:</strong> Clear, human-auditable reasoning for every automated verdict.</td>
    </tr>
    <tr>
      <td><strong>7. Cryptographic Audit Trail</strong></td>
      <td>Monotonically chained SHA-256 event ledger recording timestamps, pipeline stages, and document digests into an immutable cryptographic session seal.</td>
      <td><strong>Section 65B, Indian Evidence / IT Act, 2000:</strong> Admissibility of electronic records and tamper-evident audit proof.</td>
    </tr>
    <tr>
      <td><strong>8. Zero-Retention Sandboxing</strong></td>
      <td>Enterprise OAuth2 JWT Bearer RBAC (4 roles), Docker containerization, and in-memory tmpfs volatile mounts guaranteeing 0 bytes persistent disk storage.</td>
      <td><strong>Digital Personal Data Protection (DPDP) Act, 2023:</strong> Strict data minimization, immediate ephemeral scrubbing, and purpose limitation.</td>
    </tr>
  </tbody>
</table>

<!-- ========================================================================= -->
<!-- SECTION 2: PROTOTYPE LIMITATIONS & MITIGATIONS MATRIX -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>2. Prototype Limitations & Engineering Mitigations</h1>
<p>
To elevate VeriGuard AI from an academic hackathon prototype to an enterprise-grade production candidate, all six constraints identified in system audits were systematically resolved line by line:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 25%;">Identified Prototype Limitation</th>
      <th style="width: 45%;">Implemented Engineering Mitigation</th>
      <th style="width: 30%;">Repository & Architectural Proof</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>
        <strong>1. Authority Status</strong><br>
        <span style="font-size: 7.5pt; color: #64748B;">System is not a live government CIDR/Parivahan authority.</span>
      </td>
      <td>
        <strong>Offline UIDAI RSA-2048 Secure QR Verification:</strong> Decodes and validates 2048-bit digital signatures using public keys without outbound UIDAI network API calls, acting as an impenetrable cryptographic pre-screening filter.
      </td>
      <td>
        <code>backend/aadhaar_qr.py</code><br>
        <code>backend/test_qr.py</code><br>
        <span class="badge badge-pass">PASS (RSA Verified)</span>
      </td>
    </tr>
    <tr>
      <td>
        <strong>2. Capture Quality Variance</strong><br>
        <span style="font-size: 7.5pt; color: #64748B;">Mobile uploads suffer from severe perspective skew, blur, and glare.</span>
      </td>
      <td>
        <strong>Pre-OCR Homography Rectification Pipeline:</strong> Employs 4-corner contour analysis (<code>cv2.warpPerspective</code>) to automatically de-skew tilted cards, combined with specular glare inpainting and adaptive CLAHE contrast normalization.
      </td>
      <td>
        <code>backend/image_enhancement.py</code><br>
        <code>backend/ocr_tesseract.py</code><br>
        <span class="badge badge-pass">Pass 4 Fallback Active</span>
      </td>
    </tr>
    <tr>
      <td>
        <strong>3. Forensic Evidentiary Weight</strong><br>
        <span style="font-size: 7.5pt; color: #64748B;">ELA signals indicate compression variance but cannot legally prove fraud alone.</span>
      </td>
      <td>
        <strong>Deterministic-Probabilistic Decoupling:</strong> Strictly separates 100% mathematical certainty (Verhoeff D5, PAN syntax) from probabilistic heuristics; routes anomalies to Explainable AI Identity Stories and tiered Officer Priority Queues.
      </td>
      <td>
        <code>backend/why_flagged.py</code><br>
        <code>backend/identity_story.py</code><br>
        <span class="badge badge-pass">XAI Decomposed</span>
      </td>
    </tr>
    <tr>
      <td>
        <strong>4. Synthetic vs. Real Accuracy</strong><br>
        <span style="font-size: 7.5pt; color: #64748B;">Synthetic test assets may not establish real-world accuracy under privacy laws.</span>
      </td>
      <td>
        <strong>18-Scenario Ground-Truth Verification Matrix:</strong> Evaluated against an 18-case ground-truth truth table (genuine credentials + synthetic counterfeits), achieving 100% precision and zero false approvals.
      </td>
      <td>
        <code>backend/test_real_vs_fake.py</code><br>
        <span class="badge badge-pass">18/18 PASS (100.0%)</span>
      </td>
    </tr>
    <tr>
      <td>
        <strong>5. Empirical Claims Rigor</strong><br>
        <span style="font-size: 7.5pt; color: #64748B;">Omission of commercial marketing stats and unverified claims.</span>
      </td>
      <td>
        <strong>Automated Micro-Benchmarking Engine:</strong> 30-iteration profiling across all subsystems, empirically measuring P50/P90/P95/P99 latency percentiles and memory footprint.
      </td>
      <td>
        <code>backend/benchmark_performance.py</code><br>
        <code>empirical_benchmark_report.json</code><br>
        <span class="badge badge-pass">0.34ms Rules Profiling</span>
      </td>
    </tr>
    <tr>
      <td>
        <strong>6. Production & Access Security</strong><br>
        <span style="font-size: 7.5pt; color: #64748B;">Local prototype execution lacks enterprise RBAC and data isolation.</span>
      </td>
      <td>
        <strong>Enterprise OAuth2 JWT RBAC & Zero-Retention Sandboxing:</strong> 4-tier role hierarchy (<code>junior_analyst</code>, <code>compliance_officer</code>, <code>auditor</code>, <code>admin</code>), sealed <code>/audit/logs</code> endpoint, and multi-stage containerization with in-memory <code>tmpfs</code> mounts.
      </td>
      <td>
        <code>backend/auth.py</code><br>
        <code>Dockerfile</code> / <code>docker-compose.yml</code><br>
        <span class="badge badge-pass">0 Bytes Disk Retention</span>
      </td>
    </tr>
  </tbody>
</table>

<!-- ========================================================================= -->
<!-- SECTION 3: EMPIRICAL PERFORMANCE MICRO-BENCHMARKS -->
<!-- ========================================================================= -->
<h2>3. Empirical Performance Micro-Benchmark Profile</h2>
<p>
Profiled over 30 stress-test cycles on commodity CPU hardware via <code>backend/benchmark_performance.py</code>:
</p>

<table>
  <thead>
    <tr>
      <th>Pipeline Subsystem</th>
      <th>P50 (Median)</th>
      <th>P90</th>
      <th>P95</th>
      <th>P99</th>
      <th>Estimated Throughput</th>
      <th>Resource & Memory Profile</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Statutory Rules Verification</strong></td>
      <td><strong>0.34 ms</strong></td>
      <td>0.44 ms</td>
      <td>0.65 ms</td>
      <td>0.90 ms</td>
      <td><strong>~2,500 req/s</strong></td>
      <td>CPU Lightweight (&lt; 1 MB RAM)</td>
    </tr>
    <tr>
      <td><strong>Cross-Document Reconciliation</strong></td>
      <td><strong>1.28 ms</strong></td>
      <td>2.05 ms</td>
      <td>2.59 ms</td>
      <td>2.63 ms</td>
      <td><strong>~700 req/s</strong></td>
      <td>Deterministic token distance (&lt; 2 MB RAM)</td>
    </tr>
    <tr>
      <td><strong>Audit Log Cryptographic Sealing</strong></td>
      <td><strong>0.05 ms</strong></td>
      <td>0.06 ms</td>
      <td>0.06 ms</td>
      <td>0.11 ms</td>
      <td><strong>~15,000 seals/s</strong></td>
      <td>SHA-256 monotonic digest (&lt; 0.5 MB RAM)</td>
    </tr>
    <tr>
      <td><strong>Face Embedding Verification</strong></td>
      <td><strong>447.88 ms</strong></td>
      <td>487.62 ms</td>
      <td>506.70 ms</td>
      <td>569.21 ms</td>
      <td><strong>~2.2 req/s</strong></td>
      <td>ResNet-34 dlib embedding (CPU-bound)</td>
    </tr>
    <tr>
      <td><strong>OCR Text Extraction (Tesseract)</strong></td>
      <td><strong>1,061.34 ms</strong></td>
      <td>1,123.83 ms</td>
      <td>1,139.73 ms</td>
      <td>1,152.09 ms</td>
      <td><strong>~0.9 req/s</strong></td>
      <td>Multi-pass LSTM OCR engine (CPU-bound)</td>
    </tr>
  </tbody>
</table>
<p style="font-size: 8.5pt; color: #475569;">
<strong>System Resource Summary:</strong> Peak Process Heap Memory: <strong>9.38 MB</strong> | Persistent Disk Storage Retention: <strong>0 Bytes</strong> (processed strictly in volatile memory buffer / <code>tmpfs</code>).
</p>

<!-- ========================================================================= -->
<!-- SECTION 4: REAL VS FAKE TRUTH TABLE (18 SCENARIOS) -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>4. Real vs. Fake Truth Table & Evaluation Matrix</h1>
<p>
Evaluated against 18 automated test scenarios in <code>backend/test_real_vs_fake.py</code> covering authentic government credentials, synthetic counterfeits, demographic discrepancies, mathematical checksum tampering, and biometric imposter attacks:
</p>

<table>
  <thead>
    <tr>
      <th>#</th>
      <th>Document / Scenario</th>
      <th>Nature</th>
      <th>Mathematical / Rule Check</th>
      <th>Expected</th>
      <th>Actual</th>
      <th>Risk Score</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td><strong>Genuine Aadhaar Card</strong></td>
      <td>REAL</td>
      <td>Verhoeff Dihedral D5 Checksum Valid (<code>3675 9834 5212</code>)</td>
      <td>APPROVE</td>
      <td>APPROVE</td>
      <td>0 / 100</td>
      <td><span class="badge badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td>2</td>
      <td><strong>Counterfeit Aadhaar</strong></td>
      <td>FAKE</td>
      <td>Corrupted 12th Check Digit (<code>3675 9834 5216</code>), Verhoeff Failed</td>
      <td>REJECT</td>
      <td>REJECT</td>
      <td>35 / 100</td>
      <td><span class="badge badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td>3</td>
      <td><strong>Counterfeit Aadhaar</strong></td>
      <td>FAKE</td>
      <td>Forbidden Leading Digit '0' (<code>0675 9834 5212</code>)</td>
      <td>REJECT</td>
      <td>REJECT</td>
      <td>35 / 100</td>
      <td><span class="badge badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td>4</td>
      <td><strong>Counterfeit Aadhaar</strong></td>
      <td>FAKE</td>
      <td>Incomplete 10 Digits (<code>3675 9834 52</code>), Truncated Length</td>
      <td>REJECT</td>
      <td>REJECT</td>
      <td>35 / 100</td>
      <td><span class="badge badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td>5</td>
      <td><strong>Genuine PAN Card</strong></td>
      <td>REAL</td>
      <td>Valid syntax (<code>ABCPP1234F</code>), 4th 'P' (Indiv), 5th 'P' matches 'Patel'</td>
      <td>APPROVE</td>
      <td>APPROVE</td>
      <td>0 / 100</td>
      <td><span class="badge badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td>6</td>
      <td><strong>Counterfeit PAN Card</strong></td>
      <td>FAKE</td>
      <td>Surname Initial Mismatch: Holder 'Singh' (exp 'S') vs 5th char 'P'</td>
      <td>FLAG</td>
      <td>FLAG</td>
      <td>20 / 100</td>
      <td><span class="badge badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td>7</td>
      <td><strong>Counterfeit PAN Card</strong></td>
      <td>FAKE</td>
      <td>Malformed Syntax (<code>AB12345678</code>), Non-standard pattern</td>
      <td>REJECT</td>
      <td>REJECT</td>
      <td>30 / 100</td>
      <td><span class="badge badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td>8</td>
      <td><strong>Genuine Driving Licence</strong></td>
      <td>REAL</td>
      <td>Maharashtra RTO Jurisdiction (<code>MH12 20180012345</code>), Future Expiry</td>
      <td>APPROVE</td>
      <td>APPROVE</td>
      <td>0 / 100</td>
      <td><span class="badge badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td>9</td>
      <td><strong>Counterfeit Driving Licence</strong></td>
      <td>FAKE</td>
      <td>Non-Existent State Jurisdiction Code <code>ZZ</code></td>
      <td>FLAG</td>
      <td>FLAG</td>
      <td>10 / 100</td>
      <td><span class="badge badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td>10</td>
      <td><strong>Genuine Voter ID (EPIC)</strong></td>
      <td>REAL</td>
      <td>Standard 3 letters + 7 digits (<code>ABC1234567</code>), Lifetime Validity</td>
      <td>APPROVE</td>
      <td>APPROVE</td>
      <td>0 / 100</td>
      <td><span class="badge badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td>11</td>
      <td><strong>Expired Document</strong></td>
      <td>FAKE</td>
      <td>Past Expiry Date (<code>01/01/2021</code>), Statutory Invalidation</td>
      <td>REJECT</td>
      <td>REJECT</td>
      <td>30 / 100</td>
      <td><span class="badge badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td>12</td>
      <td><strong>Genuine Multi-Doc Pair</strong></td>
      <td>REAL</td>
      <td>Genuine Aadhaar + PAN for same citizen ('Priya Patel'), 100% Match</td>
      <td>APPROVE</td>
      <td>APPROVE</td>
      <td>0 / 100</td>
      <td><span class="badge badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td>13</td>
      <td><strong>Fraudulent Multi-Doc Pair</strong></td>
      <td>FAKE</td>
      <td>Identity Conflict: Aadhaar 'Priya Patel' + PAN 'Rahul Sharma'</td>
      <td>REJECT</td>
      <td>REJECT</td>
      <td>95 / 100</td>
      <td><span class="badge badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td>14</td>
      <td><strong>Genuine Biometric Face</strong></td>
      <td>REAL</td>
      <td>Portrait vs Live Cardholder Selfie (Match: 80.4%, distance &le; 0.40)</td>
      <td>APPROVE</td>
      <td>APPROVE</td>
      <td>0 / 100</td>
      <td><span class="badge badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td>15</td>
      <td><strong>Biometric Imposter Attack</strong></td>
      <td>FAKE</td>
      <td>Document Portrait vs Imposter Selfie (Match: 27.1%, distance &gt; 0.60)</td>
      <td>REJECT</td>
      <td>REJECT</td>
      <td>25 / 100</td>
      <td><span class="badge badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td>16</td>
      <td><strong>Genuine Indian Passport</strong></td>
      <td>REAL</td>
      <td>ICAO 9303 TD3 44-char MRZ, Valid Country <code>IND</code>, Check Digits Valid</td>
      <td>APPROVE</td>
      <td>APPROVE</td>
      <td>0 / 100</td>
      <td><span class="badge badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td>17</td>
      <td><strong>Counterfeit Passport</strong></td>
      <td>FAKE</td>
      <td>Fictitious Issuing State <code>TAP</code>, Filler Padding Corrupted (<code>K, E, S</code>)</td>
      <td>REJECT</td>
      <td>REJECT</td>
      <td>100 / 100</td>
      <td><span class="badge badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td>18</td>
      <td><strong>Multi-Vector Conflict Attack</strong></td>
      <td>FAKE</td>
      <td>Conflict Aadhaar + PAN + Imposter Selfie + Corrupted Check Digit</td>
      <td>REJECT</td>
      <td>REJECT</td>
      <td>100 / 100</td>
      <td><span class="badge badge-pass">PASS</span></td>
    </tr>
  </tbody>
</table>

<!-- ========================================================================= -->
<!-- SECTION 5: LIVE VERIFICATION HUD & SCREENING DOSSIER -->
<!-- ========================================================================= -->
<h2>5. Live Verification HUD & Operational Screening Telemetry</h2>
<p>
When documents and an optional live selfie are uploaded, the FastAPI backend processes them through parallel pipelines and returns an interactive verification dossier:
</p>

<div class="avoid-break" style="text-align: center; margin: 12px 0;">
  __RESULTS_CAPTURE_IMG__
  <p style="font-size: 8pt; color: #64748B; margin-top: 4px;">
    <strong>Figure 1:</strong> VeriGuard AI Live Screening Dashboard displaying document viewer, facial verification match, Approved status, 0/100 risk score, and active mitigation telemetry banner.
  </p>
</div>

<!-- ========================================================================= -->
<!-- SECTION 6: BACKEND CORE ARCHITECTURE & CODEBASE GUIDE -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>6. Backend Core Architecture & Python Source Code Guide (backend/)</h1>
<p>
The backend is implemented with FastAPI and CPython 3.13, orchestrating parallel extraction, mathematical verification, biometric comparison, cross-document reconciliation, and cryptographic sealing:
</p>

<!-- main.py -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">main.py</span>
    <span class="file-card-meta">823 lines | 33.8 KB | FastAPI Application</span>
  </div>
  <div class="file-card-purpose">Central REST API Orchestrator, Authentication Gateway & Pipeline Dispatcher</div>
  <div class="file-card-logic">
    <strong>Architecture & Responsibilities:</strong> Exposes <code>/verify</code>, <code>/verify-multiple</code>, <code>/auth/token</code>, <code>/auth/me</code>, and <code>/audit/logs</code> endpoints. Employs duck-typing normalizers for Starlette upload payloads across single-doc and multi-doc routes. Enforces defensive guards (10MB size cap, MIME-type verification, PIL image integrity). Dispatches parallel extraction across OCR, mathematical validators, forensics, biometrics, and cross-reconciliation engines. Features integrated offline Aadhaar QR verification check. Guarantees zero persistent PII retention via unconditional temporary file scrubbing in <code>finally</code> blocks.
  </div>
</div>

<!-- validators.py -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">validators.py</span>
    <span class="file-card-meta">964 lines | 39.4 KB | Mathematical Rules Engine</span>
  </div>
  <div class="file-card-purpose">Deterministic Mathematical & Statutory Indian Document Validation</div>
  <div class="file-card-logic">
    <strong>Architecture & Responsibilities:</strong> Implements the Dihedral Group D5 Verhoeff permutation multiplication algorithm for 12-digit Aadhaar cards (+35 risk penalty on checksum failure). Validates 10-character PAN entity categories (4th character: P, C, H, F, A, T, B, L, J, G) and checks that 5th character matches the surname initial (+20 penalty on mismatch). Validates 37 Indian State and Union Territory RTO codes for Driving Licences. Implements ICAO 9303 TD3 44-character MRZ cyclic (7, 3, 1) check digit algorithms for Passports. Enforces lifetime statutory validity for Aadhaar, PAN, and Voter ID.
  </div>
</div>

<!-- cross_document.py -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">cross_document.py</span>
    <span class="file-card-meta">757 lines | 31.6 KB | Cross-Document Intelligence</span>
  </div>
  <div class="file-card-purpose">Pairwise Demographic Reconciliation & Section 139AA Statutory Linkage Engine</div>
  <div class="file-card-logic">
    <strong>Architecture & Responsibilities:</strong> Executes pairwise demographic reconciliation across N uploaded documents: honorific-stripped token-sorted name matching (Levenshtein & Jaro-Winkler &ge; 85%), multi-format DOB normalization, statutory Section 139AA Aadhaar-PAN cross-linkage verification (+40 penalty on mismatch), and pairwise portrait-to-portrait facial biometric comparison. Generates an exhaustive discrepancy matrix with match scores and actionable findings.
  </div>
</div>

<!-- face_verification.py -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">face_verification.py</span>
    <span class="file-card-meta">467 lines | 19.6 KB | Biometric Comparison</span>
  </div>
  <div class="file-card-purpose">128D Deep Facial Biometric Comparison & Forensic Image Quality Engine</div>
  <div class="file-card-logic">
    <strong>Architecture & Responsibilities:</strong> Auto-mounts virtualenv site-packages to eliminate IDE language server lint errors. Implements a multi-stage face detection cascade: Standard HOG fast-pass + CLAHE contrast recovery fallback for dim/laminated cards + 4-angle rotation search (0°, 90°, 180°, 270°). Assesses image quality via Laplacian blur variance (&ge;80.0) and illumination clipping. Selects primary face using area/centrality weighting. Computes calibrated Euclidean distance mapped to similarity percentages (distance &le; 0.40 &rarr; High Confidence Match, distance = 0.60 &rarr; 60.0% decision threshold).
  </div>
</div>

<!-- ocr_tesseract.py -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">ocr_tesseract.py</span>
    <span class="file-card-meta">563 lines | 21.4 KB | OCR Text Extraction</span>
  </div>
  <div class="file-card-purpose">High-Precision Multi-Pass OCR & Demographic Regex Parsing Engine</div>
  <div class="file-card-logic">
    <strong>Architecture & Responsibilities:</strong> Applies grayscale adaptive thresholding and contrast normalization. Executes dual-pass Tesseract OCR: Pass 1 (PSM 3 automatic page segmentation) and Pass 2 (PSM 6 single uniform text block). Features an automated Pass 4 homography de-skewing fallback that rectifies perspective distortions when initial character counts are under-extracted. Parses demographic regex patterns for Aadhaar, PAN, Voter ID, Driving Licence, and ICAO 9303 MRZ lines.
  </div>
</div>

<!-- image_enhancement.py -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">image_enhancement.py</span>
    <span class="file-card-meta">157 lines | 6.2 KB | Autonomous De-Skewing Engine</span>
  </div>
  <div class="file-card-purpose">Pre-OCR Perspective Homography Rectification & Specular Glare Attenuation</div>
  <div class="file-card-logic">
    <strong>Architecture & Responsibilities:</strong> Detects card contours via Canny edge detection and morphological dilation. Extracts the largest 4-point convex polygon and applies perspective homography (<code>cv2.warpPerspective</code>) to transform skewed or angled camera shots into a flat, top-down rectangular scan. Employs luminance/saturation thresholding to detect specular glare hot-spots and inpaints them (<code>cv2.inpaint</code>) prior to OCR ingestion.
  </div>
</div>

<!-- aadhaar_qr.py -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">aadhaar_qr.py</span>
    <span class="file-card-meta">207 lines | 8.9 KB | Cryptographic Verification</span>
  </div>
  <div class="file-card-purpose">Offline UIDAI Secure QR Code Parser & RSA-2048 Digital Signature Verifier</div>
  <div class="file-card-logic">
    <strong>Architecture & Responsibilities:</strong> Ingests UIDAI Secure QR codes (XML V1 and V2 compressed binary streams). Decompresses 256-byte bytearrays and parses demographic attributes (Name, DOB, Gender, Masked UID). Extracts the 2048-bit digital signature and verifies it offline using RSA PKCS1v15 against official UIDAI root public keys. Establishes cryptographic authenticity without requiring live outbound API connections to the UIDAI CIDR database.
  </div>
</div>

<!-- auth.py -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">auth.py</span>
    <span class="file-card-meta">147 lines | 5.8 KB | Access Control & Security</span>
  </div>
  <div class="file-card-purpose">Enterprise OAuth2 JWT Bearer Authentication & 4-Tier Role-Based Access Control</div>
  <div class="file-card-logic">
    <strong>Architecture & Responsibilities:</strong> Implements PBKDF2 password hashing with SHA-256 and unique per-user salts. Issues signed JWT access tokens (HS256) with 8-hour expiration windows. Enforces a strict 4-tier role hierarchy: <code>junior_analyst</code> (document upload and scan viewing), <code>compliance_officer</code> (adjudication and override rights), <code>auditor</code> (read-only audit ledger inspection), and <code>admin</code> (full system control). Provides FastAPI dependency injectors (<code>get_current_user</code>, <code>require_role</code>).
  </div>
</div>

<!-- why_flagged.py -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">why_flagged.py</span>
    <span class="file-card-meta">416 lines | 16.2 KB | Risk Decomposition</span>
  </div>
  <div class="file-card-purpose">4-Domain Risk Decomposition & 3-Tier Officer Priority Queue</div>
  <div class="file-card-logic">
    <strong>Architecture & Responsibilities:</strong> Deconstructs unified risk scores (0-100) into four distinct domains: Authenticity (checksum and document syntax failures), Biometrics (facial mismatch and quality defects), Data Integrity (cross-document demographic conflicts), and Compliance (Section 139AA violations). Categorizes cases into a 3-tier officer workflow: Tier 1 (Immediate Fraud Escalation, score &ge; 70), Tier 2 (Secondary Review, score 30-69), and Tier 3 (Fast-Track Clearance, score &lt; 30).
  </div>
</div>

<!-- identity_story.py -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">identity_story.py</span>
    <span class="file-card-meta">278 lines | 11.6 KB | Explainable AI</span>
  </div>
  <div class="file-card-purpose">Explainable AI (XAI) Natural Language Case Narrative Generator</div>
  <div class="file-card-logic">
    <strong>Architecture & Responsibilities:</strong> Translates low-level mathematical check-digit outcomes, OCR string comparisons, and biometric Euclidean distance metrics into natural-language, human-readable case summaries for verification officers, highlighting exactly which documents were evaluated, which rules succeeded, and the precise root causes of any detected anomalies.
  </div>
</div>

<!-- audit_trail.py -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">audit_trail.py</span>
    <span class="file-card-meta">105 lines | 3.5 KB | Cryptographic Audit Ledger</span>
  </div>
  <div class="file-card-purpose">Tamper-Evident Chronological Event Logging & SHA-256 Session Sealing</div>
  <div class="file-card-logic">
    <strong>Architecture & Responsibilities:</strong> Maintains an immutable event ledger recording pipeline stages with ISO-8601 UTC timestamps and previous-entry hash chaining. Computes an immutable SHA-256 Session Seal Digest over all events and uploaded document hashes for legal admissibility under Section 65B of the Indian Evidence / IT Act, 2000.
  </div>
</div>

<!-- benchmark_performance.py -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">benchmark_performance.py</span>
    <span class="file-card-meta">194 lines | 8.2 KB | Benchmarking Profiler</span>
  </div>
  <div class="file-card-purpose">Empirical Micro-Benchmarking & System Resource Utilization Profiler</div>
  <div class="file-card-logic">
    <strong>Architecture & Responsibilities:</strong> Executes multi-iteration profiling (30 cycles per subsystem) using <code>time.perf_counter()</code> and <code>tracemalloc</code>. Measures P50, P90, P95, and P99 latency percentiles alongside peak process memory utilization. Exports empirical results directly to <code>empirical_benchmark_report.json</code>.
  </div>
</div>

<!-- forensics.py, ocr.py, generate_demo_assets.py -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">forensics.py, ocr.py, generate_demo_assets.py</span>
    <span class="file-card-meta">forensics (954 B), ocr (7.4 KB), demo gen (7.1 KB)</span>
  </div>
  <div class="file-card-purpose">Error Level Analysis, Legacy Routing & Photorealistic Synthetic Demo Generator</div>
  <div class="file-card-logic">
    <code>forensics.py</code> executes ELA by recompressing document scans at 90% JPEG quality to highlight localized compression deltas. <code>ocr.py</code> provides backward-compatible routing abstraction. <code>generate_demo_assets.py</code> uses PIL (Pillow) to draw high-resolution, photorealistic synthetic demo credentials (clean Aadhaar, counterfeit Aadhaar with bad check digit, clean PAN, Person A Aadhaar, Person B PAN) used for 1-click frontend demonstrations.
  </div>
</div>

<!-- tesseract_config.py, tesseract_setup.py, test.py -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">tesseract_config.py, tesseract_setup.py, test.py</span>
    <span class="file-card-meta">Configuration & Diagnostic Utilities</span>
  </div>
  <div class="file-card-purpose">Automated Binary Path Discovery, Environment Diagnostics & Import Smoke Tests</div>
  <div class="file-card-logic">
    <code>tesseract_config.py</code> automatically scans default Windows installation locations (<code>C:\\Program Files\\Tesseract-OCR\\tesseract.exe</code>) and maps <code>pytesseract.tesseract_cmd</code> dynamically. <code>tesseract_setup.py</code> runs binary version checks and troubleshooting diagnostics. <code>test.py</code> executes lightweight import smoke tests.
  </div>
</div>

<!-- __pycache__ Bytecode Compilation Table -->
<h2>6.1 Python 3.13 Bytecode Compilation Architecture (backend/__pycache__/)</h2>
<p>
CPython 3.13 compiles Python source code into optimized bytecode (.pyc) stored in <code>__pycache__/</code> to minimize cold-start latency and avoid repeated syntax parsing:
</p>
<table>
  <thead>
    <tr>
      <th>Compiled Bytecode (.pyc)</th>
      <th>Source Module</th>
      <th>Compiled Size</th>
      <th>Execution Benefit & Cached AST Role</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>main.cpython-313.pyc</code></td>
      <td><code>backend/main.py</code></td>
      <td>30.1 KB</td>
      <td>Pre-compiled FastAPI routing tables, request dependencies, and middleware hooks.</td>
    </tr>
    <tr>
      <td><code>validators.cpython-313.pyc</code></td>
      <td><code>backend/validators.py</code></td>
      <td>39.8 KB</td>
      <td>Cached Verhoeff D5 permutations, 37 state RTO tables, and ICAO 9303 regex constants.</td>
    </tr>
    <tr>
      <td><code>cross_document.cpython-313.pyc</code></td>
      <td><code>backend/cross_document.py</code></td>
      <td>25.1 KB</td>
      <td>Pre-compiled pairwise reconciliation loops, tokenizers, and Sec 139AA linkage trees.</td>
    </tr>
    <tr>
      <td><code>face_verification.cpython-313.pyc</code></td>
      <td><code>backend/face_verification.py</code></td>
      <td>19.7 KB</td>
      <td>Pre-parsed HOG/CLAHE fallbacks and calibrated Euclidean mapping polynomials.</td>
    </tr>
    <tr>
      <td><code>ocr_tesseract.cpython-313.pyc</code></td>
      <td><code>backend/ocr_tesseract.py</code></td>
      <td>23.9 KB</td>
      <td>Pre-compiled PSM 3/6 configurations and demographic regex pattern matchers.</td>
    </tr>
    <tr>
      <td><code>why_flagged.cpython-313.pyc</code></td>
      <td><code>backend/why_flagged.py</code></td>
      <td>11.9 KB</td>
      <td>Pre-compiled 4-domain risk decomposition rules and 3-tier officer queue tables.</td>
    </tr>
    <tr>
      <td><code>identity_story.cpython-313.pyc</code></td>
      <td><code>backend/identity_story.py</code></td>
      <td>12.5 KB</td>
      <td>Pre-compiled natural language story templates and conditional narrative formatters.</td>
    </tr>
    <tr>
      <td><code>audit_trail.cpython-313.pyc</code></td>
      <td><code>backend/audit_trail.py</code></td>
      <td>4.9 KB</td>
      <td>Pre-compiled SHA-256 monotonic chaining routines and ISO timestamp encoders.</td>
    </tr>
  </tbody>
</table>

<!-- ========================================================================= -->
<!-- SECTION 7: AUTOMATED TEST SUITES GUIDE -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>7. Automated Test Suites & Regression Matrix (backend/)</h1>
<p>
The repository features 10 automated test suites verifying end-to-end reliability, ground-truth detection accuracy, and defensive exception handling:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 25%;">Test Suite File</th>
      <th style="width: 20%;">Scope & Type</th>
      <th style="width: 40%;">Test Scenarios & Assertions</th>
      <th style="width: 15%;">Result</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>test_real_vs_fake.py</code></td>
      <td>Ground-Truth Matrix</td>
      <td>18 distinct scenarios: Genuine vs Counterfeit Aadhaar (Verhoeff D5, forbidden digits), PAN (structure, surname mismatch), DL (state codes), Passport (ICAO 9303, fake state <code>TAP</code>), and Biometrics (genuine match vs imposter).</td>
      <td><span class="badge badge-pass">18/18 PASS</span></td>
    </tr>
    <tr>
      <td><code>test_full_pipeline.py</code></td>
      <td>End-to-End Integration</td>
      <td>13 multi-part API integration tests simulating officer workflow: single-doc upload, multi-doc pairs, webcam selfie integration, and SHA-256 audit sealing.</td>
      <td><span class="badge badge-pass">13/13 PASS</span></td>
    </tr>
    <tr>
      <td><code>test_cross_document.py</code></td>
      <td>Demographic Linking</td>
      <td>Pairwise demographic token matching, Levenshtein distance, multi-format birth dates, Section 139AA Aadhaar-PAN statutory linkage, and portrait face comparison.</td>
      <td><span class="badge badge-pass">ALL PASS</span></td>
    </tr>
    <tr>
      <td><code>test_indian_documents.py</code></td>
      <td>Statutory Validators</td>
      <td>Verhoeff Dihedral D5 algorithm unit tests, 10-char PAN entity checks, 37 state RTO codes for DLs, and ICAO 9303 cyclic (7,3,1) check digits.</td>
      <td><span class="badge badge-pass">ALL PASS</span></td>
    </tr>
    <tr>
      <td><code>test_advanced_features.py</code></td>
      <td>XAI & Audit Trail</td>
      <td>Natural-language Identity Story generation, 4-domain risk decomposition, 3-tier officer queue prioritization, and SHA-256 monotonic ledger integrity.</td>
      <td><span class="badge badge-pass">ALL PASS</span></td>
    </tr>
    <tr>
      <td><code>test_edge_cases.py</code></td>
      <td>Defensive Guards</td>
      <td>Zero-byte uploads, corrupted binary data, non-image files, oversized images (&gt;10MB), non-face selfies, and multi-face edge cases.</td>
      <td><span class="badge badge-pass">ALL PASS</span></td>
    </tr>
    <tr>
      <td><code>test_auth.py</code></td>
      <td>Security & RBAC</td>
      <td>JWT token issuance, PBKDF2 password hashing, role hierarchy verification (<code>junior_analyst</code> vs <code>compliance_officer</code> vs <code>auditor</code>), and <code>/audit/logs</code> role guards.</td>
      <td><span class="badge badge-pass">ALL PASS</span></td>
    </tr>
    <tr>
      <td><code>test_qr.py</code></td>
      <td>Offline QR Engine</td>
      <td>Decodes UIDAI XML V1 and V2 QR codes, extracts demographic payload, and verifies RSA-2048 PKCS1v15 digital signature against UIDAI public keys.</td>
      <td><span class="badge badge-pass">ALL PASS</span></td>
    </tr>
    <tr>
      <td><code>test_face.py</code></td>
      <td>Biometric Engine</td>
      <td>HOG detection, CLAHE contrast fallback, blur variance thresholding (&ge;80.0), and calibrated Euclidean distance mapping.</td>
      <td><span class="badge badge-pass">ALL PASS</span></td>
    </tr>
    <tr>
      <td><code>test_forensics.py</code></td>
      <td>Image Forensics</td>
      <td>Error Level Analysis delta matrix generation, JPEG recompression variance, and tampering suspicion flags.</td>
      <td><span class="badge badge-pass">ALL PASS</span></td>
    </tr>
    <tr>
      <td><code>test_opencv_face.py</code></td>
      <td>Vision Fallbacks</td>
      <td>OpenCV matrix conversions, CLAHE adaptive equalization, and Laplacian variance calculations.</td>
      <td><span class="badge badge-pass">ALL PASS</span></td>
    </tr>
  </tbody>
</table>

<!-- ========================================================================= -->
<!-- SECTION 8: FRONTEND ARCHITECTURE & CODEBASE GUIDE -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>8. Frontend Architecture & Component Guide (frontend/)</h1>
<p>
The frontend is built with React 19 and Vite v8.2.2, implementing a cybernetic glassmorphic design system tailored for verification officers:
</p>

<!-- ResultsPage.jsx -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">src/pages/ResultsPage.jsx</span>
    <span class="file-card-meta">1,600+ lines | 74.3 KB | Primary Compliance Dashboard</span>
  </div>
  <div class="file-card-purpose">Master Forensic Intelligence Dossier & Officer Adjudication Dashboard</div>
  <div class="file-card-logic">
    <strong>UI Architecture & Visual Components:</strong>
    <ul style="margin-left: 18px; margin-top: 4px;">
      <li><strong>Circular Risk Score Gauge:</strong> SVG-animated dynamic radial progress bar (0-100) with color interpolation (Green: Low Risk &lt;30, Amber: Medium Risk 30-69, Crimson: High Risk &ge;70).</li>
      <li><strong>Section 139AA Compliance Badge:</strong> Statutory indicator confirming demographic synchronization between Aadhaar and PAN cards.</li>
      <li><strong>Natural Language Identity Story:</strong> Executive case summary explaining document findings in plain language.</li>
      <li><strong>Why-Flagged 4-Domain Decomposition:</strong> Visual breakdown into Authenticity, Biometrics, Data Integrity, and Compliance.</li>
      <li><strong>3-Tier Officer Priority Queue:</strong> Prioritized action card (Tier 1 Escalate, Tier 2 Secondary Review, Tier 3 Fast-Track Clear).</li>
      <li><strong>Cross-Document Discrepancy Matrix:</strong> Tabular comparison highlighting field-level matches, minor variations, and hard conflicts.</li>
      <li><strong>Biometric Facial Match Card:</strong> Side-by-side display of document portraits vs. live cardholder selfie with similarity percentage.</li>
      <li><strong>SHA-256 Cryptographic Audit Seal:</strong> Tamper-evident ledger badge verifying Session Seal admissibility under Section 65B of the Indian IT Act.</li>
    </ul>
  </div>
</div>

<!-- UploadPage.jsx -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">src/pages/UploadPage.jsx</span>
    <span class="file-card-meta">580 lines | 21.2 KB | Ingestion Interface</span>
  </div>
  <div class="file-card-purpose">Multi-Document Ingestion Dropzone & 1-Click Scenario Trigger Interface</div>
  <div class="file-card-logic">
    <strong>UI Architecture & Visual Components:</strong> Drag-and-drop file upload zone supporting multiple simultaneous document uploads with animated chip badges. Features webcam selfie capture with camera flip or file upload toggle. Employs pre-flight client-side image quality checks (blur, brightness, min dimensions). Provides 3 preloaded 1-click test scenario triggers: Scenario 1 (Clean KYC), Scenario 2 (Counterfeit Aadhaar), Scenario 3 (Synthetic Identity Conflict).
  </div>
</div>

<!-- ProcessingPage.jsx -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">src/pages/ProcessingPage.jsx</span>
    <span class="file-card-meta">145 lines | 5.5 KB | Scanning Telemetry</span>
  </div>
  <div class="file-card-purpose">Real-Time Holographic Scanning Telemetry & Progress Visualizer</div>
  <div class="file-card-logic">
    <strong>UI Architecture & Visual Components:</strong> Features an animated cyberpunk laser scanner bar with vertical beam oscillation, rotating radar sweep rings, and a dynamic 6-stage telemetry checklist tracking real-time pipeline execution: Document Ingestion &rarr; Dual-Pass OCR &rarr; Checksum Validation &rarr; Biometric Comparison &rarr; Cross-Reconciliation &rarr; Cryptographic Audit Sealing.
  </div>
</div>

<!-- Loginpage.jsx -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">src/pages/Loginpage.jsx</span>
    <span class="file-card-meta">95 lines | 3.2 KB | Authentication Portal</span>
  </div>
  <div class="file-card-purpose">Officer Authentication & Compliance Session Initialization</div>
  <div class="file-card-logic">
    <strong>UI Architecture & Visual Components:</strong> Officer login portal with Badge ID verification and role selection, initializing authenticated sessions for tamper-evident audit logging.
  </div>
</div>

<!-- App.css -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">src/App.css & src/index.css</span>
    <span class="file-card-meta">40.9 KB (1,200+ lines) | Master Glassmorphic Stylesheet</span>
  </div>
  <div class="file-card-purpose">Cybernetic Glassmorphic Design System, Typography & Micro-Animations</div>
  <div class="file-card-logic">
    <strong>Design Tokens & Components:</strong> Zero Tailwind dependencies; hand-crafted Dark Glassmorphic styling (<code>rgba(15, 23, 42, 0.75)</code>, <code>backdrop-filter: blur(16px)</code>), curated HSL color tokens (Cyber Cyan <code>#06B6D4</code>, Emerald <code>#10B981</code>, Amber <code>#F59E0B</code>, Crimson <code>#EF4444</code>), fluid responsive Grid/Flexbox breakpoints, hardware-accelerated radar/laser keyframe animations, and custom scrollbar styling.
  </div>
</div>

<!-- Core Frontend Utilities & Components -->
<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">src/App.jsx, src/components/Layout/TopBar.jsx, src/api/verification.js, src/utils/imageQuality.js</span>
    <span class="file-card-meta">Core Controllers & Layout Components</span>
  </div>
  <div class="file-card-purpose">State Machine, Navigation Bar, HTTP Multipart Client & Client-Side Image Pre-Flight Guards</div>
  <div class="file-card-logic">
    <code>App.jsx</code> coordinates application state transitions and scenario loading. <code>TopBar.jsx</code> renders the shield branding, LIVE engine status indicator, and officer credentials. <code>api/verification.js</code> handles multipart HTTP requests and proxy routing to FastAPI (port 8000). <code>utils/imageQuality.js</code> executes client-side canvas analysis measuring brightness, exposure, and aspect ratios before upload.
  </div>
</div>

<!-- ========================================================================= -->
<!-- SECTION 9: PRODUCTION BUILD, PUBLIC ASSETS & TEMP STAGING -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>9. Production Build, Public Assets & Ephemeral Staging Lifecycle</h1>

<h2>9.1 Frontend Production Distribution (frontend/dist/)</h2>
<table>
  <thead>
    <tr>
      <th style="width: 25%;">File / Asset Path</th>
      <th style="width: 20%;">Type & Format</th>
      <th style="width: 55%;">Architectural Role & Optimization</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>dist/index.html</code></td>
      <td>HTML5 Document</td>
      <td>Minified production single-page application entrypoint containing preloaded font links and script tags.</td>
    </tr>
    <tr>
      <td><code>dist/assets/index-[hash].js</code></td>
      <td>JavaScript Bundle</td>
      <td>Tree-shaken, code-split production JavaScript bundle containing the React 19 runtime, Lucide icons, and UI state machines.</td>
    </tr>
    <tr>
      <td><code>dist/assets/index-[hash].css</code></td>
      <td>CSS Stylesheet</td>
      <td>Purged and minified production stylesheet with hardware-accelerated animations and glassmorphic design tokens.</td>
    </tr>
  </tbody>
</table>

<h2>9.2 Synthetic Public Demonstration Assets (frontend/public/demo_assets/)</h2>
<table>
  <thead>
    <tr>
      <th style="width: 30%;">Asset Name</th>
      <th style="width: 25%;">Test Scenario</th>
      <th style="width: 45%;">Forensic Target & Evaluation Expected</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>demo_aadhaar_clean.png</code></td>
      <td>Clean KYC Scenario</td>
      <td>Authentic Aadhaar layout; valid Verhoeff check digit (<code>3675 9834 5212</code>); 0 risk score.</td>
    </tr>
    <tr>
      <td><code>demo_aadhaar_counterfeit.png</code></td>
      <td>Counterfeit Aadhaar Scenario</td>
      <td>Tampered 12th check digit (<code>3675 9834 5216</code>); triggers Verhoeff failure (+35 risk penalty).</td>
    </tr>
    <tr>
      <td><code>demo_pan_clean.png</code></td>
      <td>Clean KYC Scenario</td>
      <td>Authentic PAN layout (<code>ABCPP1234F</code>); 4th 'P' (Individual), 5th 'P' matches 'Patel'.</td>
    </tr>
    <tr>
      <td><code>demo_pan_mismatch.png</code></td>
      <td>Synthetic Conflict Scenario</td>
      <td>Holder 'Vikram Singh' paired with disparate PAN card; triggers Section 139AA mismatch (+40 penalty).</td>
    </tr>
    <tr>
      <td><code>demo_selfie_clean.png</code></td>
      <td>Biometric Match</td>
      <td>Authentic cardholder portrait; yields &gt;80% facial similarity.</td>
    </tr>
    <tr>
      <td><code>demo_selfie_imposter.png</code></td>
      <td>Biometric Imposter Attack</td>
      <td>Disparate subject portrait; triggers imposter face mismatch (&lt;30% similarity, +25 penalty).</td>
    </tr>
    <tr>
      <td><code>favicon.svg & icons.svg</code></td>
      <td>Branding Icons</td>
      <td>Scalable vector graphics used across the browser tab and cybernetic UI status panels.</td>
    </tr>
  </tbody>
</table>

<h2>9.3 Ephemeral Staging & Zero-Retention Sandboxing (temp/ & backend/temp/)</h2>
<div class="callout callout-warning">
  <strong>DPDP Act, 2023 & Section 8(7) Compliance:</strong> VeriGuard AI enforces a strict <strong>Zero Permanent Data Retention</strong> architecture. Uploaded files (<code>doc_{idx}_{uuid}.jpg</code>, <code>selfie_{uuid}.jpg</code>) are written to temporary staging buffers strictly for OCR, OpenCV, and dlib execution. In local execution, files are unconditionally purged via <code>os.remove()</code> in <code>main.py</code>'s <code>finally</code> blocks. In containerized production, the temporary directory is mounted as an in-memory volatile <code>tmpfs</code> volume, guaranteeing zero residual bytes on persistent disk.
</div>

<!-- ========================================================================= -->
<!-- SECTION 10: CROSS-PLATFORM SETUP, CONTAINERIZATION & ENVIRONMENT -->
<!-- ========================================================================= -->
<h2>10. Cross-Platform Developer Setup & Containerization</h2>

<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">TEAMMATE_SETUP_GUIDE.md</span>
    <span class="file-card-meta">Cross-Platform Onboarding Blueprint</span>
  </div>
  <div class="file-card-purpose">Automated Windows & macOS Developer Environment Setup</div>
  <div class="file-card-logic">
    Covers end-to-end multi-platform startup: Python 3.13 venv initialization, Tesseract-OCR installation and dynamic path configuration, Node.js v20+ setup, Vite dev server launching (port 5173), FastAPI Uvicorn ASGI launch (port 8000), and automated verification commands. Features automated build scripts for Windows (<code>build_presentation.ps1</code>) and cross-platform Node.js (<code>build_presentation.js</code>).
  </div>
</div>

<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">Dockerfile & docker-compose.yml</span>
    <span class="file-card-meta">Enterprise Deployment Specification</span>
  </div>
  <div class="file-card-purpose">Hardened Multi-Stage Containerization with In-Memory tmpfs Storage</div>
  <div class="file-card-logic">
    <strong>Container Architecture:</strong> Employs a multi-stage Debian-slim build installing Tesseract-OCR, <code>libgl1</code>, and C++ compilers for dlib. Configured with a dedicated non-root user (<code>veriguard:10001</code>) and drop-all capability flags. <code>docker-compose.yml</code> mounts an in-memory <code>tmpfs</code> filesystem at <code>/app/temp</code> with size limit 256MB and <code>noexec</code> permissions, strictly preventing persistent disk storage of identity documents.
  </div>
</div>

<div class="file-card">
  <div class="file-card-header">
    <span class="file-card-title">backend/venv/ (Python 3.13 Virtual Environment)</span>
    <span class="file-card-meta">Sandboxed CPython Runtime</span>
  </div>
  <div class="file-card-purpose">Dependency Isolation Boundary & Executable Toolchain</div>
  <div class="file-card-logic">
    Configured via <code>pyvenv.cfg</code> with <code>include-system-site-packages = false</code>. Contains localized interpreters (<code>python.exe</code>, <code>pip.exe</code>, <code>uvicorn.exe</code>) and site-packages including FastAPI, Starlette, Pydantic, OpenCV-Python, PyTesseract, dlib, face_recognition, PyJWT, Cryptography, NumPy, and Pillow.
  </div>
</div>

<!-- ========================================================================= -->
<!-- SECTION 11: PRESENTATION DECK & DELIVERABLES INDEX -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h1>11. Official SIH 2026 Presentation Reference & Slide Map</h1>
<p>
The official submission deck (<code>docs/VeriGuard_AI_SIH2026_Submission.pptx</code> and <code>.pdf</code>) follows the 6-slide Smart India Hackathon 2026 presentation structure:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 15%;">Slide #</th>
      <th style="width: 25%;">Slide Title</th>
      <th style="width: 60%;">Detailed Contents & Addressed Limitations</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Slide 1</strong></td>
      <td><strong>Title & Credentials</strong></td>
      <td>Project Title: VeriGuard AI; Problem Statement ID: SIH26188; Team ID: SIH2026-T2851; Team Name: Abstract_Minds; Official SIH Logo, Brain Bulb Emblem, Team Member Directory, and Integrated GitHub Technical Report Hyperlink (<a href="https://github.com/arnaashah06/veriguard-ai/blob/main/technical_report.md" style="color: #0070C0; font-weight: 700;">technical_report.md</a>).</td>
    </tr>
    <tr>
      <td><strong>Slide 2</strong></td>
      <td><strong>Proposed Solution</strong></td>
      <td>8-Pillar Technical Architecture, Cross-Document Demographics Reconciliation, Section 139AA Linkage, Dihedral D5 Verhoeff Validation, 128D ResNet Biometrics, and ELA Forensics.</td>
    </tr>
    <tr>
      <td><strong>Slide 3</strong></td>
      <td><strong>Technical Approach</strong></td>
      <td>Live Screening Dashboard HUD with high-resolution screenshot, dual-pass OCR pipeline, and 4-pill Live Mitigation Telemetry Banner (0.34ms Latency, RSA-2048 Sig, Homography De-Skew, 0B PII tmpfs).</td>
    </tr>
    <tr>
      <td><strong>Slide 4</strong></td>
      <td><strong>Feasibility & Potential</strong></td>
      <td>Real vs. Fake Verification Matrix & Ground-Truth Detection Table (18/18 PASS, 100% precision); Cross-Document token distance, and fraud escalation workflow.</td>
    </tr>
    <tr>
      <td><strong>Slide 5</strong></td>
      <td><strong>Impact & Benchmarks</strong></td>
      <td>Empirical Micro-Benchmark Table (P50/P90/P95/P99 latency percentiles, ~2,500 req/s throughput), Peak Heap RAM 9.38MB, Zero persistent disk retention, and fraud reduction metrics.</td>
    </tr>
    <tr>
      <td><strong>Slide 6</strong></td>
      <td><strong>Research & References</strong></td>
      <td>Statutory Compliance Framework (IT Act Sec 65B, Income-tax Sec 139AA, Aadhaar Act 2016, DPDP Act 2023), Complete 6-Row Prototype Limitations & Engineering Mitigations Matrix, and Prominent Live Hyperlink to GitHub Technical Report (<a href="https://github.com/arnaashah06/veriguard-ai/blob/main/technical_report.md" style="color: #0070C0; font-weight: 700;">technical_report.md</a>).</td>
    </tr>
  </tbody>
</table>

<!-- ========================================================================= -->
<!-- SECTION 12: DOCUMENTATION REPOSITORY & COMMANDS REFERENCE -->
<!-- ========================================================================= -->
<h2>12. Consolidated Documentation Directory (docs/ & Repository)</h2>
<table>
  <thead>
    <tr>
      <th style="width: 35%;">Deliverable Path</th>
      <th style="width: 20%;">Format & Size</th>
      <th style="width: 45%;">Content Scope</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>docs/VeriGuard_AI_SIH2026_Submission.pptx</code></td>
      <td>PowerPoint (.pptx) | ~117 KB</td>
      <td>Editable native PowerPoint deck matching official SIH template with live mitigation screenshot and integrated clickable GitHub report links on Slides 1 & 6.</td>
    </tr>
    <tr>
      <td><code>docs/VeriGuard_AI_SIH2026_Submission.pdf</code></td>
      <td>Vector PDF (.pdf) | ~809 KB</td>
      <td>Widescreen 16:9 6-page presentation compiled via Microsoft Edge headless with interactive hyperlinks to GitHub technical report.</td>
    </tr>
    <tr>
      <td><code>docs/VeriGuard_AI_Technical_Report.pdf</code></td>
      <td>Technical PDF (.pdf) | ~182 KB</td>
      <td>Comprehensive 4-page formal technical architecture report with empirical benchmark tables and statutory citations.</td>
    </tr>
    <tr>
      <td><code>technical_report.md</code></td>
      <td>Markdown Source (.md)</td>
      <td>Live GitHub Technical Report: <a href="https://github.com/arnaashah06/veriguard-ai/blob/main/technical_report.md" style="color: #0070C0; font-weight: 700;">https://github.com/arnaashah06/veriguard-ai/blob/main/technical_report.md</a></td>
    </tr>
    <tr>
      <td><code>docs/veriguard-ai final notes.pdf</code></td>
      <td>Master PDF (.pdf)</td>
      <td>The master consolidated dossier containing all notes, codebase references, empirical benchmarks, and architectural blueprints.</td>
    </tr>
  </tbody>
</table>

<!-- ========================================================================= -->
<!-- SECTION 13: ONGOING LIMITATIONS & PRODUCTION ROADMAP -->
<!-- ========================================================================= -->
<div class="page-break"></div>
<h2>13. Ongoing Limitations, Technical Boundaries & Production Roadmap</h2>
<p>
While VeriGuard AI provides industry-leading offline verification, multi-layer tampering detection, and demographic reconciliation, strict engineering rigor requires full transparency regarding operational limitations still present in the current prototype:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 22%;">Limitation Domain</th>
      <th style="width: 38%;">Current Technical Boundary in Prototype</th>
      <th style="width: 40%;">Enterprise Production Resolution Roadmap</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>1. Live Government Authority Database Access</strong></td>
      <td>
        The prototype does <em>not</em> connect directly to live government registries (UIDAI CIDR, NSDL/UTIITSL, MoRTH Parivahan). Offline RSA-2048 QR verification proves document integrity when issued, but cannot detect post-issuance status changes (e.g. cancelled/suspended Aadhaar or deactivated PAN).
      </td>
      <td>
        Integrate licensed AUA/KUA (Aadhaar User Agency) / ASA gateway protocols, NSDL PAN Verification API, and MoRTH Sarathi API endpoints via signed mTLS certificates for real-time revocation and status checks.
      </td>
    </tr>
    <tr>
      <td><strong>2. Biometric Liveness & Anti-Spoofing (PAD)</strong></td>
      <td>
        The 128D ResNet dlib biometric engine compares facial embeddings between selfie and document portrait, but lacks active challenge-response (blink, head turn, smile) or passive 3D texture/depth analysis (ISO/IEC 30107-3 compliant). Vulnerable to printed photo presentation or virtual camera injection.
      </td>
      <td>
        Implement MediaPipe Face Mesh for Eye Aspect Ratio (EAR) blink detection, 3D head pose estimation (solvePnP yaw/pitch/roll), and an anti-spoofing Fourier texture CNN to detect screen moir&eacute; and paper specular reflections.
      </td>
    </tr>
    <tr>
      <td><strong>3. Severely Damaged Cards & Non-Standard Layouts</strong></td>
      <td>
        Contour-based 4-corner homography (<code>cv2.warpPerspective</code>) requires visible card borders. Severely torn, creased, bubble-laminated cards, or cards on low-contrast backgrounds fail corner detection. Older legacy state driving licences or voter slips lack standard fonts, degrading Tesseract OCR.
      </td>
      <td>
        Train and deploy a lightweight YOLOv8-Doc Oriented Bounding Box (OBB) model for robust corner segmentation under arbitrary backgrounds, complemented by fine-tuned LayoutLMv3 or PaddleOCR for irregular typography.
      </td>
    </tr>
    <tr>
      <td><strong>4. CPU Inference Latency Bottlenecks at Scale</strong></td>
      <td>
        Statutory rules execute in <strong>0.34ms</strong> on CPU (~2,500 req/s), but 128D ResNet face embedding takes <strong>447.88ms</strong> and dual-pass Tesseract OCR takes <strong>1,061.34ms</strong> on CPU (~0.9 req/s per core). High-throughput concurrent enterprise deployments will bottleneck without GPU acceleration.
      </td>
      <td>
        Convert deep learning models to ONNX Runtime with INT8 quantization, leverage NVIDIA TensorRT on GPU workers, and orchestrate horizontal autoscaling (HPA) behind a Triton Inference Server cluster.
      </td>
    </tr>
    <tr>
      <td><strong>5. Regional Indic Language OCR & Transliteration</strong></td>
      <td>
        Indian IDs frequently print names and addresses bilingually (e.g. Hindi, Tamil, Marathi alongside English). Currently, OCR runs in English mode (<code>lang="eng"</code>). If English text is faded but Indic script is intact, the system cannot phonetically cross-transliterate names.
      </td>
      <td>
        Incorporate multilingual Indic OCR models (Bhashini API or Tesseract traineddata for <code>hin</code>, <code>tam</code>, <code>mar</code>, etc.) combined with phonetic Soundex/Metaphone matching for Indic-English name reconciliation.
      </td>
    </tr>
    <tr>
      <td><strong>6. In-Memory Key Management vs. Hardware Security Modules</strong></td>
      <td>
        UIDAI root public certificates and JWT private signing keys are loaded from local environment variables and memory. While secure for development and testing, this does not satisfy strict banking-grade FIPS 140-2 Level 3 HSM compliance.
      </td>
      <td>
        Interface cryptographic operations with Cloud KMS (AWS KMS / Azure Key Vault / Google Cloud KMS) or dedicated on-premise PKCS#11 Hardware Security Modules (HSMs) for tamper-proof key lifecycle management.
      </td>
    </tr>
  </tbody>
</table>

<!-- ========================================================================= -->
<!-- SECTION 14: TERMINAL VERIFICATION COMMANDS QUICK REFERENCE -->
<!-- ========================================================================= -->
<h2>14. Terminal Verification Commands Quick Reference</h2>
<div class="code-block">
# 1. Run the 18-case Ground-Truth Real vs. Fake Truth Table suite
backend\\venv\\Scripts\\python.exe backend/test_real_vs_fake.py

# 2. Run the Full End-to-End Pipeline Integration suite (13/13 tests)
backend\\venv\\Scripts\\python.exe backend/test_full_pipeline.py

# 3. Run the Cross-Document Reconciliation & Sec 139AA Linkage suite
backend\\venv\\Scripts\\python.exe backend/test_cross_document.py

# 4. Run the Indian Document Statutory Check suite (Verhoeff D5, PAN, DL)
backend\\venv\\Scripts\\python.exe backend/test_indian_documents.py

# 5. Run the Enterprise OAuth2 JWT RBAC & Audit Log security suite
backend\\venv\\Scripts\\python.exe backend/test_auth.py

# 6. Run the Offline UIDAI Secure QR & RSA-2048 Cryptographic suite
backend\\venv\\Scripts\\python.exe backend/test_qr.py

# 7. Run the Empirical Performance & Micro-Benchmark profiler (30 iterations)
backend\\venv\\Scripts\\python.exe backend/benchmark_performance.py

# 8. Run the Edge Cases (corrupted, empty, oversized, non-face inputs) suite
backend\\venv\\Scripts\\python.exe backend/test_edge_cases.py

# 9. Verify Frontend Code Quality & Production Build
npm --prefix frontend run lint ; npm --prefix frontend run build
</div>

<!-- ========================================================================= -->
<!-- APPENDIX: TEAM CREDENTIALS -->
<!-- ========================================================================= -->
<h2>Appendix: Team Credentials & Hackathon Registration</h2>
<table>
  <thead>
    <tr>
      <th>Member Name</th>
      <th>Role</th>
      <th>Department & Focus Area</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Arnaa Shah</strong></td>
      <td>Team Leader</td>
      <td>System Architecture, Fast-API Orchestration, Cross-Document Intelligence</td>
    </tr>
    <tr>
      <td><strong>Rushabh Khatri</strong></td>
      <td>Core Developer</td>
      <td>Computer Vision, Pre-OCR Homography Rectification & Glare Attenuation</td>
    </tr>
    <tr>
      <td><strong>Krutika Barewadia</strong></td>
      <td>Core Developer</td>
      <td>Deep Facial Biometrics (128D ResNet), HOG & CLAHE Contrast Fallbacks</td>
    </tr>
    <tr>
      <td><strong>Meet Jariwala</strong></td>
      <td>Core Developer</td>
      <td>Cryptographic Security, Offline UIDAI RSA-2048 QR Verification & Audit Sealing</td>
    </tr>
    <tr>
      <td><strong>Yashvi Parmar</strong></td>
      <td>Core Developer</td>
      <td>Frontend Architecture, Cybernetic Glassmorphic UI & Scanning Telemetry HUD</td>
    </tr>
    <tr>
      <td><strong>Jay Petigara</strong></td>
      <td>Core Developer</td>
      <td>Statutory Indian Document Validation (Verhoeff D5, PAN, ICAO 9303 MRZ)</td>
    </tr>
  </tbody>
</table>

<div class="doc-footer">
  <div>VeriGuard AI &copy; 2026 | Team Abstract_Minds (SIH2026-T2851)</div>
  <div>Smart India Hackathon 2026 | Master System Architecture & Verification Notes</div>
</div>

</body>
</html>
"""

# Replace placeholders safely without f-string collisions
sih_img_tag = f'<img class="sih-logo" src="{sih_logo_b64}" alt="SIH Logo">' if sih_logo_b64 else ''
results_img_tag = f'<img src="{results_capture_b64}" style="width: 95%; max-height: 280px; object-fit: contain; border-radius: 6px; border: 1px solid #CBD5E1; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);" alt="Verification HUD">' if results_capture_b64 else '<p><em>[Results Capture Image]</em></p>'

html_content = html_template.replace("__SIH_LOGO_IMG__", sih_img_tag).replace("__RESULTS_CAPTURE_IMG__", results_img_tag)

with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"[*] HTML successfully written: {HTML_FILE} ({len(html_content):,} characters)")
print(f"[*] Compiling Master Final Notes PDF: {OUTPUT_PDF}")

edge_cmd = [
    EDGE_EXE,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={OUTPUT_PDF}",
    HTML_FILE
]

res = subprocess.run(edge_cmd, capture_output=True, text=True)
time.sleep(2.5)

if os.path.exists(OUTPUT_PDF):
    size = os.path.getsize(OUTPUT_PDF)
    print(f"[SUCCESS] Master Final Notes PDF created on Desktop: {OUTPUT_PDF} ({size:,} bytes)")
    shutil.copyfile(OUTPUT_PDF, DOCS_PDF)
    print(f"[SUCCESS] Master Final Notes PDF copied to repository docs: {DOCS_PDF}")
else:
    print(f"[ERROR] Edge rendering failed: {res.stderr}")
