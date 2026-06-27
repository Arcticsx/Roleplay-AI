import React from "react";
import "./Sidebar.css";

function Sidebar({ activeView, onViewChange, onCreateClick }) {
    return (
        <aside className="ca-sidebar">
        <div className="ca-brand">✦ SARP</div>
        <nav className="ca-nav">
          <button
            className={`nav-item ${activeView === 'create' ? 'active' : ''}`}
            onClick={onCreateClick}
          >
            <span className="nav-icon">+</span> Create
          </button>
          <button
            className={`nav-item ${activeView === 'discover' ? 'active' : ''}`}
            onClick={() => onViewChange('discover')}
          >
            <span className="nav-icon">✦</span> Discover
          </button>
          <button
            className={`nav-item ${activeView === 'feed' ? 'active' : ''}`}
            onClick={() => onViewChange('feed')}
          >
            <span className="nav-icon">📰</span> Feed
          </button>
          <button
            className={`nav-item ${activeView === 'charms' ? 'active' : ''}`}
            onClick={() => onViewChange('charms')}
          >
            <span className="nav-icon">✨</span> Charms
          </button>
          <button
            className={`nav-item ${activeView === 'labs' ? 'active' : ''}`}
            onClick={() => onViewChange('labs')}
          >
            <span className="nav-icon">🧪</span> Labs
          </button>
        </nav>
        <div className="ca-sidebar-footer">
          <div className="ca-user">
            <span className="user-avatar">👤</span>
            <span className="user-name">Guest</span>
          </div>
        </div>
      </aside>
    );
}

export default Sidebar;