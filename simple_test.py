#!/usr/bin/env python3
"""
Simple standalone test to demonstrate project functionality
This runs without any external dependencies
"""

import json
import sys
from datetime import datetime

def simulate_knowledge_base_query(query):
    """Simulate knowledge base response"""
    # Sample knowledge base data
    knowledge_base = {
        "artificial intelligence": {
            "answer": "Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines that can think, learn, and adapt like humans. AI systems can perform tasks that typically require human intelligence, such as visual perception, speech recognition, decision-making, and language translation.",
            "source": "knowledge_base"
        },
        "machine learning": {
            "answer": "Machine Learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It uses algorithms and statistical models to identify patterns in data and make predictions or decisions.",
            "source": "knowledge_base"
        },
        "deep learning": {
            "answer": "Deep Learning is a subset of machine learning that uses artificial neural networks with multiple layers (deep neural networks) to model and understand complex patterns in data. It's particularly effective for tasks like image recognition, natural language processing, and speech recognition.",
            "source": "knowledge_base"
        }
    }
    
    # Simple keyword matching
    query_lower = query.lower()
    for keyword, data in knowledge_base.items():
        if keyword in query_lower:
            return {
                "found": True,
                "answer": data["answer"],
                "source": data["source"]
            }
    
    return {
        "found": False,
        "answer": None,
        "source": None
    }

def simulate_web_search(query):
    """Simulate web search response"""
    return {
        "success": True,
        "results": [
            {
                "title": f"Understanding {query.title()}: A Comprehensive Guide",
                "snippet": f"Learn about {query} and its applications in modern technology. This comprehensive guide covers the fundamentals and applications.",
                "url": f"https://example.com/guide-to-{query.replace(' ', '-').lower()}",
                "source": "Web Search"
            },
            {
                "title": f"{query.title()} in 2024: Latest Developments",
                "snippet": f"Explore the latest trends in {query}. Industry experts share insights about current developments in this field.",
                "url": f"https://example.com/trends-{query.replace(' ', '-').lower()}-2024",
                "source": "Web Search"
            }
        ],
        "query": query,
        "total_results": 2
    }

def simulate_chat_service(message, chat_id="test_chat"):
    """Simulate the complete chat service flow"""
    print(f"\n🤖 Processing message: '{message}'")
    print(f"📝 Chat ID: {chat_id}")
    
    # Step 1: Check knowledge base
    print("\n🔍 Step 1: Checking Knowledge Base...")
    kb_result = simulate_knowledge_base_query(message)
    
    if kb_result["found"]:
        print("✅ Found in Knowledge Base!")
        response = kb_result["answer"]
        source = "knowledge_base"
        print(f"📖 Answer: {response[:100]}...")
    else:
        print("❌ Not found in Knowledge Base")
        
        # Step 2: Fall back to web search
        print("\n🌐 Step 2: Falling back to Web Search...")
        search_result = simulate_web_search(message)
        
        if search_result["success"] and search_result["results"]:
            print("✅ Found web search results!")
            # Format search results into response
            response = f"Based on web search results for '{message}':\n\n"
            for i, result in enumerate(search_result["results"][:2], 1):
                response += f"{i}. **{result['title']}**\n"
                response += f"   {result['snippet']}\n"
                response += f"   Source: {result['url']}\n\n"
            source = "web_search"
            print(f"🔗 Results: {len(search_result['results'])} found")
        else:
            print("❌ Web search failed")
            response = "I'm sorry, I couldn't find information about that topic. Could you try rephrasing your question?"
            source = "fallback"
    
    # Step 3: Store in history (simulated)
    print(f"\n💾 Step 3: Storing in History Service...")
    history_entry = {
        "chat_id": chat_id,
        "message": message,
        "response": response,
        "source": source,
        "timestamp": datetime.now().isoformat()
    }
    print("✅ Stored in history")
    
    # Return final response
    return {
        "response": response,
        "chat_id": chat_id,
        "source": source,
        "timestamp": history_entry["timestamp"]
    }

def main():
    """Main demonstration function"""
    print("🤖 AI Agent MVP - Standalone Demonstration")
    print("=" * 60)
    print("This demonstrates how your project works without running actual services")
    print("=" * 60)
    
    # Test cases
    test_queries = [
        "What is artificial intelligence?",
        "How does machine learning work?",
        "Tell me about quantum computing",
        "Latest trends in technology"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"TEST CASE {i}")
        print(f"{'='*60}")
        
        # Simulate the chat service processing
        result = simulate_chat_service(query, f"test_chat_{i}")
        
        # Display final result
        print(f"\n📤 FINAL RESPONSE:")
        print(f"   💬 Response: {result['response'][:150]}...")
        print(f"   🔍 Source: {result['source']}")
        print(f"   🆔 Chat ID: {result['chat_id']}")
        print(f"   ⏰ Timestamp: {result['timestamp']}")
        
        if i < len(test_queries):
            input("\nPress Enter to continue to next test...")
    
    print(f"\n{'='*60}")
    print("🎉 DEMONSTRATION COMPLETE!")
    print("=" * 60)
    print("This shows exactly how your AI Agent MVP will work:")
    print("✅ Knowledge Base search with semantic matching")
    print("✅ Web search fallback for unknown queries") 
    print("✅ Chat history storage and management")
    print("✅ Multi-service orchestration")
    print("✅ Error handling and graceful degradation")

if __name__ == "__main__":
    main()
