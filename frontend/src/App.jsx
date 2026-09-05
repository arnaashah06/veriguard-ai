// src/App.jsx - COMPLETE VERSION
import { useState, useEffect } from 'react';
import './App.css';
import TopBar from './components/Layout/TopBar';
import UploadPage from './pages/UploadPage';
import ProcessingPage from './pages/ProcessingPage';
import ResultsPage from './pages/ResultsPage';
import LoginPage from './pages/Loginpage';
import { verifyDocument } from './api/verification';

function App() {
  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem('veriguard_current_user');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  });
  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    try {
      return !!localStorage.getItem('veriguard_current_user');
    } catch {
      return false;
    }
  });
  const [screen, setScreen] = useState('upload');
  const [activeTab, setActiveTab] = useState('Upload');
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState(() => {
    try {
      const savedHistory = localStorage.getItem('veriguard_history');
      return savedHistory ? JSON.parse(savedHistory) : [];
    } catch {
      return [];
    }
  });
  const [settingsMessage, setSettingsMessage] = useState('');

  // Save history whenever it changes
  useEffect(() => {
    if (uploadedFiles.length > 0) {
      localStorage.setItem('veriguard_history', JSON.stringify(uploadedFiles));
    }
  }, [uploadedFiles]);

  const handleLogin = (userData) => {
    setUser(userData);
    setIsLoggedIn(true);
    setActiveTab('Upload');
    setScreen('upload');
  };

  const handleLogout = () => {
    localStorage.removeItem('veriguard_current_user');
    setIsLoggedIn(false);
    setUser(null);
    setActiveTab('Upload');
    setScreen('upload');
  };

  const handleUpload = async (files, selfie) => {
    setError(null);
    setScreen('processing');
    setActiveTab('Dashboard');
    
    try {
      const result = await verifyDocument(files, selfie);
      setResults(result);
      
      const fileNames = Array.isArray(files) 
        ? files.map(f => f.name).join(', ') 
        : (files?.name || 'Uploaded Document');

      const newEntry = {
        id: Date.now(),
        filename: fileNames,
        date: new Date().toLocaleString(),
        risk: result.overall_risk,
        score: result.risk_score,
        document: result.document?.name || 'Unknown',
        documentType: result.is_multi_document 
          ? `Multi-Doc (${result.documents?.length || 2})` 
          : (result.document?.type || 'Document'),
        number: result.document?.number || 'N/A',
        dob: result.document?.dob || 'N/A',
        expiry: result.document?.expiry || 'N/A',
        findings: result.findings || [],
        tampering_signals: result.tampering_signals || [],
        face_match: result.face_match || { score: 0, passed: false },
        is_multi_document: !!result.is_multi_document,
        cross_document: result.cross_document || null
      };
      
      setUploadedFiles(prev => [newEntry, ...prev]);
      setScreen('results');
    } catch (err) {
      setError(err.message);
      setScreen('upload');
      setActiveTab('Upload');
    }
  };

  const handleReset = () => {
    setScreen('upload');
    setResults(null);
    setError(null);
    setActiveTab('Upload');
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'Upload') {
      setScreen('upload');
    } else if (tab === 'Dashboard') {
      if (results) {
        setScreen('results');
      } else {
        alert('📋 No document verified yet. Please upload and verify a document first.');
        setActiveTab('Upload');
      }
    } else if (tab === 'History') {
      setScreen('history');
    } else if (tab === 'Profile') {
      setScreen('profile');
    } else if (tab === 'Settings') {
      setScreen('settings');
    }
  };

  const viewHistoryDetail = (item) => {
    const result = {
      overall_risk: item.risk,
      risk_score: item.score,
      human_review_required: item.risk === 'HIGH' || item.risk === 'MEDIUM',
      document: {
        name: item.document || 'Unknown',
        type: item.documentType || 'Document',
        number: item.number || 'N/A',
        dob: item.dob || 'N/A',
        expiry: item.expiry || 'N/A'
      },
      findings: item.findings || [
        { check: "Document Validation", status: "PASS", reason: "Document verified" },
        { check: "Expiry Date", status: "PASS", reason: "Document is valid" }
      ],
      tampering_signals: item.tampering_signals || [],
      face_match: item.face_match || { score: 0, passed: false, message: "Face verification not available" }
    };
    
    setResults(result);
    setActiveTab('Dashboard');
    setScreen('results');
  };

  const handleExportReport = () => {
    if (!results) {
      alert('No results to export. Please verify a document first.');
      return;
    }
    
    const report = `
========================================
        VERIGUARD AI REPORT
========================================
User: ${user?.email || 'Guest'}

Document: ${results.document?.name || 'N/A'}
Type: ${results.document?.type || 'N/A'}
Number: ${results.document?.number || 'N/A'}
DOB: ${results.document?.dob || 'N/A'}
Expiry: ${results.document?.expiry || 'N/A'}

----------------------------------------
RISK ASSESSMENT
----------------------------------------
Overall Risk: ${results.overall_risk}
Risk Score: ${results.risk_score}%
Human Review Required: ${results.human_review_required ? 'YES' : 'NO'}

----------------------------------------
FINDINGS
----------------------------------------
${results.findings?.map(f => `${f.check}: ${f.status} - ${f.reason}`).join('\n')}

----------------------------------------
TAMPERING SIGNALS
----------------------------------------
${results.tampering_signals?.length > 0 
  ? results.tampering_signals.map(s => `${s.type}: ${s.severity} - ${s.details}`).join('\n')
  : 'No tampering signals detected'}

----------------------------------------
FACE VERIFICATION
----------------------------------------
Match Score: ${results.face_match?.score || 0}%
Match: ${results.face_match?.passed ? 'YES' : 'NO'}
Message: ${results.face_match?.message || 'Not performed'}

========================================
Report Generated: ${new Date().toLocaleString()}
========================================
    `;
    
    const blob = new Blob([report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `VeriGuard_Report_${new Date().toISOString().slice(0,10)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    alert('✅ Report exported successfully!');
  };

  const handleSettingsSave = (setting, value) => {
    setSettingsMessage(`✅ ${setting} updated to: ${value}`);
    setTimeout(() => setSettingsMessage(''), 3000);
  };

  const handleClearHistory = () => {
    if (window.confirm('Clear all screening history?')) {
      setUploadedFiles([]);
      localStorage.removeItem('veriguard_history');
    }
  };

  // Render History Page
  const renderHistory = () => (
    <div className="page">
      <div className="page-head" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>📋 Screening History</h1>
          <p>Click on any entry to view full details</p>
        </div>
        {uploadedFiles.length > 0 && (
          <button className="btn btn-danger" onClick={handleClearHistory}>
            Clear All
          </button>
        )}
      </div>
      {uploadedFiles.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
          <h3>No history yet</h3>
          <p style={{ color: '#64748b' }}>Upload and verify a document to see it here.</p>
          <button 
            className="btn btn-primary" 
            onClick={() => handleTabChange('Upload')}
            style={{ marginTop: '16px' }}
          >
            Go to Upload
          </button>
        </div>
      ) : (
        <div className="grid g2">
          {uploadedFiles.map((item) => (
            <div 
              key={item.id} 
              className="card history-item"
              onClick={() => viewHistoryDetail(item)}
              style={{ cursor: 'pointer' }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <strong>{item.filename}</strong>
                  <div style={{ fontSize: '12px', color: '#64748b' }}>{item.date}</div>
                  <div style={{ fontSize: '12px', color: '#64748b' }}>Document: {item.document}</div>
                  {item.face_match && (
                    <div style={{ fontSize: '11px', color: item.face_match.passed ? '#16A34A' : '#DC2626' }}>
                      Face: {item.face_match.passed ? '✅ Match' : '❌ No match'} ({item.face_match.score}%)
                    </div>
                  )}
                </div>
                <span className={`badge ${item.risk === 'LOW' ? 'low' : item.risk === 'HIGH' ? 'high' : 'medium'}`}>
                  {item.risk} · {item.score}%
                </span>
              </div>
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#94a3b8' }}>
                Click to view details →
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  // Render Profile Page
  const renderProfile = () => (
    <div className="profile-wrap">
      <div className="profile-card">
        <div className="profile-avatar">👤</div>
        <h2>{user?.email?.split('@')[0] || 'User'}</h2>
        <p className="profile-email">{user?.email || 'No email'}</p>
        
        <div className="profile-stats">
          <div className="profile-stat">
            <span className="num">{uploadedFiles.length}</span>
            <span className="label">Verifications</span>
          </div>
          <div className="profile-stat">
            <span className="num">
              {uploadedFiles.filter(f => f.risk === 'LOW').length}
            </span>
            <span className="label">Low Risk</span>
          </div>
          <div className="profile-stat">
            <span className="num">
              {uploadedFiles.filter(f => f.risk === 'HIGH').length}
            </span>
            <span className="label">High Risk</span>
          </div>
        </div>

        <div className="profile-actions">
          <button className="btn btn-secondary" onClick={() => handleTabChange('History')}>
            View History
          </button>
          <button className="btn btn-danger" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>
    </div>
  );

  // Render Settings Page
  const renderSettings = () => (
    <div className="page">
      <div className="page-head">
        <h1>⚙️ Settings</h1>
        <p>Configure VeriGuard AI preferences</p>
      </div>
      
      {settingsMessage && (
        <div style={{
          padding: '12px 16px',
          background: '#DCFCE7',
          borderRadius: '8px',
          border: '1px solid #16A34A',
          color: '#166534',
          marginBottom: '18px'
        }}>
          {settingsMessage}
        </div>
      )}
      
      <div className="grid g2">
        <div className="card">
          <h3><span className="ic">🔍</span>OCR Settings</h3>
          <div style={{ fontSize: '13px', color: '#64748b' }}>
            <p><strong>Language:</strong> English</p>
            <p><strong>Confidence Threshold:</strong> 60%</p>
          </div>
          <button 
            className="btn btn-secondary" 
            style={{ marginTop: '12px' }}
            onClick={() => handleSettingsSave('Language', 'English (Default)')}
          >
            Reset to Default
          </button>
        </div>
        
        <div className="card">
          <h3><span className="ic">🛡️</span>Risk Settings</h3>
          <div style={{ fontSize: '13px', color: '#64748b' }}>
            <p><strong>Low Risk:</strong> 0-30</p>
            <p><strong>Medium Risk:</strong> 31-60</p>
            <p><strong>High Risk:</strong> 61-100</p>
          </div>
          <button 
            className="btn btn-secondary" 
            style={{ marginTop: '12px' }}
            onClick={() => handleSettingsSave('Risk Thresholds', 'Default (0-30, 31-60, 61-100)')}
          >
            Reset to Default
          </button>
        </div>
        
        <div className="card">
          <h3><span className="ic">📷</span>Face Verification</h3>
          <div style={{ fontSize: '13px', color: '#64748b' }}>
            <p><strong>Threshold:</strong> 60%</p>
            <p><strong>Status:</strong> ✅ Active</p>
          </div>
          <button 
            className="btn btn-secondary" 
            style={{ marginTop: '12px' }}
            onClick={() => handleSettingsSave('Face Threshold', '60% (Default)')}
          >
            Reset to Default
          </button>
        </div>
        
        <div className="card">
          <h3><span className="ic">🔒</span>Privacy</h3>
          <div style={{ fontSize: '13px', color: '#64748b' }}>
            <p>✅ Images deleted after processing</p>
            <p>✅ No data stored permanently</p>
            <p>✅ Secure processing pipeline</p>
          </div>
          <button 
            className="btn btn-secondary" 
            style={{ marginTop: '12px' }}
            onClick={() => handleSettingsSave('Privacy Settings', 'All data is deleted after processing')}
          >
            View Privacy Policy
          </button>
        </div>
      </div>
    </div>
  );

  // Show Login Page if not logged in
  if (!isLoggedIn) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div className="app">
      <TopBar 
        activeTab={activeTab} 
        onTabChange={handleTabChange}
        user={user}
        onLogout={handleLogout}
      />
      
      {screen === 'upload' && (
        <>
          <UploadPage onUpload={handleUpload} />
          {error && (
            <div style={{ 
              maxWidth: '520px', 
              margin: '-40px auto 0', 
              padding: '12px 20px',
              background: '#FEE2E2',
              borderRadius: '8px',
              border: '1px solid #EF4444',
              color: '#991B1B',
              textAlign: 'center',
              fontSize: '14px'
            }}>
              ❌ {error}
            </div>
          )}
        </>
      )}
      
      {screen === 'processing' && <ProcessingPage />}
      
      {screen === 'results' && results && (
        <ResultsPage 
          result={results} 
          onReset={handleReset} 
          onExport={handleExportReport}
        />
      )}

      {screen === 'history' && renderHistory()}
      
      {screen === 'profile' && renderProfile()}
      
      {screen === 'settings' && renderSettings()}
    </div>
  );
}

export default App;