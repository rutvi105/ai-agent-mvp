# Manual Setup Guide (Without Docker)

This guide helps you run the AI Agent MVP project manually without Docker.

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

## Step-by-Step Setup

### 1. Install Dependencies for All Services

Open Command Prompt or PowerShell and run these commands:

```bash
# Install dependencies for Chat Service
cd chat_service
pip install -r requirements.txt
cd ..

# Install dependencies for Knowledge Base Service
cd knowledge_base_service
pip install -r requirements.txt
cd ..

# Install dependencies for Search Service
cd search_service
pip install -r requirements.txt
cd ..

# Install dependencies for History Service
cd history_service
pip install -r requirements.txt
cd ..

# Install requests for testing scripts
pip install requests
```

### 2. Start Services (Use 4 separate terminal windows)

**Terminal 1 - Knowledge Base Service:**
```bash
cd knowledge_base_service
python main.py
```

**Terminal 2 - Search Service:**
```bash
cd search_service
python main.py
```

**Terminal 3 - History Service:**
```bash
cd history_service
python main.py
```

**Terminal 4 - Chat Service:**
```bash
cd chat_service
python main.py
```

### 3. Test the System

In a new terminal, run:
```bash
python test_system.py
```

### 4. Access the Frontend

Open `frontend/index.html` in your web browser to use the chat interface.

## Quick Test Commands

You can test individual services using curl or PowerShell:

### Test Chat Service:
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -ContentType "application/json" -Body '{"message": "What is AI?", "chat_id": "test123"}'
$response
```

### Test Knowledge Base:
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8001/query" -Method Post -ContentType "application/json" -Body '{"query": "artificial intelligence"}'
$response
```

### Test Search Service:
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8002/search?query=AI" -Method Get
$response
```

## Troubleshooting

- **Port conflicts**: If you get port errors, change the ports in the service files
- **MongoDB not available**: The history service will show errors but other services will work
- **ChromaDB issues**: The knowledge base service will fall back to basic responses

## Expected Behavior

1. Knowledge Base Service will start with sample AI data
2. Chat Service will coordinate between all services
3. Search Service will provide web search results
4. History Service will attempt to connect to MongoDB (may fail without MongoDB installed)

Even if some services have issues, the main chat functionality should work!
