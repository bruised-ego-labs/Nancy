#!/usr/bin/env python3
"""
Simple Nancy MCP vs Baseline RAG Benchmark
Avoids Unicode issues while providing comprehensive performance comparison
"""

import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any

class SimpleBenchmarkExecutor:
    def __init__(self):
        self.nancy_url = "http://localhost:8000"
        self.baseline_url = "http://localhost:8002"
        
        # Test queries covering key capabilities
        self.test_queries = [
            # Core capability tests
            "Who specified the thermal constraints and what was their role in the project?",
            "How do the power dissipation requirements from electrical design affect the thermal management approach?",
            "What decisions made in team meetings affected both the component specifications and thermal analysis?",
            "How did the thermal requirements evolve throughout the project timeline?",
            "What patterns in the test results data suggest thermal management improvements?",
            
            # Engineering discipline tests
            "How do system-level requirements cascade down to component-level thermal specifications?",
            "What materials are recommended for high-temperature applications and who made these recommendations?",
            "How do EMC compliance requirements interact with thermal management design decisions?",
            "What memory allocation is required for the thermal control algorithms?",
            "How did user feedback influence the thermal interface design decisions?",
            
            # Complexity scaling tests
            "What is the maximum operating temperature?",
            "Which components have thermal constraints and what are their specifications?",
            "Analyze the relationship between component placement decisions, thermal requirements, electrical routing, and team expertise across all project documentation."
        ]
    
    def test_system_health(self, system_name: str, base_url: str) -> Dict[str, Any]:
        """Test if a system is healthy and responsive"""
        print(f"Testing {system_name} health...")
        try:
            response = requests.get(f"{base_url}/health", timeout=30)
            if response.status_code == 200:
                print(f"  {system_name}: HEALTHY")
                return {"status": "healthy", "response_time": response.elapsed.total_seconds()}
            else:
                print(f"  {system_name}: UNHEALTHY (HTTP {response.status_code})")
                return {"status": "unhealthy", "status_code": response.status_code}
        except Exception as e:
            print(f"  {system_name}: ERROR - {e}")
            return {"status": "error", "error": str(e)}
    
    def run_system_benchmark(self, system_name: str, base_url: str) -> Dict[str, Any]:
        """Run benchmark queries against a system"""
        print(f"\nBenchmarking {system_name}...")
        
        results = {
            "system": system_name,
            "timestamp": datetime.now().isoformat(),
            "query_results": [],
            "performance_metrics": {}
        }
        
        successful_queries = 0
        total_response_time = 0
        response_lengths = []
        source_counts = []
        
        for i, query in enumerate(self.test_queries, 1):
            print(f"  Query {i}/{len(self.test_queries)}: {query[:60]}...")
            
            try:
                start_time = time.time()
                response = requests.post(
                    f"{base_url}/api/query",
                    json={"query": query},
                    timeout=120
                )
                response_time = time.time() - start_time
                
                query_result = {
                    "query_id": i,
                    "query": query,
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "successful": response.status_code == 200
                }
                
                if response.status_code == 200:
                    data = response.json()
                    query_result["response"] = data.get("response", "")
                    query_result["sources"] = data.get("sources", [])
                    query_result["response_length"] = len(data.get("response", ""))
                    query_result["source_count"] = len(data.get("sources", []))
                    
                    # Nancy-specific metadata
                    if "nancy" in system_name.lower():
                        query_result["strategy_used"] = data.get("strategy_used", "unknown")
                        query_result["routing_info"] = data.get("routing_info", {})
                    
                    successful_queries += 1
                    total_response_time += response_time
                    response_lengths.append(query_result["response_length"])
                    source_counts.append(query_result["source_count"])
                    
                    print(f"    SUCCESS ({response_time:.1f}s, {query_result['response_length']} chars)")
                else:
                    query_result["error"] = response.text
                    print(f"    FAILED (HTTP {response.status_code})")
                
                results["query_results"].append(query_result)
                
            except requests.exceptions.Timeout:
                print(f"    TIMEOUT (120s)")
                results["query_results"].append({
                    "query_id": i,
                    "query": query,
                    "successful": False,
                    "timeout": True,
                    "response_time": 120.0
                })
                
            except Exception as e:
                print(f"    ERROR: {e}")
                results["query_results"].append({
                    "query_id": i,
                    "query": query,
                    "successful": False,
                    "error": str(e)
                })
        
        # Calculate performance metrics
        results["performance_metrics"] = {
            "success_rate": successful_queries / len(self.test_queries),
            "average_response_time": total_response_time / successful_queries if successful_queries > 0 else 0,
            "total_queries": len(self.test_queries),
            "successful_queries": successful_queries,
            "failed_queries": len(self.test_queries) - successful_queries,
            "average_response_length": sum(response_lengths) / len(response_lengths) if response_lengths else 0,
            "average_source_count": sum(source_counts) / len(source_counts) if source_counts else 0
        }
        
        print(f"  Results: {successful_queries}/{len(self.test_queries)} successful")
        print(f"  Avg response time: {results['performance_metrics']['average_response_time']:.2f}s")
        print(f"  Avg response length: {results['performance_metrics']['average_response_length']:.0f} chars")
        
        return results
    
    def analyze_comparison(self, nancy_results: Dict, baseline_results: Dict) -> Dict[str, Any]:
        """Compare Nancy vs Baseline performance"""
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "nancy_performance": nancy_results["performance_metrics"],
            "baseline_performance": baseline_results["performance_metrics"],
            "comparative_analysis": {}
        }
        
        nancy_metrics = nancy_results["performance_metrics"]
        baseline_metrics = baseline_results["performance_metrics"]
        
        # Success rate comparison
        nancy_success = nancy_metrics["success_rate"]
        baseline_success = baseline_metrics["success_rate"]
        success_improvement = ((nancy_success / baseline_success) - 1) * 100 if baseline_success > 0 else 0
        
        # Response time comparison
        nancy_time = nancy_metrics["average_response_time"]
        baseline_time = baseline_metrics["average_response_time"]
        time_difference = ((nancy_time / baseline_time) - 1) * 100 if baseline_time > 0 else 0
        
        # Response quality comparison
        nancy_length = nancy_metrics["average_response_length"]
        baseline_length = baseline_metrics["average_response_length"]
        quality_ratio = nancy_length / baseline_length if baseline_length > 0 else 0
        
        comparison["comparative_analysis"] = {
            "success_rate_improvement_percent": success_improvement,
            "response_time_difference_percent": time_difference,
            "response_quality_ratio": quality_ratio,
            "nancy_advantages": [],
            "baseline_advantages": [],
            "recommendations": []
        }
        
        # Determine advantages
        if success_improvement > 5:
            comparison["comparative_analysis"]["nancy_advantages"].append(
                f"Higher success rate: {nancy_success:.1%} vs {baseline_success:.1%}"
            )
        elif success_improvement < -5:
            comparison["comparative_analysis"]["baseline_advantages"].append(
                f"Higher success rate: {baseline_success:.1%} vs {nancy_success:.1%}"
            )
        
        if time_difference < -10:
            comparison["comparative_analysis"]["nancy_advantages"].append(
                f"Faster response time: {nancy_time:.1f}s vs {baseline_time:.1f}s"
            )
        elif time_difference > 20:
            comparison["comparative_analysis"]["baseline_advantages"].append(
                f"Faster response time: {baseline_time:.1f}s vs {nancy_time:.1f}s"
            )
        
        if quality_ratio > 1.2:
            comparison["comparative_analysis"]["nancy_advantages"].append(
                f"More detailed responses: {nancy_length:.0f} vs {baseline_length:.0f} chars avg"
            )
        
        # Nancy-specific features
        nancy_features = []
        for result in nancy_results["query_results"]:
            if result.get("strategy_used") and result["strategy_used"] != "unknown":
                nancy_features.append("Intelligent routing strategies")
                break
        
        if nancy_features:
            comparison["comparative_analysis"]["nancy_advantages"].extend(nancy_features)
        
        return comparison
    
    def execute_benchmark(self) -> Dict[str, Any]:
        """Execute complete benchmark comparison"""
        print("=" * 60)
        print("NANCY MCP VS BASELINE RAG BENCHMARK")
        print("=" * 60)
        
        benchmark_results = {
            "timestamp": datetime.now().isoformat(),
            "environment_validation": {},
            "nancy_results": {},
            "baseline_results": {},
            "comparative_analysis": {}
        }
        
        # Environment validation
        print("\nPhase 1: Environment Validation")
        print("-" * 30)
        nancy_health = self.test_system_health("Nancy", self.nancy_url)
        baseline_health = self.test_system_health("Baseline", self.baseline_url)
        
        benchmark_results["environment_validation"] = {
            "nancy": nancy_health,
            "baseline": baseline_health
        }
        
        if nancy_health["status"] != "healthy" or baseline_health["status"] != "healthy":
            print("\nERROR: One or more systems are not healthy. Cannot proceed.")
            return benchmark_results
        
        # Run benchmarks
        print("\nPhase 2: System Benchmarking")
        print("-" * 30)
        
        nancy_results = self.run_system_benchmark("Nancy", self.nancy_url)
        baseline_results = self.run_system_benchmark("Baseline", self.baseline_url)
        
        benchmark_results["nancy_results"] = nancy_results
        benchmark_results["baseline_results"] = baseline_results
        
        # Comparative analysis
        print("\nPhase 3: Comparative Analysis")
        print("-" * 30)
        
        comparison = self.analyze_comparison(nancy_results, baseline_results)
        benchmark_results["comparative_analysis"] = comparison
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"simple_benchmark_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(benchmark_results, f, indent=2, default=str)
        
        print(f"\nResults saved to: {results_file}")
        
        # Display summary
        self.display_summary(benchmark_results)
        
        return benchmark_results
    
    def display_summary(self, results: Dict[str, Any]) -> None:
        """Display benchmark summary"""
        print("\n" + "=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)
        
        nancy_metrics = results["nancy_results"]["performance_metrics"]
        baseline_metrics = results["baseline_results"]["performance_metrics"]
        comparison = results["comparative_analysis"]["comparative_analysis"]
        
        print(f"\nNancy Performance:")
        print(f"  Success Rate: {nancy_metrics['success_rate']:.1%}")
        print(f"  Avg Response Time: {nancy_metrics['average_response_time']:.2f}s")
        print(f"  Avg Response Length: {nancy_metrics['average_response_length']:.0f} chars")
        
        print(f"\nBaseline Performance:")
        print(f"  Success Rate: {baseline_metrics['success_rate']:.1%}")
        print(f"  Avg Response Time: {baseline_metrics['average_response_time']:.2f}s")
        print(f"  Avg Response Length: {baseline_metrics['average_response_length']:.0f} chars")
        
        print(f"\nComparative Analysis:")
        print(f"  Success Rate Change: {comparison['success_rate_improvement_percent']:+.1f}%")
        print(f"  Response Time Change: {comparison['response_time_difference_percent']:+.1f}%")
        print(f"  Response Quality Ratio: {comparison['response_quality_ratio']:.2f}x")
        
        if comparison["nancy_advantages"]:
            print(f"\nNancy Advantages:")
            for advantage in comparison["nancy_advantages"]:
                print(f"  + {advantage}")
        
        if comparison["baseline_advantages"]:
            print(f"\nBaseline Advantages:")
            for advantage in comparison["baseline_advantages"]:
                print(f"  + {advantage}")
        
        print("\n" + "=" * 60)

def main():
    """Execute simple benchmark"""
    executor = SimpleBenchmarkExecutor()
    results = executor.execute_benchmark()
    return results

if __name__ == "__main__":
    main()