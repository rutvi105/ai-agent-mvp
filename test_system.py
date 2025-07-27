#!/usr/bin/env python3
"""
Quick test script to validate the AI Agent MVP system
Tests all microservices and their integration
"""

import requests
import time
import json
import sys

# Service URLs
SERVICES = {
    'chat': 'http://localhost:8000',
    'knowledge_base': 'http://localhost:8001', 
    'search': 'http://localhost:8002',
    'history': 'http://localhost:8003'
}

def test_service_health(service_name, url):
    """Test if a service is healthy"""
    print(f"Testing {service_name} service at {url}...")
    try:
        response = requests.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ {service_name} service is healthy")
            return True
        else:
            print(f"❌ {service_name} service unhealthy: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ {service_name} service unreachable: {str(e)}")
        return False

def test_knowledge_base():
    """Test knowledge base functionality"""
    print("\n🧪 Testing Knowledge Base Service...")
    
    # Test query
    try:
        response = requests.post(
            f"{SERVICES['knowledge_base']}/query",
            json={"query": "What is artificial intelligence?"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('found'):
                print("✅ Knowledge base query successful")
                print(f"   Answer preview: {data['answer'][:100]}...")
                return True
            else:
                print("⚠️  Knowledge base returned no results")
                return False
        else:
            print(f"❌ Knowledge base query failed: {response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Knowledge base query error: {str(e)}")
        return False

def test_search_service():
    """Test search service functionality"""
    print("\n🧪 Testing Search Service...")
    
    try:
        response = requests.get(
            f"{SERVICES['search']}/search",
            params={"query": "artificial intelligence"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('results'):
                print("✅ Search service working")
                print(f"   Found {len(data['results'])} results")
                return True
            else:
                print("⚠️  Search service returned no results")
                return False
        else:
            print(f"❌ Search service failed: {response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Search service error: {str(e)}")
        return False

def test_history_service():
    """Test history service functionality"""
    print("\n🧪 Testing History Service...")
    
    test_chat_id = "test_chat_123"
    
    # Test storing history
    try:
        response = requests.post(
            f"{SERVICES['history']}/history",
            json={
                "chat_id": test_chat_id,
                "message": "Test message",
                "response": "Test response",
                "source": "test",
                "timestamp": "2024-01-01T00:00:00Z"
            },
            timeout=10
        )
        
        if response.status_code == 201:
            print("✅ History storage successful")
            
            # Test retrieving history
            response = requests.get(
                f"{SERVICES['history']}/history/{test_chat_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('history'):
                    print("✅ History retrieval successful")
                    return True
                else:
                    print("⚠️  History retrieval returned no data")
                    return False
            else:
                print(f"❌ History retrieval failed: {response.status_code}")
                return False
        else:
            print(f"❌ History storage failed: {response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ History service error: {str(e)}")
        return False

def test_chat_integration():
    """Test the full chat integration"""
    print("\n🧪 Testing Chat Service Integration...")
    
    try:
        response = requests.post(
            f"{SERVICES['chat']}/chat",
            json={
                "message": "What is machine learning?",
                "chat_id": "integration_test"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('response'):
                print("✅ Chat integration successful")
                print(f"   Response source: {data.get('source', 'unknown')}")
                print(f"   Response preview: {data['response'][:100]}...")
                return True
            else:
                print("⚠️  Chat integration returned empty response")
                return False
        else:
            print(f"❌ Chat integration failed: {response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Chat integration error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🤖 AI Agent MVP - System Testing")
    print("=" * 50)
    
    # Test all service health
    print("🏥 Health Checks:")
    health_results = []
    for service_name, url in SERVICES.items():
        health_results.append(test_service_health(service_name, url))
    
    if not all(health_results):
        print("\n❌ Some services are not healthy. Cannot proceed with integration tests.")
        sys.exit(1)
    
    print("\n✅ All services are healthy!")
    
    # Test individual services
    print("\n🔧 Individual Service Tests:")
    service_tests = [
        test_knowledge_base(),
        test_search_service(), 
        test_history_service()
    ]
    
    # Test integration
    print("\n🔗 Integration Tests:")
    integration_result = test_chat_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Health checks: {sum(health_results)}/{len(health_results)} passed")
    print(f"   Service tests: {sum(service_tests)}/{len(service_tests)} passed")
    print(f"   Integration test: {'✅ PASSED' if integration_result else '❌ FAILED'}")
    
    if all(health_results) and all(service_tests) and integration_result:
        print("\n🎉 All tests passed! System is ready for use.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
