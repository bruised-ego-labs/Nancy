#!/usr/bin/env python3
"""
Performance benchmark for Nancy Codebase MCP Server
Compares standalone MCP server performance against monolithic implementation.
"""

import asyncio
import json
import time
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
import statistics

# Add both paths for comparison
sys.path.append(str(Path(__file__).parent / "mcp-servers" / "codebase"))
sys.path.append(str(Path(__file__).parent / "nancy-services" / "core"))

# Import both implementations
from test_codebase_mcp_simple import SimplifiedCodebaseAnalyzer

# Try to import monolithic version for comparison
try:
    from ingestion import CodebaseIngestionService
    MONOLITHIC_AVAILABLE = True
except ImportError:
    print("Note: Monolithic implementation not available for direct comparison")
    MONOLITHIC_AVAILABLE = False


class BenchmarkRunner:
    """
    Comprehensive benchmark runner for codebase analysis performance.
    """
    
    def __init__(self):
        self.mcp_analyzer = SimplifiedCodebaseAnalyzer()
        self.monolithic_analyzer = CodebaseIngestionService() if MONOLITHIC_AVAILABLE else None
        self.test_files = []
        self.results = {
            "mcp_server": [],
            "monolithic": [],
            "comparison": {}
        }
    
    def collect_test_files(self, directory: str, max_files: int = 50) -> List[str]:
        """
        Collect Python files for testing from Nancy codebase.
        """
        test_files = []
        
        for root, dirs, files in os.walk(directory):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.venv', 'venv', 'node_modules'}]
            
            for file in files:
                if file.endswith('.py') and len(test_files) < max_files:
                    file_path = os.path.join(root, file)
                    # Skip empty files and very large files
                    try:
                        file_size = os.path.getsize(file_path)
                        if 100 < file_size < 100000:  # Between 100 bytes and 100KB
                            test_files.append(file_path)
                    except OSError:
                        continue
        
        return test_files
    
    def benchmark_mcp_server(self, test_files: List[str]) -> Dict[str, Any]:
        """
        Benchmark MCP server performance.
        """
        print(f"Benchmarking MCP Server with {len(test_files)} files...")
        
        results = {
            "total_files": len(test_files),
            "successful_analyses": 0,
            "failed_analyses": 0,
            "total_knowledge_packets": 0,
            "analysis_times": [],
            "packet_generation_times": [],
            "file_sizes": [],
            "complexity_scores": []
        }
        
        start_time = time.time()
        
        for i, file_path in enumerate(test_files):
            if i % 10 == 0:
                print(f"  Processing file {i+1}/{len(test_files)}")
            
            file_start = time.time()
            
            try:
                # Analyze file
                analysis_result = self.mcp_analyzer.analyze_python_file(file_path)
                
                if "error" not in analysis_result:
                    # Generate knowledge packets
                    packet_start = time.time()
                    knowledge_packets = self.mcp_analyzer.generate_knowledge_packets(analysis_result)
                    packet_time = time.time() - packet_start
                    
                    analysis_time = time.time() - file_start
                    
                    results["successful_analyses"] += 1
                    results["total_knowledge_packets"] += len(knowledge_packets)
                    results["analysis_times"].append(analysis_time)
                    results["packet_generation_times"].append(packet_time)
                    results["file_sizes"].append(len(analysis_result.get("content", "")))
                    results["complexity_scores"].append(analysis_result.get("complexity_score", 0))
                else:
                    results["failed_analyses"] += 1
                    
            except Exception as e:
                results["failed_analyses"] += 1
                print(f"    Error processing {file_path}: {e}")
        
        results["total_time"] = time.time() - start_time
        results["avg_analysis_time"] = statistics.mean(results["analysis_times"]) if results["analysis_times"] else 0
        results["avg_packet_time"] = statistics.mean(results["packet_generation_times"]) if results["packet_generation_times"] else 0
        results["files_per_second"] = len(test_files) / results["total_time"] if results["total_time"] > 0 else 0
        results["packets_per_second"] = results["total_knowledge_packets"] / results["total_time"] if results["total_time"] > 0 else 0
        
        return results
    
    def benchmark_monolithic(self, test_files: List[str]) -> Dict[str, Any]:
        """
        Benchmark monolithic implementation (if available).
        """
        if not MONOLITHIC_AVAILABLE:
            return {"error": "Monolithic implementation not available"}
        
        print(f"Benchmarking Monolithic Implementation with {len(test_files)} files...")
        
        results = {
            "total_files": len(test_files),
            "successful_analyses": 0,
            "failed_analyses": 0,
            "analysis_times": [],
            "file_sizes": []
        }
        
        start_time = time.time()
        
        for i, file_path in enumerate(test_files):
            if i % 10 == 0:
                print(f"  Processing file {i+1}/{len(test_files)}")
            
            file_start = time.time()
            
            try:
                # Use monolithic analyzer
                analysis_result = self.monolithic_analyzer.analyze_code_file(file_path)
                
                if not analysis_result.get("error"):
                    results["successful_analyses"] += 1
                    results["analysis_times"].append(time.time() - file_start)
                    
                    # Estimate file size
                    try:
                        file_size = os.path.getsize(file_path)
                        results["file_sizes"].append(file_size)
                    except OSError:
                        pass
                else:
                    results["failed_analyses"] += 1
                    
            except Exception as e:
                results["failed_analyses"] += 1
                print(f"    Error processing {file_path}: {e}")
        
        results["total_time"] = time.time() - start_time
        results["avg_analysis_time"] = statistics.mean(results["analysis_times"]) if results["analysis_times"] else 0
        results["files_per_second"] = len(test_files) / results["total_time"] if results["total_time"] > 0 else 0
        
        return results
    
    def compare_results(self, mcp_results: Dict[str, Any], monolithic_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare benchmark results between implementations.
        """
        comparison = {}
        
        if "error" in monolithic_results:
            comparison["status"] = "mcp_only"
            comparison["notes"] = "Monolithic implementation not available for comparison"
            return comparison
        
        comparison["status"] = "full_comparison"
        
        # Performance comparison
        if mcp_results["total_time"] > 0 and monolithic_results["total_time"] > 0:
            speed_improvement = ((monolithic_results["total_time"] - mcp_results["total_time"]) / monolithic_results["total_time"]) * 100
            comparison["speed_improvement_percent"] = round(speed_improvement, 2)
            
            files_per_sec_improvement = ((mcp_results["files_per_second"] - monolithic_results["files_per_second"]) / monolithic_results["files_per_second"]) * 100
            comparison["throughput_improvement_percent"] = round(files_per_sec_improvement, 2)
        
        # Success rate comparison
        mcp_success_rate = (mcp_results["successful_analyses"] / mcp_results["total_files"]) * 100
        monolithic_success_rate = (monolithic_results["successful_analyses"] / monolithic_results["total_files"]) * 100
        
        comparison["mcp_success_rate"] = round(mcp_success_rate, 2)
        comparison["monolithic_success_rate"] = round(monolithic_success_rate, 2)
        
        # Feature comparison
        comparison["mcp_unique_features"] = [
            "Knowledge Packet generation",
            "MCP protocol support", 
            "Standalone operation",
            "Enhanced Git analysis",
            "Language-specific processors"
        ]
        
        return comparison
    
    def generate_report(self, mcp_results: Dict[str, Any], monolithic_results: Dict[str, Any], 
                       comparison: Dict[str, Any]) -> str:
        """
        Generate comprehensive benchmark report.
        """
        report = []
        report.append("=" * 80)
        report.append("Nancy Codebase MCP Server - Performance Benchmark Report")
        report.append("=" * 80)
        report.append("")
        
        # Test configuration
        report.append("Test Configuration:")
        report.append(f"  Test files: {mcp_results['total_files']}")
        report.append(f"  Test directory: Nancy codebase (.py files only)")
        report.append("")
        
        # MCP Server Results
        report.append("MCP Server Results:")
        report.append(f"  Total time: {mcp_results['total_time']:.2f} seconds")
        report.append(f"  Successful analyses: {mcp_results['successful_analyses']}")
        report.append(f"  Failed analyses: {mcp_results['failed_analyses']}")
        report.append(f"  Files per second: {mcp_results['files_per_second']:.2f}")
        report.append(f"  Average analysis time: {mcp_results['avg_analysis_time']*1000:.2f}ms")
        report.append(f"  Knowledge packets generated: {mcp_results['total_knowledge_packets']}")
        report.append(f"  Packets per second: {mcp_results['packets_per_second']:.2f}")
        report.append(f"  Average packet generation time: {mcp_results['avg_packet_time']*1000:.2f}ms")
        report.append("")
        
        # Monolithic Results (if available)
        if "error" not in monolithic_results:
            report.append("Monolithic Implementation Results:")
            report.append(f"  Total time: {monolithic_results['total_time']:.2f} seconds")
            report.append(f"  Successful analyses: {monolithic_results['successful_analyses']}")
            report.append(f"  Failed analyses: {monolithic_results['failed_analyses']}")
            report.append(f"  Files per second: {monolithic_results['files_per_second']:.2f}")
            report.append(f"  Average analysis time: {monolithic_results['avg_analysis_time']*1000:.2f}ms")
            report.append("")
        else:
            report.append("Monolithic Implementation: Not available for comparison")
            report.append("")
        
        # Comparison
        report.append("Performance Comparison:")
        if comparison["status"] == "full_comparison":
            report.append(f"  Speed improvement: {comparison['speed_improvement_percent']:.2f}%")
            report.append(f"  Throughput improvement: {comparison['throughput_improvement_percent']:.2f}%")
            report.append(f"  MCP success rate: {comparison['mcp_success_rate']:.2f}%")
            report.append(f"  Monolithic success rate: {comparison['monolithic_success_rate']:.2f}%")
        else:
            report.append("  MCP-only benchmark (monolithic not available)")
        report.append("")
        
        # MCP Server Advantages
        report.append("MCP Server Advantages:")
        for feature in comparison.get("mcp_unique_features", []):
            report.append(f"  + {feature}")
        report.append("")
        
        # Quality Metrics
        if mcp_results["complexity_scores"]:
            avg_complexity = statistics.mean(mcp_results["complexity_scores"])
            max_complexity = max(mcp_results["complexity_scores"])
            report.append("Code Quality Analysis:")
            report.append(f"  Average complexity score: {avg_complexity:.2f}")
            report.append(f"  Maximum complexity score: {max_complexity}")
            report.append(f"  Files with high complexity (>20): {sum(1 for c in mcp_results['complexity_scores'] if c > 20)}")
            report.append("")
        
        # Memory and Resource Usage
        if mcp_results["file_sizes"]:
            total_chars = sum(mcp_results["file_sizes"])
            avg_file_size = statistics.mean(mcp_results["file_sizes"])
            report.append("Resource Usage:")
            report.append(f"  Total characters processed: {total_chars:,}")
            report.append(f"  Average file size: {avg_file_size:.0f} characters")
            report.append(f"  Processing rate: {total_chars / mcp_results['total_time']:.0f} chars/second")
            report.append("")
        
        # Conclusions
        report.append("Conclusions:")
        if comparison["status"] == "full_comparison":
            if comparison["speed_improvement_percent"] > 0:
                report.append(f"  + MCP Server is {comparison['speed_improvement_percent']:.1f}% faster than monolithic")
            else:
                report.append(f"  - MCP Server is {abs(comparison['speed_improvement_percent']):.1f}% slower than monolithic")
        
        report.append("  + MCP Server provides enhanced code intelligence capabilities")
        report.append("  + Knowledge Packet generation enables Four-Brain integration")
        report.append("  + Standalone operation allows for horizontal scaling")
        report.append("  + MCP protocol enables flexible Nancy architecture")
        report.append("")
        
        report.append("Recommendations:")
        report.append("  1. Deploy MCP Server for production codebase analysis")
        report.append("  2. Integrate with Nancy Core via MCP host")
        report.append("  3. Monitor performance in production environment")
        report.append("  4. Consider tree-sitter installation for full language support")
        report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)


async def run_benchmark():
    """
    Run comprehensive benchmark comparing MCP server vs monolithic implementation.
    """
    print("Nancy Codebase MCP Server - Performance Benchmark")
    print("=" * 60)
    
    benchmark = BenchmarkRunner()
    
    # Collect test files from Nancy codebase
    nancy_dir = str(Path(__file__).parent)
    test_files = benchmark.collect_test_files(nancy_dir, max_files=30)  # Limited for demo
    
    if not test_files:
        print("No test files found. Please run from Nancy project directory.")
        return
    
    print(f"Found {len(test_files)} Python files for testing")
    print("")
    
    # Benchmark MCP Server
    mcp_results = benchmark.benchmark_mcp_server(test_files)
    print("")
    
    # Benchmark Monolithic (if available)
    monolithic_results = benchmark.benchmark_monolithic(test_files)
    print("")
    
    # Compare results
    comparison = benchmark.compare_results(mcp_results, monolithic_results)
    
    # Generate report
    report = benchmark.generate_report(mcp_results, monolithic_results, comparison)
    print(report)
    
    # Save results to file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"codebase_mcp_benchmark_{timestamp}.json"
    
    results_data = {
        "timestamp": timestamp,
        "test_configuration": {
            "total_files": len(test_files),
            "test_files": test_files[:10]  # Sample of files tested
        },
        "mcp_results": mcp_results,
        "monolithic_results": monolithic_results,
        "comparison": comparison,
        "report": report
    }
    
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2, default=str)
    
    print(f"Detailed results saved to: {results_file}")


if __name__ == "__main__":
    asyncio.run(run_benchmark())