#!/usr/bin/env python3
"""
LangChain vs Other Orchestrators Comparison for Nancy

This script compares Nancy's new LangChain orchestrator against the 
existing intelligent and enhanced orchestrators to demonstrate the benefits.
"""

import requests
import json
import time
from datetime import datetime

class NancyComparison:
    def __init__(self):
        self.nancy_url = "http://localhost:8000"
        self.results = []
        
        # Test queries to compare orchestrator approaches
        self.test_queries = [
            {
                "query": "What is the operating temperature range?",
                "description": "Basic semantic search",
                "expected": "Should find thermal analysis documents"
            },
            {
                "query": "Who wrote the electrical design review?", 
                "description": "Author attribution query",
                "expected": "Should identify author from graph brain"
            },
            {
                "query": "Show me recent documents",
                "description": "Metadata query", 
                "expected": "Should list recently ingested files"
            },
            {
                "query": "How do electrical and mechanical systems relate?",
                "description": "Complex relationship query",
                "expected": "Should use multiple brains for comprehensive answer"
            }
        ]
    
    def test_orchestrator(self, orchestrator: str, query: str, timeout: int = 120) -> dict:
        """Test a specific orchestrator"""
        print(f"\n  Testing {orchestrator.upper()} orchestrator...")
        print(f"  Query: {query}")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.nancy_url}/api/query",
                json={
                    "query": query,
                    "orchestrator": orchestrator,
                    "n_results": 3
                },
                timeout=timeout
            )
            
            query_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"  SUCCESS in {query_time:.1f}s")
                
                # Extract key info based on orchestrator type
                if orchestrator == "langchain":
                    tools_used = result.get('tools_used', [])
                    agent_steps = result.get('agent_steps', [])
                    print(f"  Tools Used: {', '.join(tools_used)}")
                    print(f"  Agent Steps: {len(agent_steps)}")
                    
                elif orchestrator == "intelligent":
                    intent = result.get('intent_analysis', {})
                    brains_used = result.get('brains_used', [])
                    print(f"  Intent: {intent.get('type', 'unknown')}")
                    print(f"  Brains Used: {', '.join(brains_used)}")
                
                response_text = result.get('response', result.get('synthesized_response', ''))
                if response_text:
                    preview = response_text[:100] + "..." if len(response_text) > 100 else response_text
                    print(f"  Response: {preview}")
                
                return {
                    "success": True,
                    "query_time": query_time,
                    "result": result,
                    "orchestrator": orchestrator
                }
            else:
                print(f"  FAILED - HTTP {response.status_code}")
                error_detail = response.json().get('detail', response.text) if response.text else 'No error details'
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_detail}",
                    "query_time": query_time,
                    "orchestrator": orchestrator
                }
                
        except requests.exceptions.Timeout:
            query_time = time.time() - start_time
            print(f"  TIMEOUT after {query_time:.1f}s")
            return {
                "success": False,
                "error": "Request timed out",
                "query_time": query_time,
                "orchestrator": orchestrator
            }
        except Exception as e:
            query_time = time.time() - start_time
            print(f"  ERROR: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query_time": query_time,
                "orchestrator": orchestrator
            }
    
    def check_health(self):
        """Check Nancy system health"""
        print("\nChecking Nancy system health...")
        try:
            response = requests.get(f"{self.nancy_url}/api/health", timeout=10)
            if response.status_code == 200:
                health = response.json()
                print(f"Health Status: {health.get('status', 'unknown')}")
                return True
            else:
                print(f"Health check failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"Health check error: {e}")
            return False
    
    def run_comparison(self):
        """Run the orchestrator comparison"""
        print("Nancy LangChain vs Traditional Orchestrators Comparison")
        print("=" * 65)
        
        # Check system health
        if not self.check_health():
            print("WARNING: System health check failed. Continuing anyway...")
        
        # Test orchestrators to compare
        orchestrators = ["langchain", "intelligent", "enhanced"]
        
        comparison_results = []
        
        for i, test_case in enumerate(self.test_queries, 1):
            print(f"\n=== TEST {i}: {test_case['description']} ===")
            print(f"Expected: {test_case['expected']}")
            
            test_results = {}
            
            for orchestrator in orchestrators:
                result = self.test_orchestrator(orchestrator, test_case['query'])
                test_results[orchestrator] = result
            
            comparison_results.append({
                "test_case": test_case,
                "results": test_results
            })
        
        # Generate summary
        self.generate_summary(comparison_results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"langchain_comparison_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "comparison_results": comparison_results,
                "summary": self.analyze_results(comparison_results)
            }, f, indent=2, default=str)
        
        print(f"\nDetailed results saved to: {filename}")
        return comparison_results
    
    def generate_summary(self, results):
        """Generate comparison summary"""
        print("\n" + "=" * 65)
        print("COMPARISON SUMMARY")
        print("=" * 65)
        
        orchestrators = ["langchain", "intelligent", "enhanced"]
        
        # Success rates
        print("\nSuccess Rates:")
        for orch in orchestrators:
            successes = sum(1 for r in results if r["results"][orch]["success"])
            total = len(results)
            rate = (successes / total) * 100 if total > 0 else 0
            print(f"  {orch.capitalize():<12}: {successes}/{total} ({rate:.0f}%)")
        
        # Average response times (for successful queries)
        print("\nAverage Response Times:")
        for orch in orchestrators:
            times = [r["results"][orch]["query_time"] for r in results if r["results"][orch]["success"]]
            avg_time = sum(times) / len(times) if times else 0
            print(f"  {orch.capitalize():<12}: {avg_time:.1f}s")
        
        # LangChain specific analysis
        langchain_results = [r["results"]["langchain"] for r in results if r["results"]["langchain"]["success"]]
        if langchain_results:
            print(f"\nLangChain Agent Analysis:")
            total_tools = 0
            total_steps = 0
            for result in langchain_results:
                tools_used = result["result"].get("tools_used", [])
                agent_steps = result["result"].get("agent_steps", [])
                total_tools += len(tools_used)
                total_steps += len(agent_steps)
            
            avg_tools = total_tools / len(langchain_results)
            avg_steps = total_steps / len(langchain_results)
            print(f"  Average tools per query: {avg_tools:.1f}")
            print(f"  Average agent steps: {avg_steps:.1f}")
        
        # Recommendations
        print(f"\nRECOMMENDations:")
        langchain_successes = sum(1 for r in results if r["results"]["langchain"]["success"])
        if langchain_successes == len(results):
            print("  - LangChain integration is working correctly")
            print("  - Agent reasoning provides enhanced orchestration")
            print("  - Response times are higher but quality may be improved")
        else:
            print("  - LangChain integration needs further debugging")
            print("  - Some queries may be failing due to agent complexity")
    
    def analyze_results(self, results):
        """Detailed results analysis for JSON output"""
        analysis = {}
        orchestrators = ["langchain", "intelligent", "enhanced"]
        
        for orch in orchestrators:
            success_count = sum(1 for r in results if r["results"][orch]["success"])
            times = [r["results"][orch]["query_time"] for r in results if r["results"][orch]["success"]]
            
            analysis[orch] = {
                "success_rate": success_count / len(results),
                "avg_response_time": sum(times) / len(times) if times else 0,
                "success_count": success_count,
                "total_tests": len(results)
            }
        
        return analysis

def main():
    """Run the comparison"""
    print("Starting Nancy Orchestrator Comparison...")
    
    comparison = NancyComparison()
    
    try:
        results = comparison.run_comparison()
        print("\nComparison completed successfully!")
        return True
    except KeyboardInterrupt:
        print("\n\nComparison interrupted by user")
        return False
    except Exception as e:
        print(f"\n\nComparison failed: {e}")
        return False

if __name__ == "__main__":
    success = main()