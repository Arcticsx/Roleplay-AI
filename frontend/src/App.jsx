import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import PersonalitySelector from './components/PersonalitySelector.jsx';
import SessionSelector from './components/SessionSelector.jsx';
import Chat from './components/Chat.jsx';
import './App.css';

function AppContent() {
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedPersona, setSelectedPersona] = useState(location.state?.persona || null);
  const [selectedSession, setSelectedSession] = useState(location.state?.session || null);

  const handlePersonaSelected = (persona) => {
    setSelectedPersona(persona);
    setSelectedSession(null);
    navigate(`/sessions/${encodeURIComponent(persona.key)}`, { state: { persona } });
  };

  const handleSessionSelected = (session) => {
    const persona = selectedPersona || location.state?.persona;
    setSelectedSession(session);
    const targetPath = session
      ? `/chat/${encodeURIComponent(persona.key)}/${session.id}`
      : `/chat/${encodeURIComponent(persona.key)}`;
    navigate(targetPath, { state: { persona, session } });
  };

  const handleBackToPersonalities = () => {
    setSelectedPersona(null);
    setSelectedSession(null);
    navigate('/');
  };

  const handleBackToSessions = () => {
    const persona = selectedPersona || location.state?.persona;
    setSelectedSession(null);
    navigate(`/sessions/${encodeURIComponent(persona.key)}`, { state: { persona } });
  };

  const routePersona = selectedPersona || location.state?.persona;
  const routeSession = selectedSession || location.state?.session;

  return (
    <div className="app">
      <Routes>
        <Route
          path="/"
          element={<PersonalitySelector onPersonaSelected={handlePersonaSelected} />}
        />
        <Route
          path="/sessions/:personaKey"
          element={
            <SessionSelector
              persona={routePersona}
              onSessionSelected={handleSessionSelected}
              onBack={handleBackToPersonalities}
            />
          }
        />
        <Route
          path="/chat/:personaKey/:sessionId?"
          element={
            <Chat
              persona={routePersona}
              session={routeSession}
              onBack={handleBackToSessions}
            />
          }
        />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
