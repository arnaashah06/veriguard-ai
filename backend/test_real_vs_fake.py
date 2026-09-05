# backend/test_real_vs_fake.py
"""
VeriGuard AI - Real vs. Fake Document Comprehensive Verification Engine
Tests that the system:
1. APPROVES all genuine documents (Low Risk, 0 penalty, valid cryptographic/algorithmic checks)
2. REJECTS/FLAGS all counterfeit, forged, expired, or imposter documents
"""

import os
import sys
import subprocess
import asyncio
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Reconfigure stdout for UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure backend directory is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from fastapi import UploadFile
from validators import (
    DocumentValidator,
    validate_verhoeff,
    generate_verhoeff_check_digit,
    INDIAN_STATE_CODES,
    PAN_ENTITY_TYPES
)
from cross_document import CrossDocumentValidator
from face_verification import FaceVerifier
from main import verify_document, verify_documents
from ocr_tesseract import extract_text_from_image, extract_fields_from_text

TEMP_DIR = os.path.join(CURRENT_DIR, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)
ASSETS_DIR = os.path.join(CURRENT_DIR, "test_assets")
DOC_PORTRAIT = os.path.join(ASSETS_DIR, "doc_portrait.jpg")
SELFIE_MATCH = os.path.join(ASSETS_DIR, "selfie_match.jpg")
SELFIE_MISMATCH = os.path.join(ASSETS_DIR, "selfie_mismatch.jpg")


class TruthTableReporter:
    def __init__(self):
        self.results = []

    def record(self, category: str, test_name: str, doc_nature: str, expected_verdict: str,
               actual_verdict: str, risk_score: int, details: str, passed: bool):
        self.results.append({
            "category": category,
            "test_name": test_name,
            "nature": doc_nature,
            "expected": expected_verdict,
            "actual": actual_verdict,
            "risk_score": risk_score,
            "details": details,
            "passed": passed
        })
        status_symbol = "✅ PASS" if passed else "❌ FAIL"
        color = "\033[92m" if passed else "\033[91m"
        reset = "\033[0m"
        print(f"[{color}{status_symbol}{reset}] {doc_nature:<6} | {test_name:<42} | Exp: {expected_verdict:<8} | Got: {actual_verdict:<8} | Risk: {risk_score:>2} | {details}")

    def print_matrix(self):
        print("\n" + "=" * 115)
        print("                     VERIGUARD AI - REAL vs FAKE TRUTH TABLE & VERIFICATION MATRIX")
        print("=" * 115)
        print(f"{'#':<3} | {'Nature':<6} | {'Document / Scenario':<38} | {'Expected':<8} | {'Decision':<8} | {'Risk':<5} | {'Result':<7}")
        print("-" * 115)

        all_passed = True
        for idx, r in enumerate(self.results, 1):
            passed_str = "PASS" if r["passed"] else "FAIL"
            if not r["passed"]:
                all_passed = False
            print(f"{idx:<3} | {r['nature']:<6} | {r['test_name'][:38]:<38} | {r['expected']:<8} | {r['actual']:<8} | {r['risk_score']:>2}/100 | {passed_str:<7}")

        print("=" * 115)
        total = len(self.results)
        passed_count = sum(1 for r in self.results if r["passed"])
        print(f"Total Test Cases Evaluated: {total}")
        print(f"Successful Verifications  : {passed_count}/{total} ({passed_count/total*100:.1f}%)")
        if all_passed:
            print("Verdict: 100% SUCCESS — System reliably APPROVES authentic docs and REJECTS/FLAGS counterfeit docs! 🎉")
        else:
            print(f"Verdict: ATTENTION — {total - passed_count} test cases failed expectations.")
        print("=" * 115 + "\n")
        return all_passed


# =========================================================================
# IMAGE GENERATION HELPERS FOR REAL & FAKE CARDS
# =========================================================================

def create_image_with_text(output_path, title, lines_of_text, portrait_path=None, bg_color=(248, 250, 252)):
    w, h = 1000, 600
    img = Image.new("RGB", (w, h), color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 28)
        font_body = ImageFont.truetype("arial.ttf", 22)
        font_large = ImageFont.truetype("arial.ttf", 32)
    except Exception:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_large = ImageFont.load_default()

    # Header bar
    draw.rectangle([(0, 0), (w, 70)], fill=(30, 41, 59))
    draw.text((30, 20), title, fill=(255, 255, 255), font=font_title)

    # Portrait photo
    if portrait_path and os.path.exists(portrait_path):
        with Image.open(portrait_path) as p_img:
            p_resized = p_img.resize((220, 260))
            img.paste(p_resized, (50, 110))
            draw.rectangle([(48, 108), (272, 372)], outline=(100, 116, 139), width=2)

    # Draw lines
    x_start = 310 if portrait_path else 50
    y_start = 110
    for line in lines_of_text:
        is_large = "UID" in line or "PAN" in line or "Number" in line
        curr_font = font_large if is_large else font_body
        draw.text((x_start, y_start), line, fill=(15, 23, 42), font=curr_font)
        y_start += 45

    img.save(output_path, quality=95)
    return output_path


# =========================================================================
# MAIN TEST EXECUTION
# =========================================================================

async def main():
    reporter = TruthTableReporter()
    print("\n" + "=" * 95)
    print("      🚀 STARTING COMPREHENSIVE REAL vs. FAKE DOCUMENT AUTHENTICATION SUITE")
    print("=" * 95)

    # ---------------------------------------------------------------------
    # SECTION 1: INDIAN AADHAAR CARD (VERHOEFF CHECKSUM & SECURITY RULES)
    # ---------------------------------------------------------------------
    print("\n[SECTION 1] Indian Aadhaar Card Authentication Tests")
    print("-" * 80)

    # 1.1 Real Aadhaar (Valid Verhoeff UID + UIDAI markings)
    prefix_valid = "36759834521"
    valid_digit = generate_verhoeff_check_digit(prefix_valid)
    valid_uid = f"{prefix_valid[:4]} {prefix_valid[4:8]} {prefix_valid[8:]}{valid_digit}"

    val_real_aadhaar = DocumentValidator({
        "document_type": "Aadhaar Card",
        "name": "Priya Ramesh Patel",
        "dob": "24/11/1992",
        "document_number": valid_uid
    }, raw_text="Government of India Unique Identification Authority of India UIDAI Mera Aadhaar Meri Pehchan")
    f_real_aadhaar, r_real_aadhaar = val_real_aadhaar.validate_all()
    verdict_real_aadhaar = "APPROVE" if r_real_aadhaar < 30 else "REJECT"
    reporter.record(
        category="Aadhaar",
        test_name="Genuine Aadhaar (Verhoeff D5 Valid)",
        doc_nature="REAL",
        expected_verdict="APPROVE",
        actual_verdict=verdict_real_aadhaar,
        risk_score=r_real_aadhaar,
        details=f"UID: {valid_uid} | Verhoeff PASS | Lifetime Validity PASS",
        passed=(verdict_real_aadhaar == "APPROVE" and r_real_aadhaar == 0)
    )

    # 1.2 Fake Aadhaar (Corrupted Verhoeff check digit - counterfeit UID)
    corrupted_digit = (valid_digit + 4) % 10
    fake_uid_corrupt = f"{prefix_valid[:4]} {prefix_valid[4:8]} {prefix_valid[8:]}{corrupted_digit}"
    val_fake_aadhaar_check = DocumentValidator({
        "document_type": "Aadhaar Card",
        "name": "Priya Patel",
        "dob": "24/11/1992",
        "document_number": fake_uid_corrupt
    })
    f_fake_aadhaar, r_fake_aadhaar = val_fake_aadhaar_check.validate_all()
    verdict_fake_aadhaar = "APPROVE" if r_fake_aadhaar < 30 else "REJECT"
    has_verhoeff_fail = any("Verhoeff" in f["check"] and f["status"] == "FAIL" for f in f_fake_aadhaar)
    reporter.record(
        category="Aadhaar",
        test_name="Fake Aadhaar (Corrupted Check Digit)",
        doc_nature="FAKE",
        expected_verdict="REJECT",
        actual_verdict=verdict_fake_aadhaar,
        risk_score=r_fake_aadhaar,
        details=f"Corrupted UID: {fake_uid_corrupt} | Verhoeff FAIL flag triggered (+35 penalty)",
        passed=(verdict_fake_aadhaar == "REJECT" and has_verhoeff_fail and r_fake_aadhaar >= 35)
    )

    # 1.3 Fake Aadhaar (Disallowed leading digit '0' or '1')
    fake_uid_zero = "0675 9834 5212"
    val_fake_zero = DocumentValidator({
        "document_type": "Aadhaar Card",
        "name": "Rohan Deshmukh",
        "dob": "14/03/1990",
        "document_number": fake_uid_zero
    })
    f_fake_zero, r_fake_zero = val_fake_zero.validate_all()
    verdict_fake_zero = "APPROVE" if r_fake_zero < 30 else "REJECT"
    has_range_fail = any("Number Range" in f["check"] and f["status"] == "FAIL" for f in f_fake_zero)
    reporter.record(
        category="Aadhaar",
        test_name="Fake Aadhaar (Forbidden Leading Zero)",
        doc_nature="FAKE",
        expected_verdict="REJECT",
        actual_verdict=verdict_fake_zero,
        risk_score=r_fake_zero,
        details="UIDAI specifies numbers must start with 2-9. Leading 0 penalized (+35)",
        passed=(verdict_fake_zero == "REJECT" and has_range_fail and r_fake_zero >= 35)
    )

    # 1.4 Fake Aadhaar (Truncated / Invalid 10 digits)
    fake_uid_short = "3675 9834 52"
    val_fake_short = DocumentValidator({
        "document_type": "Aadhaar Card",
        "name": "Rohan Deshmukh",
        "dob": "14/03/1990",
        "document_number": fake_uid_short
    })
    f_fake_short, r_fake_short = val_fake_short.validate_all()
    verdict_fake_short = "APPROVE" if r_fake_short < 30 else "REJECT"
    reporter.record(
        category="Aadhaar",
        test_name="Fake Aadhaar (Incomplete 10 Digits)",
        doc_nature="FAKE",
        expected_verdict="REJECT",
        actual_verdict=verdict_fake_short,
        risk_score=r_fake_short,
        details="Must contain 12 digits. Incomplete number penalized (+25)",
        passed=(verdict_fake_short == "REJECT" and r_fake_short >= 25)
    )

    # ---------------------------------------------------------------------
    # SECTION 2: INDIAN PAN CARD (TAX ENTITY & SURNAME ALIGNMENT)
    # ---------------------------------------------------------------------
    print("\n[SECTION 2] Indian PAN Card Authentication Tests")
    print("-" * 80)

    # 2.1 Real PAN Card (Valid 10-char syntax, 4th 'P', 5th matching Surname Patel)
    pan_real = "ABCPP1234F"
    val_real_pan = DocumentValidator({
        "document_type": "PAN Card",
        "name": "Priya Ramesh Patel",
        "dob": "24/11/1992",
        "document_number": pan_real
    }, raw_text="Income Tax Department Govt. of India Permanent Account Number Card")
    f_real_pan, r_real_pan = val_real_pan.validate_all()
    verdict_real_pan = "APPROVE" if r_real_pan < 30 else "REJECT"
    reporter.record(
        category="PAN Card",
        test_name="Genuine PAN (Entity P + Surname Patel)",
        doc_nature="REAL",
        expected_verdict="APPROVE",
        actual_verdict=verdict_real_pan,
        risk_score=r_real_pan,
        details=f"PAN: {pan_real} | Entity: Individual (P) | Surname Initial: 'P' == 'Patel'",
        passed=(verdict_real_pan == "APPROVE" and r_real_pan == 0)
    )

    # 2.2 Fake / Mismatched PAN Card (Surname Initial Mismatch)
    # Cardholder is Arjun Singh (surname initial S), but PAN 5th char is 'P'
    pan_mismatch = "ABCPP1234F"
    val_mismatch_pan = DocumentValidator({
        "document_type": "PAN Card",
        "name": "Arjun Singh",
        "dob": "24/11/1992",
        "document_number": pan_mismatch
    })
    f_mismatch_pan, r_mismatch_pan = val_mismatch_pan.validate_all()
    verdict_mismatch_pan = "APPROVE" if r_mismatch_pan < 20 else "FLAG"
    has_surname_warn = any("Surname Initial" in f["check"] and f["status"] == "WARNING" for f in f_mismatch_pan)
    reporter.record(
        category="PAN Card",
        test_name="Fake PAN (Surname Initial Mismatch)",
        doc_nature="FAKE",
        expected_verdict="FLAG",
        actual_verdict=verdict_mismatch_pan,
        risk_score=r_mismatch_pan,
        details="Holder surname 'Singh' (S) does not match PAN 5th char 'P'. Flagged (+15)",
        passed=(verdict_mismatch_pan == "FLAG" and has_surname_warn and r_mismatch_pan >= 15)
    )

    # 2.3 Fake PAN Card (Invalid 10-char syntax)
    pan_bad_syntax = "AB12345678"
    val_bad_pan = DocumentValidator({
        "document_type": "PAN Card",
        "name": "Vikram Seth",
        "dob": "12/06/1984",
        "document_number": pan_bad_syntax
    })
    f_bad_pan, r_bad_pan = val_bad_pan.validate_all()
    verdict_bad_pan = "APPROVE" if r_bad_pan < 30 else "REJECT"
    reporter.record(
        category="PAN Card",
        test_name="Fake PAN (Malformed Character Syntax)",
        doc_nature="FAKE",
        expected_verdict="REJECT",
        actual_verdict=verdict_bad_pan,
        risk_score=r_bad_pan,
        details="Non-standard PAN structure. Failed regex validation (+30)",
        passed=(verdict_bad_pan == "REJECT" and r_bad_pan >= 30)
    )

    # ---------------------------------------------------------------------
    # SECTION 3: INDIAN DRIVING LICENCE & VOTER ID (EPIC)
    # ---------------------------------------------------------------------
    print("\n[SECTION 3] Indian Driving Licence & Voter ID Tests")
    print("-" * 80)

    # 3.1 Real Indian Driving Licence (Maharashtra MH12)
    dl_real = "MH12 20180012345"
    val_real_dl = DocumentValidator({
        "document_type": "Driving License",
        "name": "Amit Sharma",
        "dob": "10/05/1988",
        "document_number": dl_real,
        "expiry": "15/08/2038"
    })
    f_real_dl, r_real_dl = val_real_dl.validate_all()
    verdict_real_dl = "APPROVE" if r_real_dl < 30 else "REJECT"
    reporter.record(
        category="Driving Licence",
        test_name="Genuine Indian Driving Licence (MH RTO)",
        doc_nature="REAL",
        expected_verdict="APPROVE",
        actual_verdict=verdict_real_dl,
        risk_score=r_real_dl,
        details="Valid Maharashtra state jurisdiction code 'MH' and valid future expiry",
        passed=(verdict_real_dl == "APPROVE" and r_real_dl == 0)
    )

    # 3.2 Fake Indian Driving Licence (Fake state code ZZ)
    dl_fake_state = "ZZ99 20180012345"
    val_fake_dl = DocumentValidator({
        "document_type": "Driving License",
        "name": "Amit Sharma",
        "dob": "10/05/1988",
        "document_number": dl_fake_state,
        "expiry": "15/08/2038"
    })
    f_fake_dl, r_fake_dl = val_fake_dl.validate_all()
    verdict_fake_dl = "APPROVE" if r_fake_dl == 0 else "FLAG"
    has_state_warn = any("State Jurisdiction" in f["check"] and f["status"] == "WARNING" for f in f_fake_dl)
    reporter.record(
        category="Driving Licence",
        test_name="Fake Driving Licence (Non-Existent State ZZ)",
        doc_nature="FAKE",
        expected_verdict="FLAG",
        actual_verdict=verdict_fake_dl,
        risk_score=r_fake_dl,
        details="State code 'ZZ' not in 36 Indian States/UTs. Flagged (+10)",
        passed=(verdict_fake_dl == "FLAG" and has_state_warn)
    )

    # 3.3 Real Voter ID (EPIC format: 3 letters + 7 digits)
    voter_real = "ABC1234567"
    val_real_voter = DocumentValidator({
        "document_type": "Voter ID",
        "name": "Kavita Rao",
        "dob": "18/09/1991",
        "document_number": voter_real
    }, raw_text="Election Commission of India भारत निर्वाचन आयोग Elector Photo Identity Card")
    f_real_voter, r_real_voter = val_real_voter.validate_all()
    verdict_real_voter = "APPROVE" if r_real_voter < 30 else "REJECT"
    reporter.record(
        category="Voter ID",
        test_name="Genuine Voter ID (EPIC Standard)",
        doc_nature="REAL",
        expected_verdict="APPROVE",
        actual_verdict=verdict_real_voter,
        risk_score=r_real_voter,
        details="3 letters + 7 digits EPIC standard recognized and verified",
        passed=(verdict_real_voter == "APPROVE" and r_real_voter == 0)
    )

    # 3.4 Expired Document (Passport expired 2021)
    val_expired_pass = DocumentValidator({
        "document_type": "Passport",
        "name": "John Doe",
        "dob": "01/01/1980",
        "document_number": "P1234567",
        "expiry": "01/01/2021"
    })
    f_exp_pass, r_exp_pass = val_expired_pass.validate_all()
    verdict_exp_pass = "APPROVE" if r_exp_pass < 30 else "REJECT"
    has_expiry_fail = any("Expiry Date" in f["check"] and f["status"] == "FAIL" for f in f_exp_pass)
    reporter.record(
        category="Passport",
        test_name="Expired Document (Past Expiry Date)",
        doc_nature="FAKE",
        expected_verdict="REJECT",
        actual_verdict=verdict_exp_pass,
        risk_score=r_exp_pass,
        details=f"Expired on 01/01/2021 | Expiry FAIL triggered (+30 penalty)",
        passed=(verdict_exp_pass == "REJECT" and has_expiry_fail and r_exp_pass >= 30)
    )

    # ---------------------------------------------------------------------
    # SECTION 4: MULTI-DOCUMENT CROSS-VERIFICATION & STATUTORY LINKAGE
    # ---------------------------------------------------------------------
    print("\n[SECTION 4] Multi-Document Cross-Verification & Identity Reconciliation")
    print("-" * 80)

    cdv = CrossDocumentValidator()

    # 4.1 Real Multi-Doc Pair: Genuine Aadhaar + Genuine PAN (Same Citizen)
    real_multi_docs = [
        {"type": "Aadhaar Card", "name": "Priya Ramesh Patel", "dob": "24/11/1992", "number": valid_uid},
        {"type": "PAN Card", "name": "Priya Ramesh Patel", "dob": "24/11/1992", "number": pan_real}
    ]
    res_real_multi = cdv.evaluate_consistency(real_multi_docs, doc_paths=[DOC_PORTRAIT, DOC_PORTRAIT])
    verdict_real_multi = "APPROVE" if res_real_multi["is_consistent"] and res_real_multi["risk_penalty"] == 0 else "REJECT"
    linkage_info = res_real_multi.get("aadhaar_pan_linkage", {})
    is_linkage_ok = linkage_info.get("is_linked") is True
    reporter.record(
        category="Multi-Doc",
        test_name="Genuine Aadhaar + PAN Pair (Same Citizen)",
        doc_nature="REAL",
        expected_verdict="APPROVE",
        actual_verdict=verdict_real_multi,
        risk_score=res_real_multi["risk_penalty"],
        details=f"Consistency: {res_real_multi['consistency_score']}% | Statutory Aadhaar-PAN Linkage: VERIFIED",
        passed=(verdict_real_multi == "APPROVE" and is_linkage_ok and res_real_multi["consistency_score"] == 100)
    )

    # 4.2 Fake Multi-Doc Pair: Conflicting Identities (Fraudulent / Stolen IDs)
    # Doc 1: Aadhaar for Priya Patel, 1992
    # Doc 2: PAN for Rahul Sharma, 1985
    fake_multi_docs = [
        {"type": "Aadhaar Card", "name": "Priya Ramesh Patel", "dob": "24/11/1992", "number": valid_uid},
        {"type": "PAN Card", "name": "Rahul Vikram Sharma", "dob": "15/08/1985", "number": "ABCPK9876Q"}
    ]
    res_fake_multi = cdv.evaluate_consistency(fake_multi_docs, doc_paths=[DOC_PORTRAIT, DOC_PORTRAIT])
    verdict_fake_multi = "APPROVE" if res_fake_multi["is_consistent"] else "REJECT"
    fake_linkage = res_fake_multi.get("aadhaar_pan_linkage", {})
    linkage_rejected = fake_linkage.get("is_linked") is False
    reporter.record(
        category="Multi-Doc",
        test_name="Fake Multi-Doc Pair (Identity Hijack/Conflict)",
        doc_nature="FAKE",
        expected_verdict="REJECT",
        actual_verdict=verdict_fake_multi,
        risk_score=res_fake_multi["risk_penalty"],
        details=f"Consistency: {res_fake_multi['consistency_score']}% | Conflicting Name/DOB | Inconsistencies: {len(res_fake_multi['inconsistencies'])}",
        passed=(verdict_fake_multi == "REJECT" and linkage_rejected and res_fake_multi["risk_penalty"] >= 30)
    )

    # ---------------------------------------------------------------------
    # SECTION 5: BIOMETRIC FACE VERIFICATION (GENUINE vs IMPOSTER)
    # ---------------------------------------------------------------------
    print("\n[SECTION 5] Biometric Face Verification Engine Tests")
    print("-" * 80)

    face_engine = FaceVerifier(threshold=0.60)

    # 5.1 Real Biometric Match (Genuine cardholder portrait vs matching selfie)
    match_res = face_engine.verify_face(DOC_PORTRAIT, SELFIE_MATCH)
    is_face_match = match_res.get("is_match", False)
    verdict_match = "APPROVE" if is_face_match else "REJECT"
    reporter.record(
        category="Biometrics",
        test_name="Biometric Face Match (Authentic Cardholder)",
        doc_nature="REAL",
        expected_verdict="APPROVE",
        actual_verdict=verdict_match,
        risk_score=0 if is_face_match else 25,
        details=f"Match Score: {match_res.get('match_score')}% | Distance: {match_res.get('distance')} (<=0.40)",
        passed=(is_face_match and match_res.get("match_score", 0) >= 75)
    )

    # 5.2 Fake Biometric Match (Imposter selfie vs document portrait)
    mismatch_res = face_engine.verify_face(DOC_PORTRAIT, SELFIE_MISMATCH)
    is_imposter_blocked = not mismatch_res.get("is_match", True)
    verdict_imposter = "REJECT" if is_imposter_blocked else "APPROVE"
    reporter.record(
        category="Biometrics",
        test_name="Biometric Imposter Rejection (Different Person)",
        doc_nature="FAKE",
        expected_verdict="REJECT",
        actual_verdict=verdict_imposter,
        risk_score=25 if is_imposter_blocked else 0,
        details=f"Match Score: {mismatch_res.get('match_score')}% | Distance: {mismatch_res.get('distance')} (>0.40)",
        passed=is_imposter_blocked
    )

    # ---------------------------------------------------------------------
    # SECTION 6: END-TO-END OCR & API ENDPOINT VERIFICATION (REAL vs FAKE)
    # ---------------------------------------------------------------------
    print("\n[SECTION 6] End-to-End Image Generation, OCR & FastAPI Pipeline Tests")
    print("-" * 80)

    # 6.1 Generate Synthetic Genuine Aadhaar Card Image
    real_aadhaar_img = os.path.join(TEMP_DIR, "real_aadhaar_test.png")
    create_image_with_text(
        output_path=real_aadhaar_img,
        title="UNIQUE IDENTIFICATION AUTHORITY OF INDIA",
        lines_of_text=[
            "Government of India / भारत सरकार",
            "Mera Aadhaar, Meri Pehchan",
            "Name: Priya Ramesh Patel",
            "DOB: 24/11/1992",
            "Gender: Female",
            f"UID: {valid_uid}"
        ],
        portrait_path=DOC_PORTRAIT
    )

    with open(real_aadhaar_img, "rb") as f:
        real_aadhaar_bytes = f.read()
    with open(SELFIE_MATCH, "rb") as f:
        selfie_match_bytes = f.read()

    upload_doc_real = UploadFile(
        filename="real_aadhaar.png",
        file=BytesIO(real_aadhaar_bytes),
        headers={"content-type": "image/png"}
    )
    upload_selfie_real = UploadFile(
        filename="matching_selfie.jpg",
        file=BytesIO(selfie_match_bytes),
        headers={"content-type": "image/jpeg"}
    )

    api_real_res = await verify_document(file=upload_doc_real, selfie=upload_selfie_real)
    api_real_verdict = "APPROVE" if api_real_res.get("overall_risk") == "LOW" else "REJECT"
    reporter.record(
        category="E2E Pipeline",
        test_name="E2E API: Genuine Aadhaar Image + Selfie",
        doc_nature="REAL",
        expected_verdict="APPROVE",
        actual_verdict=api_real_verdict,
        risk_score=api_real_res.get("risk_score", 0),
        details=f"Type: {api_real_res.get('document', {}).get('type')} | Risk: {api_real_res.get('overall_risk')} | Face: {api_real_res.get('face_match', {}).get('score')}%",
        passed=(api_real_verdict == "APPROVE" and api_real_res.get("risk_score", 0) <= 20)
    )

    # 6.2 Generate Synthetic Fake Aadhaar Card Image (Corrupted Verhoeff digit)
    fake_aadhaar_img = os.path.join(TEMP_DIR, "fake_aadhaar_test.png")
    create_image_with_text(
        output_path=fake_aadhaar_img,
        title="UNIQUE IDENTIFICATION AUTHORITY OF INDIA",
        lines_of_text=[
            "Government of India / भारत सरकार",
            "Mera Aadhaar, Meri Pehchan",
            "Name: Priya Ramesh Patel",
            "DOB: 24/11/1992",
            "Gender: Female",
            f"UID: {fake_uid_corrupt}"
        ],
        portrait_path=DOC_PORTRAIT
    )

    with open(fake_aadhaar_img, "rb") as f:
        fake_aadhaar_bytes = f.read()

    upload_doc_fake = UploadFile(
        filename="fake_aadhaar.png",
        file=BytesIO(fake_aadhaar_bytes),
        headers={"content-type": "image/png"}
    )

    api_fake_res = await verify_document(file=upload_doc_fake, selfie=None)
    api_fake_verdict = "APPROVE" if api_fake_res.get("overall_risk") == "LOW" else "REJECT"
    reporter.record(
        category="E2E Pipeline",
        test_name="E2E API: Fake Aadhaar Image (Tampered UID)",
        doc_nature="FAKE",
        expected_verdict="REJECT",
        actual_verdict=api_fake_verdict,
        risk_score=api_fake_res.get("risk_score", 0),
        details=f"Risk: {api_fake_res.get('overall_risk')} (Score: {api_fake_res.get('risk_score')}) | Escalated: {api_fake_res.get('human_review_required')}",
        passed=(api_fake_verdict == "REJECT" and api_fake_res.get("risk_score", 0) >= 30)
    )

    # 6.3 Multi-Document E2E: Genuine Aadhaar + Genuine PAN (Same Citizen)
    real_pan_img = os.path.join(TEMP_DIR, "real_pan_test.png")
    create_image_with_text(
        output_path=real_pan_img,
        title="INCOME TAX DEPARTMENT - GOVT OF INDIA",
        lines_of_text=[
            "Permanent Account Number Card",
            "Name: Priya Ramesh Patel",
            "Father: Ramesh Patel",
            "DOB: 24/11/1992",
            f"PAN Number: {pan_real}"
        ],
        portrait_path=DOC_PORTRAIT
    )

    with open(real_pan_img, "rb") as f:
        real_pan_bytes = f.read()

    multi_doc1 = UploadFile(filename="real_aadhaar.png", file=BytesIO(real_aadhaar_bytes), headers={"content-type": "image/png"})
    multi_doc2 = UploadFile(filename="real_pan.png", file=BytesIO(real_pan_bytes), headers={"content-type": "image/png"})

    api_multi_res = await verify_documents(files=[multi_doc1, multi_doc2], selfie=None)
    multi_verdict = "APPROVE" if api_multi_res.get("overall_risk") == "LOW" else "REJECT"
    cross_report = api_multi_res.get("cross_document", {})
    reporter.record(
        category="E2E Pipeline",
        test_name="E2E API: Multi-Doc Aadhaar + PAN Approval",
        doc_nature="REAL",
        expected_verdict="APPROVE",
        actual_verdict=multi_verdict,
        risk_score=api_multi_res.get("risk_score", 0),
        details=f"Consistency: {cross_report.get('consistency_score')}% | Statutory Linkage: {cross_report.get('aadhaar_pan_linkage', {}).get('is_linked')}",
        passed=(multi_verdict == "APPROVE" and cross_report.get("is_consistent") is True)
    )

    # Clean up generated test images
    for p in [real_aadhaar_img, fake_aadhaar_img, real_pan_img]:
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass

    # Print final truth table summary matrix
    success = reporter.print_matrix()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
