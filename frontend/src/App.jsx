import React, { useState } from 'react';
import PersonalitySelector from './components/PersonalitySelector.jsx';
import SessionSelector from './components/SessionSelector.jsx';
import Chat from './components/Chat.jsx';
import './App.css';

function App() {
  const [selectedPersona, setSelectedPersona] = useState(null);
  const [selectedSession, setSelectedSession] = useState(null);
  const [stage, setStage] = useState('personality'); // 'personality' | 'session' | 'chat'

  const handlePersonaSelected = (persona) => {
    setSelectedPersona(persona);
    setStage('session');
  };

  const handleSessionSelected = (session) => {
    setSelectedSession(session);
    setStage('chat');
  };

  const handleBackToPersonalities = () => {
    setSelectedPersona(null);
    setSelectedSession(null);
    setStage('personality');
  };

  const handleBackToSessions = () => {
    setSelectedSession(null);
    setStage('session');
  };

  return (
    <div className="app">
      {stage === 'personality' && (
        <PersonalitySelector onPersonaSelected={handlePersonaSelected} />
      )}

      {stage === 'session' && (
        <SessionSelector 
          persona={selectedPersona}
          onSessionSelected={handleSessionSelected}
          onBack={handleBackToPersonalities}
        />
      )}

      {stage === 'chat' && (
        <Chat 
          persona={selectedPersona}
          session={selectedSession}
          onBack={handleBackToSessions}
        />
      )}
    </div>
  );
}

export default App;
