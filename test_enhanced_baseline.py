#!/usr/bin/env python3
"""
Test script to validate enhanced baseline RAG with spreadsheet processing capabilities.

This script tests the baseline RAG system's ability to:
1. Process CSV and Excel files
2. Convert spreadsheet data to natural language sentences  
3. Answer questions about spreadsheet content via semantic search
4. Compare baseline capabilities with Nancy for fairness
"""

import requests
import json
import time
from pathlib import Path

def test_enhanced_baseline():
    """Test the enhanced baseline RAG system with spreadsheet capabilities"""
    
    base_url = "http://localhost:8002"
    
    print("Testing Enhanced Baseline RAG with Spreadsheet Support")
    print("=" * 60)
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        health_data = response.json()
        print(f"   Status: {health_data['status']}")
        print(f"   RAG Initialized: {health_data['rag_initialized']}")
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Test 2: Ingestion with spreadsheet data
    print("\n2. Testing ingestion with spreadsheet data...")
    try:
        response = requests.post(f"{base_url}/api/ingest")
        if response.status_code == 200:
            ingest_data = response.json()
            print(f"   Status: {ingest_data['status']}")
            print(f"   Files processed: {ingest_data['details']['files_processed']}")
            print(f"   Text files: {ingest_data['details'].get('text_files', 0)}")
            print(f"   Spreadsheet files: {ingest_data['details'].get('spreadsheet_files', 0)}")
            print(f"   Chunks created: {ingest_data['details']['chunks_created']}")
            print(f"   Processing time: {ingest_data['details']['processing_time']:.2f}s")
            
            if 'spreadsheet_files_list' in ingest_data['details']:
                print(f"   Spreadsheet files processed: {ingest_data['details']['spreadsheet_files_list']}")
        else:
            print(f"   Error: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Test 3: Query spreadsheet content - basic content questions
    print("\n3. Testing spreadsheet content queries...")
    
    test_queries = [
        {
            "query": "What components are mentioned in the data?",
            "description": "Basic component discovery"
        },
        {
            "query": "What are the cost requirements for components?",
            "description": "Cost-related information"
        },
        {
            "query": "What test results are available?",
            "description": "Test data discovery"
        },
        {
            "query": "Who are the team members?",
            "description": "Personnel information"
        },
        {
            "query": "What are the thermal analysis results?",
            "description": "Engineering analysis data"
        }
    ]
    
    successful_queries = 0
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n   Query {i}: {test_case['description']}")
        print(f"   Question: \"{test_case['query']}\"")
        
        try:
            response = requests.post(
                f"{base_url}/api/query",
                json={"query": test_case["query"]}
            )
            
            if response.status_code == 200:
                query_data = response.json()
                response_text = query_data["response"]
                sources = query_data["sources"]
                query_time = query_data["query_time"]
                
                print(f"   Response: {response_text[:200]}{'...' if len(response_text) > 200 else ''}")
                print(f"   Sources: {sources}")
                print(f"   Query time: {query_time:.2f}s")
                
                # Check if response indicates content was found
                if "doesn't contain" in response_text.lower() or "not found" in response_text.lower():
                    print(f"   No relevant content found")
                else:
                    print(f"   Content found and processed")
                    successful_queries += 1
            else:
                print(f"   Error: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   Error: {e}")
    
    print(f"\n4. Test Summary:")
    print(f"   Successful queries: {successful_queries}/{len(test_queries)}")
    print(f"   Success rate: {(successful_queries/len(test_queries)*100):.1f}%")
    
    # Test 4: System information
    print("\n5. System information:")
    try:
        response = requests.get(f"{base_url}/api/info")
        if response.status_code == 200:
            info_data = response.json()
            for key, value in info_data.items():
                print(f"   {key}: {value}")
    except Exception as e:
        print(f"   Error getting system info: {e}")
    
    print("\nTesting completed!")
    return successful_queries > 0

if __name__ == "__main__":
    print("Starting enhanced baseline RAG test...")
    print("Make sure the baseline RAG service is running on localhost:8002")
    print("Make sure test data is available in the benchmark_data directory")
    
    # Wait a moment for services to be ready
    print("Starting test in 2 seconds...")
    time.sleep(2)
    
    success = test_enhanced_baseline()
    
    if success:
        print("\nEnhanced baseline RAG appears to be working with spreadsheet support!")
    else:
        print("\nEnhanced baseline RAG test failed. Check the service and data.")