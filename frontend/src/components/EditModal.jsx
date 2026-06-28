import React, { useState, useEffect } from 'react';
import { getImageUrl } from '../api';

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
        avatar: null
      });
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

    setForm((s) => ({ ...s, avatar: f }));

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
    <div className="fixed inset-0 z-[9998] flex items-center justify-center bg-black/70 p-4">
      <div className="w-full max-w-2xl rounded-3xl border border-border/60 bg-surface/90 p-6 shadow-2xl shadow-black/50 backdrop-blur-xl">
        <h3 className="text-xl font-semibold text-text">{initialData ? 'Edit Personality' : 'Create Personality'}</h3>
        <form onSubmit={handleSubmit} className="mt-4 space-y-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-300">Name</label>
            <input
              className="w-full rounded-xl border border-border/60 bg-[#1a0a2e] px-3 py-2 text-sm text-white placeholder:text-muted outline-none transition focus:border-accent"
              value={form.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="Enter personality name"
            />
            {errors.name && <div className="mt-1 text-sm text-rose-200">{errors.name}</div>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-300">Description</label>
            <textarea
              className="min-h-[80px] w-full rounded-xl border border-border/60 bg-[#1a0a2e] px-3 py-2 text-sm text-white placeholder:text-muted outline-none transition focus:border-accent"
              value={form.description}
              onChange={(e) => handleChange('description', e.target.value)}
              placeholder="Brief description"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-300">System Prompt</label>
            <textarea
              className="min-h-[100px] w-full rounded-xl border border-border/60 bg-[#1a0a2e] px-3 py-2 text-sm text-white placeholder:text-muted outline-none transition focus:border-accent"
              value={form.system}
              onChange={(e) => handleChange('system', e.target.value)}
              placeholder="Define the system behavior"
            />
            {errors.system && <div className="mt-1 text-sm text-rose-200">{errors.system}</div>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-300">Base Prompt / Scenario</label>
            <textarea
              className="min-h-[90px] w-full rounded-xl border border-border/60 bg-[#1a0a2e] px-3 py-2 text-sm text-white placeholder:text-muted outline-none transition focus:border-accent"
              value={form.scenario}
              onChange={(e) => handleChange('scenario', e.target.value)}
              placeholder="Scenario or context"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-300">Opening Prompt</label>
            <textarea
              className="min-h-[90px] w-full rounded-xl border border-border/60 bg-[#1a0a2e] px-3 py-2 text-sm text-white placeholder:text-muted outline-none transition focus:border-accent"
              value={form.opening_prompt}
              onChange={(e) => handleChange('opening_prompt', e.target.value)}
              placeholder="Initial assistant message"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-300">Avatar Image</label>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="mt-1 block w-full text-sm text-slate-300 file:mr-3 file:rounded-full file:border-0 file:bg-accent/15 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-slate-300 file:hover:bg-accent/30"
            />
            {preview && (
              <div className="mt-3 overflow-hidden rounded-xl border border-border/60">
                <img src={preview} alt="preview" className="h-24 w-24 object-cover" />
              </div>
            )}
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              className="rounded-lg bg-white/10 px-3 py-2 text-sm text-slate-300 transition hover:bg-white/15"
              onClick={onCancel}
              disabled={saving}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="rounded-lg bg-gradient-to-r from-accent to-accent2 px-3 py-2 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5"
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}