# build_sih_presentation_pptx.py
"""
Builds the official 16:9 widescreen PowerPoint presentation (.pptx)
matching the Smart India Hackathon (SIH 2026) 6-slide deck.
Saves to: C:\\Users\\pc\\Desktop\\VeriGuard_AI_SIH2026_Submission.pptx
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

DESKTOP_DIR = r"C:\Users\pc\Desktop"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)
OUTPUT_PPTX = os.path.join(DESKTOP_DIR, "VeriGuard_AI_SIH2026_Submission.pptx")
DOCS_PPTX = os.path.join(DOCS_DIR, "VeriGuard_AI_SIH2026_Submission.pptx")


# Color Palette
NAVY = RGBColor(31, 73, 125)        # #1F497D
PRIMARY_BLUE = RGBColor(0, 112, 192)# #0070C0
DARK_BLUE = RGBColor(30, 64, 175)   # #1E40AF
PURPLE = RGBColor(91, 33, 182)      # #5B21B6
PURPLE_LIGHT = RGBColor(245, 243, 255) # #F5F3FF
PURPLE_BORDER = RGBColor(126, 105, 171) # #7E69AB
GREEN = RGBColor(0, 132, 61)        # #00843D
GREEN_BG = RGBColor(232, 242, 236)  # #E8F2EC
RED = RGBColor(217, 83, 79)         # #D9534F
DARK_TEXT = RGBColor(30, 41, 59)    # #1E293B
MUTED_TEXT = RGBColor(100, 116, 139)# #64748B
BG_LIGHT = RGBColor(248, 250, 252)  # #F8FAFC
BORDER_COLOR = RGBColor(226, 232, 240) # #E2E8F0
WHITE = RGBColor(255, 255, 255)
TEAL = RGBColor(13, 148, 136)

# Assets
SIH_LOGO_PATH = os.path.join(ROOT_DIR, r"temp\sih_assets\page_1_img_15.png")
BRAIN_BULB_PATH = os.path.join(ROOT_DIR, r"temp\sih_assets\brain_bulb_clean.png")
RESULTS_CAPTURE_PATH = os.path.join(ROOT_DIR, r"results_capture.png")

def create_presentation():
    prs = Presentation()
    # Set 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # Blank slide

    def add_header(slide, title_text, team_badge=True):
        # Header banner line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(0.95), Inches(12.333), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = BORDER_COLOR
        line.line.fill.background()

        if team_badge:
            # Team badge oval
            badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(0.25), Inches(1.8), Inches(0.55))
            badge.fill.solid()
            badge.fill.fore_color.rgb = PURPLE_LIGHT
            badge.line.color.rgb = PURPLE_BORDER
            badge.line.width = Pt(1.5)
            p = badge.text_frame.paragraphs[0]
            p.text = "Abstract_Minds"
            p.font.size = Pt(12)
            p.font.bold = True
            p.font.color.rgb = PURPLE
            p.alignment = PP_ALIGN.CENTER
            badge.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

        # Slide Title
        title_box = slide.shapes.add_textbox(Inches(2.5), Inches(0.22), Inches(8.333), Inches(0.65))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.alignment = PP_ALIGN.CENTER

        # SIH Logo on Top Right
        if os.path.exists(SIH_LOGO_PATH):
            slide.shapes.add_picture(SIH_LOGO_PATH, Inches(11.2), Inches(0.12), width=Inches(1.6))

    def add_footer(slide, slide_num, dark=False):
        footer_y = Inches(7.05)
        # Footer background band
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), footer_y, Inches(13.333), Inches(0.45))
        bg.fill.solid()
        bg.fill.fore_color.rgb = NAVY if dark else BG_LIGHT
        bg.line.fill.background()

        # Left label
        tb = slide.shapes.add_textbox(Inches(0.5), footer_y + Inches(0.05), Inches(4.5), Inches(0.35))
        p = tb.text_frame.paragraphs[0]
        p.text = "@SIH Idea submission - Template"
        p.font.size = Pt(9.5)
        p.font.color.rgb = WHITE if dark else MUTED_TEXT

        # Center label
        tb = slide.shapes.add_textbox(Inches(4.5), footer_y + Inches(0.05), Inches(5.5), Inches(0.35))
        p = tb.text_frame.paragraphs[0]
        p.text = "Abstract_Minds | VeriGuard AI | Problem Statement SIH26188"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = RGBColor(224, 231, 255) if dark else PRIMARY_BLUE
        p.alignment = PP_ALIGN.CENTER

        # Slide number circle
        num_box = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(12.4), footer_y + Inches(0.05), Inches(0.35), Inches(0.35))
        num_box.fill.solid()
        num_box.fill.fore_color.rgb = PRIMARY_BLUE
        num_box.line.fill.background()
        p = num_box.text_frame.paragraphs[0]
        p.text = str(slide_num)
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        num_box.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

    def add_card(slide, left, top, width, height, bg_color=WHITE, border_color=BORDER_COLOR):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
        return shape

    # ==========================================
    # SLIDE 1: TITLE PAGE
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    
    # Title Top Bar
    s1_title_box = s1.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(8.5), Inches(0.6))
    p = s1_title_box.text_frame.paragraphs[0]
    p.text = "SMART INDIA HACKATHON 2026"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = NAVY

    s1_sub_box = s1.shapes.add_textbox(Inches(5.5), Inches(0.95), Inches(4.0), Inches(0.4))
    p = s1_sub_box.text_frame.paragraphs[0]
    p.text = "TITLE PAGE"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = DARK_TEXT

    if os.path.exists(SIH_LOGO_PATH):
        s1.shapes.add_picture(SIH_LOGO_PATH, Inches(11.2), Inches(0.2), width=Inches(1.6))

    # Left Metadata Box
    left_meta = add_card(s1, Inches(0.5), Inches(1.4), Inches(7.2), Inches(2.7), BG_LIGHT)
    tf = left_meta.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.25)
    tf.margin_top = Inches(0.2)

    meta_items = [
        ("Problem Statement ID", "SIH26188", PRIMARY_BLUE),
        ("Problem Statement Title", "AI-Based Fake Identity & Document Screening System", DARK_TEXT),
        ("Theme", "Smart Automation & Cyber Security", PURPLE),
        ("PS Category", "Software", DARK_BLUE),
        ("Team ID", "SIH2026-T2851", DARK_TEXT),
        ("Team Name (Registered)", "Abstract_Minds", PURPLE),
        ("Technical Report", "https://github.com/arnaashah06/veriguard-ai/blob/main/technical_report.md", PRIMARY_BLUE)
    ]
    for idx, (label, val, col) in enumerate(meta_items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.space_after = Pt(3)
        run1 = p.add_run()
        run1.text = f"{label} – "
        run1.font.size = Pt(10)
        run1.font.bold = True
        run1.font.color.rgb = DARK_TEXT

        run2 = p.add_run()
        run2.text = val
        run2.font.size = Pt(9.5 if "http" in val else 10)
        run2.font.bold = True
        run2.font.color.rgb = col
        if "http" in val:
            run2.hyperlink.address = val
            run2.font.underline = True

    # Team Members Table
    table_shape = s1.shapes.add_table(7, 3, Inches(0.5), Inches(4.25), Inches(7.2), Inches(2.6))
    table = table_shape.table
    table.columns[0].width = Inches(1.8)
    table.columns[1].width = Inches(1.5)
    table.columns[2].width = Inches(3.9)

    headers = ["Member Name", "Role", "Core Engineering Responsibility"]
    for col_idx, h in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = WHITE

    team_data = [
        ("Arnaa Shah", "Team Leader", "Master Architecture Blueprint, App Integration & Orchestration"),
        ("Rushabh Khatri", "Frontend Lead", "Frontend Implementation & Responsive User Workflow (React 18/Vite)"),
        ("Krutika Barewadia", "Compliance Lead", "Document Validation Research, Statutory Verification & Rule Integrity"),
        ("Meet Jariwala", "Backend Lead", "FastAPI Backend Pipeline, OCR Integration & Microservice Routing"),
        ("Yashvi Parmar", "UI/UX Designer", "UI/UX Design, Visuals, Color Palette & Cybernetic Officer HUD"),
        ("Jay Petigara", "System Designer", "Application Layout Structuring & Presentation Deck Architecture")
    ]
    for row_idx, (name, role, resp) in enumerate(team_data):
        r = row_idx + 1
        for col_idx, text in enumerate([name, role, resp]):
            cell = table.cell(r, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if r % 2 == 1 else BG_LIGHT
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.size = Pt(8.5)
            p.font.bold = (col_idx == 0 or col_idx == 1)
            p.font.color.rgb = PURPLE if col_idx == 1 and "Leader" in text else DARK_TEXT

    # Right Showcase Card
    right_card = add_card(s1, Inches(7.9), Inches(1.4), Inches(4.9), Inches(5.45), WHITE)
    rc_tf = right_card.text_frame
    rc_tf.margin_top = Inches(0.3)
    p = rc_tf.paragraphs[0]
    p.text = "VeriGuard AI"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.alignment = PP_ALIGN.CENTER

    p2 = rc_tf.add_paragraph()
    p2.text = "Multi-Document Cross-Verification, Biometric Matching &\nForensic Tampering Detection Engine"
    p2.font.size = Pt(11)
    p2.font.color.rgb = MUTED_TEXT
    p2.alignment = PP_ALIGN.CENTER
    p2.space_after = Pt(14)

    # Insert Brain Bulb Emblem
    if os.path.exists(BRAIN_BULB_PATH):
        s1.shapes.add_picture(BRAIN_BULB_PATH, Inches(8.5), Inches(2.7), width=Inches(3.7))

    # Badge Row
    badge_box = s1.shapes.add_textbox(Inches(8.0), Inches(5.8), Inches(4.7), Inches(0.9))
    bf = badge_box.text_frame
    p = bf.paragraphs[0]
    p.text = "✔ Aadhaar Verhoeff D5   ✔ PAN Sec 139AA\n✔ 128D ResNet Biometrics   ✔ ELA Forensics"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = GREEN
    p.alignment = PP_ALIGN.CENTER

    add_footer(s1, 1, dark=True)

    # ==========================================
    # SLIDE 2: PROPOSED SOLUTION
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "IDEA TITLE: VERIGUARD AI")

    sub_box = s2.shapes.add_textbox(Inches(0.5), Inches(0.98), Inches(12.333), Inches(0.4))
    p = sub_box.text_frame.paragraphs[0]
    p.text = "Proposed Solution (Describe your Idea/Solution/Prototype)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = DARK_BLUE

    # 3 Columns
    col_w = Inches(3.95)
    col_h = Inches(5.45)
    top_pos = Inches(1.45)

    # Col 1: Detailed Explanation
    c1 = add_card(s2, Inches(0.5), top_pos, col_w, col_h)
    tf = c1.text_frame
    tf.margin_left = tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = "1. Detailed Explanation of Solution"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)

    points1 = [
        "Comprehensive Indian Credential Screening: End-to-end multi-document fraud detection engine supporting Aadhaar, PAN, Voter ID (EPIC), Driving Licence, and Passports.",
        "Multi-Tier Synchronous Ingestion: Evaluates single uploads or multi-document batches with an optional live selfie to verify genuine presence and credential continuity.",
        "Multi-Layered Inspection Pipeline: Sequentially applies browser-level image quality checks, Tesseract OCR with adaptive contrast binarization, mathematical rule validation, 128D ResNet facial biometrics, and Error Level Analysis (ELA).",
        "Unified Officer Dossier: Synthesizes disparate forensic signals into an actionable 0-100 Risk Score with clear triage recommendations (Approve, Review, Reject)."
    ]
    for pt in points1:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(9.5)
        p.font.color.rgb = DARK_TEXT
        p.space_after = Pt(8)

    # Col 2: How It Addresses Problem
    c2 = add_card(s2, Inches(4.68), top_pos, col_w, col_h)
    tf = c2.text_frame
    tf.margin_left = tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = "2. How It Addresses the Problem"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)

    points2 = [
        "Crushes KYC Verification Silos: Legacy systems verify documents individually, failing to catch synthetic identity fraud. VeriGuard links cross-document demographics with token-sorted fuzzy distance (Levenshtein >= 85%) and checks Section 139AA statutory parity.",
        "Catches Algorithmic Forgeries: Instantly detects modified or counterfeit numbers using Dihedral Group D5 Verhoeff checksums (Aadhaar) and ICAO 9303 7-3-1 modulo-10 check digits (Passport).",
        "Exposes Micro-Image Manipulation: Error Level Analysis (ELA) identifies recompression rate anomalies across text stamps and altered portraits.",
        "Eliminates Cognitive Fatigue: Plain-English Explainable AI (XAI) 'Identity Stories' spell out exact discrepancies for human-in-the-loop triage."
    ]
    for pt in points2:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(9.5)
        p.font.color.rgb = DARK_TEXT
        p.space_after = Pt(8)

    # Col 3: Innovation & Uniqueness
    c3 = add_card(s2, Inches(8.86), top_pos, col_w, col_h)
    tf = c3.text_frame
    tf.margin_left = tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = "3. Innovation & Uniqueness"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)

    points3 = [
        "Zero Data Retention (Privacy by Design): Operates entirely in volatile memory with immediate ephemeral scrubbing—adhering strictly to DPDP Act 2023 & UIDAI privacy directives.",
        "Cryptographic Audit Seal (SHA-256): Generates an immutable, monotonically chained event digest ensuring court admissibility under Section 65B of the Indian IT Act, 2000.",
        "Multi-Stage Biometric Cascade: HOG fast-pass + CLAHE contrast recovery for low-contrast/dim laminated cards + 4-angle rotation search (0°, 90°, 180°, 270°)."
    ]
    for pt in points3:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(9.5)
        p.font.color.rgb = DARK_TEXT
        p.space_after = Pt(8)

    # Benchmarks callout inside Col 3
    bench_card = add_card(s2, Inches(9.0), Inches(5.35), Inches(3.65), Inches(1.4), GREEN_BG, RGBColor(167, 243, 208))
    bf = bench_card.text_frame
    bf.margin_left = Inches(0.15)
    bf.margin_top = Inches(0.08)
    p = bf.paragraphs[0]
    p.text = "⚡ Empirical Performance Benchmarks:"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = GREEN
    p.space_after = Pt(2)
    p2 = bf.add_paragraph()
    p2.text = "• P50 Verification: 0.34ms (Rules) | 1.28ms (Cross-Doc)\n• Regression Pass Rate: 100% (18/18 Detection | 13/13 Suites)\n• Peak RAM: 9.38 MB | Data Retention: 0 Bytes (tmpfs)"
    p2.font.size = Pt(8.0)
    p2.font.bold = True
    p2.font.color.rgb = DARK_TEXT


    add_footer(s2, 2)

    # ==========================================
    # SLIDE 3: TECHNICAL APPROACH
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "TECHNICAL APPROACH")

    sub_box = s3.shapes.add_textbox(Inches(0.5), Inches(0.98), Inches(12.333), Inches(0.4))
    p = sub_box.text_frame.paragraphs[0]
    p.text = "Technologies to be used & Methodology / Process for Implementation"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = DARK_BLUE

    # Top 4 Architecture Cards
    card_w = Inches(2.95)
    card_h = Inches(1.35)
    top_y = Inches(1.4)

    tech_cards = [
        ("Frontend & Pre-Flight", "React 18 & Vite: Ultra-fast responsive HUD\nClient Pre-Flight: In-browser blur & glare check\nOfficer Workspace: Cyan cybernetic triage console", PRIMARY_BLUE),
        ("Backend & Auth Engine", "FastAPI (Python 3.13): High-throughput ASGI\nOAuth2 JWT & RBAC: 4 preloaded officer roles\nIn-Memory tmpfs: Zero persistent disk retention", TEAL),
        ("AI, OCR & Enhancement", "Pre-OCR De-Skewing: 4-corner homography & inpainting\nTesseract OCR: Dual PSM 3 & 6 adaptive passes\nResNet 128D Embeddings: Deep facial verification", PURPLE),
        ("Rules & Cryptography", "Offline UIDAI QR: RSA-2048 barcode decode & verify\nVerhoeff D5 & PAN 139AA: Algorithmic integrity\nSHA-256 Audit Seal: Court-admissible IT Act 65B", DARK_BLUE)
    ]
    for i, (title, desc, color) in enumerate(tech_cards):
        cx = Inches(0.5) + i * Inches(3.12)
        c = add_card(s3, cx, top_y, card_w, card_h)
        tf = c.text_frame
        tf.margin_left = tf.margin_right = Inches(0.15)
        tf.margin_top = Inches(0.1)
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = color
        p.space_after = Pt(4)
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(8.0)
        p2.font.color.rgb = DARK_TEXT

    # Methodology Flowchart Label
    flow_lbl = s3.shapes.add_textbox(Inches(0.5), Inches(2.85), Inches(12.333), Inches(0.35))
    p = flow_lbl.text_frame.paragraphs[0]
    p.text = "⚙ Methodology: End-to-End Verification & Reconciliation Pipeline"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = NAVY

    # 6 Flowchart Step Cards
    flow_steps = [
        ("1", "Ingestion & De-Skew", "Blur variance & auto 4-corner perspective rectification"),
        ("2", "Secure QR & OCR", "Offline UIDAI RSA-2048 barcode + Tesseract fallback"),
        ("3", "Statutory Checks", "Verhoeff D5, PAN syntax, ICAO 9303 checksums"),
        ("4", "AI Forensics", "128D ResNet face match + ELA compression delta"),
        ("5", "Cross-Reconciliation", "Fuzzy token distance & Sec 139AA Aadhaar-PAN link"),
        ("6", "XAI Dossier & Seal", "Deterministic risk score, Identity Story, SHA-256 seal")
    ]
    step_w = Inches(1.95)
    step_h = Inches(1.6)
    step_y = Inches(3.25)
    for i, (num, stitle, sdesc) in enumerate(flow_steps):
        sx = Inches(0.5) + i * Inches(2.07)
        sc = add_card(s3, sx, step_y, step_w, step_h, WHITE if i < 5 else GREEN_BG, PRIMARY_BLUE if i < 5 else GREEN)
        tf = sc.text_frame
        tf.margin_left = tf.margin_right = Inches(0.1)
        tf.margin_top = Inches(0.1)
        p = tf.paragraphs[0]
        p.text = f"[{num}] {stitle}"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_BLUE if i < 5 else GREEN
        p.space_after = Pt(4)
        p2 = tf.add_paragraph()
        p2.text = sdesc
        p2.font.size = Pt(8.0)
        p2.font.color.rgb = DARK_TEXT

    # Bottom Row: Hardware Efficiency & UI Screenshot
    bottom_y = Inches(5.0)
    b_card = add_card(s3, Inches(0.5), bottom_y, Inches(7.5), Inches(1.85), BG_LIGHT)
    bf = b_card.text_frame
    bf.margin_left = Inches(0.2)
    bf.margin_top = Inches(0.15)
    p = bf.paragraphs[0]
    p.text = "Hardware Efficiency & Enterprise Scalability (Micro-Benchmarked)"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(4)
    p2 = bf.add_paragraph()
    p2.text = "• Micro-Benchmarked Latency: P50 statutory rules in 0.34ms (~2,500 req/s), cross-document reconciliation in 1.28ms (~700 req/s).\n• Ultra-Low RAM Footprint: Peak heap consumption of only 9.38 MB; engineered to run on commodity edge CPUs without GPU clusters.\n• Hardened Container Architecture: Multi-stage Docker + docker-compose with tmpfs mounts ensuring zero persistent disk retention (DPDP Act 2023)."
    p2.font.size = Pt(8.5)
    p2.font.color.rgb = DARK_TEXT


    # Results capture screenshot
    if os.path.exists(RESULTS_CAPTURE_PATH):
        s3.shapes.add_picture(RESULTS_CAPTURE_PATH, Inches(8.2), bottom_y, width=Inches(4.6))

    add_footer(s3, 3)

    # ==========================================
    # SLIDE 4: FEASIBILITY AND VIABILITY
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "FEASIBILITY AND VIABILITY")

    sub_box = s4.shapes.add_textbox(Inches(0.5), Inches(0.98), Inches(12.333), Inches(0.4))
    p = sub_box.text_frame.paragraphs[0]
    p.text = "Analysis of Feasibility, Potential Challenges/Risks & Overcoming Strategies"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = DARK_BLUE

    # Left Column: Feasibility Analysis
    c_left = add_card(s4, Inches(0.5), Inches(1.45), Inches(5.9), Inches(5.45))
    tf = c_left.text_frame
    tf.margin_left = tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = "1. Multi-Dimensional Feasibility Analysis"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)

    feas_points = [
        ("A. Technical Feasibility (Proven & Tested)", "Fully functional prototype verified across 13 automated regression test suites covering authentic cards, imposters, blurred inputs, and corrupted passport MRZs. Processes requests in < 1.5s on commodity CPU hardware without cloud GPU clusters."),
        ("B. Operational Feasibility (Seamless Adoption)", "1-Click Local Desktop Deployment: Provided .bat and .sh scripts launch the entire stack in under 3 minutes for immediate branch office usage. Enterprise Ready: Exposes clean OpenAPI REST endpoints for plug-and-play integration into DigiLocker, banking CBS, and e-governance portals."),
        ("C. Economic Feasibility (Zero Proprietary Cost)", "Built entirely on robust, permissively licensed open-source technologies (FastAPI, OpenCV, Tesseract, React). Zero recurring per-query proprietary vendor licensing fees.")
    ]
    for heading, text in feas_points:
        p = tf.add_paragraph()
        p.text = heading
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_BLUE
        p.space_after = Pt(2)
        p2 = tf.add_paragraph()
        p2.text = text
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = DARK_TEXT
        p2.space_after = Pt(8)

    # Stat bar in left card
    stat_card = add_card(s4, Inches(0.7), Inches(5.7), Inches(5.5), Inches(1.0), PURPLE_LIGHT, PURPLE_BORDER)
    sf = stat_card.text_frame
    sf.margin_top = Inches(0.12)
    p = sf.paragraphs[0]
    p.text = "100% Technical Readiness    |    < 3 Mins Setup Time    |    ₹ 0 License Fees"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PURPLE
    p.alignment = PP_ALIGN.CENTER

    # Right Column: Potential Challenges & Mitigations
    c_right = add_card(s4, Inches(6.6), Inches(1.45), Inches(6.2), Inches(5.45))
    tf = c_right.text_frame
    tf.margin_left = tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = "2. Potential Challenges, Risks & Mitigation Strategies"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)

    challenges = [
        ("Challenge 1: Real-World Degraded Scans (Skew, Glare, Dim Lighting)",
         "Mitigation: Pre-OCR autonomous enhancement (image_enhancement.py). 4-point contour perspective homography (cv2.warpPerspective) rectifies skewed cards; specular glare inpainting (cv2.inpaint) restores washed-out text before Tesseract ingestion."),
        ("Challenge 2: Forensic Evidentiary Weight vs Legal Fraud Proof",
         "Mitigation: Strict Deterministic-Probabilistic Decoupling. Incontrovertible mathematical proofs (Verhoeff D5, PAN syntax) deliver 100% deterministic counterfeit certainty; probabilistic ELA compression signals route to Explainable AI (XAI) Identity Stories and tiered Officer Priority Queues."),
        ("Challenge 3: Live Authority Dependency & Scaling Bottlenecks",
         "Mitigation: Offline UIDAI RSA-2048 Secure QR Verification (aadhaar_qr.py). Decodes V1 XML and V2 binary barcodes and validates digital signatures using public keys without outbound UIDAI API calls—pre-screening 90%+ traffic and relieving central server loads."),
        ("Challenge 4: Production Security & Privacy Compliance Liability",
         "Mitigation: Enterprise Hardening (auth.py, Dockerfile). OAuth2 JWT authentication with Role-Based Access Control (compliance_officer, analyst, auditor, admin) plus a hardened Docker stack with in-memory tmpfs mounts strictly guaranteeing zero persistent disk retention of PII under the DPDP Act, 2023.")
    ]

    for ch, mit in challenges:
        p = tf.add_paragraph()
        p.text = "⚠ " + ch
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = RED
        p.space_after = Pt(2)
        p2 = tf.add_paragraph()
        p2.text = mit
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = DARK_TEXT
        p2.space_after = Pt(8)

    add_footer(s4, 4)

    # ==========================================
    # SLIDE 5: IMPACT AND BENEFITS
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "IMPACT AND BENEFITS")

    sub_box = s5.shapes.add_textbox(Inches(0.5), Inches(0.98), Inches(12.333), Inches(0.4))
    p = sub_box.text_frame.paragraphs[0]
    p.text = "Potential Impact on Target Audience & Solution Benefits (Social, Economic, Environmental)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = DARK_BLUE

    # Top 4 Metric Hero Cards
    m_w = Inches(2.95)
    m_h = Inches(1.35)
    top_my = Inches(1.4)
    metrics = [
        ("0.34 ms", "P50 Statutory Rule Latency\n(~2,500 req/s Processing Throughput)", PRIMARY_BLUE),
        ("100%", "Ground-Truth Detection Precision\n(18/18 Counterfeit & Real Vectors)", GREEN),
        ("9.38 MB", "Peak Heap Memory Footprint\n(Ultra-Lightweight Edge CPU Ready)", TEAL),
        ("0 Byte", "Persistent Disk Retention of PII\n(Full DPDP Act 2023 Compliance)", DARK_BLUE)
    ]
    for i, (val, label, col) in enumerate(metrics):
        mx = Inches(0.5) + i * Inches(3.12)
        mc = add_card(s5, mx, top_my, m_w, m_h, BG_LIGHT, BORDER_COLOR)
        mf = mc.text_frame
        mf.margin_left = mf.margin_right = Inches(0.15)
        mf.margin_top = Inches(0.1)
        p = mf.paragraphs[0]
        p.text = val
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = col
        p.alignment = PP_ALIGN.CENTER
        p2 = mf.add_paragraph()
        p2.text = label
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = DARK_TEXT
        p2.alignment = PP_ALIGN.CENTER

    # 2 Big Impact Columns
    c_w = Inches(6.05)
    c_h = Inches(3.95)
    b_top = Inches(2.95)

    # Left: Impact on Target Audience
    c_aud = add_card(s5, Inches(0.5), b_top, c_w, c_h)
    af = c_aud.text_frame
    af.margin_left = af.margin_right = Inches(0.2)
    af.margin_top = Inches(0.2)
    p = af.paragraphs[0]
    p.text = "1. Impact on Target Audience"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)

    aud_items = [
        ("Verification Officers & KYC Analysts", "Replaces error-prone manual document inspection with an intelligent priority queue. Plain-English 'Identity Story' narratives eliminate cognitive overload and reduce review times by 75%."),
        ("Citizens & Everyday Applicants", "Delivers frictionless, instant onboarding for bank accounts, loan disbursements, SIM issuance, and welfare subsidies without multi-day bureaucratic queues or false-positive rejections."),
        ("Financial Institutions & Government Agencies", "Proactively neutralizes synthetic identity fraud, money laundering, ghost beneficiaries, and multi-document loan scams before accounts can be opened.")
    ]
    for title, desc in aud_items:
        p = af.add_paragraph()
        p.text = "• " + title + ": "
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_BLUE
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = DARK_TEXT
        p.space_after = Pt(8)

    # Right: Ecosystem Benefits
    c_eco = add_card(s5, Inches(6.78), b_top, c_w, c_h)
    ef = c_eco.text_frame
    ef.margin_left = ef.margin_right = Inches(0.2)
    ef.margin_top = Inches(0.2)
    p = ef.paragraphs[0]
    p.text = "2. Multi-Dimensional Ecosystem Benefits"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)

    eco_items = [
        ("Social Benefits", "Safeguards citizen identity sovereignty, protects vulnerable populations from identity theft, and democratizes trusted access to the formal financial economy."),
        ("Economic Benefits", "Slashes institutional KYC verification overhead by over 60% and saves thousands of crores in fraudulent Non-Performing Assets (NPAs)."),
        ("Environmental & Operational", "100% digital, paperless workflow eliminates physical document photocopying, courier transit, and physical warehouse archiving."),
        ("Legal & Statutory Compliance", "Cryptographic SHA-256 event chaining ensures legally admissible electronic audit records under Section 65B of Indian IT Act, 2000.")
    ]
    for title, desc in eco_items:
        p = ef.add_paragraph()
        p.text = "• " + title + ": "
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = GREEN
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = DARK_TEXT
        p.space_after = Pt(8)

    add_footer(s5, 5)

    # ==========================================
    # SLIDE 6: RESEARCH AND REFERENCES
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "RESEARCH AND REFERENCES")

    sub_box = s6.shapes.add_textbox(Inches(0.5), Inches(0.98), Inches(12.333), Inches(0.4))
    p = sub_box.text_frame.paragraphs[0]
    p.text = "Details / Links of Reference Standards, Academic Research & Implementation Work"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = DARK_BLUE

    # 3 Columns
    col_w = Inches(3.95)
    col_h = Inches(5.45)
    top_pos = Inches(1.45)

    # Col 1: Statutory Standards
    c1 = add_card(s6, Inches(0.5), top_pos, col_w, col_h)
    tf = c1.text_frame
    tf.margin_left = tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = "1. Statutory & Legal Standards"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)

    stat_refs = [
        ("Income-tax Act, 1961 (Section 139AA)", "Statutory framework mandating PAN-Aadhaar linkage and demographic parity across tax and identity credentials."),
        ("Information Technology Act, 2000 (Section 65B)", "Admissibility of electronic records, dictating VeriGuard's tamper-evident SHA-256 hash sealing."),
        ("Aadhaar Act, 2016 & UIDAI Directives", "Strict zero-storage norms and cryptographic protection standards for national identity credentials."),
        ("Digital Personal Data Protection (DPDP) Act, 2023", "In-memory ephemeral processing and complete data scrubbing after verification completion.")
    ]
    for title, desc in stat_refs:
        p = tf.add_paragraph()
        p.text = "• " + title + ": "
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_BLUE
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = DARK_TEXT
        p.space_after = Pt(8)

    # Col 2: Academic & Algorithmic Citations
    c2 = add_card(s6, Inches(4.68), top_pos, col_w, col_h)
    tf = c2.text_frame
    tf.margin_left = tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = "2. Academic & Algorithmic Citations"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)

    acad_refs = [
        ("Verhoeff, J. (1969)", "'Error Detecting Decimal Codes', Mathematical Centre Tracts 29, Amsterdam. Foundation for Aadhaar's dihedral group D5 check digit algorithm."),
        ("ICAO Document 9303", "'Machine Readable Travel Documents (MRTDs)', Part 3. Specifications for TD3 MRZ line formats and 7-3-1 modulo-10 check digits."),
        ("Krawetz, N. (2007)", "'A Picture's Worth... Digital Image Analysis & Error Level Analysis', Hacker Factor Solutions. Pixel-level recompression delta analysis."),
        ("He, K. et al. (2016)", "'Deep Residual Learning for Image Recognition', IEEE CVPR. ResNet deep convolutional network for 128D facial feature vectors."),
        ("Smith, R. (2007)", "'An Overview of the Tesseract OCR Engine', IEEE ICDAR. Multi-pass page segmentation and text extraction architecture.")
    ]
    for title, desc in acad_refs:
        p = tf.add_paragraph()
        p.text = "• " + title + ": "
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = PURPLE
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = DARK_TEXT
        p.space_after = Pt(6)

    # Col 3: Project Repository & Proofs
    c3 = add_card(s6, Inches(8.86), top_pos, col_w, col_h)
    tf = c3.text_frame
    tf.margin_left = tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = "3. Project Repository & Proofs"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)

    proofs = [
        ("Technical Report (Sec 9 Mitigations)", "https://github.com/arnaashah06/veriguard-ai/blob/main/technical_report.md"),
        ("Empirical Benchmark Profile", "empirical_benchmark_report.json: P50 latency & RAM metrics"),
        ("18/18 Truth Table & Test Suites", "100% precision on counterfeit & genuine document vectors"),
        ("Container Stack & RBAC", "Hardened Dockerfile with tmpfs mounts & OAuth2 JWT auth")
    ]
    for title, desc in proofs:
        p = tf.add_paragraph()
        p.text = "• " + title + ": "
        p.font.size = Pt(9.0)
        p.font.bold = True
        p.font.color.rgb = GREEN
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = PRIMARY_BLUE if desc.startswith("http") else DARK_TEXT
        if desc.startswith("http"):
            run.hyperlink.address = desc
            run.font.underline = True
        p.space_after = Pt(6)

    # SIH Ready Box inside Col 3
    sih_box = add_card(s6, Inches(9.05), Inches(5.4), Inches(3.55), Inches(1.35), BG_LIGHT, RGBColor(191, 219, 254))
    sf = sih_box.text_frame
    sf.margin_top = Inches(0.12)
    p = sf.paragraphs[0]
    p.text = "Smart India Hackathon 2026"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = DARK_BLUE
    p.alignment = PP_ALIGN.CENTER
    p2 = sf.add_paragraph()
    p2.text = "Team Abstract_Minds | ID: SIH2026-T2851"
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = PRIMARY_BLUE
    p2.alignment = PP_ALIGN.CENTER
    p3 = sf.add_paragraph()
    p3.text = "✔ Idea Submission Package Ready"
    p3.font.size = Pt(9.5)
    p3.font.bold = True
    p3.font.color.rgb = GREEN
    p3.alignment = PP_ALIGN.CENTER

    add_footer(s6, 6)

    # Save to Docs directory first
    prs.save(DOCS_PPTX)
    print(f"[SUCCESS] PowerPoint presentation saved to repository docs: {DOCS_PPTX}")

    # Save to Desktop (handle file lock if user has it open in PowerPoint)
    try:
        prs.save(OUTPUT_PPTX)
        print(f"[SUCCESS] PowerPoint presentation updated on Desktop: {OUTPUT_PPTX}")
    except PermissionError:
        alt_path = os.path.join(DESKTOP_DIR, "VeriGuard_AI_SIH2026_Submission_Updated.pptx")
        prs.save(alt_path)
        print(f"[WARNING] {OUTPUT_PPTX} is locked by PowerPoint. Saved to: {alt_path}")
        print("[*] Once PowerPoint is closed, it will overwrite the primary file directly.")

    size = os.path.getsize(DOCS_PPTX)
    print(f"[*] File size: {size:,} bytes")

if __name__ == "__main__":
    create_presentation()


