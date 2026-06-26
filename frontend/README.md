# AI Roleplay Frontend

Modern React frontend built with Vite for the AI Roleplay chatbot.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Make sure the backend is running on `http://localhost:8000`

3. Start the development server:
```bash
npm run dev
```

The app will open at `http://localhost:3000`

## Features

- **Personality Selection**: View existing personalities or create new ones
- **Session Management**: Start new conversations or resume previous sessions
- **Chat Interface**: Terminal-style chat with save functionality

## Structure

```
src/
├── components/
│   ├── PersonalitySelector.jsx   # Select or create personalities
│   ├── SessionSelector.jsx       # Choose session to load
│   └── Chat.jsx                  # Main chat interface
├── api.js                        # API calls to backend
├── App.jsx                       # Main app component
└── index.jsx                     # Entry point
```

## Tech Stack

- **Vite** - Fast build tool and dev server
- **React 18** - Latest React with modern features
- **No deprecated dependencies** - Clean, modern stack
