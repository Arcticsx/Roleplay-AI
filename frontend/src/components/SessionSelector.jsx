import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { api, getImageUrl } from '../api';
import './SessionSelector.css';

function SessionSelector({ persona, onSessionSelected, onBack }) {
  const { personaKey } = useParams();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!persona?.name && personaKey) {
      return;
    }
    loadSessions();
  }, [persona, personaKey]);

  const loadSessions = async () => {
    setLoading(true);
    try {
      const data = await api.getSessions(persona.name);
      setSessions(data.sessions || []);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
    setLoading(false);
  };

  const handleSelectSession = (session) => {
    onSessionSelected(session);
  };

  const handleNewSession = () => {
    onSessionSelected(null);
  };

  const handleDeleteSession = async (e, session) => {
    e.stopPropagation();
    if (!window.confirm(`Delete session ${session.id}?`)) return;
    try {
      await api.deleteSession(persona.name, session.id);
      await loadSessions();
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const getDateGroup = (dateStr) => {
    const date = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    if (date.toDateString() === today.toDateString()) return 'Today';
    if (date.toDateString() === yesterday.toDateString()) return 'Yesterday';
    return 'Older';
  };

  const grouped = sessions.reduce((acc, session) => {
    const group = getDateGroup(session.updated_at || session.created_at);
    if (!acc[group]) acc[group] = [];
    acc[group].push(session);
    return acc;
  }, {});

  const sortedGroups = ['Today', 'Yesterday', 'Older'].filter(g => grouped[g]);

  return (
    <div className="ca-session-layout">
      {/* Sidebar */}
      <aside className="ca-session-sidebar">
        <div className="session-persona">
          <div className="session-persona-avatar">
            {persona.avatar ? (
              <img src={getImageUrl(persona.avatar)} alt={persona.name} />
            ) : (
              <span>{persona.name.charAt(0)}</span>
            )}
          </div>
          <div className="session-persona-info">
            <h3>{persona.name}</h3>
            <p>#{persona.key}</p>
          </div>
        </div>
        <button className="btn-back-persona" onClick={onBack}>
          ← Back to personalities
        </button>
        <div className="session-sidebar-footer">
          <span>📋 {sessions.length} sessions</span>
        </div>
      </aside>

      {/* Main content */}
      <main className="ca-session-main">
        <header className="ca-session-header">
          <h1>Choose a session</h1>
          <button className="btn-new-session" onClick={handleNewSession}>
            + New Chat
          </button>
        </header>

        {loading && <p className="loading-text">Loading sessions…</p>}

        <div className="session-list">
          {sortedGroups.map((groupName) => (
            <div key={groupName} className="session-group">
              <div className="session-group-label">{groupName}</div>
              {grouped[groupName].map((session) => (
                <div
                  key={session.id}
                  className="session-item"
                  onClick={() => handleSelectSession(session)}
                >
                  <div className="session-icon">💬</div>
                  <div className="session-info">
                    <div className="session-title">Session #{session.id}</div>
                    <div className="session-meta">
                      {new Date(session.updated_at).toLocaleString()}
                    </div>
                  </div>
                  <button
                    className="btn-delete-session"
                    onClick={(e) => handleDeleteSession(e, session)}
                    title="Delete session"
                  >
                    🗑
                  </button>
                </div>
              ))}
            </div>
          ))}

          {sessions.length === 0 && !loading && (
            <div className="empty-sessions">
              <p>No previous sessions. Start a new one!</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default SessionSelector;