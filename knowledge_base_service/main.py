"""
Knowledge Base Service - Store, retrieve and search domain-specific knowledge
Uses ChromaDB for vector embeddings and retrieval
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import chromadb
from chromadb.config import Settings
import os
import logging
from datetime import datetime
import uuid
import json
from typing import List, Dict, Any
import hashlib

# Configure logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH', './chroma_db')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class KnowledgeBaseService:
    """Knowledge Base service using ChromaDB for vector storage and retrieval"""
    
    def __init__(self):
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=CHROMA_DB_PATH,
                settings=Settings(
                    allow_reset=True,
                    anonymized_telemetry=False
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="knowledge_base",
                metadata={"description": "AI Agent MVP Knowledge Base"}
            )
            
            # Initialize with sample data if empty
            if self.collection.count() == 0:
                self._initialize_sample_data()
            
            logger.info(f"Knowledge Base initialized with {self.collection.count()} documents")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise
    
    def _initialize_sample_data(self):
        """Initialize with sample knowledge base data"""
        sample_documents = [
            {
                "id": "ai_definition",
                "text": "Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines that can think, learn, and adapt like humans. AI systems can perform tasks that typically require human intelligence, such as visual perception, speech recognition, decision-making, and language translation.",
                "metadata": {"category": "AI Basics", "source": "knowledge_base"}
            },
            {
                "id": "machine_learning",
                "text": "Machine Learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It uses algorithms and statistical models to identify patterns in data and make predictions or decisions.",
                "metadata": {"category": "AI Basics", "source": "knowledge_base"}
            },
            {
                "id": "deep_learning",
                "text": "Deep Learning is a subset of machine learning that uses artificial neural networks with multiple layers (deep neural networks) to model and understand complex patterns in data. It's particularly effective for tasks like image recognition, natural language processing, and speech recognition.",
                "metadata": {"category": "AI Basics", "source": "knowledge_base"}
            },
            {
                "id": "neural_networks",
                "text": "Neural Networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) that process information using a connectionist approach. Neural networks can learn and model non-linear and complex relationships between inputs and outputs.",
                "metadata": {"category": "AI Basics", "source": "knowledge_base"}
            },
            {
                "id": "natural_language_processing",
                "text": "Natural Language Processing (NLP) is a branch of artificial intelligence that helps computers understand, interpret, and manipulate human language. NLP combines computational linguistics with statistical, machine learning, and deep learning models to enable computers to process human language in text and speech forms.",
                "metadata": {"category": "AI Applications", "source": "knowledge_base"}
            },
            {
                "id": "computer_vision",
                "text": "Computer Vision is a field of artificial intelligence that trains computers to interpret and understand visual information from the world. It involves acquiring, processing, analyzing, and understanding digital images and videos to extract meaningful information.",
                "metadata": {"category": "AI Applications", "source": "knowledge_base"}
            },
            {
                "id": "reinforcement_learning",
                "text": "Reinforcement Learning is a type of machine learning where an agent learns to make decisions by taking actions in an environment to maximize cumulative reward. The agent learns through trial and error, receiving feedback from its actions.",
                "metadata": {"category": "AI Methods", "source": "knowledge_base"}
            },
            {
                "id": "supervised_learning",
                "text": "Supervised Learning is a machine learning paradigm where algorithms learn from labeled training data to make predictions or decisions on new, unseen data. The algorithm learns the mapping between input features and target labels.",
                "metadata": {"category": "AI Methods", "source": "knowledge_base"}
            },
            {
                "id": "unsupervised_learning",
                "text": "Unsupervised Learning is a machine learning paradigm where algorithms find hidden patterns or structures in data without labeled examples. It includes techniques like clustering, dimensionality reduction, and association rule learning.",
                "metadata": {"category": "AI Methods", "source": "knowledge_base"}
            },
            {
                "id": "ai_ethics",
                "text": "AI Ethics involves the moral principles and values that guide the development and deployment of artificial intelligence systems. It addresses issues like bias, fairness, transparency, privacy, accountability, and the societal impact of AI technologies.",
                "metadata": {"category": "AI Ethics", "source": "knowledge_base"}
            }
        ]
        
        # Add documents to ChromaDB
        for doc in sample_documents:
            self.collection.add(
                documents=[doc["text"]],
                metadatas=[doc["metadata"]],
                ids=[doc["id"]]
            )
        
        logger.info(f"Initialized knowledge base with {len(sample_documents)} sample documents")
    
    def query(self, query_text: str, n_results: int = 3) -> Dict[str, Any]:
        """Query the knowledge base for relevant information"""
        try:
            # Perform semantic search
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            if not results['documents'] or not results['documents'][0]:
                return {
                    'found': False,
                    'answer': None,
                    'sources': [],
                    'query': query_text
                }
            
            # Format the response
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0]
            
            # Check if the best match is good enough (distance threshold)
            best_distance = distances[0] if distances else 1.0
            similarity_threshold = 0.7  # Adjust as needed
            
            if best_distance > similarity_threshold:
                return {
                    'found': False,
                    'answer': None,
                    'sources': [],
                    'query': query_text,
                    'reason': 'No sufficiently similar documents found'
                }
            
            # Combine top results into a comprehensive answer
            answer = self._format_answer(documents, metadatas, query_text)
            
            sources = []
            for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                sources.append({
                    'rank': i + 1,
                    'content': doc[:200] + "..." if len(doc) > 200 else doc,
                    'metadata': metadata,
                    'similarity_score': 1 - distance  # Convert distance to similarity
                })
            
            return {
                'found': True,
                'answer': answer,
                'sources': sources,
                'query': query_text,
                'total_results': len(documents)
            }
            
        except Exception as e:
            logger.error(f"Error querying knowledge base: {str(e)}")
            return {
                'found': False,
                'answer': None,
                'sources': [],
                'query': query_text,
                'error': str(e)
            }
    
    def _format_answer(self, documents: List[str], metadatas: List[Dict], query: str) -> str:
        """Format multiple documents into a coherent answer"""
        if not documents:
            return "I couldn't find relevant information in the knowledge base."
        
        # Use the most relevant document as the primary answer
        primary_answer = documents[0]
        
        # If there are multiple relevant documents, provide additional context
        if len(documents) > 1:
            additional_context = []
            for doc, metadata in zip(documents[1:], metadatas[1:]):
                category = metadata.get('category', 'General')
                additional_context.append(f"[{category}] {doc[:150]}...")
            
            if additional_context:
                primary_answer += "\n\nAdditional related information:\n" + "\n".join(additional_context)
        
        return primary_answer
    
    def ingest_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new document to the knowledge base"""
        try:
            # Generate ID if not provided
            doc_id = document.get('id')
            if not doc_id:
                # Generate ID from content hash
                content_hash = hashlib.md5(document['text'].encode()).hexdigest()
                doc_id = f"doc_{content_hash[:8]}"
            
            # Prepare metadata
            metadata = document.get('metadata', {})
            metadata.update({
                'ingested_at': datetime.now().isoformat(),
                'source': metadata.get('source', 'user_upload')
            })
            
            # Add to ChromaDB
            self.collection.add(
                documents=[document['text']],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            logger.info(f"Document {doc_id} added to knowledge base")
            
            return {
                'success': True,
                'document_id': doc_id,
                'message': 'Document successfully added to knowledge base'
            }
            
        except Exception as e:
            logger.error(f"Error ingesting document: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to add document to knowledge base'
            }
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base collection"""
        try:
            count = self.collection.count()
            
            # Get sample documents to analyze categories
            sample_results = self.collection.get(limit=100, include=['metadatas'])
            categories = {}
            sources = {}
            
            for metadata in sample_results.get('metadatas', []):
                category = metadata.get('category', 'Unknown')
                source = metadata.get('source', 'Unknown')
                
                categories[category] = categories.get(category, 0) + 1
                sources[source] = sources.get(source, 0) + 1
            
            return {
                'total_documents': count,
                'categories': categories,
                'sources': sources,
                'collection_name': self.collection.name
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {
                'total_documents': 0,
                'categories': {},
                'sources': {},
                'error': str(e)
            }

# Initialize the knowledge base service
try:
    kb_service = KnowledgeBaseService()
except Exception as e:
    logger.error(f"Failed to initialize knowledge base service: {str(e)}")
    kb_service = None

@app.route('/')
def home():
    """Service information page"""
    stats = kb_service.get_collection_stats() if kb_service else {}
    
    return jsonify({
        'service': 'Knowledge Base Service',
        'status': 'running',
        'endpoints': {
            'POST /query': 'Search knowledge base with embedded query',
            'POST /ingest': 'Add documents to knowledge base',
            'GET /stats': 'Get collection statistics',
            'GET /health': 'Health check'
        },
        'stats': stats,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/query', methods=['POST'])
def query_knowledge_base():
    """Search the knowledge base for relevant information"""
    if not kb_service:
        return jsonify({'error': 'Knowledge base service not available'}), 503
    
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        query_text = data['query']
        n_results = data.get('n_results', 3)
        
        if not query_text.strip():
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Perform the query
        result = kb_service.query(query_text, n_results)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Query endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/ingest', methods=['POST'])
def ingest_document():
    """Add a new document to the knowledge base"""
    if not kb_service:
        return jsonify({'error': 'Knowledge base service not available'}), 503
    
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Document text is required'}), 400
        
        # Validate document structure
        if not data['text'].strip():
            return jsonify({'error': 'Document text cannot be empty'}), 400
        
        # Ingest the document
        result = kb_service.ingest_document(data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Ingest endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get knowledge base statistics"""
    if not kb_service:
        return jsonify({'error': 'Knowledge base service not available'}), 503
    
    try:
        stats = kb_service.get_collection_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Stats endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    is_healthy = kb_service is not None
    
    return jsonify({
        'status': 'healthy' if is_healthy else 'unhealthy',
        'service': 'knowledge_base_service',
        'chroma_db': 'connected' if is_healthy else 'disconnected',
        'timestamp': datetime.now().isoformat()
    }), 200 if is_healthy else 503

if __name__ == '__main__':
    logger.info("Starting Knowledge Base Service on port 8001...")
    app.run(host='0.0.0.0', port=8001, debug=True)
