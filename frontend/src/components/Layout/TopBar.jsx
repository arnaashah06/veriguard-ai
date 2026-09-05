// src/components/Layout/TopBar.jsx

const TopBar = ({ activeTab = 'Upload', onTabChange, user, onLogout }) => {
  const tabs = ['Upload', 'Dashboard', 'History', 'Profile', 'Settings'];

  return (
    <header className="topbar">
      <div className="brand">
        <span className="mark">🛡️</span>
        VeriGuard AI
      </div>
      <nav>
        {tabs.map((tab) => (
          <span
            key={tab}
            className={tab === activeTab ? 'on' : ''}
            onClick={() => onTabChange && onTabChange(tab)}
          >
            {tab}
          </span>
        ))}
      </nav>
      <div className="user">
        <span className="username">{user?.email?.split('@')[0] || 'User'}</span>
        {onLogout ? (
          <button
            type="button"
            onClick={onLogout}
            title="Logout"
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: '14px',
              padding: '2px 4px',
            }}
          >
            🚪
          </button>
        ) : (
          <span>👤</span>
        )}
      </div>
    </header>
  );
};

export default TopBar;