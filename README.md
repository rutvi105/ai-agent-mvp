# AI Agent MVP Challenge

## Overview
This challenge involves building a minimal AI assistant that can chat with users, answer questions using a knowledge base, fall back to web search when needed, and maintain conversation history.

## System Architecture

The system consists of 4 microservices:

1. **Chat Service (Orchestrator)** - Main entry point that manages user interactions and coordinates between services
2. **Knowledge Base Service** - Store, retrieve and search domain-specific knowledge
3. **Search Service** - Provide web search capabilities when knowledge base can't answer
4. **History Service** - Maintain conversation context across interactions

## Data Flow
1. User sends message to Chat Service
2. Chat Service checks with Knowledge Base Service
3. If answer found, return it
4. If not, fall back to Search Service
5. All interactions stored via History Service

## Technical Stack
- **Backend Framework**: Flask or FastAPI
- **Database**: MongoDB (for chat history)
- **Vector Store**: ChromaDB (for embeddings and retrieval)
- **Search**: DuckDuckGo API/scraping
- **LLM Integration**: OpenAI API, Google Gemini, or mock implementation

## API Endpoints

### Chat Service
- `POST /chat`: Submit user query and receive response
- `GET /chat/{chat_id}`: Retrieve chat history

### Knowledge Base Service
- `POST /query`: Search knowledge base with embedded query
- `POST /ingest`: Add documents to knowledge base

### Search Service
- `GET /search?query={query}`: Perform web search

### History Service
- `POST /history`: Create/update chat history
- `GET /history/{chat_id}`: Remove chat history

## Evaluation Criteria
- **Functionality**: Does the system respond correctly to queries?
- **Architecture**: Are microservices properly separated with clear APIs?
- **Code Quality**: Is the code well-structured and documented?
- **Error Handling**: Does the system gracefully handle failures?

## Deliverables
- Source code for all microservices
- README with setup and run instructions
- Brief documentation of API endpoints
- Sample knowledge base content for testing

## Setup and Installation

### Prerequisites
- Python 3.8+
- Docker and Docker Compose
- MongoDB
- OpenAI API key (optional)

### Installation Steps

1. Clone the repository
```bash
git clone <repository-url>
cd ai-agent-mvp
```

2. Create environment file
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Build and run with Docker Compose
```bash
docker-compose up --build
```

4. Populate knowledge base
```bash
python populate_kb.py
```

### Manual Setup (Without Docker)

1. Install dependencies for each service
```bash
# For each service directory
pip install -r requirements.txt
```

2. Start MongoDB and ChromaDB

3. Run each service
```bash
# Terminal 1 - Chat Service
cd chat_service
python main.py

# Terminal 2 - Knowledge Base Service
cd knowledge_base_service
python main.py

# Terminal 3 - Search Service
cd search_service
python main.py

# Terminal 4 - History Service
cd history_service
python main.py
```

## Testing

### Test Chat Functionality
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is artificial intelligence?", "chat_id": "test123"}'
```

### Test Knowledge Base
```bash
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"query": "artificial intelligence"}'
```

### Test Search Service
```bash
curl "http://localhost:8002/search?query=latest AI news"
```

### Test History Service
```bash
curl -X POST http://localhost:8003/history \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "test123", "message": "Hello", "response": "Hi there!", "timestamp": "2025-01-01T00:00:00Z"}'
```

## Project Structure
```
ai-agent-mvp/
├── chat_service/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── knowledge_base_service/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── search_service/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── history_service/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── populate_kb.py
├── sample_knowledge_base.json
└── README.md
```

## Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (optional)
- `MONGODB_URL`: MongoDB connection string
- `CHAT_SERVICE_URL`: Chat service URL
- `KB_SERVICE_URL`: Knowledge base service URL
- `SEARCH_SERVICE_URL`: Search service URL
- `HISTORY_SERVICE_URL`: History service URL

## Troubleshooting

### Common Issues
1. **Port conflicts**: Make sure ports 8000-8003 are available
2. **MongoDB connection**: Ensure MongoDB is running and accessible
3. **API keys**: Check if API keys are set correctly in .env file
4. **Dependencies**: Install all required packages using pip

### Logs
Check service logs using:
```bash
docker-compose logs -f [service_name]
```

## Contributing
1. Follow PEP 8 style guidelines
2. Add proper error handling
3. Include unit tests
4. Update documentation for any changes
