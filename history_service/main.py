"""
History Service - Store and retrieve chat history using MongoDB
Manages conversation context for the AI Agent
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime
from pymongo import MongoClient, errors
from bson import json_util

# Configure logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/ai_agent_mvp')
DB_NAME = os.getenv('DB_NAME', 'ai_agent_mvp')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'chat_history')

class HistoryService:
    """History service for storing and retrieving chat sessions"""
    
    def __init__(self):
        try:
            # Initialize MongoDB client
            self.client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
            
            # Check if connection is successful
            self.client.server_info()
            
            # Access database and collection
            self.db = self.client[DB_NAME]
            self.collection = self.db[COLLECTION_NAME]
            
            # Ensure indexes are in place
            self.collection.create_index("chat_id")
            self.collection.create_index("timestamp")
            
            logger.info("MongoDB connected successfully")
            
        except errors.ServerSelectionTimeoutError as e:
            logger.error(f"MongoDB connection error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error initializing MongoDB: {str(e)}")
            raise
    
    def store_interaction(self, chat_id: str, message: str, response: str, source: str, timestamp: str) -> dict:
        """Store a chat interaction"""
        try:
            interaction = {
                'chat_id': chat_id,
                'message': message,
                'response': response,
                'source': source,
                'timestamp': timestamp
            }
            
            self.collection.insert_one(interaction)
            logger.info(f"Interaction stored for chat_id {chat_id}")
            
            return {'success': True, 'message': 'Interaction stored successfully'}
            
        except Exception as e:
            logger.error(f"Error storing interaction: {str(e)}")
            return {'success': False, 'message': 'Failed to store interaction'}
    
    def get_history(self, chat_id: str) -> dict:
        """Retrieve chat history for a specific chat ID"""
        try:
            history_cursor = self.collection.find({'chat_id': chat_id}).sort("timestamp", -1)
            history_list = list(history_cursor)
            logger.info(f"Retrieved {len(history_list)} records for chat_id {chat_id}")
            
            return {'success': True, 'history': json_util.loads(json_util.dumps(history_list))}
            
        except Exception as e:
            logger.error(f"Error retrieving history: {str(e)}")
            return {'success': False, 'message': 'Failed to retrieve history'}

# Initialize the history service
try:
    history_service = HistoryService()
except Exception as e:
    logger.error(f"Failed to initialize history service: {str(e)}")
    history_service = None

@app.route('/')
def home():
    """Service information page"""
    return jsonify({
        'service': 'History Service',
        'status': 'running',
        'endpoints': {
            'POST /history': 'Store chat interaction',
            'GET /history/<chat_id>': 'Retrieve chat history',
            'GET /health': 'Health check'
        },
        'features': [
            'MongoDB storage',
            'Indexing on chat_id and timestamp',
            'Seamless integration with AI Agent'
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/history', methods=['POST'])
def add_history():
    """Store chat history interaction"""
    if not history_service:
        return jsonify({'error': 'History service not available'}), 503
    
    try:
        data = request.get_json()
        if not data or 'chat_id' not in data or 'message' not in data or 'response' not in data:
            return jsonify({'error': 'chat_id, message, and response are required'}), 400
        
        chat_id = data['chat_id']
        message = data['message']
        response = data['response']
        source = data.get('source', 'unknown')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Store interaction
        result = history_service.store_interaction(chat_id, message, response, source, timestamp)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 500
        
    except Exception as e:
        logger.error(f"Add history error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/history/<chat_id>', methods=['GET'])
def get_history(chat_id):
    """Retrieve chat history by chat ID"""
    if not history_service:
        return jsonify({'error': 'History service not available'}), 503
    
    try:
        result = history_service.get_history(chat_id)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
        
    except Exception as e:
        logger.error(f"Get history error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    is_healthy = history_service is not None
    
    return jsonify({
        'status': 'healthy' if is_healthy else 'unhealthy',
        'service': 'history_service',
        'mongodb': 'connected' if is_healthy else 'disconnected',
        'timestamp': datetime.now().isoformat()
    }), 200 if is_healthy else 503

if __name__ == '__main__':
    logger.info("Starting History Service on port 8003...")
    app.run(host='0.0.0.0', port=8003, debug=True)

