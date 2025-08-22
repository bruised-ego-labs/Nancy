#!/usr/bin/env python3

import requests
import time
import json
from datetime import datetime

class IndependentValidator:
    def __init__(self):
        self.nancy_url = "http://localhost:8000"
        self.baseline_url = "http://localhost:8002"
        
    def test_api_rate_limiting_claim(self):
        print("API RATE LIMITING STRESS TEST")
        print("Testing rapid queries to validate rate limiting claims")
        
        test_query = "What are the thermal constraints in the project?"
        rapid_fire_results = {"nancy": [], "baseline": []}
        
        # Test Nancy with rapid queries (no delays)
        print("Testing Nancy with rapid-fire queries (no delays)...")
        for i in range(6):  
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.nancy_url}/api/query",
                    json={"query": test_query},
                    timeout=30
                )
                query_time = time.time() - start_time
                
                result = {
                    "query_num": i + 1,
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "query_time": query_time,
                    "has_429_error": response.status_code == 429
                }
                rapid_fire_results["nancy"].append(result)
                
                if response.status_code != 200:
                    print(f"  Query {i+1}: ERROR {response.status_code}")
                else:
                    print(f"  Query {i+1}: SUCCESS ({query_time:.2f}s)")
                    
            except Exception as e:
                result = {
                    "query_num": i + 1,
                    "success": False,
                    "error": str(e),
                    "query_time": time.time() - start_time
                }
                rapid_fire_results["nancy"].append(result)
                print(f"  Query {i+1}: EXCEPTION {str(e)}")
        
        # Test Baseline 
        print("Testing Baseline with rapid-fire queries (no delays)...")
        for i in range(6):
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.baseline_url}/api/query",
                    json={"query": test_query},
                    timeout=30
                )
                query_time = time.time() - start_time
                
                result = {
                    "query_num": i + 1,
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "query_time": query_time,
                    "has_429_error": response.status_code == 429
                }
                rapid_fire_results["baseline"].append(result)
                
                if response.status_code != 200:
                    print(f"  Query {i+1}: ERROR {response.status_code}")
                else:
                    print(f"  Query {i+1}: SUCCESS ({query_time:.2f}s)")
                    
            except Exception as e:
                result = {
                    "query_num": i + 1,
                    "success": False,
                    "error": str(e),
                    "query_time": time.time() - start_time
                }
                rapid_fire_results["baseline"].append(result)
                print(f"  Query {i+1}: EXCEPTION {str(e)}")
        
        # Analyze results
        nancy_errors = sum(1 for r in rapid_fire_results["nancy"] if not r["success"])
        nancy_429s = sum(1 for r in rapid_fire_results["nancy"] if r.get("has_429_error", False))
        baseline_errors = sum(1 for r in rapid_fire_results["baseline"] if not r["success"])
        baseline_429s = sum(1 for r in rapid_fire_results["baseline"] if r.get("has_429_error", False))
        
        print(f"RESULTS:")
        print(f"Nancy 429 Rate: {nancy_429s / 6 * 100:.1f}%")
        print(f"Baseline 429 Rate: {baseline_429s / 6 * 100:.1f}%")
        print(f"Nancy Error Rate: {nancy_errors / 6 * 100:.1f}%")  
        print(f"Baseline Error Rate: {baseline_errors / 6 * 100:.1f}%")
        
        return rapid_fire_results

if __name__ == "__main__":
    validator = IndependentValidator()
    validator.test_api_rate_limiting_claim()
