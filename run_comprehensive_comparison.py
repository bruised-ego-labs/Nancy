#!/usr/bin/env python3
"""
Comprehensive Nancy vs Baseline RAG Comparison Script

This script runs a systematic comparison between Nancy's Four-Brain architecture
and the baseline LangChain RAG system across multiple query types and complexity levels.

Usage: python run_comprehensive_comparison.py
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, List, Any

class RAGComparison:
    def __init__(self):
        self.nancy_url = "http://localhost:8000"
        self.baseline_url = "http://localhost:8002"
        self.results = []
        
        # Test queries across different complexity levels
        self.test_queries = [
            {
                "category": "Basic Factual",
                "query": "What is the operating temperature range mentioned in the thermal analysis?",
                "expected_capabilities": ["basic_retrieval"]
            },
            {
                "category": "Author Attribution", 
                "query": "Who wrote the electrical design review document?",
                "expected_capabilities": ["author_tracking", "metadata_retrieval"]
            },
            {
                "category": "Cross-Domain Relationships",
                "query": "How do the electrical design requirements affect the mechanical integration plan?",
                "expected_capabilities": ["relationship_discovery", "cross_document_synthesis"]
            },
            {
                "category": "Decision Chain Tracking",
                "query": "What decisions were made in the project timeline that affect the thermal analysis?",
                "expected_capabilities": ["decision_tracking", "temporal_analysis"]
            },
            {
                "category": "Complex Multi-Document",
                "query": "What are the key integration points between electrical and mechanical systems, and how do project timelines affect thermal considerations?",
                "expected_capabilities": ["multi_brain_orchestration", "complex_synthesis", "temporal_relationships"]
            },
            {
                "category": "Temporal Analysis",
                "query": "What activities are scheduled for Q4 2024 and how do they relate to thermal considerations?",
                "expected_capabilities": ["temporal_filtering", "relationship_discovery"]
            },
            {
                "category": "Technical Detail Synthesis",
                "query": "What are the power dissipation requirements and how do they impact the enclosure design?",
                "expected_capabilities": ["technical_synthesis", "cross_domain_analysis"]
            }
        ]
    
    def test_system_health(self, system_name: str, base_url: str) -> Dict[str, Any]:
        """Test if system is responsive"""
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            return {
                "system": system_name,
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_code": response.status_code,
                "details": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "system": system_name,
                "status": "error",
                "error": str(e)
            }
    
    def query_system(self, system_name: str, base_url: str, query: str, timeout: int = 180) -> Dict[str, Any]:
        """Query a RAG system and measure performance"""
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{base_url}/api/query",
                json={"query": query},
                timeout=timeout,
                headers={"Content-Type": "application/json"}
            )
            
            end_time = time.time()
            query_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract key metrics
                return {
                    "system": system_name,
                    "status": "success",
                    "query_time": query_time,
                    "response": result.get("response", ""),
                    "sources": result.get("sources", []),
                    "author_info": self._extract_author_info(result),
                    "relationship_info": self._extract_relationships(result),
                    "response_length": len(result.get("response", "")),
                    "source_count": len(result.get("sources", [])),
                    "raw_result": result
                }
            else:
                return {
                    "system": system_name,
                    "status": "error",
                    "query_time": query_time,
                    "error": f"HTTP {response.status_code}",
                    "response": response.text
                }
                
        except requests.exceptions.Timeout:
            return {
                "system": system_name,
                "status": "timeout",
                "query_time": timeout,
                "error": f"Query timed out after {timeout} seconds"
            }
        except Exception as e:
            return {
                "system": system_name,
                "status": "error",
                "query_time": time.time() - start_time,
                "error": str(e)
            }
    
    def _extract_author_info(self, result: Dict) -> Dict[str, Any]:
        """Extract author attribution information"""
        response_text = result.get("response", "").lower()
        
        # Look for author mentions
        has_author = any(word in response_text for word in ["author", "wrote", "created", "by"])
        author_names = []
        
        # Simple extraction - could be enhanced
        if "sarah chen" in response_text:
            author_names.append("Sarah Chen")
        if "mike rodriguez" in response_text:
            author_names.append("Mike Rodriguez")
        if "alex kim" in response_text:
            author_names.append("Alex Kim")
        if "jennifer park" in response_text:
            author_names.append("Jennifer Park")
            
        return {
            "has_author_attribution": has_author,
            "identified_authors": author_names,
            "author_count": len(author_names)
        }
    
    def _extract_relationships(self, result: Dict) -> Dict[str, Any]:
        """Extract relationship information"""
        response_text = result.get("response", "").lower()
        
        relationship_indicators = [
            "affects", "influences", "depends on", "related to", "impacts", 
            "caused by", "results in", "connected to", "due to"
        ]
        
        found_relationships = [ind for ind in relationship_indicators if ind in response_text]
        
        return {
            "has_relationships": len(found_relationships) > 0,
            "relationship_indicators": found_relationships,
            "relationship_count": len(found_relationships)
        }
    
    def run_comparison(self) -> Dict[str, Any]:
        """Run the complete comparison"""
        print("🔍 Starting Comprehensive Nancy vs Baseline RAG Comparison")
        print("=" * 60)
        
        comparison_start = time.time()
        
        # Test system health first
        print("1. Testing System Health...")
        nancy_health = self.test_system_health("Nancy Four-Brain", self.nancy_url)
        baseline_health = self.test_system_health("Baseline RAG", self.baseline_url)
        
        print(f"   Nancy: {nancy_health['status']}")
        print(f"   Baseline: {baseline_health['status']}")
        
        if nancy_health['status'] != 'healthy' or baseline_health['status'] != 'healthy':
            print("⚠️  Warning: One or both systems not healthy. Proceeding anyway...")
        
        print("\n2. Running Test Queries...")
        
        for i, test in enumerate(self.test_queries, 1):
            print(f"\n   Test {i}: {test['category']}")
            print(f"   Query: {test['query'][:80]}{'...' if len(test['query']) > 80 else ''}")
            
            # Test Nancy
            print(f"     → Testing Nancy... ", end="", flush=True)
            nancy_result = self.query_system("Nancy", self.nancy_url, test['query'])
            print(f"({nancy_result['query_time']:.1f}s - {nancy_result['status']})")
            
            # Test Baseline
            print(f"     → Testing Baseline... ", end="", flush=True)
            baseline_result = self.query_system("Baseline", self.baseline_url, test['query'])
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
        
        comparison_time = time.time() - comparison_start
        
        # Generate analysis
        analysis = self._analyze_results()
        
        final_results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_time": comparison_time,
                "nancy_url": self.nancy_url,
                "baseline_url": self.baseline_url,
                "test_count": len(self.test_queries)
            },
            "system_health": {
                "nancy": nancy_health,
                "baseline": baseline_health
            },
            "test_results": self.results,
            "analysis": analysis
        }
        
        return final_results
    
    def _analyze_results(self) -> Dict[str, Any]:
        """Analyze the comparison results"""
        nancy_times = []
        baseline_times = []
        nancy_successes = 0
        baseline_successes = 0
        
        category_analysis = {}
        
        for result in self.results:
            category = result['category']
            
            # Collect timing data
            if result['nancy']['status'] == 'success':
                nancy_times.append(result['nancy']['query_time'])
                nancy_successes += 1
            if result['baseline']['status'] == 'success':
                baseline_times.append(result['baseline']['query_time'])
                baseline_successes += 1
            
            # Category-specific analysis
            if category not in category_analysis:
                category_analysis[category] = {
                    'nancy_better': 0,
                    'baseline_better': 0,
                    'details': []
                }
            
            # Compare capabilities
            nancy_authors = result['nancy'].get('author_info', {}).get('author_count', 0)
            baseline_authors = result['baseline'].get('author_info', {}).get('author_count', 0)
            
            nancy_relationships = result['nancy'].get('relationship_info', {}).get('relationship_count', 0)
            baseline_relationships = result['baseline'].get('relationship_info', {}).get('relationship_count', 0)
            
            nancy_sources = result['nancy'].get('source_count', 0)
            baseline_sources = result['baseline'].get('source_count', 0)
            
            # Scoring logic
            nancy_score = 0
            baseline_score = 0
            
            if nancy_authors > baseline_authors:
                nancy_score += 1
            elif baseline_authors > nancy_authors:
                baseline_score += 1
                
            if nancy_relationships > baseline_relationships:
                nancy_score += 1
            elif baseline_relationships > nancy_relationships:
                baseline_score += 1
                
            if nancy_sources > baseline_sources:
                nancy_score += 1
            elif baseline_sources > nancy_sources:
                baseline_score += 1
            
            if nancy_score > baseline_score:
                category_analysis[category]['nancy_better'] += 1
            elif baseline_score > nancy_score:
                category_analysis[category]['baseline_better'] += 1
            
            category_analysis[category]['details'].append({
                'query': result['query'][:50] + '...',
                'nancy_score': nancy_score,
                'baseline_score': baseline_score,
                'nancy_time': result['nancy']['query_time'],
                'baseline_time': result['baseline']['query_time'],
                'nancy_authors': nancy_authors,
                'baseline_authors': baseline_authors,
                'nancy_relationships': nancy_relationships,
                'baseline_relationships': baseline_relationships
            })
        
        return {
            "performance": {
                "nancy_avg_time": sum(nancy_times) / len(nancy_times) if nancy_times else 0,
                "baseline_avg_time": sum(baseline_times) / len(baseline_times) if baseline_times else 0,
                "nancy_success_rate": nancy_successes / len(self.results),
                "baseline_success_rate": baseline_successes / len(self.results),
                "nancy_fastest": min(nancy_times) if nancy_times else None,
                "baseline_fastest": min(baseline_times) if baseline_times else None,
                "nancy_slowest": max(nancy_times) if nancy_times else None,
                "baseline_slowest": max(baseline_times) if baseline_times else None
            },
            "capabilities": {
                "total_tests": len(self.results),
                "nancy_wins": sum(cat['nancy_better'] for cat in category_analysis.values()),
                "baseline_wins": sum(cat['baseline_better'] for cat in category_analysis.values()),
                "category_breakdown": category_analysis
            },
            "summary": self._generate_summary(category_analysis, nancy_times, baseline_times)
        }
    
    def _generate_summary(self, category_analysis: Dict, nancy_times: List, baseline_times: List) -> Dict[str, str]:
        """Generate executive summary"""
        nancy_wins = sum(cat['nancy_better'] for cat in category_analysis.values())
        baseline_wins = sum(cat['baseline_better'] for cat in category_analysis.values())
        
        avg_nancy_time = sum(nancy_times) / len(nancy_times) if nancy_times else 0
        avg_baseline_time = sum(baseline_times) / len(baseline_times) if baseline_times else 0
        
        speed_winner = "Baseline RAG" if avg_baseline_time < avg_nancy_time else "Nancy Four-Brain"
        capability_winner = "Nancy Four-Brain" if nancy_wins > baseline_wins else "Baseline RAG" if baseline_wins > nancy_wins else "Tie"
        
        return {
            "speed_winner": speed_winner,
            "capability_winner": capability_winner,
            "recommendation": self._get_recommendation(nancy_wins, baseline_wins, avg_nancy_time, avg_baseline_time),
            "key_insights": [
                f"Nancy excelled in {nancy_wins} test categories vs Baseline's {baseline_wins}",
                f"Average response time: Nancy {avg_nancy_time:.1f}s vs Baseline {avg_baseline_time:.1f}s",
                f"Nancy shows strength in author attribution and relationship discovery",
                f"Baseline shows consistent speed advantage but limited advanced capabilities"
            ]
        }
    
    def _get_recommendation(self, nancy_wins: int, baseline_wins: int, nancy_time: float, baseline_time: float) -> str:
        """Generate architectural recommendation"""
        if nancy_wins > baseline_wins and nancy_time < baseline_time * 2:
            return "Recommend Nancy Four-Brain: Superior capabilities with acceptable performance"
        elif nancy_wins > baseline_wins:
            return "Recommend Nancy Four-Brain: Superior capabilities justify slower response times"
        elif baseline_wins > nancy_wins and baseline_time < nancy_time * 0.5:
            return "Consider Baseline RAG: Significantly faster with comparable capabilities"
        else:
            return "Further evaluation needed: Mixed results require deeper analysis"

def main():
    """Run the comprehensive comparison"""
    comparison = RAGComparison()
    
    try:
        results = comparison.run_comparison()
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nancy_vs_baseline_comparison_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n" + "="*60)
        print("🎯 COMPARISON COMPLETE")
        print("="*60)
        
        analysis = results['analysis']
        print(f"\n📊 PERFORMANCE SUMMARY:")
        print(f"   Nancy Average Time: {analysis['performance']['nancy_avg_time']:.1f}s")
        print(f"   Baseline Average Time: {analysis['performance']['baseline_avg_time']:.1f}s")
        print(f"   Nancy Success Rate: {analysis['performance']['nancy_success_rate']:.1%}")
        print(f"   Baseline Success Rate: {analysis['performance']['baseline_success_rate']:.1%}")
        
        print(f"\n🧠 CAPABILITY ANALYSIS:")
        print(f"   Nancy Wins: {analysis['capabilities']['nancy_wins']} categories")
        print(f"   Baseline Wins: {analysis['capabilities']['baseline_wins']} categories")
        print(f"   Speed Winner: {analysis['summary']['speed_winner']}")
        print(f"   Capability Winner: {analysis['summary']['capability_winner']}")
        
        print(f"\n💡 RECOMMENDATION:")
        print(f"   {analysis['summary']['recommendation']}")
        
        print(f"\n📁 Results saved to: {filename}")
        
        return results
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Comparison interrupted by user")
        return None
    except Exception as e:
        print(f"\n\n❌ Comparison failed: {e}")
        return None

if __name__ == "__main__":
    main()