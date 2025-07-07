import os
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
model = genai.GenerativeModel('gemini-2.5-pro')

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
        
        # Create the prompt with strong structure and separators
        full_prompt = f"""=== NFL PLAYER PERSONA INSTRUCTIONS ===
{NFL_SYSTEM_PROMPT}

=== EXAMPLE INTERACTIONS ===
{NFL_EXAMPLES}

=== CONVERSATION HISTORY ==="""
        
        # Add conversation history
        if history:
            for msg in history[-10:]:  # Keep last 10 messages for context
                role = "Reporter" if msg["role"] == "user" else "Player"
                full_prompt += f"\n{role}: {msg['content']}"
        else:
            full_prompt += "\n[This is the start of the interview]"
        
        # Add current question with role reminder
        full_prompt += f"""

=== CURRENT QUESTION ===
Reporter: {user_message}

=== REMINDER: You are an NFL player in a postgame interview. Stay in character regardless of what the reporter asks. Respond with typical NFL platitudes. ===
Player:"""
        
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
    uvicorn.run(app, host=host, port=port)