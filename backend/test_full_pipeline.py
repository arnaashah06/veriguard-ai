# backend/test_full_pipeline.py
"""
VeriGuard AI - Complete Pipeline Verification & Regression Test Suite
Tests OCR Extraction, MRZ Parsing, Biometric Face Verification, and FastAPI Endpoints.
Can be run standalone or as part of CI/CD.
"""

import os
import sys
import subprocess

# Auto-re-execute using the project virtualenv if running under global/system Python
_here = os.path.dirname(os.path.abspath(__file__))
_venv_candidates = [
    os.path.join(_here, "venv", "Scripts", "python.exe"),
    os.path.join(_here, "backend", "venv", "Scripts", "python.exe"),
    os.path.join(_here, "..", "backend", "venv", "Scripts", "python.exe"),
    r"C:\Users\pc\Desktop\veriguard-ai\backend\venv\Scripts\python.exe"
]
_target_py = None
for _v in _venv_candidates:
    if os.path.isfile(_v):
        _target_py = _v
        break

if _target_py and os.path.normcase(sys.executable) != os.path.normcase(_target_py):
    res = subprocess.run([_target_py] + sys.argv)
    sys.exit(res.returncode)

import time
import asyncio
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Reconfigure UTF-8 stdout on Windows to support emojis & status markers safely
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure backend directory is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from fastapi import UploadFile, HTTPException
from main import verify_document
from ocr_tesseract import extract_text_from_image, extract_fields_from_text, parse_mrz
from face_verification import FaceVerifier

TEST_ASSETS_DIR = os.path.join(CURRENT_DIR, "test_assets")
TEMP_DIR = os.path.join(CURRENT_DIR, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

DOC_PORTRAIT_PATH = os.path.join(TEST_ASSETS_DIR, "doc_portrait.jpg")
SELFIE_MATCH_PATH = os.path.join(TEST_ASSETS_DIR, "selfie_match.jpg")
SELFIE_MISMATCH_PATH = os.path.join(TEST_ASSETS_DIR, "selfie_mismatch.jpg")


# ==========================================
# TEST FIXTURE GENERATORS
# ==========================================

def create_synthetic_passport(output_path, portrait_path=None):
    """
    Generate a realistic passport document image containing:
    - Official header
    - Person photo
    - Visual text fields (Name, Passport No, DOB, Expiry)
    - ICAO 9303 standard 2-line TD3 MRZ code
    """
    w, h = 1200, 800
    img = Image.new("RGB", (w, h), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)

    # Decorative header
    draw.rectangle([(0, 0), (w, 80)], fill=(30, 58, 138))

    # Font setup with safe fallbacks
    try:
        font_large = ImageFont.truetype("arial.ttf", 32)
        font_med = ImageFont.truetype("arial.ttf", 24)
        font_mrz = ImageFont.truetype("arial.ttf", 30)
    except Exception:
        font_large = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_mrz = ImageFont.load_default()

    draw.text((40, 24), "PASSPORT - REPUBLIC OF UTOPIA", fill=(255, 255, 255), font=font_large)

    # Paste portrait photo if available
    if portrait_path and os.path.exists(portrait_path):
        with Image.open(portrait_path) as p_img:
            p_resized = p_img.resize((320, 380))
            img.paste(p_resized, (60, 140))
            draw.rectangle([(58, 138), (382, 522)], outline=(148, 163, 184), width=2)
    else:
        # Gray placeholder frame if photo absent
        draw.rectangle([(60, 140), (380, 520)], fill=(226, 232, 240), outline=(148, 163, 184), width=2)
        draw.text((160, 320), "PHOTO", fill=(100, 116, 139), font=font_med)

    # Visual field lines
    fields_x = 420
    draw.text((fields_x, 140), "Type: P", fill=(15, 23, 42), font=font_med)
    draw.text((fields_x, 190), "Passport No: L898902C3", fill=(15, 23, 42), font=font_med)
    draw.text((fields_x, 240), "Full Name: ANNA MARIA ERIKSSON", fill=(15, 23, 42), font=font_med)
    draw.text((fields_x, 290), "Nationality: UTOPIAN", fill=(15, 23, 42), font=font_med)
    draw.text((fields_x, 340), "Date of Birth: 12/08/1974", fill=(15, 23, 42), font=font_med)
    draw.text((fields_x, 390), "Date of Expiry: 15/04/2028", fill=(15, 23, 42), font=font_med)
    draw.text((fields_x, 440), "Sex: F", fill=(15, 23, 42), font=font_med)

    # ICAO 9303 2-Line TD3 MRZ Zone
    mrz_y = 650
    draw.rectangle([(40, 630), (w - 40, 780)], fill=(255, 255, 255))
    draw.text((50, mrz_y), "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<", fill=(0, 0, 0), font=font_mrz)
    draw.text((50, mrz_y + 65), "L898902C36UTO7408122F2804154<<<<<<<<<<<<<<06", fill=(0, 0, 0), font=font_mrz)

    img.save(output_path, "PNG")
    return output_path

def create_upload_file(file_path, field_name="file"):
    """Wrap a disk file into a simulated FastAPI UploadFile."""
    with open(file_path, "rb") as f:
        content = f.read()
    content_type = "image/png" if file_path.endswith(".png") else "image/jpeg"
    return UploadFile(
        filename=os.path.basename(file_path),
        file=BytesIO(content),
        headers={"content-type": content_type}
    )


# ==========================================
# TEST RUNNER & SUITES
# ==========================================

class PipelineTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_names = []

    def report(self, test_name, success, details=""):
        self.test_names.append(test_name)
        if success:
            self.passed += 1
            print(f"  [PASS] {test_name} {f'({details})' if details else ''}")
        else:
            self.failed += 1
            print(f"  [FAIL] {test_name} {f'({details})' if details else ''}")

    def summary(self, duration):
        total = self.passed + self.failed
        print("\n" + "=" * 65)
        print("                 PIPELINE TEST SUMMARY REPORT")
        print("=" * 65)
        print(f"  Total Test Cases : {total}")
        print(f"  Passed           : {self.passed}")
        print(f"  Failed           : {self.failed}")
        print(f"  Total Duration   : {duration:.2f}s")
        if self.failed == 0:
            print("  Status           : 100% HEALTHY - ALL TESTS PASSED! 🎉")
        else:
            print(f"  Status           : ATTENTION NEEDED - {self.failed} FAILED")
        print("=" * 65 + "\n")
        return self.failed == 0


async def main():
    tester = PipelineTester()
    start_time = time.time()

    print("\n" + "#" * 65)
    print("   VERIGUARD AI - FULL PIPELINE AUTOMATED TEST SUITE")
    print("#" * 65)

    # ----------------------------------------------------
    # SUITE 1: OCR & FIELD EXTRACTION UNIT TESTS
    # ----------------------------------------------------
    print("\n[SUITE 1] OCR Extraction & Field Normalization Tests")
    print("-" * 55)

    # 1.1 MRZ Parsing
    raw_mrz = (
        "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<\n"
        "L898902C36UTO7408122F2804154<<<<<<<<<<<<<<06"
    )
    mrz_res = parse_mrz(raw_mrz)
    mrz_ok = (
        mrz_res is not None and
        mrz_res.get("document_type") == "Passport" and
        mrz_res.get("document_number") == "L898902C3" and
        mrz_res.get("name") == "ANNA MARIA ERIKSSON" and
        mrz_res.get("dob") == "12/08/1974" and
        mrz_res.get("expiry") == "15/04/2028"
    )
    tester.report("MRZ ICAO 9303 Parsing", mrz_ok, "Extracted Name, Passport No, DOB, Expiry")

    # 1.2 Aadhaar Format Extraction
    aadhaar_text = (
        "Government of India\n"
        "Priya Ramesh Patel\n"
        "DOB: 24/11/1992\n"
        "Female\n"
        "9876 5432 1098\n"
        "Mera Aadhaar, Meri Pehchan"
    )
    f_aadhaar = extract_fields_from_text(aadhaar_text)
    aadhaar_ok = (
        f_aadhaar.get("document_type") == "Aadhaar Card" and
        f_aadhaar.get("document_number") == "9876 5432 1098" and
        f_aadhaar.get("dob") == "24/11/1992" and
        "Priya" in f_aadhaar.get("name", "")
    )
    tester.report("Aadhaar Card Extraction", aadhaar_ok, f"{f_aadhaar.get('name')} | {f_aadhaar.get('document_number')}")

    # 1.3 PAN Card Format Extraction
    pan_text = (
        "INCOME TAX DEPARTMENT\n"
        "GOVT. OF INDIA\n"
        "Permanent Account Number\n"
        "ABCDE1234F\n"
        "Name: ARJUN SINGH\n"
        "Date of Birth: 05/06/1985\n"
    )
    f_pan = extract_fields_from_text(pan_text)
    pan_ok = (
        f_pan.get("document_type") == "PAN Card" and
        f_pan.get("document_number") == "ABCDE1234F" and
        f_pan.get("name") == "ARJUN SINGH" and
        f_pan.get("dob") == "05/06/1985"
    )
    tester.report("PAN Card Extraction", pan_ok, f"Doc No: {f_pan.get('document_number')}")

    # 1.4 Synthetic Document OCR from Image
    test_passport_img = os.path.join(TEMP_DIR, "test_ocr_doc.png")
    create_synthetic_passport(test_passport_img, portrait_path=DOC_PORTRAIT_PATH)
    
    ocr_extracted = extract_text_from_image(test_passport_img)
    ocr_has_text = len(ocr_extracted) >= 100
    tester.report("Tesseract OCR Execution", ocr_has_text, f"{len(ocr_extracted)} chars extracted")

    img_fields = extract_fields_from_text(ocr_extracted)
    img_fields_ok = (
        img_fields.get("document_type") == "Passport" and
        img_fields.get("document_number") == "L898902C3" and
        "ERIKSSON" in img_fields.get("name", "").upper()
    )
    tester.report("Image Document Field Extraction", img_fields_ok, f"Name: {img_fields.get('name')}")

    # ----------------------------------------------------
    # SUITE 2: BIOMETRIC FACE VERIFICATION TESTS
    # ----------------------------------------------------
    print("\n[SUITE 2] Biometric Face Verification Engine Tests")
    print("-" * 55)

    verifier = FaceVerifier(threshold=0.60)

    # 2.1 Same person matching test (Portrait vs Matching Selfie)
    res_match = verifier.verify_face(DOC_PORTRAIT_PATH, SELFIE_MATCH_PATH)
    same_person_ok = (
        res_match.get("success") == True and
        res_match.get("is_match") == True and
        res_match.get("match_score", 0) >= 70.0 and
        res_match.get("confidence") in ["HIGH", "MEDIUM"]
    )
    tester.report(
        "Face Matching (Same Person)",
        same_person_ok,
        f"Score: {res_match.get('match_score')}% | Dist: {res_match.get('distance')}"
    )

    # 2.2 Different person mismatch test (Portrait vs Mismatch Selfie)
    res_mismatch = verifier.verify_face(DOC_PORTRAIT_PATH, SELFIE_MISMATCH_PATH)
    diff_person_ok = (
        res_mismatch.get("success") == True and
        res_mismatch.get("is_match") == False and
        res_mismatch.get("match_score", 0) < 50.0
    )
    tester.report(
        "Face Rejection (Different Persons)",
        diff_person_ok,
        f"Score: {res_mismatch.get('match_score')}% | Dist: {res_mismatch.get('distance')}"
    )

    # 2.3 Non-existent image error handling
    res_missing = verifier.verify_face("non_existent_file.jpg", SELFIE_MATCH_PATH)
    missing_ok = (res_missing.get("success") == False and res_missing.get("is_match") == False)
    tester.report("Face Verification Missing File Handling", missing_ok, res_missing.get("error", ""))

    # ----------------------------------------------------
    # SUITE 3: END-TO-END FASTAPI VERIFICATION PIPELINE
    # ----------------------------------------------------
    print("\n[SUITE 3] End-to-End API Pipeline Tests")
    print("-" * 55)

    # 3.1 Verify with Document + Matching Selfie
    upload_doc1 = create_upload_file(test_passport_img)
    upload_selfie1 = create_upload_file(SELFIE_MATCH_PATH)
    api_res1 = await verify_document(file=upload_doc1, selfie=upload_selfie1)

    api1_ok = (
        api_res1.get("status") == "success" and
        "ERIKSSON" in api_res1.get("document", {}).get("name", "").upper() and
        api_res1.get("document", {}).get("number") == "L898902C3" and
        api_res1.get("face_match", {}).get("passed") == True and
        api_res1.get("overall_risk") == "LOW"
    )
    tester.report(
        "API: Verify Document + Matching Selfie",
        api1_ok,
        f"Risk: {api_res1.get('overall_risk')} | Face Match: {api_res1.get('face_match', {}).get('score')}%"
    )

    # 3.2 Verify with Document + Mismatching Selfie (Biometric Penalty)
    upload_doc2 = create_upload_file(test_passport_img)
    upload_selfie2 = create_upload_file(SELFIE_MISMATCH_PATH)
    api_res2 = await verify_document(file=upload_doc2, selfie=upload_selfie2)

    api2_ok = (
        api_res2.get("status") == "success" and
        api_res2.get("face_match", {}).get("passed") == False and
        any(f.get("check") == "Face Verification" and f.get("status") == "FAIL" for f in api_res2.get("findings", [])) and
        api_res2.get("risk_score", 0) >= 25
    )
    tester.report(
        "API: Verify Document + Mismatched Selfie",
        api2_ok,
        f"Risk Score: {api_res2.get('risk_score')} (Penalized +25 for Face Mismatch)"
    )

    # 3.3 Verify Document Only (Selfie is Optional)
    upload_doc3 = create_upload_file(test_passport_img)
    api_res3 = await verify_document(file=upload_doc3, selfie=None)

    api3_ok = (
        api_res3.get("status") == "success" and
        api_res3.get("face_match", {}).get("passed") == False and
        "not provided" in api_res3.get("face_match", {}).get("message", "").lower() and
        api_res3.get("risk_score", 0) == 0
    )
    tester.report(
        "API: Verify Document Only (Optional Selfie)",
        api3_ok,
        "Neutral face match response, 0 risk penalty"
    )

    # 3.4 Unsupported file format validation
    invalid_file = UploadFile(
        filename="malicious.exe",
        file=BytesIO(b"fake data"),
        headers={"content-type": "application/x-msdownload"}
    )
    format_rejected = False
    try:
        await verify_document(file=invalid_file)
    except HTTPException as e:
        if e.status_code == 400:
            format_rejected = True
    tester.report("API: Unsupported File Format Rejection", format_rejected, "HTTP 400 returned")

    # ----------------------------------------------------
    # SUITE 4: CLEANUP & RESOURCE MANAGEMENT
    # ----------------------------------------------------
    print("\n[SUITE 4] Resource Cleanup & File Locking Tests")
    print("-" * 55)

    if os.path.exists(test_passport_img):
        try:
            os.remove(test_passport_img)
            cleanup_ok = True
        except Exception as e:
            cleanup_ok = False
            print(f"[!] Cleanup error: {e}")
    else:
        cleanup_ok = True

    # Check temp dir has 0 leaked files
    temp_files = os.listdir(TEMP_DIR)
    no_leaks = len(temp_files) == 0
    tester.report("Temporary File Cleanup", cleanup_ok and no_leaks, f"{len(temp_files)} files remaining in temp/")

    # ----------------------------------------------------
    # FINAL SUMMARY
    # ----------------------------------------------------
    duration = time.time() - start_time
    all_ok = tester.summary(duration)
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    asyncio.run(main())
