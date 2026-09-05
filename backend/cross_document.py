# backend/cross_document.py
"""
VeriGuard AI - Cross-Document Consistency Engine
Performs multi-document identity reconciliation:
1. Name comparison (Token Set overlap, Levenshtein distance, middle name omission, initials).
2. Date of Birth comparison (Multi-format normalization, date matching, year check).
3. Document Number & Type cross-verification.
4. Cross-document biometric face matching (Doc 1 Portrait vs Doc 2 Portrait).
5. Comprehensive consistency scoring and risk penalty aggregation.
"""

import os
import re
import difflib
from datetime import datetime
from typing import List, Dict, Any, Optional


class CrossDocumentValidator:
    def __init__(self):
        # Common title honorifics to strip during name normalization
        self.titles = {
            "MR", "MRS", "MS", "MISS", "DR", "PROF", "MD",
            "SHRI", "SMT", "KUMARI", "MASTER", "SIR", "MADAM"
        }

    # =========================================================================
    # 1. NAME NORMALIZATION & COMPARISON
    # =========================================================================

    def normalize_name(self, name: Optional[str]) -> str:
        """
        Cleans and normalizes a person's name:
        - Uppercases and strips leading/trailing whitespace
        - Strips OCR artifacts, unwanted suffixes (DOB, dates, etc.)
        - Removes common titles/honorifics
        - Normalizes multiple spaces into a single space
        """
        if not name:
            return ""

        # Remove "DOB", "Date of Birth", and anything trailing
        cleaned = re.sub(r"\s*(DOB|Date of Birth|Birth)\b.*$", "", name, flags=re.IGNORECASE)
        # Remove non-alpha except space and hyphen
        cleaned = re.sub(r"[^A-Za-z\s\-]", " ", cleaned)
        cleaned = cleaned.upper().strip()

        # Tokenize and remove known titles
        tokens = [t for t in re.split(r"[\s\-]+", cleaned) if t]
        filtered = [t for t in tokens if t not in self.titles]

        return " ".join(filtered)

    def compare_names(self, name1: Optional[str], name2: Optional[str]) -> Dict[str, Any]:
        """
        Compares two names across documents using hybrid matching:
        - Exact match
        - Token subset match (handles middle name omission, e.g. "ANNA MARIA ERIKSSON" vs "ANNA ERIKSSON")
        - Token reordering (e.g. "DOE JOHN" vs "JOHN DOE")
        - Levenshtein SequenceMatcher fuzzy similarity (handles minor OCR misspellings)
        """
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)

        if not norm1 or not norm2 or norm1 == "NOT DETECTED" or norm2 == "NOT DETECTED":
            return {
                "field": "Name",
                "val1": name1 or "Not detected",
                "val2": name2 or "Not detected",
                "status": "UNKNOWN",
                "is_consistent": True,
                "similarity_score": 0,
                "severity": "LOW",
                "reason": "Name missing or undetected in one or both documents",
                "badge": "⚠️ Undetected",
            }

        # 1. Exact string match
        if norm1 == norm2:
            return {
                "field": "Name",
                "val1": norm1,
                "val2": norm2,
                "status": "EXACT",
                "is_consistent": True,
                "similarity_score": 100,
                "severity": "NONE",
                "reason": "Names match exactly across documents",
                "badge": "✅ Exact Match",
            }

        tokens1 = set(norm1.split())
        tokens2 = set(norm2.split())

        # 2. Token Set Equality (Reordered tokens, e.g. Last First vs First Last)
        if tokens1 == tokens2:
            return {
                "field": "Name",
                "val1": norm1,
                "val2": norm2,
                "status": "EXACT_REORDERED",
                "is_consistent": True,
                "similarity_score": 98,
                "severity": "NONE",
                "reason": "Identical name tokens present in different order",
                "badge": "✅ Name Match",
            }

        # 3. Token Subset (Middle name added or omitted)
        if tokens1.issubset(tokens2) or tokens2.issubset(tokens1):
            overlap = tokens1.intersection(tokens2)
            jaccard = len(overlap) / max(len(tokens1.union(tokens2)), 1)
            score = round(80.0 + (jaccard * 18.0), 1)
            return {
                "field": "Name",
                "val1": norm1,
                "val2": norm2,
                "status": "HIGH_SIMILARITY",
                "is_consistent": True,
                "similarity_score": score,
                "severity": "LOW",
                "reason": "Consistent name with middle name or initial variation",
                "badge": "✅ Name Match (Partial/Middle)",
            }

        # 4. Fuzzy character similarity ratio
        ratio = difflib.SequenceMatcher(None, norm1, norm2).ratio()
        fuzzy_score = round(ratio * 100, 1)

        # Token overlap ratio
        common_tokens = tokens1.intersection(tokens2)
        has_common_surname_or_given = len(common_tokens) >= 1

        if ratio >= 0.85:
            return {
                "field": "Name",
                "val1": norm1,
                "val2": norm2,
                "status": "HIGH_SIMILARITY",
                "is_consistent": True,
                "similarity_score": fuzzy_score,
                "severity": "LOW",
                "reason": f"High character similarity ({fuzzy_score}%) - probable minor spelling or OCR variation",
                "badge": "✅ Minor Variation",
            }
        elif ratio >= 0.65 and has_common_surname_or_given:
            return {
                "field": "Name",
                "val1": norm1,
                "val2": norm2,
                "status": "PARTIAL_MATCH",
                "is_consistent": True,
                "similarity_score": fuzzy_score,
                "severity": "MEDIUM",
                "reason": f"Partial name match ({fuzzy_score}%) with shared name component: {', '.join(common_tokens)}",
                "badge": "🟡 Partial Match",
            }
        else:
            return {
                "field": "Name",
                "val1": norm1,
                "val2": norm2,
                "status": "MISMATCH",
                "is_consistent": False,
                "similarity_score": fuzzy_score,
                "severity": "HIGH",
                "reason": f"Name discrepancy detected: '{norm1}' vs '{norm2}' (similarity {fuzzy_score}%)",
                "badge": "❌ Name Mismatch",
            }

    # =========================================================================
    # 2. DATE OF BIRTH NORMALIZATION & COMPARISON
    # =========================================================================

    def normalize_dob(self, dob_str: Optional[str]) -> Optional[str]:
        """
        Parses various date strings into ISO format YYYY-MM-DD.
        Handles:
        - 12/08/1974, 12-08-1974, 12.08.1974
        - 1974-08-12, 1974/08/12
        - 12 Aug 1974, 12 August 1974, Aug 12 1974
        """
        if not dob_str:
            return None

        cleaned = str(dob_str).strip()
        # Remove extra words like "DOB", "Birth"
        cleaned = re.sub(r"^(DOB|Date of Birth|Birth)[:\s]*", "", cleaned, flags=re.IGNORECASE).strip()

        date_formats = [
            "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",
            "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d",
            "%m/%d/%Y", "%m-%d-%Y",
            "%d %b %Y", "%d %B %Y",
            "%b %d %Y", "%B %d %Y",
            "%d%m%Y", "%Y%m%d"
        ]

        for fmt in date_formats:
            try:
                dt = datetime.strptime(cleaned, fmt)
                if 1900 <= dt.year <= datetime.now().year:
                    return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

        # Try regex search for 4-digit year and 2-digit components
        m = re.search(r"\b(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})\b", cleaned)
        if m:
            d, mth, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
            try:
                dt = datetime(y, mth, d)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass

        m2 = re.search(r"\b(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})\b", cleaned)
        if m2:
            y, mth, d = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))
            try:
                dt = datetime(y, mth, d)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass

        return None

    def compare_dobs(self, dob1: Optional[str], dob2: Optional[str]) -> Dict[str, Any]:
        """
        Compares two birthdates across documents:
        - Exact date match
        - Year match with day/month transposition or mismatch
        - Date mismatch
        """
        norm1 = self.normalize_dob(dob1)
        norm2 = self.normalize_dob(dob2)

        if not norm1 or not norm2:
            return {
                "field": "Date of Birth",
                "val1": dob1 or "Not detected",
                "val2": dob2 or "Not detected",
                "status": "UNKNOWN",
                "is_consistent": True,
                "severity": "LOW",
                "reason": "DOB format could not be verified in one or both documents",
                "badge": "⚠️ Undetected",
            }

        if norm1 == norm2:
            return {
                "field": "Date of Birth",
                "val1": norm1,
                "val2": norm2,
                "status": "EXACT",
                "is_consistent": True,
                "severity": "NONE",
                "reason": f"Dates of birth match exactly across documents ({norm1})",
                "badge": "✅ Exact Match",
            }

        y1, m1, d1 = norm1.split("-")
        y2, m2, d2 = norm2.split("-")

        # Check if year matches but day/month differ
        if y1 == y2:
            # Check for day-month transposition (e.g. 05-12 vs 12-05)
            if m1 == d2 and d1 == m2:
                return {
                    "field": "Date of Birth",
                    "val1": norm1,
                    "val2": norm2,
                    "status": "PARTIAL_TRANSPOSITION",
                    "is_consistent": True,
                    "severity": "LOW",
                    "reason": f"Birth date format transposition detected ({norm1} vs {norm2}) — same year {y1}",
                    "badge": "🟡 Format Transposition",
                }
            return {
                "field": "Date of Birth",
                "val1": norm1,
                "val2": norm2,
                "status": "YEAR_MATCH_ONLY",
                "is_consistent": False,
                "severity": "MEDIUM",
                "reason": f"Birth year matches ({y1}) but day/month differs: {norm1} vs {norm2}",
                "badge": "⚠️ Month/Day Mismatch",
            }

        # Complete mismatch (different years)
        return {
            "field": "Date of Birth",
            "val1": norm1,
            "val2": norm2,
            "status": "MISMATCH",
            "is_consistent": False,
            "severity": "HIGH",
            "reason": f"DOB discrepancy detected: '{norm1}' vs '{norm2}'",
            "badge": "❌ DOB Mismatch",
        }

    # =========================================================================
    # 3. DOCUMENT NUMBER & TYPE VALIDATION
    # =========================================================================

    def compare_document_numbers(
        self,
        doc1_type: str,
        doc1_num: Optional[str],
        doc2_type: str,
        doc2_num: Optional[str]
    ) -> Dict[str, Any]:
        """
        Evaluates document number integrity:
        - If same document type: numbers MUST match (otherwise conflicting documents).
        - If different document types: numbers should be distinct and not suspiciously duplicated.
        """
        clean_num1 = re.sub(r"[\s\-]", "", str(doc1_num or "")).upper()
        clean_num2 = re.sub(r"[\s\-]", "", str(doc2_num or "")).upper()
        type1 = (doc1_type or "Unknown").strip().title()
        type2 = (doc2_type or "Unknown").strip().title()

        if not clean_num1 or not clean_num2 or clean_num1 == "NOTDETECTED" or clean_num2 == "NOTDETECTED":
            return {
                "field": "Document Number",
                "val1": doc1_num or "Not detected",
                "val2": doc2_num or "Not detected",
                "status": "UNKNOWN",
                "is_consistent": True,
                "severity": "LOW",
                "reason": f"Document number unextracted on one or both documents ({type1} / {type2})",
                "badge": "⚠️ Undetected",
            }

        # If same document type
        if type1.lower() == type2.lower() and type1.lower() not in ["unknown", "document"]:
            if clean_num1 == clean_num2:
                return {
                    "field": "Document Number",
                    "val1": f"{type1} #{doc1_num}",
                    "val2": f"{type2} #{doc2_num}",
                    "status": "EXACT",
                    "is_consistent": True,
                    "severity": "NONE",
                    "reason": f"Both {type1} documents reference the identical document number ({doc1_num})",
                    "badge": "✅ Matching Numbers",
                }
            else:
                return {
                    "field": "Document Number",
                    "val1": f"{type1} #{doc1_num}",
                    "val2": f"{type2} #{doc2_num}",
                    "status": "CONFLICT",
                    "is_consistent": False,
                    "severity": "HIGH",
                    "reason": f"Conflicting numbers for duplicate {type1}: '{doc1_num}' vs '{doc2_num}'",
                    "badge": "❌ Conflicting Numbers",
                }

        # If different document types
        if clean_num1 == clean_num2 and len(clean_num1) >= 4:
            return {
                "field": "Document Number",
                "val1": f"{type1} #{doc1_num}",
                "val2": f"{type2} #{doc2_num}",
                "status": "SUSPICIOUS_DUPLICATE",
                "is_consistent": False,
                "severity": "HIGH",
                "reason": f"Suspicious identical number '{clean_num1}' shared across different document types ({type1} & {type2})",
                "badge": "❌ Suspicious Duplication",
            }

        return {
            "field": "Document Number",
            "val1": f"{type1} #{doc1_num}",
            "val2": f"{type2} #{doc2_num}",
            "status": "DISTINCT_VALID",
            "is_consistent": True,
            "severity": "NONE",
            "reason": f"Valid distinct document identifiers for {type1} and {type2}",
            "badge": "✅ Distinct Valid IDs",
        }

    # =========================================================================
    # 4. CROSS-DOCUMENT BIOMETRIC FACE COMPARISON
    # =========================================================================

    def compare_document_faces(
        self,
        face_verifier,
        doc_paths: List[str],
        doc_names: List[str],
        selfie_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes pairwise face comparison across document portraits and against selfie.
        Returns pairwise scores, overall face consistency verdict, and matrix.
        """
        if not face_verifier:
            return {
                "evaluated": False,
                "overall_face_match": False,
                "cross_doc_score": 0,
                "message": "Face verifier instance not available",
                "pairs": []
            }

        pairs = []
        doc_face_scores = []
        overall_consistent = True

        # 1. Compare Doc i Portrait vs Doc j Portrait
        n = len(doc_paths)
        for i in range(n):
            for j in range(i + 1, n):
                p1, p2 = doc_paths[i], doc_paths[j]
                label1, label2 = doc_names[i], doc_names[j]

                try:
                    res = face_verifier.verify_face(p1, p2)
                    is_match = res.get("is_match", False)
                    score = res.get("match_score", 0)

                    pairs.append({
                        "type": "doc_to_doc",
                        "source": label1,
                        "target": label2,
                        "match_score": score,
                        "is_match": is_match,
                        "confidence": res.get("confidence", "LOW"),
                        "message": res.get("message", "Document portraits compared"),
                    })
                    if is_match:
                        doc_face_scores.append(score)
                    else:
                        overall_consistent = False
                except Exception as e:
                    pairs.append({
                        "type": "doc_to_doc",
                        "source": label1,
                        "target": label2,
                        "match_score": 0,
                        "is_match": False,
                        "confidence": "NONE",
                        "message": f"Portrait comparison error: {str(e)}",
                    })
                    overall_consistent = False

        # 2. Compare Selfie vs each Doc Portrait
        selfie_scores = []
        if selfie_path and os.path.exists(selfie_path):
            for i in range(n):
                p_doc = doc_paths[i]
                label_doc = doc_names[i]

                try:
                    res = face_verifier.verify_face(p_doc, selfie_path)
                    is_match = res.get("is_match", False)
                    score = res.get("match_score", 0)

                    pairs.append({
                        "type": "selfie_to_doc",
                        "source": "Selfie",
                        "target": label_doc,
                        "match_score": score,
                        "is_match": is_match,
                        "confidence": res.get("confidence", "LOW"),
                        "message": res.get("message", "Selfie compared with document portrait"),
                    })
                    if is_match:
                        selfie_scores.append(score)
                    else:
                        overall_consistent = False
                except Exception as e:
                    pairs.append({
                        "type": "selfie_to_doc",
                        "source": "Selfie",
                        "target": label_doc,
                        "match_score": 0,
                        "is_match": False,
                        "confidence": "NONE",
                        "message": f"Selfie comparison error: {str(e)}",
                    })

        all_scores = doc_face_scores + selfie_scores
        avg_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0

        return {
            "evaluated": len(pairs) > 0,
            "overall_face_match": overall_consistent and len(doc_face_scores) > 0,
            "cross_doc_score": avg_score,
            "pairs": pairs,
            "message": (
                f"✅ Biometric facial identity verified across documents ({avg_score}% avg match)"
                if overall_consistent and len(doc_face_scores) > 0
                else "⚠️ Facial comparison could not verify single identity across all documents"
            )
        }

    # =========================================================================
    # 4.5 INDIAN STATUTORY DEMOGRAPHIC LINKAGE (AADHAAR <-> PAN)
    # =========================================================================

    def check_aadhaar_pan_linkage(self, documents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Specialized Indian KYC verification:
        Reconciles Aadhaar Card and PAN Card when uploaded together, verifying
        demographic linkage, DOB match, and PAN 5th character vs Aadhaar surname.
        """
        aadhaar_doc = None
        pan_doc = None

        for d in documents:
            dtype = (d.get("type") or "").lower()
            if "aadhaar" in dtype:
                aadhaar_doc = d
            elif "pan" in dtype:
                pan_doc = d

        if not aadhaar_doc or not pan_doc:
            return None

        aadhaar_name = aadhaar_doc.get("name", "")
        pan_name = pan_doc.get("name", "")
        aadhaar_dob = aadhaar_doc.get("dob", "")
        pan_dob = pan_doc.get("dob", "")
        pan_num = (pan_doc.get("number") or "").upper().replace(" ", "")

        # 1. Compare names
        name_res = self.compare_names(aadhaar_name, pan_name)

        # 2. Check PAN 5th character against Aadhaar surname
        pan_surname_match = False
        surname_expected = ""
        actual_5th = ""
        if len(pan_num) == 10 and pan_num[3] == 'P' and aadhaar_name and aadhaar_name != "Not detected":
            name_parts = [p for p in aadhaar_name.strip().split() if len(p) > 1]
            if name_parts:
                surname_expected = name_parts[-1][0].upper()
                actual_5th = pan_num[4]
                pan_surname_match = (actual_5th == surname_expected)

        # 3. Compare DOBs
        dob_res = self.compare_dobs(aadhaar_dob, pan_dob)

        is_linked = name_res["is_consistent"] and dob_res["is_consistent"] and (pan_surname_match or not surname_expected)

        return {
            "is_applicable": True,
            "is_linked": is_linked,
            "aadhaar_name": aadhaar_name,
            "pan_name": pan_name,
            "pan_number": pan_num,
            "pan_surname_initial_check": {
                "passed": pan_surname_match,
                "expected": surname_expected,
                "actual": actual_5th,
            },
            "dob_match": dob_res["is_consistent"],
            "summary": (
                "Statutory Aadhaar-PAN linkage verified. Demographics and surname initial align."
                if is_linked else
                "Discrepancy detected between Aadhaar and PAN records. Statutory linkage flagged for review."
            )
        }

    # =========================================================================
    # 5. AGGREGATED CONSISTENCY EVALUATION
    # =========================================================================

    def evaluate_consistency(
        self,
        documents_data: List[Dict[str, Any]],
        doc_paths: List[str],
        selfie_path: Optional[str] = None,
        face_verifier=None
    ) -> Dict[str, Any]:
        """
        Executes complete cross-document consistency check across 2+ documents:
        - Pairwise Name, DOB, and Document Number checks.
        - Pairwise Document Face biometrics (and optional Selfie verification).
        - Flags inconsistencies with severity levels.
        - Computes consistency score (0 - 100) and risk penalty.
        """
        num_docs = len(documents_data)
        if num_docs < 2:
            return {
                "is_multi_document": False,
                "consistency_score": 100,
                "is_consistent": True,
                "inconsistencies": [],
                "matches": [],
                "comparisons": [],
                "risk_penalty": 0,
                "summary": "Single document verified. Cross-document comparison requires 2+ documents.",
            }

        doc_names = [
            f"Doc {i+1} ({doc.get('type', 'Document')})"
            for i, doc in enumerate(documents_data)
        ]

        comparisons = []
        inconsistencies = []
        matches = []
        risk_penalty = 0

        # Pairwise attribute comparisons
        for i in range(num_docs):
            for j in range(i + 1, num_docs):
                d1 = documents_data[i]
                d2 = documents_data[j]
                l1 = doc_names[i]
                l2 = doc_names[j]

                # --- 1. Compare Name ---
                name_comp = self.compare_names(d1.get("name"), d2.get("name"))
                name_entry = {
                    "doc1": l1,
                    "doc2": l2,
                    "field": "Name",
                    "val1": name_comp["val1"],
                    "val2": name_comp["val2"],
                    "status": name_comp["status"],
                    "badge": name_comp["badge"],
                    "severity": name_comp["severity"],
                    "reason": name_comp["reason"],
                    "is_consistent": name_comp["is_consistent"],
                }
                comparisons.append(name_entry)

                if not name_comp["is_consistent"]:
                    inconsistencies.append({
                        "field": "Name",
                        "docs": f"{l1} vs {l2}",
                        "severity": name_comp["severity"],
                        "description": name_comp["reason"],
                        "val1": name_comp["val1"],
                        "val2": name_comp["val2"],
                    })
                    risk_penalty += 35
                else:
                    matches.append(name_comp["reason"])

                # --- 2. Compare DOB ---
                dob_comp = self.compare_dobs(d1.get("dob"), d2.get("dob"))
                dob_entry = {
                    "doc1": l1,
                    "doc2": l2,
                    "field": "Date of Birth",
                    "val1": dob_comp["val1"],
                    "val2": dob_comp["val2"],
                    "status": dob_comp["status"],
                    "badge": dob_comp["badge"],
                    "severity": dob_comp["severity"],
                    "reason": dob_comp["reason"],
                    "is_consistent": dob_comp["is_consistent"],
                }
                comparisons.append(dob_entry)

                if not dob_comp["is_consistent"]:
                    inconsistencies.append({
                        "field": "Date of Birth",
                        "docs": f"{l1} vs {l2}",
                        "severity": dob_comp["severity"],
                        "description": dob_comp["reason"],
                        "val1": dob_comp["val1"],
                        "val2": dob_comp["val2"],
                    })
                    risk_penalty += 30 if dob_comp["severity"] == "HIGH" else 15
                else:
                    matches.append(dob_comp["reason"])

                # --- 3. Compare Document Number ---
                num_comp = self.compare_document_numbers(
                    d1.get("type", "Unknown"), d1.get("number"),
                    d2.get("type", "Unknown"), d2.get("number")
                )
                num_entry = {
                    "doc1": l1,
                    "doc2": l2,
                    "field": "Document Number",
                    "val1": num_comp["val1"],
                    "val2": num_comp["val2"],
                    "status": num_comp["status"],
                    "badge": num_comp["badge"],
                    "severity": num_comp["severity"],
                    "reason": num_comp["reason"],
                    "is_consistent": num_comp["is_consistent"],
                }
                comparisons.append(num_entry)

                if not num_comp["is_consistent"]:
                    inconsistencies.append({
                        "field": "Document Number",
                        "docs": f"{l1} vs {l2}",
                        "severity": num_comp["severity"],
                        "description": num_comp["reason"],
                        "val1": num_comp["val1"],
                        "val2": num_comp["val2"],
                    })
                    risk_penalty += 35
                else:
                    matches.append(num_comp["reason"])

        # --- 3.5. Indian Statutory Aadhaar-PAN Demographic Linkage ---
        aadhaar_pan_report = self.check_aadhaar_pan_linkage(documents_data)
        if aadhaar_pan_report:
            if aadhaar_pan_report["is_linked"]:
                matches.append(f"🇮🇳 Statutory Aadhaar-PAN Linkage Verified: Demographics align for PAN {aadhaar_pan_report['pan_number']}")
            else:
                inconsistencies.append({
                    "field": "Aadhaar-PAN Linkage",
                    "docs": "Aadhaar Card vs PAN Card",
                    "severity": "HIGH",
                    "description": aadhaar_pan_report["summary"],
                    "val1": aadhaar_pan_report.get("aadhaar_name", "Aadhaar Record"),
                    "val2": aadhaar_pan_report.get("pan_name", "PAN Record"),
                })
                risk_penalty += 30

        # --- 4. Biometric Face Cross-Verification ---
        face_results = self.compare_document_faces(
            face_verifier=face_verifier,
            doc_paths=doc_paths,
            doc_names=doc_names,
            selfie_path=selfie_path
        )

        for pair in face_results.get("pairs", []):
            if not pair.get("is_match", False) and pair.get("type") == "doc_to_doc":
                inconsistencies.append({
                    "field": "Biometric Face",
                    "docs": f"{pair['source']} vs {pair['target']}",
                    "severity": "HIGH",
                    "description": f"Facial mismatch between document portraits ({pair['match_score']}% match)",
                    "val1": pair['source'],
                    "val2": pair['target'],
                })
                risk_penalty += 35
            elif pair.get("is_match", False):
                matches.append(f"Biometric face verified between {pair['source']} and {pair['target']}")

        # Calculate overall consistency score (0 - 100)
        total_checks = len(comparisons) + len(face_results.get("pairs", []))
        failed_checks = len(inconsistencies)
        if total_checks > 0:
            raw_score = max(0, int(((total_checks - failed_checks) / total_checks) * 100))
        else:
            raw_score = 100

        # Adjust score if critical mismatch
        if any(inc.get("severity") == "HIGH" for inc in inconsistencies):
            consistency_score = min(raw_score, 45)
        else:
            consistency_score = raw_score

        is_consistent = len(inconsistencies) == 0

        if is_consistent:
            summary_status = "CONSISTENT"
            summary_msg = f"All {num_docs} documents demonstrate consistent identity attributes and biometric profile."
        elif consistency_score >= 60:
            summary_status = "PARTIALLY_CONSISTENT"
            summary_msg = f"{len(inconsistencies)} minor discrepancy flagged across documents. Review recommended."
        else:
            summary_status = "INCONSISTENT"
            summary_msg = f"Critical discrepancies detected across documents ({len(inconsistencies)} flagged). High risk of identity conflict or synthetic identity."

        return {
            "is_multi_document": True,
            "document_count": num_docs,
            "is_consistent": is_consistent,
            "consistency_status": summary_status,
            "consistency_score": consistency_score,
            "risk_penalty": risk_penalty,
            "summary": summary_msg,
            "inconsistencies": inconsistencies,
            "matches": matches,
            "comparisons": comparisons,
            "face_biometrics": face_results,
            "aadhaar_pan_linkage": aadhaar_pan_report,
        }
