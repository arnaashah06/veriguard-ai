# backend/test_indian_documents.py
"""
VeriGuard AI - Indian Government Document Authentication & Cross-Verification Test Suite
Tests:
1. Aadhaar Card Verhoeff Checksum & UIDAI Security Design Verification
2. Counterfeit Aadhaar Detection (Corrupted Check Digit & Forbidden Leading Digits)
3. PAN Card 10-Character Structure, 4th Char Entity, and 5th Char Surname Initial Match
4. Counterfeit / Mismatched PAN Card Detection
5. Voter ID (EPIC) & Indian Driving Licence Validation
6. Aadhaar + PAN Cross-Document Statutory Linkage
7. FastAPI /verify-multiple Endpoint Integration
"""

import os
import sys
import subprocess
from io import BytesIO

# Auto-re-execute using the project virtualenv if running under global/system Python
_here = os.path.dirname(os.path.abspath(__file__))
_venv_python = os.path.join(_here, "venv", "Scripts", "python.exe")
if os.path.isfile(_venv_python) and os.path.normcase(sys.executable) != os.path.normcase(_venv_python):
    res = subprocess.run([_venv_python] + sys.argv)
    sys.exit(res.returncode)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from fastapi import UploadFile
from validators import (
    DocumentValidator,
    validate_verhoeff,
    generate_verhoeff_check_digit
)
from cross_document import CrossDocumentValidator
from main import verify_documents


def test_aadhaar_verification():
    print("\n--- Test 1: Authentic Aadhaar Card (Verhoeff Checksum) ---")
    prefix = "36759834521"
    check_digit = generate_verhoeff_check_digit(prefix)
    valid_uid = f"{prefix[:4]} {prefix[4:8]} {prefix[8:]}{check_digit}"

    validator = DocumentValidator({
        "document_type": "Aadhaar Card",
        "name": "Priya Ramesh Patel",
        "dob": "24/11/1992",
        "document_number": valid_uid
    }, raw_text="Government of India Unique Identification Authority of India UIDAI")

    findings, risk = validator.validate_all()
    assert risk == 0, f"Expected risk 0 for authentic Aadhaar, got {risk}"
    assert any("Verhoeff" in f["check"] and f["status"] == "PASS" for f in findings)
    assert any("lifetime" in f["reason"].lower() for f in findings)
    print(f"✓ Valid Aadhaar UID {valid_uid} verified with Verhoeff Checksum (Risk: {risk})")


def test_fake_aadhaar_rejection():
    print("\n--- Test 2: Counterfeit Aadhaar Detection ---")
    prefix = "36759834521"
    true_digit = generate_verhoeff_check_digit(prefix)
    corrupted_digit = (true_digit + 3) % 10
    fake_uid = f"{prefix[:4]} {prefix[4:8]} {prefix[8:]}{corrupted_digit}"

    validator = DocumentValidator({
        "document_type": "Aadhaar Card",
        "name": "Priya Patel",
        "dob": "24/11/1992",
        "document_number": fake_uid
    })

    findings, risk = validator.validate_all()
    assert risk >= 35, f"Expected risk >= 35 for corrupted Aadhaar, got {risk}"
    assert any("Verhoeff" in f["check"] and f["status"] == "FAIL" for f in findings)
    print(f"✓ Fake Aadhaar UID {fake_uid} successfully rejected (Risk: {risk})")

    # Leading zero test
    invalid_leading_uid = "0675 9834 5212"
    val_lead = DocumentValidator({
        "document_type": "Aadhaar Card",
        "name": "Priya Patel",
        "dob": "24/11/1992",
        "document_number": invalid_leading_uid
    })
    f_lead, r_lead = val_lead.validate_all()
    assert any("Number Range" in f["check"] and f["status"] == "FAIL" for f in f_lead)
    print(f"✓ Aadhaar starting with 0 successfully rejected (Risk: {r_lead})")


def test_pan_card_verification():
    print("\n--- Test 3: Authentic PAN Card & Surname Match ---")
    # Surname Patel -> 5th char P, 4th char P for Individual
    pan_num = "ABCPP1234F"

    validator = DocumentValidator({
        "document_type": "PAN Card",
        "name": "Priya Ramesh Patel",
        "dob": "24/11/1992",
        "document_number": pan_num
    }, raw_text="Income Tax Department Govt. of India Permanent Account Number Card")

    findings, risk = validator.validate_all()
    assert risk == 0, f"Expected risk 0 for authentic PAN, got {risk}"
    assert any("Taxpayer Entity" in f["check"] and f["status"] == "PASS" for f in findings)
    assert any("Surname Initial" in f["check"] and f["status"] == "PASS" for f in findings)
    print(f"✓ Authentic PAN {pan_num} verified with Surname Initial 'P' (Risk: {risk})")


def test_pan_card_surname_mismatch():
    print("\n--- Test 4: PAN Card Surname Initial Mismatch ---")
    # Cardholder name is Arjun Singh, but PAN has 'P' as 5th char (Mismatch)
    pan_mismatch = "ABCPP1234F"

    validator = DocumentValidator({
        "document_type": "PAN Card",
        "name": "Arjun Singh",
        "dob": "24/11/1992",
        "document_number": pan_mismatch
    })

    findings, risk = validator.validate_all()
    assert risk >= 15, f"Expected penalty for surname mismatch, got {risk}"
    assert any("Surname Initial" in f["check"] and f["status"] == "WARNING" for f in findings)
    print(f"✓ PAN Surname Mismatch successfully flagged (Risk: {risk})")


def test_voter_and_driving_licence():
    print("\n--- Test 5: Voter ID & Indian Driving Licence Validation ---")
    voter_val = DocumentValidator({
        "document_type": "Voter ID",
        "name": "Amit Sharma",
        "dob": "10/05/1988",
        "document_number": "ABC1234567"
    }, raw_text="Election Commission of India भारत निर्वाचन आयोग")
    f_voter, r_voter = voter_val.validate_all()
    assert any("EPIC" in f["check"] and f["status"] == "PASS" for f in f_voter)
    print("✓ Election Commission of India (EPIC) Voter ID validated")

    dl_val = DocumentValidator({
        "document_type": "Driving License",
        "name": "Amit Sharma",
        "dob": "10/05/1988",
        "document_number": "MH12 20180012345",
        "expiry": "15/08/2038"
    })
    f_dl, r_dl = dl_val.validate_all()
    assert any("State Jurisdiction" in f["check"] and "Maharashtra" in f["reason"] for f in f_dl)
    print("✓ Indian Driving Licence Maharashtra (MH12) validated")


def test_aadhaar_pan_cross_linkage():
    print("\n--- Test 6: Cross-Document Statutory Aadhaar-PAN Linkage ---")
    cdv = CrossDocumentValidator()

    docs = [
        {"type": "Aadhaar Card", "name": "Priya Ramesh Patel", "dob": "24/11/1992", "number": "3675 9834 5212"},
        {"type": "PAN Card", "name": "Priya Ramesh Patel", "dob": "24/11/1992", "number": "ABCPP1234F"}
    ]

    res = cdv.evaluate_consistency(docs, ["doc1.jpg", "doc2.jpg"])
    assert res["is_consistent"] is True
    assert res["aadhaar_pan_linkage"] is not None
    assert res["aadhaar_pan_linkage"]["is_linked"] is True
    print("✓ Statutory Aadhaar-PAN linkage verified across documents")


def test_verify_multiple_endpoint():
    print("\n--- Test 7: FastAPI /verify-multiple Endpoint Integration ---")
    assets_dir = os.path.join(_here, "test_assets")
    doc_path = os.path.join(assets_dir, "doc_portrait.jpg")

    with open(doc_path, "rb") as f:
        content1 = f.read()
    with open(doc_path, "rb") as f:
        content2 = f.read()

    file1 = UploadFile(filename="aadhaar_test.jpg", file=BytesIO(content1), headers={"content-type": "image/jpeg"})
    file2 = UploadFile(filename="pan_test.jpg", file=BytesIO(content2), headers={"content-type": "image/jpeg"})

    response = asyncio.run(verify_documents(files=[file1, file2]))
    assert response["is_multi_document"] is True
    assert "cross_document" in response
    assert "identity_story" in response
    assert "why_flagged" in response
    assert "audit_trail" in response
    print("✓ /verify-multiple endpoint returned complete multi-document intelligence package")


if __name__ == "__main__":
    import asyncio
    print("=" * 60)
    print("🇮🇳 RUNNING INDIAN DOCUMENT AUTHENTICATION TEST SUITE")
    print("=" * 60)

    test_aadhaar_verification()
    test_fake_aadhaar_rejection()
    test_pan_card_verification()
    test_pan_card_surname_mismatch()
    test_voter_and_driving_licence()
    test_aadhaar_pan_cross_linkage()
    test_verify_multiple_endpoint()

    print("=" * 60)
    print("🎉 ALL INDIAN DOCUMENT VERIFICATION TESTS PASSED!")
    print("=" * 60)
