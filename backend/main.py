# backend/main.py
"""
VeriGuard AI - Backend API
Integrates OCR Extraction, Document Validation, Tampering Analysis, and Face Verification.
"""

import os
import sys
import subprocess

# Ensure backend directory is in sys.path regardless of how main.py is invoked
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

# Auto-re-execute using the project virtualenv if running directly under global/system Python
if __name__ == "__main__":
    _venv_python = os.path.join(_backend_dir, "venv", "Scripts", "python.exe")
    if os.path.isfile(_venv_python) and os.path.normcase(sys.executable) != os.path.normcase(_venv_python):
        res = subprocess.run([_venv_python] + sys.argv, cwd=_backend_dir)
        sys.exit(res.returncode)

import shutil
import uuid
import hashlib
from typing import Optional, List
try:
    from PIL import Image
except ImportError:
    Image = None

# Ensure UTF-8 stdout encoding on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

try:
    from ocr_tesseract import extract_text_from_image, extract_fields_from_text
    from validators import DocumentValidator
    from forensics import TamperingDetector
    from face_verification import FaceVerifier
    from cross_document import CrossDocumentValidator
    from identity_story import generate_identity_story
    from why_flagged import decompose_risk
    from audit_trail import AuditTrailLogger
except ImportError:
    from backend.ocr_tesseract import extract_text_from_image, extract_fields_from_text
    from backend.validators import DocumentValidator
    from backend.forensics import TamperingDetector
    from backend.face_verification import FaceVerifier
    from backend.cross_document import CrossDocumentValidator
    from backend.identity_story import generate_identity_story
    from backend.why_flagged import decompose_risk
    from backend.audit_trail import AuditTrailLogger

# ==========================================
# CREATE FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="VeriGuard AI",
    description="AI-powered document verification & biometric authentication system",
    version="1.0.0"
)

# ==========================================
# CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# TEMPORARY UPLOAD FOLDER
# ==========================================

TEMP_FOLDER = "temp"
os.makedirs(TEMP_FOLDER, exist_ok=True)

# ==========================================
# STATUS ROUTES
_frontend_dist = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
)

@app.get("/")
async def root():
    index_file = os.path.join(_frontend_dist, "index.html") if os.path.isdir(_frontend_dist) else None
    if index_file and os.path.isfile(index_file):
        from fastapi.responses import FileResponse
        return FileResponse(index_file)
    return {
        "message": "VeriGuard AI Backend is running!",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "VeriGuard AI"
    }

# ==========================================
# DOCUMENT & FACE VERIFICATION
# ==========================================

# ==========================================
# DOCUMENT & FACE VERIFICATION (SINGLE & MULTI-DOC)
# ==========================================

@app.post("/verify")
@app.post("/verify-multiple")
async def verify_documents(
    files: List[UploadFile] = File(default=[]),
    file: Optional[UploadFile] = File(default=None),
    selfie: Optional[UploadFile] = File(default=None)
):
    print("\n" + "=" * 50)
    print("🚀 NEW VERIFICATION REQUEST")
    print("=" * 50)

    # 1. Collect all uploaded document files safely
    upload_files: List[UploadFile] = []

    if isinstance(files, list):
        for f in files:
            if hasattr(f, "filename") and f.filename and f not in upload_files:
                upload_files.append(f)
    elif hasattr(files, "filename") and files.filename and files not in upload_files:
        upload_files.append(files)

    if hasattr(file, "filename") and file.filename and file not in upload_files:
        upload_files.append(file)

    if not upload_files:
        raise HTTPException(status_code=400, detail="No document file uploaded")

    allowed_types = ["image/jpeg", "image/jpg", "image/png"]
    for uf in upload_files:
        ct = getattr(uf, "content_type", "") or ""
        ext = os.path.splitext(uf.filename)[1].lower()
        if ct not in allowed_types and ext not in [".jpg", ".jpeg", ".png"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format for {uf.filename}. Please upload JPG or PNG."
            )
        uf.file.seek(0, 2)
        sz = uf.file.tell()
        uf.file.seek(0)
        if sz == 0:
            raise HTTPException(
                status_code=400,
                detail=f"File {uf.filename} is empty (0 bytes). Please upload a valid image."
            )
        if sz > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File {uf.filename} exceeds 10MB limit"
            )
        if Image is not None:
            try:
                with Image.open(uf.file) as test_img:
                    test_img.verify()
                uf.file.seek(0)
            except Exception:
                uf.file.seek(0)
                raise HTTPException(
                    status_code=400,
                    detail=f"File {uf.filename} is corrupt or not a readable image file."
                )

    # 2. Validate Selfie File (if provided)
    has_selfie = hasattr(selfie, "filename") and bool(selfie.filename)
    if has_selfie:
        ct = getattr(selfie, "content_type", "") or ""
        ext = os.path.splitext(selfie.filename)[1].lower()
        if ct not in allowed_types and ext not in [".jpg", ".jpeg", ".png"]:
            raise HTTPException(
                status_code=400,
                detail="Unsupported selfie format. Please upload JPG or PNG."
            )
        selfie.file.seek(0, 2)
        selfie_size = selfie.file.tell()
        selfie.file.seek(0)
        if selfie_size == 0:
            raise HTTPException(status_code=400, detail="Selfie file is empty (0 bytes).")
        if selfie_size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Selfie file size exceeds 10MB limit")
        if Image is not None:
            try:
                with Image.open(selfie.file) as test_img:
                    test_img.verify()
                selfie.file.seek(0)
            except Exception:
                selfie.file.seek(0)
                raise HTTPException(
                    status_code=400,
                    detail=f"Selfie file {selfie.filename} is corrupt or not a readable image file."
                )

    temp_paths_to_clean: List[str] = []
    audit = AuditTrailLogger()
    audit.log_event(
        category="INGESTION",
        step="Verification Request Received",
        status="SUCCESS",
        details=f"Received {len(upload_files)} document(s) + {'Selfie' if has_selfie else 'No Selfie'}"
    )

    try:
        # Save selfie if provided
        selfie_temp_path = None
        if has_selfie:
            selfie.file.seek(0)
            selfie_bytes = selfie.file.read()
            selfie.file.seek(0)
            selfie_hash = hashlib.sha256(selfie_bytes).hexdigest().upper()

            selfie_ext = os.path.splitext(selfie.filename)[1] or ".jpg"
            selfie_temp_path = os.path.join(TEMP_FOLDER, f"selfie_{uuid.uuid4()}{selfie_ext}")
            with open(selfie_temp_path, "wb") as buf:
                shutil.copyfileobj(selfie.file, buf)
            temp_paths_to_clean.append(selfie_temp_path)
            print(f"📸 Selfie saved: {selfie_temp_path}")

            audit.log_event(
                category="INGESTION",
                step="Live Selfie Cryptographic Fingerprint",
                status="SUCCESS",
                details=f"File: {selfie.filename} (SHA-256: {selfie_hash[:16]}..., {len(selfie_bytes)/1024:.1f} KB)",
                metadata={"filename": selfie.filename, "sha256": selfie_hash}
            )

        # Process each document
        processed_docs = []
        doc_temp_paths = []

        for idx, doc_file in enumerate(upload_files):
            doc_file.file.seek(0)
            doc_bytes = doc_file.file.read()
            doc_file.file.seek(0)
            doc_hash = hashlib.sha256(doc_bytes).hexdigest().upper()

            doc_ext = os.path.splitext(doc_file.filename)[1] or ".jpg"
            doc_temp_path = os.path.join(TEMP_FOLDER, f"doc_{idx+1}_{uuid.uuid4()}{doc_ext}")
            with open(doc_temp_path, "wb") as buf:
                shutil.copyfileobj(doc_file.file, buf)
            temp_paths_to_clean.append(doc_temp_path)
            doc_temp_paths.append(doc_temp_path)
            print(f"\n📁 Document [{idx+1}/{len(upload_files)}] saved: {doc_temp_path} ({doc_file.filename})")

            audit.log_event(
                category="INGESTION",
                step=f"Doc {idx+1} Cryptographic Fingerprint",
                status="SUCCESS",
                details=f"File: {doc_file.filename} (SHA-256: {doc_hash[:16]}..., {len(doc_bytes)/1024:.1f} KB)",
                metadata={"filename": doc_file.filename, "sha256": doc_hash}
            )

            # Step 1: OCR
            ocr_text = extract_text_from_image(doc_temp_path)
            print(f"Doc {idx+1} OCR extracted {len(ocr_text)} characters")

            audit.log_event(
                category="OCR",
                step=f"Doc {idx+1} Tesseract OCR Extraction",
                status="SUCCESS" if ocr_text else "WARNING",
                details=f"Extracted {len(ocr_text)} characters using multi-pass PSM 3/6 engine",
                metadata={"doc_index": idx + 1, "char_count": len(ocr_text)}
            )

            # Step 2: Field Extraction
            extracted_fields = extract_fields_from_text(ocr_text) if ocr_text else {}
            audit.log_event(
                category="OCR",
                step=f"Doc {idx+1} Field Normalization",
                status="SUCCESS",
                details=f"Identified as {extracted_fields.get('document_type', 'Unknown')} for {extracted_fields.get('name', 'Unknown')}",
                metadata={"fields": extracted_fields}
            )

            # Step 3: Tampering Detection
            tampering_signals = []
            tampering_report = {"overall_suspicion": "LOW"}
            try:
                detector = TamperingDetector(doc_temp_path)
                tampering_signals = detector.analyze_all()
                tampering_report = detector.get_report()
            except Exception as error:
                print(f"⚠️ Doc {idx+1} tampering detection error: {error}")

            audit.log_event(
                category="FORENSICS",
                step=f"Doc {idx+1} Digital Tampering Analysis",
                status="WARNING" if tampering_signals else "SUCCESS",
                details=f"{len(tampering_signals)} tampering anomaly detected" if tampering_signals else "No pixel-level tampering or metadata anomaly detected",
                metadata={"signal_count": len(tampering_signals)}
            )

            # Step 4: Document Validation
            validator = DocumentValidator(extracted_fields, raw_text=ocr_text)
            doc_findings, doc_risk = validator.validate_all()

            # Add tampering signals to findings
            if tampering_signals:
                for signal in tampering_signals:
                    severity = signal.get("severity", "MEDIUM")
                    doc_findings.append({
                        "check": f"Tampering: {signal.get('type', 'Unknown')}",
                        "status": "FAIL" if severity in ["HIGH", "MEDIUM"] else "WARNING",
                        "reason": signal.get("details", "Potential tampering detected")
                    })
                    if severity == "HIGH":
                        doc_risk += 30
                    elif severity == "MEDIUM":
                        doc_risk += 15
                    else:
                        doc_risk += 5

            audit.log_event(
                category="VALIDATION",
                step=f"Doc {idx+1} Syntax & Expiry Validation",
                status="FAIL" if doc_risk >= 30 else ("WARNING" if doc_risk > 0 else "SUCCESS"),
                details=f"Type: {extracted_fields.get('document_type', 'Unknown')} | Number: {extracted_fields.get('document_number', 'Not detected')} | Risk: {doc_risk} pts",
                metadata={"findings_count": len(doc_findings), "doc_risk": doc_risk}
            )

            doc_info = {
                "index": idx + 1,
                "filename": doc_file.filename,
                "name": extracted_fields.get("name", "Not detected"),
                "type": extracted_fields.get("document_type", "Unknown"),
                "number": extracted_fields.get("document_number", "Not detected"),
                "dob": extracted_fields.get("dob", "Not detected"),
                "expiry": extracted_fields.get("expiry", "Not detected"),
                "extracted_fields": extracted_fields,
                "ocr_text": ocr_text or "(No readable text detected)",
                "tampering_signals": tampering_signals,
                "tampering_report": tampering_report,
                "findings": doc_findings,
                "risk_score": max(0, min(100, doc_risk)),
            }
            processed_docs.append(doc_info)

        # ==================================
        # SINGLE DOCUMENT FLOW
        # ==================================
        if len(processed_docs) == 1:
            doc = processed_docs[0]
            findings = list(doc["findings"])
            risk_score = doc["risk_score"]

            face_match = {
                "score": 0,
                "threshold": 60,
                "passed": False,
                "confidence": "NONE",
                "message": "ℹ️ Selfie not provided for face verification"
            }

            if selfie_temp_path:
                print("\n🔍 RUNNING SINGLE DOC FACE VERIFICATION")
                try:
                    face_verifier = FaceVerifier(threshold=0.60)
                    face_res = face_verifier.verify_face(doc_temp_paths[0], selfie_temp_path)
                    is_match = face_res.get("is_match", False)
                    match_score = face_res.get("match_score", 0)
                    face_match = {
                        "score": match_score,
                        "threshold": 60,
                        "passed": is_match,
                        "confidence": face_res.get("confidence", "LOW"),
                        "message": face_res.get("message", "Face verification completed"),
                        "distance": face_res.get("distance", None)
                    }
                    if is_match:
                        findings.append({
                            "check": "Face Verification",
                            "status": "PASS",
                            "reason": f"Biometric face match verified with {match_score}% similarity"
                        })
                    else:
                        findings.append({
                            "check": "Face Verification",
                            "status": "FAIL",
                            "reason": face_match["message"]
                        })
                        risk_score += 25

                    audit.log_event(
                        category="BIOMETRICS",
                        step="128D ResNet Biometric Verification",
                        status="SUCCESS" if is_match else "FAIL",
                        details=f"Facial similarity: {match_score}% (Threshold: 60%, Distance: {face_res.get('distance', 'N/A')})",
                        metadata={"score": match_score, "passed": is_match}
                    )
                except Exception as face_err:
                    print(f"⚠️ Face verification error: {face_err}")
                    face_match["message"] = f"Face verification could not be evaluated: {face_err}"
                    audit.log_event(
                        category="BIOMETRICS",
                        step="Face Verification Error",
                        status="FAIL",
                        details=str(face_err)
                    )
            else:
                audit.log_event(
                    category="BIOMETRICS",
                    step="Biometric Face Verification Skipped",
                    status="INFO",
                    details="No live selfie submitted during screening"
                )

            risk_score = max(0, min(100, risk_score))
            overall_risk = "LOW" if risk_score < 30 else ("MEDIUM" if risk_score < 60 else "HIGH")
            human_review_required = overall_risk != "LOW"

            audit.log_event(
                category="RISK_ENGINE",
                step="Multi-Factor Risk Assessment Decision",
                status="SUCCESS" if overall_risk == "LOW" else ("WARNING" if overall_risk == "MEDIUM" else "FAIL"),
                details=f"Assigned Risk: {overall_risk} (Score: {risk_score}/100) | Review Required: {human_review_required}",
                metadata={"risk_score": risk_score, "overall_risk": overall_risk}
            )

            # Generate Identity Story, Why-Flagged breakdown, and sealed Audit Trail
            identity_story = generate_identity_story(
                documents=processed_docs,
                cross_report=None,
                face_match=face_match,
                overall_risk=overall_risk,
                risk_score=risk_score
            )

            why_flagged = decompose_risk(
                documents=processed_docs,
                findings=findings,
                cross_report=None,
                face_match=face_match,
                risk_score=risk_score,
                overall_risk=overall_risk
            )

            audit_trail = audit.finalize()

            return {
                "status": "success",
                "filename": doc["filename"],
                "ocr_text": doc["ocr_text"],
                "overall_risk": overall_risk,
                "risk_score": risk_score,
                "human_review_required": human_review_required,
                "document": doc,
                "documents": [doc],
                "findings": findings,
                "tampering_signals": doc["tampering_signals"],
                "tampering_report": doc["tampering_report"],
                "face_match": face_match,
                "is_multi_document": False,
                "cross_document": None,
                "identity_story": identity_story,
                "why_flagged": why_flagged,
                "audit_trail": audit_trail,
            }

        # ==================================
        # MULTI-DOCUMENT CROSS-CONSISTENCY FLOW
        # ==================================
        print(f"\n🔍 RUNNING CROSS-DOCUMENT CONSISTENCY CHECK ({len(processed_docs)} documents)")
        cross_validator = CrossDocumentValidator()
        face_verifier = FaceVerifier(threshold=0.60)

        cross_report = cross_validator.evaluate_consistency(
            documents_data=processed_docs,
            doc_paths=doc_temp_paths,
            selfie_path=selfie_temp_path,
            face_verifier=face_verifier
        )

        audit.log_event(
            category="CROSS_DOC",
            step="Cross-Document Demographic Reconciliation",
            status="SUCCESS" if cross_report["is_consistent"] else "FAIL",
            details=f"Consistency Score: {cross_report['consistency_score']}% | Inconsistencies: {len(cross_report['inconsistencies'])}",
            metadata={"consistency_score": cross_report["consistency_score"], "flags": len(cross_report["inconsistencies"])}
        )

        # Aggregate findings
        all_findings = []
        for d in processed_docs:
            for f in d["findings"]:
                all_findings.append({
                    "check": f"[Doc {d['index']} {d['type']}] {f['check']}",
                    "status": f["status"],
                    "reason": f["reason"]
                })

        # Add cross-document findings
        for match in cross_report["matches"]:
            all_findings.append({
                "check": "Cross-Document Consistency",
                "status": "PASS",
                "reason": match
            })

        for inc in cross_report["inconsistencies"]:
            all_findings.append({
                "check": f"Cross-Doc Inconsistency: {inc['field']}",
                "status": "FAIL" if inc["severity"] == "HIGH" else "WARNING",
                "reason": f"{inc['docs']} — {inc['description']}"
            })

        # Calculate multi-document risk score
        base_risk = max(d["risk_score"] for d in processed_docs)
        total_risk = base_risk + cross_report["risk_penalty"]

        # Face match payload for multi-document
        face_bio = cross_report.get("face_biometrics", {})
        face_match = {
            "score": face_bio.get("cross_doc_score", 0),
            "threshold": 60,
            "passed": face_bio.get("overall_face_match", False),
            "confidence": "HIGH" if face_bio.get("overall_face_match", False) else "LOW",
            "message": face_bio.get("message", "Multi-document facial consistency evaluated"),
            "pairs": face_bio.get("pairs", [])
        }

        audit.log_event(
            category="BIOMETRICS",
            step="Cross-Document Portrait Biometric Matching",
            status="SUCCESS" if face_bio.get("overall_face_match") else "WARNING",
            details=f"Portrait similarity: {face_bio.get('cross_doc_score', 0)}% across documents",
            metadata={"cross_doc_face_score": face_bio.get("cross_doc_score", 0)}
        )

        total_risk = max(0, min(100, total_risk))
        if total_risk < 30 and cross_report["is_consistent"]:
            overall_risk = "LOW"
            human_review_required = False
        elif total_risk < 60:
            overall_risk = "MEDIUM"
            human_review_required = True
        else:
            overall_risk = "HIGH"
            human_review_required = True

        audit.log_event(
            category="RISK_ENGINE",
            step="Unified Multi-Document Risk Assessment",
            status="SUCCESS" if overall_risk == "LOW" else ("WARNING" if overall_risk == "MEDIUM" else "FAIL"),
            details=f"Unified Risk: {overall_risk} (Score: {total_risk}/100) | Review Required: {human_review_required}",
            metadata={"risk_score": total_risk, "overall_risk": overall_risk}
        )

        all_tampering_signals = []
        for d in processed_docs:
            all_tampering_signals.extend(d["tampering_signals"])

        primary_doc = processed_docs[0]

        # Generate Identity Story, Why-Flagged breakdown, and sealed Audit Trail
        identity_story = generate_identity_story(
            documents=processed_docs,
            cross_report=cross_report,
            face_match=face_match,
            overall_risk=overall_risk,
            risk_score=total_risk
        )

        why_flagged = decompose_risk(
            documents=processed_docs,
            findings=all_findings,
            cross_report=cross_report,
            face_match=face_match,
            risk_score=total_risk,
            overall_risk=overall_risk
        )

        audit_trail = audit.finalize()

        return {
            "status": "success",
            "filename": ", ".join(d["filename"] for d in processed_docs),
            "ocr_text": "\n\n--- NEXT DOCUMENT ---\n\n".join(
                f"[{d['filename']} - {d['type']}]\n{d['ocr_text']}" for d in processed_docs
            ),
            "overall_risk": overall_risk,
            "risk_score": total_risk,
            "human_review_required": human_review_required,
            "document": primary_doc,
            "documents": processed_docs,
            "findings": all_findings,
            "tampering_signals": all_tampering_signals,
            "tampering_report": {
                "overall_suspicion": "HIGH" if any(d["tampering_report"].get("overall_suspicion") == "HIGH" for d in processed_docs) else "LOW"
            },
            "face_match": face_match,
            "is_multi_document": True,
            "cross_document": cross_report,
            "identity_story": identity_story,
            "why_flagged": why_flagged,
            "audit_trail": audit_trail,
        }

    finally:
        # Safe cleanup of all temp files
        for p in temp_paths_to_clean:
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception as cleanup_err:
                    print(f"⚠️ Could not delete temp file {p}: {cleanup_err}")

# Backward-compatible function alias
verify_document = verify_documents

# ==========================================
# OPTIONAL FRONTEND SPA STATIC MOUNTING
# ==========================================

_frontend_dist = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
)

if os.path.isdir(_frontend_dist):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    _assets_dir = os.path.join(_frontend_dist, "assets")
    if os.path.isdir(_assets_dir):
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="spa-assets")

    _demo_assets_dir = os.path.join(_frontend_dist, "demo_assets")
    if os.path.isdir(_demo_assets_dir):
        app.mount("/demo_assets", StaticFiles(directory=_demo_assets_dir), name="spa-demo-assets")

    @app.get("/favicon.svg")
    async def get_favicon():
        fav = os.path.join(_frontend_dist, "favicon.svg")
        if os.path.isfile(fav):
            return FileResponse(fav)
        raise HTTPException(status_code=404)

    @app.get("/icons.svg")
    async def get_icons():
        ico = os.path.join(_frontend_dist, "icons.svg")
        if os.path.isfile(ico):
            return FileResponse(ico)
        raise HTTPException(status_code=404)

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path in ("verify", "verify-multiple", "health") or full_path.startswith("verify/"):
            raise HTTPException(status_code=404, detail="Endpoint not found")
        candidate = os.path.join(_frontend_dist, full_path)
        if full_path and os.path.isfile(candidate):
            return FileResponse(candidate)
        index_file = os.path.join(_frontend_dist, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Page not found")

# ==========================================
# SERVER ENTRYPOINT
# ==========================================

if __name__ == "__main__":
    import uvicorn
    import socket

    def is_port_in_use(port: int) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                return s.connect_ex(("127.0.0.1", port)) == 0
        except Exception:
            return False

    target_port = 8000
    if is_port_in_use(target_port):
        print(f"[*] Notice: Port {target_port} is already active.")
        if not is_port_in_use(8001):
            target_port = 8001
            print(f"[*] Binding to alternative port {target_port}.")

    os.chdir(_backend_dir)
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=target_port,
        app_dir=_backend_dir,
        reload=False
    )