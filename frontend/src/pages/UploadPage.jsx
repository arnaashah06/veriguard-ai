// src/pages/UploadPage.jsx
import { useState, useRef } from 'react';
import { checkImageQuality } from '../utils/imageQuality';

const UploadPage = ({ onUpload }) => {
  const [documentFiles, setDocumentFiles] = useState([]);
  const [selfieFile, setSelfieFile] = useState(null);
  const [error, setError] = useState(null);
  const [warnings, setWarnings] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [loadingScenario, setLoadingScenario] = useState(null);
  const documentInputRef = useRef(null);
  const addMoreInputRef = useRef(null);
  const selfieInputRef = useRef(null);

  const fetchAsFile = async (url, filename, mimeType) => {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Could not load demo asset: ${filename}`);
    const blob = await res.blob();
    return new File([blob], filename, { type: mimeType });
  };

  const loadDemoScenario = async (scenarioId) => {
    setError(null);
    setWarnings([]);
    setLoadingScenario(scenarioId);

    try {
      if (scenarioId === 'clean') {
        const [aadhaar, pan, selfie] = await Promise.all([
          fetchAsFile('/demo_assets/demo_aadhaar_clean.png', 'aadhaar_rahul_sharma.png', 'image/png'),
          fetchAsFile('/demo_assets/demo_pan_clean.png', 'pan_rahul_sharma.png', 'image/png'),
          fetchAsFile('/demo_assets/demo_selfie_match.jpg', 'selfie_rahul_sharma.jpg', 'image/jpeg'),
        ]);
        setDocumentFiles([aadhaar, pan]);
        setSelfieFile(selfie);
        onUpload([aadhaar, pan], selfie);
      } else if (scenarioId === 'counterfeit') {
        const aadhaar = await fetchAsFile(
          '/demo_assets/demo_aadhaar_counterfeit.png',
          'aadhaar_forged_uid.png',
          'image/png'
        );
        setDocumentFiles([aadhaar]);
        setSelfieFile(null);
        onUpload([aadhaar], null);
      } else if (scenarioId === 'conflict') {
        const [aadhaar, pan, selfie] = await Promise.all([
          fetchAsFile('/demo_assets/demo_aadhaar_person_a.png', 'aadhaar_rajesh_kumar.png', 'image/png'),
          fetchAsFile('/demo_assets/demo_pan_person_b.png', 'pan_vikram_singh.png', 'image/png'),
          fetchAsFile('/demo_assets/demo_selfie_imposter.jpg', 'selfie_imposter_mismatch.jpg', 'image/jpeg'),
        ]);
        setDocumentFiles([aadhaar, pan]);
        setSelfieFile(selfie);
        onUpload([aadhaar, pan], selfie);
      }
    } catch (err) {
      setError(`Failed to load demo scenario: ${err.message}`);
    } finally {
      setLoadingScenario(null);
    }
  };

  const validateFile = (file) => {
    if (!file) return 'No file selected';
    if (file.size > 10 * 1024 * 1024) return `File "${file.name}" exceeds 10MB limit`;
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
      return `File "${file.name}" has unsupported format. Please use JPG or PNG.`;
    }
    return null;
  };

  const processIncomingFiles = async (newFiles) => {
    setError(null);
    setWarnings([]);

    if (!newFiles || newFiles.length === 0) return;

    const validNewFiles = [];
    const collectedWarnings = [];

    setIsAnalyzing(true);

    for (const file of newFiles) {
      const valError = validateFile(file);
      if (valError) {
        setIsAnalyzing(false);
        setError(valError);
        return;
      }

      // Check duplicates by filename & size
      const isDuplicate = documentFiles.some(
        (existing) => existing.name === file.name && existing.size === file.size
      );
      if (isDuplicate) {
        continue;
      }

      try {
        const qualityResult = await checkImageQuality(file);
        if (!qualityResult.passed && qualityResult.warnings?.length > 0) {
          collectedWarnings.push(`${file.name}: ${qualityResult.warnings.join(', ')}`);
        }
      } catch {
        // Quality check fallback
      }

      validNewFiles.push(file);
    }

    setIsAnalyzing(false);

    if (collectedWarnings.length > 0) {
      setWarnings(collectedWarnings);
    }

    if (validNewFiles.length > 0) {
      setDocumentFiles((prev) => [...prev, ...validNewFiles]);
    }
  };

  const handleDocumentSelect = async (e) => {
    const files = Array.from(e.target.files || []);
    await processIncomingFiles(files);
    e.target.value = '';
  };

  const handleRemoveDocument = (indexToRemove) => {
    setDocumentFiles((prev) => prev.filter((_, idx) => idx !== indexToRemove));
  };

  const handleSelfieSelect = async (e) => {
    setError(null);
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    const valError = validateFile(selectedFile);
    if (valError) {
      setError(valError);
      return;
    }

    setIsAnalyzing(true);
    try {
      const qualityResult = await checkImageQuality(selectedFile);
      setIsAnalyzing(false);
      if (!qualityResult.passed && qualityResult.warnings?.length > 0) {
        setWarnings(qualityResult.warnings);
      }
      setSelfieFile(selectedFile);
    } catch {
      setIsAnalyzing(false);
      setSelfieFile(selectedFile);
    }
    e.target.value = '';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files || []);
    await processIncomingFiles(droppedFiles);
  };

  const handleSubmit = () => {
    if (documentFiles.length > 0) {
      onUpload(documentFiles, selfieFile);
    }
  };

  return (
    <div className="upload-wrap">
      <div className="upload-card">
        <div className="shield">🇮🇳</div>
        <h2>Upload Indian Identity Documents</h2>
        <p>
          Upload 1 or more Indian government-approved documents (Aadhaar, PAN, Voter ID, Driving Licence, Passport) for automated OCR, Verhoeff checksum &amp; fraud analysis, and cross-document reconciliation.
        </p>

        {/* Quick Demo Showcase */}
        <div className="demo-showcase-bar">
          <div className="demo-showcase-header">
            <div>
              <div className="demo-showcase-title">
                <span>⚡</span> Preloaded Test Scenarios (1-Click Verification)
              </div>
              <div className="demo-showcase-subtitle">
                Select a real-world scenario to test VeriGuard&apos;s forensic OCR, UIDAI dihedral checksums, and cross-doc linkage
              </div>
            </div>
            {loadingScenario && (
              <span style={{ fontSize: '12px', color: '#38bdf8', fontFamily: 'monospace' }}>
                ⏳ Launching {loadingScenario}...
              </span>
            )}
          </div>

          <div className="demo-cards-grid">
            {/* Scenario 1: Clean KYC */}
            <div
              className="demo-scenario-card clean"
              onClick={() => !loadingScenario && loadDemoScenario('clean')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && !loadingScenario && loadDemoScenario('clean')}
            >
              <div>
                <span className="demo-tag clean">🟢 Genuine · Risk 0</span>
                <div className="demo-card-title">1. Clean Indian KYC Approval</div>
                <div className="demo-card-desc">
                  Rahul K. Sharma · Valid Aadhaar &amp; PAN card with matching selfie. Confirms Sec 139AA statutory linkage &amp; fast-tracks approval.
                </div>
              </div>
              <button
                type="button"
                className="demo-btn"
                disabled={loadingScenario !== null}
                onClick={(e) => {
                  e.stopPropagation();
                  loadDemoScenario('clean');
                }}
              >
                {loadingScenario === 'clean' ? '⏳ Launching...' : '⚡ Test Clean Flow →'}
              </button>
            </div>

            {/* Scenario 2: Counterfeit UID */}
            <div
              className="demo-scenario-card fake"
              onClick={() => !loadingScenario && loadDemoScenario('counterfeit')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && !loadingScenario && loadDemoScenario('counterfeit')}
            >
              <div>
                <span className="demo-tag fake">🔴 Forgery · Checksum Fail</span>
                <div className="demo-card-title">2. Counterfeit Aadhaar Alert</div>
                <div className="demo-card-desc">
                  Tampered 12-digit UID failing UIDAI Dihedral D5 Verhoeff checksum. Triggers instant Tier-1 fraud escalation.
                </div>
              </div>
              <button
                type="button"
                className="demo-btn"
                disabled={loadingScenario !== null}
                onClick={(e) => {
                  e.stopPropagation();
                  loadDemoScenario('counterfeit');
                }}
              >
                {loadingScenario === 'counterfeit' ? '⏳ Launching...' : '⚡ Test Counterfeit →'}
              </button>
            </div>

            {/* Scenario 3: Identity Conflict */}
            <div
              className="demo-scenario-card conflict"
              onClick={() => !loadingScenario && loadDemoScenario('conflict')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && !loadingScenario && loadDemoScenario('conflict')}
            >
              <div>
                <span className="demo-tag conflict">⚠️ Conflict · Risk 95</span>
                <div className="demo-card-title">3. Identity Conflict &amp; Imposter</div>
                <div className="demo-card-desc">
                  Rajesh Kumar (Aadhaar) paired with Vikram Singh (PAN) + Imposter Selfie. Detects demographic collision &amp; face mismatch.
                </div>
              </div>
              <button
                type="button"
                className="demo-btn"
                disabled={loadingScenario !== null}
                onClick={(e) => {
                  e.stopPropagation();
                  loadDemoScenario('conflict');
                }}
              >
                {loadingScenario === 'conflict' ? '⏳ Launching...' : '⚡ Test Conflict Flow →'}
              </button>
            </div>
          </div>
        </div>

        {/* Dropzone */}
        <div
          className={`dropzone ${isDragging ? 'active' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => documentInputRef.current?.click()}
          style={{
            borderColor: isDragging ? '#16A34A' : '',
            background: isDragging ? '#DCFCE7' : '',
            cursor: 'pointer',
          }}
        >
          <div className="dz-ic">{isDragging ? '📥' : '📄'}</div>
          <b>
            {isDragging
              ? 'Drop documents here'
              : documentFiles.length > 0
              ? 'Add more documents or drop here'
              : 'Drag and drop 1 or more documents here'}
          </b>
          <span>Supports multiple files (Passport, Aadhaar, PAN, Driving License)</span>
          <div style={{ marginTop: '8px' }}>
            <button
              className="btn btn-primary"
              onClick={(e) => {
                e.stopPropagation();
                documentInputRef.current?.click();
              }}
              type="button"
            >
              Browse Documents
            </button>
          </div>
          <input
            ref={documentInputRef}
            type="file"
            multiple
            accept=".jpg,.jpeg,.png"
            onChange={handleDocumentSelect}
            style={{ display: 'none' }}
          />
          <input
            ref={addMoreInputRef}
            type="file"
            multiple
            accept=".jpg,.jpeg,.png"
            onChange={handleDocumentSelect}
            style={{ display: 'none' }}
          />
        </div>

        {/* Document List / Queue */}
        {documentFiles.length > 0 && (
          <div style={{ marginTop: '16px', textAlign: 'left' }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '8px',
              }}
            >
              <span style={{ fontSize: '13px', fontWeight: '700', color: '#1e293b' }}>
                📁 Uploaded Documents ({documentFiles.length})
              </span>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => addMoreInputRef.current?.click()}
                style={{ fontSize: '12px', padding: '4px 10px', height: 'auto' }}
              >
                + Add Another Document
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {documentFiles.map((doc, idx) => (
                <div
                  key={`${doc.name}-${doc.size}-${idx}`}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '8px 12px',
                    background: '#f8fafc',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    fontSize: '13px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
                    <span
                      style={{
                        background: '#065F46',
                        color: 'white',
                        fontSize: '11px',
                        fontWeight: '700',
                        padding: '2px 6px',
                        borderRadius: '4px',
                      }}
                    >
                      Doc {idx + 1}
                    </span>
                    <span
                      style={{
                        fontWeight: '600',
                        color: '#0f172a',
                        textOverflow: 'ellipsis',
                        overflow: 'hidden',
                        whiteSpace: 'nowrap',
                        maxWidth: '220px',
                      }}
                      title={doc.name}
                    >
                      {doc.name}
                    </span>
                    <span style={{ color: '#64748b', fontSize: '12px' }}>
                      ({(doc.size / 1024 / 1024).toFixed(2)} MB)
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemoveDocument(idx)}
                    title="Remove document"
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#ef4444',
                      fontWeight: 'bold',
                      cursor: 'pointer',
                      fontSize: '16px',
                      padding: '2px 6px',
                      lineHeight: '1',
                    }}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>

            {/* Multi-Document Intelligence Indicator */}
            {documentFiles.length >= 2 && (
              <div
                style={{
                  marginTop: '12px',
                  padding: '10px 14px',
                  background: '#ECFDF5',
                  border: '1px solid #10B981',
                  borderRadius: '8px',
                  fontSize: '12px',
                  color: '#065F46',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <span style={{ fontSize: '18px' }}>✨</span>
                <div>
                  <b>Cross-Document Intelligence Active:</b> VeriGuard will cross-compare Name, DOB, Document Numbers, and biometrically reconcile facial portraits across all {documentFiles.length} documents.
                </div>
              </div>
            )}
          </div>
        )}

        {/* Selfie Upload */}
        <div style={{ marginTop: '16px' }}>
          <p style={{ fontSize: '13px', fontWeight: '600', marginBottom: '8px', textAlign: 'left' }}>
            📸 Upload a selfie{' '}
            <span style={{ fontWeight: '400', color: '#64748b' }}>
              (optional - for facial biometric cross-matching)
            </span>
          </p>
          <div
            className="dropzone"
            onClick={() => selfieInputRef.current?.click()}
            style={{
              padding: '18px',
              cursor: 'pointer',
              background: selfieFile ? '#DCFCE7' : '#f8fafc',
            }}
          >
            <div className="dz-ic">🤳</div>
            <span>{selfieFile ? `✓ Selfie uploaded: ${selfieFile.name}` : 'Click to upload a selfie'}</span>
            <div style={{ marginTop: '6px' }}>
              <button
                className="btn btn-secondary"
                onClick={(e) => {
                  e.stopPropagation();
                  selfieInputRef.current?.click();
                }}
                type="button"
                style={{ fontSize: '12px', padding: '5px 12px' }}
              >
                {selfieFile ? 'Change Selfie' : 'Upload Selfie'}
              </button>
            </div>
            <input
              ref={selfieInputRef}
              type="file"
              accept=".jpg,.jpeg,.png"
              onChange={handleSelfieSelect}
              style={{ display: 'none' }}
            />
          </div>
        </div>

        {isAnalyzing && (
          <div style={{ marginTop: '12px', fontSize: '13px', color: '#64748B' }}>
            🔍 Analyzing image quality...
          </div>
        )}

        {warnings.length > 0 && (
          <div
            style={{
              marginTop: '12px',
              padding: '12px 16px',
              background: '#FEF9C3',
              borderRadius: '8px',
              border: '1px solid #EAB308',
              textAlign: 'left',
            }}
          >
            <div style={{ fontWeight: '600', fontSize: '13px', color: '#A16207', marginBottom: '6px' }}>
              ⚠️ Quality Warnings
            </div>
            {warnings.map((warning, idx) => (
              <div key={idx} style={{ fontSize: '12px', color: '#92400E', marginTop: '4px' }}>
                • {warning}
              </div>
            ))}
          </div>
        )}

        {error && (
          <div style={{ marginTop: '12px', fontSize: '13px', color: '#EF4444', textAlign: 'left' }}>
            ❌ {error}
          </div>
        )}

        {documentFiles.length > 0 && !isAnalyzing && (
          <div style={{ marginTop: '18px' }}>
            <button
              className="btn btn-primary"
              onClick={handleSubmit}
              style={{ width: '100%', padding: '12px', fontSize: '15px' }}
            >
              {documentFiles.length === 1
                ? `Verify Document ${selfieFile ? '✅ with Face Verification' : ''} →`
                : `Verify ${documentFiles.length} Documents & Cross-Check Identity ${selfieFile ? '✅ with Biometrics' : ''} →`}
            </button>
          </div>
        )}

        <div className="fmt-row">
          <span className="fmt-chip">JPG</span>
          <span className="fmt-chip">JPEG</span>
          <span className="fmt-chip">PNG</span>
          <span className="fmt-chip">MULTI-DOC</span>
          <span className="fmt-chip">MAX 10MB</span>
        </div>

        <div style={{ marginTop: '14px', display: 'flex', gap: '6px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <span className="fmt-chip" style={{ background: '#ecfdf5', color: '#065f46', border: '1px solid #a7f3d0' }}>🇮🇳 Aadhaar (UIDAI)</span>
          <span className="fmt-chip" style={{ background: '#eff6ff', color: '#1e40af', border: '1px solid #bfdbfe' }}>🇮🇳 PAN Card</span>
          <span className="fmt-chip" style={{ background: '#fef3c7', color: '#92400e', border: '1px solid #fde68a' }}>🇮🇳 Voter ID (EPIC)</span>
          <span className="fmt-chip" style={{ background: '#f5f3ff', color: '#5b21b6', border: '1px solid #ddd6fe' }}>🇮🇳 Driving Licence</span>
          <span className="fmt-chip" style={{ background: '#fdf2f8', color: '#9d174d', border: '1px solid #fbcfe8' }}>🇮🇳 Passport</span>
        </div>
        <div className="privacy-note">
          🔒 Sensitive fields are masked in logs · deleted per retention policy
        </div>
      </div>
    </div>
  );
};

export default UploadPage;