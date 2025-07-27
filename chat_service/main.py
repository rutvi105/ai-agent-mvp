"""
Chat Service - Main orchestrator for AI Agent MVP
Handles user interactions and coordinates between microservices
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import os
import logging
from datetime import datetime
import uuid
import json

# Configure logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Service URLs
KB_SERVICE_URL = os.getenv('KB_SERVICE_URL', 'http://localhost:8001')
SEARCH_SERVICE_URL = os.getenv('SEARCH_SERVICE_URL', 'http://localhost:8002')
HISTORY_SERVICE_URL = os.getenv('HISTORY_SERVICE_URL', 'http://localhost:8003')

# OpenAI API Key (optional)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class ChatOrchestrator:
    """Main orchestrator class for handling chat logic"""
    
    def __init__(self):
        self.kb_service_url = KB_SERVICE_URL
        self.search_service_url = SEARCH_SERVICE_URL
        self.history_service_url = HISTORY_SERVICE_URL
    
    def process_message(self, message: str, chat_id: str = None) -> dict:
        """
        Process user message through the AI agent pipeline
        1. Check knowledge base
        2. Fall back to search if needed
        3. Store interaction in history
        """
        if not chat_id:
            chat_id = str(uuid.uuid4())
        
        try:
            # Step 1: Query knowledge base
            kb_response = self._query_knowledge_base(message)
            
            if kb_response and kb_response.get('found'):
                response_text = kb_response.get('answer', 'I found some information but cannot format it properly.')
                source = 'knowledge_base'
                logger.info(f"Knowledge base answered query: {message[:50]}...")
            else:
                # Step 2: Fall back to web search
                search_response = self._perform_web_search(message)
                if search_response:
                    response_text = self._format_search_response(search_response, message)
                    source = 'web_search'
                    logger.info(f"Web search answered query: {message[:50]}...")
                else:
                    response_text = "I'm sorry, I couldn't find information about that topic. Could you try rephrasing your question?"
                    source = 'fallback'
            
            # Step 3: Store interaction in history
            self._store_interaction(chat_id, message, response_text, source)
            
            return {
                'response': response_text,
                'chat_id': chat_id,
                'source': source,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                'response': "I'm experiencing technical difficulties. Please try again later.",
                'chat_id': chat_id,
                'source': 'error',
                'timestamp': datetime.now().isoformat()
            }
    
    def _query_knowledge_base(self, query: str) -> dict:
        """Query the knowledge base service"""
        try:
            response = requests.post(
                f"{self.kb_service_url}/query",
                json={'query': query},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            logger.error(f"Knowledge base service error: {str(e)}")
        return None
    
    def _perform_web_search(self, query: str) -> dict:
        """Perform web search using search service"""
        try:
            response = requests.get(
                f"{self.search_service_url}/search",
                params={'query': query},
                timeout=15
            )
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            logger.error(f"Search service error: {str(e)}")
        return None
    
    def _format_search_response(self, search_data: dict, original_query: str) -> str:
        """Format search results into a readable response"""
        if not search_data or not search_data.get('results'):
            return "I couldn't find relevant information on the web."
        
        results = search_data.get('results', [])[:3]  # Top 3 results
        
        response = f"Based on web search results for '{original_query}':\n\n"
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            snippet = result.get('snippet', 'No description available')
            url = result.get('url', '')
            
            response += f"{i}. **{title}**\n"
            response += f"   {snippet}\n"
            if url:
                response += f"   Source: {url}\n"
            response += "\n"
        
        return response.strip()
    
    def _store_interaction(self, chat_id: str, message: str, response: str, source: str):
        """Store interaction in history service"""
        try:
            requests.post(
                f"{self.history_service_url}/history",
                json={
                    'chat_id': chat_id,
                    'message': message,
                    'response': response,
                    'source': source,
                    'timestamp': datetime.now().isoformat()
                },
                timeout=5
            )
        except requests.RequestException as e:
            logger.error(f"History service error: {str(e)}")
    
    def get_chat_history(self, chat_id: str) -> dict:
        """Retrieve chat history"""
        try:
            response = requests.get(
                f"{self.history_service_url}/history/{chat_id}",
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            logger.error(f"Error retrieving chat history: {str(e)}")
        return {'history': []}

# Initialize orchestrator
orchestrator = ChatOrchestrator()

@app.route('/')
def home():
    """Simple web interface for testing"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Agent MVP - Chat Service</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
            .chat-box { background: white; height: 400px; overflow-y: auto; padding: 15px; border: 1px solid #ddd; margin: 10px 0; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user-message { background: #007bff; color: white; text-align: right; }
            .ai-message { background: #e9ecef; color: #333; }
            input[type="text"] { width: 70%; padding: 10px; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
            .status { margin: 10px 0; font-style: italic; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AI Agent MVP - Chat Interface</h1>
            <div class="status">Status: Chat Service Running ✅</div>
            <div id="chat-box" class="chat-box"></div>
            <div>
                <input type="text" id="message-input" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">Send</button>
            </div>
            <div class="status">
                <small>
                    Services: KB Service, Search Service, History Service<br>
                    Endpoints: POST /chat, GET /chat/{chat_id}
                </small>
            </div>
        </div>
        
        <script>
            let chatId = Math.random().toString(36).substring(7);
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
            
            function sendMessage() {
                const input = document.getElementById('message-input');
                const message = input.value.trim();
                if (!message) return;
                
                displayMessage(message, 'user-message');
                input.value = '';
                
                fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message, chat_id: chatId})
                })
                .then(response => response.json())
                .then(data => {
                    displayMessage(data.response + ' [Source: ' + data.source + ']', 'ai-message');
                })
                .catch(error => {
                    displayMessage('Error: ' + error.message, 'ai-message');
                });
            }
            
            function displayMessage(message, className) {
                const chatBox = document.getElementById('chat-box');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + className;
                messageDiv.textContent = message;
                chatBox.appendChild(messageDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        message = data['message']
        chat_id = data.get('chat_id')
        
        # Process the message
        result = orchestrator.process_message(message, chat_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/chat/<chat_id>', methods=['GET'])
def get_chat_history(chat_id):
    """Get chat history for a specific chat ID"""
    try:
        history = orchestrator.get_chat_history(chat_id)
        return jsonify(history)
    except Exception as e:
        logger.error(f"Get history error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'chat_service',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/services/status', methods=['GET'])
def services_status():
    """Check status of all dependent services"""
    services = {}
    
    # Check Knowledge Base Service
    try:
        response = requests.get(f"{KB_SERVICE_URL}/health", timeout=5)
        services['knowledge_base'] = 'healthy' if response.status_code == 200 else 'unhealthy'
    except:
        services['knowledge_base'] = 'unreachable'
    
    # Check Search Service
    try:
        response = requests.get(f"{SEARCH_SERVICE_URL}/health", timeout=5)
        services['search'] = 'healthy' if response.status_code == 200 else 'unhealthy'
    except:
        services['search'] = 'unreachable'
    
    # Check History Service
    try:
        response = requests.get(f"{HISTORY_SERVICE_URL}/health", timeout=5)
        services['history'] = 'healthy' if response.status_code == 200 else 'unhealthy'
    except:
        services['history'] = 'unreachable'
    
    return jsonify({
        'chat_service': 'healthy',
        'dependent_services': services,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("Starting Chat Service on port 8000...")
    app.run(host='0.0.0.0', port=8000, debug=True)
