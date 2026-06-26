import React, { useState, useEffect } from 'react';
import { api, getImageUrl } from '../api';
import ConfirmModal from './ConfirmModal.jsx';
import EditModal from './EditModal.jsx';
import './PersonalitySelector.css';

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
      setError('Unable to load personalities. Confirm the backend is running on localhost:8000.');
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
      const savedPersona = editingPersonaKey
        ? await api.updatePersonality(editingPersonaKey, data)
        : await api.createPersonality(data);
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

  const handleDeletePersona = async (e, persona) => {
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

  const personalityList = Object.values(personalities);
  const filteredPersonalities = personalityList.filter((persona) => {
    const search = query.toLowerCase();
    return (
      persona.name.toLowerCase().includes(search) ||
      String(persona.key).includes(search) ||
      (persona.description || '').toLowerCase().includes(search)
    );
  });

  return (
    <div className="personality-selector">
      <h1>SELECT PERSONALITY</h1>

      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button type="button" className="btn-retry" onClick={loadPersonalities} disabled={loading}>
            Retry
          </button>
        </div>
      )}
      {toast && <div className="toast">{toast}</div>}
      {loading && <p>Loading...</p>}

      <div className="personality-controls">
        <input
          placeholder="Search by name, key, or description"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          className="btn-create"
          type="button"
          onClick={() => {
            setEditingPersonaKey(null);
            setModalInitialData(null);
            setEditModalOpen(true);
          }}
          disabled={loading}
        >
          + CREATE NEW PERSONALITY
        </button>
      </div>

      <div className="personality-list personality-card-grid">
        {filteredPersonalities.length === 0 && !loading && (
          <p className="empty-state">No personalities found. Create one to get started.</p>
        )}

        {filteredPersonalities.map((persona) => (
          <div key={persona.key} className="persona-card">
            <div className="persona-card-top">
              <div className="persona-avatar-wrap" onClick={() => handlePersonaClick(persona)}>
                {persona.avatar ? (
                  <img src={getImageUrl(persona.avatar)} alt={persona.name} className="persona-avatar" />
                ) : (
                  <div className="persona-avatar-fallback">{(persona.name || 'P').charAt(0)}</div>
                )}
              </div>
              <div className="persona-card-meta" onClick={() => handlePersonaClick(persona)}>
                <div className="persona-card-name">{persona.name}</div>
                <div className="persona-card-key">{persona.key ? `#${persona.key}` : 'untagged'}</div>
              </div>
            </div>

            {persona.description && <div className="persona-card-description">{persona.description}</div>}

            <div className="persona-card-bottom">
              <button
                type="button"
                className="btn-ghost"
                onClick={() => handlePersonaClick(persona)}
              >
                Open persona
              </button>
              <div className="persona-card-actions">
                <button
                  type="button"
                  className="btn-icon"
                  onClick={(e) => handleEditPersona(e, persona)}
                  disabled={loading}
                  title="Edit personality"
                >
                  ✎
                </button>
                <button
                  type="button"
                  className="btn-icon btn-delete"
                  onClick={(e) => handleDeletePersona(e, persona)}
                  disabled={loading}
                  title="Delete personality"
                >
                  🗑
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

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
