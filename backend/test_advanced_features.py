# backend/test_advanced_features.py
"""
Unit and Integration tests for VeriGuard AI Advanced Intelligence Features:
- Identity Story Narrative Engine
- Enhanced Why-Flagged Risk Decomposer & Officer Priority Queue
- Cryptographic Audit Trail Logger
- FastAPI Integration verification
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
from identity_story import generate_identity_story
from why_flagged import decompose_risk
from audit_trail import AuditTrailLogger
from main import verify_documents

ASSETS_DIR = os.path.join(_here, "test_assets")
DOC_PORTRAIT = os.path.join(ASSETS_DIR, "doc_portrait.jpg")
SELFIE_MATCH = os.path.join(ASSETS_DIR, "selfie_match.jpg")


def create_upload_file(file_path: str) -> UploadFile:
    with open(file_path, "rb") as f:
        content = f.read()
    content_type = "image/png" if file_path.endswith(".png") else "image/jpeg"
    return UploadFile(
        filename=os.path.basename(file_path),
        file=BytesIO(content),
        headers={"content-type": content_type}
    )


def test_identity_story_narrative():
    print("\n--- Test 1: Identity Story Narrative Generation ---")

    # Consistent multi-document story
    docs = [
        {"name": "Anna Maria Eriksson", "dob": "12/08/1974", "type": "Passport", "number": "L898902C3"},
        {"name": "Anna Eriksson", "dob": "12/08/1974", "type": "National ID", "number": "ID-99482"}
    ]
    cross_report = {
        "is_multi_document": True,
        "is_consistent": True,
        "consistency_score": 96,
        "inconsistencies": [],
        "matches": ["Names match with middle name variation", "Dates of birth match exactly"],
        "face_biometrics": {
            "overall_face_match": True,
            "cross_doc_score": 80.4,
            "pairs": [{"type": "doc_to_doc", "source": "Doc 1", "target": "Doc 2", "is_match": True, "match_score": 80.4}]
        }
    }
    story = generate_identity_story(
        documents=docs,
        cross_report=cross_report,
        face_match={"score": 80.4, "passed": True},
        overall_risk="LOW",
        risk_score=0
    )

    assert "Anna" in story["headline"]
    assert len(story["paragraphs"]) >= 2
    assert any("Passport" in p for p in story["paragraphs"])
    assert story["status_tier"] == "CONFIRMED_CONSISTENT"
    assert len(story["key_facts"]) >= 4
    print(f"✓ Consistent Multi-Doc Story generated: \"{story['headline']}\"")

    # Conflict / Discrepancy story
    docs_conflict = [
        {"name": "Anna Eriksson", "dob": "12/08/1974", "type": "Passport", "number": "L898902C3"},
        {"name": "John Doe", "dob": "25/11/1990", "type": "Driver License", "number": "DL-1122"}
    ]
    cross_conflict = {
        "is_multi_document": True,
        "is_consistent": False,
        "consistency_score": 35,
        "inconsistencies": [
            {"field": "Name", "description": "Name discrepancy detected: 'Anna Eriksson' vs 'John Doe'"},
            {"field": "Date of Birth", "description": "DOB discrepancy detected: '1974-08-12' vs '1990-11-25'"}
        ],
        "face_biometrics": {"pairs": []}
    }
    conflict_story = generate_identity_story(
        documents=docs_conflict,
        cross_report=cross_conflict,
        overall_risk="HIGH",
        risk_score=75
    )
    assert "Conflict" in conflict_story["headline"] or "Inconsistencies" in conflict_story["headline"]
    assert conflict_story["status_tier"] == "FLAGGED_INCONSISTENCY"
    print(f"✓ Conflict Story generated: \"{conflict_story['headline']}\"")


def test_why_flagged_panel():
    print("\n--- Test 2: Why-Flagged Risk Decomposer & Priority Queue ---")

    docs = [{"filename": "doc.jpg", "tampering_signals": [{"type": "Edge Artifact", "severity": "HIGH", "details": "Suspicious edge splice"}]}]
    findings = [
        {"check": "Tampering: Edge Artifact", "status": "FAIL", "reason": "Suspicious edge splice"},
        {"check": "Expiry Date", "status": "FAIL", "reason": "Document expired on 01/01/2023"}
    ]
    cross_report = {
        "is_multi_document": True,
        "inconsistencies": [
            {"field": "Name", "severity": "HIGH", "description": "Name discrepancy", "docs": "Doc 1 vs Doc 2"}
        ],
        "matches": []
    }
    face_match = {"score": 25.0, "passed": False, "message": "Biometric match below threshold"}

    res = decompose_risk(
        documents=docs,
        findings=findings,
        cross_report=cross_report,
        face_match=face_match,
        risk_score=85,
        overall_risk="HIGH"
    )

    assert "priority_queue" in res
    assert len(res["priority_queue"]) >= 4
    # Highest severity items should come first
    first_item = res["priority_queue"][0]
    assert first_item["severity"] in ["CRITICAL", "HIGH"]
    assert res["officer_tier"] == "TIER_1_IMMEDIATE_ESCALATION"
    assert res["domain_points"]["AUTHENTICITY"] > 0
    assert res["domain_points"]["BIOMETRICS"] > 0
    assert res["domain_points"]["DATA_INTEGRITY"] > 0
    print(f"✓ Why-Flagged decomposition completed: {res['action_required_count']} action items sorted into {res['tier_label']}")


def test_audit_trail_logger():
    print("\n--- Test 3: Cryptographic Audit Trail Logger ---")
    logger = AuditTrailLogger(session_id="VR-AUDIT-TEST-001")

    logger.log_event("INGESTION", "File Received", "SUCCESS", "Uploaded document test.jpg")
    logger.log_event("OCR", "Text Extraction", "SUCCESS", "Extracted 250 chars")
    logger.log_event("BIOMETRICS", "Face Verified", "SUCCESS", "Similarity: 80.4%")

    trail = logger.finalize()

    assert trail["audit_id"] == "VR-AUDIT-TEST-001"
    assert trail["total_events"] == 4  # 3 events + 1 seal event
    assert len(trail["cryptographic_seal"]) == 64  # SHA-256 length
    assert trail["events"][0]["elapsed_formatted"].startswith("+")
    print(f"✓ Audit Trail sealed with SHA-256 digest: {trail['cryptographic_seal'][:16]}... ({trail['total_events']} events)")


async def test_api_advanced_features_integration():
    print("\n--- Test 4: API Advanced Features Integration ---")

    f1 = create_upload_file(DOC_PORTRAIT)
    f2 = create_upload_file(SELFIE_MATCH)

    data = await verify_documents(files=[f1, f2])

    assert data["status"] == "success"
    assert "identity_story" in data
    assert "headline" in data["identity_story"]
    assert len(data["identity_story"]["paragraphs"]) > 0

    assert "why_flagged" in data
    assert "priority_queue" in data["why_flagged"]
    assert "domain_points" in data["why_flagged"]

    assert "audit_trail" in data
    assert "cryptographic_seal" in data["audit_trail"]
    assert len(data["audit_trail"]["events"]) >= 5
    print("✓ Full API response returned identity_story, why_flagged, and audit_trail")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 RUNNING ADVANCED FEATURES TEST SUITE")
    print("=" * 60)
    test_identity_story_narrative()
    test_why_flagged_panel()
    test_audit_trail_logger()
    asyncio.run(test_api_advanced_features_integration())
    print("\n" + "=" * 60)
    print("🎉 ALL ADVANCED FEATURES TESTS PASSED!")
    print("=" * 60)
