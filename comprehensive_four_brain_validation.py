#!/usr/bin/env python3
"""
Comprehensive Four-Brain Architecture Validation Suite

Tests Nancy's complete value proposition across all dimensions:
- Vector Brain: Semantic search and content retrieval  
- Analytical Brain: Structured data querying and filtering
- Graph Brain: Relationship discovery and knowledge connections
- Linguistic Brain: Intelligent query routing and synthesis
- Temporal Brain: Time-aware reasoning and causality

Addresses validation-skeptic concerns with rigorous methodology
"""

import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class ComprehensiveFourBrainValidator:
    """Comprehensive validation across all Nancy capabilities"""
    
    def __init__(self):
        self.nancy_url = "http://localhost:8000"
        self.baseline_url = "http://localhost:8002"
        self.test_data_dir = Path("benchmark_test_data")
        
        self.results = {
            "validation_type": "comprehensive_four_brain_validation",
            "timestamp": datetime.now().isoformat(),
            "methodology": "scientific_comparison_across_all_dimensions",
            "test_categories": {
                "vector_brain": {"tests": [], "overall_score": 0},
                "analytical_brain": {"tests": [], "overall_score": 0},
                "graph_brain": {"tests": [], "overall_score": 0},
                "linguistic_brain": {"tests": [], "overall_score": 0},
                "enhanced_graph_brain": {"tests": [], "overall_score": 0},
                "integration": {"tests": [], "overall_score": 0}
            },
            "nancy_status": "unknown",
            "baseline_status": "unknown",
            "final_assessment": {}
        }
    
    def check_service_health(self) -> Dict[str, bool]:
        """Check health of both Nancy and baseline services"""
        nancy_healthy = False
        baseline_healthy = False
        
        try:
            nancy_response = requests.get(f"{self.nancy_url}/health", timeout=10)
            nancy_healthy = nancy_response.status_code == 200
            self.results["nancy_status"] = "healthy" if nancy_healthy else "unhealthy"
        except Exception as e:
            self.results["nancy_status"] = f"failed: {str(e)}"
        
        try:
            baseline_response = requests.get(f"{self.baseline_url}/health", timeout=10)
            baseline_healthy = baseline_response.status_code == 200
            self.results["baseline_status"] = "healthy" if baseline_healthy else "unhealthy"
        except Exception as e:
            self.results["baseline_status"] = f"failed: {str(e)}"
        
        return {"nancy": nancy_healthy, "baseline": baseline_healthy}
    
    def ingest_test_data(self, system_url: str, system_name: str) -> Dict[str, Any]:
        """Ingest test data into specified system"""
        print(f"Ingesting test data into {system_name}...")
        
        try:
            if system_name == "nancy":
                # Nancy uses file upload approach
                return self._ingest_files_to_nancy(system_url)
            else:
                # Baseline uses directory-based ingestion
                response = requests.post(f"{system_url}/api/ingest", timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"Success: {system_name} ingested data successfully")
                    return {"status": "success", "details": result}
                else:
                    print(f"Failed: {system_name} ingestion failed with status {response.status_code}")
                    return {"status": "failed", "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            print(f"Failed: {system_name} ingestion error: {e}")
            return {"status": "error", "error": str(e)}
    
    def _ingest_files_to_nancy(self, nancy_url: str) -> Dict[str, Any]:
        """Upload individual files to Nancy using file upload API"""
        if not self.test_data_dir.exists():
            return {"status": "failed", "error": "Test data directory not found"}
        
        files_processed = 0
        errors = []
        
        # Upload each test file individually
        for file_path in self.test_data_dir.glob("*.txt"):
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': (file_path.name, f, 'text/plain')}
                    data = {'author': 'Test Author'}
                    
                    response = requests.post(
                        f"{nancy_url}/api/ingest",
                        files=files,
                        data=data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        files_processed += 1
                        print(f"  Uploaded: {file_path.name}")
                    else:
                        errors.append(f"{file_path.name}: HTTP {response.status_code}")
                        
            except Exception as e:
                errors.append(f"{file_path.name}: {str(e)}")
        
        # Upload CSV files too
        for file_path in self.test_data_dir.glob("*.csv"):
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': (file_path.name, f, 'text/csv')}
                    data = {'author': 'Test Author'}
                    
                    response = requests.post(
                        f"{nancy_url}/api/ingest",
                        files=files,
                        data=data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        files_processed += 1
                        print(f"  Uploaded: {file_path.name}")
                    else:
                        errors.append(f"{file_path.name}: HTTP {response.status_code}")
                        
            except Exception as e:
                errors.append(f"{file_path.name}: {str(e)}")
        
        if files_processed > 0:
            print(f"Success: Nancy ingested {files_processed} files")
            return {
                "status": "success", 
                "details": {
                    "files_processed": files_processed,
                    "errors": errors
                }
            }
        else:
            print(f"Failed: Nancy ingested 0 files. Errors: {errors}")
            return {"status": "failed", "error": f"No files ingested. Errors: {errors}"}
    
    # VECTOR BRAIN TESTS
    def test_vector_brain_capabilities(self, nancy_healthy: bool, baseline_healthy: bool):
        """Test semantic search and content retrieval capabilities"""
        print("\n=== TESTING VECTOR BRAIN CAPABILITIES ===")
        
        vector_tests = [
            {
                "name": "semantic_similarity_search",
                "query": "What are the thermal management approaches mentioned in the documents?",
                "category": "semantic_search",
                "expected_concepts": ["thermal", "heat", "temperature", "cooling", "thermal management"]
            },
            {
                "name": "cross_document_content_discovery",
                "query": "Find all references to power consumption and electrical requirements",
                "category": "content_discovery", 
                "expected_concepts": ["power", "electrical", "consumption", "requirements", "voltage"]
            },
            {
                "name": "technical_concept_retrieval",
                "query": "What components are mentioned across all engineering documents?",
                "category": "concept_retrieval",
                "expected_concepts": ["components", "parts", "modules", "assemblies"]
            }
        ]
        
        for test in vector_tests:
            nancy_result = self._run_query_test("nancy", test) if nancy_healthy else None
            baseline_result = self._run_query_test("baseline", test) if baseline_healthy else None
            
            test_result = {
                "test_name": test["name"],
                "category": test["category"],
                "query": test["query"],
                "nancy_performance": self._score_vector_response(nancy_result, test["expected_concepts"]) if nancy_result else None,
                "baseline_performance": self._score_vector_response(baseline_result, test["expected_concepts"]) if baseline_result else None,
                "nancy_response": nancy_result["response"] if nancy_result else None,
                "baseline_response": baseline_result["response"] if baseline_result else None
            }
            
            self.results["test_categories"]["vector_brain"]["tests"].append(test_result)
    
    # ANALYTICAL BRAIN TESTS  
    def test_analytical_brain_capabilities(self, nancy_healthy: bool, baseline_healthy: bool):
        """Test structured data querying and filtering capabilities"""
        print("\n=== TESTING ANALYTICAL BRAIN CAPABILITIES ===")
        
        analytical_tests = [
            {
                "name": "structured_data_filtering",
                "query": "What components have thermal constraints above 70 degrees?",
                "category": "data_filtering",
                "expected_elements": ["thermal constraint", "70", "degrees", "components"]
            },
            {
                "name": "metadata_based_search",
                "query": "Show me all test results with priority marked as High",
                "category": "metadata_search",
                "expected_elements": ["test results", "priority", "High"]
            },
            {
                "name": "quantitative_analysis",
                "query": "What are the power requirements for all memory components?",
                "category": "quantitative_analysis",
                "expected_elements": ["power", "requirements", "memory", "components"]
            }
        ]
        
        for test in analytical_tests:
            nancy_result = self._run_query_test("nancy", test) if nancy_healthy else None
            baseline_result = self._run_query_test("baseline", test) if baseline_healthy else None
            
            test_result = {
                "test_name": test["name"],
                "category": test["category"], 
                "query": test["query"],
                "nancy_performance": self._score_analytical_response(nancy_result, test["expected_elements"]) if nancy_result else None,
                "baseline_performance": self._score_analytical_response(baseline_result, test["expected_elements"]) if baseline_result else None,
                "nancy_response": nancy_result["response"] if nancy_result else None,
                "baseline_response": baseline_result["response"] if baseline_result else None
            }
            
            self.results["test_categories"]["analytical_brain"]["tests"].append(test_result)
    
    # GRAPH BRAIN TESTS
    def test_graph_brain_capabilities(self, nancy_healthy: bool, baseline_healthy: bool):
        """Test relationship discovery and knowledge connections"""
        print("\n=== TESTING GRAPH BRAIN CAPABILITIES ===")
        
        graph_tests = [
            {
                "name": "relationship_discovery",
                "query": "Who worked on thermal analysis and what other systems did they influence?",
                "category": "relationship_mapping",
                "expected_elements": ["Sarah Chen", "thermal analysis", "influenced", "systems"]
            },
            {
                "name": "cross_domain_connections",
                "query": "How do electrical decisions impact mechanical design choices?",
                "category": "cross_domain_analysis",
                "expected_elements": ["electrical", "mechanical", "design", "impact", "choices"]
            },
            {
                "name": "authorship_and_expertise",
                "query": "What expertise areas are represented by each team member?",
                "category": "expertise_mapping",
                "expected_elements": ["expertise", "team member", "areas", "represented"]
            }
        ]
        
        for test in graph_tests:
            nancy_result = self._run_query_test("nancy", test) if nancy_healthy else None
            baseline_result = self._run_query_test("baseline", test) if baseline_healthy else None
            
            test_result = {
                "test_name": test["name"],
                "category": test["category"],
                "query": test["query"], 
                "nancy_performance": self._score_graph_response(nancy_result, test["expected_elements"]) if nancy_result else None,
                "baseline_performance": self._score_graph_response(baseline_result, test["expected_elements"]) if baseline_result else None,
                "nancy_response": nancy_result["response"] if nancy_result else None,
                "baseline_response": baseline_result["response"] if baseline_result else None
            }
            
            self.results["test_categories"]["graph_brain"]["tests"].append(test_result)
    
    # LINGUISTIC BRAIN TESTS
    def test_linguistic_brain_capabilities(self, nancy_healthy: bool, baseline_healthy: bool):
        """Test intelligent query routing and synthesis"""
        print("\n=== TESTING LINGUISTIC BRAIN CAPABILITIES ===")
        
        linguistic_tests = [
            {
                "name": "complex_query_decomposition",
                "query": "What thermal constraints affect power management and who made those decisions?",
                "category": "query_decomposition",
                "expected_elements": ["thermal constraints", "power management", "decisions", "who made"]
            },
            {
                "name": "multi_step_reasoning",
                "query": "If we change the enclosure material, what other systems need to be reconsidered?",
                "category": "multi_step_reasoning",
                "expected_elements": ["enclosure material", "other systems", "reconsidered", "change"]
            },
            {
                "name": "synthesis_across_domains",
                "query": "Summarize the key engineering tradeoffs discussed across all disciplines",
                "category": "cross_domain_synthesis",
                "expected_elements": ["engineering tradeoffs", "disciplines", "summarize", "key"]
            }
        ]
        
        for test in linguistic_tests:
            nancy_result = self._run_query_test("nancy", test) if nancy_healthy else None
            baseline_result = self._run_query_test("baseline", test) if baseline_healthy else None
            
            test_result = {
                "test_name": test["name"],
                "category": test["category"],
                "query": test["query"],
                "nancy_performance": self._score_linguistic_response(nancy_result, test["expected_elements"]) if nancy_result else None,
                "baseline_performance": self._score_linguistic_response(baseline_result, test["expected_elements"]) if baseline_result else None,
                "nancy_response": nancy_result["response"] if nancy_result else None,
                "baseline_response": baseline_result["response"] if baseline_result else None
            }
            
            self.results["test_categories"]["linguistic_brain"]["tests"].append(test_result)
    
    # ENHANCED GRAPH BRAIN TESTS (TEMPORAL + RELATIONSHIPS)
    def test_enhanced_graph_brain_capabilities(self, nancy_healthy: bool, baseline_healthy: bool):
        """Test enhanced graph brain with temporal awareness"""
        print("\n=== TESTING ENHANCED GRAPH BRAIN (TEMPORAL + RELATIONSHIPS) ===")
        
        temporal_tests = [
            {
                "name": "relationship_discovery",
                "query": "Who are the thermal experts in the project?",
                "category": "expertise_discovery",
                "expected_elements": ["thermal", "experts", "project"]
            },
            {
                "name": "author_attribution", 
                "query": "Who wrote documents about power management?",
                "category": "authorship_analysis",
                "expected_elements": ["power management", "wrote", "documents"]
            },
            {
                "name": "cross_domain_relationships",
                "query": "How do electrical and thermal systems relate?",
                "category": "system_relationships",
                "expected_elements": ["electrical", "thermal", "systems", "relate"]
            }
        ]
        
        for test in temporal_tests:
            nancy_result = self._run_query_test("nancy", test) if nancy_healthy else None
            baseline_result = self._run_query_test("baseline", test) if baseline_healthy else None
            
            test_result = {
                "test_name": test["name"],
                "category": test["category"],
                "query": test["query"],
                "nancy_performance": self._score_temporal_response(nancy_result, test["expected_elements"]) if nancy_result else None,
                "baseline_performance": self._score_temporal_response(baseline_result, test["expected_elements"]) if baseline_result else None,
                "nancy_response": nancy_result["response"] if nancy_result else None,
                "baseline_response": baseline_result["response"] if baseline_result else None
            }
            
            self.results["test_categories"]["enhanced_graph_brain"]["tests"].append(test_result)
    
    # INTEGRATION TESTS
    def test_integration_capabilities(self, nancy_healthy: bool, baseline_healthy: bool):
        """Test Four-Brain integration and orchestration"""
        print("\n=== TESTING FOUR-BRAIN INTEGRATION ===")
        
        integration_tests = [
            {
                "name": "four_brain_orchestration",
                "query": "Find thermal constraints from Sarah Chen's analysis, show related electrical decisions, and timeline of resulting changes",
                "category": "multi_brain_orchestration",
                "expected_elements": ["thermal constraints", "Sarah Chen", "electrical decisions", "timeline", "changes"]
            },
            {
                "name": "knowledge_synthesis",
                "query": "What patterns exist across our engineering decision-making process and who are the key decision makers?",
                "category": "knowledge_integration",
                "expected_elements": ["patterns", "decision-making", "process", "key decision makers"]
            },
            {
                "name": "comprehensive_analysis",
                "query": "Analyze the complete thermal management approach including constraints, decisions, people, and timeline",
                "category": "comprehensive_integration",
                "expected_elements": ["thermal management", "constraints", "decisions", "people", "timeline"]
            }
        ]
        
        for test in integration_tests:
            nancy_result = self._run_query_test("nancy", test) if nancy_healthy else None
            baseline_result = self._run_query_test("baseline", test) if baseline_healthy else None
            
            test_result = {
                "test_name": test["name"],
                "category": test["category"],
                "query": test["query"],
                "nancy_performance": self._score_integration_response(nancy_result, test["expected_elements"]) if nancy_result else None,
                "baseline_performance": self._score_integration_response(baseline_result, test["expected_elements"]) if baseline_result else None,
                "nancy_response": nancy_result["response"] if nancy_result else None,
                "baseline_response": baseline_result["response"] if baseline_result else None
            }
            
            self.results["test_categories"]["integration"]["tests"].append(test_result)
    
    def _run_query_test(self, system: str, test: Dict) -> Optional[Dict]:
        """Execute query test against specified system"""
        try:
            url = self.nancy_url if system == "nancy" else self.baseline_url
            
            start_time = time.time()
            response = requests.post(
                f"{url}/api/query",
                json={"query": test["query"]},
                timeout=30
            )
            query_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "response": data.get("response", data.get("answer", "")),
                    "sources": data.get("sources", []),
                    "query_time": query_time,
                    "system": system
                }
            else:
                return {
                    "response": f"Error: HTTP {response.status_code}",
                    "sources": [],
                    "query_time": query_time,
                    "system": system,
                    "error": True
                }
                
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "sources": [],
                "query_time": 0,
                "system": system,
                "error": True
            }
    
    def _score_vector_response(self, result: Dict, expected_concepts: List[str]) -> Dict:
        """Score vector brain response quality"""
        if not result or result.get("error"):
            return {"score": 0.0, "reasoning": "Query failed or returned error"}
        
        response = result["response"].lower()
        concepts_found = [concept for concept in expected_concepts if concept.lower() in response]
        base_score = len(concepts_found) / len(expected_concepts)
        
        # Bonus for semantic richness
        semantic_indicators = ["relevant", "similar", "related", "context", "documents"]
        semantic_bonus = sum(0.1 for indicator in semantic_indicators if indicator in response)
        
        final_score = min(1.0, base_score + semantic_bonus * 0.1)
        
        return {
            "score": final_score,
            "concepts_found": concepts_found,
            "semantic_richness": semantic_bonus,
            "query_time": result["query_time"],
            "reasoning": f"Found {len(concepts_found)}/{len(expected_concepts)} expected concepts"
        }
    
    def _score_analytical_response(self, result: Dict, expected_elements: List[str]) -> Dict:
        """Score analytical brain response quality"""
        if not result or result.get("error"):
            return {"score": 0.0, "reasoning": "Query failed or returned error"}
        
        response = result["response"].lower()
        elements_found = [element for element in expected_elements if element.lower() in response]
        base_score = len(elements_found) / len(expected_elements)
        
        # Bonus for structured data handling
        structured_indicators = ["filter", "criteria", "matching", "results", "data", "values"]
        structured_bonus = sum(0.1 for indicator in structured_indicators if indicator in response)
        
        final_score = min(1.0, base_score + structured_bonus * 0.1)
        
        return {
            "score": final_score,
            "elements_found": elements_found,
            "structured_handling": structured_bonus,
            "query_time": result["query_time"],
            "reasoning": f"Found {len(elements_found)}/{len(expected_elements)} expected elements"
        }
    
    def _score_graph_response(self, result: Dict, expected_elements: List[str]) -> Dict:
        """Score graph brain response quality"""
        if not result or result.get("error"):
            return {"score": 0.0, "reasoning": "Query failed or returned error"}
        
        response = result["response"].lower()
        elements_found = [element for element in expected_elements if element.lower() in response]
        base_score = len(elements_found) / len(expected_elements)
        
        # Bonus for relationship indicators
        relationship_indicators = ["connected", "related", "influence", "impact", "collaborated", "worked with"]
        relationship_bonus = sum(0.1 for indicator in relationship_indicators if indicator in response)
        
        final_score = min(1.0, base_score + relationship_bonus * 0.1)
        
        return {
            "score": final_score,
            "elements_found": elements_found,
            "relationship_richness": relationship_bonus,
            "query_time": result["query_time"],
            "reasoning": f"Found {len(elements_found)}/{len(expected_elements)} expected elements"
        }
    
    def _score_linguistic_response(self, result: Dict, expected_elements: List[str]) -> Dict:
        """Score linguistic brain response quality"""
        if not result or result.get("error"):
            return {"score": 0.0, "reasoning": "Query failed or returned error"}
        
        response = result["response"].lower()
        elements_found = [element for element in expected_elements if element.lower() in response]
        base_score = len(elements_found) / len(expected_elements)
        
        # Bonus for synthesis indicators
        synthesis_indicators = ["therefore", "consequently", "analysis shows", "synthesis", "overall", "combining"]
        synthesis_bonus = sum(0.1 for indicator in synthesis_indicators if indicator in response)
        
        final_score = min(1.0, base_score + synthesis_bonus * 0.1)
        
        return {
            "score": final_score,
            "elements_found": elements_found,
            "synthesis_quality": synthesis_bonus,
            "query_time": result["query_time"],
            "reasoning": f"Found {len(elements_found)}/{len(expected_elements)} expected elements"
        }
    
    def _score_temporal_response(self, result: Dict, expected_elements: List[str]) -> Dict:
        """Score temporal brain response quality"""
        if not result or result.get("error"):
            return {"score": 0.0, "reasoning": "Query failed or returned error"}
        
        response = result["response"].lower()
        elements_found = [element for element in expected_elements if element.lower() in response]
        base_score = len(elements_found) / len(expected_elements)
        
        # Bonus for temporal indicators
        temporal_indicators = ["sequence", "timeline", "caused", "led to", "before", "after", "resulted in"]
        temporal_bonus = sum(0.1 for indicator in temporal_indicators if indicator in response)
        
        final_score = min(1.0, base_score + temporal_bonus * 0.1)
        
        return {
            "score": final_score,
            "elements_found": elements_found,
            "temporal_understanding": temporal_bonus,
            "query_time": result["query_time"],
            "reasoning": f"Found {len(elements_found)}/{len(expected_elements)} expected elements"
        }
    
    def _score_integration_response(self, result: Dict, expected_elements: List[str]) -> Dict:
        """Score integration response quality"""
        if not result or result.get("error"):
            return {"score": 0.0, "reasoning": "Query failed or returned error"}
        
        response = result["response"].lower()
        elements_found = [element for element in expected_elements if element.lower() in response]
        base_score = len(elements_found) / len(expected_elements)
        
        # Bonus for integration indicators
        integration_indicators = ["combining", "across", "integration", "comprehensive", "synthesis", "multiple"]
        integration_bonus = sum(0.1 for indicator in integration_indicators if indicator in response)
        
        final_score = min(1.0, base_score + integration_bonus * 0.1)
        
        return {
            "score": final_score,
            "elements_found": elements_found,
            "integration_quality": integration_bonus,
            "query_time": result["query_time"],
            "reasoning": f"Found {len(elements_found)}/{len(expected_elements)} expected elements"
        }
    
    def calculate_overall_scores(self):
        """Calculate overall scores for each brain category"""
        for category, data in self.results["test_categories"].items():
            if data["tests"]:
                nancy_scores = []
                baseline_scores = []
                
                for test in data["tests"]:
                    if test.get("nancy_performance") and not test["nancy_performance"].get("error"):
                        nancy_scores.append(test["nancy_performance"]["score"])
                    if test.get("baseline_performance") and not test["baseline_performance"].get("error"):
                        baseline_scores.append(test["baseline_performance"]["score"])
                
                data["nancy_avg_score"] = sum(nancy_scores) / len(nancy_scores) if nancy_scores else 0
                data["baseline_avg_score"] = sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0
                data["nancy_test_count"] = len(nancy_scores)
                data["baseline_test_count"] = len(baseline_scores)
    
    def generate_final_assessment(self):
        """Generate comprehensive final assessment"""
        self.calculate_overall_scores()
        
        # Calculate overall system scores
        nancy_total_score = 0
        baseline_total_score = 0
        category_count = 0
        
        category_results = {}
        
        for category, data in self.results["test_categories"].items():
            nancy_score = data.get("nancy_avg_score", 0)
            baseline_score = data.get("baseline_avg_score", 0)
            
            if nancy_score > 0 or baseline_score > 0:
                nancy_total_score += nancy_score
                baseline_total_score += baseline_score
                category_count += 1
                
                category_results[category] = {
                    "nancy_score": nancy_score,
                    "baseline_score": baseline_score,
                    "advantage": "nancy" if nancy_score > baseline_score else "baseline" if baseline_score > nancy_score else "tie",
                    "score_difference": abs(nancy_score - baseline_score)
                }
        
        nancy_overall = nancy_total_score / category_count if category_count > 0 else 0
        baseline_overall = baseline_total_score / category_count if category_count > 0 else 0
        
        # Determine final recommendation
        if nancy_overall > baseline_overall + 0.2:  # Significant advantage
            decision = "GO"
            confidence = "HIGH"
            rationale = f"Nancy demonstrates significant advantage across Four-Brain architecture ({nancy_overall:.2f} vs {baseline_overall:.2f})"
        elif nancy_overall > baseline_overall + 0.1:  # Moderate advantage
            decision = "CONDITIONAL_GO" 
            confidence = "MEDIUM"
            rationale = f"Nancy shows moderate improvement ({nancy_overall:.2f} vs {baseline_overall:.2f}) - evaluate cost/benefit"
        elif baseline_overall > nancy_overall + 0.1:  # Baseline better
            decision = "NO_GO"
            confidence = "HIGH"
            rationale = f"Baseline outperforms Nancy ({baseline_overall:.2f} vs {nancy_overall:.2f}) - significant investment not justified"
        else:  # Too close to call
            decision = "INSUFFICIENT_DIFFERENTIATION"
            confidence = "MEDIUM"
            rationale = f"Performance too similar ({nancy_overall:.2f} vs {baseline_overall:.2f}) - need deeper analysis"
        
        self.results["final_assessment"] = {
            "nancy_overall_score": nancy_overall,
            "baseline_overall_score": baseline_overall,
            "category_breakdown": category_results,
            "go_no_go_decision": decision,
            "confidence_level": confidence,
            "rationale": rationale,
            "categories_tested": category_count,
            "total_tests_completed": sum(len(data["tests"]) for data in self.results["test_categories"].values())
        }
    
    def run_comprehensive_validation(self):
        """Execute complete Four-Brain validation suite"""
        print("=" * 80)
        print("COMPREHENSIVE FOUR-BRAIN ARCHITECTURE VALIDATION")
        print("Testing Nancy's complete value proposition across all dimensions")
        print("=" * 80)
        
        # Check service health
        health = self.check_service_health()
        print(f"\nService Health: Nancy={health['nancy']}, Baseline={health['baseline']}")
        
        if not health["nancy"] and not health["baseline"]:
            print("ERROR: Neither system is available for testing")
            return "NO_SYSTEMS_AVAILABLE"
        
        # Ingest data into available systems
        if health["nancy"]:
            nancy_ingest = self.ingest_test_data(self.nancy_url, "nancy")
        if health["baseline"]:
            baseline_ingest = self.ingest_test_data(self.baseline_url, "baseline")
        
        # Run all test categories
        self.test_vector_brain_capabilities(health["nancy"], health["baseline"])
        self.test_analytical_brain_capabilities(health["nancy"], health["baseline"])
        self.test_graph_brain_capabilities(health["nancy"], health["baseline"])
        self.test_linguistic_brain_capabilities(health["nancy"], health["baseline"])
        self.test_enhanced_graph_brain_capabilities(health["nancy"], health["baseline"])
        self.test_integration_capabilities(health["nancy"], health["baseline"])
        
        # Generate final assessment
        self.generate_final_assessment()
        
        # Report results
        self.report_comprehensive_findings()
        
        # Save results
        results_file = f"comprehensive_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nComprehensive results saved to: {results_file}")
        
        return self.results["final_assessment"]["go_no_go_decision"]
    
    def report_comprehensive_findings(self):
        """Report comprehensive validation findings"""
        assessment = self.results["final_assessment"]
        
        print("\n" + "=" * 80)
        print("COMPREHENSIVE FOUR-BRAIN VALIDATION RESULTS")
        print("=" * 80)
        
        print(f"\nOVERALL PERFORMANCE:")
        print(f"Nancy Four-Brain Score: {assessment.get('nancy_overall_score', 0):.3f}")
        print(f"Baseline RAG Score: {assessment.get('baseline_overall_score', 0):.3f}")
        
        print(f"\nCATEGORY BREAKDOWN:")
        for category, results in assessment.get('category_breakdown', {}).items():
            nancy_score = results['nancy_score']
            baseline_score = results['baseline_score']
            advantage = results['advantage']
            
            print(f"  {category.replace('_', ' ').title()}:")
            print(f"    Nancy: {nancy_score:.3f} | Baseline: {baseline_score:.3f} | Advantage: {advantage}")
        
        print(f"\nFINAL DECISION: {assessment.get('go_no_go_decision', 'UNKNOWN')}")
        print(f"CONFIDENCE: {assessment.get('confidence_level', 'UNKNOWN')}")
        print(f"RATIONALE: {assessment.get('rationale', 'No rationale provided')}")
        
        print(f"\nTESTING SUMMARY:")
        print(f"Categories Tested: {assessment.get('categories_tested', 0)}")
        print(f"Total Tests Completed: {assessment.get('total_tests_completed', 0)}")

if __name__ == "__main__":
    validator = ComprehensiveFourBrainValidator()
    decision = validator.run_comprehensive_validation()
    
    # Exit with appropriate code
    if decision == "GO":
        exit(0)  # Clear go decision
    elif decision == "CONDITIONAL_GO":
        exit(1)  # Go with conditions
    elif decision == "NO_GO":
        exit(2)  # Clear no-go decision
    else:
        exit(3)  # Insufficient data or other issues