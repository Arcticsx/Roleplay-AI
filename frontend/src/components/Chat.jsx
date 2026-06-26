import React, { useState, useEffect, useRef } from 'react';
import { api } from '../api';
import './Chat.css';

function Chat({ persona, session, onBack }) {
  const [messages, setMessages] = useState([]);
  const [fullMessages, setFullMessages] = useState([]);
  const [sessionId, setSessionId] = useState(session?.id || null);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    initializeChat();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeChat = async () => {
    setInitializing(true);
    try {
      const data = await api.loadSession(persona.key, session);
      setMessages(data.messages || []);
      setFullMessages(data.full_messages || []);
      setSessionId(session?.id || null);
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

    try {
      const data = await api.sendMessage(
        persona.key,
        messages,
        fullMessages,
        sessionId,
        userInput
      );

      setMessages(data.messages);
      setFullMessages(data.full_messages);
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message');
    }

    setLoading(false);
  };

  const handleSaveSession = async () => {
    if (fullMessages.length === 0) {
      alert('No messages to save');
      return;
    }

    setLoading(true);
    try {
      const data = await api.saveSession(persona.key, fullMessages, sessionId);
      setSessionId(data.session_id);
      alert('Session saved successfully!');
    } catch (error) {
      console.error('Failed to save session:', error);
      alert('Failed to save session');
    }
    setLoading(false);
  };

  if (initializing) {
    return (
      <div className="chat">
        <p>Loading chat...</p>
      </div>
    );
  }

  return (
    <div className="chat">
      <div className="chat-header">
        <button className="btn-back" onClick={onBack}>
          ← BACK TO SESSIONS
        </button>
        <div className="chat-info">
          <h1>{persona.name}</h1>
          <p>Session ID: {sessionId || 'New Session'}</p>
        </div>
        <button 
          className="btn-save" 
          onClick={handleSaveSession}
          disabled={loading || fullMessages.length === 0}
        >
          SAVE SESSION
        </button>
      </div>

      <div className="chat-messages">
        {messages.map((msg, index) => {
          if (msg.role === 'system') return null;
          
          return (
            <div 
              key={index} 
              className={`message message-${msg.role}`}
            >
              <div className="message-role">
                {msg.role === 'user' ? '> USER' : `> ${persona.name.toUpperCase()}`}
              </div>
              <div className="message-content">{msg.content}</div>
            </div>
          );
        })}
        
        {loading && (
          <div className="message message-assistant">
            <div className="message-role">{`> ${persona.name.toUpperCase()}`}</div>
            <div className="message-content">...</div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSendMessage}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={loading}
          autoFocus
        />
        <button type="submit" disabled={loading || !input.trim()}>
          SEND
        </button>
      </form>
    </div>
  );
}

export default Chat;
