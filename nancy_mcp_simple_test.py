#!/usr/bin/env python3
"""
Nancy MCP Simple Test
Focused test of critical Nancy MCP functionality to isolate specific issues.
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, Any

def test_basic_functionality():
    """Test basic Nancy functionality that should work."""
    
    base_url = "http://localhost:8000"
    results = {}
    
    print("Nancy MCP Simple Test")
    print("=" * 40)
    
    # Test 1: Basic connectivity
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        results["basic_connectivity"] = {
            "status": "success" if response.status_code == 200 else "failed",
            "response": response.json() if response.status_code == 200 else response.text
        }
        print(f"[OK] Basic connectivity: {results['basic_connectivity']['status']}")
    except Exception as e:
        results["basic_connectivity"] = {"status": "error", "error": str(e)}
        print(f"[ERROR] Basic connectivity: {e}")
    
    # Test 2: Legacy ingestion (should work)
    try:
        test_content = f"Test content for Nancy MCP simple test - {datetime.now().isoformat()}"
        
        import io
        files = {
            'file': ('simple_test.txt', io.BytesIO(test_content.encode('utf-8')), 'text/plain')
        }
        data = {'author': 'Simple Test'}
        
        response = requests.post(
            f"{base_url}/api/ingest",
            files=files,
            data=data,
            timeout=30
        )
        
        results["legacy_ingestion"] = {
            "status": "success" if response.status_code == 200 else "failed",
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text[:200]
        }
        print(f"[OK] Legacy ingestion: {results['legacy_ingestion']['status']} (status: {response.status_code})")
        
        # If ingestion succeeded, note the doc_id for query test
        if response.status_code == 200:
            resp_data = response.json()
            doc_id = resp_data.get("doc_id") or resp_data.get("packet_id")
            results["legacy_ingestion"]["doc_id"] = doc_id
        
    except Exception as e:
        results["legacy_ingestion"] = {"status": "error", "error": str(e)}
        print(f"[ERROR] Legacy ingestion: {e}")
    
    # Wait for indexing
    print("[INFO] Waiting 3 seconds for indexing...")
    time.sleep(3)
    
    # Test 3: Query functionality
    try:
        query_data = {
            "query": "simple test content",
            "n_results": 5,
            "orchestrator": "intelligent"
        }
        
        response = requests.post(
            f"{base_url}/api/query",
            json=query_data,
            timeout=60
        )
        
        results["query_functionality"] = {
            "status": "success" if response.status_code == 200 else "failed",
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text[:200]
        }
        print(f"[OK] Query functionality: {results['query_functionality']['status']} (status: {response.status_code})")
        
        # Check if query found the ingested content
        if response.status_code == 200:
            query_result = response.json()
            found_content = "simple test" in str(query_result).lower()
            results["query_functionality"]["found_ingested_content"] = found_content
            print(f"  -> Content found in query: {found_content}")
        
    except Exception as e:
        results["query_functionality"] = {"status": "error", "error": str(e)}
        print(f"[ERROR] Query functionality: {e}")
    
    # Test 4: Graph query
    try:
        graph_data = {
            "author_name": "Simple Test",
            "use_enhanced": True
        }
        
        response = requests.post(
            f"{base_url}/api/query/graph",
            json=graph_data,
            timeout=30
        )
        
        results["graph_query"] = {
            "status": "success" if response.status_code == 200 else "failed",
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text[:200]
        }
        print(f"[OK] Graph query: {results['graph_query']['status']} (status: {response.status_code})")
        
    except Exception as e:
        results["graph_query"] = {"status": "error", "error": str(e)}
        print(f"[ERROR] Graph query: {e}")
    
    # Test 5: Configuration endpoint (should work)
    try:
        response = requests.get(f"{base_url}/api/nancy/configuration", timeout=10)
        results["configuration"] = {
            "status": "success" if response.status_code == 200 else "failed",
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text[:200]
        }
        print(f"[OK] Configuration endpoint: {results['configuration']['status']} (status: {response.status_code})")
        
    except Exception as e:
        results["configuration"] = {"status": "error", "error": str(e)}
        print(f"[ERROR] Configuration endpoint: {e}")
    
    # Test 6: Ingestion status endpoint
    try:
        response = requests.get(f"{base_url}/api/ingest/status", timeout=10)
        results["ingestion_status"] = {
            "status": "success" if response.status_code == 200 else "failed",
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text[:200]
        }
        print(f"[OK] Ingestion status: {results['ingestion_status']['status']} (status: {response.status_code})")
        
    except Exception as e:
        results["ingestion_status"] = {"status": "error", "error": str(e)}
        print(f"[ERROR] Ingestion status: {e}")
    
    # Summary
    print("\nTest Summary:")
    print("-" * 40)
    
    working_tests = [k for k, v in results.items() if v.get("status") == "success"]
    failed_tests = [k for k, v in results.items() if v.get("status") in ["failed", "error"]]
    
    print(f"[OK] Working: {len(working_tests)}/{len(results)}")
    print(f"[ERROR] Failed: {len(failed_tests)}/{len(results)}")
    
    if working_tests:
        print(f"\nWorking endpoints:")
        for test in working_tests:
            print(f"  [OK] {test}")
    
    if failed_tests:
        print(f"\nFailed endpoints:")
        for test in failed_tests:
            error_info = results[test].get("error", results[test].get("response", "Unknown error"))
            print(f"  [ERROR] {test}: {error_info}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"nancy_simple_test_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump({
            "test_timestamp": datetime.now().isoformat(),
            "test_results": results,
            "summary": {
                "total_tests": len(results),
                "working_tests": len(working_tests),
                "failed_tests": len(failed_tests),
                "working_endpoints": working_tests,
                "failed_endpoints": failed_tests
            }
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {filename}")
    
    return results

if __name__ == "__main__":
    test_basic_functionality()