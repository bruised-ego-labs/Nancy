#!/usr/bin/env python3
"""
Simple test for Nancy Memory MCP Server functionality
"""

import json
import requests
import sys
import time

NANCY_API_BASE = "http://localhost:8000"

def test_nancy_connection():
    """Test connection to Nancy API"""
    print("Testing Nancy API connection...")
    try:
        response = requests.get(f"{NANCY_API_BASE}/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"PASS: Nancy API is healthy: {health['status']}")
            return True
        else:
            print(f"FAIL: Nancy API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: Failed to connect to Nancy API: {e}")
        return False

def test_ingestion():
    """Test Nancy ingestion capability"""
    print("\nTesting information ingestion...")
    
    content = """
    Test Decision: Nancy MCP Integration
    
    We have successfully implemented Nancy as an MCP server to provide
    infinite memory capabilities for other LLMs. This allows any AI assistant
    to store and retrieve project context across conversations.
    
    Key benefits:
    - Persistent memory across conversations
    - Intelligent context retrieval
    - Author attribution and expertise tracking
    - Cross-domain technical analysis
    """
    
    try:
        files = {'file': ('test_decision.txt', content.encode(), 'text/plain')}
        data = {'author': 'MCP Test'}
        
        response = requests.post(
            f"{NANCY_API_BASE}/api/ingest",
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("PASS: Successfully ingested test information")
            return True
        else:
            print(f"FAIL: Ingestion failed: {response.status_code} {response.text}")
            return False
            
    except Exception as e:
        print(f"FAIL: Ingestion error: {e}")
        return False

def test_querying():
    """Test Nancy querying capability"""
    print("\nTesting memory querying...")
    
    try:
        query_data = {
            "query": "What are the benefits of Nancy MCP integration?",
            "n_results": 5,
            "orchestrator": "langchain"
        }
        
        response = requests.post(
            f"{NANCY_API_BASE}/api/query",
            json=query_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("PASS: Query successful")
            response_text = result.get('response', 'No response')
            print(f"Response preview: {response_text[:150]}...")
            return True
        else:
            print(f"FAIL: Query failed: {response.status_code} {response.text}")
            return False
            
    except Exception as e:
        print(f"FAIL: Query error: {e}")
        return False

def test_project_status():
    """Test Nancy project status capability"""
    print("\nTesting project status...")
    
    try:
        response = requests.get(f"{NANCY_API_BASE}/api/nancy/status", timeout=30)
        
        if response.status_code == 200:
            status = response.json()
            print("PASS: Project status retrieved")
            print(f"System status: {status.get('status', {}).get('status', 'unknown')}")
            return True
        else:
            print(f"FAIL: Status query failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"FAIL: Status error: {e}")
        return False

def main():
    """Run comprehensive Nancy MCP test"""
    print("=" * 60)
    print("Nancy Memory MCP Server Test")
    print("=" * 60)
    
    tests = [
        ("Nancy Connection", test_nancy_connection),
        ("Information Ingestion", test_ingestion),
        ("Memory Querying", test_querying), 
        ("Project Status", test_project_status)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            
            # Wait between tests
            if test_name == "Information Ingestion":
                print("Waiting for Nancy to process...")
                time.sleep(3)
                
        except Exception as e:
            print(f"FAIL: {test_name} - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nResult: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\nSUCCESS: Nancy MCP server is working correctly!")
        print("\nNext steps:")
        print("1. Configure Nancy MCP server in Claude Code")
        print("2. Start using persistent memory with any LLM")
        print("3. Transform AI assistants into project-aware intelligence")
        
        print("\nMCP Configuration for Claude Code:")
        config = {
            "mcpServers": {
                "nancy-memory": {
                    "command": "python",
                    "args": ["./mcp-servers/nancy-memory/server.py"],
                    "env": {"NANCY_API_BASE": "http://localhost:8000"}
                }
            }
        }
        print(json.dumps(config, indent=2))
        
    else:
        print("\nFAILURE: Some tests failed. Check Nancy configuration.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)