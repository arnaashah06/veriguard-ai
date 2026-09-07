# build_sih_presentation_pdf.py
import os
import sys
import base64
import subprocess
import time

DESKTOP_DIR = r"C:\Users\pc\Desktop"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUTPUT_PDF = os.path.join(DESKTOP_DIR, "VeriGuard_AI_SIH2026_Submission.pdf")
DOCS_PDF = os.path.join(DOCS_DIR, "VeriGuard_AI_SIH2026_Submission.pdf")
HTML_FILE = os.path.join(ROOT_DIR, "temp_sih_presentation.html")


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
print(f"[*] Clean Brain Bulb loaded: {bool(brain_bulb_b64)}")
print(f"[*] Results Capture loaded: {bool(results_capture_b64)}")

# SVG Icons
ICON_SHIELD = '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'''
ICON_CHECK = '''<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00843D" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'''
ICON_CPU = '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>'''
ICON_FILE = '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>'''
ICON_USERS = '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'''
ICON_ALERT = '''<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#D9534F" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>'''
ICON_CHEVRON = '''<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0070C0" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>'''

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>VeriGuard AI - SIH 2026 Official Submission</title>
<style>
  @page {{
    size: 16in 9in;
    margin: 0;
  }}
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}
  body {{
    font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    background: #E2E8F0;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    color: #1E293B;
  }}
  .slide {{
    width: 16in;
    height: 9in;
    position: relative;
    page-break-after: always;
    page-break-inside: avoid;
    background: #FFFFFF;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }}

  /* HEADER TEMPLATE */
  .slide-header {{
    height: 1.12in;
    padding: 0.16in 0.65in 0 0.65in;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    border-bottom: 2px solid #E2E8F0;
    background: #FFFFFF;
  }}
  .team-badge-oval {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 6px 18px;
    border: 2px solid #7E69AB;
    border-radius: 50px;
    background: #F5F3FF;
    color: #5B21B6;
    font-weight: 800;
    font-size: 14pt;
    letter-spacing: 0.5px;
    box-shadow: 0 2px 4px rgba(126, 105, 171, 0.15);
  }}
  .slide-title-center {{
    text-align: center;
    font-size: 25pt;
    font-weight: 900;
    color: #0F172A;
    letter-spacing: 0.8px;
    text-transform: uppercase;
  }}
  .header-sih-logo {{
    height: 0.82in;
    object-fit: contain;
  }}

  /* SUB-HEADER BLUE PROMPT BANNER */
  .prompt-banner {{
    padding: 0.12in 0.65in 0.08in 0.65in;
    background: #FFFFFF;
  }}
  .prompt-title {{
    font-size: 16.5pt;
    font-weight: 800;
    color: #1F497D;
    display: inline-block;
    padding-bottom: 4px;
    border-bottom: 3.5px solid #1F497D;
    letter-spacing: -0.2px;
  }}

  /* MAIN CONTENT AREA */
  .slide-body {{
    flex: 1;
    padding: 0.12in 0.65in 0.14in 0.65in;
    display: flex;
    gap: 0.28in;
    position: relative;
    overflow: hidden;
  }}

  /* FOOTER BLUE BANNER */
  .slide-footer {{
    height: 0.55in;
    background: #0070C0;
    color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 0.65in;
    font-size: 11pt;
    font-weight: 600;
  }}
  .footer-center-tag {{
    letter-spacing: 0.5px;
    opacity: 0.95;
  }}
  .footer-slide-num {{
    font-size: 18pt;
    font-weight: 900;
    background: rgba(255,255,255,0.22);
    padding: 2px 14px;
    border-radius: 6px;
  }}

  /* CARD STYLES */
  .card {{
    background: #FFFFFF;
    border: 1.5px solid #E2E8F0;
    border-radius: 10px;
    padding: 0.22in;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
    display: flex;
    flex-direction: column;
  }}
  .card-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 0.12in;
    padding-bottom: 8px;
    border-bottom: 1.5px solid #F1F5F9;
  }}
  .card-title {{
    font-size: 13.5pt;
    font-weight: 800;
    color: #0F172A;
  }}
  .card-icon {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 6px;
    background: #EFF6FF;
    color: #0070C0;
  }}

  /* POINT ITEMS */
  .point-item {{
    display: flex;
    gap: 10px;
    margin-bottom: 8.5px;
    font-size: 10.8pt;
    line-height: 1.44;
    color: #334155;
  }}
  .point-bullet {{
    color: #0070C0;
    font-weight: 900;
    font-size: 14pt;
    line-height: 1;
    margin-top: 2px;
  }}
  .point-text strong {{
    color: #0F172A;
    font-weight: 700;
  }}

  /* PILL BADGE */
  .badge {{
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 9.5pt;
    font-weight: 700;
  }}
  .badge-blue {{ background: #DBEAFE; color: #1E40AF; }}
  .badge-green {{ background: #DCFCE7; color: #166534; }}
  .badge-amber {{ background: #FEF3C7; color: #92400E; }}
  .badge-purple {{ background: #F3E8FF; color: #6B21A8; }}

  /* SLIDE 1 SPECIFICS */
  .s1-header {{
    height: 1.22in;
    padding: 0.28in 0.8in 0 0.8in;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .s1-main-title {{
    font-size: 28pt;
    font-weight: 900;
    color: #1F497D;
    letter-spacing: 0.5px;
  }}
  .s1-sub-title {{
    font-size: 20pt;
    font-weight: 800;
    color: #0F172A;
    margin-top: 4px;
    text-align: center;
  }}
  .s1-grid {{
    display: grid;
    grid-template-columns: 1.25fr 0.95fr;
    gap: 0.35in;
    padding: 0.12in 0.8in 0.35in 0.8in;
    flex: 1;
  }}
  .s1-meta-list {{
    display: flex;
    flex-direction: column;
    gap: 9px;
  }}
  .s1-meta-row {{
    display: flex;
    font-size: 12pt;
    line-height: 1.35;
    background: #F8FAFC;
    padding: 7px 14px;
    border-radius: 6px;
    border-left: 4px solid #0070C0;
  }}
  .s1-meta-label {{
    width: 2.7in;
    font-weight: 800;
    color: #0F172A;
  }}
  .s1-meta-val {{
    font-weight: 600;
    color: #1E293B;
    flex: 1;
  }}
  .team-table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    overflow: hidden;
  }}
  .team-table th {{
    background: #1E293B;
    color: #FFFFFF;
    padding: 6px 10px;
    font-size: 9.5pt;
    text-align: left;
  }}
  .team-table td {{
    padding: 5.5px 10px;
    font-size: 9.2pt;
    border-bottom: 1px solid #F1F5F9;
  }}

  /* FLOWCHART STYLES FOR SLIDE 3 */
  .flow-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 12px 0;
    gap: 6px;
  }}
  .flow-step {{
    flex: 1;
    background: #FFFFFF;
    border: 2px solid #0070C0;
    border-radius: 8px;
    padding: 10px 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    box-shadow: 0 3px 6px rgba(0, 112, 192, 0.08);
  }}
  .flow-num {{
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #0070C0;
    color: #FFFFFF;
    font-weight: 800;
    font-size: 10pt;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 6px;
  }}
  .flow-name {{
    font-size: 10pt;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 3px;
  }}
  .flow-desc {{
    font-size: 8pt;
    color: #64748B;
    line-height: 1.25;
  }}
  .flow-arrow {{
    display: flex;
    align-items: center;
    justify-content: center;
    color: #0070C0;
    padding: 0 2px;
  }}

  /* KPI METRIC CARDS */
  .kpi-row {{
    display: flex;
    gap: 14px;
    margin-bottom: 12px;
  }}
  .kpi-card {{
    flex: 1;
    background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
    border: 1.5px solid #BFDBFE;
    border-radius: 8px;
    padding: 10px 14px;
    display: flex;
    flex-direction: column;
  }}
  .kpi-val {{
    font-size: 20pt;
    font-weight: 900;
    color: #0070C0;
  }}
  .kpi-lbl {{
    font-size: 9pt;
    font-weight: 700;
    color: #475569;
    margin-top: 2px;
  }}
</style>
</head>
<body>

<!-- ======================================================================== -->
<!-- SLIDE 1: TITLE PAGE -->
<!-- ======================================================================== -->
<div class="slide">
  <div class="s1-header">
    <div>
      <div class="s1-main-title">SMART INDIA HACKATHON 2026</div>
    </div>
    <img class="header-sih-logo" src="{sih_logo_b64}" alt="SIH 2026">
  </div>
  
  <div class="s1-sub-title">TITLE PAGE</div>

  <div class="s1-grid">
    <!-- Left Column: Details & Team Roster -->
    <div style="display: flex; flex-direction: column; justify-content: space-between;">
      <div class="s1-meta-list">
        <div class="s1-meta-row">
          <div class="s1-meta-label">Problem Statement ID –</div>
          <div class="s1-meta-val"><strong style="color: #0070C0; font-size: 13pt;">SIH26188</strong></div>
        </div>
        <div class="s1-meta-row">
          <div class="s1-meta-label">Problem Statement Title –</div>
          <div class="s1-meta-val">AI-Based Fake Identity & Document Screening System</div>
        </div>
        <div class="s1-meta-row">
          <div class="s1-meta-label">Theme –</div>
          <div class="s1-meta-val"><span class="badge badge-purple">Smart Automation & Cyber Security</span></div>
        </div>
        <div class="s1-meta-row">
          <div class="s1-meta-label">PS Category –</div>
          <div class="s1-meta-val"><span class="badge badge-blue">Software</span></div>
        </div>
        <div class="s1-meta-row">
          <div class="s1-meta-label">Team ID –</div>
          <div class="s1-meta-val"><strong style="color: #1E293B;">SIH2026-T2851</strong></div>
        </div>
        <div class="s1-meta-row">
          <div class="s1-meta-label">Team Name (Registered) –</div>
          <div class="s1-meta-val"><strong style="color: #5B21B6; font-size: 13pt;">Abstract_Minds</strong></div>
        </div>
      </div>

      <!-- Team Members & Roles Table -->
      <div>
        <div style="font-size: 10.5pt; font-weight: 800; color: #0F172A; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
          {ICON_USERS} <span>Team Members & Allotted Engineering Responsibilities:</span>
        </div>
        <table class="team-table">
          <thead>
            <tr>
              <th style="width: 30%;">Member Name</th>
              <th style="width: 22%;">Role</th>
              <th style="width: 48%;">Core Engineering Responsibility</th>
            </tr>
          </thead>
          <tbody>
            <tr style="background: #F8FAFC;">
              <td><strong>Arnaa Shah</strong></td>
              <td><span class="badge badge-blue">Team Leader</span></td>
              <td>Master Architecture Blueprint, App Integration & Orchestration</td>
            </tr>
            <tr>
              <td><strong>Rushabh Khatri</strong></td>
              <td><span class="badge badge-green">Frontend Lead</span></td>
              <td>Frontend Implementation & Responsive User Workflow (React/Vite)</td>
            </tr>
            <tr style="background: #F8FAFC;">
              <td><strong>Krutika Barewadia</strong></td>
              <td><span class="badge badge-amber">Compliance Lead</span></td>
              <td>Document Validation Research, Statutory Verification & Rule Integrity</td>
            </tr>
            <tr>
              <td><strong>Meet Jariwala</strong></td>
              <td><span class="badge badge-purple">Backend Lead</span></td>
              <td>FastAPI Backend Pipeline, OCR Integration & Microservice Routing</td>
            </tr>
            <tr style="background: #F8FAFC;">
              <td><strong>Yashvi Parmar</strong></td>
              <td><span class="badge badge-blue">UI/UX Designer</span></td>
              <td>UI/UX Design, Visuals, Color Palette & Cybernetic Officer HUD</td>
            </tr>
            <tr>
              <td><strong>Jay Petigara</strong></td>
              <td><span class="badge badge-green">System Designer</span></td>
              <td>Application Layout Structuring & Presentation Deck Architecture</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Right Column: Clean SIH Brain Bulb Graphic & Highlights -->
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; background: #F8FAFC; border: 1.5px solid #E2E8F0; border-radius: 12px; padding: 0.22in; position: relative;">
      <div style="font-size: 24pt; font-weight: 900; color: #0070C0; margin-bottom: 4px; letter-spacing: 0.5px;">
        VeriGuard AI
      </div>
      <div style="font-size: 11pt; font-weight: 600; color: #475569; text-align: center; margin-bottom: 12px; max-width: 4.8in;">
        Multi-Document Cross-Verification, Biometric Matching & Forensic Tampering Detection Engine
      </div>
      
      <div style="display: flex; align-items: center; justify-content: center; background: #FFFFFF; border: 2px solid #E2E8F0; border-radius: 16px; padding: 16px 28px; box-shadow: 0 4px 12px rgba(0,112,192,0.08); margin-bottom: 14px;">
        <img src="{brain_bulb_b64}" style="max-height: 2.2in; max-width: 2.2in; object-fit: contain;" alt="SIH Brain Bulb">
        <div style="margin-left: 20px; text-align: left;">
          <div style="font-size: 18pt; font-weight: 900; color: #1F497D; line-height: 1.15;">SMART INDIA<br>HACKATHON<br><span style="color: #0070C0;">2026</span></div>
          <div style="font-size: 9.5pt; font-weight: 700; color: #64748B; margin-top: 6px;">Team: Abstract_Minds</div>
        </div>
      </div>

      <div style="display: flex; gap: 8px; flex-wrap: wrap; justify-content: center;">
        <span class="badge badge-green">✔ Aadhaar Verhoeff D₅</span>
        <span class="badge badge-blue">✔ PAN Sec 139AA</span>
        <span class="badge badge-purple">✔ 128D ResNet Biometrics</span>
        <span class="badge badge-amber">✔ ELA Forensics</span>
      </div>
    </div>
  </div>

  <div class="slide-footer" style="background: #1F497D;">
    <div>Smart India Hackathon 2026 | National Level Innovation Pitch</div>
    <div class="footer-center-tag">Idea Submission Template — PS: SIH26188</div>
    <div class="footer-slide-num">1</div>
  </div>
</div>

<!-- ======================================================================== -->
<!-- SLIDE 2: PROPOSED SOLUTION -->
<!-- ======================================================================== -->
<div class="slide">
  <div class="slide-header">
    <div class="team-badge-oval">Abstract_Minds</div>
    <div class="slide-title-center">IDEA TITLE: VeriGuard AI</div>
    <img class="header-sih-logo" src="{sih_logo_b64}" alt="SIH 2026">
  </div>

  <div class="prompt-banner">
    <div class="prompt-title">Proposed Solution (Describe your Idea/Solution/Prototype)</div>
  </div>

  <div class="slide-body">
    <!-- Card 1: Detailed Solution Explanation -->
    <div class="card" style="flex: 1.1;">
      <div class="card-header">
        <div class="card-icon">{ICON_SHIELD}</div>
        <div class="card-title">1. Detailed Explanation of Proposed Solution</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Comprehensive Indian Credential Screening:</strong> End-to-end multi-document fraud detection engine tailored for India's 1.4B+ citizens, supporting <strong>Aadhaar, PAN, Voter ID (EPIC), Driving Licence, and Passports</strong>.</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Multi-Tier Synchronous Ingestion:</strong> Evaluates single uploads or multi-document batches with an optional live selfie to verify genuine presence and credential continuity.</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Multi-Layered Inspection Pipeline:</strong> Sequentially applies browser-level image quality checks, Tesseract OCR with adaptive contrast binarization, mathematical rule validation, 128D ResNet facial biometrics, and Error Level Analysis (ELA).</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Unified Officer Dossier:</strong> Synthesizes disparate forensic signals into an actionable <strong>0-100 Risk Score</strong> with clear triage recommendations (Approve, Review, Reject).</div>
      </div>
      <div style="margin-top: auto; padding: 6px 10px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; display: flex; justify-content: space-between; font-size: 8.5pt; font-weight: 700; color: #475569;">
        <span>🆔 Aadhaar</span><span>💳 PAN</span><span>🗳️ Voter ID</span><span>🚗 Driving Licence</span><span>🛂 Passport</span>
      </div>
    </div>

    <!-- Card 2: How It Addresses the Problem -->
    <div class="card" style="flex: 1.1;">
      <div class="card-header">
        <div class="card-icon">{ICON_CPU}</div>
        <div class="card-title">2. How It Addresses the Problem</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Crushes KYC Verification Silos:</strong> Legacy systems verify documents individually, failing to catch <em>synthetic identity fraud</em> (e.g., Person A's Aadhaar paired with Person B's PAN). VeriGuard links cross-document demographics with token-sorted fuzzy distance (Levenshtein &ge; 85%) and checks Section 139AA statutory parity.</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Catches Algorithmic Forgeries:</strong> Instantly detects modified or counterfeit numbers using Dihedral Group <strong>D₅ Verhoeff checksums</strong> (Aadhaar) and ICAO 9303 7-3-1 modulo-10 check digits (Passport).</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Exposes Micro-Image Manipulation:</strong> Error Level Analysis (ELA) identifies recompression rate anomalies across text stamps and altered portraits.</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Eliminates Cognitive Fatigue:</strong> Plain-English Explainable AI (XAI) "Identity Stories" spell out exact discrepancies for human-in-the-loop triage.</div>
      </div>
    </div>

    <!-- Card 3: Innovation & Uniqueness -->
    <div class="card" style="flex: 1;">
      <div class="card-header">
        <div class="card-icon">{ICON_CHECK}</div>
        <div class="card-title">3. Innovation & Uniqueness</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Zero Data Retention (Privacy by Design):</strong> Operates entirely in volatile memory with immediate ephemeral scrubbing—adhering strictly to DPDP Act 2023 & UIDAI privacy directives.</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Cryptographic Audit Seal (SHA-256):</strong> Generates an immutable, monotonically chained event digest ensuring court admissibility under <strong>Section 65B of the Indian IT Act, 2000</strong>.</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Multi-Stage Biometric Cascade:</strong> HOG fast-pass + CLAHE contrast recovery for low-contrast/dim laminated cards + 4-angle rotation search (0°, 90°, 180°, 270°).</div>
      </div>
      <div style="margin-top: auto; padding: 8px 10px; background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 6px;">
        <div style="font-size: 9.5pt; font-weight: 800; color: #166534; margin-bottom: 2px;">⚡ Empirical Performance Benchmarks:</div>
        <div style="font-size: 8.5pt; color: #15803D; line-height: 1.4;">• P50 Verification: <strong>0.34ms (Rules) | 1.28ms (Cross-Doc)</strong><br>• Regression Pass Rate: <strong>100% (18/18 Detection | 13/13 Suites)</strong><br>• Peak RAM: <strong>9.38 MB</strong> | Data Retention: <strong>0 Bytes (tmpfs)</strong></div>
      </div>

    </div>
  </div>

  <div class="slide-footer">
    <div>@SIH Idea submission- Template</div>
    <div class="footer-center-tag">Abstract_Minds | VeriGuard AI | Problem Statement SIH26188</div>
    <div class="footer-slide-num">2</div>
  </div>
</div>

<!-- ======================================================================== -->
<!-- SLIDE 3: TECHNICAL APPROACH -->
<!-- ======================================================================== -->
<div class="slide">
  <div class="slide-header">
    <div class="team-badge-oval">Abstract_Minds</div>
    <div class="slide-title-center">TECHNICAL APPROACH</div>
    <img class="header-sih-logo" src="{sih_logo_b64}" alt="SIH 2026">
  </div>

  <div class="prompt-banner">
    <div class="prompt-title">Technologies to be used & Methodology / Process for Implementation</div>
  </div>

  <div class="slide-body" style="flex-direction: column; gap: 0.16in;">
    <!-- Top Row: Technologies Used Matrix -->
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px;">
      <div class="card" style="padding: 11px 13px;">
        <div style="font-size: 11pt; font-weight: 800; color: #0070C0; margin-bottom: 4px;">Frontend & Pre-Flight</div>
        <div style="font-size: 9.3pt; color: #334155; line-height: 1.38;">
          • <strong>React 18 & Vite:</strong> Ultra-fast responsive HUD<br>
          • <strong>Client Pre-flight:</strong> In-browser blur & glare screening<br>
          • <strong>Officer Workspace:</strong> Cyan cybernetic triage console
        </div>
      </div>
      <div class="card" style="padding: 11px 13px;">
        <div style="font-size: 11pt; font-weight: 800; color: #2E7D32; margin-bottom: 4px;">Backend & Auth Engine</div>
        <div style="font-size: 9.3pt; color: #334155; line-height: 1.38;">
          • <strong>FastAPI (Python 3.13):</strong> High-throughput ASGI<br>
          • <strong>OAuth2 JWT & RBAC:</strong> 4 preloaded officer roles<br>
          • <strong>In-Memory tmpfs:</strong> Zero persistent disk retention
        </div>
      </div>
      <div class="card" style="padding: 11px 13px;">
        <div style="font-size: 11pt; font-weight: 800; color: #C9972B; margin-bottom: 4px;">AI, OCR & Enhancement</div>
        <div style="font-size: 9.3pt; color: #334155; line-height: 1.38;">
          • <strong>Pre-OCR De-Skewing:</strong> 4-corner homography & inpaint<br>
          • <strong>Tesseract OCR:</strong> Dual PSM 3 & 6 adaptive passes<br>
          • <strong>ResNet 128D Embeddings:</strong> Deep facial verification
        </div>
      </div>
      <div class="card" style="padding: 11px 13px;">
        <div style="font-size: 11pt; font-weight: 800; color: #7C3AED; margin-bottom: 4px;">Rules & Cryptography</div>
        <div style="font-size: 9.3pt; color: #334155; line-height: 1.38;">
          • <strong>Offline UIDAI QR:</strong> RSA-2048 barcode decode & verify<br>
          • <strong>Verhoeff D₅ & PAN 139AA:</strong> Algorithmic integrity<br>
          • <strong>SHA-256 Audit Seal:</strong> Court-admissible IT Act 65B
        </div>
      </div>
    </div>

    <!-- Middle: Methodology & Process Architecture Flowchart -->
    <div class="card" style="flex: 1; padding: 12px 18px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <div style="font-size: 11.5pt; font-weight: 800; color: #0F172A; display: flex; align-items: center; gap: 8px;">
          {ICON_CPU} <span>Methodology: End-to-End Verification & Reconciliation Pipeline</span>
        </div>
        <span class="badge badge-green">Live Working Prototype Verified</span>
      </div>

      <!-- Connected Flowchart with Chevron Arrows -->
      <div class="flow-row">
        <div class="flow-step">
          <div class="flow-num">1</div>
          <div class="flow-name">Ingestion & De-Skew</div>
          <div class="flow-desc">Blur variance & auto 4-corner perspective rectification</div>
        </div>
        <div class="flow-arrow">{ICON_CHEVRON}</div>
        <div class="flow-step">
          <div class="flow-num">2</div>
          <div class="flow-name">Secure QR & OCR</div>
          <div class="flow-desc">Offline UIDAI RSA-2048 barcode + Tesseract fallback</div>
        </div>
        <div class="flow-arrow">{ICON_CHEVRON}</div>
        <div class="flow-step">
          <div class="flow-num">3</div>
          <div class="flow-name">Statutory Checks</div>
          <div class="flow-desc">Verhoeff D₅, PAN syntax, ICAO 9303 checksums</div>
        </div>
        <div class="flow-arrow">{ICON_CHEVRON}</div>
        <div class="flow-step">
          <div class="flow-num">4</div>
          <div class="flow-name">AI Forensics</div>
          <div class="flow-desc">128D ResNet face match + ELA compression delta</div>
        </div>
        <div class="flow-arrow">{ICON_CHEVRON}</div>
        <div class="flow-step">
          <div class="flow-num">5</div>
          <div class="flow-name">Cross-Reconciliation</div>
          <div class="flow-desc">Fuzzy token distance & Sec 139AA Aadhaar-PAN link</div>
        </div>
        <div class="flow-arrow">{ICON_CHEVRON}</div>
        <div class="flow-step" style="border-color: #00843D; background: #F0FDF4;">
          <div class="flow-num" style="background: #00843D;">6</div>
          <div class="flow-name" style="color: #166534;">XAI Dossier & Seal</div>
          <div class="flow-desc">Deterministic risk score, Identity Story, SHA-256 seal</div>
        </div>
      </div>

      <!-- Bottom Prototype Proof Split -->
      <div style="display: flex; gap: 16px; margin-top: 6px; align-items: center;">
        <div style="flex: 1.1; font-size: 9.0pt; color: #475569; line-height: 1.40;">
          <strong>Hardware Efficiency & Scalability (Micro-Benchmarked):</strong> P50 statutory rules in 0.34ms (~2,500 req/s), cross-doc reconciliation in 1.28ms (~700 req/s). Peak heap memory of only <strong>9.38 MB</strong> running on commodity edge CPUs without GPU clusters. Hardened multi-stage Docker container with in-memory <code>tmpfs</code> mounts ensures zero persistent disk retention (DPDP Act 2023).
        </div>
        <div style="flex: 1; display: flex; align-items: center; gap: 12px; background: #F8FAFC; padding: 6px 12px; border-radius: 6px; border: 1px solid #E2E8F0;">
          <img src="{results_capture_b64}" style="height: 0.72in; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" alt="Prototype UI">
          <div style="font-size: 8.8pt; color: #1E293B;">
            <strong style="color: #166534;">Live Screening HUD:</strong> Risk gauge (0-100), natural language Identity Story, and one-click officer case disposition.
          </div>
        </div>
      </div>
    </div>
  </div>


  <div class="slide-footer">
    <div>@SIH Idea submission- Template</div>
    <div class="footer-center-tag">Abstract_Minds | VeriGuard AI | Problem Statement SIH26188</div>
    <div class="footer-slide-num">3</div>
  </div>
</div>

<!-- ======================================================================== -->
<!-- SLIDE 4: FEASIBILITY AND VIABILITY -->
<!-- ======================================================================== -->
<div class="slide">
  <div class="slide-header">
    <div class="team-badge-oval">Abstract_Minds</div>
    <div class="slide-title-center">FEASIBILITY AND VIABILITY</div>
    <img class="header-sih-logo" src="{sih_logo_b64}" alt="SIH 2026">
  </div>

  <div class="prompt-banner">
    <div class="prompt-title">Analysis of Feasibility, Potential Challenges/Risks & Overcoming Strategies</div>
  </div>

  <div class="slide-body">
    <!-- Left Column: Feasibility Analysis -->
    <div class="card" style="flex: 1.1;">
      <div class="card-header">
        <div class="card-icon">{ICON_CHECK}</div>
        <div class="card-title">1. Multi-Dimensional Feasibility Analysis</div>
      </div>
      
      <div style="margin-bottom: 12px;">
        <div style="font-size: 11pt; font-weight: 800; color: #0070C0; margin-bottom: 2px;">A. Technical Feasibility (Proven & Tested)</div>
        <div class="point-item" style="margin-bottom: 4px;">
          <div class="point-bullet">•</div>
          <div class="point-text">Fully functional prototype verified across <strong>13 automated regression test suites</strong> covering authentic cards, imposters, blurred inputs, and corrupted passport MRZs.</div>
        </div>
        <div class="point-item" style="margin-bottom: 4px;">
          <div class="point-bullet">•</div>
          <div class="point-text">Processes requests in <strong>&lt; 1.5 seconds</strong> on lightweight CPU hardware without specialized GPU clusters.</div>
        </div>
      </div>

      <div style="margin-bottom: 12px;">
        <div style="font-size: 11pt; font-weight: 800; color: #2E7D32; margin-bottom: 2px;">B. Operational Feasibility (Seamless Adoption)</div>
        <div class="point-item" style="margin-bottom: 4px;">
          <div class="point-bullet">•</div>
          <div class="point-text"><strong>1-Click Local Desktop Deployment:</strong> Provided `.bat` and `.sh` scripts launch the entire stack in under 3 minutes for immediate branch office usage.</div>
        </div>
        <div class="point-item" style="margin-bottom: 4px;">
          <div class="point-bullet">•</div>
          <div class="point-text"><strong>Enterprise Ready:</strong> Exposes clean OpenAPI REST endpoints for plug-and-play integration into DigiLocker, banking CBS, and e-governance portals.</div>
        </div>
      </div>

      <div>
        <div style="font-size: 11pt; font-weight: 800; color: #C9972B; margin-bottom: 2px;">C. Economic Feasibility (Zero Proprietary Cost)</div>
        <div class="point-item">
          <div class="point-bullet">•</div>
          <div class="point-text">Built entirely on robust, permissively licensed open-source technologies (FastAPI, OpenCV, Tesseract, React). Zero recurring per-query proprietary vendor licensing fees.</div>
        </div>
      </div>

      <div style="margin-top: auto; padding: 8px 12px; background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 6px; display: flex; justify-content: space-around; text-align: center;">
        <div><div style="font-size: 13pt; font-weight: 900; color: #0070C0;">100%</div><div style="font-size: 8pt; color: #475569; font-weight: 600;">Technical Readiness</div></div>
        <div style="border-left: 1px solid #CBD5E1;"></div>
        <div><div style="font-size: 13pt; font-weight: 900; color: #2E7D32;">&lt; 3 Mins</div><div style="font-size: 8pt; color: #475569; font-weight: 600;">Setup Time</div></div>
        <div style="border-left: 1px solid #CBD5E1;"></div>
        <div><div style="font-size: 13pt; font-weight: 900; color: #7C3AED;">₹ 0</div><div style="font-size: 8pt; color: #475569; font-weight: 600;">License Fees</div></div>
      </div>
    </div>

    <!-- Right Column: Challenges & Mitigation Strategies -->
    <div class="card" style="flex: 1.3;">
      <div class="card-header">
        <div class="card-icon">{ICON_SHIELD}</div>
        <div class="card-title">2. Potential Challenges, Risks & Mitigation Strategies</div>
      </div>

      <div style="display: flex; flex-direction: column; gap: 9px;">
        <!-- Challenge 1 -->
        <div style="background: #F8FAFC; border-left: 3.5px solid #E11D48; padding: 7px 12px; border-radius: 4px;">
          <div style="font-size: 10pt; font-weight: 800; color: #9F1239; display: flex; align-items: center; gap: 6px;">
            {ICON_ALERT} <span>Challenge 1: Real-World Degraded Scans (Skew, Glare, Dim Lighting)</span>
          </div>
          <div style="font-size: 9.3pt; color: #334155; margin-top: 2px;">
            <strong>Mitigation:</strong> Pre-OCR autonomous enhancement (<code>image_enhancement.py</code>). 4-point contour perspective homography (<code>cv2.warpPerspective</code>) rectifies skewed cards; specular glare inpainting (<code>cv2.inpaint</code>) restores washed-out text before Tesseract ingestion.
          </div>
        </div>

        <!-- Challenge 2 -->
        <div style="background: #F8FAFC; border-left: 3.5px solid #D97706; padding: 7px 12px; border-radius: 4px;">
          <div style="font-size: 10pt; font-weight: 800; color: #92400E; display: flex; align-items: center; gap: 6px;">
            {ICON_ALERT} <span>Challenge 2: Forensic Evidentiary Weight vs Legal Fraud Proof</span>
          </div>
          <div style="font-size: 9.3pt; color: #334155; margin-top: 2px;">
            <strong>Mitigation:</strong> Strict Deterministic-Probabilistic Decoupling. Incontrovertible mathematical proofs (Verhoeff D₅, PAN syntax) deliver 100% deterministic counterfeit certainty; probabilistic ELA compression signals route to Explainable AI (XAI) Identity Stories and tiered Officer Priority Queues.
          </div>
        </div>

        <!-- Challenge 3 -->
        <div style="background: #F8FAFC; border-left: 3.5px solid #2563EB; padding: 7px 12px; border-radius: 4px;">
          <div style="font-size: 10pt; font-weight: 800; color: #1E40AF; display: flex; align-items: center; gap: 6px;">
            {ICON_ALERT} <span>Challenge 3: Live Authority Dependency & Scaling Bottlenecks</span>
          </div>
          <div style="font-size: 9.3pt; color: #334155; margin-top: 2px;">
            <strong>Mitigation:</strong> Offline UIDAI RSA-2048 Secure QR Verification (<code>aadhaar_qr.py</code>). Decodes V1 XML and V2 binary barcodes and validates digital signatures using public keys without outbound UIDAI API calls—pre-screening 90%+ traffic and relieving central server loads.
          </div>
        </div>

        <!-- Challenge 4 -->
        <div style="background: #F8FAFC; border-left: 3.5px solid #16A34A; padding: 7px 12px; border-radius: 4px;">
          <div style="font-size: 10pt; font-weight: 800; color: #15803D; display: flex; align-items: center; gap: 6px;">
            {ICON_ALERT} <span>Challenge 4: Production Security & Privacy Compliance Liability</span>
          </div>
          <div style="font-size: 9.3pt; color: #334155; margin-top: 2px;">
            <strong>Mitigation:</strong> Enterprise Hardening (<code>auth.py</code>, <code>Dockerfile</code>). OAuth2 JWT authentication with Role-Based Access Control (<code>compliance_officer</code>, <code>analyst</code>, <code>auditor</code>, <code>admin</code>) plus a hardened Docker stack with in-memory <code>tmpfs</code> mounts strictly guaranteeing zero persistent disk retention of PII under the DPDP Act, 2023.
          </div>
        </div>
      </div>
    </div>
  </div>


  <div class="slide-footer">
    <div>@SIH Idea submission- Template</div>
    <div class="footer-center-tag">Abstract_Minds | VeriGuard AI | Problem Statement SIH26188</div>
    <div class="footer-slide-num">4</div>
  </div>
</div>

<!-- ======================================================================== -->
<!-- SLIDE 5: IMPACT AND BENEFITS -->
<!-- ======================================================================== -->
<div class="slide">
  <div class="slide-header">
    <div class="team-badge-oval">Abstract_Minds</div>
    <div class="slide-title-center">IMPACT AND BENEFITS</div>
    <img class="header-sih-logo" src="{sih_logo_b64}" alt="SIH 2026">
  </div>

  <div class="prompt-banner">
    <div class="prompt-title">Potential Impact on Target Audience & Solution Benefits (Social, Economic, Environmental)</div>
  </div>

  <div class="slide-body" style="flex-direction: column; gap: 0.16in;">
    <!-- Top Row: High-Impact KPI Badges -->
    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-val">0.34 ms</div>
        <div class="kpi-lbl">P50 Statutory Rule Latency (~2,500 req/s Throughput)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-val">100%</div>
        <div class="kpi-lbl">Ground-Truth Detection Precision (18/18 Vectors)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-val">9.38 MB</div>
        <div class="kpi-lbl">Peak Heap Memory Footprint (Commodity Edge Ready)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-val">0 Byte</div>
        <div class="kpi-lbl">Persistent Disk Retention of PII (DPDP Act 2023)</div>
      </div>
    </div>


    <!-- Bottom Row: 2-Column Deep Dive -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; flex: 1;">
      <!-- Audience Impact -->
      <div class="card">
        <div class="card-header">
          <div class="card-icon">{ICON_USERS}</div>
          <div class="card-title">1. Impact on Target Audience</div>
        </div>
        <div class="point-item">
          <div class="point-bullet">•</div>
          <div class="point-text"><strong>Verification Officers & KYC Analysts:</strong> Replaces error-prone manual document inspection with an intelligent priority queue. Plain-English "Identity Story" narratives eliminate cognitive overload.</div>
        </div>
        <div class="point-item">
          <div class="point-bullet">•</div>
          <div class="point-text"><strong>Citizens & Everyday Applicants:</strong> Delivers frictionless, instant onboarding for bank accounts, loan disbursements, SIM issuance, and welfare subsidies without multi-day bureaucratic queues.</div>
        </div>
        <div class="point-item">
          <div class="point-bullet">•</div>
          <div class="point-text"><strong>Financial Institutions & Government Agencies:</strong> Proactively neutralizes synthetic identity fraud, money laundering, ghost beneficiaries, and multi-document loan scams.</div>
        </div>
      </div>

      <!-- Multi-Dimensional Benefits -->
      <div class="card">
        <div class="card-header">
          <div class="card-icon">{ICON_SHIELD}</div>
          <div class="card-title">2. Multi-Dimensional Ecosystem Benefits</div>
        </div>
        <div class="point-item">
          <div class="point-bullet">•</div>
          <div class="point-text"><strong>Social Benefits:</strong> Safeguards citizen identity sovereignty, protects vulnerable populations from identity theft, and democratizes trusted access to the formal financial economy.</div>
        </div>
        <div class="point-item">
          <div class="point-bullet">•</div>
          <div class="point-text"><strong>Economic Benefits:</strong> Slashes institutional KYC verification overhead by over <strong>60%</strong> and saves thousands of crores in fraudulent Non-Performing Assets (NPAs).</div>
        </div>
        <div class="point-item">
          <div class="point-bullet">•</div>
          <div class="point-text"><strong>Environmental & Operational:</strong> 100% digital, paperless workflow eliminates physical document photocopying, courier transit, and physical warehouse archiving.</div>
        </div>
        <div class="point-item">
          <div class="point-bullet">•</div>
          <div class="point-text"><strong>Legal & Statutory Compliance:</strong> Cryptographic SHA-256 event chaining ensures legally admissible electronic audit records under <strong>Section 65B of Indian IT Act, 2000</strong>.</div>
        </div>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div>@SIH Idea submission- Template</div>
    <div class="footer-center-tag">Abstract_Minds | VeriGuard AI | Problem Statement SIH26188</div>
    <div class="footer-slide-num">5</div>
  </div>
</div>

<!-- ======================================================================== -->
<!-- SLIDE 6: RESEARCH AND REFERENCES -->
<!-- ======================================================================== -->
<div class="slide">
  <div class="slide-header">
    <div class="team-badge-oval">Abstract_Minds</div>
    <div class="slide-title-center">RESEARCH AND REFERENCES</div>
    <img class="header-sih-logo" src="{sih_logo_b64}" alt="SIH 2026">
  </div>

  <div class="prompt-banner">
    <div class="prompt-title">Details / Links of Reference Standards, Academic Research & Implementation Work</div>
  </div>

  <div class="slide-body">
    <!-- Col 1: Statutory Frameworks -->
    <div class="card" style="flex: 1;">
      <div class="card-header">
        <div class="card-icon">{ICON_FILE}</div>
        <div class="card-title">1. Statutory & Legal Standards</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Income-tax Act, 1961 (Section 139AA):</strong> Statutory framework mandating PAN-Aadhaar linkage and demographic parity across tax and identity credentials.</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Information Technology Act, 2000 (Section 65B):</strong> Admissibility of electronic records, dictating VeriGuard's tamper-evident SHA-256 hash sealing.</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Aadhaar Act, 2016 & UIDAI Security Directives:</strong> Strict zero-storage norms and cryptographic protection standards for national identity credentials.</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Digital Personal Data Protection (DPDP) Act, 2023:</strong> In-memory ephemeral processing and complete data scrubbing after verification completion.</div>
      </div>
    </div>

    <!-- Col 2: Academic & Algorithmic Literature -->
    <div class="card" style="flex: 1.1;">
      <div class="card-header">
        <div class="card-icon">{ICON_CPU}</div>
        <div class="card-title">2. Academic & Algorithmic Citations</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Verhoeff, J. (1969):</strong> <em>"Error Detecting Decimal Codes"</em>, Mathematical Centre Tracts 29, Amsterdam. Foundation for Aadhaar's dihedral group D₅ check digit algorithm.</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>ICAO Document 9303:</strong> <em>"Machine Readable Travel Documents (MRTDs)"</em>, Part 3. Specifications for TD3 MRZ line formats and 7-3-1 modulo-10 check digits.</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Krawetz, N. (2007):</strong> <em>"A Picture's Worth... Digital Image Analysis & Error Level Analysis"</em>, Hacker Factor Solutions. Pixel-level recompression delta analysis.</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>He, K. et al. (2016):</strong> <em>"Deep Residual Learning for Image Recognition"</em>, IEEE CVPR. ResNet deep convolutional network for 128D facial feature vectors.</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Smith, R. (2007):</strong> <em>"An Overview of the Tesseract OCR Engine"</em>, IEEE ICDAR. Multi-pass page segmentation and text extraction architecture.</div>
      </div>
    </div>

    <!-- Col 3: Project Repository & Prototype Verification -->
    <div class="card" style="flex: 0.95;">
      <div class="card-header">
        <div class="card-icon">{ICON_CHECK}</div>
        <div class="card-title">3. Project Repository & Proofs</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Technical Report (Sec 9 Mitigations):</strong><br><a href="https://github.com/arnaashah06/veriguard-ai/blob/main/technical_report.md" style="color: #5B21B6; font-weight: 800; text-decoration: underline; word-break: break-all;">📄 Read technical_report.md (GitHub)</a></div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Empirical Benchmark Profile:</strong> <code>empirical_benchmark_report.json</code> logging P50 latency & memory profiling.</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>18/18 Truth Table & Suites:</strong> 100% precision on counterfeit check digits, syntax, and imposters.</div>
      </div>
      <div class="point-item">
        <div class="point-bullet">•</div>
        <div class="point-text"><strong>Container Stack & RBAC:</strong> Hardened Dockerfile with <code>tmpfs</code> mounts and OAuth2 JWT auth.</div>
      </div>
      <div style="margin-top: auto; padding: 10px; background: #EFF6FF; border: 1.5px solid #BFDBFE; border-radius: 8px; text-align: center;">
        <div style="font-size: 11pt; font-weight: 800; color: #1E40AF;">Smart India Hackathon 2026</div>
        <div style="font-size: 9.5pt; color: #3B82F6; margin-top: 2px;">Team Abstract_Minds | ID: SIH2026-T2851</div>
        <div style="font-size: 9pt; font-weight: 700; color: #00843D; margin-top: 4px;">✔ Idea Submission Package Ready</div>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div>@SIH Idea submission- Template</div>
    <div class="footer-center-tag">Abstract_Minds | VeriGuard AI | Problem Statement SIH26188</div>
    <div class="footer-slide-num">6</div>
  </div>
</div>

</body>
</html>
"""

with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"[*] HTML successfully written to: {HTML_FILE}")
print(f"[*] Invoking Microsoft Edge headless to render PDF: {OUTPUT_PDF}")

edge_cmd = [
    EDGE_EXE,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={OUTPUT_PDF}",
    HTML_FILE
]

res = subprocess.run(edge_cmd, capture_output=True, text=True)
time.sleep(1.5)

import shutil
if os.path.exists(OUTPUT_PDF):
    size = os.path.getsize(OUTPUT_PDF)
    print(f"[SUCCESS] PDF successfully created on Desktop: {OUTPUT_PDF} ({size:,} bytes)")
    shutil.copyfile(OUTPUT_PDF, DOCS_PDF)
    print(f"[SUCCESS] PDF copied to repository docs: {DOCS_PDF}")
    
    # Verify with PyMuPDF
    import pymupdf
    doc = pymupdf.open(OUTPUT_PDF)
    print(f"[VERIFY] Total Pages in PDF: {len(doc)}")
    for i, page in enumerate(doc):
        r = page.rect
        aspect = r.width / r.height
        print(f"  Page {i+1}: {r.width:.1f} x {r.height:.1f} pt (Aspect: {aspect:.2f})")
    doc.close()

else:
    print(f"[ERROR] PDF generation failed. Edge stderr: {res.stderr}")
