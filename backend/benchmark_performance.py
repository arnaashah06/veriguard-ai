# backend/benchmark_performance.py
"""
VeriGuard AI - Empirical Latency & Performance Benchmarking Suite
Runs rigorous multi-iteration trials measuring P50, P90, P99 latency percentiles,
peak RAM allocation, and stage-by-stage execution breakdowns.
Resolves prototype limitation #5 by replacing assumptions with verified empirical data.
"""

import os
import sys
import time
import json
import statistics
import tracemalloc

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
TEST_ASSETS_DIR = os.path.join(BACKEND_DIR, "test_assets")
sys.path.insert(0, BACKEND_DIR)

# Import internal modules
from validators import validate_verhoeff, DocumentValidator
from cross_document import CrossDocumentValidator
from ocr_tesseract import extract_text_from_image, extract_fields_from_text
from face_verification import verify_face
from audit_trail import AuditTrailLogger
from why_flagged import decompose_risk
from identity_story import generate_identity_story

def calculate_percentiles(data):
    if not data:
        return {"p50": 0, "p90": 0, "p95": 0, "p99": 0, "min": 0, "max": 0, "mean": 0}
    sorted_data = sorted(data)
    n = len(sorted_data)
    return {
        "min": round(sorted_data[0] * 1000, 2),
        "mean": round(statistics.mean(sorted_data) * 1000, 2),
        "p50": round(statistics.median(sorted_data) * 1000, 2),
        "p90": round(sorted_data[min(int(n * 0.90), n - 1)] * 1000, 2),
        "p95": round(sorted_data[min(int(n * 0.95), n - 1)] * 1000, 2),
        "p99": round(sorted_data[min(int(n * 0.99), n - 1)] * 1000, 2),
        "max": round(sorted_data[-1] * 1000, 2)
    }

def run_benchmarks(iterations=30):
    print("=" * 80)
    print("      VERIGUARD AI - EMPIRICAL PERFORMANCE & LATENCY PROFILER")
    print(f"      Running {iterations} iterations across each architectural pipeline stage")
    print("=" * 80)

    tracemalloc.start()
    results = {}

    # 1. Statutory Mathematical Validation (Verhoeff, PAN, MRZ)
    print("\n[BENCHMARK 1/5] Measuring Statutory & Mathematical Checksums...")
    times_statutory = []
    for _ in range(iterations * 10):
        t0 = time.perf_counter()
        validate_verhoeff("367598345212")
        pan_validator = DocumentValidator({"document_type": "PAN Card", "document_number": "ABCPP1234F", "name": "Priya Patel"})
        pan_validator.validate_all()
        mrz_validator = DocumentValidator({
            "document_type": "Passport",
            "mrz_line1": "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<",
            "mrz_line2": "L898902C36UTO7408122F2804154<<<<<<<<<<<<<<06"
        })
        mrz_validator.validate_mrz_security()
        times_statutory.append(time.perf_counter() - t0)
    results["statutory_rules"] = calculate_percentiles(times_statutory)
    print(f"  -> Mean: {results['statutory_rules']['mean']:.3f} ms | P95: {results['statutory_rules']['p95']:.3f} ms | P99: {results['statutory_rules']['p99']:.3f} ms")

    # 2. Cross-Document Reconciliation & Fuzzy Demographics
    print("\n[BENCHMARK 2/5] Measuring Multi-Doc Cross-Reconciliation...")
    times_reconciliation = []
    doc_a = {"document_type": "Aadhaar Card", "name": "Rahul Kumar Sharma", "dob": "15/08/1990", "document_number": "3675 9834 5212"}
    doc_b = {"document_type": "PAN Card", "name": "Rahul K. Sharma", "dob": "15/08/1990", "document_number": "ABCPS1234F"}
    cross_val = CrossDocumentValidator()
    for _ in range(iterations * 5):
        t0 = time.perf_counter()
        cross_res = cross_val.evaluate_consistency([doc_a, doc_b], doc_paths=["doc1.png", "doc2.png"])
        generate_identity_story([doc_a, doc_b], cross_report=cross_res, overall_risk="LOW", risk_score=0)
        decompose_risk([doc_a, doc_b], findings=[], cross_report=cross_res, risk_score=0, overall_risk="LOW")
        times_reconciliation.append(time.perf_counter() - t0)
    results["cross_document_reconciliation"] = calculate_percentiles(times_reconciliation)
    print(f"  -> Mean: {results['cross_document_reconciliation']['mean']:.3f} ms | P95: {results['cross_document_reconciliation']['p95']:.3f} ms | P99: {results['cross_document_reconciliation']['p99']:.3f} ms")

    # 3. Biometric ResNet-128D Face Verification
    doc_portrait = os.path.join(TEST_ASSETS_DIR, "doc_portrait.jpg")
    selfie_match = os.path.join(TEST_ASSETS_DIR, "selfie_match.jpg")
    if os.path.exists(doc_portrait) and os.path.exists(selfie_match):
        print("\n[BENCHMARK 3/5] Measuring 128D ResNet Biometric Face Verification...")
        times_face = []
        for _ in range(max(10, iterations // 2)):
            t0 = time.perf_counter()
            verify_face(doc_portrait, selfie_match)
            times_face.append(time.perf_counter() - t0)
        results["biometric_face_verification"] = calculate_percentiles(times_face)
        print(f"  -> Mean: {results['biometric_face_verification']['mean']:.2f} ms | P95: {results['biometric_face_verification']['p95']:.2f} ms | P99: {results['biometric_face_verification']['p99']:.2f} ms")
    else:
        print("\n[BENCHMARK 3/5] Face test assets not found, skipping face verification benchmark.")
        results["biometric_face_verification"] = {"mean": 0, "p50": 0, "p90": 0, "p95": 0, "p99": 0}

    # 4. Tesseract Dual-Pass OCR Extraction
    test_doc = os.path.join(ROOT_DIR, "temp", "doc_1_76d86076-34c5-486d-b1f3-e02ce795c7b2.jpg")
    if not os.path.exists(test_doc):
        # Fallback to any image in test_assets
        for f in os.listdir(TEST_ASSETS_DIR):
            if f.endswith((".png", ".jpg", ".jpeg")):
                test_doc = os.path.join(TEST_ASSETS_DIR, f)
                break
                
    if os.path.exists(test_doc):
        print(f"\n[BENCHMARK 4/5] Measuring Tesseract OCR Extraction on sample document...")
        times_ocr = []
        for _ in range(max(5, iterations // 3)):
            t0 = time.perf_counter()
            text = extract_text_from_image(test_doc)
            extract_fields_from_text(text)
            times_ocr.append(time.perf_counter() - t0)
        results["tesseract_ocr"] = calculate_percentiles(times_ocr)
        print(f"  -> Mean: {results['tesseract_ocr']['mean']:.2f} ms | P95: {results['tesseract_ocr']['p95']:.2f} ms | P99: {results['tesseract_ocr']['p99']:.2f} ms")
    else:
        print("\n[BENCHMARK 4/5] Sample OCR document not found, skipping OCR benchmark.")
        results["tesseract_ocr"] = {"mean": 0, "p50": 0, "p90": 0, "p95": 0, "p99": 0}

    # 5. Cryptographic SHA-256 Chained Audit Trail
    print("\n[BENCHMARK 5/5] Measuring Cryptographic Audit Trail Sealing...")
    times_audit = []
    logger = AuditTrailLogger(session_id="BENCHMARK-SESSION-001")
    for i in range(iterations * 10):
        t0 = time.perf_counter()
        logger.log_event(
            category="COMPLIANCE",
            step=f"TRIAL_{i}",
            status="SUCCESS",
            details="Cryptographic hash sealing test"
        )
        times_audit.append(time.perf_counter() - t0)
    logger.finalize()
    results["audit_trail_sealing"] = calculate_percentiles(times_audit)
    print(f"  -> Mean: {results['audit_trail_sealing']['mean']:.3f} ms | P95: {results['audit_trail_sealing']['p95']:.3f} ms | P99: {results['audit_trail_sealing']['p99']:.3f} ms")

    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_mb = peak_mem / (1024 * 1024)
    results["peak_ram_allocated_mb"] = round(peak_mb, 2)

    # Combined Full-Pipeline Estimated Latency
    pipeline_mean = (
        results.get("tesseract_ocr", {}).get("mean", 0) +
        results.get("statutory_rules", {}).get("mean", 0) +
        results.get("biometric_face_verification", {}).get("mean", 0) +
        results.get("cross_document_reconciliation", {}).get("mean", 0) +
        results.get("audit_trail_sealing", {}).get("mean", 0)
    )
    pipeline_p95 = (
        results.get("tesseract_ocr", {}).get("p95", 0) +
        results.get("statutory_rules", {}).get("p95", 0) +
        results.get("biometric_face_verification", {}).get("p95", 0) +
        results.get("cross_document_reconciliation", {}).get("p95", 0) +
        results.get("audit_trail_sealing", {}).get("p95", 0)
    )
    results["pipeline_total_estimated"] = {
        "mean_ms": round(pipeline_mean, 2),
        "p95_ms": round(pipeline_p95, 2),
        "mean_seconds": round(pipeline_mean / 1000, 3),
        "p95_seconds": round(pipeline_p95 / 1000, 3)
    }

    # Print Summary Table
    print("\n" + "=" * 80)
    print("                    EMPIRICAL BENCHMARK SUMMARY TABLE")
    print("=" * 80)
    print(f"{'Pipeline Component':<35} | {'P50 (ms)':<10} | {'P90 (ms)':<10} | {'P95 (ms)':<10} | {'P99 (ms)':<10}")
    print("-" * 80)
    for k in ["statutory_rules", "cross_document_reconciliation", "audit_trail_sealing", "biometric_face_verification", "tesseract_ocr"]:
        if k in results and isinstance(results[k], dict) and "p50" in results[k]:
            name = k.replace("_", " ").title()
            print(f"{name:<35} | {results[k]['p50']:<10.2f} | {results[k]['p90']:<10.2f} | {results[k]['p95']:<10.2f} | {results[k]['p99']:<10.2f}")
    print("-" * 80)
    print(f"Total Pipeline Execution (Estimated) : {results['pipeline_total_estimated']['mean_ms']:.2f} ms ({results['pipeline_total_estimated']['mean_seconds']} s)")
    print(f"P95 Pipeline Latency Cap             : {results['pipeline_total_estimated']['p95_ms']:.2f} ms ({results['pipeline_total_estimated']['p95_seconds']} s)")
    print(f"Peak Heap RAM Utilization            : {results['peak_ram_allocated_mb']} MB")
    print("=" * 80)

    # Save empirical results to JSON
    out_file = os.path.join(ROOT_DIR, "empirical_benchmark_report.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] Empirical benchmark report written to: {out_file}")
    return results

if __name__ == "__main__":
    run_benchmarks(iterations=30)
