# backend/generate_demo_assets.py
"""
VeriGuard AI - Automated Demonstration Asset Generator
Generates realistic, high-resolution document images for:
1. Scenario 1: Clean Indian KYC (Genuine Aadhaar + Genuine PAN + Matching Selfie)
2. Scenario 2: Counterfeit Aadhaar (Tampered Verhoeff Check Digit)
3. Scenario 3: Synthetic Identity Conflict (Aadhaar Person A + PAN Person B + Imposter Selfie)
Saves fixtures to both backend/test_assets/demo/ and frontend/public/demo_assets/
"""

import os
import sys
import shutil
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_PUBLIC_DEMO = os.path.join(CURRENT_DIR, "..", "frontend", "public", "demo_assets")
BACKEND_DEMO = os.path.join(CURRENT_DIR, "test_assets", "demo")

os.makedirs(FRONTEND_PUBLIC_DEMO, exist_ok=True)
os.makedirs(BACKEND_DEMO, exist_ok=True)

DOC_PORTRAIT_A = os.path.join(CURRENT_DIR, "test_assets", "doc_portrait.jpg")
SELFIE_MATCH_A = os.path.join(CURRENT_DIR, "test_assets", "selfie_match.jpg")
SELFIE_MISMATCH_B = os.path.join(CURRENT_DIR, "test_assets", "selfie_mismatch.jpg")


def draw_card(output_path, header_text, lines, portrait_path=None, theme="aadhaar"):
    w, h = 1000, 600

    if theme == "aadhaar":
        bg_color = (255, 255, 255)
        header_bg = (234, 88, 12)  # Indian saffron/orange
        accent_color = (22, 101, 52) # green bottom stripe
    elif theme == "pan":
        bg_color = (248, 250, 252)
        header_bg = (30, 58, 138)  # IT Dept navy blue
        accent_color = (217, 119, 6) # gold
    elif theme == "counterfeit":
        bg_color = (254, 242, 242)
        header_bg = (185, 28, 28)  # warning crimson
        accent_color = (153, 27, 27)
    else:
        bg_color = (248, 250, 252)
        header_bg = (30, 41, 59)
        accent_color = (71, 85, 105)

    img = Image.new("RGB", (w, h), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Header bar
    draw.rectangle([(0, 0), (w, 80)], fill=header_bg)

    try:
        font_header = ImageFont.truetype("arial.ttf", 26)
        font_body = ImageFont.truetype("arial.ttf", 22)
        font_bold = ImageFont.truetype("arial.ttf", 30)
    except Exception:
        font_header = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_bold = ImageFont.load_default()

    draw.text((30, 25), header_text, fill=(255, 255, 255), font=font_header)

    # Portrait photo
    if portrait_path and os.path.exists(portrait_path):
        with Image.open(portrait_path) as p_img:
            p_resized = p_img.resize((240, 290))
            img.paste(p_resized, (50, 120))
            draw.rectangle([(48, 118), (292, 412)], outline=(148, 163, 184), width=3)

    # Content
    x_pos = 330 if portrait_path else 60
    y_pos = 120
    for line in lines:
        is_highlight = any(k in line for k in ["UID", "PAN", "Number", "3675", "ABCPP", "ABCPK"])
        font_to_use = font_bold if is_highlight else font_body
        text_color = (15, 23, 42) if not is_highlight else (30, 58, 138)
        draw.text((x_pos, y_pos), line, fill=text_color, font=font_to_use)
        y_pos += 46

    # Bottom security accent stripe
    draw.rectangle([(0, h - 18), (w, h)], fill=accent_color)

    img.save(output_path, quality=95)
    return output_path


def copy_to_both(src_file, filename):
    dest_front = os.path.join(FRONTEND_PUBLIC_DEMO, filename)
    dest_back = os.path.join(BACKEND_DEMO, filename)
    shutil.copyfile(src_file, dest_front)
    shutil.copyfile(src_file, dest_back)
    print(f"  [+] Saved {filename} -> frontend & backend demo assets")


def generate_all():
    print("=" * 65)
    print("🎨 GENERATING VERIGUARD DEMO SCENARIO ASSETS")
    print("=" * 65)

    tmp_sc1_aadh = os.path.join(CURRENT_DIR, "temp", "tmp_demo_aadhaar_clean.png")
    tmp_sc1_pan = os.path.join(CURRENT_DIR, "temp", "tmp_demo_pan_clean.png")
    tmp_sc2_fake = os.path.join(CURRENT_DIR, "temp", "tmp_demo_aadhaar_fake.png")
    tmp_sc3_pan = os.path.join(CURRENT_DIR, "temp", "tmp_demo_pan_conflict.png")

    # 1. SCENARIO 1: Clean Indian KYC
    print("\n[Scenario 1] Clean Indian KYC (Aadhaar + PAN + Selfie)")
    draw_card(
        output_path=tmp_sc1_aadh,
        header_text="GOVERNMENT OF INDIA / UIDAI - AADHAAR",
        lines=[
            "Unique Identification Authority of India",
            "Mera Aadhaar, Meri Pehchan",
            "Name: Priya Ramesh Patel",
            "DOB: 24/11/1992",
            "Gender: Female",
            "UID: 3675 9834 5212"
        ],
        portrait_path=DOC_PORTRAIT_A,
        theme="aadhaar"
    )
    copy_to_both(tmp_sc1_aadh, "demo_aadhaar_clean.png")

    draw_card(
        output_path=tmp_sc1_pan,
        header_text="INCOME TAX DEPARTMENT - GOVT OF INDIA",
        lines=[
            "Permanent Account Number Card",
            "Name: Priya Ramesh Patel",
            "Father's Name: Ramesh Patel",
            "DOB: 24/11/1992",
            "PAN: ABCPP1234F"
        ],
        portrait_path=DOC_PORTRAIT_A,
        theme="pan"
    )
    copy_to_both(tmp_sc1_pan, "demo_pan_clean.png")
    copy_to_both(SELFIE_MATCH_A, "demo_selfie_match.jpg")

    # 2. SCENARIO 2: Counterfeit Aadhaar Alert
    print("\n[Scenario 2] Counterfeit Aadhaar (Tampered Verhoeff Check Digit)")
    draw_card(
        output_path=tmp_sc2_fake,
        header_text="GOVERNMENT OF INDIA / UIDAI - AADHAAR",
        lines=[
            "Unique Identification Authority of India",
            "Mera Aadhaar, Meri Pehchan",
            "Name: Priya Ramesh Patel",
            "DOB: 24/11/1992",
            "Gender: Female",
            "UID: 3675 9834 5216"  # Corrupted 12th digit
        ],
        portrait_path=DOC_PORTRAIT_A,
        theme="counterfeit"
    )
    copy_to_both(tmp_sc2_fake, "demo_aadhaar_counterfeit.png")

    # 3. SCENARIO 3: Identity Conflict (Person A Aadhaar + Person B PAN + Imposter Selfie)
    print("\n[Scenario 3] Identity Conflict & Imposter Biometrics")
    copy_to_both(tmp_sc1_aadh, "demo_aadhaar_person_a.png")

    draw_card(
        output_path=tmp_sc3_pan,
        header_text="INCOME TAX DEPARTMENT - GOVT OF INDIA",
        lines=[
            "Permanent Account Number Card",
            "Name: Rahul Vikram Sharma",
            "Father's Name: Vikram Sharma",
            "DOB: 15/08/1985",
            "PAN: ABCPK9876Q"
        ],
        portrait_path=SELFIE_MISMATCH_B,
        theme="pan"
    )
    copy_to_both(tmp_sc3_pan, "demo_pan_person_b.png")
    copy_to_both(SELFIE_MISMATCH_B, "demo_selfie_imposter.jpg")

    # Clean up temp files
    for p in [tmp_sc1_aadh, tmp_sc1_pan, tmp_sc2_fake, tmp_sc3_pan]:
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass

    print("\n" + "=" * 65)
    print("✅ DEMO SCENARIO ASSETS GENERATED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    generate_all()
