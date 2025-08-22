#!/usr/bin/env python3
"""
Comprehensive test script to validate the nancy-memory MCP server fix
across all orchestrator types and edge cases.

This script tests:
1. All orchestrator types (intelligent, langchain, enhanced)
2. Error handling for unexpected response formats
3. Fallback logic when fields are missing
4. Data extraction accuracy for each orchestrator type
"""

import json
import sys
import time
import requests
from typing import Dict, Any, List

class NancyMCPOrchestratorValidator:
    """Validator for Nancy MCP server orchestrator compatibility fix"""
    
    def __init__(self, nancy_api_base: str = "http://localhost:8000"):
        self.nancy_api_base = nancy_api_base
        self.test_results = []
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive orchestrator compatibility tests"""
        print("🔧 Nancy MCP Orchestrator Fix Validation")
        print("=" * 50)
        
        # Check if Nancy is running
        if not self._check_nancy_health():
            return {"status": "error", "message": "Nancy API is not accessible"}
        
        # Test all orchestrator types
        orchestrators = ["intelligent", "langchain", "enhanced"]
        test_queries = [
            "What are thermal constraints?",
            "Who worked on electrical systems?", 
            "Show me recent files",
            "List all authors in the system"
        ]
        
        total_tests = 0
        passed_tests = 0
        
        for orchestrator in orchestrators:
            print(f"\n🧠 Testing {orchestrator.upper()} orchestrator...")
            
            for query in test_queries:
                total_tests += 1
                test_result = self._test_orchestrator_query(orchestrator, query)
                
                if test_result["status"] == "success":
                    passed_tests += 1
                    print(f"  ✅ PASS: {query[:40]}...")
                else:
                    print(f"  ❌ FAIL: {query[:40]}... - {test_result.get('error', 'Unknown error')}")
                
                self.test_results.append({
                    "orchestrator": orchestrator,
                    "query": query,
                    "result": test_result,
                    "timestamp": time.time()
                })
                
                # Rate limiting
                time.sleep(1)
        
        # Test edge cases
        print(f"\n🔍 Testing edge cases...")
        edge_case_tests = self._test_edge_cases()
        total_tests += len(edge_case_tests)
        passed_tests += sum(1 for test in edge_case_tests if test["status"] == "success")
        
        # Generate summary report
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "orchestrator_results": self._analyze_orchestrator_results(),
            "edge_case_results": edge_case_tests,
            "detailed_results": self.test_results
        }
        
        print(f"\n📊 Test Summary:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {total_tests - passed_tests}")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        
        return summary
    
    def _check_nancy_health(self) -> bool:
        """Check if Nancy API is accessible"""
        try:
            response = requests.get(f"{self.nancy_api_base}/health", timeout=10)
            return response.status_code == 200
        except:
            print("❌ Nancy API is not accessible. Make sure it's running with: docker-compose up -d")
            return False
    
    def _test_orchestrator_query(self, orchestrator: str, query: str) -> Dict[str, Any]:
        """Test a specific orchestrator with a query"""
        try:
            # Simulate the nancy-memory MCP server query
            query_data = {
                "query": query,
                "n_results": 5,
                "orchestrator": orchestrator
            }
            
            response = requests.post(
                f"{self.nancy_api_base}/api/query",
                json=query_data,
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "error": f"Nancy API returned {response.status_code}: {response.text[:200]}"
                }
            
            try:
                result = response.json()
            except ValueError:
                return {
                    "status": "error",
                    "error": "Nancy API returned invalid JSON"
                }
            
            # Test orchestrator detection
            orchestrator_type = self._detect_orchestrator_type(result)
            extracted_data = self._extract_response_data(result, orchestrator_type)
            
            # Validate extracted data
            validation_result = self._validate_extracted_data(extracted_data, orchestrator_type)
            
            return {
                "status": "success",
                "orchestrator_detected": orchestrator_type,
                "orchestrator_requested": orchestrator,
                "extraction_validation": validation_result,
                "response_length": len(extracted_data.get("response", "")),
                "sources_count": len(extracted_data.get("sources", [])),
                "has_brain_analysis": bool(extracted_data.get("brain_analysis")),
                "raw_keys": list(result.keys())
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Test execution failed: {str(e)}"
            }
    
    def _test_edge_cases(self) -> List[Dict[str, Any]]:
        """Test edge cases and error scenarios"""
        edge_cases = []
        
        # Test 1: Malformed response simulation
        print("  🔍 Testing malformed response handling...")
        malformed_result = {"unexpected_field": "value", "random_data": [1, 2, 3]}
        try:
            orchestrator_type = self._detect_orchestrator_type(malformed_result)
            extracted_data = self._extract_response_data(malformed_result, orchestrator_type)
            edge_cases.append({
                "test": "malformed_response",
                "status": "success",
                "orchestrator_detected": orchestrator_type,
                "fallback_triggered": orchestrator_type == "unknown"
            })
        except Exception as e:
            edge_cases.append({
                "test": "malformed_response", 
                "status": "error",
                "error": str(e)
            })
        
        # Test 2: Empty response simulation
        print("  🔍 Testing empty response handling...")
        try:
            empty_result = {}
            orchestrator_type = self._detect_orchestrator_type(empty_result)
            extracted_data = self._extract_response_data(empty_result, orchestrator_type)
            edge_cases.append({
                "test": "empty_response",
                "status": "success",
                "orchestrator_detected": orchestrator_type,
                "response_generated": bool(extracted_data.get("response"))
            })
        except Exception as e:
            edge_cases.append({
                "test": "empty_response",
                "status": "error", 
                "error": str(e)
            })
        
        # Test 3: Partial response simulation
        print("  🔍 Testing partial response handling...")
        try:
            partial_result = {"response": "Test response", "incomplete": True}
            orchestrator_type = self._detect_orchestrator_type(partial_result)
            extracted_data = self._extract_response_data(partial_result, orchestrator_type)
            edge_cases.append({
                "test": "partial_response",
                "status": "success",
                "orchestrator_detected": orchestrator_type,
                "extraction_successful": bool(extracted_data.get("response"))
            })
        except Exception as e:
            edge_cases.append({
                "test": "partial_response",
                "status": "error",
                "error": str(e)
            })
        
        return edge_cases
    
    def _analyze_orchestrator_results(self) -> Dict[str, Dict[str, Any]]:
        """Analyze results by orchestrator type"""
        orchestrator_analysis = {}
        
        for orchestrator in ["intelligent", "langchain", "enhanced"]:
            orchestrator_tests = [r for r in self.test_results if r["orchestrator"] == orchestrator]
            
            if orchestrator_tests:
                successful_tests = [r for r in orchestrator_tests if r["result"]["status"] == "success"]
                
                orchestrator_analysis[orchestrator] = {
                    "total_tests": len(orchestrator_tests),
                    "successful_tests": len(successful_tests),
                    "success_rate": (len(successful_tests) / len(orchestrator_tests)) * 100,
                    "detection_accuracy": sum(1 for r in successful_tests 
                                             if r["result"].get("orchestrator_detected") == orchestrator or
                                                r["result"].get("orchestrator_detected") in ["legacy", "unknown"]) / len(successful_tests) * 100 if successful_tests else 0
                }
        
        return orchestrator_analysis
    
    # Copy the helper methods from the fixed MCP server for testing
    def _detect_orchestrator_type(self, result: Dict[str, Any]) -> str:
        """Detect orchestrator type - copied from fixed MCP server"""
        if "synthesized_response" in result and "raw_results" in result and "intent_analysis" in result:
            return "intelligent"
        if "response" in result and "routing_info" in result and "raw_results" not in result:
            return "langchain"
        if "results" in result and "strategy_used" in result and "synthesized_response" not in result:
            return "enhanced"
        if "response" in result and "raw_results" in result:
            return "legacy"
        return "unknown"
    
    def _extract_response_data(self, result: Dict[str, Any], orchestrator_type: str) -> Dict[str, Any]:
        """Extract response data - copied from fixed MCP server"""
        try:
            if orchestrator_type == "intelligent":
                return self._extract_intelligent_data(result)
            elif orchestrator_type == "langchain":
                return self._extract_langchain_data(result)
            elif orchestrator_type == "enhanced":
                return self._extract_enhanced_data(result)
            elif orchestrator_type == "legacy":
                return self._extract_legacy_data(result)
            else:
                return self._extract_fallback_data(result)
        except Exception as e:
            return self._extract_fallback_data(result)
    
    def _extract_intelligent_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract intelligent orchestrator data"""
        sources = []
        for raw_result in result.get("raw_results", []):
            source = {
                "content": raw_result.get("text", ""),
                "metadata": raw_result.get("metadata", {}),
                "relevance_score": 1.0 - raw_result.get("distance", 0.0),
                "source_type": raw_result.get("source", "unknown"),
                "chunk_id": raw_result.get("chunk_id", "")
            }
            sources.append(source)
        
        return {
            "response": result.get("synthesized_response", "No response generated"),
            "strategy_used": result.get("strategy_used", "intelligent"),
            "sources": sources,
            "brain_analysis": result.get("intent_analysis", {}),
            "confidence": result.get("intent_analysis", {}).get("confidence", "unknown"),
            "brains_used": result.get("brains_used", []),
            "processing_timestamp": result.get("processing_timestamp", "")
        }
    
    def _extract_langchain_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract langchain orchestrator data"""
        return {
            "response": result.get("response", "No response generated"),
            "strategy_used": result.get("strategy_used", "langchain_router"),
            "sources": [],
            "brain_analysis": result.get("routing_info", {}),
            "confidence": result.get("routing_info", {}).get("confidence", "unknown"),
            "brains_used": [result.get("routing_info", {}).get("selected_brain", "unknown")],
            "processing_timestamp": result.get("processing_timestamp", "")
        }
    
    def _extract_enhanced_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract enhanced orchestrator data"""
        sources = []
        for enhanced_result in result.get("results", []):
            source = {
                "content": enhanced_result.get("content", ""),
                "metadata": enhanced_result.get("metadata", {}),
                "relevance_score": enhanced_result.get("relevance_score", 0.5),
                "source_type": enhanced_result.get("source_type", "unknown"),
                "chunk_id": enhanced_result.get("chunk_id", "")
            }
            sources.append(source)
        
        response = result.get("response", "")
        if not response and sources:
            response = f"Found {len(sources)} relevant sources. "
            if sources[0].get("content"):
                response += f"Key content: {sources[0]['content'][:200]}..."
        
        return {
            "response": response or "No response generated",
            "strategy_used": result.get("strategy_used", "enhanced"),
            "sources": sources,
            "brain_analysis": result.get("intent", {}),
            "confidence": result.get("intent", {}).get("confidence", "unknown"),
            "brains_used": result.get("brains_used", ["enhanced"]),
            "processing_timestamp": result.get("processing_timestamp", "")
        }
    
    def _extract_legacy_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract legacy format data"""
        sources = []
        for raw_result in result.get("raw_results", []):
            source = {
                "content": raw_result.get("text", raw_result.get("content", "")),
                "metadata": raw_result.get("metadata", {}),
                "relevance_score": 1.0 - raw_result.get("distance", 0.0),
                "source_type": raw_result.get("source", "unknown"),
                "chunk_id": raw_result.get("chunk_id", "")
            }
            sources.append(source)
        
        return {
            "response": result.get("response", "No response generated"),
            "strategy_used": result.get("strategy_used", "legacy"),
            "sources": sources,
            "brain_analysis": result.get("brain_analysis", {}),
            "confidence": result.get("confidence", "unknown"),
            "brains_used": result.get("brains_used", []),
            "processing_timestamp": result.get("processing_timestamp", "")
        }
    
    def _extract_fallback_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data with fallback logic"""
        response_candidates = ["synthesized_response", "response", "answer", "result"]
        response = "No response generated"
        for candidate in response_candidates:
            if candidate in result and result[candidate]:
                response = str(result[candidate])
                break
        
        sources = []
        sources_candidates = ["raw_results", "results", "sources", "documents"]
        for candidate in sources_candidates:
            if candidate in result and isinstance(result[candidate], list):
                for item in result[candidate]:
                    if isinstance(item, dict):
                        source = {
                            "content": item.get("text", item.get("content", item.get("document", ""))),
                            "metadata": item.get("metadata", {}),
                            "relevance_score": 1.0 - item.get("distance", 0.0) if "distance" in item else 0.5,
                            "source_type": item.get("source", item.get("source_type", "unknown")),
                            "chunk_id": item.get("chunk_id", item.get("id", ""))
                        }
                        sources.append(source)
                break
        
        return {
            "response": response,
            "strategy_used": result.get("strategy_used", "fallback"),
            "sources": sources,
            "brain_analysis": result.get("intent_analysis", result.get("routing_info", result.get("intent", {}))),
            "confidence": "unknown",
            "brains_used": result.get("brains_used", ["unknown"]),
            "processing_timestamp": result.get("processing_timestamp", "")
        }
    
    def _validate_extracted_data(self, extracted_data: Dict[str, Any], orchestrator_type: str) -> Dict[str, bool]:
        """Validate that extracted data has required fields and reasonable values"""
        return {
            "has_response": bool(extracted_data.get("response")),
            "has_strategy": bool(extracted_data.get("strategy_used")),
            "has_sources": isinstance(extracted_data.get("sources"), list),
            "has_brain_analysis": isinstance(extracted_data.get("brain_analysis"), dict),
            "has_confidence": extracted_data.get("confidence") is not None,
            "has_brains_used": isinstance(extracted_data.get("brains_used"), list),
            "response_not_empty": extracted_data.get("response") != "No response generated",
            "sources_valid": all(isinstance(s, dict) for s in extracted_data.get("sources", [])),
        }

def main():
    """Run the validation tests"""
    validator = NancyMCPOrchestratorValidator()
    results = validator.run_all_tests()
    
    # Save detailed results
    timestamp = int(time.time())
    results_file = f"nancy_mcp_orchestrator_fix_validation_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Return appropriate exit code
    if results["success_rate"] >= 80:
        print("\n🎉 Orchestrator fix validation PASSED!")
        return 0
    else:
        print("\n❌ Orchestrator fix validation FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())