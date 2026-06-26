# Setup Guide

## Backend Setup

1. Navigate to the backend directory and activate virtual environment:
```bash
cd backend
# On Windows:
..\.venv\Scripts\activate
```

2. Install dependencies (if not already done):
```bash
pip install -r ../requirements.txt
```

3. Start the backend server:
```bash
python app/main.py
```

The backend will run on `http://localhost:8000`

## Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the Vite development server:
```bash
npm run dev
```

The frontend will automatically open at `http://localhost:3000`

## Usage

1. **Create or Select a Personality**: On the first screen, create a new AI personality or select an existing one
2. **Choose a Session**: Start a new conversation or resume a previous session
3. **Chat**: Type messages and interact with the AI personality
4. **Save**: Click "SAVE SESSION" to persist the conversation

## Troubleshooting

- Make sure the backend is running before starting the frontend
- Check that port 8000 (backend) and 3000 (frontend) are available
- If you get CORS errors, verify the backend has CORS middleware configured
