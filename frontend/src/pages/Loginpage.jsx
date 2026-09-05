// src/pages/Loginpage.jsx
import { useState } from 'react';

const Loginpage = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSignup, setIsSignup] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    if (isSignup) {
      const users = JSON.parse(localStorage.getItem('veriguard_users') || '[]');
      if (users.find(u => u.email === email)) {
        setError('User already exists');
        return;
      }
      users.push({ email, password });
      localStorage.setItem('veriguard_users', JSON.stringify(users));
      alert('Account created! Please login.');
      setIsSignup(false);
      setPassword('');
    } else {
      const users = JSON.parse(localStorage.getItem('veriguard_users') || '[]');
      const user = users.find(u => u.email === email && u.password === password);
      if (!user) {
        setError('Invalid email or password');
        return;
      }
      localStorage.setItem('veriguard_current_user', JSON.stringify({ email }));
      onLogin({ email });
    }
  };

  return (
    <div className="login-wrap">
      <div className="login-card">
        <div className="login-icon">🛡️</div>
        <h2>{isSignup ? 'Create Account' : 'Welcome Back'}</h2>
        <p>{isSignup ? 'Sign up to start verifying documents' : 'Login to access VeriGuard AI'}</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
            />
          </div>

          {error && <div className="login-error">❌ {error}</div>}

          <button type="submit" className="btn btn-primary login-btn">
            {isSignup ? 'Create Account' : 'Login'}
          </button>
        </form>

        <div className="login-footer">
          <span>
            {isSignup ? 'Already have an account?' : "Don't have an account?"}
          </span>
          <button
            className="btn btn-secondary"
            onClick={() => { setIsSignup(!isSignup); setError(''); }}
          >
            {isSignup ? 'Login' : 'Sign Up'}
          </button>
        </div>

        <div className="login-demo">
          <p>Demo Accounts:</p>
          <div className="demo-grid">
            <div className="demo-item">
              <span>user@demo.com</span>
              <span className="demo-pass">password123</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Loginpage;