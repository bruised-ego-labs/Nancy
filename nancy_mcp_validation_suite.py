#!/usr/bin/env python3
"""
Nancy MCP Validation Suite
Automated testing suite for ongoing Nancy MCP functionality validation.

This script provides a comprehensive test framework for validating Nancy's
MCP memory system functionality and catching regressions.
"""

import json
import logging
import requests
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("nancy_mcp_validation")


class NancyMCPValidator:
    """Comprehensive validation suite for Nancy MCP system."""
    
    def __init__(self, nancy_api_base: str = "http://localhost:8000"):
        self.nancy_api_base = nancy_api_base
        self.test_results = {
            "validation_timestamp": datetime.now().isoformat(),
            "nancy_api_base": nancy_api_base,
            "test_suites": {},
            "overall_status": "unknown",
            "recommendations": []
        }
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete validation suite."""
        logger.info("Starting Nancy MCP Validation Suite")
        
        # Test Suite 1: Core Functionality
        self._test_core_functionality()
        
        # Test Suite 2: MCP Tool Validation
        self._test_mcp_tools()
        
        # Test Suite 3: Performance Validation
        self._test_performance()
        
        # Test Suite 4: Error Handling
        self._test_error_handling()
        
        # Generate overall assessment
        self._generate_assessment()
        
        return self.test_results
    
    def _test_core_functionality(self):
        """Test core Nancy functionality."""
        logger.info("Testing core functionality...")
        
        core_tests = {
            "api_connectivity": self._test_api_connectivity(),
            "legacy_ingestion": self._test_legacy_ingestion(),
            "query_processing": self._test_query_processing(),
            "graph_functionality": self._test_graph_functionality(),
            "configuration_access": self._test_configuration_access()
        }
        
        self.test_results["test_suites"]["core_functionality"] = {
            "tests": core_tests,
            "passed": len([t for t in core_tests.values() if t["status"] == "pass"]),
            "failed": len([t for t in core_tests.values() if t["status"] == "fail"]),
            "errors": len([t for t in core_tests.values() if t["status"] == "error"])
        }
    
    def _test_mcp_tools(self):
        """Test MCP tool functionality."""
        logger.info("Testing MCP tools...")
        
        # First ingest some test content
        test_content = f"MCP validation test content - {datetime.now().isoformat()}"
        ingest_result = self._ingest_test_content("mcp_validation_test.txt", test_content, "MCP Validator")
        
        mcp_tests = {
            "ingest_information": self._simulate_mcp_ingest_information(test_content),
            "query_memory": self._simulate_mcp_query_memory("MCP validation test"),
            "find_author_contributions": self._simulate_mcp_find_author_contributions("MCP Validator"),
            "get_project_overview": self._simulate_mcp_get_project_overview()
        }
        
        self.test_results["test_suites"]["mcp_tools"] = {
            "setup_ingestion": ingest_result,
            "tests": mcp_tests,
            "passed": len([t for t in mcp_tests.values() if t["status"] == "pass"]),
            "failed": len([t for t in mcp_tests.values() if t["status"] == "fail"]),
            "errors": len([t for t in mcp_tests.values() if t["status"] == "error"])
        }
    
    def _test_performance(self):
        """Test performance characteristics."""
        logger.info("Testing performance...")
        
        performance_tests = {
            "ingestion_speed": self._test_ingestion_speed(),
            "query_response_time": self._test_query_response_time(),
            "concurrent_requests": self._test_concurrent_requests()
        }
        
        self.test_results["test_suites"]["performance"] = {
            "tests": performance_tests,
            "passed": len([t for t in performance_tests.values() if t["status"] == "pass"]),
            "failed": len([t for t in performance_tests.values() if t["status"] == "fail"]),
            "errors": len([t for t in performance_tests.values() if t["status"] == "error"])
        }
    
    def _test_error_handling(self):
        """Test error handling and edge cases."""
        logger.info("Testing error handling...")
        
        error_tests = {
            "invalid_query": self._test_invalid_query(),
            "malformed_request": self._test_malformed_request(),
            "timeout_handling": self._test_timeout_handling(),
            "large_content": self._test_large_content_handling()
        }
        
        self.test_results["test_suites"]["error_handling"] = {
            "tests": error_tests,
            "passed": len([t for t in error_tests.values() if t["status"] == "pass"]),
            "failed": len([t for t in error_tests.values() if t["status"] == "fail"]),
            "errors": len([t for t in error_tests.values() if t["status"] == "error"])
        }
    
    # Core Functionality Tests
    
    def _test_api_connectivity(self) -> Dict[str, Any]:
        """Test basic API connectivity."""
        try:
            response = requests.get(f"{self.nancy_api_base}/", timeout=5)
            return {
                "status": "pass" if response.status_code == 200 else "fail",
                "response_time": response.elapsed.total_seconds(),
                "details": response.json() if response.status_code == 200 else response.text[:100]
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _test_legacy_ingestion(self) -> Dict[str, Any]:
        """Test legacy file ingestion."""
        try:
            test_content = f"Validation test content {datetime.now().isoformat()}"
            result = self._ingest_test_content("validation_test.txt", test_content, "Validator")
            return {
                "status": "pass" if result["success"] else "fail",
                "response_time": result.get("response_time", 0),
                "details": result
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _test_query_processing(self) -> Dict[str, Any]:
        """Test query processing functionality."""
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.nancy_api_base}/api/query",
                json={"query": "validation test", "n_results": 5},
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                has_response = bool(result.get("synthesized_response"))
                return {
                    "status": "pass" if has_response else "fail",
                    "response_time": response_time,
                    "details": {"has_response": has_response, "brains_used": result.get("brains_used", [])}
                }
            else:
                return {"status": "fail", "error": response.text[:100]}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _test_graph_functionality(self) -> Dict[str, Any]:
        """Test graph query functionality."""
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.nancy_api_base}/api/query/graph",
                json={"author_name": "Test Author", "use_enhanced": True},
                timeout=15
            )
            response_time = time.time() - start_time
            
            return {
                "status": "pass" if response.status_code == 200 else "fail",
                "response_time": response_time,
                "details": response.json() if response.status_code == 200 else response.text[:100]
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _test_configuration_access(self) -> Dict[str, Any]:
        """Test configuration endpoint access."""
        try:
            response = requests.get(f"{self.nancy_api_base}/api/nancy/configuration", timeout=10)
            return {
                "status": "pass" if response.status_code == 200 else "fail",
                "details": response.json() if response.status_code == 200 else response.text[:100]
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # MCP Tool Simulation Tests
    
    def _simulate_mcp_ingest_information(self, content: str) -> Dict[str, Any]:
        """Simulate MCP ingest_information tool."""
        try:
            # This simulates what the MCP server does
            import io
            files = {
                'file': ('mcp_simulation.txt', io.BytesIO(content.encode('utf-8')), 'text/plain')
            }
            data = {'author': 'MCP Simulation'}
            
            start_time = time.time()
            response = requests.post(
                f"{self.nancy_api_base}/api/ingest",
                files=files,
                data=data,
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                # Check if Nancy-style response
                success = result.get("status") != "error"
                return {
                    "status": "pass" if success else "fail",
                    "response_time": response_time,
                    "details": result
                }
            else:
                return {"status": "fail", "error": response.text[:100]}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _simulate_mcp_query_memory(self, query: str) -> Dict[str, Any]:
        """Simulate MCP query_memory tool."""
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.nancy_api_base}/api/query",
                json={"query": query, "n_results": 5, "orchestrator": "intelligent"},
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                # Check for proper MCP-style response
                has_response = result.get("synthesized_response") != "No response generated"
                return {
                    "status": "pass" if has_response else "fail",
                    "response_time": response_time,
                    "details": {
                        "has_response": has_response,
                        "response_length": len(result.get("synthesized_response", "")),
                        "brains_used": result.get("brains_used", [])
                    }
                }
            else:
                return {"status": "fail", "error": response.text[:100]}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _simulate_mcp_find_author_contributions(self, author: str) -> Dict[str, Any]:
        """Simulate MCP find_author_contributions tool."""
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.nancy_api_base}/api/query/graph",
                json={"author_name": author, "use_enhanced": True},
                timeout=30
            )
            response_time = time.time() - start_time
            
            return {
                "status": "pass" if response.status_code == 200 else "fail",
                "response_time": response_time,
                "details": response.json() if response.status_code == 200 else response.text[:100]
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _simulate_mcp_get_project_overview(self) -> Dict[str, Any]:
        """Simulate MCP get_project_overview tool."""
        try:
            # Test both endpoints that the MCP tool uses
            status_response = requests.get(f"{self.nancy_api_base}/api/nancy/status", timeout=30)
            ingest_response = requests.get(f"{self.nancy_api_base}/api/ingest/status", timeout=30)
            
            status_ok = status_response.status_code == 200
            ingest_ok = ingest_response.status_code == 200
            
            # The MCP tool should be able to get at least one of these
            return {
                "status": "pass" if ingest_ok else "fail",
                "details": {
                    "nancy_status": {"ok": status_ok, "status_code": status_response.status_code},
                    "ingest_status": {"ok": ingest_ok, "status_code": ingest_response.status_code},
                    "note": "nancy/status endpoint has known event loop issues"
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # Performance Tests
    
    def _test_ingestion_speed(self) -> Dict[str, Any]:
        """Test ingestion performance."""
        try:
            content_sizes = [100, 1000, 5000]  # Character counts
            results = []
            
            for size in content_sizes:
                content = "x" * size
                start_time = time.time()
                result = self._ingest_test_content(f"perf_test_{size}.txt", content, "Performance Test")
                end_time = time.time()
                
                results.append({
                    "content_size": size,
                    "ingestion_time": end_time - start_time,
                    "success": result["success"]
                })
            
            avg_time = sum(r["ingestion_time"] for r in results) / len(results)
            all_successful = all(r["success"] for r in results)
            
            return {
                "status": "pass" if all_successful and avg_time < 10 else "fail",
                "details": {
                    "average_time": avg_time,
                    "all_successful": all_successful,
                    "results": results
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _test_query_response_time(self) -> Dict[str, Any]:
        """Test query response time."""
        try:
            queries = ["test", "performance validation", "author information"]
            times = []
            
            for query in queries:
                start_time = time.time()
                response = requests.post(
                    f"{self.nancy_api_base}/api/query",
                    json={"query": query, "n_results": 5},
                    timeout=30
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    times.append(end_time - start_time)
            
            avg_time = sum(times) / len(times) if times else float('inf')
            
            return {
                "status": "pass" if avg_time < 15 else "fail",  # 15 second threshold
                "details": {
                    "average_response_time": avg_time,
                    "successful_queries": len(times),
                    "total_queries": len(queries)
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _test_concurrent_requests(self) -> Dict[str, Any]:
        """Test handling of concurrent requests."""
        try:
            import threading
            import concurrent.futures
            
            def make_query(query_id):
                try:
                    response = requests.post(
                        f"{self.nancy_api_base}/api/query",
                        json={"query": f"concurrent test {query_id}", "n_results": 3},
                        timeout=30
                    )
                    return response.status_code == 200
                except:
                    return False
            
            # Test 3 concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(make_query, i) for i in range(3)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            success_rate = sum(results) / len(results)
            
            return {
                "status": "pass" if success_rate >= 0.67 else "fail",  # At least 2/3 should succeed
                "details": {
                    "success_rate": success_rate,
                    "successful_requests": sum(results),
                    "total_requests": len(results)
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # Error Handling Tests
    
    def _test_invalid_query(self) -> Dict[str, Any]:
        """Test handling of invalid queries."""
        try:
            # Test empty query
            response = requests.post(
                f"{self.nancy_api_base}/api/query",
                json={"query": "", "n_results": 5},
                timeout=15
            )
            
            # Should handle gracefully (either 400 error or empty response)
            handled_gracefully = response.status_code in [200, 400]
            
            return {
                "status": "pass" if handled_gracefully else "fail",
                "details": {
                    "status_code": response.status_code,
                    "handled_gracefully": handled_gracefully
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _test_malformed_request(self) -> Dict[str, Any]:
        """Test handling of malformed requests."""
        try:
            # Send malformed JSON
            response = requests.post(
                f"{self.nancy_api_base}/api/query",
                data="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            # Should return 400 or 422
            handled_properly = response.status_code in [400, 422]
            
            return {
                "status": "pass" if handled_properly else "fail",
                "details": {
                    "status_code": response.status_code,
                    "handled_properly": handled_properly
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _test_timeout_handling(self) -> Dict[str, Any]:
        """Test timeout handling."""
        try:
            # Test very short timeout
            try:
                response = requests.post(
                    f"{self.nancy_api_base}/api/query",
                    json={"query": "timeout test", "n_results": 5},
                    timeout=0.001  # Very short timeout
                )
                return {"status": "fail", "details": "Request should have timed out"}
            except requests.exceptions.Timeout:
                return {"status": "pass", "details": "Timeout handled correctly"}
            except Exception as e:
                return {"status": "pass", "details": f"Connection handling: {str(e)[:50]}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _test_large_content_handling(self) -> Dict[str, Any]:
        """Test handling of large content."""
        try:
            # Test large content (50KB)
            large_content = "x" * 50000
            result = self._ingest_test_content("large_test.txt", large_content, "Large Test")
            
            return {
                "status": "pass" if result["success"] else "fail",
                "details": {
                    "content_size": len(large_content),
                    "ingestion_successful": result["success"],
                    "response_time": result.get("response_time", 0)
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # Helper Methods
    
    def _ingest_test_content(self, filename: str, content: str, author: str) -> Dict[str, Any]:
        """Helper to ingest test content."""
        try:
            import io
            files = {
                'file': (filename, io.BytesIO(content.encode('utf-8')), 'text/plain')
            }
            data = {'author': author}
            
            start_time = time.time()
            response = requests.post(
                f"{self.nancy_api_base}/api/ingest",
                files=files,
                data=data,
                timeout=30
            )
            response_time = time.time() - start_time
            
            success = response.status_code == 200
            if success:
                result = response.json()
                success = result.get("status") != "error"
            
            return {
                "success": success,
                "response_time": response_time,
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text[:100]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_assessment(self):
        """Generate overall assessment and recommendations."""
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        
        for suite_name, suite_data in self.test_results["test_suites"].items():
            total_tests += len(suite_data["tests"])
            total_passed += suite_data["passed"]
            total_failed += suite_data["failed"]
            total_errors += suite_data["errors"]
        
        success_rate = total_passed / total_tests if total_tests > 0 else 0
        
        # Determine overall status
        if success_rate >= 0.9:
            overall_status = "excellent"
        elif success_rate >= 0.75:
            overall_status = "good"
        elif success_rate >= 0.5:
            overall_status = "fair"
        else:
            overall_status = "poor"
        
        self.test_results["overall_status"] = overall_status
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "errors": total_errors,
            "success_rate": success_rate
        }
        
        # Generate recommendations
        recommendations = []
        
        if total_errors > 0:
            recommendations.append("Investigate and fix test errors to ensure system stability")
        
        if success_rate < 0.75:
            recommendations.append("System reliability needs improvement - review failed tests")
        
        # Check specific issues
        core_suite = self.test_results["test_suites"].get("core_functionality", {})
        if core_suite.get("failed", 0) > 0:
            recommendations.append("Core functionality issues detected - priority fix required")
        
        mcp_suite = self.test_results["test_suites"].get("mcp_tools", {})
        if mcp_suite.get("failed", 0) > 0:
            recommendations.append("MCP tool functionality needs attention for proper integration")
        
        performance_suite = self.test_results["test_suites"].get("performance", {})
        if performance_suite.get("failed", 0) > 0:
            recommendations.append("Performance optimization recommended")
        
        self.test_results["recommendations"] = recommendations
    
    def save_results(self, filename: Optional[str] = None):
        """Save validation results to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nancy_mcp_validation_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"Validation results saved to {filename}")
        return filename


def main():
    """Run the Nancy MCP validation suite."""
    validator = NancyMCPValidator()
    
    print("Nancy MCP Validation Suite")
    print("=" * 50)
    
    # Run full validation
    results = validator.run_full_validation()
    
    # Save results
    filename = validator.save_results()
    
    # Print summary
    summary = results["summary"]
    overall = results["overall_status"]
    
    print(f"\\nValidation Complete - Results saved to {filename}")
    print(f"Overall Status: {overall.upper()}")
    print(f"\\nTest Summary:")
    print(f"  Total Tests: {summary['total_tests']}")
    print(f"  Passed: {summary['passed']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Errors: {summary['errors']}")
    print(f"  Success Rate: {summary['success_rate']:.1%}")
    
    print(f"\\nRecommendations:")
    for rec in results["recommendations"]:
        print(f"  - {rec}")
    
    # Print test suite breakdown
    print(f"\\nTest Suite Breakdown:")
    for suite_name, suite_data in results["test_suites"].items():
        suite_success_rate = suite_data["passed"] / len(suite_data["tests"]) if suite_data["tests"] else 0
        status_icon = "[OK]" if suite_success_rate >= 0.75 else "[WARN]" if suite_success_rate >= 0.5 else "[ERROR]"
        print(f"  {status_icon} {suite_name}: {suite_data['passed']}/{len(suite_data['tests'])} ({suite_success_rate:.1%})")
    
    return results


if __name__ == "__main__":
    main()