# NFL Player Postgame Interview Chatbot

A web application that simulates a postgame interview with an NFL player who speaks only in vague platitudes and never really answers questions directly.

## Quick Setup

1. **Get a Gemini API key**: Go to https://makersuite.google.com/app/apikey
2. **Copy .env.example to .env** and add your API key
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Run locally**: `cd app && uvicorn main:app --reload --host 0.0.0.0 --port 8000`
5. **Open**: http://localhost:8000

## Features

- Real-time chat with WebSockets
- NFL player persona with authentic platitudes
- Multi-user support with isolated sessions
- Easy LLM provider switching
- Docker deployment ready

## Tech Stack

- Backend: FastAPI with WebSockets
- Frontend: HTML/CSS/JavaScript (vanilla)
- LLM: Google Gemini API
- Deployment: Docker

This project was generated automatically. For detailed documentation, see the original README artifact.