#!/usr/bin/env python3
"""
Simple comparison test of Nancy vs Baseline using Gemma 3 1B
"""
import requests
import json
import time
from datetime import datetime

def test_system(name, url, query):
    """Test a system with a query"""
    print(f"\n=== Testing {name} ===")
    print(f"Query: {query}")
    
    start_time = time.time()
    try:
        response = requests.post(f"{url}/api/query", 
                               json={"query": query}, 
                               timeout=30)
        query_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"Status: Success")
            print(f"Query time: {query_time:.2f}s")
            print(f"Response: {result.get('response', 'No response')[:200]}...")
            print(f"Sources: {len(result.get('sources', []))} files")
            return {
                "system": name,
                "status": "success", 
                "query_time": query_time,
                "response": result.get("response", ""),
                "sources": len(result.get("sources", [])),
                "raw_result": result
            }
        else:
            print(f"❌ Status: HTTP {response.status_code}")
            print(f"Error: {response.text}")
            return {
                "system": name,
                "status": "error",
                "query_time": query_time,
                "error": f"HTTP {response.status_code}",
                "raw_result": response.text
            }
            
    except Exception as e:
        query_time = time.time() - start_time
        print(f"❌ Status: Exception")
        print(f"Error: {str(e)}")
        return {
            "system": name,
            "status": "error", 
            "query_time": query_time,
            "error": str(e)
        }

def main():
    query = "What are the key integration points between electrical and mechanical systems?"
    
    print("🔬 NANCY vs BASELINE COMPARISON TEST")
    print("=" * 50)
    print(f"Query: {query}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Test both systems
    nancy_result = test_system("Nancy", "http://localhost:8000", query)
    baseline_result = test_system("Baseline", "http://localhost:8002", query)
    
    # Save results
    comparison = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "nancy": nancy_result,
        "baseline": baseline_result
    }
    
    filename = f"simple_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(comparison, f, indent=2)
    
    print(f"\n📊 COMPARISON SUMMARY")
    print("=" * 30)
    print(f"Nancy:    {nancy_result['status']} ({nancy_result.get('query_time', 0):.2f}s)")
    print(f"Baseline: {baseline_result['status']} ({baseline_result.get('query_time', 0):.2f}s)")
    print(f"Results saved to: {filename}")

if __name__ == "__main__":
    main()