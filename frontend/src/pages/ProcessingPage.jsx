// src/pages/ProcessingPage.jsx
import { useEffect, useState } from 'react';

const STAGES = [
  { id: 1, title: 'Cryptographic Ingestion', desc: 'SHA-256 hashing & metadata extraction', icon: '📡' },
  { id: 2, title: 'Tesseract Multi-Pass OCR', desc: 'Full-text extraction & layout analysis', icon: '🔍' },
  { id: 3, title: 'Indian Credential Authenticator', desc: 'UIDAI Verhoeff D5 & PAN syntax validation', icon: '🇮🇳' },
  { id: 4, title: '128D ResNet Biometrics', desc: 'Facial landmark vector encoding & comparison', icon: '👤' },
  { id: 5, title: 'Section 139AA Reconciliation', desc: 'Statutory cross-document demographic linkage', icon: '🔗' },
  { id: 6, title: 'Multi-Factor Risk Engine', desc: 'Decomposing risk signals & sealing audit trail', icon: '🛡️' }
];

const ProcessingPage = () => {
  const [activeStage, setActiveStage] = useState(1);
  const [progress, setProgress] = useState(15);
  const [hudMessage, setHudMessage] = useState('CALIBRATING SPECTRAL IMAGING SENSORS...');

  useEffect(() => {
    const stageInterval = setInterval(() => {
      setActiveStage((prev) => {
        if (prev < STAGES.length) {
          return prev + 1;
        }
        return prev;
      });
    }, 700);

    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev < 95) {
          const inc = Math.floor(Math.random() * 8) + 4;
          return Math.min(prev + inc, 95);
        }
        return prev;
      });
    }, 250);

    const hudMessages = [
      'INITIALIZING HIGH-RESOLUTION OPTICAL SCANNER...',
      'RUNNING MULTI-PASS PSM 3/6 TEXT RECOGNITION...',
      'COMPUTING DIHEDRAL D5 VERHOEFF CHECKSUM...',
      'EXTRACTING 128-DIMENSIONAL DEEP FACIAL EMBEDDINGS...',
      'RECONCILING SECTION 139AA AADHAAR-PAN LINKAGE...',
      'COMPILING EVIDENCE DOSSIER & SHA-256 AUDIT LOG...'
    ];

    const hudInterval = setInterval(() => {
      setHudMessage((prev) => {
        const nextIdx = (hudMessages.indexOf(prev) + 1) % hudMessages.length;
        return hudMessages[nextIdx];
      });
    }, 900);

    return () => {
      clearInterval(stageInterval);
      clearInterval(progressInterval);
      clearInterval(hudInterval);
    };
  }, []);

  return (
    <div className="proc-wrap">
      <div className="proc-card proc-card-modern">
        {/* Hologram Scanner HUD */}
        <div className="hud-scanner-container">
          <div className="hud-corner hud-top-left"></div>
          <div className="hud-corner hud-top-right"></div>
          <div className="hud-corner hud-bottom-left"></div>
          <div className="hud-corner hud-bottom-right"></div>

          <div className="hud-document-frame">
            <div className="hud-laser-beam"></div>
            <div className="hud-grid-overlay"></div>
            <div className="hud-card-silhouette">
              <div className="hud-silhouette-portrait"></div>
              <div className="hud-silhouette-lines">
                <div className="hud-line"></div>
                <div className="hud-line"></div>
                <div className="hud-line short"></div>
              </div>
            </div>
          </div>

          <div className="hud-status-strip">
            <span className="hud-live-indicator">
              <span className="hud-pulse-dot"></span> SCANNER ACTIVE
            </span>
            <span className="hud-metric">RESOLUTION: 300 DPI</span>
            <span className="hud-metric">SECURITY LEVEL: TIER 1</span>
          </div>
        </div>

        {/* Header & Percentage */}
        <div className="proc-header-row">
          <div>
            <div className="proc-title">Identity Verification in Progress</div>
            <div className="proc-sub">{hudMessage}</div>
          </div>
          <div className="proc-percent-badge">{progress}%</div>
        </div>

        {/* Progress Bar */}
        <div className="proc-progress-track">
          <div className="proc-progress-bar" style={{ width: `${progress}%` }}></div>
        </div>

        {/* Dynamic Multi-Stage Timeline */}
        <div className="proc-stages-grid">
          {STAGES.map((stage) => {
            const isDone = stage.id < activeStage;
            const isActive = stage.id === activeStage;

            return (
              <div
                key={stage.id}
                className={`stage-card ${isDone ? 'done' : isActive ? 'active' : 'pending'}`}
              >
                <div className="stage-icon-wrap">
                  {isDone ? (
                    <span className="stage-status-check">✓</span>
                  ) : isActive ? (
                    <span className="stage-spinner"></span>
                  ) : (
                    <span className="stage-icon">{stage.icon}</span>
                  )}
                </div>
                <div className="stage-content">
                  <div className="stage-title">
                    {stage.title}
                    {isActive && <span className="stage-badge-live">RUNNING</span>}
                  </div>
                  <div className="stage-desc">{stage.desc}</div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer Security Seal */}
        <div className="proc-security-footer">
          <span>🔒 256-Bit Hardware Accelerated Cryptographic Screening</span>
          <span>Compliance: UIDAI · Income Tax Act §139AA · ICAO 9303</span>
        </div>
      </div>
    </div>
  );
};

export default ProcessingPage;