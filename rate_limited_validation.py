#!/usr/bin/env python3
"""
Rate-Limited Nancy Validation
Validates Nancy vs Baseline with proper API rate limiting considerations
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class RateLimitedValidator:
    def __init__(self):
        self.nancy_url = "http://localhost:8000"
        self.baseline_url = "http://localhost:8002"
        self.query_delay = 3.0  # 3 seconds between queries to avoid rate limits
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_results": [],
            "nancy_wins": 0,
            "baseline_wins": 0,
            "ties": 0,
            "api_errors": 0
        }
    
    def check_health(self) -> Dict[str, bool]:
        """Check if both systems are healthy"""
        try:
            nancy_response = requests.get(f"{self.nancy_url}/health", timeout=10)
            nancy_healthy = nancy_response.status_code == 200
        except Exception:
            nancy_healthy = False
            
        try:
            baseline_response = requests.get(f"{self.baseline_url}/health", timeout=10)
            baseline_healthy = baseline_response.status_code == 200
        except Exception:
            baseline_healthy = False
            
        return {"nancy": nancy_healthy, "baseline": baseline_healthy}
    
    def run_single_query(self, system: str, query: str) -> Dict[str, Any]:
        """Run a single query with error handling"""
        url = self.nancy_url if system == "nancy" else self.baseline_url
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{url}/api/query",
                json={"query": query},
                timeout=30
            )
            query_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response": data.get("response", data.get("answer", "")),
                    "query_time": query_time,
                    "system": system
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "query_time": query_time,
                    "system": system
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query_time": 0,
                "system": system
            }
    
    def compare_responses(self, nancy_result: Dict, baseline_result: Dict, query: str, expected_elements: List[str]) -> Dict[str, Any]:
        """Compare Nancy vs Baseline responses for a single query"""
        
        # Check for API errors first
        nancy_error = not nancy_result.get("success", False)
        baseline_error = not baseline_result.get("success", False)
        
        if nancy_error and baseline_error:
            self.results["api_errors"] += 1
            return {
                "query": query,
                "result": "both_failed",
                "nancy_error": nancy_result.get("error", "Unknown"),
                "baseline_error": baseline_result.get("error", "Unknown")
            }
        elif nancy_error:
            self.results["baseline_wins"] += 1
            return {
                "query": query,
                "result": "baseline_wins",
                "reason": "Nancy failed with API error",
                "nancy_error": nancy_result.get("error", "Unknown"),
                "baseline_response": baseline_result.get("response", "")[:200]
            }
        elif baseline_error:
            self.results["nancy_wins"] += 1
            return {
                "query": query,
                "result": "nancy_wins", 
                "reason": "Baseline failed with API error",
                "baseline_error": baseline_result.get("error", "Unknown"),
                "nancy_response": nancy_result.get("response", "")[:200]
            }
        
        # Both succeeded - compare quality
        nancy_response = nancy_result.get("response", "").lower()
        baseline_response = baseline_result.get("response", "").lower()
        
        # Score based on expected elements
        nancy_score = sum(1 for element in expected_elements if element.lower() in nancy_response)
        baseline_score = sum(1 for element in expected_elements if element.lower() in baseline_response)
        
        # Also consider response comprehensiveness
        nancy_length_bonus = min(len(nancy_response) / 500, 1.0)  # Bonus for detailed responses
        baseline_length_bonus = min(len(baseline_response) / 500, 1.0)
        
        nancy_final = nancy_score + nancy_length_bonus * 0.3
        baseline_final = baseline_score + baseline_length_bonus * 0.3
        
        if nancy_final > baseline_final + 0.5:  # Clear win threshold
            self.results["nancy_wins"] += 1
            result = "nancy_wins"
            reason = f"Nancy: {nancy_final:.1f} vs Baseline: {baseline_final:.1f}"
        elif baseline_final > nancy_final + 0.5:
            self.results["baseline_wins"] += 1
            result = "baseline_wins"
            reason = f"Baseline: {baseline_final:.1f} vs Nancy: {nancy_final:.1f}"
        else:
            self.results["ties"] += 1
            result = "tie"
            reason = f"Close scores - Nancy: {nancy_final:.1f} vs Baseline: {baseline_final:.1f}"
        
        return {
            "query": query,
            "result": result,
            "reason": reason,
            "nancy_score": nancy_final,
            "baseline_score": baseline_final,
            "nancy_response": nancy_result.get("response", "")[:300],
            "baseline_response": baseline_result.get("response", "")[:300],
            "nancy_time": nancy_result.get("query_time", 0),
            "baseline_time": baseline_result.get("query_time", 0)
        }
    
    def run_validation(self):
        """Run the rate-limited validation"""
        print("=== RATE-LIMITED NANCY VS BASELINE VALIDATION ===")
        print(f"Query delay: {self.query_delay}s to avoid rate limits")
        
        # Check health first
        health = self.check_health()
        print(f"System Health - Nancy: {health['nancy']}, Baseline: {health['baseline']}")
        
        if not health['nancy']:
            print("❌ Nancy is not healthy - aborting validation")
            return
        if not health['baseline']:
            print("❌ Baseline is not healthy - aborting validation")
            return
        
        # Define test queries that showcase Nancy's strengths
        test_queries = [
            {
                "query": "What are the thermal constraints mentioned in the project?",
                "category": "vector_search",
                "expected_elements": ["thermal", "constraints", "temperature", "heat"]
            },
            {
                "query": "Who are the authors in this project and what did they write?",
                "category": "author_attribution", 
                "expected_elements": ["authors", "wrote", "documents", "sarah", "mike", "lisa"]
            },
            {
                "query": "How many files are in the database?",
                "category": "analytical_query",
                "expected_elements": ["files", "database", "count", "total"]
            },
            {
                "query": "What electrical and mechanical systems are mentioned?",
                "category": "cross_domain",
                "expected_elements": ["electrical", "mechanical", "systems", "components"]
            },
            {
                "query": "Explain the relationship between thermal design and power management",
                "category": "synthesis",
                "expected_elements": ["thermal", "power", "relationship", "design", "management"]
            }
        ]
        
        print(f"\nRunning {len(test_queries)} test queries with {self.query_delay}s delays...")
        
        for i, test in enumerate(test_queries, 1):
            print(f"\n--- Test {i}/{len(test_queries)}: {test['category']} ---")
            print(f"Query: {test['query']}")
            
            # Query Nancy first
            print("  Querying Nancy...")
            nancy_result = self.run_single_query("nancy", test["query"])
            
            # Wait to avoid rate limits
            print(f"  Waiting {self.query_delay}s...")
            time.sleep(self.query_delay)
            
            # Query Baseline
            print("  Querying Baseline...")
            baseline_result = self.run_single_query("baseline", test["query"])
            
            # Compare results
            comparison = self.compare_responses(nancy_result, baseline_result, test["query"], test["expected_elements"])
            self.results["test_results"].append(comparison)
            
            print(f"  Result: {comparison['result']} - {comparison.get('reason', 'No reason')}")
            
            # Wait before next query
            if i < len(test_queries):
                time.sleep(self.query_delay)
        
        # Generate final report
        self.generate_report()
    
    def generate_report(self):
        """Generate final validation report"""
        total_tests = len(self.results["test_results"])
        
        print("\n" + "="*60)
        print("RATE-LIMITED VALIDATION RESULTS")
        print("="*60)
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"Nancy Wins: {self.results['nancy_wins']}")
        print(f"Baseline Wins: {self.results['baseline_wins']}")
        print(f"Ties: {self.results['ties']}")
        print(f"API Errors: {self.results['api_errors']}")
        
        if total_tests > 0:
            nancy_win_rate = self.results['nancy_wins'] / total_tests * 100
            baseline_win_rate = self.results['baseline_wins'] / total_tests * 100
            
            print(f"\nWin Rates:")
            print(f"Nancy: {nancy_win_rate:.1f}%")
            print(f"Baseline: {baseline_win_rate:.1f}%")
            
            if nancy_win_rate > baseline_win_rate:
                print(f"\nRESULT: Nancy outperforms Baseline by {nancy_win_rate - baseline_win_rate:.1f} percentage points")
            elif baseline_win_rate > nancy_win_rate:
                print(f"\nRESULT: Baseline outperforms Nancy by {baseline_win_rate - nancy_win_rate:.1f} percentage points")
            else:
                print(f"\nRESULT: Nancy and Baseline are tied")
            
            if self.results['api_errors'] > 0:
                print(f"\nWARNING: {self.results['api_errors']} tests failed due to API rate limits")
        
        # Save detailed results
        results_file = f"rate_limited_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nDetailed results saved to: {results_file}")

if __name__ == "__main__":
    validator = RateLimitedValidator()
    validator.run_validation()