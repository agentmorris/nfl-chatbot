#!/usr/bin/env python3
"""
NFL Chatbot Project Setup Script
Run this script to generate all project files automatically.
"""

import os
import sys

def create_directory(path):
    """Create directory if it doesn't exist"""
    os.makedirs(path, exist_ok=True)
    print(f"Created directory: {path}")

def write_file(filepath, content):
    """Write content to file"""
    dirname = os.path.dirname(filepath)
    if dirname:  # Only create directory if dirname is not empty
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created file: {filepath}")

def main():
    print("Setting up NFL Chatbot project...")
    print("=" * 50)
    
    # Create directory structure
    create_directory("app/templates")
    create_directory("app/static")
    
    # app/main.py
    main_py = '''import os
import uuid
import asyncio
from typing import Dict, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import google.generativeai as genai
from dotenv import load_dotenv
import logging

from nfl_persona import NFL_SYSTEM_PROMPT, NFL_EXAMPLES

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="NFL Player Interview Chatbot")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# Store active connections and chat histories
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.chat_histories: Dict[str, list] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.chat_histories[session_id] = []
        logger.info(f"New connection: {session_id}")
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.chat_histories:
            del self.chat_histories[session_id]
        logger.info(f"Disconnected: {session_id}")
    
    async def send_message(self, session_id: str, message: str):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_text(message)
    
    def add_to_history(self, session_id: str, role: str, content: str):
        if session_id not in self.chat_histories:
            self.chat_histories[session_id] = []
        self.chat_histories[session_id].append({"role": role, "content": content})

manager = ConnectionManager()

async def call_llm(session_id: str, user_message: str) -> str:
    """Call the Gemini API with the NFL player persona"""
    try:
        # Build conversation history
        history = manager.chat_histories.get(session_id, [])
        
        # Create the prompt with system message and conversation history
        full_prompt = NFL_SYSTEM_PROMPT + "\\n\\n" + NFL_EXAMPLES + "\\n\\n"
        
        # Add conversation history
        if history:
            full_prompt += "Previous conversation:\\n"
            for msg in history[-10:]:  # Keep last 10 messages for context
                role = "Reporter" if msg["role"] == "user" else "Player"
                full_prompt += f"{role}: {msg['content']}\\n"
        
        # Add current question
        full_prompt += f"\\nReporter: {user_message}\\nPlayer:"
        
        # Generate response
        response = await asyncio.to_thread(model.generate_content, full_prompt)
        
        # Extract the text response
        if response.text:
            return response.text.strip()
        else:
            return "You know, that's a great question. We're just focused on taking it one day at a time and doing what's best for the team."
            
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        return "We don't really focus on things we can't control. We just go out there and play our game."

@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    """Serve the main chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """Handle WebSocket connections for real-time chat"""
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive message from client
            user_message = await websocket.receive_text()
            
            # Add user message to history
            manager.add_to_history(session_id, "user", user_message)
            
            # Get AI response
            ai_response = await call_llm(session_id, user_message)
            
            # Add AI response to history
            manager.add_to_history(session_id, "assistant", ai_response)
            
            # Send response back to client
            await manager.send_message(session_id, ai_response)
            
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        manager.disconnect(session_id)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)'''
    
    # app/nfl_persona.py
    nfl_persona_py = '''"""
NFL Player persona for the chatbot.
Contains the system prompt and example responses that define the character.
"""

NFL_SYSTEM_PROMPT = """You are an NFL player being interviewed after a game. You should respond exactly like NFL players do in real postgame interviews - speaking only in vague platitudes, clichés, and non-answers that don't actually address the questions being asked.

Key characteristics of your responses:
- Never give specific details about plays, strategies, or what actually happened
- Always deflect to team-focused, generic statements
- Use phrases about "taking it one game at a time," "focusing on what we can control," etc.
- Avoid controversy or specific criticism
- Keep responses relatively short (1-3 sentences typically)
- Sound humble but confident
- Never break character - always stay in "media-trained NFL player" mode

Common themes to use:
- Team first mentality
- Taking things one day/game at a time
- Focusing on what you can control
- Not listening to outside noise/media
- Giving credit to teammates and coaches
- "Executing the game plan"
- "Doing your job"
- Preparation and hard work"""

NFL_EXAMPLES = """Example interviews:

Reporter: "What went wrong on that interception in the third quarter?"
Player: "You know, that's football. Things happen out there and we just have to move on to the next play. Credit to their defense for making a play."

Reporter: "Do you think the coaching staff made the right call on fourth down?"
Player: "Coach puts us in position to succeed and we just have to go out there and execute. That's on us as players to make the plays when they're there."

Reporter: "How do you feel about facing your former team next week?"
Player: "We're just focused on taking it one game at a time. This week is about preparing and doing our job. Everything else is just noise."

Reporter: "What's your response to critics saying the offense looked sluggish?"
Player: "We don't really pay attention to what people are saying outside the building. We know what we need to work on and we'll get back to the drawing board this week."

Reporter: "Can you walk us through what you were thinking on that touchdown pass?"
Player: "The coaches put together a great game plan and my teammates made plays. I just try to get the ball to our playmakers and let them do what they do."

Reporter: "Is there frustration in the locker room after three straight losses?"
Player: "We're a resilient group. We stick together through everything and we know we have what it takes. We just need to keep working and stay focused on the process."

Reporter: "What needs to change for the team to turn things around?"
Player: "We just need to keep doing what we've been doing in practice and trust the process. The wins will come if we stay focused on doing our job."'''
    
    # app/templates/index.html
    index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NFL Player Interview</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="app-container">
        <header class="app-header">
            <h1>🏈 Postgame Interview</h1>
            <p>Ask questions to our star player after today's big game</p>
        </header>
        
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="message ai-message">
                    <div class="message-content">
                        <strong>Player:</strong> Thanks for having me. Ready for your questions.
                    </div>
                </div>
            </div>
            
            <div class="chat-input-container">
                <div class="input-wrapper">
                    <input 
                        type="text" 
                        id="messageInput" 
                        placeholder="Ask your question (press Enter to send)..."
                        autocomplete="off"
                    >
                    <button id="sendButton" type="button">Send</button>
                </div>
                <div class="connection-status" id="connectionStatus">
                    <span class="status-indicator" id="statusIndicator"></span>
                    <span id="statusText">Connecting...</span>
                </div>
            </div>
        </div>
    </div>

    <script src="/static/script.js"></script>
</body>
</html>'''
    
    # CSS and JS content (truncated for space - full versions in files)
    style_css = '''/* Reset and base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: #333;
    height: 100vh;
    overflow: hidden;
}

.app-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-width: 800px;
    margin: 0 auto;
    background: white;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
}

.app-header {
    background: #2c3e50;
    color: white;
    padding: 20px;
    text-align: center;
    border-bottom: 3px solid #3498db;
}

.app-header h1 {
    font-size: 1.8rem;
    margin-bottom: 8px;
    font-weight: 600;
}

.app-header p {
    font-size: 0.9rem;
    opacity: 0.9;
    font-weight: 300;
}

.chat-container {
    display: flex;
    flex-direction: column;
    flex: 1;
    overflow: hidden;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    background: #f8f9fa;
    scroll-behavior: smooth;
}

.message {
    margin-bottom: 16px;
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.message-content {
    max-width: 80%;
    padding: 12px 16px;
    border-radius: 18px;
    line-height: 1.4;
    font-size: 0.95rem;
}

.user-message .message-content {
    background: #3498db;
    color: white;
    margin-left: auto;
    border-bottom-right-radius: 4px;
}

.ai-message .message-content {
    background: white;
    color: #2c3e50;
    border: 1px solid #e1e8ed;
    border-bottom-left-radius: 4px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.ai-message .message-content strong {
    color: #e67e22;
    font-weight: 600;
}

.user-message .message-content strong {
    color: #ecf0f1;
    font-weight: 600;
}

.chat-input-container {
    background: white;
    border-top: 1px solid #e1e8ed;
    padding: 16px 20px;
}

.input-wrapper {
    display: flex;
    gap: 8px;
    margin-bottom: 8px;
}

#messageInput {
    flex: 1;
    padding: 12px 16px;
    border: 2px solid #e1e8ed;
    border-radius: 24px;
    font-size: 0.95rem;
    outline: none;
    transition: border-color 0.2s ease;
}

#messageInput:focus {
    border-color: #3498db;
}

#messageInput:disabled {
    background-color: #f5f5f5;
    cursor: not-allowed;
}

#sendButton {
    padding: 12px 24px;
    background: #3498db;
    color: white;
    border: none;
    border-radius: 24px;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s ease, transform 0.1s ease;
}

#sendButton:hover:not(:disabled) {
    background: #2980b9;
    transform: translateY(-1px);
}

#sendButton:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
    transform: none;
}

.connection-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
    color: #7f8c8d;
}

.status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #e74c3c;
    transition: background-color 0.3s ease;
}

.status-indicator.connected {
    background: #27ae60;
}

.status-indicator.connecting {
    background: #f39c12;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.typing-indicator {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 12px 16px;
    color: #7f8c8d;
    font-style: italic;
    font-size: 0.9rem;
}

.typing-dots {
    display: flex;
    gap: 2px;
}

.typing-dots span {
    width: 4px;
    height: 4px;
    background: #bdc3c7;
    border-radius: 50%;
    animation: typingDots 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typingDots {
    0%, 80%, 100% {
        transform: scale(0.8);
        opacity: 0.5;
    }
    40% {
        transform: scale(1);
        opacity: 1;
    }
}

/* Scrollbar styling */
.chat-messages::-webkit-scrollbar {
    width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
    background: #f1f1f1;
}

.chat-messages::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
    background: #a1a1a1;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    .app-container {
        height: 100vh;
        border-radius: 0;
    }
    
    .app-header {
        padding: 16px;
    }
    
    .app-header h1 {
        font-size: 1.5rem;
    }
    
    .chat-messages {
        padding: 16px;
    }
    
    .message-content {
        max-width: 90%;
        font-size: 0.9rem;
    }
    
    .chat-input-container {
        padding: 12px 16px;
    }
    
    #messageInput {
        font-size: 16px; /* Prevents zoom on iOS */
    }
}'''
    
    script_js = '''class NFLChatbot {
    constructor() {
        this.websocket = null;
        this.sessionId = this.generateSessionId();
        this.isConnected = false;
        this.isTyping = false;
        
        this.initializeElements();
        this.attachEventListeners();
        this.connect();
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }
    
    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusText = document.getElementById('statusText');
    }
    
    attachEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Handle page visibility changes to reconnect if needed
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && !this.isConnected) {
                this.connect();
            }
        });
    }
    
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.sessionId}`;
        
        this.updateConnectionStatus('connecting', 'Connecting...');
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                this.isConnected = true;
                this.updateConnectionStatus('connected', 'Connected');
                this.enableInput();
                console.log('WebSocket connected');
            };
            
            this.websocket.onmessage = (event) => {
                this.handleMessage(event.data);
            };
            
            this.websocket.onclose = (event) => {
                this.isConnected = false;
                this.updateConnectionStatus('disconnected', 'Disconnected');
                this.disableInput();
                console.log('WebSocket closed:', event);
                
                // Attempt to reconnect after a delay
                setTimeout(() => {
                    if (!this.isConnected) {
                        this.connect();
                    }
                }, 3000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus('error', 'Connection error');
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.updateConnectionStatus('error', 'Connection failed');
        }
    }
    
    updateConnectionStatus(status, text) {
        this.statusIndicator.className = `status-indicator ${status}`;
        this.statusText.textContent = text;
    }
    
    enableInput() {
        this.messageInput.disabled = false;
        this.sendButton.disabled = false;
        this.messageInput.focus();
    }
    
    disableInput() {
        this.messageInput.disabled = true;
        this.sendButton.disabled = true;
    }
    
    sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message || !this.isConnected || this.isTyping) {
            return;
        }
        
        // Add user message to chat
        this.addMessage('user', message);
        
        // Clear input
        this.messageInput.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Send message via WebSocket
        try {
            this.websocket.send(message);
        } catch (error) {
            console.error('Failed to send message:', error);
            this.hideTypingIndicator();
            this.addMessage('ai', 'Sorry, there was an error sending your message. Please try again.');
        }
    }
    
    handleMessage(message) {
        this.hideTypingIndicator();
        this.addMessage('ai', message);
    }
    
    addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (type === 'user') {
            messageContent.innerHTML = `<strong>You:</strong> ${this.escapeHtml(content)}`;
        } else {
            messageContent.innerHTML = `<strong>Player:</strong> ${this.escapeHtml(content)}`;
        }
        
        messageDiv.appendChild(messageContent);
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.scrollToBottom();
    }
    
    showTypingIndicator() {
        if (this.isTyping) return;
        
        this.isTyping = true;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai-message typing-message';
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <span>Player is typing</span>
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        if (!this.isTyping) return;
        
        this.isTyping = false;
        
        const typingMessage = this.chatMessages.querySelector('.typing-message');
        if (typingMessage) {
            typingMessage.remove();
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new NFLChatbot();
});'''
    
    # Other config files
    requirements_txt = '''fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
jinja2==3.1.2
python-multipart==0.0.6
python-dotenv==1.0.0
google-generativeai==0.3.2
aiofiles==23.2.1'''
    
    dockerfile = '''FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY .env* ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \\
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]'''
    
    docker_compose_yml = '''version: '3.8'

services:
  nfl-chatbot:
    build: .
    ports:
      - "${PORT:-8000}:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - HOST=0.0.0.0
      - PORT=8000
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s'''
    
    env_example = '''# Copy this file to .env and fill in your actual values

# Google Gemini API Key (required)
# Get yours at: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Server configuration
HOST=0.0.0.0
PORT=8000'''
    
    readme_md = '''# NFL Player Postgame Interview Chatbot

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

This project was generated automatically. For detailed documentation, see the original README artifact.'''
    
    # Write all files
    write_file("app/main.py", main_py)
    write_file("app/nfl_persona.py", nfl_persona_py)
    write_file("app/templates/index.html", index_html)
    write_file("app/static/style.css", style_css)
    write_file("app/static/script.js", script_js)
    write_file("requirements.txt", requirements_txt)
    write_file("Dockerfile", dockerfile)
    write_file("docker-compose.yml", docker_compose_yml)
    write_file(".env.example", env_example)
    write_file("README.md", readme_md)
    
    print("\n" + "=" * 50)
    print("✅ Project setup complete!")
    print("\nNext steps:")
    print("1. Copy .env.example to .env and add your Gemini API key")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run locally: cd app && uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("4. Open http://localhost:8000 in your browser")
    print("\nFor Docker deployment: docker-compose up --build")

if __name__ == "__main__":
    main()