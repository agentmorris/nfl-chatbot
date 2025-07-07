# NFL Player Postgame Interview Chatbot

A web application that simulates a postgame interview with an NFL player who speaks only in vague platitudes and never really answers questions directly.

## Project Overview

This app creates a real-time chat interface where users can "interview" an AI-powered NFL player. The AI is prompted to respond like a typical NFL player in postgame interviews, using familiar phrases like "We just came here to take care of business" and avoiding direct answers to questions.

**Tech Stack:**
- Backend: FastAPI with WebSockets for real-time chat
- Frontend: HTML/CSS/JavaScript (vanilla, no frameworks)
- LLM: Google Gemini API (easily switchable to other providers)
- Deployment: Docker container
- Testing: Runnable locally with Python

## Features

- Real-time chat interface similar to modern chat applications
- Multiple concurrent users with isolated sessions
- NFL player persona with authentic-sounding platitudes
- Clean, simple UI without unnecessary graphics
- Easy deployment to any server with Docker
- Configurable for different LLM providers

## Project Structure

```
nfl-chatbot/
├── app/
│   ├── main.py              # FastAPI application
│   ├── nfl_persona.py       # NFL player prompts and responses
│   ├── templates/
│   │   └── index.html       # Main chat interface
│   └── static/
│       ├── style.css        # Styling
│       └── script.js        # Frontend JavaScript
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── .env.example            # Environment variables template
└── README.md              # This file
```

## Setup Instructions

### Local Development (Recommended for Testing)

1. **Clone/Create the project directory:**
   ```bash
   mkdir nfl-chatbot
   cd nfl-chatbot
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows WSL:
   source venv/bin/activate
   # On Windows Command Prompt:
   # venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

5. **Run the application:**
   ```bash
   cd app
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the app:**
   Open your browser to `http://localhost:8000`

### Docker Deployment

1. **Build and run with Docker Compose:**
   ```bash
   docker compose up --build
   ```

2. **Access the app:**
   Open your browser to `http://your-hostname:8000` or `http://your-ip:8000`

### Production Deployment

For production deployment on your Ubuntu VM:

1. **Copy files to your server**
2. **Create .env file with your Gemini API key**
3. **Run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

The app will be available at `your-hostname.com:8000` alongside your existing Apache setup.

## Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
HOST=0.0.0.0
PORT=8000
```

## Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

## Deployment

### Ubuntu Linux Server Deployment

#### Prerequisites

1. **Install Docker and Docker Compose on Ubuntu:**
   ```bash
   # Update package index
   sudo apt update
   
   # Install Docker
   sudo apt install -y docker.io docker-compose
   
   # Start and enable Docker
   sudo systemctl start docker
   sudo systemctl enable docker
   
   # Add your user to docker group (logout/login required)
   sudo usermod -aG docker $USER
   ```

2. **Open required ports:**
   ```bash
   # Open port 8000 (or your chosen port) in UFW firewall
   sudo ufw allow 8000
   
   # If using iptables instead:
   sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
   ```

#### Deployment Steps

1. **Copy project files to your server:**
   ```bash
   # Using scp from your local machine:
   scp -r nfl-chatbot/ user@your-server-ip:/home/user/
   
   # Or clone if using git:
   git clone your-repo-url nfl-chatbot
   cd nfl-chatbot
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   nano .env  # Add your Gemini API key
   ```

3. **Deploy with Docker:**
   ```bash
   # Build and start the application
   docker-compose up -d --build
   
   # View logs to ensure it's running
   docker-compose logs -f
   ```

4. **Verify deployment:**
   ```bash
   # Check if the container is running
   docker-compose ps
   
   # Test the health endpoint
   curl http://localhost:8000/health
   
   # Or test from another machine
   curl http://your-server-ip:8000/health
   ```

5. **Access your application:**
   - Local: `http://your-server-ip:8000`
   - Domain: `http://yourdomain.com:8000`

#### Managing the Deployment

**Stop the application:**
```bash
docker-compose down
```

**Update and restart:**
```bash
# Pull latest changes (if using git)
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

**View logs:**
```bash
# View current logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f
```

**Change the port:**
Edit `docker-compose.yml` and change the port mapping:
```yaml
ports:
  - "8080:8000"  # This would make it accessible on port 8080
```

#### Running alongside Apache

Since you mentioned Apache is already running on your server:

1. **The app runs on port 8000 by default** (separate from Apache's 80/443)
2. **Users access it directly**: `yourdomain.com:8000`
3. **Optional: Set up Apache reverse proxy** to serve it on a subdomain:
   ```apache
   # In Apache virtual host config
   <VirtualHost *:80>
       ServerName nfl-chat.yourdomain.com
       ProxyPass / http://localhost:8000/
       ProxyPassReverse / http://localhost:8000/
   </VirtualHost>
   ```

#### Troubleshooting

**Port already in use:**
```bash
# Check what's using port 8000
sudo netstat -tlnp | grep :8000

# Change port in docker-compose.yml if needed
```

**Permission denied:**
```bash
# Make sure user is in docker group
groups $USER

# If not, add and restart session:
sudo usermod -aG docker $USER
# Then logout and login again
```

**Container won't start:**
```bash
# Check detailed logs
docker-compose logs nfl-chatbot

# Check container status
docker-compose ps
```

## Customization

### Changing the LLM Provider

The LLM integration is isolated in `app/main.py`. To switch to a different provider:

1. Update the `call_llm()` function in `main.py`
2. Update `requirements.txt` with the new client library
3. Update environment variables as needed

### Modifying the NFL Persona

Edit `app/nfl_persona.py` to:
- Add more example responses
- Adjust the personality
- Add team-specific responses

### Styling Changes

Modify `app/static/style.css` to change the appearance of the chat interface.

## API Endpoints

- `GET /` - Main chat interface
- `WebSocket /ws/{session_id}` - Real-time chat connection

## Troubleshooting

### Common Issues

1. **"Port already in use"**: Change the port in `.env` or docker-compose.yml
2. **Gemini API errors**: Verify your API key and check quotas
3. **WebSocket connection failed**: Ensure firewall allows the port

### Testing Locally

For local testing without Docker:
```bash
cd app
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Viewing Logs

With Docker:
```bash
docker-compose logs -f
```

## Future Enhancements

Potential features to add:
- Player selection (different teams/personalities)
- Question categories (game performance, team strategy, etc.)
- Response variety based on "game outcome"
- Simple admin interface for prompt management

## Support

This app was designed to be simple and focused. For modifications or debugging, the codebase is intentionally minimal and well-commented for easy understanding.