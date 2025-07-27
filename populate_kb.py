#!/usr/bin/env python3
"""
Script to populate the knowledge base with sample data
Run this after the services are up and running
"""

import requests
import json
import time
import sys

# Configuration
KB_SERVICE_URL = "http://localhost:8001"
SAMPLE_DATA_FILE = "sample_knowledge_base.json"

def wait_for_service(url, timeout=60):
    """Wait for a service to be available"""
    print(f"Waiting for service at {url}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Service at {url} is ready!")
                return True
        except requests.RequestException:
            pass
        
        time.sleep(2)
    
    print(f"❌ Service at {url} is not available after {timeout} seconds")
    return False

def populate_knowledge_base():
    """Populate the knowledge base with sample data"""
    try:
        # Load sample data
        with open(SAMPLE_DATA_FILE, 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
        
        print(f"📚 Populating knowledge base with {len(sample_data)} documents...")
        
        # Send each document to the knowledge base service
        success_count = 0
        for doc in sample_data:
            try:
                response = requests.post(
                    f"{KB_SERVICE_URL}/ingest",
                    json=doc,
                    timeout=10
                )
                
                if response.status_code == 201:
                    print(f"✅ Added document: {doc['id']}")
                    success_count += 1
                else:
                    print(f"❌ Failed to add document {doc['id']}: {response.status_code}")
                    print(f"   Response: {response.text}")
            
            except requests.RequestException as e:
                print(f"❌ Error adding document {doc['id']}: {str(e)}")
        
        print(f"\n📊 Successfully added {success_count}/{len(sample_data)} documents")
        return success_count > 0
        
    except FileNotFoundError:
        print(f"❌ Sample data file '{SAMPLE_DATA_FILE}' not found")
        return False
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in '{SAMPLE_DATA_FILE}'")
        return False
    except Exception as e:
        print(f"❌ Error populating knowledge base: {str(e)}")
        return False

def main():
    """Main function"""
    print("🤖 AI Agent MVP - Knowledge Base Population Script")
    print("=" * 50)
    
    # Wait for knowledge base service to be ready
    if not wait_for_service(KB_SERVICE_URL):
        print("❌ Cannot connect to knowledge base service. Make sure it's running.")
        sys.exit(1)
    
    # Populate the knowledge base
    if populate_knowledge_base():
        print("\n✅ Knowledge base population completed successfully!")
        
        # Test a query
        print("\n🧪 Testing knowledge base with a sample query...")
        try:
            test_response = requests.post(
                f"{KB_SERVICE_URL}/query",
                json={"query": "What is artificial intelligence?"},
                timeout=10
            )
            
            if test_response.status_code == 200:
                result = test_response.json()
                if result.get('found'):
                    print("✅ Test query successful!")
                    print(f"   Answer preview: {result['answer'][:100]}...")
                else:
                    print("⚠️  Test query returned no results")
            else:
                print(f"❌ Test query failed: {test_response.status_code}")
        
        except requests.RequestException as e:
            print(f"❌ Test query error: {str(e)}")
        
    else:
        print("\n❌ Knowledge base population failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
