"""
Benchmark Framework for Three-Brain Architecture vs Standard RAG
Designed for multidisciplinary engineering teams with varying information needs.
"""

import json
import time
import statistics
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from .query_orchestrator import QueryOrchestrator

@dataclass
class BenchmarkQuery:
    """Represents a benchmark query with expected results"""
    query: str
    discipline: str  # e.g., "mechanical", "electrical", "systems", "industrial_design", "pm"
    query_type: str  # e.g., "author_attribution", "metadata_filter", "semantic", "relationship"
    expected_docs: List[str]  # Expected relevant document filenames
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

class StandardRAGBaseline:
    """Simple vector-only RAG for comparison"""
    def __init__(self):
        from .nlp import VectorBrain
        self.vector_brain = VectorBrain()
    
    def query(self, query_text: str, n_results: int = 10):
        """Vector-only query without metadata or knowledge graph enrichment"""
        vector_results = self.vector_brain.query(query_texts=[query_text], n_results=n_results)
        
        # Extract just the basic information
        results = []
        if vector_results and vector_results.get('ids'):
            for i, id_list in enumerate(vector_results['ids']):
                for j, chunk_id in enumerate(id_list):
                    doc_id = vector_results['metadatas'][i][j].get('source', 'unknown')
                    results.append({
                        "chunk_id": chunk_id,
                        "document_id": doc_id,
                        "distance": vector_results['distances'][i][j],
                        "text": vector_results['documents'][i][j]
                    })
        
        return {"status": "success", "results": results}

class MultidisciplinaryBenchmark:
    """Benchmark framework for evaluating three-brain architecture benefits"""
    
    def __init__(self):
        self.three_brain_orchestrator = QueryOrchestrator()
        self.standard_rag = StandardRAGBaseline()
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
                query="Show me all CAD files and stress analysis from last month",
                discipline="mechanical",
                query_type="metadata_filter",
                expected_docs=["stress_analysis_march.txt", "cad_review_notes.txt"],
                description="Mechanical engineer reviewing recent design work"
            ),
            BenchmarkQuery(
                query="What materials were considered for the housing design?",
                discipline="mechanical",
                query_type="semantic",
                expected_docs=["material_selection_matrix.txt", "housing_design_review.txt"],
                description="Material selection research"
            ),
            
            # Electrical Engineering Queries
            BenchmarkQuery(
                query="What documents reference the power supply schematic?",
                discipline="electrical",
                query_type="relationship",
                expected_docs=["power_supply_v3.txt", "electrical_review_meeting.txt", "pcb_layout_notes.txt"],
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
                expected_docs=["firmware_requirements.txt", "memory_allocation_plan.txt"],
                description="Firmware engineer checking memory constraints"
            ),
            BenchmarkQuery(
                query="Which documents discuss the communication protocol implementation?",
                discipline="firmware",
                query_type="semantic",
                expected_docs=["comm_protocol_spec.txt", "firmware_architecture.txt"],
                description="Protocol implementation research"
            ),
            
            # Industrial Design Queries
            BenchmarkQuery(
                query="What user feedback influenced the interface design?",
                discipline="industrial_design",
                query_type="semantic",
                expected_docs=["user_research_summary.txt", "voice_of_customer.txt", "interface_mockups.txt"],
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
                expected_docs=["march_design_review_transcript.txt", "decision_matrix_march.txt"],
                description="PM tracking design decisions"
            ),
            BenchmarkQuery(
                query="Which documents are related to the budget constraints discussion?",
                discipline="pm",
                query_type="relationship",
                expected_docs=["budget_review.txt", "cost_analysis.txt", "march_design_review_transcript.txt"],
                description="Finding budget-related documentation"
            ),
            
            # Cross-Disciplinary Queries (the real power of three-brain)
            BenchmarkQuery(
                query="What thermal issues did Sarah Chen identify that affected Mike's electrical design?",
                discipline="cross_disciplinary",
                query_type="relationship",
                expected_docs=["thermal_constraints_doc.txt", "electrical_review_meeting.txt", "design_conflict_resolution.txt"],
                expected_author="Sarah Chen",
                description="Complex cross-team dependency tracking"
            ),
            BenchmarkQuery(
                query="Show me all documents from the last two weeks that mention power consumption",
                discipline="cross_disciplinary",
                query_type="metadata_filter",
                expected_docs=["power_analysis_report.txt", "system_requirements_v2.txt", "electrical_review_meeting.txt"],
                description="Recent power-related work across all disciplines"
            )
        ]
    
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
    
    def _extract_doc_names(self, results: List[Dict]) -> List[str]:
        """Extract document names from query results"""
        doc_names = []
        for result in results:
            if 'document_metadata' in result and result['document_metadata']:
                doc_names.append(result['document_metadata']['filename'])
            elif 'document_id' in result:
                doc_names.append(result['document_id'])
        return doc_names
    
    def run_single_benchmark(self, query: BenchmarkQuery, system_type: str = "three_brain") -> BenchmarkResult:
        """Run a single benchmark query"""
        start_time = time.time()
        
        if system_type == "three_brain":
            response = self.three_brain_orchestrator.query(query.query, n_results=10)
        else:  # standard_rag
            response = self.standard_rag.query(query.query, n_results=10)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Extract retrieved documents
        results = response.get('results', [])
        retrieved_docs = self._extract_doc_names(results)
        
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
        for query in self.benchmark_queries:
            print(f"Testing: {query.description}")
            
            # Test three-brain system
            tb_result = self.run_single_benchmark(query, "three_brain")
            three_brain_results.append(tb_result)
            
            # Test standard RAG
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