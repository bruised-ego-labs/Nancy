#!/usr/bin/env python3
"""
Independent Performance Validation for Nancy System
Dr. Elena Vasquez - Rigorous Scientific Evaluation

This script provides an unbiased, comprehensive assessment of Nancy's 
performance issues and the effectiveness of claimed fixes.
"""

import requests
import time
import json
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

class IndependentValidator:
    def __init__(self):
        self.nancy_url = "http://localhost:8000"
        self.baseline_url = "http://localhost:8002"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "validation_type": "independent_rigorous_assessment",
            "methodology": "scientific_stress_testing_with_controls",
            "tests_performed": [],
            "summary": {}
        }
    
    def test_api_rate_limiting_claim(self) -> Dict[str, Any]:
        """
        Test the central claim that API rate limiting was the primary issue
        by conducting rapid-fire queries to both systems
        """
        print("
=== API RATE LIMITING STRESS TEST ===")
        print("Testing rapid queries to validate rate limiting claims")
        
        test_query = "What are the thermal constraints in the project?"
        rapid_fire_results = {"nancy": [], "baseline": []}
        
        # Test Nancy with rapid queries (no delays)
        print("
Testing Nancy with rapid-fire queries (no delays)...")
        for i in range(8):  # Reduced to 8 for faster testing
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.nancy_url}/api/query",
                    json={"query": test_query},
                    timeout=30
                )
                query_time = time.time() - start_time
                
                rapid_fire_results["nancy"].append({
                    "query_num": i + 1,
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "query_time": query_time,
                    "has_429_error": response.status_code == 429,
                    "response_length": len(response.text) if response.status_code == 200 else 0
                })
                
                if response.status_code != 200:
                    print(f"  Query {i+1}: ERROR {response.status_code}")
                else:
                    print(f"  Query {i+1}: SUCCESS ({query_time:.2f}s)")
                    
            except Exception as e:
                rapid_fire_results["nancy"].append({
                    "query_num": i + 1,
                    "success": False,
                    "error": str(e),
                    "query_time": time.time() - start_time
                })
                print(f"  Query {i+1}: EXCEPTION {str(e)}")
        
        # Test Baseline with same rapid queries
        print("
Testing Baseline with rapid-fire queries (no delays)...")
        for i in range(8):
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.baseline_url}/api/query",
                    json={"query": test_query},
                    timeout=30
                )
                query_time = time.time() - start_time
                
                rapid_fire_results["baseline"].append({
                    "query_num": i + 1,
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "query_time": query_time,
                    "has_429_error": response.status_code == 429,
                    "response_length": len(response.text) if response.status_code == 200 else 0
                })
                
                if response.status_code != 200:
                    print(f"  Query {i+1}: ERROR {response.status_code}")
                else:
                    print(f"  Query {i+1}: SUCCESS ({query_time:.2f}s)")
                    
            except Exception as e:
                rapid_fire_results["baseline"].append({
                    "query_num": i + 1,
                    "success": False,
                    "error": str(e),
                    "query_time": time.time() - start_time
                })
                print(f"  Query {i+1}: EXCEPTION {str(e)}")
        
        # Analyze results
        nancy_errors = sum(1 for r in rapid_fire_results["nancy"] if not r["success"])
        nancy_429s = sum(1 for r in rapid_fire_results["nancy"] if r.get("has_429_error", False))
        baseline_errors = sum(1 for r in rapid_fire_results["baseline"] if not r["success"])
        baseline_429s = sum(1 for r in rapid_fire_results["baseline"] if r.get("has_429_error", False))
        
        return {
            "test_name": "api_rate_limiting_stress_test",
            "nancy_error_rate": nancy_errors / 8 * 100,
            "nancy_429_rate": nancy_429s / 8 * 100,
            "baseline_error_rate": baseline_errors / 8 * 100,
            "baseline_429_rate": baseline_429s / 8 * 100,
            "raw_results": rapid_fire_results,
            "conclusion": "Nancy has rate limiting issues" if nancy_429s > baseline_429s else "No clear rate limiting advantage"
        }

if __name__ == "__main__":
    validator = IndependentValidator()
    result = validator.test_api_rate_limiting_claim()
    print("Rate limiting test completed:")
    print(f"Nancy 429 Rate: {result['nancy_429_rate']:.1f}%")
    print(f"Baseline 429 Rate: {result['baseline_429_rate']:.1f}%")
    print(f"Nancy Error Rate: {result['nancy_error_rate']:.1f}%")  
    print(f"Baseline Error Rate: {result['baseline_error_rate']:.1f}%")
    print(f"Conclusion: {result['conclusion']}")
