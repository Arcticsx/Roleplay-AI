import React, { useState, useEffect } from 'react';
import { getImageUrl } from '../api';
import './EditModal.css';

export default function EditModal({ open, initialData, onSave, onCancel, saving }) {
  const [form, setForm] = useState({ name: '', description: '', system: '', scenario: '', opening_prompt: '', avatar: null });
  const [errors, setErrors] = useState({});
  const [preview, setPreview] = useState('');

  useEffect(() => {
    if (initialData) {
      setForm({
        name: initialData.name || '',
        description: initialData.description || '',
        system: initialData.system || '',
        scenario: initialData.Scenario || '',
        opening_prompt: initialData.opening_prompt || '',
        avatar: null // Don't store existing avatar as file object
      });
      // Set preview to the backend URL for existing avatar
      setPreview(initialData.avatar ? getImageUrl(initialData.avatar) : '');
    } else {
      setForm({ name: '', description: '', system: '', scenario: '', opening_prompt: '', avatar: null });
      setPreview('');
    }
    setErrors({});
  }, [initialData, open]);

  if (!open) return null;

  const validate = () => {
    const e = {};
    if (!form.name.trim()) e.name = 'Name is required';
    if (!form.system.trim()) e.system = 'System prompt is required';
    return e;
  };

  const handleChange = (k, v) => setForm({ ...form, [k]: v });

  const handleFileChange = (e) => {
    const f = e.target.files && e.target.files[0];
    if (!f) return;
    
    // Store the actual File object
    setForm((s) => ({ ...s, avatar: f }));
    
    // Create preview URL for display
    const reader = new FileReader();
    reader.onload = () => {
      setPreview(reader.result);
    };
    reader.readAsDataURL(f);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const eobj = validate();
    setErrors(eobj);
    if (Object.keys(eobj).length === 0) {
      onSave(form);
    }
  };

  return (
    <div className="edit-overlay">
      <div className="edit-modal glass">
        <h3>{initialData ? 'Edit Personality' : 'Create Personality'}</h3>
        <form onSubmit={handleSubmit}>
          <label>Name</label>
          <input value={form.name} onChange={(e) => handleChange('name', e.target.value)} />
          {errors.name && <div className="field-error">{errors.name}</div>}

          <label>Description</label>
          <textarea value={form.description} onChange={(e) => handleChange('description', e.target.value)} />

          <label>System Prompt</label>
          <textarea value={form.system} onChange={(e) => handleChange('system', e.target.value)} />
          {errors.system && <div className="field-error">{errors.system}</div>}

          <label>Base Prompt / Scenario</label>
          <textarea value={form.scenario} onChange={(e) => handleChange('scenario', e.target.value)} />

          <label>Opening Prompt</label>
          <textarea value={form.opening_prompt} onChange={(e) => handleChange('opening_prompt', e.target.value)} />

          <label>Avatar Image</label>
          <input type="file" accept="image/*" onChange={handleFileChange} />
          {preview && <div className="avatar-preview"><img src={preview} alt="preview" /></div>}

          <div className="edit-buttons">
            <button type="button" className="btn-cancel" onClick={onCancel} disabled={saving}>Cancel</button>
            <button type="submit" className="btn-save" disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}
