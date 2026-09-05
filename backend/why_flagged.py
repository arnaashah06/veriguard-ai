# backend/why_flagged.py
"""
VeriGuard AI - Enhanced Why-Flagged Engine & Officer Priority Queue
Decomposes screening risk scores into visual, color-coded factors across 4 standardized domains:
1. Document Authenticity & Digital Forensics
2. Biometric Facial Verification
3. Data & Cross-Document Consistency
4. Watchlist & Compliance Checks

Sorts all findings into a structured Officer Priority Queue with actionable guidance.
"""

from typing import List, Dict, Any, Optional


def decompose_risk(
    documents: List[Dict[str, Any]],
    findings: List[Dict[str, Any]],
    cross_report: Optional[Dict[str, Any]] = None,
    face_match: Optional[Dict[str, Any]] = None,
    risk_score: int = 0,
    overall_risk: str = "LOW"
) -> Dict[str, Any]:
    """
    Decomposes risk score into categorized factors and structures an Officer Priority Queue.
    """
    factors = []
    domain_points = {
        "AUTHENTICITY": 0,
        "BIOMETRICS": 0,
        "DATA_INTEGRITY": 0,
        "COMPLIANCE": 0,
    }

    # -------------------------------------------------------------------------
    # 1. BIOMETRIC FACE FACTORS
    # -------------------------------------------------------------------------
    if face_match:
        score = face_match.get("score", 0)
        passed = face_match.get("passed", False)
        msg = face_match.get("message", "")

        if score > 0 and not passed:
            impact = 25
            domain_points["BIOMETRICS"] += impact
            factors.append({
                "id": "bio_face_mismatch",
                "category": "BIOMETRICS",
                "category_label": "Biometric Facial Verification",
                "category_icon": "👤",
                "title": "Biometric Face Mismatch",
                "severity": "HIGH",
                "points_impact": impact,
                "status": "FAIL",
                "evidence": f"Face verification score {score}% is below the 60% threshold. ({msg})",
                "officer_action": "Request high-resolution re-take of live selfie or mandate in-person physical identity check.",
                "review_state": "PENDING"
            })
        elif score >= 60 and passed:
            factors.append({
                "id": "bio_face_verified",
                "category": "BIOMETRICS",
                "category_label": "Biometric Facial Verification",
                "category_icon": "👤",
                "title": "Biometric Identity Confirmed",
                "severity": "PASS",
                "points_impact": 0,
                "status": "PASS",
                "evidence": f"Biometric face match verified with {score}% confidence (128D ResNet embedding match).",
                "officer_action": "No action needed. Biometric portrait correlation verified.",
                "review_state": "CLEARED"
            })

    # -------------------------------------------------------------------------
    # 2. CROSS-DOCUMENT IDENTITY FACTORS
    # -------------------------------------------------------------------------
    if cross_report and cross_report.get("is_multi_document"):
        inconsistencies = cross_report.get("inconsistencies", [])
        for inc in inconsistencies:
            field = inc.get("field", "Attribute")
            severity = inc.get("severity", "MEDIUM")
            desc = inc.get("description", "")
            docs = inc.get("docs", "")

            if field == "Name":
                impact = 35
                domain_points["DATA_INTEGRITY"] += impact
                action = "Inspect both documents for legal name alias, marriage certificate, or deed poll documentation."
            elif field == "Date of Birth":
                impact = 30 if severity == "HIGH" else 15
                domain_points["DATA_INTEGRITY"] += impact
                action = "Verify primary civil registry records to identify correct legal Date of Birth."
            elif field == "Document Number":
                impact = 35
                domain_points["DATA_INTEGRITY"] += impact
                action = "Check for stolen/counterfeit document alert on database for conflicting document number."
            elif field == "Biometric Face":
                impact = 35
                domain_points["BIOMETRICS"] += impact
                action = "Escalate immediately to fraud unit: Multiple documents submitted with differing portraits."
            else:
                impact = 15
                domain_points["DATA_INTEGRITY"] += impact
                action = "Review flagged attribute discrepancies with applicant."

            factors.append({
                "id": f"cross_doc_{field.lower().replace(' ', '_')}",
                "category": "BIOMETRICS" if field == "Biometric Face" else "DATA_INTEGRITY",
                "category_label": "Biometric Facial Verification" if field == "Biometric Face" else "Cross-Document Consistency",
                "category_icon": "👤" if field == "Biometric Face" else "📑",
                "title": f"Cross-Document {field} Discrepancy",
                "severity": severity,
                "points_impact": impact,
                "status": "FAIL" if severity == "HIGH" else "WARNING",
                "evidence": f"{docs}: {desc}",
                "officer_action": action,
                "review_state": "PENDING"
            })

        # Record positive cross-document matches
        for match in cross_report.get("matches", []):
            factors.append({
                "id": f"cross_match_{abs(hash(match)) % 10000}",
                "category": "DATA_INTEGRITY",
                "category_label": "Cross-Document Consistency",
                "category_icon": "📑",
                "title": "Cross-Document Consistency Match",
                "severity": "PASS",
                "points_impact": 0,
                "status": "PASS",
                "evidence": match,
                "officer_action": "No action needed. Cross-document identity consistent.",
                "review_state": "CLEARED"
            })

    # -------------------------------------------------------------------------
    # 3. DOCUMENT AUTHENTICITY & FORENSICS FACTORS
    # -------------------------------------------------------------------------
    has_tampering = False
    for doc in documents:
        for sig in doc.get("tampering_signals", []):
            has_tampering = True
            sev = sig.get("severity", "MEDIUM")
            impact = 30 if sev == "HIGH" else (15 if sev == "MEDIUM" else 5)
            domain_points["AUTHENTICITY"] += impact

            factors.append({
                "id": f"tamper_{abs(hash(sig.get('details', ''))) % 10000}",
                "category": "AUTHENTICITY",
                "category_label": "Document Authenticity & Forensics",
                "category_icon": "🛡️",
                "title": f"Tampering Flag: {sig.get('type', 'Digital Anomaly')}",
                "severity": sev,
                "points_impact": impact,
                "status": "FAIL" if sev in ["HIGH", "MEDIUM"] else "WARNING",
                "evidence": f"{doc.get('filename')}: {sig.get('details', 'Potential image manipulation detected')}",
                "officer_action": "Inspect physical security features (guilloche patterns, holograms, microprint) under UV light.",
                "review_state": "PENDING"
            })

    if not has_tampering:
        factors.append({
            "id": "forensics_clean",
            "category": "AUTHENTICITY",
            "category_label": "Document Authenticity & Forensics",
            "category_icon": "🛡️",
            "title": "Digital Forensics Clean",
            "severity": "PASS",
            "points_impact": 0,
            "status": "PASS",
            "evidence": "No ELA anomalies, copy-move cloning, or suspicious editing software metadata detected.",
            "officer_action": "No action needed. Image authenticity verified.",
            "review_state": "CLEARED"
        })

    # -------------------------------------------------------------------------
    # 4. COMPLIANCE & LIFECYCLE FACTORS (Expiry, Blacklist, Required Fields)
    # -------------------------------------------------------------------------
    for finding in findings:
        check = finding.get("check", "")
        status = finding.get("status", "")
        reason = finding.get("reason", "")

        if "Blacklist" in check and status == "FAIL":
            domain_points["COMPLIANCE"] += 50
            factors.append({
                "id": "blacklist_hit",
                "category": "COMPLIANCE",
                "category_label": "Watchlist & Compliance",
                "category_icon": "🗄️",
                "title": "Watchlist / Blacklist Hit",
                "severity": "CRITICAL",
                "points_impact": 50,
                "status": "FAIL",
                "evidence": f"Document number matches active watchlist registry: {reason}",
                "officer_action": "Immediate stop-notice. Notify supervisory compliance officer and regulatory reporting desk.",
                "review_state": "PENDING"
            })
        elif "Expiry" in check and status == "FAIL":
            domain_points["COMPLIANCE"] += 30
            factors.append({
                "id": "doc_expired",
                "category": "COMPLIANCE",
                "category_label": "Watchlist & Compliance",
                "category_icon": "🗄️",
                "title": "Document Expired",
                "severity": "HIGH",
                "points_impact": 30,
                "status": "FAIL",
                "evidence": reason,
                "officer_action": "Reject as expired credentials. Request current, valid government-issued photo ID.",
                "review_state": "PENDING"
            })
        elif "Expiry" in check and status == "WARNING" and "soon" in reason.lower():
            domain_points["COMPLIANCE"] += 10
            factors.append({
                "id": "doc_expiring_soon",
                "category": "COMPLIANCE",
                "category_label": "Watchlist & Compliance",
                "category_icon": "🗄️",
                "title": "Document Expiring Soon",
                "severity": "MEDIUM",
                "points_impact": 10,
                "status": "WARNING",
                "evidence": reason,
                "officer_action": "Document is valid but approaching expiry. Note expiry date in subject profile.",
                "review_state": "PENDING"
            })
        elif "Passport Security" in check or "MRZ" in check:
            if status in ["FAIL", "WARNING"]:
                is_fail = status == "FAIL"
                impact = 45 if is_fail else 20
                domain_points["AUTHENTICITY"] += impact
                factors.append({
                    "id": f"passport_sec_{abs(hash(check + reason)) % 10000}",
                    "category": "AUTHENTICITY",
                    "category_label": "Document Authenticity & Forensics",
                    "category_icon": "🛡️",
                    "title": check,
                    "severity": "CRITICAL" if ("Sovereign" in check or "Filler" in check or "Checksum" in check) and is_fail else ("HIGH" if is_fail else "MEDIUM"),
                    "points_impact": impact,
                    "status": status,
                    "evidence": reason,
                    "officer_action": "Impound credential. Initiate fraudulent travel document investigation and notify border/KYC compliance.",
                    "review_state": "PENDING"
                })
        elif "Aadhaar Security" in check and status in ["FAIL", "WARNING"]:
            is_fail = status == "FAIL"
            impact = 35 if is_fail else 15
            domain_points["AUTHENTICITY"] += impact
            factors.append({
                "id": f"aadhaar_sec_{abs(hash(check + reason)) % 10000}",
                "category": "AUTHENTICITY",
                "category_label": "Document Authenticity & Forensics",
                "category_icon": "🛡️",
                "title": check,
                "severity": "CRITICAL" if "Verhoeff" in check and is_fail else ("HIGH" if is_fail else "MEDIUM"),
                "points_impact": impact,
                "status": status,
                "evidence": reason,
                "officer_action": "Verify UIDAI online verification API and inspect physical QR code/hologram.",
                "review_state": "PENDING"
            })
        elif "PAN Security" in check and status in ["FAIL", "WARNING"]:
            is_fail = status == "FAIL"
            impact = 30 if is_fail else 15
            domain_points["DATA_INTEGRITY"] += impact
            factors.append({
                "id": f"pan_sec_{abs(hash(check + reason)) % 10000}",
                "category": "DATA_INTEGRITY",
                "category_label": "Cross-Document Consistency",
                "category_icon": "📑",
                "title": check,
                "severity": "HIGH" if is_fail else "MEDIUM",
                "points_impact": impact,
                "status": status,
                "evidence": reason,
                "officer_action": "Check Income Tax Department NSDL/UTIITSL verification database for PAN status.",
                "review_state": "PENDING"
            })
        elif "Name" in check and status in ["FAIL", "WARNING"]:
            is_fail = status == "FAIL"
            impact = 35 if is_fail else 15
            domain_points["DATA_INTEGRITY"] += impact
            factors.append({
                "id": f"name_sec_{abs(hash(check + reason)) % 10000}",
                "category": "DATA_INTEGRITY",
                "category_label": "Cross-Document Consistency",
                "category_icon": "📑",
                "title": check,
                "severity": "HIGH" if is_fail else "MEDIUM",
                "points_impact": impact,
                "status": status,
                "evidence": reason,
                "officer_action": "Subject name failed phonetic/structural validation. Request secondary primary identification.",
                "review_state": "PENDING"
            })

    # -------------------------------------------------------------------------
    # 5. CONSTRUCT OFFICER PRIORITY QUEUE
    # -------------------------------------------------------------------------
    # Sort order: CRITICAL (0), HIGH (1), MEDIUM (2), LOW (3), PASS (4)
    severity_rank = {
        "CRITICAL": 0,
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3,
        "PASS": 4,
    }

    priority_queue = sorted(
        factors,
        key=lambda f: (severity_rank.get(f.get("severity"), 5), -f.get("points_impact", 0))
    )

    action_required_items = [f for f in priority_queue if f.get("severity") != "PASS"]

    # Assign Priority Tier
    if any(f.get("severity") == "CRITICAL" for f in priority_queue) or risk_score >= 60:
        officer_tier = "TIER_1_IMMEDIATE_ESCALATION"
        tier_label = "Tier 1: Immediate Escalation Required"
        tier_color = "#DC2626"
        officer_summary = f"{len(action_required_items)} high-risk flags require mandatory senior investigator review before clearance."
    elif any(f.get("severity") in ["HIGH", "MEDIUM"] for f in priority_queue) or risk_score >= 30:
        officer_tier = "TIER_2_SECONDARY_REVIEW"
        tier_label = "Tier 2: Standard Secondary Inspection"
        tier_color = "#D97706"
        officer_summary = f"{len(action_required_items)} moderate items flagged. Officer verification recommended."
    else:
        officer_tier = "TIER_3_FAST_TRACK"
        tier_label = "Tier 3: Fast-Track Clearance Eligible"
        tier_color = "#16A34A"
        officer_summary = "All automated verification checks passed. Identity meets fast-track approval standards."

    return {
        "overall_risk": overall_risk,
        "risk_score": risk_score,
        "officer_tier": officer_tier,
        "tier_label": tier_label,
        "tier_color": tier_color,
        "officer_summary": officer_summary,
        "domain_points": domain_points,
        "priority_queue": priority_queue,
        "action_required_count": len(action_required_items),
        "total_checks_evaluated": len(priority_queue),
    }
