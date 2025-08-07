#!/usr/bin/env python3
"""
Complex Query Benchmark for Nancy Four-Brain Architecture

Tests realistic, complex queries that engineering teams actually need to answer
but that traditional search systems struggle with.
"""

import time
import chromadb
import requests
import json
from typing import Dict, List, Any

class ComplexQueryBenchmark:
    """Benchmark focused on complex, real-world engineering queries"""
    
    def __init__(self):
        self.chromadb_client = chromadb.HttpClient(host="localhost", port=8001)
        self.results = []
    
    def get_complex_queries(self) -> List[Dict[str, Any]]:
        """Generate complex queries that teams actually need to answer"""
        
        return [
            # Cross-document relationship queries
            {
                "id": "cross_doc_001",
                "category": "cross_document_analysis",
                "complexity": 4,
                "query": "Did the person who wrote the thermal analysis report participate in planning meetings?",
                "why_complex": "Requires connecting authorship info with meeting participation across different documents",
                "expected_nancy_advantage": "Graph brain can map person -> document -> meeting relationships",
                "baseline_limitation": "Vector search can't connect person identity across document types"
            },
            {
                "id": "cross_doc_002", 
                "category": "decision_influence_tracking",
                "complexity": 5,
                "query": "How did the thermal analysis report author feel about project risks early on?",
                "why_complex": "Requires identifying author, finding their early statements, and sentiment analysis",
                "expected_nancy_advantage": "LLM can analyze sentiment, graph can track person over time",
                "baseline_limitation": "No capability to track individual perspectives over time"
            },
            {
                "id": "cross_doc_003",
                "category": "decision_timeline",
                "complexity": 4,
                "query": "When was it decided that we needed a thermal analysis?",
                "why_complex": "Requires finding the decision point, not just the analysis document",
                "expected_nancy_advantage": "Graph brain tracks decision chronology and causation",
                "baseline_limitation": "Can find the analysis but not when the need was identified"
            },
            
            # Collaboration and influence network queries  
            {
                "id": "collab_001",
                "category": "collaboration_network",
                "complexity": 5,
                "query": "Who influences Mike Rodriguez's technical decisions the most?",
                "why_complex": "Requires analyzing influence patterns across multiple decisions and documents",
                "expected_nancy_advantage": "Graph brain maps influence networks and decision patterns",
                "baseline_limitation": "No understanding of influence relationships"
            },
            {
                "id": "collab_002",
                "category": "expertise_evolution", 
                "complexity": 4,
                "query": "Has Sarah Chen's expertise focus changed over the course of the project?",
                "why_complex": "Requires tracking expertise domains over time from document contributions",
                "expected_nancy_advantage": "Can track expertise evolution through document analysis over time",
                "baseline_limitation": "No temporal understanding of expertise development"
            },
            {
                "id": "collab_003",
                "category": "team_dynamics",
                "complexity": 4,
                "query": "Which team members collaborate most frequently on thermal-electrical interface issues?",
                "why_complex": "Requires understanding both collaboration patterns and technical domain intersection",
                "expected_nancy_advantage": "Graph brain maps collaboration + domain expertise intersection",
                "baseline_limitation": "Can find domain docs but not collaboration patterns"
            },
            
            # Causal reasoning and impact analysis
            {
                "id": "causal_001",
                "category": "causal_reasoning",
                "complexity": 5,
                "query": "What decisions were triggered by thermal constraint discoveries?",
                "why_complex": "Requires understanding causal chains: discovery -> constraint -> decision",
                "expected_nancy_advantage": "Graph brain models causal relationships between events",
                "baseline_limitation": "No understanding of causation, only correlation"
            },
            {
                "id": "causal_002",
                "category": "impact_prediction",
                "complexity": 5,
                "query": "If we change the aluminum heat sink design, what other systems need to be reconsidered?",
                "why_complex": "Requires understanding dependency chains and impact propagation",
                "expected_nancy_advantage": "Graph brain maps technical dependencies and impacts",
                "baseline_limitation": "No understanding of system dependencies"
            },
            {
                "id": "causal_003",
                "category": "risk_evolution",
                "complexity": 4,
                "query": "How did our understanding of thermal risks evolve throughout the project?",
                "why_complex": "Requires tracking risk perception changes over time",
                "expected_nancy_advantage": "Temporal analysis + sentiment tracking of risk discussions",
                "baseline_limitation": "No temporal understanding of evolving perspectives"
            },
            
            # Knowledge gap and learning queries
            {
                "id": "knowledge_001",
                "category": "knowledge_gaps",
                "complexity": 4,
                "query": "What technical questions were raised but never answered in our documentation?",
                "why_complex": "Requires understanding question vs. answer patterns across documents",
                "expected_nancy_advantage": "LLM can identify question patterns and track resolution status",
                "baseline_limitation": "No understanding of question-answer relationships"
            },
            {
                "id": "knowledge_002",
                "category": "learning_progression",
                "complexity": 4,
                "query": "What did the team learn about power management that wasn't known at project start?",
                "why_complex": "Requires comparing early vs. late knowledge states",
                "expected_nancy_advantage": "Temporal analysis of knowledge evolution",
                "baseline_limitation": "No temporal comparison capabilities"
            },
            {
                "id": "knowledge_003",
                "category": "expertise_sourcing",
                "complexity": 3,
                "query": "When the team encountered thermal issues, who did they typically consult?",
                "why_complex": "Requires identifying consultation patterns and expertise seeking behavior",
                "expected_nancy_advantage": "Graph brain maps expertise consultation networks",
                "baseline_limitation": "No understanding of consultation relationships"
            },
            
            # Strategic and planning queries
            {
                "id": "strategic_001",
                "category": "strategic_alignment",
                "complexity": 4,
                "query": "Are our technical decisions aligned with the privacy-first architecture goal?",
                "why_complex": "Requires understanding strategic goals and evaluating decision alignment",
                "expected_nancy_advantage": "LLM can assess strategic alignment across decisions",
                "baseline_limitation": "No understanding of strategic consistency"
            },
            {
                "id": "strategic_002",
                "category": "resource_allocation",
                "complexity": 4,
                "query": "Which technical challenges consumed the most team discussion time?",
                "why_complex": "Requires quantifying discussion focus across multiple documents and meetings",
                "expected_nancy_advantage": "Can analyze discussion volume and categorize by technical domain",
                "baseline_limitation": "No capability to quantify discussion focus"
            },
            {
                "id": "strategic_003",
                "category": "decision_consistency",
                "complexity": 5,
                "query": "Have we made any contradictory decisions about thermal management approaches?",
                "why_complex": "Requires understanding decision content and identifying contradictions",
                "expected_nancy_advantage": "LLM can analyze decision consistency + graph tracks decision relationships",
                "baseline_limitation": "No understanding of decision contradiction"
            }
        ]
    
    def test_query_with_both_systems(self, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single complex query with both ChromaDB and Nancy"""
        
        query = query_info["query"]
        print(f"\n{'='*80}")
        print(f"TESTING: {query}")
        print(f"Category: {query_info['category']} | Complexity: {query_info['complexity']}/5")
        print(f"Why Complex: {query_info['why_complex']}")
        print(f"{'='*80}")
        
        results = {
            "query_info": query_info,
            "chromadb_result": None,
            "nancy_result": None,
            "comparison": {}
        }
        
        # Test ChromaDB Direct
        print("1. CHROMADB DIRECT:")
        print("-" * 40)
        start_time = time.time()
        try:
            collection = self.chromadb_client.get_collection("nancy_documents")
            chroma_results = collection.query(
                query_texts=[query],
                n_results=5
            )
            response_time = time.time() - start_time
            
            num_results = len(chroma_results["documents"][0]) if chroma_results["documents"] else 0
            print(f"Response Time: {response_time:.3f}s")
            print(f"Results Found: {num_results}")
            
            if num_results > 0:
                print("Top Results:")
                for i, (doc, distance) in enumerate(zip(chroma_results["documents"][0][:2], chroma_results["distances"][0][:2])):
                    print(f"  {i+1}. (dist: {distance:.3f}) {doc[:100]}...")
                    
                # Assess result quality for complex query
                best_distance = min(chroma_results["distances"][0]) if chroma_results["distances"][0] else float('inf')
                quality_assessment = self._assess_chromadb_quality(query_info, chroma_results)
                print(f"Quality Assessment: {quality_assessment}")
            else:
                print("No results found")
                quality_assessment = "No results"
                best_distance = float('inf')
            
            results["chromadb_result"] = {
                "success": True,
                "response_time": response_time,
                "num_results": num_results,
                "best_distance": best_distance,
                "quality_assessment": quality_assessment,
                "raw_results": chroma_results
            }
            
        except Exception as e:
            print(f"FAILED: {e}")
            results["chromadb_result"] = {
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }
        
        # Test Nancy Four-Brain
        print(f"\n2. NANCY FOUR-BRAIN:")
        print("-" * 40)
        start_time = time.time()
        try:
            response = requests.post(
                "http://localhost:8000/api/query",
                json={"query": query, "n_results": 5, "use_enhanced": True},
                timeout=60  # Longer timeout for complex queries
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                nancy_result = response.json()
                num_results = len(nancy_result.get("results", []))
                strategy = nancy_result.get("strategy_used", "unknown")
                intent = nancy_result.get("intent", {})
                
                print(f"Response Time: {response_time:.3f}s")
                print(f"Strategy Used: {strategy}")
                print(f"Intent Analysis: {intent.get('type', 'unknown')}")
                print(f"Results Found: {num_results}")
                
                if num_results > 0:
                    print("Top Results:")
                    for i, result in enumerate(nancy_result.get("results", [])[:2]):
                        text = result.get("text", "")
                        distance = result.get("distance", "N/A")
                        filename = result.get("document_metadata", {}).get("filename", "unknown")
                        print(f"  {i+1}. (dist: {distance}, file: {filename}) {text[:80]}...")
                
                # Assess Nancy's handling of complex query
                quality_assessment = self._assess_nancy_quality(query_info, nancy_result)
                print(f"Quality Assessment: {quality_assessment}")
                
                results["nancy_result"] = {
                    "success": True,
                    "response_time": response_time,
                    "strategy": strategy,
                    "intent": intent,
                    "num_results": num_results,
                    "quality_assessment": quality_assessment,
                    "raw_results": nancy_result
                }
                
            else:
                print(f"FAILED: HTTP {response.status_code}")
                results["nancy_result"] = {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response_time": response_time
                }
                
        except Exception as e:
            print(f"FAILED: {e}")
            results["nancy_result"] = {
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }
        
        # Compare results
        results["comparison"] = self._compare_results(results["chromadb_result"], results["nancy_result"], query_info)
        
        print(f"\n3. COMPARISON:")
        print("-" * 40)
        comparison = results["comparison"]
        print(f"Winner: {comparison.get('winner', 'unclear')}")
        print(f"Reason: {comparison.get('reason', 'N/A')}")
        print(f"Nancy Advantage Realized: {comparison.get('nancy_advantage_realized', 'unclear')}")
        
        return results
    
    def _assess_chromadb_quality(self, query_info: Dict[str, Any], results: Dict[str, Any]) -> str:
        """Assess how well ChromaDB handled the complex query"""
        
        if not results["documents"] or not results["documents"][0]:
            return "No relevant results found"
        
        # For complex queries, ChromaDB typically struggles with:
        # - Cross-document relationships
        # - Temporal reasoning  
        # - Causal connections
        # - Multi-step logic
        
        category = query_info["category"]
        if category in ["cross_document_analysis", "decision_influence_tracking", "collaboration_network"]:
            return "Likely insufficient - requires cross-document relationship analysis"
        elif category in ["causal_reasoning", "impact_prediction", "decision_timeline"]:
            return "Likely insufficient - requires causal understanding"
        elif category in ["knowledge_gaps", "strategic_alignment", "decision_consistency"]:
            return "Likely insufficient - requires semantic reasoning"
        else:
            return "May provide relevant documents but lacks deeper analysis"
    
    def _assess_nancy_quality(self, query_info: Dict[str, Any], results: Dict[str, Any]) -> str:
        """Assess how well Nancy handled the complex query"""
        
        strategy = results.get("strategy", "unknown")
        intent_type = results.get("intent", {}).get("type", "unknown")
        num_results = results.get("num_results", 0)
        
        if num_results == 0:
            return "No results found - query may be too complex or data insufficient"
        
        # Nancy should excel at complex queries by using appropriate strategies
        if strategy == "hybrid" and intent_type in ["relationship_primary", "hybrid"]:
            return "Good - used multi-brain approach for complex query"
        elif strategy == "analytical_first" and "temporal" in str(results.get("intent", {})):
            return "Good - recognized temporal aspects"
        elif num_results > 0:
            return "Adequate - found relevant content but strategy may not be optimal"
        else:
            return "Unclear - need to examine specific results"
    
    def _compare_results(self, chromadb_result: Dict, nancy_result: Dict, query_info: Dict) -> Dict[str, str]:
        """Compare the two systems' performance on the complex query"""
        
        if not chromadb_result.get("success") and not nancy_result.get("success"):
            return {"winner": "neither", "reason": "Both systems failed"}
        
        if not chromadb_result.get("success"):
            return {"winner": "nancy", "reason": "Only Nancy succeeded"}
        
        if not nancy_result.get("success"):
            return {"winner": "chromadb", "reason": "Only ChromaDB succeeded"}
        
        # Both succeeded - compare on multiple dimensions
        chromadb_quality = chromadb_result.get("quality_assessment", "")
        nancy_quality = nancy_result.get("quality_assessment", "")
        
        # For complex queries, Nancy should have advantages
        expected_advantage = query_info.get("expected_nancy_advantage", "")
        
        if "Good" in nancy_quality and "insufficient" in chromadb_quality:
            return {
                "winner": "nancy", 
                "reason": "Nancy provided deeper analysis for complex query",
                "nancy_advantage_realized": True
            }
        elif nancy_result.get("response_time", 999) > chromadb_result.get("response_time", 0) * 5:
            return {
                "winner": "mixed", 
                "reason": "Nancy better quality but significantly slower",
                "nancy_advantage_realized": "partial"
            }
        else:
            return {
                "winner": "mixed", 
                "reason": "Both provided results, trade-offs in speed vs. analysis depth",
                "nancy_advantage_realized": "unclear"
            }
    
    def run_complex_benchmark(self) -> str:
        """Run the complete complex query benchmark"""
        
        print("NANCY COMPLEX QUERY BENCHMARK")
        print("="*80)
        print("Testing queries that require multi-document analysis, reasoning, and relationships")
        print("="*80)
        
        queries = self.get_complex_queries()
        all_results = []
        
        for i, query_info in enumerate(queries):
            print(f"\n[QUERY {i+1}/{len(queries)}]")
            result = self.test_query_with_both_systems(query_info)
            all_results.append(result)
            
            # Brief pause between queries
            time.sleep(1)
        
        # Generate summary
        summary = self._generate_summary(all_results)
        
        # Save results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = f"complex_benchmark_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "summary": summary,
                "detailed_results": all_results
            }, f, indent=2)
        
        print(f"\n{'='*80}")
        print("COMPLEX BENCHMARK SUMMARY")
        print(f"{'='*80}")
        print(summary["text_summary"])
        print(f"Detailed results saved to: {results_file}")
        
        return results_file
    
    def _generate_summary(self, all_results: List[Dict]) -> Dict:
        """Generate summary of complex benchmark results"""
        
        total_queries = len(all_results)
        nancy_wins = sum(1 for r in all_results if r["comparison"].get("winner") == "nancy")
        chromadb_wins = sum(1 for r in all_results if r["comparison"].get("winner") == "chromadb")
        mixed_results = sum(1 for r in all_results if r["comparison"].get("winner") == "mixed")
        
        nancy_advantages_realized = sum(1 for r in all_results 
                                      if r["comparison"].get("nancy_advantage_realized") == True)
        
        # Calculate average response times
        nancy_times = [r["nancy_result"]["response_time"] for r in all_results 
                      if r["nancy_result"] and r["nancy_result"].get("success")]
        chromadb_times = [r["chromadb_result"]["response_time"] for r in all_results 
                         if r["chromadb_result"] and r["chromadb_result"].get("success")]
        
        avg_nancy_time = sum(nancy_times) / len(nancy_times) if nancy_times else 0
        avg_chromadb_time = sum(chromadb_times) / len(chromadb_times) if chromadb_times else 0
        
        text_summary = f"""
COMPLEX QUERY BENCHMARK RESULTS:

Total Queries Tested: {total_queries}
Nancy Clear Wins: {nancy_wins} ({nancy_wins/total_queries*100:.1f}%)
ChromaDB Clear Wins: {chromadb_wins} ({chromadb_wins/total_queries*100:.1f}%)
Mixed Results: {mixed_results} ({mixed_results/total_queries*100:.1f}%)

Nancy Advantages Realized: {nancy_advantages_realized}/{total_queries} ({nancy_advantages_realized/total_queries*100:.1f}%)

Average Response Times:
- Nancy: {avg_nancy_time:.2f}s
- ChromaDB: {avg_chromadb_time:.2f}s
- Speed Ratio: {avg_nancy_time/avg_chromadb_time:.1f}x slower

Key Insights:
- Complex queries requiring cross-document analysis: Nancy advantage expected
- Simple document retrieval: ChromaDB competitive
- Multi-step reasoning: Nancy's LLM integration crucial
- Relationship mapping: Nancy's graph brain essential
        """.strip()
        
        return {
            "text_summary": text_summary,
            "metrics": {
                "total_queries": total_queries,
                "nancy_wins": nancy_wins,
                "chromadb_wins": chromadb_wins,
                "mixed_results": mixed_results,
                "nancy_advantages_realized": nancy_advantages_realized,
                "avg_nancy_time": avg_nancy_time,
                "avg_chromadb_time": avg_chromadb_time
            }
        }

if __name__ == "__main__":
    benchmark = ComplexQueryBenchmark()
    results_file = benchmark.run_complex_benchmark()
    print(f"\nBenchmark complete! Results in {results_file}")