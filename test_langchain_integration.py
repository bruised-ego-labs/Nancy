#!/usr/bin/env python3
"""
Test script to validate LangChain integration with Nancy's Four-Brain architecture.

This script tests the new LangChain orchestrator against the existing intelligent
orchestrator to ensure functionality is maintained while gaining LangChain benefits.
"""

import requests
import json
import time
from datetime import datetime

def test_orchestrator(orchestrator_type: str, query: str, description: str = ""):
    """Test a specific orchestrator with a query"""
    print(f"\n{'='*60}")
    print(f"Testing {orchestrator_type.upper()} Orchestrator")
    if description:
        print(f"Test: {description}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8000/api/query",
            json={
                "query": query,
                "orchestrator": orchestrator_type,
                "n_results": 5
            },
            timeout=180  # 3 minute timeout
        )
        
        query_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ SUCCESS ({query_time:.1f}s)")
            print(f"Strategy: {result.get('strategy_used', 'Unknown')}")
            
            if orchestrator_type == "langchain":
                print(f"Tools Used: {', '.join(result.get('tools_used', []))}")
                print(f"Agent Steps: {len(result.get('agent_steps', []))}")
            
            if orchestrator_type == "intelligent":
                intent = result.get('intent_analysis', {})
                print(f"Intent Type: {intent.get('type', 'Unknown')}")
                print(f"Confidence: {intent.get('confidence', 0)}")
                print(f"Brains Used: {', '.join(result.get('brains_used', []))}")
            
            # Show response preview
            response_text = result.get('response', result.get('synthesized_response', ''))
            if response_text:
                print(f"Response Preview: {response_text[:150]}{'...' if len(response_text) > 150 else ''}")
            
            return {
                "success": True,
                "query_time": query_time,
                "result": result,
                "orchestrator": orchestrator_type
            }
        else:
            print(f"❌ FAILED - HTTP {response.status_code}")
            print(f"Error: {response.text}")
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}",
                "query_time": query_time,
                "orchestrator": orchestrator_type
            }
            
    except requests.exceptions.Timeout:
        query_time = time.time() - start_time
        print(f"⏰ TIMEOUT ({query_time:.1f}s)")
        return {
            "success": False,
            "error": "Request timed out",
            "query_time": query_time,
            "orchestrator": orchestrator_type
        }
    except Exception as e:
        query_time = time.time() - start_time
        print(f"❌ ERROR ({query_time:.1f}s): {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "query_time": query_time,
            "orchestrator": orchestrator_type
        }

def test_health_check():
    """Test system health"""
    print(f"\n{'='*60}")
    print("Testing System Health")
    print(f"{'='*60}")
    
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=30)
        
        if response.status_code == 200:
            health = response.json()
            print(f"✅ HEALTH CHECK PASSED")
            print(f"Overall Status: {health.get('status', 'Unknown')}")
            
            if 'health' in health and 'brains' in health['health']:
                brains = health['health']['brains']
                for brain_name, brain_health in brains.items():
                    status = brain_health.get('status', 'unknown')
                    print(f"  {brain_name.title()} Brain: {status}")
            
            return True
        else:
            print(f"❌ HEALTH CHECK FAILED - HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ HEALTH CHECK ERROR: {str(e)}")
        return False

def main():
    """Run comprehensive LangChain integration test"""
    print("🔍 Nancy LangChain Integration Test Suite")
    print("="*60)
    
    # Test queries covering different capabilities
    test_queries = [
        {
            "query": "What is the operating temperature range?",
            "description": "Basic semantic search",
            "expected_tools": ["vector_brain"]
        },
        {
            "query": "Who wrote the electrical design review?",
            "description": "Author attribution query",
            "expected_tools": ["graph_brain", "vector_brain"]
        },
        {
            "query": "Show me recent documents",
            "description": "Metadata filtering query",
            "expected_tools": ["analytical_brain"]
        },
        {
            "query": "How do electrical requirements affect mechanical design?",
            "description": "Complex relationship query",
            "expected_tools": ["vector_brain", "graph_brain", "linguistic_brain"]
        }
    ]
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "health_check": False,
        "test_results": []
    }
    
    # 1. Health check first
    results["health_check"] = test_health_check()
    
    if not results["health_check"]:
        print("\n⚠️  System health check failed. Some tests may not work properly.")
    
    # 2. Run comparison tests
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n🧪 TEST {i}/{len(test_queries)}: {test_case['description']}")
        
        # Test LangChain orchestrator
        langchain_result = test_orchestrator("langchain", test_case["query"], test_case["description"])
        
        # Test Intelligent orchestrator for comparison
        intelligent_result = test_orchestrator("intelligent", test_case["query"], f"{test_case['description']} (comparison)")
        
        # Analyze results
        comparison = {
            "test_case": test_case,
            "langchain": langchain_result,
            "intelligent": intelligent_result,
            "comparison": {
                "both_succeeded": langchain_result["success"] and intelligent_result["success"],
                "langchain_faster": False,
                "time_difference": 0
            }
        }
        
        if comparison["comparison"]["both_succeeded"]:
            time_diff = langchain_result["query_time"] - intelligent_result["query_time"]
            comparison["comparison"]["langchain_faster"] = time_diff < 0
            comparison["comparison"]["time_difference"] = time_diff
            
            print(f"\n📊 COMPARISON SUMMARY:")
            print(f"  LangChain: {langchain_result['query_time']:.1f}s")
            print(f"  Intelligent: {intelligent_result['query_time']:.1f}s")
            print(f"  Winner: {'LangChain' if comparison['comparison']['langchain_faster'] else 'Intelligent'}")
        
        results["test_results"].append(comparison)
    
    # 3. Generate final summary
    print(f"\n{'='*60}")
    print("🎯 FINAL SUMMARY")
    print(f"{'='*60}")
    
    langchain_successes = sum(1 for r in results["test_results"] if r["langchain"]["success"])
    intelligent_successes = sum(1 for r in results["test_results"] if r["intelligent"]["success"])
    both_succeeded = sum(1 for r in results["test_results"] if r["comparison"]["both_succeeded"])
    
    print(f"Tests Run: {len(test_queries)}")
    print(f"LangChain Successes: {langchain_successes}/{len(test_queries)}")
    print(f"Intelligent Successes: {intelligent_successes}/{len(test_queries)}")
    print(f"Both Succeeded: {both_succeeded}/{len(test_queries)}")
    
    if both_succeeded > 0:
        avg_langchain_time = sum(r["langchain"]["query_time"] for r in results["test_results"] if r["comparison"]["both_succeeded"]) / both_succeeded
        avg_intelligent_time = sum(r["intelligent"]["query_time"] for r in results["test_results"] if r["comparison"]["both_succeeded"]) / both_succeeded
        
        print(f"\nPerformance Comparison (avg):")
        print(f"  LangChain: {avg_langchain_time:.1f}s")
        print(f"  Intelligent: {avg_intelligent_time:.1f}s")
        print(f"  Performance: {'LangChain faster' if avg_langchain_time < avg_intelligent_time else 'Intelligent faster'}")
    
    # 4. Migration recommendation
    if langchain_successes == len(test_queries):
        print(f"\n✅ MIGRATION RECOMMENDATION: PROCEED")
        print("LangChain integration is working correctly and maintains all functionality.")
    elif langchain_successes >= len(test_queries) * 0.75:
        print(f"\n⚠️  MIGRATION RECOMMENDATION: PROCEED WITH CAUTION")
        print("LangChain integration mostly working but some issues detected.")
    else:
        print(f"\n❌ MIGRATION RECOMMENDATION: DO NOT PROCEED")
        print("LangChain integration has significant issues that need to be resolved.")
    
    # Save detailed results
    with open(f"langchain_integration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to JSON file.")
    
    return results

if __name__ == "__main__":
    main()