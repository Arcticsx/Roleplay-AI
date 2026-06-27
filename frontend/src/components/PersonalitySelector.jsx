import React, { useState, useEffect } from 'react';
import { api, getImageUrl } from '../api';
import ConfirmModal from './ConfirmModal.jsx';
import EditModal from './EditModal.jsx';
import './PersonalitySelector.css';
import Sidebar from './Sidebar.jsx';

function PersonalitySelector({ onPersonaSelected }) {
  const [personalities, setPersonalities] = useState({});
  const [editingPersonaKey, setEditingPersonaKey] = useState(null);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [modalInitialData, setModalInitialData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [toast, setToast] = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmTarget, setConfirmTarget] = useState(null);
  const [query, setQuery] = useState('');
  const [activeView, setActiveView] = useState('discover');

  useEffect(() => {
    loadPersonalities();
  }, []);

  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(''), 3000);
    return () => clearTimeout(timer);
  }, [toast]);

  const loadPersonalities = async () => {
    setError('');
    setLoading(true);
    try {
      const data = await api.getPersonalities();
      setPersonalities(data);
    } catch (error) {
      console.error('Failed to load personalities:', error);
      setError('Unable to load personalities. Confirm the backend is running.');
      setPersonalities({});
    }
    setLoading(false);
  };

  const handlePersonaClick = (persona) => {
    onPersonaSelected(persona);
  };

  const handleSavePersona = async (data) => {
    setLoading(true);
    setError('');
    setToast('');
    try {
      if (editingPersonaKey) {
        await api.updatePersonality(editingPersonaKey, data);
      } else {
        await api.createPersonality(data);
      }
      await loadPersonalities();
      setEditModalOpen(false);
      setEditingPersonaKey(null);
      setModalInitialData(null);
      setToast('Persona saved successfully');
    } catch (error) {
      console.error('Failed to save personality:', error);
      setError(`Failed to save personality: ${error.message}`);
      setToast(`Failed to save: ${error.message}`);
    }
    setLoading(false);
  };

  const handleEditPersona = (e, persona) => {
    e.stopPropagation();
    setEditingPersonaKey(persona.key);
    setModalInitialData(persona);
    setEditModalOpen(true);
  };

  const handleDeletePersona = (e, persona) => {
    e.stopPropagation();
    setConfirmTarget(persona);
    setConfirmOpen(true);
  };

  const doDeleteConfirmed = async () => {
    if (!confirmTarget) return;
    setConfirmOpen(false);
    setLoading(true);
    setError('');
    setToast('');
    try {
      await api.deletePersonality(confirmTarget.key);
      setToast(`Deleted ${confirmTarget.name}`);
      await loadPersonalities();
    } catch (error) {
      console.error('Failed to delete personality:', error);
      setError(`Failed to delete personality: ${error.message}`);
      setToast(`Delete failed: ${error.message}`);
    }
    setConfirmTarget(null);
    setLoading(false);
  };

  const handleCancelEdit = () => {
    setEditModalOpen(false);
    setEditingPersonaKey(null);
    setModalInitialData(null);
  };

  // Filter personalities based on search query
  const filteredList = Object.values(personalities).filter((p) => {
    const search = query.toLowerCase();
    return (
      p.name.toLowerCase().includes(search) ||
      (p.description || '').toLowerCase().includes(search) ||
      p.key.toLowerCase().includes(search)
    );
  });

  // For "Featured" we can show first 4, "For you" rest, or just show all in one grid
  // We'll just show all in a single grid with a "Discover" heading
  const personalityList = filteredList;

  return (
    <div className="ca-layout">
      {/* Sidebar */}
      <Sidebar
        activeView={activeView}
        onViewChange={setActiveView}
        onCreateClick={() => {
          setEditingPersonaKey(null);
          setModalInitialData(null);
          setEditModalOpen(true);
        }}/>

      {/* Main content */}
      <main className="ca-main">
        {/* Top bar */}
        <header className="ca-topbar">
          <div className="ca-search">
            <input
              type="text"
              placeholder="Search personalities…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <div className="ca-top-actions">
            <button
              className="btn-create"
              onClick={() => {
                setEditingPersonaKey(null);
                setModalInitialData(null);
                setEditModalOpen(true);
              }}
            >
              + Create New
            </button>
          </div>
        </header>

        {/* Error / Toast */}
        {error && <div className="ca-error">{error}</div>}
        {toast && <div className="ca-toast">{toast}</div>}

        {/* Content */}
        <section className="ca-content">
          {loading ? (
            <div className="ca-loading">Loading personalities…</div>
          ) : personalityList.length === 0 ? (
            <div className="ca-empty">
              <p>No personalities found. Create one to get started.</p>
            </div>
          ) : (
            <>
              <div className="ca-section">
                <h2 className="ca-section-title">Discover</h2>
                <div className="ca-grid">
                  {personalityList.map((persona) => (
                    <div
                      key={persona.key}
                      className="ca-card"
                      onClick={() => handlePersonaClick(persona)}
                    >
                      <div className="card-avatar">
                        {persona.avatar ? (
                          <img src={getImageUrl(persona.avatar)} alt={persona.name} />
                        ) : (
                          <span>{persona.name.charAt(0)}</span>
                        )}
                      </div>
                      <div className="card-body">
                        <h3 className="card-name">{persona.name}</h3>
                        <p className="card-creator">by @user_{persona.key}</p>
                        <p className="card-description">{persona.description || 'No description'}</p>
                        <div className="card-stats">
                          <span>💬 0 sessions</span>
                        </div>
                      </div>
                      <div className="card-actions">
                        <button
                          className="btn-edit"
                          onClick={(e) => handleEditPersona(e, persona)}
                          title="Edit"
                        >
                          ✎
                        </button>
                        <button
                          className="btn-delete"
                          onClick={(e) => handleDeletePersona(e, persona)}
                          title="Delete"
                        >
                          🗑
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </section>
      </main>

      <EditModal
        open={editModalOpen}
        initialData={modalInitialData}
        onSave={handleSavePersona}
        onCancel={handleCancelEdit}
        saving={loading}
      />
      <ConfirmModal
        open={confirmOpen}
        title="Delete Persona"
        message={confirmTarget ? `Delete persona '${confirmTarget.name}'? This cannot be undone.` : ''}
        onConfirm={doDeleteConfirmed}
        onCancel={() => setConfirmOpen(false)}
      />
    </div>
  );
}

export default PersonalitySelector;