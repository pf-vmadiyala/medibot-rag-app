'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  ShieldAlert,
  Send,
  LogOut,
  Database,
  FolderLock,
  Sparkles,
  FileText,
  LockKeyhole
} from 'lucide-react';

export default function Home() {
  const [user, setUser] = useState(null); // { username, role, token }
  const [usernameInput, setUsernameInput] = useState('');
  const [passwordInput, setPasswordInput] = useState('');
  const [loginError, setLoginError] = useState('');

  const [collections, setCollections] = useState([]);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);

  // Sync scroll on chat update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load collections when role changes
  useEffect(() => {
    if (user?.role) {
      fetch(`http://localhost:8000/collections/${user.role}`)
        .then((res) => {
          if (!res.ok) throw new Error('Failed to load collections');
          return res.json();
        })
        .then((data) => setCollections(data))
        .catch((err) => console.error(err));
    }
  }, [user]);

  // Handle Demo Quick Login
  const handleQuickLogin = (uname, role) => {
    setLoading(true);
    setLoginError('');

    fetch('http://localhost:8000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: uname, password: 'password' })
    })
      .then((res) => {
        if (!res.ok) throw new Error('Invalid credentials');
        return res.json();
      })
      .then((data) => {
        setUser({ username: data.username, role: data.role, token: data.token });
        setMessages([
          {
            sender: 'bot',
            text: `Welcome, ${uname}! I am MediBot. How can I assist you today?`,
            retrieval_type: 'system'
          }
        ]);
      })
      .catch((err) => setLoginError(err.message))
      .finally(() => setLoading(false));
  };

  // Handle Manual Form Submission
  const handleManualLogin = (e) => {
    e.preventDefault();
    setLoading(true);
    setLoginError('');

    fetch('http://localhost:8000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: usernameInput, password: passwordInput })
    })
      .then((res) => {
        if (!res.ok) throw new Error('Invalid username or password');
        return res.json();
      })
      .then((data) => {
        setUser({ username: data.username, role: data.role, token: data.token });
        setMessages([
          {
            sender: 'bot',
            text: `Welcome back, ${data.username}! I am MediBot. How can I help you today?`,
            retrieval_type: 'system'
          }
        ]);
      })
      .catch((err) => setLoginError(err.message))
      .finally(() => setLoading(false));
  };

  // Handle Send Chat Message
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    const userText = inputMessage;
    setInputMessage('');
    setMessages((prev) => [...prev, { sender: 'user', text: userText }]);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify({ question: userText })
      });

      if (!response.ok) {
        throw new Error('Connection error. Server may be down.');
      }

      const data = await response.json();

      // Determine if it was an RBAC refusal message
      const isRefusal = data.answer.toLowerCase().includes('access denied') ||
        data.answer.toLowerCase().includes('sorry') && data.answer.toLowerCase().includes('access');

      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: data.answer,
          sources: data.sources || [],
          retrieval_type: data.retrieval_type,
          isRefusal: isRefusal
        }
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: `Error: ${err.message}`,
          retrieval_type: 'error',
          isRefusal: true
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setUser(null);
    setMessages([]);
    setUsernameInput('');
    setPasswordInput('');
  };

  // Render Login Card
  if (!user) {
    return (
      <div className="login-container">
        <div className="login-card">
          <h2>MediBot Portal</h2>
          <p>Sign in to access search & analytics</p>

          <div className="demo-accounts-title">Quick Demo Login</div>
          <div className="demo-grid">
            <button className="demo-btn" onClick={() => handleQuickLogin('dr.mehta', 'doctor')}>
              <span>dr.mehta</span>
              <span className="role-tag role-doctor">Doctor</span>
            </button>
            <button className="demo-btn" onClick={() => handleQuickLogin('nurse.priya', 'nurse')}>
              <span>nurse.priya</span>
              <span className="role-tag role-nurse">Nurse</span>
            </button>
            <button className="demo-btn" onClick={() => handleQuickLogin('billing.ravi', 'billing_executive')}>
              <span>billing.ravi</span>
              <span className="role-tag role-billing_executive">Billing Exec</span>
            </button>
            <button className="demo-btn" onClick={() => handleQuickLogin('tech.anand', 'technician')}>
              <span>tech.anand</span>
              <span className="role-tag role-technician">Technician</span>
            </button>
            <button className="demo-btn" onClick={() => handleQuickLogin('admin.sys', 'admin')}>
              <span>admin.sys</span>
              <span className="role-tag role-admin">Admin</span>
            </button>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', margin: '1.5rem 0' }}>
            <hr style={{ flex: 1, border: '0', borderTop: '1px solid var(--border-color)' }} />
            <span style={{ padding: '0 0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>OR</span>
            <hr style={{ flex: 1, border: '0', borderTop: '1px solid var(--border-color)' }} />
          </div>

          <form onSubmit={handleManualLogin}>
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                className="form-control"
                value={usernameInput}
                onChange={(e) => setUsernameInput(e.target.value)}
                placeholder="Enter username"
                required
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                className="form-control"
                value={passwordInput}
                onChange={(e) => setPasswordInput(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>
            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? 'Authenticating...' : 'Sign In'}
            </button>
            {loginError && <div className="error-text">{loginError}</div>}
          </form>
        </div>
      </div >
    );
  }

  // Render Dashboard
  const activeRoleClass = `role-${user.role}`;

  return (
    <div className="chat-layout">
      {/* Sidebar Panel */}
      <aside className="sidebar">
        <div className="sidebar-top">
          <div className="brand">
            <Sparkles size={20} color="#3b82f6" />
            <span>MediBot Console</span>
          </div>

          <div className="user-profile">
            <div className="user-profile-title">Signed In As</div>
            <div className="user-profile-name">{user.username}</div>
            <span className={`role-tag ${activeRoleClass}`}>
              {user.role.replace('_', ' ')}
            </span>
          </div>

          <div className="collections-panel">
            <div className="collections-title">Accessible Documents</div>
            {collections.length === 0 ? (
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Loading rules...</p>
            ) : (
              collections.map((col, idx) => (
                <div className="collection-item" key={idx}>
                  <div className="collection-dot"></div>
                  <span>{col.toUpperCase()}</span>
                </div>
              ))
            )}
          </div>
        </div>

        <button className="logout-btn" onClick={handleLogout}>
          <LogOut size={16} />
          <span>Logout</span>
        </button>
      </aside>

      {/* Main Chat Interface */}
      <main className="chat-window">
        <header className="chat-header">
          <h1>MediAssist RAG Assistant</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            <LockKeyhole size={14} color="#10b981" />
            <span>Strict RBAC Active</span>
          </div>
        </header>

        {/* Message Feed */}
        <div className="chat-messages">
          {messages.map((msg, idx) => {
            const isBot = msg.sender === 'bot';
            return (
              <div key={idx} className={`message ${msg.sender} ${msg.isRefusal ? 'refusal-card' : ''}`}>
                <div className="message-bubble">
                  {msg.text}
                </div>

                {isBot && (
                  <div className="meta-row">
                    {msg.retrieval_type === 'sql_rag' && (
                      <span className="badge-tag badge-rag-type" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        <Database size={10} /> Database SQL
                      </span>
                    )}
                    {msg.retrieval_type === 'hybrid_rag' && (
                      <span className="badge-tag badge-rag-type" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        <Sparkles size={10} /> Hybrid RAG
                      </span>
                    )}
                    {msg.isRefusal && (
                      <span className="badge-tag" style={{ background: 'rgba(239,68,68,0.12)', color: '#f87171', border: '1px solid rgba(239,68,68,0.2)', display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        <ShieldAlert size={10} /> RBAC Blocked
                      </span>
                    )}

                    {/* Sources Box */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="citations-box">
                        <div className="citations-title">Retrieved Citations:</div>
                        <div className="citation-links">
                          {msg.sources.map((src, sIdx) => (
                            <div key={sIdx} className="citation-chip" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                              <FileText size={10} />
                              <span>{src.source_document} &gt; {src.section_title} ({src.collection})</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
          {loading && (
            <div className="message bot">
              <div className="message-bubble" style={{ color: 'var(--text-secondary)' }}>
                Thinking...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="chat-input-area">
          <form className="chat-input-form" onSubmit={handleSendMessage}>
            <input
              type="text"
              className="chat-input"
              placeholder="Ask me something about policy codes, clinical guidelines or claim figures..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              disabled={loading}
            />
            <button type="submit" className="send-btn" disabled={!inputMessage.trim() || loading}>
              <Send size={18} />
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
