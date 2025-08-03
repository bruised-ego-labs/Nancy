#!/usr/bin/env python3
"""
Benchmark Runner for Nancy Three-Brain Architecture (API Version)
Uses the Nancy API endpoints instead of direct database access to avoid locking issues.
"""

import json
import time
import requests
import statistics
from datetime import datetime
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class BenchmarkQuery:
    """Represents a benchmark query with expected results"""
    query: str
    discipline: str
    query_type: str
    expected_docs: List[str]
    expected_author: str = None
    description: str = ""

@dataclass
class BenchmarkResult:
    """Results from a single benchmark query"""
    query: str
    discipline: str
    query_type: str
    retrieved_docs: List[str]
    precision_at_k: float
    recall_at_k: float
    f1_score: float
    mrr: float
    response_time: float
    found_expected_author: bool
    total_results: int

class APIBenchmark:
    """Benchmark using Nancy API endpoints"""
    
    def __init__(self, api_base_url="http://localhost:8000"):
        self.api_base_url = api_base_url
        self.benchmark_queries = self._create_benchmark_queries()
    
    def _create_benchmark_queries(self) -> List[BenchmarkQuery]:
        """Create realistic queries from different engineering disciplines"""
        return [
            # Systems Engineering Queries
            BenchmarkQuery(
                query="What are the system requirements for power consumption?",
                discipline="systems",
                query_type="semantic",
                expected_docs=["system_requirements_v2.txt", "power_analysis_report.txt"],
                description="Systems engineer looking for power requirements"
            ),
            BenchmarkQuery(
                query="Who defined the thermal constraints for the enclosure?",
                discipline="systems",
                query_type="author_attribution",
                expected_docs=["thermal_constraints_doc.txt"],
                expected_author="Sarah Chen",
                description="Finding accountability for thermal decisions"
            ),
            
            # Mechanical Engineering Queries
            BenchmarkQuery(
                query="What materials were considered for the housing design?",
                discipline="mechanical",
                query_type="semantic",
                expected_docs=["march_design_review_transcript.txt", "voice_of_customer.txt"],
                description="Material selection research"
            ),
            
            # Electrical Engineering Queries
            BenchmarkQuery(
                query="What documents reference the power supply schematic?",
                discipline="electrical",
                query_type="relationship",
                expected_docs=["electrical_review_meeting.txt", "march_design_review_transcript.txt"],
                description="Finding all references to power supply design"
            ),
            BenchmarkQuery(
                query="Who approved the EMC testing results?",
                discipline="electrical",
                query_type="author_attribution",
                expected_docs=["emc_test_results.txt"],
                expected_author="Mike Rodriguez",
                description="Finding approval authority for compliance testing"
            ),
            
            # Firmware Engineering Queries
            BenchmarkQuery(
                query="What are the memory requirements mentioned in firmware specs?",
                discipline="firmware",
                query_type="semantic",
                expected_docs=["firmware_requirements.txt", "power_analysis_report.txt"],
                description="Firmware engineer checking memory constraints"
            ),
            BenchmarkQuery(
                query="Which documents discuss the communication protocol implementation?",
                discipline="firmware",
                query_type="semantic",
                expected_docs=["firmware_requirements.txt", "system_requirements_v2.txt"],
                description="Protocol implementation research"
            ),
            
            # Industrial Design Queries
            BenchmarkQuery(
                query="What user feedback influenced the interface design?",
                discipline="industrial_design",
                query_type="semantic",
                expected_docs=["voice_of_customer.txt", "ergonomic_analysis.txt"],
                description="Design decisions based on user input"
            ),
            BenchmarkQuery(
                query="Who created the ergonomic study for the device?",
                discipline="industrial_design",
                query_type="author_attribution",
                expected_docs=["ergonomic_analysis.txt"],
                expected_author="Lisa Park",
                description="Finding ergonomic study author"
            ),
            
            # Project Management Queries
            BenchmarkQuery(
                query="What decisions were made in the March design review meeting?",
                discipline="pm",
                query_type="semantic",
                expected_docs=["march_design_review_transcript.txt"],
                description="PM tracking design decisions"
            ),
            BenchmarkQuery(
                query="Which documents are related to the budget constraints discussion?",
                discipline="pm",
                query_type="relationship",
                expected_docs=["march_design_review_transcript.txt"],
                description="Finding budget-related documentation"
            ),
            
            # Cross-Disciplinary Queries
            BenchmarkQuery(
                query="What thermal issues did Sarah Chen identify that affected electrical design?",
                discipline="cross_disciplinary",
                query_type="relationship",
                expected_docs=["thermal_constraints_doc.txt", "electrical_review_meeting.txt"],
                expected_author="Sarah Chen",
                description="Complex cross-team dependency tracking"
            ),
            BenchmarkQuery(
                query="Show me all documents that mention power consumption",
                discipline="cross_disciplinary",
                query_type="semantic",
                expected_docs=["power_analysis_report.txt", "system_requirements_v2.txt", "electrical_review_meeting.txt"],
                description="Power-related work across all disciplines"
            )
        ]
    
    def setup_test_data(self):
        """Ingest test data via API"""
        test_files = [
            ("system_requirements_v2.txt", "Sarah Chen"),
            ("thermal_constraints_doc.txt", "Sarah Chen"), 
            ("electrical_review_meeting.txt", "Mike Rodriguez"),
            ("emc_test_results.txt", "Mike Rodriguez"),
            ("voice_of_customer.txt", "Lisa Park"),
            ("march_design_review_transcript.txt", "Jennifer Adams"),
            ("ergonomic_analysis.txt", "Lisa Park"),
            ("power_analysis_report.txt", "Tom Wilson"),
            ("firmware_requirements.txt", "Tom Wilson")
        ]
        
        print("Setting up test data via API...")
        successful_ingestions = 0
        
        for filename, author in test_files:
            filepath = f"benchmark_test_data/{filename}"
            
            try:
                with open(filepath, 'rb') as f:
                    files = {'file': (filename, f, 'text/plain')}
                    data = {'author': author}
                    
                    response = requests.post(
                        f"{self.api_base_url}/api/ingest",
                        files=files,
                        data=data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        print(f"Successfully ingested {filename} by {author}")
                        successful_ingestions += 1
                    else:
                        print(f"Failed to ingest {filename}: {response.status_code}")
                        
            except Exception as e:
                print(f"Error ingesting {filename}: {e}")
        
        print(f"Successfully ingested {successful_ingestions}/{len(test_files)} documents")
        time.sleep(2)  # Give system time to process
        return successful_ingestions
    
    def query_nancy_api(self, query_text: str, n_results: int = 10) -> Dict:
        """Query Nancy's three-brain system via API"""
        try:
            response = requests.post(
                f"{self.api_base_url}/api/query",
                json={"query": query_text, "n_results": n_results},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API query failed: {response.status_code}")
                return {"status": "error", "results": []}
                
        except Exception as e:
            print(f"API query error: {e}")
            return {"status": "error", "results": []}
    
    def simulate_standard_rag(self, query_text: str, n_results: int = 10) -> Dict:
        """Simulate standard RAG by removing author and metadata info from Nancy results"""
        nancy_results = self.query_nancy_api(query_text, n_results)
        
        # Strip out three-brain specific information to simulate standard RAG
        if nancy_results.get("results"):
            simplified_results = []
            for result in nancy_results["results"]:
                simplified_results.append({
                    "text": result.get("text", ""),
                    "distance": result.get("distance", 1.0),
                    "document_id": result.get("document_metadata", {}).get("filename", "unknown") if result.get("document_metadata") else "unknown"
                })
            
            return {"status": "success", "results": simplified_results}
        
        return nancy_results
    
    def _calculate_precision_recall(self, retrieved_docs: List[str], expected_docs: List[str], k: int = 10) -> Tuple[float, float, float]:
        """Calculate precision@k, recall@k, and F1 score"""
        retrieved_set = set(retrieved_docs[:k])
        expected_set = set(expected_docs)
        
        if not retrieved_set:
            return 0.0, 0.0, 0.0
        
        relevant_retrieved = retrieved_set.intersection(expected_set)
        
        precision = len(relevant_retrieved) / len(retrieved_set) if retrieved_set else 0.0
        recall = len(relevant_retrieved) / len(expected_set) if expected_set else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return precision, recall, f1
    
    def _calculate_mrr(self, retrieved_docs: List[str], expected_docs: List[str]) -> float:
        """Calculate Mean Reciprocal Rank"""
        expected_set = set(expected_docs)
        
        for i, doc in enumerate(retrieved_docs):
            if doc in expected_set:
                return 1.0 / (i + 1)
        
        return 0.0
    
    def _extract_doc_names(self, results: List[Dict], system_type: str) -> List[str]:
        """Extract document names from query results"""
        doc_names = []
        for result in results:
            if system_type == "three_brain":
                if result.get('document_metadata') and result['document_metadata'].get('filename'):
                    doc_names.append(result['document_metadata']['filename'])
            else:  # standard_rag
                if result.get('document_id'):
                    doc_names.append(result['document_id'])
        return doc_names
    
    def run_single_benchmark(self, query: BenchmarkQuery, system_type: str = "three_brain") -> BenchmarkResult:
        """Run a single benchmark query"""
        start_time = time.time()
        
        if system_type == "three_brain":
            response = self.query_nancy_api(query.query, n_results=10)
        else:  # standard_rag
            response = self.simulate_standard_rag(query.query, n_results=10)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Extract retrieved documents
        results = response.get('results', [])
        retrieved_docs = self._extract_doc_names(results, system_type)
        
        # Calculate metrics
        precision, recall, f1 = self._calculate_precision_recall(retrieved_docs, query.expected_docs)
        mrr = self._calculate_mrr(retrieved_docs, query.expected_docs)
        
        # Check if expected author was found (for three-brain system)
        found_expected_author = False
        if query.expected_author and system_type == "three_brain":
            for result in results:
                if result.get('author') == query.expected_author:
                    found_expected_author = True
                    break
        
        return BenchmarkResult(
            query=query.query,
            discipline=query.discipline,
            query_type=query.query_type,
            retrieved_docs=retrieved_docs,
            precision_at_k=precision,
            recall_at_k=recall,
            f1_score=f1,
            mrr=mrr,
            response_time=response_time,
            found_expected_author=found_expected_author,
            total_results=len(results)
        )
    
    def run_full_benchmark(self) -> Dict[str, Any]:
        """Run complete benchmark comparing three-brain vs standard RAG"""
        print("Starting comprehensive benchmark...")
        
        three_brain_results = []
        standard_rag_results = []
        
        # Run all queries on both systems
        for i, query in enumerate(self.benchmark_queries, 1):
            print(f"[{i}/{len(self.benchmark_queries)}] Testing: {query.description}")
            
            # Test three-brain system
            tb_result = self.run_single_benchmark(query, "three_brain")
            three_brain_results.append(tb_result)
            
            # Test standard RAG simulation
            sr_result = self.run_single_benchmark(query, "standard_rag")
            standard_rag_results.append(sr_result)
        
        # Calculate aggregate metrics
        tb_metrics = self._calculate_aggregate_metrics(three_brain_results)
        sr_metrics = self._calculate_aggregate_metrics(standard_rag_results)
        
        # Analyze by discipline
        discipline_analysis = self._analyze_by_discipline(three_brain_results, standard_rag_results)
        
        return {
            "three_brain_metrics": tb_metrics,
            "standard_rag_metrics": sr_metrics,
            "discipline_analysis": discipline_analysis,
            "detailed_results": {
                "three_brain": [self._result_to_dict(r) for r in three_brain_results],
                "standard_rag": [self._result_to_dict(r) for r in standard_rag_results]
            }
        }
    
    def _calculate_aggregate_metrics(self, results: List[BenchmarkResult]) -> Dict[str, float]:
        """Calculate aggregate metrics across all queries"""
        if not results:
            return {}
        
        return {
            "avg_precision": statistics.mean([r.precision_at_k for r in results]),
            "avg_recall": statistics.mean([r.recall_at_k for r in results]),
            "avg_f1": statistics.mean([r.f1_score for r in results]),
            "avg_mrr": statistics.mean([r.mrr for r in results]),
            "avg_response_time": statistics.mean([r.response_time for r in results]),
            "author_attribution_accuracy": sum([r.found_expected_author for r in results]) / len(results),
            "total_queries": len(results)
        }
    
    def _analyze_by_discipline(self, tb_results: List[BenchmarkResult], sr_results: List[BenchmarkResult]) -> Dict[str, Dict]:
        """Analyze performance by engineering discipline"""
        disciplines = set([r.discipline for r in tb_results])
        analysis = {}
        
        for discipline in disciplines:
            tb_discipline = [r for r in tb_results if r.discipline == discipline]
            sr_discipline = [r for r in sr_results if r.discipline == discipline]
            
            analysis[discipline] = {
                "three_brain": self._calculate_aggregate_metrics(tb_discipline),
                "standard_rag": self._calculate_aggregate_metrics(sr_discipline),
                "improvement_factors": self._calculate_improvements(tb_discipline, sr_discipline)
            }
        
        return analysis
    
    def _calculate_improvements(self, tb_results: List[BenchmarkResult], sr_results: List[BenchmarkResult]) -> Dict[str, float]:
        """Calculate improvement factors (three-brain vs standard RAG)"""
        if not tb_results or not sr_results:
            return {}
        
        tb_avg_f1 = statistics.mean([r.f1_score for r in tb_results])
        sr_avg_f1 = statistics.mean([r.f1_score for r in sr_results])
        
        tb_avg_recall = statistics.mean([r.recall_at_k for r in tb_results])
        sr_avg_recall = statistics.mean([r.recall_at_k for r in sr_results])
        
        return {
            "f1_improvement": (tb_avg_f1 - sr_avg_f1) / sr_avg_f1 if sr_avg_f1 > 0 else 0,
            "recall_improvement": (tb_avg_recall - sr_avg_recall) / sr_avg_recall if sr_avg_recall > 0 else 0,
            "author_attribution_advantage": statistics.mean([r.found_expected_author for r in tb_results])
        }
    
    def _result_to_dict(self, result: BenchmarkResult) -> Dict:
        """Convert BenchmarkResult to dictionary for JSON serialization"""
        return {
            "query": result.query,
            "discipline": result.discipline,
            "query_type": result.query_type,
            "retrieved_docs": result.retrieved_docs,
            "precision_at_k": result.precision_at_k,
            "recall_at_k": result.recall_at_k,
            "f1_score": result.f1_score,
            "mrr": result.mrr,
            "response_time": result.response_time,
            "found_expected_author": result.found_expected_author,
            "total_results": result.total_results
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = "benchmark_results.json"):
        """Save benchmark results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Benchmark results saved to {filename}")

def print_summary_report(results):
    """Print a formatted summary of benchmark results"""
    if not results:
        print("No results to display")
        return
        
    print("\n" + "="*60)
    print("BENCHMARK RESULTS SUMMARY")
    print("="*60)
    
    tb_metrics = results['three_brain_metrics']
    sr_metrics = results['standard_rag_metrics']
    
    print(f"\nOVERALL PERFORMANCE COMPARISON")
    print("-" * 40)
    print(f"{'Metric':<25} {'Three-Brain':<12} {'Standard RAG':<12} {'Improvement'}")
    print("-" * 65)
    
    # Calculate improvements
    def safe_improvement(new_val, old_val):
        return ((new_val - old_val) / old_val * 100) if old_val > 0 else 0
    
    precision_imp = safe_improvement(tb_metrics['avg_precision'], sr_metrics['avg_precision'])
    recall_imp = safe_improvement(tb_metrics['avg_recall'], sr_metrics['avg_recall'])
    f1_imp = safe_improvement(tb_metrics['avg_f1'], sr_metrics['avg_f1'])
    mrr_imp = safe_improvement(tb_metrics['avg_mrr'], sr_metrics['avg_mrr'])
    
    print(f"{'Precision@10':<25} {tb_metrics['avg_precision']:<12.3f} {sr_metrics['avg_precision']:<12.3f} {precision_imp:+.1f}%")
    print(f"{'Recall@10':<25} {tb_metrics['avg_recall']:<12.3f} {sr_metrics['avg_recall']:<12.3f} {recall_imp:+.1f}%")
    print(f"{'F1 Score':<25} {tb_metrics['avg_f1']:<12.3f} {sr_metrics['avg_f1']:<12.3f} {f1_imp:+.1f}%")
    print(f"{'Mean Reciprocal Rank':<25} {tb_metrics['avg_mrr']:<12.3f} {sr_metrics['avg_mrr']:<12.3f} {mrr_imp:+.1f}%")
    print(f"{'Author Attribution':<25} {tb_metrics['author_attribution_accuracy']:<12.3f} {'N/A':<12} {tb_metrics['author_attribution_accuracy']*100:.1f}%")
    
    print(f"\nDISCIPLINE-SPECIFIC ANALYSIS")
    print("-" * 40)
    
    discipline_results = results['discipline_analysis']
    
    for discipline, data in discipline_results.items():
        if discipline == 'cross_disciplinary':
            discipline_name = "Cross-Disciplinary"
        else:
            discipline_name = discipline.replace('_', ' ').title()
        
        print(f"\n{discipline_name}:")
        tb_f1 = data['three_brain']['avg_f1']
        sr_f1 = data['standard_rag']['avg_f1']
        improvement = data['improvement_factors'].get('f1_improvement', 0) * 100
        
        print(f"  F1 Score: {tb_f1:.3f} vs {sr_f1:.3f} ({improvement:+.1f}% improvement)")
        
        if 'author_attribution_advantage' in data['improvement_factors']:
            auth_adv = data['improvement_factors']['author_attribution_advantage'] * 100
            print(f"  Author Attribution: {auth_adv:.1f}% success rate")

def main():
    """Main benchmark execution"""
    print("="*60)
    print("NANCY THREE-BRAIN ARCHITECTURE BENCHMARK")
    print("API-Based Multidisciplinary Team Evaluation")
    print("="*60)
    
    # Check API availability
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print(f"Error: Nancy API returned status {response.status_code}")
            return 1
        print("Nancy API is available")
    except Exception as e:
        print(f"Error connecting to Nancy API: {e}")
        return 1
    
    try:
        benchmark = APIBenchmark()
        
        # Setup test data
        ingested = benchmark.setup_test_data()
        if ingested == 0:
            print("Error: No test data could be ingested")
            return 1
        
        # Run benchmark
        results = benchmark.run_full_benchmark()
        
        # Display results
        print_summary_report(results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"benchmark_results_{timestamp}.json"
        benchmark.save_results(results, filename)
        
        print(f"\nDetailed results saved to: {filename}")
        print("\nBenchmark completed successfully!")
        
        return 0
        
    except Exception as e:
        print(f"Error running benchmark: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())