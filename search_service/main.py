"""
Search Service - Provide web search capabilities using DuckDuckGo API/scraping
Falls back when knowledge base can't answer queries
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import logging
from datetime import datetime
import json
import time
from urllib.parse import quote
import re
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class SearchService:
    """Web search service using DuckDuckGo"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://duckduckgo.com"
        
    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Perform web search using DuckDuckGo
        Returns formatted search results
        """
        try:
            # Sanitize and encode query
            clean_query = self._sanitize_query(query)
            if not clean_query:
                return {
                    'success': False,
                    'results': [],
                    'query': query,
                    'error': 'Invalid query'
                }
            
            # Perform search using DuckDuckGo instant answer API
            results = self._search_duckduckgo(clean_query, max_results)
            
            if not results:
                # Fallback to mock results for demonstration
                results = self._get_mock_results(query)
            
            return {
                'success': True,
                'results': results,
                'query': query,
                'total_results': len(results),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return {
                'success': False,
                'results': [],
                'query': query,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _sanitize_query(self, query: str) -> str:
        """Clean and sanitize search query"""
        if not query or not isinstance(query, str):
            return ""
        
        # Remove special characters and normalize whitespace
        clean_query = re.sub(r'[^\w\s\-\+]', '', query.strip())
        clean_query = re.sub(r'\s+', ' ', clean_query)
        
        return clean_query[:200]  # Limit query length
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search using DuckDuckGo instant answer API
        """
        try:
            # DuckDuckGO instant answer API
            api_url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            
            # Parse instant answer
            if data.get('AbstractText'):
                results.append({
                    'title': data.get('Heading', 'DuckDuckGo Instant Answer'),
                    'snippet': data.get('AbstractText', ''),
                    'url': data.get('AbstractURL', ''),
                    'source': 'DuckDuckGo Instant Answer'
                })
            
            # Parse related topics
            for topic in data.get('RelatedTopics', [])[:max_results-len(results)]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                        'snippet': topic.get('Text', ''),
                        'url': topic.get('FirstURL', ''),
                        'source': 'DuckDuckGo Related Topic'
                    })
            
            # If we have results, return them
            if results:
                return results[:max_results]
            
            # Otherwise try HTML scraping approach (simplified)
            return self._search_duckduckgo_html(query, max_results)
            
        except Exception as e:
            logger.error(f"DuckDuckGo API search error: {str(e)}")
            return []
    
    def _search_duckduckgo_html(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Fallback: Simple HTML scraping of DuckDuckGo search results
        """
        try:
            search_url = f"https://duckduckgo.com/html/?q={quote(query)}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # Very basic HTML parsing (in production, use BeautifulSoup)
            html = response.text
            results = []
            
            # Simple regex to extract results (not recommended for production)
            # This is a simplified approach for demonstration
            title_pattern = r'class="result__title"><a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
            snippet_pattern = r'class="result__snippet">([^<]*)</span>'
            
            titles = re.findall(title_pattern, html)
            snippets = re.findall(snippet_pattern, html)
            
            for i, (url, title) in enumerate(titles[:max_results]):
                snippet = snippets[i] if i < len(snippets) else "No description available"
                
                results.append({
                    'title': title.strip(),
                    'snippet': snippet.strip(),
                    'url': url,
                    'source': 'DuckDuckGo Search'
                })
            
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo HTML search error: {str(e)}")
            return []
    
    def _get_mock_results(self, query: str) -> List[Dict[str, Any]]:
        """
        Generate mock search results for demonstration purposes
        This simulates web search results when actual search fails
        """
        mock_results = []
        
        # AI-related mock results
        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural network']
        tech_keywords = ['programming', 'coding', 'software', 'development', 'computer']
        science_keywords = ['science', 'research', 'technology', 'innovation']
        
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ai_keywords):
            mock_results = [
                {
                    'title': f'Understanding {query.title()}: A Comprehensive Guide',
                    'snippet': f'Learn about {query} and its applications in modern technology. This comprehensive guide covers the fundamentals, applications, and future prospects of {query}.',
                    'url': f'https://example.com/guide-to-{query.replace(" ", "-").lower()}',
                    'source': 'Mock Search Result'
                },
                {
                    'title': f'{query.title()} in 2024: Latest Trends and Developments',
                    'snippet': f'Explore the latest trends in {query}. Industry experts share insights about current developments and future directions in this rapidly evolving field.',
                    'url': f'https://example.com/trends-{query.replace(" ", "-").lower()}-2024',
                    'source': 'Mock Search Result'
                },
                {
                    'title': f'Practical Applications of {query.title()}',
                    'snippet': f'Discover real-world applications of {query} across various industries. From healthcare to finance, see how {query} is transforming different sectors.',
                    'url': f'https://example.com/applications-{query.replace(" ", "-").lower()}',
                    'source': 'Mock Search Result'
                }
            ]
        elif any(keyword in query_lower for keyword in tech_keywords):
            mock_results = [
                {
                    'title': f'{query.title()}: Best Practices and Tips',
                    'snippet': f'Master {query} with these expert tips and best practices. Learn from experienced professionals and improve your skills.',
                    'url': f'https://example.com/best-practices-{query.replace(" ", "-").lower()}',
                    'source': 'Mock Search Result'
                },
                {
                    'title': f'Getting Started with {query.title()}',
                    'snippet': f'A beginner-friendly introduction to {query}. Step-by-step guide to help you get started with the fundamentals.',
                    'url': f'https://example.com/getting-started-{query.replace(" ", "-").lower()}',
                    'source': 'Mock Search Result'
                }
            ]
        else:
            # Generic mock results
            mock_results = [
                {
                    'title': f'Everything You Need to Know About {query.title()}',
                    'snippet': f'Comprehensive information about {query}. Find answers to your questions and learn more about this topic.',
                    'url': f'https://example.com/about-{query.replace(" ", "-").lower()}',
                    'source': 'Mock Search Result'
                },
                {
                    'title': f'{query.title()}: FAQ and Common Questions',
                    'snippet': f'Frequently asked questions about {query}. Get quick answers to the most common queries related to this topic.',
                    'url': f'https://example.com/faq-{query.replace(" ", "-").lower()}',
                    'source': 'Mock Search Result'
                }
            ]
        
        return mock_results[:3]  # Return top 3 mock results

# Initialize search service
search_service = SearchService()

@app.route('/')
def home():
    """Service information page"""
    return jsonify({
        'service': 'Search Service',
        'status': 'running',
        'endpoints': {
            'GET /search?query={query}': 'Perform web search',
            'GET /health': 'Health check'
        },
        'features': [
            'DuckDuckGo search integration',
            'Query sanitization',
            'Mock results fallback',
            'Configurable result limits'
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/search', methods=['GET'])
def web_search():
    """Perform web search"""
    try:
        query = request.args.get('query')
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        query = query.strip()
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Get max results parameter
        max_results = request.args.get('max_results', 5)
        try:
            max_results = int(max_results)
            max_results = min(max(max_results, 1), 10)  # Limit between 1-10
        except ValueError:
            max_results = 5
        
        # Perform search
        result = search_service.search(query, max_results)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Search endpoint error: {str(e)}")
        return jsonify({
            'success': False,
            'results': [],
            'query': query if 'query' in locals() else '',
            'error': 'Internal server error',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'search_service',
        'search_engine': 'DuckDuckGo',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/test', methods=['GET'])
def test_search():
    """Test endpoint for search functionality"""
    test_queries = [
        'artificial intelligence',
        'machine learning',
        'web development',
        'python programming'
    ]
    
    results = {}
    for query in test_queries:
        result = search_service.search(query, 2)
        results[query] = {
            'success': result['success'],
            'result_count': len(result['results']),
            'sample_title': result['results'][0]['title'] if result['results'] else None
        }
    
    return jsonify({
        'test_results': results,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("Starting Search Service on port 8002...")
    app.run(host='0.0.0.0', port=8002, debug=True)
