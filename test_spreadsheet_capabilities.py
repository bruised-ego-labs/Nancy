#!/usr/bin/env python3
"""
Test Nancy's spreadsheet capabilities vs baseline for structured data analysis
"""

import requests
import json
import time
from datetime import datetime

def test_spreadsheet_query_capabilities():
    """Test Nancy's ability to handle spreadsheet-specific queries"""
    
    nancy_url = "http://localhost:8000"
    baseline_url = "http://localhost:8002"
    
    # Spreadsheet-focused test queries
    spreadsheet_queries = [
        "What are the thermal test results for each component?",
        "Which team members are responsible for mechanical analysis?",
        "Show me the component requirements that failed testing?",
        "What patterns exist in the test results data?",
        "Who is the project manager and what are their contact details?",
        "Compare the thermal constraints across different components",
        "What is the relationship between component cost and thermal performance?",
        "List all electrical engineers and their project roles",
        "What are the maximum temperature values in the thermal test data?",
        "Which components have both high temperature and high cost?"
    ]
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "spreadsheet_capabilities",
        "nancy_results": [],
        "baseline_results": [],
        "comparison": {}
    }
    
    print("Testing Nancy's Spreadsheet Capabilities vs Baseline")
    print("=" * 60)
    
    # Test Nancy
    print("\nTesting Nancy...")
    nancy_successes = 0
    nancy_total_time = 0
    nancy_total_length = 0
    
    for i, query in enumerate(spreadsheet_queries, 1):
        print(f"  Query {i}: {query[:50]}...")
        try:
            start_time = time.time()
            response = requests.post(
                f"{nancy_url}/api/query",
                json={"query": query},
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                
                result = {
                    "query": query,
                    "success": True,
                    "response_time": response_time,
                    "response_length": len(response_text),
                    "response": response_text,
                    "sources": data.get("sources", []),
                    "strategy_used": data.get("strategy_used", "unknown"),
                    "routing_info": data.get("routing_info", {})
                }
                
                nancy_successes += 1
                nancy_total_time += response_time
                nancy_total_length += len(response_text)
                
                print(f"    SUCCESS ({response_time:.1f}s, {len(response_text)} chars)")
                
                # Check for structured data indicators
                if "temperature" in response_text.lower() and any(char.isdigit() for char in response_text):
                    result["has_structured_data"] = True
                if "team" in response_text.lower() or "engineer" in response_text.lower():
                    result["has_team_data"] = True
                
            else:
                result = {
                    "query": query,
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
                print(f"    FAILED (HTTP {response.status_code})")
                
            results["nancy_results"].append(result)
            
        except Exception as e:
            print(f"    ERROR: {e}")
            results["nancy_results"].append({
                "query": query,
                "success": False,
                "error": str(e)
            })
    
    # Test Baseline
    print(f"\nTesting Baseline...")
    baseline_successes = 0
    baseline_total_time = 0
    baseline_total_length = 0
    
    for i, query in enumerate(spreadsheet_queries, 1):
        print(f"  Query {i}: {query[:50]}...")
        try:
            start_time = time.time()
            response = requests.post(
                f"{baseline_url}/api/query",
                json={"query": query},
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                
                result = {
                    "query": query,
                    "success": True,
                    "response_time": response_time,
                    "response_length": len(response_text),
                    "response": response_text,
                    "sources": data.get("sources", [])
                }
                
                baseline_successes += 1
                baseline_total_time += response_time
                baseline_total_length += len(response_text)
                
                print(f"    SUCCESS ({response_time:.1f}s, {len(response_text)} chars)")
                
                # Check for structured data indicators
                if "temperature" in response_text.lower() and any(char.isdigit() for char in response_text):
                    result["has_structured_data"] = True
                if "team" in response_text.lower() or "engineer" in response_text.lower():
                    result["has_team_data"] = True
                
            else:
                result = {
                    "query": query,
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
                print(f"    FAILED (HTTP {response.status_code})")
                
            results["baseline_results"].append(result)
            
        except Exception as e:
            print(f"    ERROR: {e}")
            results["baseline_results"].append({
                "query": query,
                "success": False,
                "error": str(e)
            })
    
    # Generate comparison
    results["comparison"] = {
        "nancy_metrics": {
            "success_rate": nancy_successes / len(spreadsheet_queries),
            "avg_response_time": nancy_total_time / nancy_successes if nancy_successes > 0 else 0,
            "avg_response_length": nancy_total_length / nancy_successes if nancy_successes > 0 else 0,
            "successful_queries": nancy_successes,
            "total_queries": len(spreadsheet_queries)
        },
        "baseline_metrics": {
            "success_rate": baseline_successes / len(spreadsheet_queries),
            "avg_response_time": baseline_total_time / baseline_successes if baseline_successes > 0 else 0,
            "avg_response_length": baseline_total_length / baseline_successes if baseline_successes > 0 else 0,
            "successful_queries": baseline_successes,
            "total_queries": len(spreadsheet_queries)
        }
    }
    
    # Analyze structured data handling
    nancy_structured = sum(1 for r in results["nancy_results"] if r.get("has_structured_data", False))
    baseline_structured = sum(1 for r in results["baseline_results"] if r.get("has_structured_data", False))
    
    nancy_team_data = sum(1 for r in results["nancy_results"] if r.get("has_team_data", False))
    baseline_team_data = sum(1 for r in results["baseline_results"] if r.get("has_team_data", False))
    
    results["comparison"]["structured_data_analysis"] = {
        "nancy_structured_responses": nancy_structured,
        "baseline_structured_responses": baseline_structured,
        "nancy_team_data_responses": nancy_team_data,
        "baseline_team_data_responses": baseline_team_data,
        "nancy_mcp_features": sum(1 for r in results["nancy_results"] if r.get("strategy_used", "unknown") != "unknown")
    }
    
    # Display summary
    print("\n" + "=" * 60)
    print("SPREADSHEET CAPABILITIES SUMMARY")
    print("=" * 60)
    
    nancy_metrics = results["comparison"]["nancy_metrics"]
    baseline_metrics = results["comparison"]["baseline_metrics"]
    structured_analysis = results["comparison"]["structured_data_analysis"]
    
    print(f"\nNancy Performance:")
    print(f"  Success Rate: {nancy_metrics['success_rate']:.1%}")
    print(f"  Avg Response Time: {nancy_metrics['avg_response_time']:.2f}s")
    print(f"  Avg Response Length: {nancy_metrics['avg_response_length']:.0f} chars")
    print(f"  Structured Data Responses: {structured_analysis['nancy_structured_responses']}")
    print(f"  Team Data Responses: {structured_analysis['nancy_team_data_responses']}")
    print(f"  MCP Strategy Used: {structured_analysis['nancy_mcp_features']} queries")
    
    print(f"\nBaseline Performance:")
    print(f"  Success Rate: {baseline_metrics['success_rate']:.1%}")
    print(f"  Avg Response Time: {baseline_metrics['avg_response_time']:.2f}s")
    print(f"  Avg Response Length: {baseline_metrics['avg_response_length']:.0f} chars")
    print(f"  Structured Data Responses: {structured_analysis['baseline_structured_responses']}")
    print(f"  Team Data Responses: {structured_analysis['baseline_team_data_responses']}")
    
    # Comparative advantages
    if nancy_metrics['success_rate'] > baseline_metrics['success_rate']:
        print(f"\nNancy Advantage: Higher success rate")
    
    if structured_analysis['nancy_structured_responses'] > structured_analysis['baseline_structured_responses']:
        print(f"Nancy Advantage: Better structured data handling")
    
    if structured_analysis['nancy_mcp_features'] > 0:
        print(f"Nancy Advantage: MCP architecture routing capabilities")
    
    if baseline_metrics['avg_response_time'] < nancy_metrics['avg_response_time']:
        print(f"\nBaseline Advantage: Faster response times")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"spreadsheet_capabilities_test_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to: {filename}")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    test_spreadsheet_query_capabilities()