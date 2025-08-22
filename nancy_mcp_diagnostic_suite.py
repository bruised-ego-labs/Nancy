#!/usr/bin/env python3
"""
Nancy MCP Diagnostic Suite
Comprehensive testing and validation of Nancy MCP memory system functionality.

This script performs systematic testing of all Nancy MCP tools and identifies
specific failure points in the memory system architecture.
"""

import json
import logging
import requests
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("nancy_mcp_diagnostic")

class NancyMCPDiagnostic:
    """Comprehensive diagnostic suite for Nancy MCP memory system."""
    
    def __init__(self, nancy_api_base: str = "http://localhost:8000"):
        self.nancy_api_base = nancy_api_base
        self.test_results = {
            "diagnostic_timestamp": datetime.now().isoformat(),
            "nancy_api_base": nancy_api_base,
            "system_health": {},
            "individual_tests": {},
            "integration_tests": {},
            "identified_issues": [],
            "recommendations": []
        }
        
    def run_complete_diagnostic(self) -> Dict[str, Any]:
        """Run complete diagnostic suite."""
        logger.info("Starting Nancy MCP Diagnostic Suite")
        
        # 1. System Health Check
        self._test_system_health()
        
        # 2. Direct API Tests
        self._test_direct_api_endpoints()
        
        # 3. MCP Tool Simulation Tests
        self._test_mcp_tool_simulation()
        
        # 4. Integration Flow Tests
        self._test_integration_flows()
        
        # 5. Event Loop Investigation
        self._investigate_event_loop_issues()
        
        # 6. Analyze Results and Generate Recommendations
        self._analyze_results()
        
        return self.test_results
    
    def _test_system_health(self):
        """Test basic system health and connectivity."""
        logger.info("Testing system health...")
        
        health_tests = {}
        
        # Basic connectivity
        try:
            response = requests.get(f"{self.nancy_api_base}/health", timeout=10)
            health_tests["connectivity"] = {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            health_tests["connectivity"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Nancy status endpoint
        try:
            response = requests.get(f"{self.nancy_api_base}/api/nancy/status", timeout=10)
            health_tests["nancy_status"] = {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            health_tests["nancy_status"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Configuration endpoint
        try:
            response = requests.get(f"{self.nancy_api_base}/api/nancy/configuration", timeout=10)
            health_tests["configuration"] = {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            health_tests["configuration"] = {
                "status": "error",
                "error": str(e)
            }
        
        self.test_results["system_health"] = health_tests
    
    def _test_direct_api_endpoints(self):
        """Test Nancy's direct API endpoints that MCP tools use."""
        logger.info("Testing direct API endpoints...")
        
        api_tests = {}
        
        # Test ingestion endpoint (legacy)
        test_content = "This is a test document for Nancy MCP diagnostic suite."
        test_author = "MCP Diagnostic Suite"
        
        try:
            import io
            files = {
                'file': ('test_diagnostic.txt', io.BytesIO(test_content.encode('utf-8')), 'text/plain')
            }
            data = {'author': test_author}
            
            response = requests.post(
                f"{self.nancy_api_base}/api/ingest",
                files=files,
                data=data,
                timeout=30
            )
            
            api_tests["legacy_ingestion"] = {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text[:500]
            }
            
        except Exception as e:
            api_tests["legacy_ingestion"] = {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        
        # Test knowledge packet ingestion
        try:
            packet_data = {
                "content": test_content,
                "content_type": "text",
                "author": test_author,
                "filename": "test_diagnostic_packet.txt",
                "metadata": {"test": "diagnostic_suite"},
                "source": "mcp_diagnostic",
                "brain_routing": "auto"
            }
            
            response = requests.post(
                f"{self.nancy_api_base}/api/ingest/knowledge-packet",
                json=packet_data,
                timeout=30
            )
            
            api_tests["knowledge_packet_ingestion"] = {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text[:500]
            }
            
        except Exception as e:
            api_tests["knowledge_packet_ingestion"] = {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        
        # Test query endpoint
        try:
            query_data = {
                "query": "diagnostic test content",
                "n_results": 5,
                "orchestrator": "intelligent"
            }
            
            response = requests.post(
                f"{self.nancy_api_base}/api/query",
                json=query_data,
                timeout=60
            )
            
            api_tests["query_endpoint"] = {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text[:500]
            }
            
        except Exception as e:
            api_tests["query_endpoint"] = {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        
        # Test graph query endpoint
        try:
            graph_data = {
                "author_name": test_author,
                "use_enhanced": True
            }
            
            response = requests.post(
                f"{self.nancy_api_base}/api/query/graph",
                json=graph_data,
                timeout=30
            )
            
            api_tests["graph_query"] = {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text[:500]
            }
            
        except Exception as e:
            api_tests["graph_query"] = {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        
        self.test_results["individual_tests"]["direct_api"] = api_tests
    
    def _test_mcp_tool_simulation(self):
        """Simulate MCP tool calls to identify specific issues."""
        logger.info("Testing MCP tool simulation...")
        
        mcp_tests = {}
        
        # Test 1: Ingest Information (simulate MCP tool)
        test_content = "Nancy MCP diagnostic test - This document tests the ingestion capabilities."
        
        try:
            # Simulate the ingest_information tool logic
            # First check Nancy mode
            health_response = requests.get(f"{self.nancy_api_base}/health", timeout=10)
            nancy_mode = "unknown"
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                nancy_mode = health_data.get("nancy_core", {}).get("migration_mode", "unknown")
            
            # Use appropriate ingestion method
            if nancy_mode == "mcp":
                packet_data = {
                    "content": test_content,
                    "content_type": "text",
                    "author": "MCP Diagnostic",
                    "filename": "mcp_diagnostic_test.txt",
                    "metadata": {"diagnostic": True},
                    "source": "mcp_client",
                    "brain_routing": "auto"
                }
                
                response = requests.post(
                    f"{self.nancy_api_base}/api/ingest/knowledge-packet",
                    json=packet_data,
                    timeout=30
                )
            else:
                # Legacy mode
                import io
                files = {
                    'file': ('mcp_diagnostic_test.txt', io.BytesIO(test_content.encode('utf-8')), 'text/plain')
                }
                data = {'author': 'MCP Diagnostic'}
                
                response = requests.post(
                    f"{self.nancy_api_base}/api/ingest",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            mcp_tests["ingest_information"] = {
                "status": "success" if response.status_code == 200 else "failed",
                "nancy_mode": nancy_mode,
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text[:500]
            }
            
        except Exception as e:
            mcp_tests["ingest_information"] = {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        
        # Test 2: Query Memory (simulate MCP tool)
        try:
            query_data = {
                "query": "diagnostic test",
                "n_results": 5,
                "orchestrator": "intelligent"
            }
            
            response = requests.post(
                f"{self.nancy_api_base}/api/query",
                json=query_data,
                timeout=60
            )
            
            mcp_tests["query_memory"] = {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text[:500]
            }
            
        except Exception as e:
            mcp_tests["query_memory"] = {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        
        # Test 3: Find Author Contributions (simulate MCP tool)
        try:
            author_data = {
                "author_name": "MCP Diagnostic",
                "use_enhanced": True
            }
            
            response = requests.post(
                f"{self.nancy_api_base}/api/query/graph",
                json=author_data,
                timeout=30
            )
            
            mcp_tests["find_author_contributions"] = {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text[:500]
            }
            
        except Exception as e:
            mcp_tests["find_author_contributions"] = {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        
        # Test 4: Get Project Overview (simulate MCP tool)
        try:
            # This should trigger the problematic endpoint
            response = requests.get(
                f"{self.nancy_api_base}/api/nancy/status",
                timeout=30
            )
            
            status_result = {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text[:500]
            }
            
            # Also test ingestion status
            ingest_response = requests.get(
                f"{self.nancy_api_base}/api/ingest/status",
                timeout=30
            )
            
            mcp_tests["get_project_overview"] = {
                "nancy_status": status_result,
                "ingest_status": {
                    "status": "success" if ingest_response.status_code == 200 else "failed",
                    "status_code": ingest_response.status_code,
                    "response": ingest_response.json() if ingest_response.status_code == 200 else ingest_response.text[:500]
                }
            }
            
        except Exception as e:
            mcp_tests["get_project_overview"] = {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        
        self.test_results["individual_tests"]["mcp_simulation"] = mcp_tests
    
    def _test_integration_flows(self):
        """Test complete ingestion-to-query flows."""
        logger.info("Testing integration flows...")
        
        integration_tests = {}
        
        # Flow 1: Ingest then Query
        try:
            # Step 1: Ingest unique content
            unique_content = f"Integration test content - timestamp {datetime.now().isoformat()}"
            
            import io
            files = {
                'file': ('integration_test.txt', io.BytesIO(unique_content.encode('utf-8')), 'text/plain')
            }
            data = {'author': 'Integration Test'}
            
            ingest_response = requests.post(
                f"{self.nancy_api_base}/api/ingest",
                files=files,
                data=data,
                timeout=30
            )
            
            # Wait for indexing
            time.sleep(2)
            
            # Step 2: Query for the content
            query_data = {
                "query": "integration test content timestamp",
                "n_results": 10,
                "orchestrator": "intelligent"
            }
            
            query_response = requests.post(
                f"{self.nancy_api_base}/api/query",
                json=query_data,
                timeout=60
            )
            
            # Analyze if query found the ingested content
            query_result = query_response.json() if query_response.status_code == 200 else {}
            found_content = False
            
            if "response" in query_result and unique_content[:20] in str(query_result):
                found_content = True
            elif "sources" in query_result:
                for source in query_result.get("sources", []):
                    if "integration_test" in str(source).lower():
                        found_content = True
                        break
            
            integration_tests["ingest_to_query_flow"] = {
                "ingest_status": "success" if ingest_response.status_code == 200 else "failed",
                "ingest_response": ingest_response.json() if ingest_response.status_code == 200 else ingest_response.text[:200],
                "query_status": "success" if query_response.status_code == 200 else "failed", 
                "query_response": query_result,
                "content_found": found_content,
                "overall_flow": "success" if found_content else "failed"
            }
            
        except Exception as e:
            integration_tests["ingest_to_query_flow"] = {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        
        self.test_results["integration_tests"] = integration_tests
    
    def _investigate_event_loop_issues(self):
        """Investigate specific event loop problems."""
        logger.info("Investigating event loop issues...")
        
        event_loop_tests = {}
        
        # Test endpoints that might have event loop issues
        problematic_endpoints = [
            "/health",
            "/api/nancy/status", 
            "/api/nancy/configuration"
        ]
        
        for endpoint in problematic_endpoints:
            try:
                response = requests.get(f"{self.nancy_api_base}{endpoint}", timeout=10)
                
                event_loop_tests[endpoint] = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code == 200 else response.text[:300],
                    "event_loop_error": "event loop is already running" in response.text if response.status_code != 200 else False
                }
                
            except Exception as e:
                event_loop_tests[endpoint] = {
                    "status": "error",
                    "error": str(e),
                    "event_loop_error": "event loop is already running" in str(e)
                }
        
        self.test_results["individual_tests"]["event_loop"] = event_loop_tests
    
    def _analyze_results(self):
        """Analyze test results and generate recommendations."""
        logger.info("Analyzing results and generating recommendations...")
        
        issues = []
        recommendations = []
        
        # Analyze system health
        health = self.test_results.get("system_health", {})
        if health.get("connectivity", {}).get("status") != "success":
            issues.append("Nancy API connectivity failed")
            recommendations.append("Check that Nancy is running with 'docker-compose up -d'")
        
        # Check for event loop issues
        nancy_health = health.get("connectivity", {}).get("response", {})
        if isinstance(nancy_health, dict) and nancy_health.get("nancy_core", {}).get("error"):
            error_msg = nancy_health["nancy_core"]["error"]
            if "event loop is already running" in error_msg:
                issues.append("Event loop already running error in Nancy core")
                recommendations.append("Fix asyncio event loop usage in legacy_adapter.py lines 155-158 and 269-270")
        
        # Analyze MCP tool simulation
        mcp_tests = self.test_results.get("individual_tests", {}).get("mcp_simulation", {})
        for tool_name, result in mcp_tests.items():
            if result.get("status") != "success":
                issues.append(f"MCP tool simulation failed: {tool_name}")
                if "error" in result:
                    recommendations.append(f"Fix {tool_name}: {result['error']}")
        
        # Analyze integration flows
        integration = self.test_results.get("integration_tests", {})
        ingest_query = integration.get("ingest_to_query_flow", {})
        if not ingest_query.get("content_found", False):
            issues.append("Ingestion-to-query flow broken - ingested content not found in queries")
            recommendations.append("Investigate search indexing and query processing pipeline")
        
        # Check for empty responses
        query_result = mcp_tests.get("query_memory", {}).get("response", {})
        if isinstance(query_result, dict) and query_result.get("response") == "No response generated":
            issues.append("Query endpoint returning 'No response generated'")
            recommendations.append("Check LLM connectivity and query processing logic")
        
        self.test_results["identified_issues"] = issues
        self.test_results["recommendations"] = recommendations
    
    def save_results(self, filename: Optional[str] = None):
        """Save diagnostic results to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nancy_mcp_diagnostic_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"Diagnostic results saved to {filename}")
        return filename


def main():
    """Run the Nancy MCP diagnostic suite."""
    diagnostic = NancyMCPDiagnostic()
    
    print("Nancy MCP Diagnostic Suite")
    print("=" * 50)
    
    # Run complete diagnostic
    results = diagnostic.run_complete_diagnostic()
    
    # Save results
    filename = diagnostic.save_results()
    
    # Print summary
    print(f"\nDiagnostic Complete - Results saved to {filename}")
    print(f"\nIdentified Issues ({len(results['identified_issues'])}):")
    for issue in results["identified_issues"]:
        print(f"  ❌ {issue}")
    
    print(f"\nRecommendations ({len(results['recommendations'])}):")
    for rec in results["recommendations"]:
        print(f"  💡 {rec}")
    
    print(f"\nSystem Health Summary:")
    health = results.get("system_health", {})
    for test_name, test_result in health.items():
        status = test_result.get("status", "unknown")
        icon = "✅" if status == "success" else "❌" if status == "failed" else "⚠️"
        print(f"  {icon} {test_name}: {status}")
    
    return results


if __name__ == "__main__":
    main()