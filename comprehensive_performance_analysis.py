#!/usr/bin/env python3
"""
Comprehensive Performance Analysis - Nancy MCP vs Baseline RAG
Analyzes all benchmark results to provide strategic assessment
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import glob

class ComprehensivePerformanceAnalyzer:
    def __init__(self, base_dir: str = "C:\\Users\\scott\\Documents\\Nancy"):
        self.base_dir = base_dir
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "analysis_version": "1.0",
            "data_sources": [],
            "performance_metrics": {},
            "capability_analysis": {},
            "strategic_assessment": {},
            "competitive_advantages": [],
            "optimization_opportunities": [],
            "business_recommendations": []
        }
    
    def load_benchmark_results(self) -> Dict[str, Any]:
        """Load all available benchmark result files"""
        result_files = {
            "simple_benchmark": glob.glob(os.path.join(self.base_dir, "simple_benchmark_results_*.json")),
            "spreadsheet_capabilities": glob.glob(os.path.join(self.base_dir, "spreadsheet_capabilities_test_*.json")),
            "mcp_performance": glob.glob(os.path.join(self.base_dir, "mcp_performance_benchmark_*.json")),
            "comprehensive_benchmark": glob.glob(os.path.join(self.base_dir, "comprehensive_benchmark_*.json")),
            "codebase_mcp": glob.glob(os.path.join(self.base_dir, "codebase_mcp_benchmark_*.json"))
        }
        
        loaded_data = {}
        
        for category, files in result_files.items():
            if files:
                # Get most recent file
                latest_file = max(files, key=os.path.getctime)
                try:
                    with open(latest_file, 'r') as f:
                        loaded_data[category] = json.load(f)
                        self.analysis_results["data_sources"].append({
                            "category": category,
                            "file": latest_file,
                            "timestamp": datetime.fromtimestamp(os.path.getctime(latest_file)).isoformat()
                        })
                        print(f"Loaded {category}: {os.path.basename(latest_file)}")
                except Exception as e:
                    print(f"Error loading {category} from {latest_file}: {e}")
        
        return loaded_data
    
    def analyze_performance_metrics(self, benchmark_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance metrics across all benchmarks"""
        metrics = {
            "success_rates": {"nancy": [], "baseline": []},
            "response_times": {"nancy": [], "baseline": []},
            "response_qualities": {"nancy": [], "baseline": []},
            "specialized_capabilities": {},
            "mcp_benefits": {}
        }
        
        # Analyze simple benchmark
        if "simple_benchmark" in benchmark_data:
            simple = benchmark_data["simple_benchmark"]
            nancy_perf = simple.get("nancy_results", {}).get("performance_metrics", {})
            baseline_perf = simple.get("baseline_results", {}).get("performance_metrics", {})
            
            if nancy_perf:
                metrics["success_rates"]["nancy"].append(nancy_perf.get("success_rate", 0))
                metrics["response_times"]["nancy"].append(nancy_perf.get("average_response_time", 0))
                metrics["response_qualities"]["nancy"].append(nancy_perf.get("average_response_length", 0))
            
            if baseline_perf:
                metrics["success_rates"]["baseline"].append(baseline_perf.get("success_rate", 0))
                metrics["response_times"]["baseline"].append(baseline_perf.get("average_response_time", 0))
                metrics["response_qualities"]["baseline"].append(baseline_perf.get("average_response_length", 0))
        
        # Analyze spreadsheet capabilities
        if "spreadsheet_capabilities" in benchmark_data:
            spread = benchmark_data["spreadsheet_capabilities"]
            comparison = spread.get("comparison", {})
            
            nancy_metrics = comparison.get("nancy_metrics", {})
            baseline_metrics = comparison.get("baseline_metrics", {})
            
            if nancy_metrics:
                metrics["success_rates"]["nancy"].append(nancy_metrics.get("success_rate", 0))
                metrics["response_times"]["nancy"].append(nancy_metrics.get("avg_response_time", 0))
                metrics["response_qualities"]["nancy"].append(nancy_metrics.get("avg_response_length", 0))
            
            if baseline_metrics:
                metrics["success_rates"]["baseline"].append(baseline_metrics.get("success_rate", 0))
                metrics["response_times"]["baseline"].append(baseline_metrics.get("avg_response_time", 0))
                metrics["response_qualities"]["baseline"].append(baseline_metrics.get("avg_response_length", 0))
            
            # Analyze structured data capabilities
            structured_analysis = comparison.get("structured_data_analysis", {})
            metrics["specialized_capabilities"]["structured_data"] = {
                "nancy_structured_responses": structured_analysis.get("nancy_structured_responses", 0),
                "baseline_structured_responses": structured_analysis.get("baseline_structured_responses", 0),
                "nancy_team_data_responses": structured_analysis.get("nancy_team_data_responses", 0),
                "baseline_team_data_responses": structured_analysis.get("baseline_team_data_responses", 0),
                "nancy_mcp_features": structured_analysis.get("nancy_mcp_features", 0)
            }
        
        # Analyze MCP performance
        if "mcp_performance" in benchmark_data:
            mcp_data = benchmark_data["mcp_performance"]
            # Extract MCP-specific performance metrics
            if "performance_summary" in mcp_data:
                summary = mcp_data["performance_summary"]
                metrics["mcp_benefits"]["processing_efficiency"] = {
                    "rows_per_second": summary.get("processing_performance", {}).get("total_rows_per_second", 0),
                    "memory_efficiency": summary.get("memory_performance", {}).get("kb_per_row_avg", 0),
                    "knowledge_packet_overhead": summary.get("packet_generation_overhead_percent", 0)
                }
        
        # Calculate aggregate metrics
        nancy_avg_success = sum(metrics["success_rates"]["nancy"]) / len(metrics["success_rates"]["nancy"]) if metrics["success_rates"]["nancy"] else 0
        baseline_avg_success = sum(metrics["success_rates"]["baseline"]) / len(metrics["success_rates"]["baseline"]) if metrics["success_rates"]["baseline"] else 0
        
        nancy_avg_time = sum(metrics["response_times"]["nancy"]) / len(metrics["response_times"]["nancy"]) if metrics["response_times"]["nancy"] else 0
        baseline_avg_time = sum(metrics["response_times"]["baseline"]) / len(metrics["response_times"]["baseline"]) if metrics["response_times"]["baseline"] else 0
        
        nancy_avg_quality = sum(metrics["response_qualities"]["nancy"]) / len(metrics["response_qualities"]["nancy"]) if metrics["response_qualities"]["nancy"] else 0
        baseline_avg_quality = sum(metrics["response_qualities"]["baseline"]) / len(metrics["response_qualities"]["baseline"]) if metrics["response_qualities"]["baseline"] else 0
        
        metrics["aggregated"] = {
            "nancy": {
                "avg_success_rate": nancy_avg_success,
                "avg_response_time": nancy_avg_time,
                "avg_response_quality": nancy_avg_quality
            },
            "baseline": {
                "avg_success_rate": baseline_avg_success,
                "avg_response_time": baseline_avg_time,
                "avg_response_quality": baseline_avg_quality
            },
            "comparative": {
                "success_rate_improvement": ((nancy_avg_success / baseline_avg_success) - 1) * 100 if baseline_avg_success > 0 else 0,
                "response_time_ratio": nancy_avg_time / baseline_avg_time if baseline_avg_time > 0 else 0,
                "response_quality_ratio": nancy_avg_quality / baseline_avg_quality if baseline_avg_quality > 0 else 0
            }
        }
        
        return metrics
    
    def analyze_capabilities(self, benchmark_data: Dict[str, Any], performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Nancy's unique capabilities and competitive advantages"""
        capabilities = {
            "unique_features": [],
            "capability_scores": {},
            "competitive_differentiation": {},
            "value_propositions": []
        }
        
        # Identify unique Nancy features
        unique_features = set()
        
        # MCP Architecture Benefits
        if performance_metrics.get("specialized_capabilities", {}).get("structured_data", {}).get("nancy_mcp_features", 0) > 0:
            unique_features.add("MCP Architecture Routing")
            unique_features.add("Intelligent Query Orchestration")
        
        # Multi-brain coordination
        if "simple_benchmark" in benchmark_data:
            nancy_results = benchmark_data["simple_benchmark"].get("nancy_results", {}).get("query_results", [])
            for result in nancy_results:
                if result.get("strategy_used") and result["strategy_used"] != "unknown":
                    unique_features.add("Multi-Brain Strategy Selection")
                    break
                if result.get("routing_info"):
                    unique_features.add("Transparent Brain Routing")
                    break
        
        # Structured data handling
        structured_data = performance_metrics.get("specialized_capabilities", {}).get("structured_data", {})
        if structured_data.get("nancy_structured_responses", 0) > structured_data.get("baseline_structured_responses", 0):
            unique_features.add("Enhanced Structured Data Processing")
        
        if structured_data.get("nancy_team_data_responses", 0) > structured_data.get("baseline_team_data_responses", 0):
            unique_features.add("Advanced Team and Role Analysis")
        
        capabilities["unique_features"] = list(unique_features)
        
        # Calculate capability scores
        aggregated = performance_metrics.get("aggregated", {})
        nancy_perf = aggregated.get("nancy", {})
        comparative = aggregated.get("comparative", {})
        
        capabilities["capability_scores"] = {
            "query_accuracy": nancy_perf.get("avg_success_rate", 0),
            "response_quality": min(1.0, comparative.get("response_quality_ratio", 0) / 2.0),  # Normalize
            "unique_feature_count": len(unique_features),
            "structured_data_advantage": 1.0 if structured_data.get("nancy_structured_responses", 0) > structured_data.get("baseline_structured_responses", 0) else 0.5
        }
        
        # Competitive differentiation analysis
        capabilities["competitive_differentiation"] = {
            "percentage_unique_features": (len(unique_features) / 10) * 100,  # Assume 10 total possible unique features
            "structured_data_superiority": structured_data.get("nancy_structured_responses", 0) > structured_data.get("baseline_structured_responses", 0),
            "mcp_architecture_benefits": structured_data.get("nancy_mcp_features", 0) > 0,
            "response_depth_advantage": comparative.get("response_quality_ratio", 0) > 1.5
        }
        
        # Value propositions
        if capabilities["competitive_differentiation"]["structured_data_superiority"]:
            capabilities["value_propositions"].append("Superior handling of complex engineering data structures")
        
        if capabilities["competitive_differentiation"]["mcp_architecture_benefits"]:
            capabilities["value_propositions"].append("Transparent and intelligent query routing across specialized components")
        
        if capabilities["competitive_differentiation"]["response_depth_advantage"]:
            capabilities["value_propositions"].append("More comprehensive and detailed responses for complex engineering queries")
        
        if len(unique_features) >= 3:
            capabilities["value_propositions"].append("Multiple unique capabilities not available in standard RAG systems")
        
        return capabilities
    
    def generate_strategic_assessment(self, performance_metrics: Dict[str, Any], capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategic assessment and recommendations"""
        
        # Calculate overall success score
        capability_scores = capabilities.get("capability_scores", {})
        aggregated = performance_metrics.get("aggregated", {})
        
        # Weighted scoring
        weights = {
            "query_accuracy": 0.25,
            "response_quality": 0.20,
            "unique_feature_count": 0.15,
            "structured_data_advantage": 0.20,
            "competitive_differentiation": 0.20
        }
        
        overall_score = 0
        for metric, weight in weights.items():
            if metric == "unique_feature_count":
                score = min(1.0, capability_scores.get(metric, 0) / 5)  # Normalize to 0-1
            elif metric == "competitive_differentiation":
                diff_data = capabilities.get("competitive_differentiation", {})
                score = sum([
                    1 if diff_data.get("structured_data_superiority", False) else 0,
                    1 if diff_data.get("mcp_architecture_benefits", False) else 0,
                    1 if diff_data.get("response_depth_advantage", False) else 0
                ]) / 3
            else:
                score = capability_scores.get(metric, 0)
            
            overall_score += score * weight
        
        # Determine maturity and readiness
        if overall_score >= 0.8:
            maturity_level = "Production Ready"
            market_readiness = "Ready for market leadership positioning"
            investment_recommendation = "Accelerate development and marketing"
        elif overall_score >= 0.65:
            maturity_level = "Market Ready"
            market_readiness = "Ready for targeted market deployment"
            investment_recommendation = "Continue development with selective market entry"
        elif overall_score >= 0.5:
            maturity_level = "Development Stage"
            market_readiness = "Ready for pilot deployments"
            investment_recommendation = "Focus on identified improvement areas"
        else:
            maturity_level = "Early Stage"
            market_readiness = "Not ready for market deployment"
            investment_recommendation = "Fundamental improvements required"
        
        return {
            "overall_success_score": overall_score,
            "maturity_level": maturity_level,
            "market_readiness": market_readiness,
            "investment_recommendation": investment_recommendation,
            "key_strengths": capabilities.get("value_propositions", []),
            "competitive_position": "Differentiated" if len(capabilities.get("unique_features", [])) >= 3 else "Competitive",
            "business_value_clarity": "High" if overall_score >= 0.7 else "Medium" if overall_score >= 0.5 else "Low"
        }
    
    def identify_optimization_opportunities(self, performance_metrics: Dict[str, Any]) -> List[str]:
        """Identify specific optimization opportunities"""
        opportunities = []
        
        aggregated = performance_metrics.get("aggregated", {})
        comparative = aggregated.get("comparative", {})
        
        # Response time optimization
        if comparative.get("response_time_ratio", 1) > 1.5:
            opportunities.append("Optimize query processing pipeline to reduce response times")
        
        # Success rate improvements
        nancy_success = aggregated.get("nancy", {}).get("avg_success_rate", 1)
        if nancy_success < 0.95:
            opportunities.append("Improve error handling and query success rates")
        
        # MCP efficiency
        mcp_benefits = performance_metrics.get("mcp_benefits", {})
        if mcp_benefits and mcp_benefits.get("processing_efficiency", {}).get("knowledge_packet_overhead", 0) > 5:
            opportunities.append("Optimize MCP knowledge packet generation overhead")
        
        # Structured data handling
        structured_data = performance_metrics.get("specialized_capabilities", {}).get("structured_data", {})
        nancy_structured = structured_data.get("nancy_structured_responses", 0)
        total_queries = 10  # Based on spreadsheet test
        if nancy_structured < total_queries * 0.8:
            opportunities.append("Enhance structured data recognition and processing")
        
        return opportunities
    
    def generate_business_recommendations(self, strategic_assessment: Dict[str, Any], capabilities: Dict[str, Any]) -> List[str]:
        """Generate actionable business recommendations"""
        recommendations = []
        
        overall_score = strategic_assessment.get("overall_success_score", 0)
        unique_features = len(capabilities.get("unique_features", []))
        
        # Market positioning recommendations
        if overall_score >= 0.75 and unique_features >= 3:
            recommendations.extend([
                "Position Nancy as premium AI for Engineering solution with unique MCP architecture",
                "Develop thought leadership content highlighting multi-brain AI innovations",
                "Target enterprise engineering teams with complex, multi-disciplinary projects",
                "Create case studies demonstrating ROI for structured data analysis"
            ])
        elif overall_score >= 0.6:
            recommendations.extend([
                "Focus on specialized engineering workflows where Nancy shows clear advantages",
                "Pilot with friendly customers to gather success stories",
                "Develop competitive analysis highlighting unique capabilities",
                "Plan targeted optimization based on performance analysis"
            ])
        else:
            recommendations.extend([
                "Focus on core capability improvements before major market initiatives",
                "Consider strategic partnerships for complementary capabilities",
                "Develop minimum viable product for specific use cases",
                "Establish clear success metrics for next development phase"
            ])
        
        # Technical development recommendations
        competitive_diff = capabilities.get("competitive_differentiation", {})
        if competitive_diff.get("mcp_architecture_benefits", False):
            recommendations.append("Leverage MCP architecture as key differentiator in product marketing")
        
        if competitive_diff.get("structured_data_superiority", False):
            recommendations.append("Develop specialized solutions for data-heavy engineering workflows")
        
        return recommendations
    
    def execute_comprehensive_analysis(self) -> Dict[str, Any]:
        """Execute complete performance analysis"""
        print("=" * 60)
        print("COMPREHENSIVE NANCY MCP PERFORMANCE ANALYSIS")
        print("=" * 60)
        
        # Load all benchmark data
        print("\nStep 1: Loading Benchmark Data")
        print("-" * 30)
        benchmark_data = self.load_benchmark_results()
        
        if not benchmark_data:
            print("ERROR: No benchmark data found")
            return self.analysis_results
        
        # Analyze performance metrics
        print("\nStep 2: Analyzing Performance Metrics")
        print("-" * 30)
        performance_metrics = self.analyze_performance_metrics(benchmark_data)
        self.analysis_results["performance_metrics"] = performance_metrics
        
        aggregated = performance_metrics.get("aggregated", {})
        if aggregated:
            print(f"Nancy Average Success Rate: {aggregated['nancy']['avg_success_rate']:.1%}")
            print(f"Baseline Average Success Rate: {aggregated['baseline']['avg_success_rate']:.1%}")
            print(f"Response Quality Ratio: {aggregated['comparative']['response_quality_ratio']:.2f}x")
        
        # Analyze capabilities
        print("\nStep 3: Analyzing Capabilities")
        print("-" * 30)
        capabilities = self.analyze_capabilities(benchmark_data, performance_metrics)
        self.analysis_results["capability_analysis"] = capabilities
        
        print(f"Unique Features Identified: {len(capabilities['unique_features'])}")
        for feature in capabilities["unique_features"]:
            print(f"  - {feature}")
        
        # Generate strategic assessment
        print("\nStep 4: Strategic Assessment")
        print("-" * 30)
        strategic_assessment = self.generate_strategic_assessment(performance_metrics, capabilities)
        self.analysis_results["strategic_assessment"] = strategic_assessment
        
        print(f"Overall Success Score: {strategic_assessment['overall_success_score']:.1%}")
        print(f"Maturity Level: {strategic_assessment['maturity_level']}")
        print(f"Market Readiness: {strategic_assessment['market_readiness']}")
        
        # Identify optimization opportunities
        print("\nStep 5: Optimization Opportunities")
        print("-" * 30)
        optimization_opportunities = self.identify_optimization_opportunities(performance_metrics)
        self.analysis_results["optimization_opportunities"] = optimization_opportunities
        
        for opportunity in optimization_opportunities:
            print(f"  - {opportunity}")
        
        # Generate business recommendations
        print("\nStep 6: Business Recommendations")
        print("-" * 30)
        business_recommendations = self.generate_business_recommendations(strategic_assessment, capabilities)
        self.analysis_results["business_recommendations"] = business_recommendations
        
        for recommendation in business_recommendations[:5]:  # Show top 5
            print(f"  - {recommendation}")
        
        # Save comprehensive analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_file = f"comprehensive_performance_analysis_{timestamp}.json"
        
        with open(analysis_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
        
        print(f"\nComprehensive analysis saved to: {analysis_file}")
        
        # Display executive summary
        self.display_executive_summary()
        
        return self.analysis_results
    
    def display_executive_summary(self):
        """Display executive summary of analysis"""
        print("\n" + "=" * 60)
        print("EXECUTIVE SUMMARY")
        print("=" * 60)
        
        strategic = self.analysis_results.get("strategic_assessment", {})
        capabilities = self.analysis_results.get("capability_analysis", {})
        performance = self.analysis_results.get("performance_metrics", {})
        
        print(f"\nOVERALL ASSESSMENT:")
        print(f"  Success Score: {strategic.get('overall_success_score', 0):.1%}")
        print(f"  Maturity Level: {strategic.get('maturity_level', 'Unknown')}")
        print(f"  Competitive Position: {strategic.get('competitive_position', 'Unknown')}")
        print(f"  Business Value: {strategic.get('business_value_clarity', 'Unknown')}")
        
        print(f"\nKEY COMPETITIVE ADVANTAGES:")
        for strength in strategic.get("key_strengths", [])[:3]:
            print(f"  - {strength}")
        
        print(f"\nUNIQUE CAPABILITIES:")
        for feature in capabilities.get("unique_features", []):
            print(f"  - {feature}")
        
        aggregated = performance.get("aggregated", {})
        if aggregated:
            comparative = aggregated.get("comparative", {})
            print(f"\nPERFORMANCE HIGHLIGHTS:")
            if comparative.get("success_rate_improvement", 0) > 0:
                print(f"  - Success rate improvement: +{comparative['success_rate_improvement']:.1f}%")
            if comparative.get("response_quality_ratio", 0) > 1.2:
                print(f"  - Response quality ratio: {comparative['response_quality_ratio']:.1f}x baseline")
        
        print(f"\nSTRATEGIC RECOMMENDATION:")
        print(f"  {strategic.get('investment_recommendation', 'Continue assessment')}")
        
        print("\n" + "=" * 60)

def main():
    """Execute comprehensive performance analysis"""
    analyzer = ComprehensivePerformanceAnalyzer()
    results = analyzer.execute_comprehensive_analysis()
    return results

if __name__ == "__main__":
    main()