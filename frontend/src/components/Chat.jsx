import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../api';
import { ArrowUpIcon } from 'lucide-react';

function Chat({ persona, session, onBack }) {
  const { personaKey, sessionId: routeSessionId } = useParams();
  const [messages, setMessages] = useState([]);
  const [context, setContext] = useState([]);
  const [sessionId, setSessionId] = useState(session?.id || routeSessionId || null);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    setSessionId(session?.id || routeSessionId || null);
  }, [session?.id, routeSessionId]);

  useEffect(() => {
    if (persona?.key) {
        initializeChat();
    }
  }, []); 

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeChat = async () => {
    if (!persona?.key) return;
    const activeSession = session || (routeSessionId ? { id: parseInt(routeSessionId) } : null);
    setInitializing(true);
    setMessages([]);
    setContext([]);
    try {
        const data = await api.loadSession(persona.key, activeSession);
        console.log("loadSession response:", data);
        setMessages(data.messages || []);
        setContext(data.context || []);
        setSessionId(activeSession?.id || null);
    } catch (error) {
        console.error('Failed to load session:', error);
        alert('Failed to load chat session');
    }
    setInitializing(false);
  };
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    const userInput = input.trim();
    setInput('');
    setLoading(true);

    const optimisticMessages = [...messages, { role: 'user', content: userInput }];
    setMessages(optimisticMessages);

    try {
      const data = await api.sendMessage(persona.key, messages, context, sessionId, userInput);
      setMessages(data.messages);
      setContext(data.context);

      const saveData = await api.saveSession(persona.key, data.messages, data.context, sessionId);
      setSessionId(saveData.session_id);

    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message');
    }

    setLoading(false);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleSaveSession = async () => {
    if (context.length === 0) {
      alert('No messages to save');
      return;
    }
    setLoading(true);
    try {
      const data = await api.saveSession(persona.key, messages, context, sessionId);
      setSessionId(data.session_id);
      alert('Session saved successfully!');
    } catch (error) {
      console.error('Failed to save session:', error);
      alert('Failed to save session');
    }
    setLoading(false);
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
    const textarea = e.target;
    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  if (initializing) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bg text-text">
        <p className="text-muted">Loading chat...</p>
      </div>
    );
  }

  return (
    <>
      {/* Purple-themed scrollbar styles */}
      <style>{`
        .scrollbar-themed::-webkit-scrollbar {
          width: 6px;
        }
        .scrollbar-themed::-webkit-scrollbar-track {
          background: transparent;
        }
        .scrollbar-themed::-webkit-scrollbar-thumb {
          background: #7c3aed; /* purple-600 */
          border-radius: 3px;
        }
        .scrollbar-themed::-webkit-scrollbar-thumb:hover {
          background: #a78bfa; /* purple-400 */
        }
        .scrollbar-themed {
          scrollbar-width: thin;
          scrollbar-color: #7c3aed transparent;
        }
      `}</style>

      <div className="mx-auto flex h-full max-w-5xl flex-col px-4 py-4 sm:px-6 lg:px-8">
        <div className="mb-4 flex items-center gap-3 rounded-2xl border border-border/60 bg-surface/70 px-4 py-3 shadow-lg shadow-black/20">
          <button className="rounded-full border border-border/60 bg-white/5 px-3 py-1.5 text-sm text-muted transition hover:bg-white/10 hover:text-white" onClick={onBack}>
            ← Back
          </button>
          <div className="flex-1">
            <div className="text-base font-semibold text-text">{persona.name}</div>
            <div className="text-sm text-muted">Session #{sessionId || 'New'}</div>
          </div>
        </div>

        <div className="scrollbar-themed mb-4 flex-1 overflow-y-auto rounded-2xl border border-border/50 bg-surface/60 p-4 shadow-inner shadow-black/20">
          <div className="flex flex-col gap-4">
            {messages.map((msg, index) => {
              if (msg.role === 'system') return null;
              const isUser = msg.role === 'user';
              const roleLabel = isUser ? 'You' : persona.name;

              return (
                <div key={index} className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-7 ${isUser ? 'ml-auto bg-emerald-500/15 text-white' : 'bg-white/5 text-slate-200'}`}>
                  <div className={`mb-1 text-[11px] font-semibold uppercase tracking-[0.2em] ${isUser ? 'text-sky-300' : 'text-emerald-200'}`}>{roleLabel}</div>
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                </div>
              );
            })}

            {loading && (
              <div className="max-w-[80%] rounded-2xl bg-white/5 px-4 py-3 text-sm leading-7 text-slate-200">
                <div className="mb-1 text-[11px] font-semibold uppercase tracking-[0.2em] text-emerald-200">{persona.name}</div>
                <div className="animate-pulse text-muted">…</div>
              </div>
            )}
          </div>
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSendMessage} className="flex items-end gap-2 rounded-2xl border border-border/40 bg-surface/70 p-3 shadow-lg shadow-black/20">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Type your message… (Shift+Enter for new line)"
            disabled={loading}
            autoFocus
            className="max-h-[200px] flex-1 resize-none bg-transparent px-2 py-2 text-sm text-text outline-none placeholder:text-muted overflow-y-auto"
          />
          <button
            type={loading ? 'button' : 'submit'}
            disabled={loading || !input.trim()}
            className="shrink-0 rounded-full border border-border/40 p-1.5 text-white transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="currentColor"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-label="Stop"
              >
                <title>Stop</title>
                <rect x="6" y="6" width="12" height="12" />
              </svg>
            ) : (
              <ArrowUpIcon size={20} />
            )}
          </button>
        </form>
      </div>
    </>
  );
}

export default Chat;