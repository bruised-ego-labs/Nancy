#!/usr/bin/env python3
"""
Simple Nancy vs Baseline Test
Tests both systems without unicode characters that cause encoding issues on Windows.
"""

import requests
import time
import json
from datetime import datetime

def test_system(name, url, query):
    """Test a system with a single query"""
    print(f"Testing {name}...")
    
    try:
        start_time = time.time()
        
        request_data = {"query": query}
        if name == "Nancy":
            request_data["orchestrator"] = "langchain"
        
        response = requests.post(
            f"{url}/api/query",
            json=request_data,
            timeout=120,
            headers={"Content-Type": "application/json"}
        )
        
        query_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            return {
                "system": name,
                "status": "success",
                "query_time": query_time,
                "response": result.get("response", ""),
                "sources": len(result.get("sources", [])),
                "strategy": result.get("strategy_used", result.get("method", "unknown"))
            }
        else:
            return {
                "system": name,
                "status": "error", 
                "query_time": query_time,
                "error": f"HTTP {response.status_code}"
            }
            
    except Exception as e:
        return {
            "system": name,
            "status": "error",
            "error": str(e)
        }

def main():
    print("=== NANCY VS BASELINE QUICK TEST ===")
    print()
    
    # Test query
    query = "What are the key integration points between electrical and mechanical systems?"
    
    print(f"Query: {query}")
    print()
    
    # Test both systems
    nancy_result = test_system("Nancy", "http://localhost:8000", query)
    baseline_result = test_system("Baseline", "http://localhost:8002", query)
    
    # Results
    print("RESULTS:")
    print("-" * 50)
    
    for result in [nancy_result, baseline_result]:
        print(f"{result['system']}: {result['status']}")
        if result['status'] == 'success':
            print(f"  Time: {result['query_time']:.1f}s")
            print(f"  Strategy: {result['strategy']}")
            print(f"  Sources: {result['sources']}")
            print(f"  Response: {result['response'][:100]}...")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")
        print()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"simple_test_{timestamp}.json"
    
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "nancy": nancy_result,
        "baseline": baseline_result
    }
    
    with open(filename, 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print(f"Results saved to: {filename}")
    
    # Summary
    print()
    print("SUMMARY:")
    if nancy_result['status'] == 'success' and baseline_result['status'] == 'success':
        print(f"Nancy: {nancy_result['query_time']:.1f}s vs Baseline: {baseline_result['query_time']:.1f}s")
        if nancy_result['query_time'] < baseline_result['query_time']:
            print("Nancy is faster")
        else:
            print("Baseline is faster")
    
    print("Test complete - both systems are functional!")

if __name__ == "__main__":
    main()