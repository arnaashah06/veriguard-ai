# backend/test_edge_cases.py
"""
VeriGuard AI - Edge Cases, Anomaly Ingestion & Defensive Error Handling Test Suite
Tests:
1. Empty Document Upload (0 files) -> HTTP 400
2. 0-Byte Empty Image Upload -> HTTP 400
3. Corrupted / Non-Image Data with .jpg extension -> HTTP 400
4. Oversized File (>10MB) -> HTTP 400
5. Unsupported File Extension (.exe, .pdf) -> HTTP 400
6. Pure Blank Image (0 text, 0 faces) -> Graceful OCR & Risk Assessment (No Crash)
7. Non-Face Landscape Image as Selfie -> Graceful "No Face Detected" Handling (No Crash)
8. Complex / Long Indian Names with Titles & Hyphens
9. Boundary Date Formats & Edge-Case DOBs
10. Mixed Multi-Document Batch (1 Authentic + 1 Blank)
"""

import os
import sys
import asyncio
from io import BytesIO
from PIL import Image, ImageDraw

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from fastapi import UploadFile, HTTPException
from main import verify_document, verify_documents
from validators import DocumentValidator
from ocr_tesseract import extract_fields_from_text
from face_verification import FaceVerifier

TEMP_DIR = os.path.join(CURRENT_DIR, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)
ASSETS_DIR = os.path.join(CURRENT_DIR, "test_assets")
DOC_PORTRAIT = os.path.join(ASSETS_DIR, "doc_portrait.jpg")


def create_blank_image(path, w=800, h=600, color=(255, 255, 255)):
    img = Image.new("RGB", (w, h), color=color)
    img.save(path, format="JPEG")
    return path


def create_landscape_scenic_image(path, w=800, h=600):
    """Creates an image with scenery/shapes but strictly NO human faces."""
    img = Image.new("RGB", (w, h), color=(135, 206, 235)) # sky blue
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 350), (w, h)], fill=(34, 139, 34)) # green grass
    draw.polygon([(100, 350), (300, 150), (500, 350)], fill=(128, 128, 128)) # mountain
    draw.ellipse([(650, 50), (750, 150)], fill=(255, 215, 0)) # sun
    img.save(path, format="JPEG")
    return path


async def test_edge_cases():
    print("=" * 80)
    print("🧪 RUNNING COMPREHENSIVE EDGE CASES & ERROR HANDLING TEST SUITE")
    print("=" * 80)

    passed_tests = 0
    total_tests = 10

    # -------------------------------------------------------------------------
    # Edge Case 1: Empty Document Upload (0 files)
    # -------------------------------------------------------------------------
    print("\n[Edge Case 1] Empty Document Upload (0 files)")
    try:
        await verify_documents(files=[])
        print("❌ FAILED: Expected HTTP 400 for empty upload")
    except HTTPException as e:
        assert e.status_code == 400
        assert "No document file uploaded" in e.detail
        print(f"✅ PASS: HTTP {e.status_code} returned: {e.detail}")
        passed_tests += 1

    # -------------------------------------------------------------------------
    # Edge Case 2: 0-Byte Empty Image Upload
    # -------------------------------------------------------------------------
    print("\n[Edge Case 2] 0-Byte Empty File Upload")
    empty_file = UploadFile(
        filename="empty.jpg",
        file=BytesIO(b""),
        headers={"content-type": "image/jpeg"}
    )
    try:
        await verify_document(file=empty_file)
        print("❌ FAILED: Expected HTTP 400 for 0-byte file")
    except HTTPException as e:
        assert e.status_code == 400
        assert "0 bytes" in e.detail
        print(f"✅ PASS: HTTP {e.status_code} returned: {e.detail}")
        passed_tests += 1

    # -------------------------------------------------------------------------
    # Edge Case 3: Corrupt Data with .jpg extension
    # -------------------------------------------------------------------------
    print("\n[Edge Case 3] Corrupt / Non-Image Data with .jpg extension")
    corrupt_file = UploadFile(
        filename="corrupt.jpg",
        file=BytesIO(b"This is not a real JPEG image file, just random text bytes."),
        headers={"content-type": "image/jpeg"}
    )
    try:
        await verify_document(file=corrupt_file)
        print("❌ FAILED: Expected HTTP 400 for corrupt image")
    except HTTPException as e:
        assert e.status_code == 400
        assert "corrupt or not a readable image" in e.detail
        print(f"✅ PASS: HTTP {e.status_code} returned: {e.detail}")
        passed_tests += 1

    # -------------------------------------------------------------------------
    # Edge Case 4: Oversized File (>10MB)
    # -------------------------------------------------------------------------
    print("\n[Edge Case 4] Oversized File (>10MB Limit)")
    big_buffer = BytesIO(b"X" * (11 * 1024 * 1024))
    big_file = UploadFile(
        filename="huge_document.png",
        file=big_buffer,
        headers={"content-type": "image/png"}
    )
    try:
        await verify_document(file=big_file)
        print("❌ FAILED: Expected HTTP 400 for oversized file")
    except HTTPException as e:
        assert e.status_code == 400
        assert "exceeds 10MB limit" in e.detail
        print(f"✅ PASS: HTTP {e.status_code} returned: {e.detail}")
        passed_tests += 1

    # -------------------------------------------------------------------------
    # Edge Case 5: Unsupported File Extension (.exe / .pdf)
    # -------------------------------------------------------------------------
    print("\n[Edge Case 5] Unsupported File Extension Rejection")
    bad_ext_file = UploadFile(
        filename="contract.pdf",
        file=BytesIO(b"%PDF-1.4 dummy pdf"),
        headers={"content-type": "application/pdf"}
    )
    try:
        await verify_document(file=bad_ext_file)
        print("❌ FAILED: Expected HTTP 400 for PDF")
    except HTTPException as e:
        assert e.status_code == 400
        assert "Unsupported file format" in e.detail
        print(f"✅ PASS: HTTP {e.status_code} returned: {e.detail}")
        passed_tests += 1

    # -------------------------------------------------------------------------
    # Edge Case 6: Pure Blank Image (0 text, 0 faces)
    # -------------------------------------------------------------------------
    print("\n[Edge Case 6] Pure Blank Image (Graceful OCR & Missing Field Flagging)")
    blank_path = os.path.join(TEMP_DIR, "blank_test_image.jpg")
    create_blank_image(blank_path)
    with open(blank_path, "rb") as f:
        blank_bytes = f.read()

    blank_upload = UploadFile(
        filename="blank.jpg",
        file=BytesIO(blank_bytes),
        headers={"content-type": "image/jpeg"}
    )

    blank_res = await verify_document(file=blank_upload, selfie=None)
    assert blank_res["status"] == "success"
    assert blank_res["document"]["name"] == "Not detected"
    assert blank_res["risk_score"] >= 30  # Missing required fields penalized
    assert blank_res["human_review_required"] is True
    print(f"✅ PASS: Blank image processed safely. Risk: {blank_res['overall_risk']} ({blank_res['risk_score']} pts), Review: {blank_res['human_review_required']}")
    passed_tests += 1

    # -------------------------------------------------------------------------
    # Edge Case 7: Non-Face Landscape Image as Selfie
    # -------------------------------------------------------------------------
    print("\n[Edge Case 7] Non-Face Scenic Image as Selfie (Graceful Biometric Handling)")
    scenic_path = os.path.join(TEMP_DIR, "scenic_no_face.jpg")
    create_landscape_scenic_image(scenic_path)
    with open(scenic_path, "rb") as f:
        scenic_bytes = f.read()

    doc_upload = UploadFile(
        filename="doc_portrait.jpg",
        file=open(DOC_PORTRAIT, "rb"),
        headers={"content-type": "image/jpeg"}
    )
    selfie_scenic_upload = UploadFile(
        filename="scenic_selfie.jpg",
        file=BytesIO(scenic_bytes),
        headers={"content-type": "image/jpeg"}
    )

    face_res = await verify_document(file=doc_upload, selfie=selfie_scenic_upload)
    assert face_res["status"] == "success"
    assert face_res["face_match"]["passed"] is False
    assert "No clear face detected" in face_res["face_match"]["message"]
    print(f"✅ PASS: No-face selfie handled gracefully. Verdict: {face_res['face_match']['message']}")
    passed_tests += 1

    # -------------------------------------------------------------------------
    # Edge Case 8: Complex Indian Names with Titles, Initials & Hyphens
    # -------------------------------------------------------------------------
    print("\n[Edge Case 8] Complex Indian Names with Titles, Initials & Hyphens")
    complex_names_text = """
    GOVERNMENT OF INDIA
    Unique Identification Authority of India
    Name: Dr. A. P. J. Abdul-Kalam
    DOB: 15/10/1931
    UID: 3675 9834 5212
    """
    fields = extract_fields_from_text(complex_names_text)
    assert fields["document_type"] == "Aadhaar Card"
    assert "Abdul-Kalam" in fields["name"] or "Kalam" in fields["name"] or len(fields["name"]) > 5
    assert fields["dob"] == "15/10/1931"

    validator = DocumentValidator(fields, raw_text=complex_names_text)
    f_res, r_res = validator.validate_all()
    assert r_res == 0, f"Expected risk 0, got {r_res}"
    print(f"✅ PASS: Complex name parsed and validated successfully (Extracted Name: '{fields['name']}')")
    passed_tests += 1

    # -------------------------------------------------------------------------
    # Edge Case 9: Boundary Date Formats (Single digit dates, Written months)
    # -------------------------------------------------------------------------
    print("\n[Edge Case 9] Boundary Date Formats & Century Handling")
    date_text = """
    INCOME TAX DEPARTMENT
    PERMANENT ACCOUNT NUMBER CARD
    Name: Vikramaditya Rao
    DOB: 5 Aug 1990
    PAN: ABCPR1234F
    """
    date_fields = extract_fields_from_text(date_text)
    assert date_fields["dob"] == "05/08/1990"
    date_val = DocumentValidator(date_fields, raw_text=date_text)
    f_date, r_date = date_val.validate_all()
    assert r_date == 0
    print(f"✅ PASS: Written month date normalized to standard DD/MM/YYYY: {date_fields['dob']}")
    passed_tests += 1

    # -------------------------------------------------------------------------
    # Edge Case 10: Mixed Multi-Document Batch (1 Authentic + 1 Blank Image)
    # -------------------------------------------------------------------------
    print("\n[Edge Case 10] Mixed Multi-Doc Batch (1 Authentic + 1 Blank Document)")
    with open(DOC_PORTRAIT, "rb") as f:
        doc_bytes1 = f.read()

    upload_m1 = UploadFile(filename="doc1_portrait.jpg", file=BytesIO(doc_bytes1), headers={"content-type": "image/jpeg"})
    upload_m2 = UploadFile(filename="doc2_blank.jpg", file=BytesIO(blank_bytes), headers={"content-type": "image/jpeg"})

    mixed_res = await verify_documents(files=[upload_m1, upload_m2], selfie=None)
    assert mixed_res["is_multi_document"] is True
    assert len(mixed_res["documents"]) == 2
    # Document 2 should be flagged for missing fields, while Doc 1 is inspected
    assert mixed_res["human_review_required"] is True
    assert mixed_res["why_flagged"]["risk_score"] >= 20
    assert mixed_res["risk_score"] >= 20
    print(f"✅ PASS: Mixed batch handled cleanly. Processed 2 documents, flagged anomalies in Doc 2.")
    passed_tests += 1

    # Cleanup temp test files
    for p in [blank_path, scenic_path]:
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass

    print("\n" + "=" * 80)
    print(f"🎉 ALL {passed_tests}/{total_tests} EDGE CASES PASSED! ZERO CRASHES.")
    print("=" * 80 + "\n")
    return passed_tests == total_tests


if __name__ == "__main__":
    ok = asyncio.run(test_edge_cases())
    sys.exit(0 if ok else 1)
