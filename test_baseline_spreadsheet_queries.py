#!/usr/bin/env python3
"""
Focused test of baseline RAG's ability to answer specific spreadsheet queries.

This validates that the enhanced baseline can now compete fairly with Nancy 
on spreadsheet-related questions that were previously impossible for 
text-only RAG systems.
"""

import requests
import json
import time

def test_spreadsheet_specific_queries():
    """Test baseline RAG with specific spreadsheet queries that demonstrate fairness"""
    
    base_url = "http://localhost:8002"
    
    print("Testing Baseline RAG Spreadsheet Query Capabilities")
    print("=" * 60)
    
    # Focused spreadsheet queries that should work with textification
    test_queries = [
        {
            "query": "Which components have thermal constraints over 70 degrees?",
            "description": "Thermal constraint filtering",
            "expected_content": ["COMP-001", "COMP-002", "Primary CPU", "Memory Module"]
        },
        {
            "query": "What components does Sarah Chen own?",
            "description": "Owner-based component lookup",
            "expected_content": ["Sarah Chen", "Primary CPU", "Sensor Array", "COMP-001", "COMP-005"]
        },
        {
            "query": "Which test results failed?",
            "description": "Test result status filtering", 
            "expected_content": ["Fail", "TEST-004", "Heavy Rain"]
        },
        {
            "query": "What is the power requirement for the Radio Transceiver?",
            "description": "Specific component property lookup",
            "expected_content": ["Radio Transceiver", "8.7", "COMP-003"]
        },
        {
            "query": "Which components are validated and have high priority?",
            "description": "Multi-criteria filtering",
            "expected_content": ["Validated", "High", "Primary CPU", "Radio Transceiver", "Sensor Array"]
        }
    ]
    
    successful_queries = 0
    detailed_results = []
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Query: \"{test_case['query']}\"")
        
        try:
            response = requests.post(
                f"{base_url}/api/query",
                json={"query": test_case["query"]},
                timeout=30
            )
            
            if response.status_code == 200:
                query_data = response.json()
                response_text = query_data["response"].lower()
                sources = query_data["sources"]
                query_time = query_data["query_time"]
                
                # Check if response contains expected content
                content_matches = 0
                found_content = []
                
                for expected_item in test_case["expected_content"]:
                    if expected_item.lower() in response_text:
                        content_matches += 1
                        found_content.append(expected_item)
                
                success_rate = content_matches / len(test_case["expected_content"])
                
                print(f"   Response: {query_data['response'][:150]}{'...' if len(query_data['response']) > 150 else ''}")
                print(f"   Sources: {sources}")
                print(f"   Query time: {query_time:.2f}s")
                print(f"   Expected content found: {content_matches}/{len(test_case['expected_content'])} ({success_rate*100:.1f}%)")
                print(f"   Found: {found_content}")
                
                # Consider successful if finds at least 50% of expected content
                if success_rate >= 0.5:
                    print(f"   Result: SUCCESS")
                    successful_queries += 1
                else:
                    print(f"   Result: PARTIAL - may lack specific spreadsheet data")
                
                detailed_results.append({
                    "query": test_case["query"],
                    "description": test_case["description"],
                    "success_rate": success_rate,
                    "response_time": query_time,
                    "sources": sources,
                    "found_content": found_content
                })
                
            else:
                print(f"   Error: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                detailed_results.append({
                    "query": test_case["query"],
                    "description": test_case["description"],
                    "success_rate": 0.0,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"   Error: {e}")
            detailed_results.append({
                "query": test_case["query"],
                "description": test_case["description"],
                "success_rate": 0.0,
                "error": str(e)
            })
    
    print(f"\n{'='*60}")
    print(f"FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Successful queries: {successful_queries}/{len(test_queries)}")
    print(f"Overall success rate: {(successful_queries/len(test_queries)*100):.1f}%")
    
    # Check if baseline can handle spreadsheet content
    if successful_queries >= len(test_queries) * 0.6:  # 60% threshold
        print("\nCONCLUSION: Enhanced baseline RAG successfully handles spreadsheet content!")
        print("This creates a fair comparison baseline for Nancy's advanced capabilities.")
        fairness_achieved = True
    else:
        print("\nCONCLUSION: Baseline still struggles with spreadsheet queries.")
        print("May need further textification improvements.")
        fairness_achieved = False
    
    # Save detailed results
    results_file = f"baseline_spreadsheet_test_results_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            "test_summary": {
                "total_queries": len(test_queries),
                "successful_queries": successful_queries,
                "success_rate": successful_queries/len(test_queries),
                "fairness_achieved": fairness_achieved
            },
            "detailed_results": detailed_results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")
    return fairness_achieved

if __name__ == "__main__":
    print("Testing enhanced baseline RAG spreadsheet query capabilities...")
    print("This validates fair comparison with Nancy's four-brain architecture.")
    
    success = test_spreadsheet_specific_queries()
    
    if success:
        print("\nBaseline RAG enhancement successful - fair comparison achieved!")
    else:
        print("\nBaseline RAG may need additional improvements for full fairness.")