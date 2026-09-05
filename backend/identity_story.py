# backend/identity_story.py
"""
VeriGuard AI - Identity Story Narrative Engine
Synthesizes demographic data, cross-document reconciliation, biometric matching,
and tamper forensics into a coherent, human-readable executive briefing.
"""

from typing import List, Dict, Any, Optional


def generate_identity_story(
    documents: List[Dict[str, Any]],
    cross_report: Optional[Dict[str, Any]] = None,
    face_match: Optional[Dict[str, Any]] = None,
    overall_risk: str = "LOW",
    risk_score: int = 0
) -> Dict[str, Any]:
    """
    Constructs a comprehensive identity narrative for human compliance officers.
    """
    num_docs = len(documents)
    is_multi = num_docs > 1 and cross_report is not None

    # Collect subject names and DOBs
    names = [d.get("name") for d in documents if d.get("name") and d.get("name") != "Not detected"]
    dobs = [d.get("dob") for d in documents if d.get("dob") and d.get("dob") != "Not detected"]
    doc_types = [d.get("type", "Document") for d in documents]
    doc_nums = [d.get("number", "N/A") for d in documents]

    primary_name = names[0] if names else "Unidentified Individual"
    primary_dob = dobs[0] if dobs else "Unspecified"

    paragraphs = []
    headline = ""
    status_tier = "GENUINE"
    recommendation = ""

    # =========================================================================
    # MULTI-DOCUMENT NARRATIVE
    # =========================================================================
    if is_multi:
        is_consistent = cross_report.get("is_consistent", True)
        consistency_score = cross_report.get("consistency_score", 100)
        inconsistencies = cross_report.get("inconsistencies", [])
        face_bio = cross_report.get("face_biometrics", {})

        doc_summary_parts = [
            f"{doc_types[i]} ({doc_nums[i]})" if doc_nums[i] != "N/A" else doc_types[i]
            for i in range(num_docs)
        ]
        doc_summary_str = " and ".join(doc_summary_parts) if len(doc_summary_parts) == 2 else ", ".join(doc_summary_parts)

        # 1. Demographic consistency narrative
        name_inconsistencies = [inc for inc in inconsistencies if inc.get("field") == "Name"]
        dob_inconsistencies = [inc for inc in inconsistencies if inc.get("field") == "Date of Birth"]
        num_inconsistencies = [inc for inc in inconsistencies if inc.get("field") == "Document Number"]

        if is_consistent:
            headline = f"{primary_name} verified across {num_docs} documents with consistent demographic and biometric profile."
            status_tier = "CONFIRMED_CONSISTENT"
            p1 = (
                f"Subject {primary_name} presented {num_docs} identity documents ({doc_summary_str}). "
                f"Demographic reconciliation confirms that the subject's full name and Date of Birth ({primary_dob}) "
                f"appear consistently across all submitted documents without conflict."
            )
        else:
            headline = f"Identity Conflict Detected: Inconsistencies flagged across {num_docs} documents for subject {primary_name}."
            status_tier = "FLAGGED_INCONSISTENCY"
            issues_text = []
            if name_inconsistencies:
                issues_text.append(f"a name mismatch ({name_inconsistencies[0].get('description')})")
            if dob_inconsistencies:
                issues_text.append(f"conflicting dates of birth ({dob_inconsistencies[0].get('description')})")
            if num_inconsistencies:
                issues_text.append(f"document number discrepancies ({num_inconsistencies[0].get('description')})")

            issues_summary = "; ".join(issues_text) if issues_text else "conflicting record attributes"
            p1 = (
                f"Cross-document screening of {num_docs} submitted records ({doc_summary_str}) "
                f"revealed critical identity discrepancies, including {issues_summary}. "
                f"Overall demographic consistency score is {consistency_score}%."
            )
        paragraphs.append(p1)

        # 2. Biometric Facial Narrative
        pairs = face_bio.get("pairs", [])
        doc_pairs = [p for p in pairs if p.get("type") == "doc_to_doc"]
        selfie_pairs = [p for p in pairs if p.get("type") == "selfie_to_doc"]

        if doc_pairs:
            doc_p = doc_pairs[0]
            if doc_p.get("is_match"):
                p_bio = (
                    f"Biometric cross-matching of document portraits confirms that {doc_p['source']} "
                    f"and {doc_p['target']} depict the identical individual with {doc_p['match_score']}% facial similarity."
                )
            else:
                p_bio = (
                    f"Biometric analysis detected a portrait mismatch between {doc_p['source']} and {doc_p['target']} "
                    f"(match score {doc_p['match_score']}%, below the 60% decision threshold), indicating possible synthetic record substitution."
                )

            if selfie_pairs:
                selfie_p = selfie_pairs[0]
                if selfie_p.get("is_match"):
                    p_bio += f" Furthermore, the submitted live selfie verified identity with {selfie_p['match_score']}% confidence."
                else:
                    p_bio += f" However, the submitted live selfie failed biometric matching against document portraits ({selfie_p['match_score']}% similarity)."

            paragraphs.append(p_bio)
        elif face_match and face_match.get("score", 0) > 0:
            if face_match.get("passed"):
                paragraphs.append(
                    f"Biometric face verification successfully validated the applicant against the submitted selfie with {face_match['score']}% similarity."
                )
            else:
                paragraphs.append(
                    f"Biometric verification flagged a face mismatch with the submitted selfie ({face_match['score']}% match)."
                )

        # 3. Forensics & Document Validity Narrative
        has_tampering = any(d.get("tampering_signals") for d in documents)
        if not has_tampering:
            paragraphs.append(
                f"Forensic inspection detected no signs of pixel-level tampering, digital splicing, or metadata manipulation across any of the {num_docs} uploaded documents."
            )
        else:
            paragraphs.append(
                f"Digital forensics flagged potential tampering artifacts (compression noise or edge anomalies) on one or more documents, warranting secondary inspection."
            )

        # 4. Recommendation
        if is_consistent and overall_risk == "LOW":
            recommendation = (
                "Automated clearance approved. The subject demonstrates unbroken cross-document continuity "
                "and authentic biometric correlation across all records."
            )
        elif overall_risk == "MEDIUM":
            recommendation = (
                "Routing to secondary review. Minor demographic variance or image quality anomalies require manual officer sign-off before clearance."
            )
        else:
            recommendation = (
                "Action Required: Immediate escalation to Tier-1 fraud investigation. Severe identity attribute contradictions "
                "or biometric discrepancies indicate high impersonation risk."
            )

    # =========================================================================
    # SINGLE DOCUMENT NARRATIVE
    # =========================================================================
    else:
        doc = documents[0] if documents else {}
        doc_type = doc.get("type", "Identity Document")
        doc_num = doc.get("number", "Unextracted")
        expiry = doc.get("expiry", "Not detected")

        headline = f"Subject {primary_name} screened via {doc_type} (#{doc_num})."
        p1 = (
            f"Subject {primary_name} submitted a single {doc_type} (Document #{doc_num}) "
            f"with recorded Date of Birth {primary_dob}. Document validity checks confirm "
            f"{'valid unexpired credentials through ' + expiry if expiry != 'Not detected' else 'document format parsed successfully'}."
        )
        paragraphs.append(p1)

        # Face verification narrative
        if face_match and face_match.get("score", 0) > 0:
            if face_match.get("passed"):
                status_tier = "CONFIRMED_GENUINE"
                paragraphs.append(
                    f"Biometric authentication verified the subject's live selfie against the {doc_type} portrait with "
                    f"{face_match['score']}% facial similarity (128D ResNet vector distance {face_match.get('distance', 'verified')})."
                )
            else:
                status_tier = "BIOMETRIC_MISMATCH"
                paragraphs.append(
                    f"Biometric authentication failed: Submitted selfie scored {face_match['score']}% similarity against the "
                    f"document portrait, failing the 60% verification threshold."
                )
        else:
            paragraphs.append(
                "No live selfie was provided during this screening session; verification is based solely on document data integrity and forensic analysis."
            )

        # Security Failures & Counterfeit narrative
        security_failures = [f for f in doc.get("findings", []) if f.get("status") == "FAIL"]
        if security_failures:
            status_tier = "CRITICAL_FRAUD_ALERT" if overall_risk == "HIGH" else "SECURITY_ANOMALY"
            reasons = "; ".join(f.get("reason", "") for f in security_failures[:2])
            paragraphs.append(
                f"CRITICAL SECURITY ALERT: The submitted {doc_type} failed statutory security verification ({reasons}). "
                "Document exhibits structural, checksum, or sovereign authority anomalies inconsistent with genuine credentials."
            )
            headline = f"Security Alert: Suspect {doc_type} (#{doc_num}) flagged for potential forgery."

        # Tampering narrative
        if doc.get("tampering_signals"):
            paragraphs.append("Digital forensic analysis detected anomalies requiring manual inspection.")
        elif not security_failures:
            paragraphs.append("Digital forensic checks confirmed genuine texture continuity and authentic metadata signatures.")

        if overall_risk == "LOW":
            recommendation = f"Standard clearance recommended. The submitted {doc_type} appears authentic and uncompromised."
        elif overall_risk == "MEDIUM":
            recommendation = "Secondary review recommended. Officer should verify physical document security features."
        else:
            recommendation = "Action Required: Immediate escalation to fraud unit. Document failed forensic and statutory integrity checks."

    # Key Facts summary table
    key_facts = [
        {"label": "Confirmed Name", "value": primary_name},
        {"label": "Date of Birth", "value": primary_dob},
        {"label": "Documents Screened", "value": f"{num_docs} ({', '.join(doc_types)})"},
        {"label": "Biometric Verdict", "value": f"{face_match.get('score', 0)}% Match" if face_match else "N/A"},
        {"label": "Overall Risk Assessment", "value": f"{risk_score}/100 ({overall_risk} RISK)"},
    ]

    return {
        "headline": headline,
        "status_tier": status_tier,
        "paragraphs": paragraphs,
        "key_facts": key_facts,
        "recommendation": recommendation,
        "primary_name": primary_name,
        "primary_dob": primary_dob,
    }
