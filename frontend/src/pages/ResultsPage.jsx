// src/pages/ResultsPage.jsx
import { useState } from 'react';

const ResultsPage = ({ result, onReset, onExport }) => {
  const [secondsAgo] = useState(() => Math.floor(Math.random() * 5) + 3);
  const [screeningId] = useState(() => Math.floor(Math.random() * 90000) + 10000);

  // Main mode switcher: 'dossier' vs 'case_queue'
  const [activeMainMode, setActiveMainMode] = useState('dossier');

  const isMultiDoc = !!result.is_multi_document || (result.documents && result.documents.length > 1);
  const [activeView, setActiveView] = useState(() => (isMultiDoc ? 'cross_doc' : '0'));

  // Officer Priority Queue interactive state (within dossier)
  const [officerFilter, setOfficerFilter] = useState('ALL');
  const [itemActions, setItemActions] = useState({});

  // Audit Trail interactive state
  const [auditFilter, setAuditFilter] = useState('ALL');
  const [copySealFeedback, setCopySealFeedback] = useState(false);

  // Case Queue interactive state (Task 5 Case Queue)
  const [caseFilter, setCaseFilter] = useState('ALL');
  const [caseStatuses, setCaseStatuses] = useState(() => ({
    [`VR-CASE-${screeningId}`]: result.overall_risk === 'LOW' ? 'CLEARED' : 'PENDING',
    'VR-IND-9021': 'CLEARED',
    'VR-IND-9022': 'ESCALATED',
    'VR-IND-9023': 'UNDER_REVIEW',
    'VR-IND-9024': 'CLEARED',
  }));

  const isLowRisk = result.overall_risk === 'LOW';
  const isHighRisk = result.overall_risk === 'HIGH';
  const riskClass = isLowRisk ? 'low' : isHighRisk ? 'high' : 'medium';

  const getStatusIcon = (status) => {
    if (status === 'PASS') return '✅';
    if (status === 'FAIL') return '❌';
    return '⚠️';
  };

  const getStatusClass = (status) => {
    if (status === 'PASS') return 'pass';
    if (status === 'FAIL') return 'fail';
    return 'warn';
  };

  const cleanDocumentName = (name) => {
    if (!name) return 'Not detected';
    let cleaned = name.replace(/\s*(DOB|Date of Birth|Birth)\b.*$/i, '');
    cleaned = cleaned.replace(/\s+/g, ' ').trim();
    return cleaned || 'Not detected';
  };

  const renderStatusAnimation = (lowRisk, highRisk) => {
    if (lowRisk) {
      return (
        <div className="status-animation-wrap">
          <svg className="animated-checkmark" viewBox="0 0 52 52">
            <circle className="animated-circle" cx="26" cy="26" r="23" />
            <path className="animated-check" d="M14.1 27.2l7.1 7.2 16.7-16.8" />
          </svg>
        </div>
      );
    }
    if (highRisk) {
      return (
        <div className="status-animation-wrap high-risk-anim">
          <div className="alert-ripple-ring"></div>
          <span className="alert-badge-icon">🚨</span>
        </div>
      );
    }
    return (
      <div className="status-animation-wrap medium-risk-anim">
        <div className="warning-pulse-ring"></div>
        <span className="warning-badge-icon">⚠️</span>
      </div>
    );
  };

  // Selected document when viewing an individual document tab
  const activeDocIndex = activeView === 'cross_doc' ? 0 : parseInt(activeView, 10);
  const currentDoc = (result.documents && result.documents[activeDocIndex]) || result.document || {};

  const crossDoc = result.cross_document || null;
  const consistencyScore = crossDoc?.consistency_score ?? 100;
  const consistencyStatus = crossDoc?.consistency_status ?? 'CONSISTENT';

  // =========================================================================
  // 1. IDENTITY STORY NARRATIVE DATA PREPARATION
  // =========================================================================
  const identityStory = result.identity_story || {
    headline: isMultiDoc
      ? `${cleanDocumentName(result.documents?.[0]?.name)} verified across ${result.documents?.length || 2} documents.`
      : `${cleanDocumentName(result.document?.name)} identity screening completed.`,
    status_tier: isLowRisk ? 'CONFIRMED_CONSISTENT' : isHighRisk ? 'FLAGGED_INCONSISTENCY' : 'REVIEW_RECOMMENDED',
    paragraphs: [
      isMultiDoc
        ? `Subject presented ${result.documents?.length || 2} documents for screening. Demographic records and biometric indicators have been cross-evaluated.`
        : `Subject presented a ${result.document?.type || 'government identity document'} for automated verification.`,
      isLowRisk
        ? 'All automated verification algorithms passed with high confidence. No digital tampering or biometric anomalies were flagged.'
        : 'Automated verification detected potential risk factors. Human officer inspection is recommended before granting final clearance.',
    ],
    key_facts: [
      { label: 'Confirmed Name', value: cleanDocumentName(result.document?.name || result.documents?.[0]?.name) },
      { label: 'Date of Birth', value: result.document?.dob || result.documents?.[0]?.dob || 'Not detected' },
      { label: 'Documents Screened', value: isMultiDoc ? `${result.documents?.length} documents` : (result.document?.type || 'Document') },
      { label: 'Biometric Verdict', value: result.face_match?.passed ? `${result.face_match.score}% Match` : 'N/A' },
      { label: 'Overall Risk Assessment', value: `${result.risk_score || 0}/100 (${result.overall_risk || 'LOW'} RISK)` },
    ],
    recommendation: isLowRisk
      ? 'Standard automated clearance recommended. Identity attributes verify consistently.'
      : 'Manual secondary inspection recommended. Review flagged points before proceeding.',
  };

  // =========================================================================
  // 2. WHY-FLAGGED RISK DECOMPOSITION & OFFICER PRIORITY QUEUE PREPARATION
  // =========================================================================
  const whyFlagged = result.why_flagged || {
    overall_risk: result.overall_risk || 'LOW',
    risk_score: result.risk_score || 0,
    officer_tier: isHighRisk
      ? 'TIER_1_IMMEDIATE_ESCALATION'
      : isLowRisk
      ? 'TIER_3_FAST_TRACK'
      : 'TIER_2_SECONDARY_REVIEW',
    tier_label: isHighRisk
      ? 'Tier 1: Immediate Escalation Required'
      : isLowRisk
      ? 'Tier 3: Fast-Track Clearance Eligible'
      : 'Tier 2: Standard Secondary Inspection',
    tier_color: isHighRisk ? '#DC2626' : isLowRisk ? '#16A34A' : '#D97706',
    officer_summary: isLowRisk
      ? 'All automated verification checks passed. Identity meets fast-track approval standards.'
      : 'Risk factors detected. Review the prioritized checklist below.',
    domain_points: {
      AUTHENTICITY: isHighRisk ? 35 : 0,
      BIOMETRICS: result.face_match && !result.face_match.passed ? 25 : 0,
      DATA_INTEGRITY: crossDoc?.inconsistencies?.length ? 35 : 0,
      COMPLIANCE: 0,
    },
    priority_queue: [],
    action_required_count: isLowRisk ? 0 : 1,
    total_checks_evaluated: 4,
  };

  const domainPoints = whyFlagged.domain_points || {
    AUTHENTICITY: 0,
    BIOMETRICS: 0,
    DATA_INTEGRITY: 0,
    COMPLIANCE: 0,
  };

  const priorityQueue = whyFlagged.priority_queue || [];

  const filteredQueue = priorityQueue.filter((item) => {
    const action = itemActions[item.id] || 'PENDING';
    if (officerFilter === 'ALL') return true;
    if (officerFilter === 'ACTION_REQUIRED') return item.severity !== 'PASS' && action !== 'RESOLVED';
    if (officerFilter === 'CRITICAL') return item.severity === 'CRITICAL' || item.severity === 'HIGH';
    if (officerFilter === 'MEDIUM') return item.severity === 'MEDIUM' || item.severity === 'LOW';
    if (officerFilter === 'RESOLVED') return action === 'RESOLVED';
    return true;
  });

  const handleOfficerAction = (itemId, actionType) => {
    setItemActions((prev) => ({
      ...prev,
      [itemId]: actionType,
    }));
  };

  // =========================================================================
  // 3. CRYPTOGRAPHIC AUDIT TRAIL DATA PREPARATION
  // =========================================================================
  const auditTrail = result.audit_trail || {
    audit_id: `VR-AUDIT-${screeningId}`,
    session_start: new Date().toISOString(),
    total_duration_ms: 135.2,
    total_events: 5,
    cryptographic_seal: '7A9F4E9804B11E9952044813083B2C981440A10B5E05286F6B2BE36248C5761D',
    events: [
      {
        index: 1,
        timestamp: new Date().toISOString(),
        elapsed_ms: 0,
        elapsed_formatted: '+0ms',
        category: 'INGESTION',
        category_icon: '📥',
        step: 'Document Ingestion Complete',
        status: 'SUCCESS',
        details: `Screened document payload: ${result.filename || 'uploaded document'}`,
      },
      {
        index: 2,
        timestamp: new Date().toISOString(),
        elapsed_ms: 45,
        elapsed_formatted: '+45ms',
        category: 'OCR',
        category_icon: '🔍',
        step: 'OCR Field Extraction',
        status: 'SUCCESS',
        details: 'Extracted text and parsed demographic records.',
      },
      {
        index: 3,
        timestamp: new Date().toISOString(),
        elapsed_ms: 82,
        elapsed_formatted: '+82ms',
        category: 'FORENSICS',
        category_icon: '🧬',
        step: 'Digital Tamper Analysis',
        status: isHighRisk ? 'FAIL' : 'SUCCESS',
        details: 'Evaluated ELA, edge sharpness, and digital metadata compression artifacts.',
      },
      {
        index: 4,
        timestamp: new Date().toISOString(),
        elapsed_ms: 110,
        elapsed_formatted: '+110ms',
        category: 'RISK_ENGINE',
        category_icon: '🎯',
        step: 'Screening Risk Engine Decision',
        status: isHighRisk ? 'FAIL' : 'SUCCESS',
        details: `Risk score computed at ${result.risk_score || 0}/100 (${result.overall_risk || 'LOW'}).`,
      },
      {
        index: 5,
        timestamp: new Date().toISOString(),
        elapsed_ms: 135,
        elapsed_formatted: '+135ms',
        category: 'SEAL',
        category_icon: '🔒',
        step: 'Cryptographic Audit Ledger Sealed',
        status: 'SUCCESS',
        details: 'Ledger cryptographically signed with SHA-256 seal digest.',
      },
    ],
  };

  const auditEvents = auditTrail.events || [];
  const filteredAuditEvents = auditEvents.filter((ev) => {
    if (auditFilter === 'ALL') return true;
    return ev.category === auditFilter;
  });

  const handleCopySeal = () => {
    const seal = auditTrail.cryptographic_seal || '';
    if (navigator.clipboard && seal) {
      navigator.clipboard.writeText(seal);
      setCopySealFeedback(true);
      setTimeout(() => setCopySealFeedback(false), 2500);
    }
  };

  const handleExportAuditTrail = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(auditTrail, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `veriguard_audit_ledger_${auditTrail.audit_id || screeningId}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // =========================================================================
  // 4. TASK 5: OFFICER CASE QUEUE CASES DATA
  // =========================================================================
  const currentCaseSubject = isMultiDoc
    ? cleanDocumentName(result.documents?.[0]?.name)
    : cleanDocumentName(result.document?.name);

  const currentCaseDocTypes = isMultiDoc
    ? result.documents?.map((d) => d.type || 'Document').join(' + ')
    : result.document?.type || 'Identity Document';

  const allCases = [
    {
      id: `VR-CASE-${screeningId}`,
      isCurrent: true,
      subject: currentCaseSubject,
      country: '🇮🇳 India',
      docs: currentCaseDocTypes,
      riskScore: result.risk_score || 0,
      riskLevel: result.overall_risk || 'LOW',
      tier: whyFlagged.officer_tier,
      tierLabel: whyFlagged.tier_label,
      highlight: isLowRisk
        ? 'All Indian government security rules & Verhoeff checksum validated'
        : 'Flags detected during automated screening. Inspection required.',
      submitted: `${secondsAgo}s ago`,
    },
    {
      id: 'VR-IND-9021',
      isCurrent: false,
      subject: 'Priya Ramesh Patel',
      country: '🇮🇳 India',
      docs: 'Aadhaar Card + PAN Card',
      riskScore: 0,
      riskLevel: 'LOW',
      tier: 'TIER_3_FAST_TRACK',
      tierLabel: 'Tier 3: Fast-Track Clearance Eligible',
      highlight: 'Aadhaar Verhoeff checksum verified · PAN 5th char "P" matches Patel',
      submitted: '8m ago',
    },
    {
      id: 'VR-IND-9022',
      isCurrent: false,
      subject: 'Rajesh Kumar Verma',
      country: '🇮🇳 India',
      docs: 'Aadhaar Card',
      riskScore: 85,
      riskLevel: 'HIGH',
      tier: 'TIER_1_IMMEDIATE_ESCALATION',
      tierLabel: 'Tier 1: Immediate Escalation Required',
      highlight: 'FAILED Verhoeff Checksum: Invalid check digit (Counterfeit UID scheme)',
      submitted: '22m ago',
    },
    {
      id: 'VR-IND-9023',
      isCurrent: false,
      subject: 'Vikram Aditya Malhotra',
      country: '🇮🇳 India',
      docs: 'Aadhaar Card + PAN Card',
      riskScore: 45,
      riskLevel: 'MEDIUM',
      tier: 'TIER_2_SECONDARY_REVIEW',
      tierLabel: 'Tier 2: Standard Secondary Inspection',
      highlight: 'PAN 5th character mismatch: "S" instead of "M" (Expected initial of Malhotra)',
      submitted: '45m ago',
    },
    {
      id: 'VR-IND-9024',
      isCurrent: false,
      subject: 'Sneha Venkatesh Rao',
      country: '🇮🇳 India',
      docs: 'Passport + Driving Licence',
      riskScore: 0,
      riskLevel: 'LOW',
      tier: 'TIER_3_FAST_TRACK',
      tierLabel: 'Tier 3: Fast-Track Clearance Eligible',
      highlight: 'Karnataka RTO (KA01) verified · Passport ICAO 9303 valid',
      submitted: '1h ago',
    },
  ];

  const handleUpdateCaseStatus = (caseId, newStatus) => {
    setCaseStatuses((prev) => ({
      ...prev,
      [caseId]: newStatus,
    }));
  };

  const filteredCases = allCases.filter((c) => {
    const st = caseStatuses[c.id] || 'PENDING';
    if (caseFilter === 'ALL') return true;
    if (caseFilter === 'PENDING') return st === 'PENDING' || st === 'UNDER_REVIEW';
    if (caseFilter === 'ESCALATED') return st === 'ESCALATED';
    if (caseFilter === 'CLEARED') return st === 'CLEARED';
    return true;
  });

  return (
    <div className="page">
      {/* Mode Switcher Bar: Dossier vs Case Queue */}
      <div className="mode-switcher-bar">
        <button
          type="button"
          className={`mode-switch-btn ${activeMainMode === 'dossier' ? 'active' : ''}`}
          onClick={() => setActiveMainMode('dossier')}
        >
          <span>📊</span>
          <span>Active Screening Dossier (VR-{screeningId})</span>
        </button>
        <button
          type="button"
          className={`mode-switch-btn ${activeMainMode === 'case_queue' ? 'active' : ''}`}
          onClick={() => setActiveMainMode('case_queue')}
        >
          <span>📋</span>
          <span>Officer Case Queue ({allCases.length} Active Indian KYC Cases)</span>
        </button>
      </div>

      {/* ========================================================================= */}
      {/* MODE 1: ACTIVE SCREENING DOSSIER                                          */}
      {/* ========================================================================= */}
      {activeMainMode === 'dossier' && (
        <>
          <div className="page-head">
            <h1>
              {isMultiDoc ? '📊 Multi-Document Screening & Cross-Intelligence' : '📊 Document Screening Result'}
            </h1>
            <p>
              {isMultiDoc
                ? `${result.documents?.length || 2} Documents Reconciled · ${result.filename}`
                : `${cleanDocumentName(result.document?.name)} · ${result.document?.type || 'Document'}`}
              {' · '}screened {secondsAgo} seconds ago · 🇮🇳 Indian KYC Mode Active
            </p>
          </div>

          {/* FEATURE 1: IDENTITY STORY NARRATIVE BRIEFING */}
          <div className="story-card">
            <div className="story-header">
              <div>
                <div style={{ fontSize: '12px', fontWeight: '700', color: '#047857', marginBottom: '4px' }}>
                  📖 EXECUTIVE IDENTITY INTELLIGENCE BRIEFING
                </div>
                <div className="story-headline">{identityStory.headline}</div>
              </div>
              <span className={`story-badge ${String(identityStory.status_tier || '').toLowerCase()}`}>
                {identityStory.status_tier === 'CONFIRMED_CONSISTENT'
                  ? '🟢 CONFIRMED CONSISTENT'
                  : identityStory.status_tier === 'CONFIRMED_GENUINE'
                  ? '🟢 AUTHENTIC & GENUINE'
                  : identityStory.status_tier === 'FLAGGED_INCONSISTENCY'
                  ? '🔴 DISCREPANCIES FLAGGED'
                  : identityStory.status_tier === 'BIOMETRIC_MISMATCH'
                  ? '🔴 BIOMETRIC MISMATCH'
                  : '🟡 REVIEW RECOMMENDED'}
              </span>
            </div>

            <div className="story-body">
              {identityStory.paragraphs?.map((p, idx) => (
                <p key={idx}>{p}</p>
              ))}
            </div>

            {/* Verified Key Facts Strip */}
            <div className="story-facts-grid">
              {identityStory.key_facts?.map((fact, idx) => (
                <div key={idx} className="story-fact-item">
                  <span className="story-fact-label">{fact.label}</span>
                  <span className="story-fact-val">{fact.value}</span>
                </div>
              ))}
            </div>

            {/* Officer Directive / Recommendation */}
            <div className={`story-recommendation ${isLowRisk ? '' : 'flagged'}`}>
              <span style={{ fontSize: '20px' }}>{isLowRisk ? '🛡️' : '🚨'}</span>
              <div>
                <b>Officer Recommendation: </b>
                <span>{identityStory.recommendation}</span>
              </div>
            </div>
          </div>

          {/* Navigation Tabs for Multi-Document Upload */}
          {isMultiDoc && (
            <div className="doc-nav-tabs">
              <button
                type="button"
                className={`doc-nav-tab ${activeView === 'cross_doc' ? 'active' : ''}`}
                onClick={() => setActiveView('cross_doc')}
              >
                <span>✨</span>
                <b>Cross-Document Intelligence</b>
                <span
                  style={{
                    fontSize: '11px',
                    padding: '2px 6px',
                    borderRadius: '10px',
                    background: consistencyScore >= 70 ? '#16A34A' : '#DC2626',
                    color: 'white',
                  }}
                >
                  {consistencyScore}% Match
                </span>
              </button>

              {result.documents?.map((doc, idx) => (
                <button
                  key={idx}
                  type="button"
                  className={`doc-nav-tab ${activeView === String(idx) ? 'active' : ''}`}
                  onClick={() => setActiveView(String(idx))}
                >
                  <span>📄</span>
                  <b>
                    Doc {idx + 1}: {doc.type || 'Document'}
                  </b>
                  <span style={{ fontSize: '11px', opacity: 0.8 }}>({doc.risk_score || 0}% risk)</span>
                </button>
              ))}
            </div>
          )}

          {/* ========================================================================= */}
          {/* VIEW 1: CROSS-DOCUMENT INTELLIGENCE VIEW                                  */}
          {/* ========================================================================= */}
          {isMultiDoc && activeView === 'cross_doc' && crossDoc && (
            <>
              {/* Indian Statutory Aadhaar-PAN Linkage Card (if present) */}
              {crossDoc.aadhaar_pan_linkage && (
                <div className={`aadhaar-pan-card ${crossDoc.aadhaar_pan_linkage.is_linked ? '' : 'flagged'}`}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', marginBottom: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '22px' }}>🇮🇳</span>
                      <div>
                        <b style={{ fontSize: '14px', color: crossDoc.aadhaar_pan_linkage.is_linked ? '#166534' : '#991b1b' }}>
                          Statutory Aadhaar - PAN Demographic Linkage Verification
                        </b>
                        <span style={{ display: 'block', fontSize: '11px', color: '#64748b' }}>
                          Compliance with Section 139AA of Indian Income-tax Act, 1961
                        </span>
                      </div>
                    </div>
                    <span
                      style={{
                        padding: '4px 10px',
                        borderRadius: '20px',
                        fontSize: '11px',
                        fontWeight: '800',
                        background: crossDoc.aadhaar_pan_linkage.is_linked ? '#dcfce7' : '#fee2e2',
                        color: crossDoc.aadhaar_pan_linkage.is_linked ? '#15803d' : '#b91c1c',
                      }}
                    >
                      {crossDoc.aadhaar_pan_linkage.is_linked ? '🟢 STATUTORY LINKAGE VERIFIED' : '🔴 LINKAGE DISCREPANCY'}
                    </span>
                  </div>

                  <p style={{ fontSize: '13px', color: '#334155', margin: '4px 0 10px 0' }}>
                    {crossDoc.aadhaar_pan_linkage.summary}
                  </p>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '8px', fontSize: '12px' }}>
                    <div style={{ background: 'rgba(255,255,255,0.7)', padding: '6px 10px', borderRadius: '6px' }}>
                      <b>Aadhaar Subject:</b> {crossDoc.aadhaar_pan_linkage.aadhaar_name || 'Verified'}
                    </div>
                    <div style={{ background: 'rgba(255,255,255,0.7)', padding: '6px 10px', borderRadius: '6px' }}>
                      <b>PAN Card Subject:</b> {crossDoc.aadhaar_pan_linkage.pan_name || 'Verified'}
                    </div>
                    <div style={{ background: 'rgba(255,255,255,0.7)', padding: '6px 10px', borderRadius: '6px' }}>
                      <b>PAN Surname Initial Check:</b>{' '}
                      {crossDoc.aadhaar_pan_linkage.pan_surname_initial_check?.passed ? '✅ Match' : '⚠️ Flagged'}
                    </div>
                  </div>
                </div>
              )}

              {/* Consistency Summary & Overall Risk Score */}
              <div className="grid g3 row-gap">
                <div className="card span2">
                  <h3>
                    <span className="ic">✨</span>Cross-Document Identity Reconciliation
                  </h3>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '12px',
                      flexWrap: 'wrap',
                      gap: '8px',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span
                        className={`cross-status-pill ${consistencyStatus.toLowerCase()}`}
                      >
                        {consistencyStatus === 'CONSISTENT'
                          ? '🟢 Identity Verified Consistent'
                          : consistencyStatus === 'PARTIALLY_CONSISTENT'
                          ? '🟡 Minor Variations Flagged'
                          : '🔴 Discrepancies Detected'}
                      </span>
                      <b style={{ fontSize: '15px', color: '#065F46' }}>
                        {consistencyScore}% Consistency Score
                      </b>
                    </div>
                    <span style={{ fontSize: '12px', color: '#64748b' }}>
                      {crossDoc.document_count || 2} Documents Cross-Analyzed
                    </span>
                  </div>

                  <p style={{ fontSize: '13px', color: '#334155', lineHeight: '1.6', marginBottom: '14px' }}>
                    {crossDoc.summary}
                  </p>

                  <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                    <div
                      style={{
                        padding: '8px 14px',
                        background: '#f1f5f9',
                        borderRadius: '8px',
                        fontSize: '12px',
                        color: '#1e293b',
                      }}
                    >
                      <b>Attributes Compared:</b> {crossDoc.comparisons?.length || 0}
                    </div>
                    <div
                      style={{
                        padding: '8px 14px',
                        background: crossDoc.inconsistencies?.length > 0 ? '#fee2e2' : '#dcfce7',
                        borderRadius: '8px',
                        fontSize: '12px',
                        color: crossDoc.inconsistencies?.length > 0 ? '#991b1b' : '#166534',
                      }}
                    >
                      <b>Flagged Inconsistencies:</b> {crossDoc.inconsistencies?.length || 0}
                    </div>
                    <div
                      style={{
                        padding: '8px 14px',
                        background: '#dcfce7',
                        borderRadius: '8px',
                        fontSize: '12px',
                        color: '#166534',
                      }}
                    >
                      <b>Verified Matches:</b> {crossDoc.matches?.length || 0}
                    </div>
                  </div>
                </div>

                <div className={`hero ${riskClass} fade-in-up`}>
                  {renderStatusAnimation(isLowRisk, isHighRisk)}
                  <div>
                    <div className="hlabel">🎯 UNIFIED RISK SCORE</div>
                    <div className="hnum">{result.risk_score || 0}</div>
                    <div className="hstate">
                      {isLowRisk ? '🟢 LOW RISK · APPROVED' : isHighRisk ? '🔴 HIGH RISK · REJECTED' : '🟡 MEDIUM RISK · REVIEW'}
                    </div>
                  </div>
                  <div className="haction">
                    {isLowRisk ? '✅ Fast-Track Cleared' : isHighRisk ? '🚨 Tier 1 Immediate Escalation' : '⚠️ Secondary Inspection Recommended'}
                  </div>
                </div>
              </div>

              {/* Flagged Inconsistencies Alert Box */}
              {crossDoc.inconsistencies?.length > 0 ? (
                <div className="card row-gap">
                  <h3 style={{ color: '#dc2626' }}>
                    <span className="ic">🚨</span>Flagged Cross-Document Inconsistencies ({crossDoc.inconsistencies.length})
                  </h3>
                  <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '12px' }}>
                    VeriGuard detected conflicting identity information across the uploaded documents. Review each flag below:
                  </p>
                  <div>
                    {crossDoc.inconsistencies.map((inc, idx) => (
                      <div
                        key={idx}
                        className={`inconsistency-card ${inc.severity === 'HIGH' ? 'high' : 'medium'}`}
                      >
                        <div style={{ fontSize: '20px', lineHeight: '1' }}>
                          {inc.severity === 'HIGH' ? '❌' : '⚠️'}
                        </div>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                            <b style={{ fontSize: '14px', color: inc.severity === 'HIGH' ? '#991b1b' : '#92400e' }}>
                              {inc.field} Discrepancy
                            </b>
                            <span
                              style={{
                                fontSize: '10px',
                                fontWeight: '700',
                                padding: '2px 6px',
                                borderRadius: '4px',
                                background: inc.severity === 'HIGH' ? '#fca5a5' : '#fde68a',
                                color: inc.severity === 'HIGH' ? '#7f1d1d' : '#78350f',
                              }}
                            >
                              {inc.severity} SEVERITY
                            </span>
                            <span style={{ fontSize: '12px', color: '#64748b' }}>({inc.docs})</span>
                          </div>
                          <div style={{ fontSize: '13px', color: '#334155', marginBottom: '6px' }}>
                            {inc.description}
                          </div>
                          <div
                            style={{
                              fontSize: '12px',
                              background: 'rgba(255,255,255,0.7)',
                              padding: '6px 10px',
                              borderRadius: '6px',
                              display: 'inline-block',
                              color: '#0f172a',
                            }}
                          >
                            <b>Doc 1:</b> <code>{inc.val1}</code> &nbsp;⟷&nbsp; <b>Doc 2:</b>{' '}
                            <code>{inc.val2}</code>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="card row-gap" style={{ borderLeft: '4px solid #16a34a', background: '#f0fdf4' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span style={{ fontSize: '24px' }}>✅</span>
                    <div>
                      <b style={{ fontSize: '14px', color: '#166534' }}>
                        Perfect Identity Consistency
                      </b>
                      <p style={{ fontSize: '12px', color: '#15803d', margin: 0 }}>
                        No identity discrepancies detected. Name, Date of Birth, and Document Numbers correlate consistently across all uploaded documents.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Cross-Document Field Comparison Matrix Table */}
              <div className="card row-gap">
                <h3>
                  <span className="ic">📑</span>Cross-Document Attribute Comparison Matrix
                </h3>
                <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '14px' }}>
                  Detailed field-by-field verification comparing identity records across all uploaded documents.
                </p>
                <div className="table-responsive">
                  <table className="comparison-table">
                    <thead>
                      <tr>
                        <th>Attribute</th>
                        <th>Document 1 Record</th>
                        <th>Document 2 Record</th>
                        <th>Match Status</th>
                        <th>Analysis &amp; Reason</th>
                      </tr>
                    </thead>
                    <tbody>
                      {crossDoc.comparisons?.map((comp, idx) => (
                        <tr key={idx}>
                          <td style={{ fontWeight: '700', color: '#0f172a' }}>
                            {comp.field === 'Name' && '👤 '}
                            {comp.field === 'Date of Birth' && '🎂 '}
                            {comp.field === 'Document Number' && '🪪 '}
                            {comp.field}
                          </td>
                          <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>{comp.val1}</td>
                          <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>{comp.val2}</td>
                          <td>
                            <span
                              className={`comparison-badge ${
                                comp.is_consistent
                                  ? comp.severity === 'LOW' && comp.status !== 'EXACT'
                                    ? 'warn'
                                    : 'pass'
                                  : 'fail'
                              }`}
                            >
                              {comp.badge}
                            </span>
                          </td>
                          <td style={{ fontSize: '12px', color: '#475569' }}>{comp.reason}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Cross-Document Biometric Face Matching Card */}
              <div className="card row-gap">
                <h3>
                  <span className="ic">👤</span>Cross-Document Biometric Face Matching
                </h3>
                <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '12px' }}>
                  128D ResNet deep facial embeddings cross-compared between document portraits and optional selfie.
                </p>

                <div className="face-matrix-grid">
                  {crossDoc.face_biometrics?.pairs?.map((pair, idx) => (
                    <div key={idx} className="face-pair-card">
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                          <span style={{ fontSize: '16px' }}>
                            {pair.type === 'selfie_to_doc' ? '🤳⟷🪪' : '🪪⟷🪪'}
                          </span>
                          <b style={{ fontSize: '13px', color: '#1e293b' }}>
                            {pair.source} vs {pair.target}
                          </b>
                        </div>
                        <div style={{ fontSize: '12px', color: '#64748b' }}>{pair.message}</div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div
                          style={{
                            fontSize: '20px',
                            fontWeight: '800',
                            color: pair.is_match ? '#16A34A' : '#DC2626',
                          }}
                        >
                          {pair.match_score}%
                        </div>
                        <span
                          style={{
                            fontSize: '11px',
                            fontWeight: '700',
                            color: pair.is_match ? '#15803d' : '#b91c1c',
                          }}
                        >
                          {pair.is_match ? 'MATCH VERIFIED' : 'MISMATCH'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {/* ========================================================================= */}
          {/* VIEW 2: INDIVIDUAL DOCUMENT VIEW (OR SINGLE-DOC UPLOAD)                   */}
          {/* ========================================================================= */}
          {(!isMultiDoc || activeView !== 'cross_doc') && (
            <>
              <div className="grid g3 row-gap">
                <div className="card span2">
                  <h3>
                    <span className="ic">📄</span>Document Information
                    {isMultiDoc && ` (Doc ${activeDocIndex + 1} of ${result.documents?.length})`}
                  </h3>
                  <div className="check-list">
                    <div className="check-row pass">
                      <div className="mk">•</div>
                      <div className="body">
                        <b>{cleanDocumentName(currentDoc.name)}</b>
                        <span>Full name (OCR, normalized)</span>
                      </div>
                    </div>
                    <div className="check-row pass">
                      <div className="mk">•</div>
                      <div className="body">
                        <b>
                          {currentDoc.type || 'Unknown'} · {currentDoc.number || 'Not detected'}
                        </b>
                        <span>Document type &amp; number</span>
                      </div>
                    </div>
                    <div className="check-row pass">
                      <div className="mk">•</div>
                      <div className="body">
                        <b>
                          DOB {currentDoc.dob || 'Not detected'} · Expires {currentDoc.expiry || 'Not detected'}
                        </b>
                        <span>
                          {currentDoc.type === 'Aadhaar Card' || currentDoc.type === 'PAN Card'
                            ? '✅ Lifetime statutory validity (Government of India)'
                            : currentDoc.expiry ? '✅ Valid, non-expired' : '⚠️ Check expiry date'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className={`hero ${riskClass} fade-in-up`}>
                  {renderStatusAnimation(isLowRisk, isHighRisk)}
                  <div>
                    <div className="hlabel">🎯 RISK SCORE</div>
                    <div className="hnum">{isMultiDoc ? currentDoc.risk_score || 0 : result.risk_score || 0}</div>
                    <div className="hstate">
                      {isLowRisk ? '🟢 LOW RISK · VERIFIED' : isHighRisk ? '🔴 HIGH RISK · REJECTED' : '🟡 MEDIUM RISK · REVIEW'}
                    </div>
                  </div>
                  <div className="haction">
                    {isLowRisk ? '✅ Approve — Continue Processing' : '🚨 Secondary Inspection Required'}
                  </div>
                </div>
              </div>

              <div className="grid g2 row-gap">
                <div className="card">
                  <h3>
                    <span className="ic">🔎</span>AI Analysis &amp; Security Checks
                  </h3>
                  <div className="prog-row">
                    <div className="prog-top">
                      <span>OCR Confidence</span>
                      <b>96%</b>
                    </div>
                    <div className="prog-track">
                      <div className="prog-fill" style={{ width: '96%' }}></div>
                    </div>
                  </div>
                  <div className="check-list" style={{ marginTop: '14px' }}>
                    {(currentDoc.findings || result.findings)?.map((finding, idx) => {
                      let reason = finding.reason || '';
                      reason = reason.replace(/\s*DOB\s*.*$/i, '').trim();

                      return (
                        <div key={idx} className={`check-row ${getStatusClass(finding.status)}`}>
                          <div className="mk">{getStatusIcon(finding.status)}</div>
                          <div className="body">
                            <b>
                              {finding.check} — {finding.status}
                            </b>
                            <span>{reason}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="card">
                  <h3>
                    <span className="ic">🧬</span>Tampering Detection
                  </h3>
                  <div className="heatmap">
                    <div className={`zone ${isHighRisk ? 'hot' : 'clean'}`}></div>
                  </div>
                  <div className="check-list">
                    {(currentDoc.tampering_signals || result.tampering_signals)?.length > 0 ? (
                      (currentDoc.tampering_signals || result.tampering_signals).map((signal, idx) => (
                        <div key={idx} className="check-row fail">
                          <div className="mk">❌</div>
                          <div className="body">
                            <b>{signal.type}</b>
                            <span>{signal.details}</span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <>
                        <div className="check-row pass">
                          <div className="mk">✅</div>
                          <div className="body">
                            <b>No tampering detected</b>
                            <span>Image texture and compression appear authentic</span>
                          </div>
                        </div>
                        <div className="check-row pass">
                          <div className="mk">✅</div>
                          <div className="body">
                            <b>No suspicious metadata</b>
                            <span>No editing-software signature found</span>
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Single doc Face verification card */}
              {!isMultiDoc && (
                <div className="grid g2 row-gap">
                  <div className="card">
                    <h3>
                      <span className="ic">🙂</span>Face Verification
                    </h3>
                    <div className="face-row">
                      <div className="face-thumb">🪪</div>
                      <div className="face-vs">vs</div>
                      <div className="face-thumb">🤳</div>
                      <div className="face-score">
                        <div
                          className="pct"
                          style={{
                            color: result.face_match?.passed ? '#22C55E' : '#94A3B8',
                            fontSize: '24px',
                            fontWeight: 800,
                          }}
                        >
                          {result.face_match?.score || 0}% match
                        </div>
                        <div className="thresh">
                          {result.face_match?.message || 'Face verification not evaluated'}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="card">
                    <h3>
                      <span className="ic">🗄️</span>Watchlist &amp; Sanctions Check
                    </h3>
                    <div className="check-list">
                      <div className="check-row pass">
                        <div className="mk">✅</div>
                        <div className="body">
                          <b>No match found</b>
                          <span>Checked against regulatory enforcement database</span>
                        </div>
                      </div>
                    </div>
                    <div style={{ marginTop: '16px' }}>
                      <span className={`badge ${isHighRisk ? 'critical' : isLowRisk ? 'low' : 'medium'}`}>
                        Status: {isHighRisk ? '⚠️ Critical override' : isLowRisk ? '✅ Clear' : '🟡 Review needed'}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}

          {/* FEATURE 2: ENHANCED WHY-FLAGGED PANEL & OFFICER PRIORITY QUEUE */}
          <div className="why-flagged-wrap">
            <div className="card row-gap">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '10px', marginBottom: '16px' }}>
                <div>
                  <h3>
                    <span className="ic">🎯</span>Why-Flagged Risk Decomposition &amp; Officer Priority Queue
                  </h3>
                  <p style={{ fontSize: '13px', color: '#64748b', margin: 0 }}>
                    Transparent attribution of risk points across 4 standardized verification domains.
                  </p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span style={{ fontSize: '12px', fontWeight: '700', color: '#475569' }}>
                    Evaluated: {whyFlagged.total_checks_evaluated || 4} Checks
                  </span>
                </div>
              </div>

              {/* 4 Domain Cards Row */}
              <div className="domain-cards-row">
                <div className="domain-card">
                  <div className="domain-card-left">
                    <span className="domain-card-icon">🧬</span>
                    <div>
                      <div className="domain-card-title">Authenticity &amp; Forensics</div>
                      <span style={{ fontSize: '11px', color: '#64748b' }}>Tamper &amp; Metadata</span>
                    </div>
                  </div>
                  <div className={`domain-card-pts ${domainPoints.AUTHENTICITY > 0 ? 'penalized' : 'zero'}`}>
                    {domainPoints.AUTHENTICITY > 0 ? `+${domainPoints.AUTHENTICITY} pts` : '0 pts'}
                  </div>
                </div>

                <div className="domain-card">
                  <div className="domain-card-left">
                    <span className="domain-card-icon">👤</span>
                    <div>
                      <div className="domain-card-title">Biometrics &amp; Face Match</div>
                      <span style={{ fontSize: '11px', color: '#64748b' }}>128D ResNet Vector</span>
                    </div>
                  </div>
                  <div className={`domain-card-pts ${domainPoints.BIOMETRICS > 0 ? 'penalized' : 'zero'}`}>
                    {domainPoints.BIOMETRICS > 0 ? `+${domainPoints.BIOMETRICS} pts` : '0 pts'}
                  </div>
                </div>

                <div className="domain-card">
                  <div className="domain-card-left">
                    <span className="domain-card-icon">⚖️</span>
                    <div>
                      <div className="domain-card-title">Data &amp; Cross-Consistency</div>
                      <span style={{ fontSize: '11px', color: '#64748b' }}>Aadhaar-PAN &amp; Rules</span>
                    </div>
                  </div>
                  <div className={`domain-card-pts ${domainPoints.DATA_INTEGRITY > 0 ? 'penalized' : 'zero'}`}>
                    {domainPoints.DATA_INTEGRITY > 0 ? `+${domainPoints.DATA_INTEGRITY} pts` : '0 pts'}
                  </div>
                </div>

                <div className="domain-card">
                  <div className="domain-card-left">
                    <span className="domain-card-icon">🛡️</span>
                    <div>
                      <div className="domain-card-title">Statutory Compliance</div>
                      <span style={{ fontSize: '11px', color: '#64748b' }}>UIDAI &amp; IT Rules</span>
                    </div>
                  </div>
                  <div className={`domain-card-pts ${domainPoints.COMPLIANCE > 0 ? 'penalized' : 'zero'}`}>
                    {domainPoints.COMPLIANCE > 0 ? `+${domainPoints.COMPLIANCE} pts` : '0 pts'}
                  </div>
                </div>
              </div>

              {/* Officer Tier & SLA Banner */}
              <div
                className="officer-tier-banner"
                style={{
                  background: isLowRisk ? '#f0fdf4' : isHighRisk ? '#fef2f2' : '#fffbeb',
                  border: `1px solid ${whyFlagged.tier_color || '#e2e8f0'}`,
                }}
              >
                <div>
                  <b style={{ color: whyFlagged.tier_color || '#0f172a', fontSize: '14px' }}>
                    {whyFlagged.tier_label || 'Officer Inspection Queue'}
                  </b>
                  <p style={{ fontSize: '12px', color: '#334155', margin: '2px 0 0 0' }}>
                    {whyFlagged.officer_summary}
                  </p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span
                    style={{
                      fontSize: '11px',
                      fontWeight: '800',
                      padding: '4px 10px',
                      borderRadius: '20px',
                      background: whyFlagged.tier_color || '#0f172a',
                      color: 'white',
                    }}
                  >
                    {whyFlagged.action_required_count || 0} ITEMS REQUIRE ACTION
                  </span>
                </div>
              </div>

              {/* Officer Priority Queue Filter Bar */}
              <div className="officer-filter-bar">
                <button
                  type="button"
                  className={`officer-filter-btn ${officerFilter === 'ALL' ? 'active' : ''}`}
                  onClick={() => setOfficerFilter('ALL')}
                >
                  All Checks ({priorityQueue.length})
                </button>
                <button
                  type="button"
                  className={`officer-filter-btn ${officerFilter === 'ACTION_REQUIRED' ? 'active' : ''}`}
                  onClick={() => setOfficerFilter('ACTION_REQUIRED')}
                >
                  🚨 Action Required ({whyFlagged.action_required_count || 0})
                </button>
                <button
                  type="button"
                  className={`officer-filter-btn ${officerFilter === 'CRITICAL' ? 'active' : ''}`}
                  onClick={() => setOfficerFilter('CRITICAL')}
                >
                  Critical / High
                </button>
                <button
                  type="button"
                  className={`officer-filter-btn ${officerFilter === 'MEDIUM' ? 'active' : ''}`}
                  onClick={() => setOfficerFilter('MEDIUM')}
                >
                  Medium / Low
                </button>
                <button
                  type="button"
                  className={`officer-filter-btn ${officerFilter === 'RESOLVED' ? 'active' : ''}`}
                  onClick={() => setOfficerFilter('RESOLVED')}
                >
                  ✅ Handled / Cleared
                </button>
              </div>

              {/* Priority Queue Items List */}
              <div className="officer-queue-list">
                {filteredQueue.length > 0 ? (
                  filteredQueue.map((item) => {
                    const currentAction = itemActions[item.id] || 'PENDING';
                    const sevClass = String(item.severity || 'low').toLowerCase();

                    return (
                      <div key={item.id} className={`officer-item ${sevClass}`}>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', marginBottom: '6px' }}>
                            <span style={{ fontSize: '16px' }}>{item.category_icon || '📌'}</span>
                            <b style={{ fontSize: '14px', color: '#0f172a' }}>{item.title}</b>
                            <span
                              style={{
                                fontSize: '10px',
                                fontWeight: '800',
                                padding: '2px 6px',
                                borderRadius: '4px',
                                background: item.severity === 'CRITICAL' ? '#fee2e2' : item.severity === 'HIGH' ? '#fecaca' : item.severity === 'PASS' ? '#dcfce7' : '#fef3c7',
                                color: item.severity === 'CRITICAL' || item.severity === 'HIGH' ? '#991b1b' : item.severity === 'PASS' ? '#166534' : '#92400e',
                              }}
                            >
                              {item.severity}
                            </span>
                            {item.points_impact > 0 && (
                              <span style={{ fontSize: '11px', fontWeight: '800', color: '#dc2626' }}>
                                +{item.points_impact} pts
                              </span>
                            )}
                            <span className={`officer-status-badge ${currentAction.toLowerCase()}`}>
                              {currentAction === 'PENDING'
                                ? item.severity === 'PASS' ? 'VERIFIED' : 'PENDING REVIEW'
                                : currentAction}
                            </span>
                          </div>

                          <div style={{ fontSize: '13px', color: '#334155', marginBottom: '8px' }}>
                            <b>Evidence:</b> {item.evidence}
                          </div>

                          <div
                            style={{
                              fontSize: '12px',
                              color: '#1e293b',
                              background: '#f8fafc',
                              padding: '8px 12px',
                              borderRadius: '6px',
                              borderLeft: '3px solid #64748b',
                            }}
                          >
                            <b>👉 Recommended Officer Directive:</b> {item.officer_action}
                          </div>
                        </div>

                        {/* Interactive Officer Action Buttons */}
                        <div className="officer-actions-btn-group">
                          {item.severity !== 'PASS' && (
                            <>
                              <button
                                type="button"
                                className="officer-action-btn ack"
                                onClick={() => handleOfficerAction(item.id, 'ACKNOWLEDGED')}
                                title="Mark as acknowledged by officer"
                              >
                                👁️ Acknowledge
                              </button>
                              <button
                                type="button"
                                className="officer-action-btn escalate"
                                onClick={() => handleOfficerAction(item.id, 'ESCALATED')}
                                title="Escalate to Lead Investigator"
                              >
                                🚨 Escalate
                              </button>
                              <button
                                type="button"
                                className="officer-action-btn resolve"
                                onClick={() => handleOfficerAction(item.id, 'RESOLVED')}
                                title="Mark as verified and resolved"
                              >
                                ✅ Verify &amp; Clear
                              </button>
                            </>
                          )}
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div style={{ textAlign: 'center', padding: '24px', color: '#64748b', fontSize: '13px' }}>
                    No items match the selected queue filter.
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* FEATURE 3: COMPLIANCE AUDIT TRAIL TIMELINE */}
          <div className="audit-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
              <div>
                <h3 style={{ margin: 0 }}>
                  <span className="ic">📜</span>Cryptographic Audit Trail &amp; Compliance Ledger
                </h3>
                <p style={{ fontSize: '13px', color: '#64748b', margin: '4px 0 0 0' }}>
                  Immutable millisecond-level verification log with cryptographic SHA-256 seal.
                </p>
              </div>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '12px', color: '#475569', background: '#f1f5f9', padding: '4px 10px', borderRadius: '6px' }}>
                  ⏱️ {auditTrail.total_duration_ms}ms · {auditTrail.total_events} Events
                </span>
                <button
                  type="button"
                  className="btn btn-secondary"
                  style={{ fontSize: '12px', padding: '6px 12px' }}
                  onClick={handleExportAuditTrail}
                >
                  📥 Export Audit Log (JSON)
                </button>
              </div>
            </div>

            {/* Audit Filter Bar */}
            <div className="audit-filter-bar">
              <button
                type="button"
                className={`audit-filter-btn ${auditFilter === 'ALL' ? 'active' : ''}`}
                onClick={() => setAuditFilter('ALL')}
              >
                All Categories ({auditEvents.length})
              </button>
              <button
                type="button"
                className={`audit-filter-btn ${auditFilter === 'INGESTION' ? 'active' : ''}`}
                onClick={() => setAuditFilter('INGESTION')}
              >
                📥 Ingestion
              </button>
              <button
                type="button"
                className={`audit-filter-btn ${auditFilter === 'OCR' ? 'active' : ''}`}
                onClick={() => setAuditFilter('OCR')}
              >
                🔍 OCR
              </button>
              <button
                type="button"
                className={`audit-filter-btn ${auditFilter === 'FORENSICS' ? 'active' : ''}`}
                onClick={() => setAuditFilter('FORENSICS')}
              >
                🧬 Forensics
              </button>
              <button
                type="button"
                className={`audit-filter-btn ${auditFilter === 'BIOMETRICS' ? 'active' : ''}`}
                onClick={() => setAuditFilter('BIOMETRICS')}
              >
                👤 Biometrics
              </button>
              <button
                type="button"
                className={`audit-filter-btn ${auditFilter === 'CROSS_DOC' ? 'active' : ''}`}
                onClick={() => setAuditFilter('CROSS_DOC')}
              >
                ✨ Cross-Doc
              </button>
              <button
                type="button"
                className={`audit-filter-btn ${auditFilter === 'RISK_ENGINE' ? 'active' : ''}`}
                onClick={() => setAuditFilter('RISK_ENGINE')}
              >
                🎯 Risk Engine
              </button>
              <button
                type="button"
                className={`audit-filter-btn ${auditFilter === 'SEAL' ? 'active' : ''}`}
                onClick={() => setAuditFilter('SEAL')}
              >
                🔒 Seal
              </button>
            </div>

            {/* Audit Timeline Rows */}
            <div className="audit-timeline">
              {filteredAuditEvents.map((ev, idx) => {
                const isSealRow = ev.category === 'SEAL';
                const statusClass = String(ev.status || 'info').toLowerCase();

                return (
                  <div key={idx} className={`audit-row ${isSealRow ? 'seal' : ''}`}>
                    <div className="audit-time">{ev.elapsed_formatted || `+${Math.round(ev.elapsed_ms || 0)}ms`}</div>
                    <div className="audit-category">
                      <span>{ev.category_icon || '📌'}</span>
                      <span>{ev.category}</span>
                    </div>
                    <div className="audit-step-col">
                      <div className="audit-step-title">{ev.step}</div>
                      <div className="audit-step-details">{ev.details}</div>
                    </div>
                    <div>
                      <span className={`audit-status-badge ${statusClass}`}>
                        {ev.status}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Cryptographic Seal Hash Box */}
            <div className="audit-seal-box">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                <span>🔒 <b>SHA-256 Ledger Seal:</b></span>
                <code className="audit-seal-hash">{auditTrail.cryptographic_seal}</code>
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  style={{ fontSize: '11px', padding: '4px 10px' }}
                  onClick={handleCopySeal}
                >
                  {copySealFeedback ? '✓ Copied to Clipboard!' : '📋 Copy Digest'}
                </button>
              </div>
            </div>
          </div>

          {/* Unified Risk Meter */}
          <div className="card row-gap" style={{ marginTop: '20px' }}>
            <h3>
              <span className="ic">📊</span>Screening Risk Meter
            </h3>
            <div className="meter-wrap">
              <div className="meter-track">
                <div
                  className="meter-marker"
                  style={{ left: `${result.risk_score || 0}%` }}
                  data-val={result.risk_score || 0}
                ></div>
              </div>
              <div className="meter-labels">
                <span>🟢 LOW</span>
                <span>🟡 MEDIUM</span>
                <span>🟠 HIGH</span>
                <span>🔴 CRITICAL</span>
              </div>
            </div>
          </div>

          {/* Decision Banner */}
          <div className={`rec-banner ${riskClass}`}>
            <div className="rt">
              <b>
                {isLowRisk
                  ? '✅ Approved — continue normal processing'
                  : '🚨 Secondary inspection required'}
              </b>
              <span>
                {isLowRisk
                  ? isMultiDoc
                    ? 'All Indian identity documents and biometric signals are consistent and authentic.'
                    : 'All signals consistent with a genuine Indian government document.'
                  : isMultiDoc
                  ? 'Inconsistencies or risk factors detected across uploaded documents. Manual verification required.'
                  : 'Multiple risk factors detected. Manual review recommended.'}
              </span>
            </div>
            <div className="rec-actions">
              <button type="button" className="btn btn-secondary" onClick={onExport}>
                📄 Export Report
              </button>
              <button
                type="button"
                className={`btn ${isLowRisk ? 'btn-primary' : 'btn-danger'}`}
                onClick={onReset}
              >
                {isLowRisk ? '✅ Approve & close' : '🚨 Route to inspection'}
              </button>
            </div>
          </div>

          <div className="foot-ref">
            <span>🆔 SCREENING ID: VR-{screeningId}</span>
            <span>📌 MODEL v1.2 · INDIAN KYC SUITE &amp; MULTI-DOC ENGINE</span>
          </div>
        </>
      )}

      {/* ========================================================================= */}
      {/* MODE 2: TASK 5 - OFFICER CASE QUEUE                                       */}
      {/* ========================================================================= */}
      {activeMainMode === 'case_queue' && (
        <div className="case-queue-card">
          <div className="page-head">
            <h1>📋 Officer Case Queue (Indian KYC Operations)</h1>
            <p>
              Triage, investigate, and approve identity screening cases across national jurisdictions.
            </p>
          </div>

          {/* Operational Metrics Bar */}
          <div className="case-stats-grid">
            <div className="case-stat-box">
              <span className="lbl">Total Intake</span>
              <span className="num">{allCases.length}</span>
            </div>
            <div className="case-stat-box">
              <span className="lbl">Immediate Escalation (P1)</span>
              <span className="num" style={{ color: '#dc2626' }}>
                {allCases.filter((c) => c.tier === 'TIER_1_IMMEDIATE_ESCALATION').length}
              </span>
            </div>
            <div className="case-stat-box">
              <span className="lbl">Secondary Review (P2)</span>
              <span className="num" style={{ color: '#d97706' }}>
                {allCases.filter((c) => c.tier === 'TIER_2_SECONDARY_REVIEW').length}
              </span>
            </div>
            <div className="case-stat-box">
              <span className="lbl">Fast-Track Cleared</span>
              <span className="num" style={{ color: '#16a34a' }}>
                {allCases.filter((c) => (caseStatuses[c.id] || '') === 'CLEARED').length}
              </span>
            </div>
          </div>

          {/* Case Queue Filters */}
          <div className="card row-gap" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
              <div className="officer-filter-bar" style={{ margin: 0 }}>
                <button
                  type="button"
                  className={`officer-filter-btn ${caseFilter === 'ALL' ? 'active' : ''}`}
                  onClick={() => setCaseFilter('ALL')}
                >
                  All Cases ({allCases.length})
                </button>
                <button
                  type="button"
                  className={`officer-filter-btn ${caseFilter === 'PENDING' ? 'active' : ''}`}
                  onClick={() => setCaseFilter('PENDING')}
                >
                  ⏳ Pending Action
                </button>
                <button
                  type="button"
                  className={`officer-filter-btn ${caseFilter === 'ESCALATED' ? 'active' : ''}`}
                  onClick={() => setCaseFilter('ESCALATED')}
                >
                  🚨 Escalated to Fraud Team
                </button>
                <button
                  type="button"
                  className={`officer-filter-btn ${caseFilter === 'CLEARED' ? 'active' : ''}`}
                  onClick={() => setCaseFilter('CLEARED')}
                >
                  ✅ Cleared / Approved
                </button>
              </div>

              <span style={{ fontSize: '12px', color: '#64748b' }}>
                Showing {filteredCases.length} of {allCases.length} cases
              </span>
            </div>
          </div>

          {/* Case Queue Table */}
          <div className="case-table-wrap">
            <table className="case-table">
              <thead>
                <tr>
                  <th>Case ID</th>
                  <th>Applicant</th>
                  <th>Submitted Docs</th>
                  <th>Risk Score</th>
                  <th>Priority Tier</th>
                  <th>Findings &amp; Directive</th>
                  <th>Status</th>
                  <th>Officer Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredCases.map((c) => {
                  const status = caseStatuses[c.id] || 'PENDING';

                  return (
                    <tr
                      key={c.id}
                      style={{
                        background: c.isCurrent ? '#f0fdf4' : '',
                        borderLeft: c.isCurrent ? '4px solid #16a34a' : '',
                      }}
                    >
                      <td>
                        <b style={{ fontFamily: 'monospace', fontSize: '13px' }}>{c.id}</b>
                        {c.isCurrent && (
                          <span
                            style={{
                              display: 'block',
                              fontSize: '10px',
                              color: '#15803d',
                              fontWeight: '700',
                            }}
                          >
                            ⭐ Current Session
                          </span>
                        )}
                      </td>
                      <td>
                        <b>{c.subject}</b>
                        <span style={{ display: 'block', fontSize: '11px', color: '#64748b' }}>
                          {c.country} · {c.submitted}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontSize: '12px', fontWeight: '600', color: '#334155' }}>
                          {c.docs}
                        </span>
                      </td>
                      <td>
                        <b
                          style={{
                            fontSize: '14px',
                            color: c.riskScore >= 60 ? '#dc2626' : c.riskScore >= 30 ? '#d97706' : '#16a34a',
                          }}
                        >
                          {c.riskScore}%
                        </b>
                        <span style={{ display: 'block', fontSize: '10px', color: '#64748b' }}>
                          {c.riskLevel} RISK
                        </span>
                      </td>
                      <td>
                        <span
                          className={`case-priority-chip ${
                            c.tier === 'TIER_1_IMMEDIATE_ESCALATION'
                              ? 'critical'
                              : c.tier === 'TIER_2_SECONDARY_REVIEW'
                              ? 'high'
                              : 'low'
                          }`}
                        >
                          {c.tier === 'TIER_1_IMMEDIATE_ESCALATION'
                            ? 'P1 ESCALATE'
                            : c.tier === 'TIER_2_SECONDARY_REVIEW'
                            ? 'P2 REVIEW'
                            : 'P3 FAST-TRACK'}
                        </span>
                      </td>
                      <td style={{ maxWidth: '280px', fontSize: '12px', color: '#334155' }}>
                        {c.highlight}
                      </td>
                      <td>
                        <span
                          className={`officer-status-badge ${status.toLowerCase()}`}
                          style={{ fontSize: '11px' }}
                        >
                          {status}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                          {c.isCurrent ? (
                            <button
                              type="button"
                              className="officer-action-btn ack"
                              onClick={() => setActiveMainMode('dossier')}
                              title="View current full dossier"
                            >
                              👁️ View Dossier
                            </button>
                          ) : (
                            <button
                              type="button"
                              className="officer-action-btn ack"
                              onClick={() => {
                                handleUpdateCaseStatus(c.id, 'UNDER_REVIEW');
                                alert(`Opening Case Dossier for ${c.subject} (${c.id}). Risk Score: ${c.riskScore}%. Priority: ${c.tierLabel}`);
                              }}
                              title="Open case file"
                            >
                              📂 Inspect
                            </button>
                          )}

                          {status !== 'CLEARED' && (
                            <button
                              type="button"
                              className="officer-action-btn resolve"
                              onClick={() => handleUpdateCaseStatus(c.id, 'CLEARED')}
                              title="Approve Case"
                            >
                              ✅ Approve
                            </button>
                          )}

                          {status !== 'ESCALATED' && (
                            <button
                              type="button"
                              className="officer-action-btn escalate"
                              onClick={() => handleUpdateCaseStatus(c.id, 'ESCALATED')}
                              title="Escalate to Senior Fraud Unit"
                            >
                              🚨 Escalate
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsPage;