#!/usr/bin/env python3
"""
Nancy vs Baseline RAG Performance Comparison

This script runs identical queries against both:
1. Nancy's Four-Brain Architecture (http://localhost:8000)
2. LangChain + ChromaDB Baseline (http://localhost:8001)

Focus is on demonstrating functional benefits where Nancy should excel:
- Author attribution 
- Cross-document relationships
- Decision tracking
- Expert identification
"""

import time
import json
import requests
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class TestQuery:
    id: str
    query: str
    category: str
    complexity: int
    nancy_advantage: str
    description: str

class NancyBaselineComparison:
    """Compare Nancy Four-Brain vs LangChain RAG baseline"""
    
    def __init__(self):
        self.nancy_endpoint = "http://localhost:8000"
        self.baseline_endpoint = "http://localhost:8001"  
        
    def get_test_queries(self) -> List[TestQuery]:
        """Test queries designed to highlight Nancy's advantages"""
        return [
            TestQuery(
                id="simple_lookup",
                query="What is the thermal analysis about?",
                category="basic_information_retrieval", 
                complexity=1,
                nancy_advantage="none",
                description="Basic semantic search - both systems should perform similarly"
            ),
            TestQuery(
                id="author_attribution",
                query="Who wrote the thermal analysis report?", 
                category="metadata_lookup",
                complexity=2,
                nancy_advantage="analytical_brain",
                description="Nancy's Analytical Brain stores author metadata; baseline has no author info"
            ),
            TestQuery(
                id="cross_document_thermal_mechanical",
                query="How do the thermal constraints affect the mechanical design?",
                category="cross_document_relationship",
                complexity=3, 
                nancy_advantage="graph_brain",
                description="Nancy's Graph Brain can map technical dependencies; baseline finds similar text chunks"
            ),
            TestQuery(
                id="decision_timeline",
                query="What decisions were made regarding the heat sink design?",
                category="decision_tracking",
                complexity=4,
                nancy_advantage="graph_brain + llm_orchestration", 
                description="Nancy tracks decisions in knowledge graph; baseline only finds text mentioning decisions"
            ),
            TestQuery(
                id="expert_identification",
                query="Who is the expert on thermal-electrical interfaces?",
                category="expertise_mapping",
                complexity=4,
                nancy_advantage="graph_brain + analytical_brain",
                description="Nancy maps expertise through document analysis; baseline cannot identify domain experts"
            ),
            TestQuery(
                id="project_evolution",
                query="How did the project requirements change over time?",
                category="temporal_analysis",
                complexity=5,
                nancy_advantage="graph_brain + analytical_brain",
                description="Nancy tracks project evolution; baseline has no temporal understanding"
            ),
            TestQuery(
                id="collaboration_patterns", 
                query="Which teams collaborate most on electrical design issues?",
                category="team_dynamics",
                complexity=5,
                nancy_advantage="graph_brain",
                description="Nancy maps collaboration networks; baseline cannot identify team relationships"
            ),
            TestQuery(
                id="technical_dependencies",
                query="If we change the power requirements, what other systems need updates?",
                category="impact_analysis", 
                complexity=5,
                nancy_advantage="graph_brain + llm_orchestration",
                description="Nancy models technical dependencies; baseline cannot predict cascading changes"
            )
        ]
    
    def query_system(self, endpoint: str, question: str, system_name: str) -> Dict[str, Any]:
        """Query a system and return structured results"""
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{endpoint}/api/query",
                json={"query": question},
                timeout=60
            )
            
            query_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "sources": result.get("sources", []),
                    "query_time": query_time,
                    "system": system_name,
                    "metadata": result.get("metadata", {}),
                    "status_code": 200
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "query_time": query_time,
                    "system": system_name,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query_time": 0,
                "system": system_name,
                "status_code": None
            }
    
    def check_system_health(self) -> Dict[str, bool]:
        """Check if both systems are running"""
        health_status = {}
        
        for name, endpoint in [("Nancy", self.nancy_endpoint), ("Baseline", self.baseline_endpoint)]:
            try:
                response = requests.get(f"{endpoint}/health", timeout=5)
                health_status[name] = response.status_code == 200
            except:
                health_status[name] = False
        
        return health_status
    
    def run_comparison(self) -> Dict[str, Any]:
        """Run complete comparison between Nancy and baseline"""
        
        print("Nancy vs Baseline RAG Comparison")
        print("=" * 50)
        
        # Check system health
        print("Checking system health...")
        health = self.check_system_health()
        print(f"Nancy (port 8000): {'✓' if health['Nancy'] else '✗'}")
        print(f"Baseline (port 8001): {'✓' if health['Baseline'] else '✗'}")
        
        if not all(health.values()):
            print("⚠️  One or more systems are not responding. Please start all services.")
            return {"error": "Systems not available", "health": health}
        
        # Initialize results
        results = {
            "timestamp": time.strftime("%Y%m%d_%H%M%S"),
            "test_queries": [],
            "summary": {
                "total_queries": 0,
                "nancy_successes": 0,
                "baseline_successes": 0,
                "nancy_advantages_realized": 0,
                "avg_nancy_time": 0,
                "avg_baseline_time": 0
            },
            "insights": []
        }
        
        queries = self.get_test_queries()
        nancy_times = []
        baseline_times = []
        
        print(f"\\nRunning {len(queries)} test queries...\\n")
        
        for i, test_query in enumerate(queries, 1):
            print(f"[{i}/{len(queries)}] {test_query.category.upper()}")
            print(f"Query: {test_query.query}")
            print(f"Expected Nancy Advantage: {test_query.nancy_advantage}")
            
            # Query both systems
            nancy_result = self.query_system(self.nancy_endpoint, test_query.query, "Nancy")
            baseline_result = self.query_system(self.baseline_endpoint, test_query.query, "Baseline")
            
            # Analyze results
            test_result = {
                "query_info": asdict(test_query),
                "nancy_result": nancy_result,
                "baseline_result": baseline_result,
                "analysis": self.analyze_responses(test_query, nancy_result, baseline_result)
            }
            
            results["test_queries"].append(test_result)
            
            # Track timing
            if nancy_result["success"]:
                nancy_times.append(nancy_result["query_time"])
            if baseline_result["success"]:
                baseline_times.append(baseline_result["query_time"])
            
            # Print immediate results  
            print(f"Nancy: {nancy_result['query_time']:.2f}s ({'Success' if nancy_result['success'] else 'Failed'})")
            print(f"Baseline: {baseline_result['query_time']:.2f}s ({'Success' if baseline_result['success'] else 'Failed'})")
            print(f"Advantage: {test_result['analysis']['advantage']}")
            print("-" * 50)
        
        # Calculate summary statistics
        results["summary"] = {
            "total_queries": len(queries),
            "nancy_successes": sum(1 for r in results["test_queries"] if r["nancy_result"]["success"]),
            "baseline_successes": sum(1 for r in results["test_queries"] if r["baseline_result"]["success"]),
            "nancy_advantages_realized": sum(1 for r in results["test_queries"] if r["analysis"]["advantage"] == "Nancy"),
            "avg_nancy_time": sum(nancy_times) / len(nancy_times) if nancy_times else 0,
            "avg_baseline_time": sum(baseline_times) / len(baseline_times) if baseline_times else 0
        }
        
        # Generate insights
        results["insights"] = self.generate_insights(results)
        
        return results
    
    def analyze_responses(self, query: TestQuery, nancy_result: Dict, baseline_result: Dict) -> Dict[str, Any]:
        """Analyze which system provided better response for this query type"""
        
        # Basic success check
        nancy_success = nancy_result["success"]
        baseline_success = baseline_result["success"]
        
        if not nancy_success and not baseline_success:
            return {"advantage": "Neither", "reason": "Both systems failed"}
        elif nancy_success and not baseline_success:
            return {"advantage": "Nancy", "reason": "Only Nancy succeeded"}
        elif baseline_success and not nancy_success:
            return {"advantage": "Baseline", "reason": "Only Baseline succeeded"}
        
        # Both succeeded - analyze quality based on query category
        nancy_response = nancy_result.get("response", "").lower()
        baseline_response = baseline_result.get("response", "").lower()
        
        analysis = {"advantage": "Similar", "reason": "Both provided responses"}
        
        # Category-specific analysis
        if query.category == "metadata_lookup":
            # Check if Nancy provided author attribution
            if any(name in nancy_response for name in ["author", "written by", "by:", "created by"]):
                if not any(name in baseline_response for name in ["author", "written by", "by:", "created by"]):
                    analysis = {"advantage": "Nancy", "reason": "Nancy provided author attribution, baseline did not"}
        
        elif query.category in ["cross_document_relationship", "decision_tracking", "expertise_mapping"]:
            # Check for relationship/connection language
            nancy_connections = len([word for word in ["because", "due to", "affects", "influences", "connects", "relationship", "depends on"] if word in nancy_response])
            baseline_connections = len([word for word in ["because", "due to", "affects", "influences", "connects", "relationship", "depends on"] if word in baseline_response])
            
            if nancy_connections > baseline_connections:
                analysis = {"advantage": "Nancy", "reason": "Nancy showed better relationship understanding"}
        
        elif query.category in ["temporal_analysis", "team_dynamics", "impact_analysis"]:
            # These require sophisticated reasoning Nancy should excel at
            if len(nancy_response) > len(baseline_response) * 1.2:  # Nancy gave more detailed response
                analysis = {"advantage": "Nancy", "reason": "Nancy provided more comprehensive analysis"}
        
        return analysis
    
    def generate_insights(self, results: Dict) -> List[str]:
        """Generate high-level insights from the comparison"""
        insights = []
        summary = results["summary"]
        
        # Success rates
        nancy_success_rate = summary["nancy_successes"] / summary["total_queries"] * 100
        baseline_success_rate = summary["baseline_successes"] / summary["total_queries"] * 100
        
        insights.append(f"Nancy success rate: {nancy_success_rate:.1f}% ({summary['nancy_successes']}/{summary['total_queries']})")
        insights.append(f"Baseline success rate: {baseline_success_rate:.1f}% ({summary['baseline_successes']}/{summary['total_queries']})")
        
        # Performance advantages
        advantages_rate = summary["nancy_advantages_realized"] / summary["total_queries"] * 100
        insights.append(f"Nancy showed functional advantages on {advantages_rate:.1f}% of queries ({summary['nancy_advantages_realized']}/{summary['total_queries']})")
        
        # Speed comparison
        if summary["avg_nancy_time"] > 0 and summary["avg_baseline_time"] > 0:
            speed_diff = summary["avg_nancy_time"] - summary["avg_baseline_time"]
            faster_system = "Nancy" if speed_diff < 0 else "Baseline"
            insights.append(f"{faster_system} was faster by {abs(speed_diff):.2f}s on average")
        
        # Category-specific insights
        category_performance = {}
        for test in results["test_queries"]:
            category = test["query_info"]["category"]
            advantage = test["analysis"]["advantage"]
            
            if category not in category_performance:
                category_performance[category] = {"Nancy": 0, "Baseline": 0, "Similar": 0, "Neither": 0}
            category_performance[category][advantage] += 1
        
        insights.append("\\nCategory Performance:")
        for category, performance in category_performance.items():
            nancy_wins = performance["Nancy"]
            baseline_wins = performance["Baseline"] 
            total = sum(performance.values())
            insights.append(f"  {category}: Nancy {nancy_wins}/{total}, Baseline {baseline_wins}/{total}")
        
        return insights
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save detailed results to JSON file"""
        if filename is None:
            filename = f"nancy_vs_baseline_comparison_{results['timestamp']}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\\n📁 Detailed results saved to: {filename}")
    
    def print_summary(self, results: Dict[str, Any]):
        """Print human-readable summary"""
        print("\\n" + "=" * 60)
        print("NANCY vs BASELINE RAG COMPARISON SUMMARY") 
        print("=" * 60)
        
        summary = results["summary"]
        print(f"Total Queries: {summary['total_queries']}")
        print(f"Nancy Advantages Realized: {summary['nancy_advantages_realized']}/{summary['total_queries']} ({summary['nancy_advantages_realized']/summary['total_queries']*100:.1f}%)")
        print(f"Average Response Times: Nancy {summary['avg_nancy_time']:.2f}s, Baseline {summary['avg_baseline_time']:.2f}s")
        
        print("\\n📊 INSIGHTS:")
        for insight in results["insights"]:
            print(f"   {insight}")
        
        print("\\n🎯 KEY FINDINGS:")
        advantages = summary['nancy_advantages_realized']
        total = summary['total_queries']
        
        if advantages / total >= 0.6:
            print("   ✅ Nancy shows significant functional advantages over standard RAG")
        elif advantages / total >= 0.3:
            print("   ⚠️  Nancy shows moderate advantages - architecture provides value for specific use cases") 
        else:
            print("   ❌ Nancy advantages not clearly demonstrated - may need architecture refinement")

if __name__ == "__main__":
    comparison = NancyBaselineComparison()
    
    print("Starting Nancy vs Baseline RAG Comparison...")
    print("Ensure both systems are running:")
    print("  Nancy: http://localhost:8000")
    print("  Baseline: http://localhost:8001")
    print()
    
    results = comparison.run_comparison()
    
    if "error" in results:
        print(f"❌ Comparison failed: {results['error']}")
    else:
        comparison.save_results(results)
        comparison.print_summary(results)