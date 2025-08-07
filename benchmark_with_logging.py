#!/usr/bin/env python3
"""
Enhanced Nancy Benchmark with Detailed Response Logging

This version logs all actual responses from each system so we can validate
the fairness and accuracy of our comparative methods.
"""

import asyncio
import json
import time
import logging
from pathlib import Path
from datetime import datetime
import requests
from automated_benchmark import BenchmarkDataGenerator, BenchmarkQuery

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DetailedBenchmarkRunner:
    """Benchmark runner with comprehensive response logging"""
    
    def __init__(self):
        self.results_dir = Path("detailed_benchmark_results")
        self.results_dir.mkdir(exist_ok=True)
        self.run_timestamp = datetime.now().isoformat().replace(':', '-').replace('.', '-')
        
        # Create detailed log file
        self.log_file = self.results_dir / f"detailed_responses_{self.run_timestamp}.jsonl"
        
    def log_response(self, system_name: str, query: str, response_data: dict, error: str = None):
        """Log detailed response for analysis"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "system": system_name,
            "query": query,
            "response": response_data,
            "error": error,
            "response_preview": str(response_data)[:500] + "..." if len(str(response_data)) > 500 else str(response_data)
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, indent=None) + '\n')
    
    async def test_nancy_query(self, query: str) -> dict:
        """Test Nancy with detailed logging"""
        start_time = time.time()
        
        try:
            response = requests.post(
                "http://localhost:8000/api/query",
                json={"query": query, "n_results": 5, "use_enhanced": True},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            response_time = time.time() - start_time
            
            # Log detailed Nancy response
            self.log_response("nancy_four_brain", query, {
                "strategy_used": result.get("strategy_used"),
                "intent_analysis": result.get("intent"),
                "num_results": len(result.get("results", [])),
                "sources": [r.get("document_metadata", {}).get("filename") for r in result.get("results", [])],
                "response_preview": [r.get("text", "")[:200] for r in result.get("results", [])][:3],
                "response_time": response_time
            })
            
            return {
                "system": "nancy_four_brain",
                "success": True,
                "response_time": response_time,
                "results_count": len(result.get("results", [])),
                "strategy": result.get("strategy_used"),
                "sources": [r.get("document_metadata", {}).get("filename") for r in result.get("results", [])],
                "raw_response": result
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_response("nancy_four_brain", query, {}, str(e))
            return {
                "system": "nancy_four_brain",
                "success": False,
                "error": str(e),
                "response_time": response_time
            }
    
    def test_chromadb_direct(self, query: str) -> dict:
        """Test ChromaDB directly (bypassing Nancy's orchestration)"""
        start_time = time.time()
        
        try:
            # Try to query the existing Nancy collection directly
            response = requests.post(
                "http://localhost:8001/api/v1/collections/documents/query",
                json={
                    "query_texts": [query],
                    "n_results": 5
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_time = time.time() - start_time
                
                self.log_response("chromadb_direct", query, {
                    "num_results": len(result.get("documents", [[]])[0]),
                    "distances": result.get("distances", [[]])[0][:3] if result.get("distances") else [],
                    "response_preview": result.get("documents", [[]])[0][:3] if result.get("documents") else [],
                    "response_time": response_time
                })
                
                return {
                    "system": "chromadb_direct",
                    "success": True,
                    "response_time": response_time,
                    "results_count": len(result.get("documents", [[]])[0]),
                    "raw_response": result
                }
            else:
                # Try different collection names
                collections_to_try = ["nancy_collection", "documents", "default"]
                for collection_name in collections_to_try:
                    try:
                        response = requests.post(
                            f"http://localhost:8001/api/v1/collections/{collection_name}/query",
                            json={"query_texts": [query], "n_results": 5},
                            timeout=10
                        )
                        if response.status_code == 200:
                            result = response.json()
                            response_time = time.time() - start_time
                            
                            self.log_response("chromadb_direct", query, {
                                "collection_used": collection_name,
                                "num_results": len(result.get("documents", [[]])[0]),
                                "response_time": response_time
                            })
                            
                            return {
                                "system": "chromadb_direct",
                                "success": True,
                                "response_time": response_time,
                                "results_count": len(result.get("documents", [[]])[0]),
                                "collection_used": collection_name,
                                "raw_response": result
                            }
                    except:
                        continue
                
                # If all collections failed
                response_time = time.time() - start_time
                self.log_response("chromadb_direct", query, {}, f"No valid collections found. Status: {response.status_code}")
                return {
                    "system": "chromadb_direct", 
                    "success": False,
                    "error": f"ChromaDB query failed: {response.status_code}",
                    "response_time": response_time
                }
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_response("chromadb_direct", query, {}, str(e))
            return {
                "system": "chromadb_direct",
                "success": False,
                "error": str(e),
                "response_time": response_time
            }
    
    def test_simple_text_search(self, query: str) -> dict:
        """Test basic text search against Nancy's data"""
        start_time = time.time()
        
        try:
            # Search in Nancy's data directory for ingested files
            data_paths = [
                Path("data"),
                Path("nancy-services/data"), 
                Path("benchmark_data")
            ]
            
            search_terms = [term.lower() for term in query.split() if len(term) > 2]
            results = []
            
            for data_path in data_paths:
                if data_path.exists():
                    for file_path in data_path.rglob("*.txt"):
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().lower()
                            
                            matches = sum(1 for term in search_terms if term in content)
                            if matches > 0:
                                # Get snippet around first match
                                first_match_pos = min((content.find(term) for term in search_terms if content.find(term) != -1), default=0)
                                snippet_start = max(0, first_match_pos - 100)
                                snippet_end = min(len(content), first_match_pos + 200)
                                snippet = content[snippet_start:snippet_end]
                                
                                results.append({
                                    "file": str(file_path),
                                    "matches": matches,
                                    "score": matches / len(search_terms),
                                    "snippet": snippet
                                })
                        except Exception:
                            continue
            
            # Sort by match score
            results.sort(key=lambda x: x["score"], reverse=True)
            results = results[:5]  # Top 5 results
            
            response_time = time.time() - start_time
            
            self.log_response("simple_text_search", query, {
                "search_terms": search_terms,
                "num_results": len(results),
                "results": results[:3],  # Log top 3 for brevity
                "response_time": response_time
            })
            
            return {
                "system": "simple_text_search",
                "success": True,
                "response_time": response_time,
                "results_count": len(results),
                "results": results
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_response("simple_text_search", query, {}, str(e))
            return {
                "system": "simple_text_search",
                "success": False,
                "error": str(e),
                "response_time": response_time
            }
    
    def test_keyword_search(self, query: str) -> dict:
        """Test keyword-based search (simulating traditional search engines)"""
        start_time = time.time()
        
        try:
            # Simple keyword matching approach
            keywords = query.lower().split()
            
            # Predefined "database" of documents (simulating indexed content)
            document_database = [
                {
                    "title": "Thermal Analysis Report",
                    "author": "Sarah Chen", 
                    "content": "thermal analysis report aluminum heat sink CPU temperatures 85°C stress testing copper solution insufficient sustained loads aluminum provides 40% better heat dissipation cost 2mm additional clearance airflow",
                    "keywords": ["thermal", "analysis", "aluminum", "heat", "sink", "temperature", "cpu", "sarah", "chen"]
                },
                {
                    "title": "Electrical Design Review",
                    "author": "Mike Rodriguez",
                    "content": "electrical design review meeting split power rail design thermal constraints component spacing optimization hotspot risks power efficiency routing optimization",
                    "keywords": ["electrical", "design", "power", "rail", "thermal", "constraints", "mike", "rodriguez", "optimization"]
                },
                {
                    "title": "Mechanical Integration Plan", 
                    "author": "Lisa Park",
                    "content": "mechanical integration enclosure redesign 15% larger volume accommodate aluminum heat sink split power rail requirements height increased 3mm clearance internal partitioning airflow channels",
                    "keywords": ["mechanical", "enclosure", "redesign", "volume", "aluminum", "heat", "sink", "lisa", "park"]
                },
                {
                    "title": "Project Timeline Q4 2024",
                    "author": "Scott Johnson",
                    "content": "project timeline Q4 2024 integration phase scott johnson thermal analysis electrical design mechanical integration cross-team collaboration architecture decisions",
                    "keywords": ["project", "timeline", "q4", "2024", "integration", "phase", "scott", "johnson", "collaboration"]
                }
            ]
            
            # Score documents based on keyword matches
            results = []
            for doc in document_database:
                score = 0
                matches = []
                for keyword in keywords:
                    if keyword in doc["keywords"]:
                        score += 2  # Exact keyword match
                        matches.append(keyword)
                    elif any(keyword in k for k in doc["keywords"]):
                        score += 1  # Partial match
                        matches.append(keyword + "*")
                
                if score > 0:
                    results.append({
                        "title": doc["title"],
                        "author": doc["author"],
                        "score": score,
                        "matches": matches,
                        "relevance": score / len(keywords),
                        "snippet": doc["content"][:200] + "..."
                    })
            
            # Sort by score
            results.sort(key=lambda x: x["score"], reverse=True)
            
            response_time = time.time() - start_time
            
            self.log_response("keyword_search", query, {
                "keywords": keywords,
                "num_results": len(results),
                "results": results,
                "response_time": response_time
            })
            
            return {
                "system": "keyword_search",
                "success": True,
                "response_time": response_time,
                "results_count": len(results),
                "results": results
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_response("keyword_search", query, {}, str(e))
            return {
                "system": "keyword_search",
                "success": False,
                "error": str(e),
                "response_time": response_time
            }
    
    async def run_comparative_test(self):
        """Run detailed comparative test with response logging"""
        
        test_queries = [
            "Who wrote the thermal analysis report?",  # Simple factual query
            "Why was aluminum chosen for the heat sink design?",  # Decision provenance
            "Who is the primary expert on thermal design?",  # Expert identification
            "How do thermal and electrical design decisions affect each other?",  # Relationship discovery
            "What decisions were made during Q4 2024?",  # Temporal analysis
        ]
        
        print(f"\n{'='*80}")
        print("DETAILED BENCHMARK WITH RESPONSE LOGGING")
        print(f"{'='*80}")
        print(f"Log file: {self.log_file}")
        print(f"{'='*80}\n")
        
        all_results = []
        
        for i, query in enumerate(test_queries):
            print(f"\n{'-'*60}")
            print(f"Query {i+1}: {query}")
            print(f"{'-'*60}")
            
            query_results = {}
            
            # Test Nancy
            print("Testing Nancy Four-Brain...")
            nancy_result = await self.test_nancy_query(query)
            query_results["nancy"] = nancy_result
            print(f"  Nancy: {'OK' if nancy_result['success'] else 'FAIL'} ({nancy_result['response_time']:.2f}s)")
            if nancy_result['success']:
                print(f"    Strategy: {nancy_result.get('strategy', 'unknown')}")
                print(f"    Results: {nancy_result['results_count']}")
                print(f"    Sources: {nancy_result.get('sources', [])}")
            
            # Test ChromaDB Direct
            print("Testing ChromaDB Direct...")
            chromadb_result = self.test_chromadb_direct(query)
            query_results["chromadb"] = chromadb_result
            print(f"  ChromaDB: {'OK' if chromadb_result['success'] else 'FAIL'} ({chromadb_result['response_time']:.2f}s)")
            if chromadb_result['success']:
                print(f"    Results: {chromadb_result['results_count']}")
                if 'collection_used' in chromadb_result:
                    print(f"    Collection: {chromadb_result['collection_used']}")
            
            # Test Simple Text Search
            print("Testing Simple Text Search...")
            text_search_result = self.test_simple_text_search(query)
            query_results["text_search"] = text_search_result
            print(f"  Text Search: {'OK' if text_search_result['success'] else 'FAIL'} ({text_search_result['response_time']:.2f}s)")
            if text_search_result['success']:
                print(f"    Results: {text_search_result['results_count']}")
            
            # Test Keyword Search
            print("Testing Keyword Search...")
            keyword_result = self.test_keyword_search(query)
            query_results["keyword"] = keyword_result
            print(f"  Keyword Search: {'OK' if keyword_result['success'] else 'FAIL'} ({keyword_result['response_time']:.2f}s)")
            if keyword_result['success']:
                print(f"    Results: {keyword_result['results_count']}")
                if keyword_result['results']:
                    top_result = keyword_result['results'][0]
                    print(f"    Top match: {top_result['title']} (score: {top_result['score']})")
            
            all_results.append({
                "query": query,
                "results": query_results
            })
        
        # Save comprehensive results
        results_file = self.results_dir / f"comparative_results_{self.run_timestamp}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n{'='*80}")
        print("BENCHMARK COMPLETE")
        print(f"{'='*80}")
        print(f"Detailed responses logged to: {self.log_file}")
        print(f"Comparative results saved to: {results_file}")
        print(f"{'='*80}\n")
        
        return results_file

async def main():
    runner = DetailedBenchmarkRunner()
    await runner.run_comparative_test()

if __name__ == "__main__":
    asyncio.run(main())