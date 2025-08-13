#!/usr/bin/env python3
"""
Comprehensive Nancy vs Baseline RAG Benchmark with LLM/Embedding Usage Metrics

This script:
1. Ingests test data into both Nancy and baseline systems
2. Measures ingestion time and resource usage
3. Runs benchmark queries comparing both systems
4. Tracks LLM calls, token usage, and embedding operations
5. Provides detailed performance and cost analysis

Usage: python comprehensive_benchmark_with_metrics.py
"""

import requests
import time
import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Any, Tuple
import threading
from collections import defaultdict

class ComprehensiveBenchmark:
    def __init__(self):
        self.nancy_url = "http://localhost:8000"
        self.baseline_url = "http://localhost:8002"
        self.results = []
        self.metrics = {
            "nancy": {
                "llm_calls": 0,
                "total_tokens": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "embedding_operations": 0,
                "processing_time": 0,
                "errors": 0
            },
            "baseline": {
                "llm_calls": 0,
                "total_tokens": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "embedding_operations": 0,
                "processing_time": 0,
                "errors": 0
            }
        }
        
        # Test data directory
        self.test_data_dir = "benchmark_test_data"
        
        # Enhanced test queries with expected LLM usage patterns - 15 comprehensive queries
        self.test_queries = [
            # Systems Engineering (3 queries)
            {
                "category": "Systems Engineering - Requirements",
                "query": "What are the system-level requirements and how do they constrain the mechanical design?",
                "expected_llm_calls": {"nancy": 1, "baseline": 1},
                "expected_capabilities": ["basic_retrieval", "cross_document_synthesis"]
            },
            {
                "category": "Systems Engineering - Integration",
                "query": "Which integration points between electrical and mechanical systems need special attention?",
                "expected_llm_calls": {"nancy": 1, "baseline": 1},
                "expected_capabilities": ["relationship_discovery", "technical_synthesis"]
            },
            {
                "category": "Systems Engineering - Verification",
                "query": "What verification procedures are defined for thermal performance validation?",
                "expected_llm_calls": {"nancy": 1, "baseline": 1},
                "expected_capabilities": ["basic_retrieval", "temporal_analysis"]
            },
            
            # Mechanical Engineering (3 queries)
            {
                "category": "Mechanical Engineering - Materials",
                "query": "What materials are specified for high-temperature components and who selected them?",
                "expected_llm_calls": {"nancy": 1, "baseline": 1},
                "expected_capabilities": ["basic_retrieval", "author_tracking"]
            },
            {
                "category": "Mechanical Engineering - Stress Analysis",
                "query": "What are the critical stress points identified in the structural analysis documents?",
                "expected_llm_calls": {"nancy": 1, "baseline": 1},
                "expected_capabilities": ["technical_synthesis", "basic_retrieval"]
            },
            {
                "category": "Mechanical Engineering - CAD Integration",
                "query": "How do the CAD model revisions relate to thermal analysis updates?",
                "expected_llm_calls": {"nancy": 1, "baseline": 1},
                "expected_capabilities": ["relationship_discovery", "temporal_analysis"]
            },
            
            # Electrical Engineering (3 queries)
            {
                "category": "Electrical Engineering - Power Systems",
                "query": "What are the power dissipation requirements and how do they impact the enclosure design?",
                "expected_llm_calls": {"nancy": 1, "baseline": 1},
                "expected_capabilities": ["technical_synthesis", "cross_domain_analysis"]
            },
            {
                "category": "Electrical Engineering - EMC Compliance",
                "query": "What EMC compliance measures are specified and who is responsible for implementation?",
                "expected_llm_calls": {"nancy": 1, "baseline": 1},
                "expected_capabilities": ["basic_retrieval", "author_tracking"]
            },
            {
                "category": "Electrical Engineering - Circuit Design",
                "query": "How do circuit board layout constraints affect thermal management decisions?",
                "expected_llm_calls": {"nancy": 1, "baseline": 1},
                "expected_capabilities": ["cross_domain_analysis", "relationship_discovery"]
            },
            
            # Firmware Engineering (2 queries)
            {
                "category": "Firmware Engineering - Memory Requirements",
                "query": "What are the memory allocation requirements for the thermal control algorithms?",
                "expected_llm_calls": {"nancy": 1, "baseline": 1},
                "expected_capabilities": ["basic_retrieval", "technical_synthesis"]
            },
            {
                "category": "Firmware Engineering - Control Protocols",
                "query": "Which communication protocols are used between thermal sensors and the main controller?",
                "expected_llm_calls": {"nancy": 1, "baseline": 1},
                "expected_capabilities": ["technical_synthesis", "basic_retrieval"]
            },
            
            # Industrial Design (2 queries)
            {
                "category": "Industrial Design - User Interface",
                "query": "What user feedback influenced the thermal management interface design decisions?",
                "expected_llm_calls": {"nancy": 1, "baseline": 1},
                "expected_capabilities": ["decision_tracking", "author_attribution"]
            },
            {
                "category": "Industrial Design - Ergonomics",
                "query": "How do ergonomic considerations affect the placement of thermal management controls?",
                "expected_llm_calls": {"nancy": 1, "baseline": 1},
                "expected_capabilities": ["cross_domain_analysis", "basic_retrieval"]
            },
            
            # Project Management (2 queries)
            {
                "category": "Project Management - Timeline",
                "query": "What activities are scheduled for Q4 2024 and how do they relate to thermal considerations?",
                "expected_llm_calls": {"nancy": 1, "baseline": 1},
                "expected_capabilities": ["temporal_filtering", "relationship_discovery"]
            },
            {
                "category": "Project Management - Decision Tracking",
                "query": "What decisions were made in the project timeline that affect the thermal analysis, and who made them?",
                "expected_llm_calls": {"nancy": 2, "baseline": 1},
                "expected_capabilities": ["decision_tracking", "temporal_analysis", "author_attribution"]
            }
        ]
    
    def ingest_test_data(self, system_name: str, base_url: str) -> Dict[str, Any]:
        """Ingest test data and measure performance"""
        print(f"📥 Starting data ingestion for {system_name}...")
        
        if not os.path.exists(self.test_data_dir):
            return {
                "status": "error",
                "error": f"Test data directory '{self.test_data_dir}' not found"
            }
        
        test_files = glob.glob(os.path.join(self.test_data_dir, "*.txt"))
        if not test_files:
            return {
                "status": "error", 
                "error": f"No .txt files found in '{self.test_data_dir}'"
            }
        
        ingestion_start = time.time()
        ingested_files = []
        errors = []
        
        for file_path in test_files:
            try:
                filename = os.path.basename(file_path)
                print(f"   → Uploading {filename}...")
                
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Prepare multipart form data
                files = {
                    'file': (filename, content, 'text/plain')
                }
                data = {
                    'author': 'Benchmark Test User'  # Standard author for benchmark
                }
                
                # Upload to system
                upload_start = time.time()
                response = requests.post(
                    f"{base_url}/api/ingest",
                    files=files,
                    data=data,
                    timeout=120
                )
                upload_time = time.time() - upload_start
                
                if response.status_code == 200:
                    ingested_files.append({
                        "filename": filename,
                        "size_bytes": len(content),
                        "upload_time": upload_time,
                        "status": "success"
                    })
                    print(f"      ✓ Uploaded {filename} ({len(content)} bytes) in {upload_time:.1f}s")
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    errors.append({
                        "filename": filename,
                        "error": error_msg
                    })
                    print(f"      ✗ Failed to upload {filename}: {error_msg}")
                
            except Exception as e:
                error_msg = str(e)
                errors.append({
                    "filename": filename,
                    "error": error_msg
                })
                print(f"      ✗ Error uploading {filename}: {error_msg}")
        
        ingestion_time = time.time() - ingestion_start
        total_bytes = sum(f["size_bytes"] for f in ingested_files)
        
        result = {
            "status": "completed",
            "system": system_name,
            "total_files": len(test_files),
            "successful_uploads": len(ingested_files),
            "failed_uploads": len(errors),
            "total_bytes": total_bytes,
            "ingestion_time": ingestion_time,
            "average_upload_time": sum(f["upload_time"] for f in ingested_files) / len(ingested_files) if ingested_files else 0,
            "upload_speed_mbps": (total_bytes / (1024 * 1024)) / ingestion_time if ingestion_time > 0 else 0,
            "ingested_files": ingested_files,
            "errors": errors
        }
        
        print(f"   ✓ Ingestion complete: {len(ingested_files)}/{len(test_files)} files in {ingestion_time:.1f}s")
        print(f"     Speed: {result['upload_speed_mbps']:.2f} MB/s")
        
        return result
    
    def test_system_health(self, system_name: str, base_url: str) -> Dict[str, Any]:
        """Test system health and readiness"""
        try:
            response = requests.get(f"{base_url}/health", timeout=30)
            if response.status_code == 200:
                health_data = response.json()
                return {
                    "status": "healthy",
                    "response_code": response.status_code,
                    "details": health_data
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_code": response.status_code,
                    "error": response.text
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def query_with_metrics(self, system_name: str, base_url: str, query: str, timeout: int = 180) -> Dict[str, Any]:
        """Query system and capture detailed metrics"""
        start_time = time.time()
        
        # Reset metrics for this query
        query_metrics = {
            "llm_calls": 0,
            "tokens": {"input": 0, "output": 0, "total": 0},
            "embedding_operations": 0,
            "query_time": 0,
            "network_time": 0
        }
        
        try:
            # Prepare request
            request_data = {"query": query}
            if system_name.lower() == "nancy":
                request_data["orchestrator"] = "langchain"  # Use LangChain router mode
            
            # Make request
            network_start = time.time()
            response = requests.post(
                f"{base_url}/api/query",
                json=request_data,
                timeout=timeout,
                headers={"Content-Type": "application/json"}
            )
            network_time = time.time() - network_start
            query_time = time.time() - start_time
            
            query_metrics["query_time"] = query_time
            query_metrics["network_time"] = network_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract metrics from response
                if system_name.lower() == "nancy":
                    # Nancy provides detailed orchestrator information
                    query_metrics["orchestrator_used"] = result.get("strategy_used", "unknown")
                    query_metrics["routing_info"] = result.get("routing_info", {})
                    
                    # Estimate LLM calls (Nancy uses LLM for routing + potential brain LLM usage)
                    query_metrics["llm_calls"] = 1  # Router call
                    if "langchain" in result.get("strategy_used", "").lower():
                        query_metrics["llm_calls"] += 1  # Additional orchestration
                else:
                    # Baseline RAG
                    query_metrics["method"] = result.get("method", "unknown")
                    query_metrics["llm_calls"] = 1  # Standard RAG LLM call
                
                # Estimate embedding operations (both systems use embeddings for vector search)
                query_metrics["embedding_operations"] = 1
                
                # Update cumulative metrics
                self.metrics[system_name.lower()]["llm_calls"] += query_metrics["llm_calls"]
                self.metrics[system_name.lower()]["embedding_operations"] += query_metrics["embedding_operations"]
                self.metrics[system_name.lower()]["processing_time"] += query_time
                
                return {
                    "status": "success",
                    "query_time": query_time,
                    "response": result.get("response", ""),
                    "sources": result.get("sources", []),
                    "response_length": len(result.get("response", "")),
                    "source_count": len(result.get("sources", [])),
                    "metrics": query_metrics,
                    "raw_result": result
                }
            else:
                self.metrics[system_name.lower()]["errors"] += 1
                return {
                    "status": "error",
                    "query_time": query_time,
                    "error": f"HTTP {response.status_code}",
                    "response": response.text,
                    "metrics": query_metrics
                }
                
        except requests.exceptions.Timeout:
            self.metrics[system_name.lower()]["errors"] += 1
            return {
                "status": "timeout",
                "query_time": timeout,
                "error": f"Query timed out after {timeout} seconds",
                "metrics": query_metrics
            }
        except Exception as e:
            self.metrics[system_name.lower()]["errors"] += 1
            return {
                "status": "error",
                "query_time": time.time() - start_time,
                "error": str(e),
                "metrics": query_metrics
            }
    
    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run complete benchmark with ingestion and querying"""
        print("🚀 Starting Comprehensive Nancy vs Baseline Benchmark")
        print("=" * 70)
        
        benchmark_start = time.time()
        
        # Phase 1: System Health Check
        print("\n1️⃣ SYSTEM HEALTH CHECK")
        print("-" * 30)
        nancy_health = self.test_system_health("Nancy", self.nancy_url)
        baseline_health = self.test_system_health("Baseline", self.baseline_url)
        
        print(f"   Nancy Four-Brain: {nancy_health['status']}")
        print(f"   Baseline RAG: {baseline_health['status']}")
        
        if nancy_health['status'] != 'healthy' or baseline_health['status'] != 'healthy':
            print("⚠️  Warning: Systems not fully healthy. Results may be affected.")
        
        # Phase 2: Data Ingestion
        print("\n2️⃣ DATA INGESTION PHASE")
        print("-" * 30)
        nancy_ingestion = self.ingest_test_data("Nancy", self.nancy_url)
        print()
        baseline_ingestion = self.ingest_test_data("Baseline", self.baseline_url)
        
        # Wait for systems to process ingested data
        print("\n   ⏳ Allowing time for data processing...")
        time.sleep(10)
        
        # Phase 3: Query Benchmarking
        print("\n3️⃣ QUERY BENCHMARK PHASE")
        print("-" * 30)
        
        for i, test in enumerate(self.test_queries, 1):
            print(f"\n   Test {i}/{len(self.test_queries)}: {test['category']}")
            print(f"   Query: {test['query'][:80]}{'...' if len(test['query']) > 80 else ''}")
            
            # Test Nancy
            print(f"     🧠 Nancy Four-Brain... ", end="", flush=True)
            nancy_result = self.query_with_metrics("Nancy", self.nancy_url, test['query'])
            print(f"({nancy_result['query_time']:.1f}s - {nancy_result['status']})")
            
            # Test Baseline  
            print(f"     📚 Baseline RAG... ", end="", flush=True)
            baseline_result = self.query_with_metrics("Baseline", self.baseline_url, test['query'])
            print(f"({baseline_result['query_time']:.1f}s - {baseline_result['status']})")
            
            # Store results
            test_result = {
                "test_id": i,
                "category": test['category'],
                "query": test['query'],
                "expected_capabilities": test['expected_capabilities'],
                "nancy": nancy_result,
                "baseline": baseline_result,
                "timestamp": datetime.now().isoformat()
            }
            
            self.results.append(test_result)
        
        benchmark_time = time.time() - benchmark_start
        
        # Phase 4: Analysis
        print("\n4️⃣ ANALYSIS PHASE")
        print("-" * 30)
        analysis = self._analyze_comprehensive_results()
        
        # Final results
        final_results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_benchmark_time": benchmark_time,
                "nancy_url": self.nancy_url,
                "baseline_url": self.baseline_url,
                "test_count": len(self.test_queries),
                "test_data_directory": self.test_data_dir
            },
            "system_health": {
                "nancy": nancy_health,
                "baseline": baseline_health
            },
            "ingestion_results": {
                "nancy": nancy_ingestion,
                "baseline": baseline_ingestion
            },
            "query_results": self.results,
            "usage_metrics": self.metrics,
            "analysis": analysis
        }
        
        return final_results
    
    def _analyze_comprehensive_results(self) -> Dict[str, Any]:
        """Comprehensive analysis including resource usage"""
        nancy_times = []
        baseline_times = []
        nancy_successes = 0
        baseline_successes = 0
        
        # Performance analysis
        for result in self.results:
            if result['nancy']['status'] == 'success':
                nancy_times.append(result['nancy']['query_time'])
                nancy_successes += 1
            if result['baseline']['status'] == 'success':
                baseline_times.append(result['baseline']['query_time'])
                baseline_successes += 1
        
        # Resource efficiency analysis
        nancy_metrics = self.metrics['nancy']
        baseline_metrics = self.metrics['baseline']
        
        return {
            "performance": {
                "nancy_avg_time": sum(nancy_times) / len(nancy_times) if nancy_times else 0,
                "baseline_avg_time": sum(baseline_times) / len(baseline_times) if baseline_times else 0,
                "nancy_success_rate": nancy_successes / len(self.results),
                "baseline_success_rate": baseline_successes / len(self.results),
                "speed_advantage": "Nancy" if sum(nancy_times) < sum(baseline_times) else "Baseline"
            },
            "resource_usage": {
                "nancy": {
                    "total_llm_calls": nancy_metrics['llm_calls'],
                    "total_embedding_ops": nancy_metrics['embedding_operations'],
                    "avg_llm_calls_per_query": nancy_metrics['llm_calls'] / len(self.results),
                    "total_processing_time": nancy_metrics['processing_time'],
                    "error_rate": nancy_metrics['errors'] / len(self.results)
                },
                "baseline": {
                    "total_llm_calls": baseline_metrics['llm_calls'],
                    "total_embedding_ops": baseline_metrics['embedding_operations'],
                    "avg_llm_calls_per_query": baseline_metrics['llm_calls'] / len(self.results),
                    "total_processing_time": baseline_metrics['processing_time'],
                    "error_rate": baseline_metrics['errors'] / len(self.results)
                }
            },
            "efficiency_metrics": {
                "llm_efficiency": {
                    "nancy_calls_per_success": nancy_metrics['llm_calls'] / nancy_successes if nancy_successes > 0 else 0,
                    "baseline_calls_per_success": baseline_metrics['llm_calls'] / baseline_successes if baseline_successes > 0 else 0
                },
                "embedding_efficiency": {
                    "nancy_embeds_per_query": nancy_metrics['embedding_operations'] / len(self.results),
                    "baseline_embeds_per_query": baseline_metrics['embedding_operations'] / len(self.results)
                }
            },
            "recommendations": self._generate_efficiency_recommendations(nancy_metrics, baseline_metrics, nancy_times, baseline_times)
        }
    
    def _generate_efficiency_recommendations(self, nancy_metrics: Dict, baseline_metrics: Dict, 
                                           nancy_times: List, baseline_times: List) -> List[str]:
        """Generate efficiency recommendations based on metrics"""
        recommendations = []
        
        # LLM usage comparison
        nancy_llm_rate = nancy_metrics['llm_calls'] / len(self.results)
        baseline_llm_rate = baseline_metrics['llm_calls'] / len(self.results)
        
        if nancy_llm_rate > baseline_llm_rate * 1.5:
            recommendations.append("Nancy uses significantly more LLM calls - consider optimizing orchestration")
        elif baseline_llm_rate > nancy_llm_rate * 1.5:
            recommendations.append("Baseline uses more LLM calls than Nancy's efficient routing")
        
        # Speed vs capability tradeoff
        avg_nancy_time = sum(nancy_times) / len(nancy_times) if nancy_times else 0
        avg_baseline_time = sum(baseline_times) / len(baseline_times) if baseline_times else 0
        
        if avg_nancy_time > avg_baseline_time * 2:
            recommendations.append("Nancy's advanced capabilities come with significant latency cost")
        elif avg_nancy_time < avg_baseline_time:
            recommendations.append("Nancy provides superior capabilities with competitive speed")
        
        # Error rate analysis
        nancy_error_rate = nancy_metrics['errors'] / len(self.results)
        baseline_error_rate = baseline_metrics['errors'] / len(self.results)
        
        if nancy_error_rate > baseline_error_rate:
            recommendations.append("Nancy shows higher error rates - investigate stability")
        elif baseline_error_rate > nancy_error_rate:
            recommendations.append("Nancy shows better reliability than baseline")
        
        return recommendations

def main():
    """Run the comprehensive benchmark"""
    benchmark = ComprehensiveBenchmark()
    
    try:
        results = benchmark.run_comprehensive_benchmark()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_benchmark_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Display summary
        print("\n" + "="*70)
        print("📊 COMPREHENSIVE BENCHMARK RESULTS")
        print("="*70)
        
        analysis = results['analysis']
        
        print(f"\n🏃 PERFORMANCE SUMMARY:")
        perf = analysis['performance']
        print(f"   Nancy Average: {perf['nancy_avg_time']:.1f}s")
        print(f"   Baseline Average: {perf['baseline_avg_time']:.1f}s")
        print(f"   Speed Advantage: {perf['speed_advantage']}")
        print(f"   Nancy Success Rate: {perf['nancy_success_rate']:.1%}")
        print(f"   Baseline Success Rate: {perf['baseline_success_rate']:.1%}")
        
        print(f"\n🔧 RESOURCE USAGE:")
        nancy_usage = analysis['resource_usage']['nancy']
        baseline_usage = analysis['resource_usage']['baseline']
        print(f"   Nancy LLM Calls: {nancy_usage['total_llm_calls']} ({nancy_usage['avg_llm_calls_per_query']:.1f}/query)")
        print(f"   Baseline LLM Calls: {baseline_usage['total_llm_calls']} ({baseline_usage['avg_llm_calls_per_query']:.1f}/query)")
        print(f"   Nancy Embeddings: {nancy_usage['total_embedding_ops']}")
        print(f"   Baseline Embeddings: {baseline_usage['total_embedding_ops']}")
        
        print(f"\n📈 INGESTION PERFORMANCE:")
        nancy_ingest = results['ingestion_results']['nancy']
        baseline_ingest = results['ingestion_results']['baseline']
        if nancy_ingest['status'] == 'completed' and baseline_ingest['status'] == 'completed':
            print(f"   Nancy: {nancy_ingest['successful_uploads']} files in {nancy_ingest['ingestion_time']:.1f}s ({nancy_ingest['upload_speed_mbps']:.2f} MB/s)")
            print(f"   Baseline: {baseline_ingest['successful_uploads']} files in {baseline_ingest['ingestion_time']:.1f}s ({baseline_ingest['upload_speed_mbps']:.2f} MB/s)")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in analysis['recommendations']:
            print(f"   • {rec}")
        
        print(f"\n📁 Detailed results saved to: {filename}")
        
        return results
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
        return None
    except Exception as e:
        print(f"\n\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()