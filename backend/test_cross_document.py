# backend/test_cross_document.py
"""
Unit and Integration tests for VeriGuard AI Cross-Document Intelligence:
- CrossDocumentValidator algorithms (Name, DOB, Doc Number, Biometrics)
- Multi-document upload via FastAPI async verify_documents handler
"""

import os
import sys
import subprocess
import asyncio
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
from cross_document import CrossDocumentValidator
from face_verification import FaceVerifier
from main import verify_documents

ASSETS_DIR = os.path.join(_here, "test_assets")
DOC_PORTRAIT = os.path.join(ASSETS_DIR, "doc_portrait.jpg")
SELFIE_MATCH = os.path.join(ASSETS_DIR, "selfie_match.jpg")
SELFIE_MISMATCH = os.path.join(ASSETS_DIR, "selfie_mismatch.jpg")


def create_upload_file(file_path: str) -> UploadFile:
    with open(file_path, "rb") as f:
        content = f.read()
    content_type = "image/png" if file_path.endswith(".png") else "image/jpeg"
    return UploadFile(
        filename=os.path.basename(file_path),
        file=BytesIO(content),
        headers={"content-type": content_type}
    )


def test_name_comparison():
    print("\n--- Test 1: Cross-Document Name Matching ---")
    validator = CrossDocumentValidator()

    # Exact match
    res1 = validator.compare_names("ANNA MARIA ERIKSSON", "ANNA MARIA ERIKSSON")
    assert res1["status"] == "EXACT", f"Expected EXACT, got {res1['status']}"
    assert res1["is_consistent"] is True
    print("✓ Exact Name Match passed")

    # Middle name omission / token subset
    res2 = validator.compare_names("ANNA MARIA ERIKSSON", "ANNA ERIKSSON")
    assert res2["status"] == "HIGH_SIMILARITY", f"Expected HIGH_SIMILARITY, got {res2['status']}"
    assert res2["is_consistent"] is True
    print("✓ Middle Name Omission / Token Subset passed")

    # Name reordering (Last First vs First Last)
    res3 = validator.compare_names("ERIKSSON ANNA", "ANNA ERIKSSON")
    assert res3["status"] == "EXACT_REORDERED", f"Expected EXACT_REORDERED, got {res3['status']}"
    assert res3["is_consistent"] is True
    print("✓ Reordered Name Tokens passed")

    # Name with title prefix
    res4 = validator.compare_names("DR. ANNA ERIKSSON", "ANNA ERIKSSON")
    assert res4["status"] == "EXACT", f"Expected EXACT, got {res4['status']}"
    print("✓ Title Normalization passed")

    # Blatant mismatch
    res5 = validator.compare_names("ANNA ERIKSSON", "JOHNATHAN DOE")
    assert res5["status"] == "MISMATCH", f"Expected MISMATCH, got {res5['status']}"
    assert res5["is_consistent"] is False
    assert res5["severity"] == "HIGH"
    print("✓ Name Mismatch Detection passed")


def test_dob_comparison():
    print("\n--- Test 2: Cross-Document DOB Matching ---")
    validator = CrossDocumentValidator()

    # Same date, different formatting
    res1 = validator.compare_dobs("12/08/1974", "1974-08-12")
    assert res1["status"] == "EXACT", f"Expected EXACT, got {res1['status']}"
    assert res1["is_consistent"] is True
    print("✓ Cross-format Exact Date Match passed (12/08/1974 vs 1974-08-12)")

    # Written month vs numeric month
    res2 = validator.compare_dobs("12 Aug 1974", "12/08/1974")
    assert res2["status"] == "EXACT", f"Expected EXACT, got {res2['status']}"
    print("✓ Written Month Normalization passed (12 Aug 1974)")

    # Same year, different day/month
    res3 = validator.compare_dobs("12/08/1974", "15/03/1974")
    assert res3["status"] == "YEAR_MATCH_ONLY", f"Expected YEAR_MATCH_ONLY, got {res3['status']}"
    assert res3["is_consistent"] is False
    print("✓ Year Match Only flagged correctly")

    # Complete mismatch
    res4 = validator.compare_dobs("12/08/1974", "25/11/1992")
    assert res4["status"] == "MISMATCH", f"Expected MISMATCH, got {res4['status']}"
    assert res4["is_consistent"] is False
    assert res4["severity"] == "HIGH"
    print("✓ DOB Mismatch Detection passed (1974 vs 1992)")


def test_document_number_comparison():
    print("\n--- Test 3: Document Number Validation ---")
    validator = CrossDocumentValidator()

    # Same document type with matching numbers
    res1 = validator.compare_document_numbers("Passport", "Z1234567", "Passport", "Z1234567")
    assert res1["status"] == "EXACT"
    assert res1["is_consistent"] is True
    print("✓ Matching Duplicate Doc Numbers passed")

    # Same document type with conflicting numbers
    res2 = validator.compare_document_numbers("Passport", "Z1234567", "Passport", "Z9876543")
    assert res2["status"] == "CONFLICT"
    assert res2["is_consistent"] is False
    assert res2["severity"] == "HIGH"
    print("✓ Conflicting Duplicate Doc Numbers flagged")

    # Different document types with valid distinct numbers
    res3 = validator.compare_document_numbers("Passport", "Z1234567", "Aadhaar", "123456789012")
    assert res3["status"] == "DISTINCT_VALID"
    assert res3["is_consistent"] is True
    print("✓ Distinct Document Types with valid separate IDs passed")

    # Suspicious duplicate across different types
    res4 = validator.compare_document_numbers("Passport", "ABC12345", "PAN", "ABC12345")
    assert res4["status"] == "SUSPICIOUS_DUPLICATE"
    assert res4["is_consistent"] is False
    print("✓ Suspicious Shared Number across document types flagged")


def test_cross_document_biometrics():
    print("\n--- Test 4: Cross-Document Biometric Face Matching ---")
    validator = CrossDocumentValidator()
    verifier = FaceVerifier(threshold=0.60)

    # 2 documents of the same person
    res_match = validator.compare_document_faces(
        face_verifier=verifier,
        doc_paths=[DOC_PORTRAIT, SELFIE_MATCH],
        doc_names=["Doc 1 (Passport)", "Doc 2 (Aadhaar)"],
        selfie_path=None
    )
    assert res_match["evaluated"] is True
    assert res_match["overall_face_match"] is True
    assert res_match["cross_doc_score"] >= 70
    print(f"✓ Cross-Document Biometric Match passed ({res_match['cross_doc_score']}% similarity)")

    # 2 documents of different persons
    res_mismatch = validator.compare_document_faces(
        face_verifier=verifier,
        doc_paths=[DOC_PORTRAIT, SELFIE_MISMATCH],
        doc_names=["Doc 1 (Passport)", "Doc 2 (ID)"],
        selfie_path=None
    )
    assert res_mismatch["overall_face_match"] is False
    print("✓ Cross-Document Face Mismatch correctly detected between conflicting documents")


async def test_fastapi_multi_document_upload():
    print("\n--- Test 5: FastAPI Multi-Document Upload Integration ---")

    # Upload 2 documents simultaneously
    f1 = create_upload_file(DOC_PORTRAIT)
    f2 = create_upload_file(SELFIE_MATCH)
    data = await verify_documents(files=[f1, f2])

    assert data["status"] == "success"
    assert data["is_multi_document"] is True
    assert len(data["documents"]) == 2
    assert "cross_document" in data
    assert data["cross_document"]["document_count"] == 2
    assert "comparisons" in data["cross_document"]
    print(f"✓ Multi-document upload returned success (Consistency: {data['cross_document']['consistency_score']}%)")

    # Test single-document backwards compatibility
    single_f = create_upload_file(DOC_PORTRAIT)
    single_data = await verify_documents(file=single_f)
    assert single_data["status"] == "success"
    assert single_data["is_multi_document"] is False
    assert single_data["document"]["filename"] == "doc_portrait.jpg"
    print("✓ Single-document backwards compatibility verified")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 RUNNING CROSS-DOCUMENT INTELLIGENCE TEST SUITE")
    print("=" * 60)
    test_name_comparison()
    test_dob_comparison()
    test_document_number_comparison()
    test_cross_document_biometrics()
    asyncio.run(test_fastapi_multi_document_upload())
    print("\n" + "=" * 60)
    print("🎉 ALL CROSS-DOCUMENT TESTS PASSED!")
    print("=" * 60)
