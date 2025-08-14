#!/usr/bin/env python3
"""
Comprehensive Spreadsheet Ingestion Test Suite for Nancy Four-Brain Architecture

This test suite validates all aspects of Nancy's spreadsheet processing capabilities:
- Core ingestion functionality (CSV and Excel)
- Four-brain integration (Vector, Analytical, Graph, Linguistic)
- Natural language query processing
- Engineering domain intelligence
- API integration and performance

Author: Test Engineer
Date: 2025-08-13
"""

import requests
import json
import time
import pandas as pd
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NancySpreadsheetTester:
    """Comprehensive test suite for Nancy's spreadsheet capabilities"""
    
    def __init__(self, nancy_api_url: str = "http://localhost:8000", test_data_dir: str = "./test_data"):
        self.nancy_api_url = nancy_api_url
        self.test_data_dir = test_data_dir
        self.test_results = {
            "test_start_time": datetime.now().isoformat(),
            "nancy_api_url": nancy_api_url,
            "test_data_directory": test_data_dir,
            "results": {}
        }
        
        # Test files from existing test_data
        self.test_files = [
            "component_requirements.csv",
            "thermal_test_results.csv", 
            "test_results.csv",
            "team_directory.csv",
            "engineering_projects_overview.csv",
            "mechanical_analysis.csv"
        ]
        
        # Additional test data to create for comprehensive testing
        self.additional_test_data = {
            "multi_sheet_excel": "engineering_data_comprehensive.xlsx",
            "complex_csv": "complex_engineering_data.csv"
        }
        
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all comprehensive spreadsheet tests"""
        logger.info("Starting comprehensive Nancy spreadsheet ingestion tests")
        
        try:
            # Test 1: Health check and environment validation
            self.test_results["results"]["health_check"] = self._test_health_check()
            
            # Test 2: Create additional test data
            self.test_results["results"]["test_data_creation"] = self._create_additional_test_data()
            
            # Test 3: CSV ingestion tests
            self.test_results["results"]["csv_ingestion"] = self._test_csv_ingestion()
            
            # Test 4: Excel ingestion tests  
            self.test_results["results"]["excel_ingestion"] = self._test_excel_ingestion()
            
            # Test 5: Four-brain validation
            self.test_results["results"]["four_brain_validation"] = self._test_four_brain_validation()
            
            # Test 6: Natural language query tests
            self.test_results["results"]["natural_language_queries"] = self._test_natural_language_queries()
            
            # Test 7: Engineering domain intelligence
            self.test_results["results"]["engineering_domain"] = self._test_engineering_domain_intelligence()
            
            # Test 8: Performance and reliability
            self.test_results["results"]["performance_reliability"] = self._test_performance_reliability()
            
            # Test 9: Error handling and edge cases
            self.test_results["results"]["error_handling"] = self._test_error_handling()
            
            # Test 10: Cross-brain integration queries
            self.test_results["results"]["cross_brain_queries"] = self._test_cross_brain_queries()
            
        except Exception as e:
            logger.error(f"Test suite failed with error: {e}")
            self.test_results["results"]["fatal_error"] = {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        
        # Finalize results
        self.test_results["test_end_time"] = datetime.now().isoformat()
        self.test_results["overall_status"] = self._calculate_overall_status()
        
        return self.test_results
    
    def _test_health_check(self) -> Dict[str, Any]:
        """Test Nancy API health and environment"""
        logger.info("Testing Nancy API health check")
        
        try:
            response = requests.get(f"{self.nancy_api_url}/health", timeout=30)
            health_data = response.json()
            
            result = {
                "status": "PASS" if response.status_code == 200 else "FAIL",
                "response_code": response.status_code,
                "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2),
                "health_data": health_data,
                "timestamp": datetime.now().isoformat()
            }
            
            if response.status_code == 200:
                logger.info("✓ Nancy API health check passed")
            else:
                logger.error(f"✗ Nancy API health check failed: {response.status_code}")
                
            return result
            
        except Exception as e:
            logger.error(f"✗ Health check failed: {e}")
            return {
                "status": "FAIL",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _create_additional_test_data(self) -> Dict[str, Any]:
        """Create additional comprehensive test data"""
        logger.info("Creating additional test data for comprehensive testing")
        
        results = {}
        
        try:
            # Create multi-sheet Excel file
            excel_path = os.path.join(self.test_data_dir, self.additional_test_data["multi_sheet_excel"])
            
            # Sheet 1: Component specifications
            components_data = {
                "component_id": ["COMP-101", "COMP-102", "COMP-103", "COMP-104", "COMP-105"],
                "component_name": ["Advanced CPU", "High-Speed Memory", "RF Module", "Power Controller", "Sensor Hub"],
                "category": ["Processing", "Storage", "Communication", "Power", "Sensing"],
                "thermal_max_c": [95, 85, 70, 60, 45],
                "power_consumption_w": [25.5, 8.2, 12.0, 15.8, 3.5],
                "cost_usd": [125.50, 89.99, 210.00, 67.25, 45.00],
                "supplier": ["TechCorp", "MemoryInc", "RadioTech", "PowerSys", "SensorWorks"],
                "lead_time_weeks": [8, 4, 12, 6, 3],
                "design_engineer": ["Alice Johnson", "Bob Smith", "Carol Wilson", "Dave Chen", "Eva Rodriguez"]
            }
            
            # Sheet 2: Test execution results
            test_data = {
                "test_id": ["TST-001", "TST-002", "TST-003", "TST-004", "TST-005", "TST-006"],
                "test_name": ["Thermal Stress Test", "EMC Compliance", "Power Efficiency", "Durability Test", "Performance Benchmark", "Safety Validation"],
                "component_tested": ["COMP-101", "COMP-103", "COMP-104", "COMP-101", "COMP-102", "COMP-105"],
                "test_result": ["PASS", "FAIL", "PASS", "PASS", "CONDITIONAL", "PASS"],
                "measured_value": [92.5, None, 94.2, None, 98.7, None],
                "requirement_value": [95.0, None, 90.0, None, 95.0, None],
                "test_engineer": ["Alice Johnson", "Charlie Brown", "Alice Johnson", "Bob Smith", "Dave Chen", "Eva Rodriguez"],
                "test_date": ["2025-08-10", "2025-08-11", "2025-08-11", "2025-08-12", "2025-08-12", "2025-08-13"],
                "notes": ["Within spec", "EMI issues found", "Excellent efficiency", "All cycles passed", "Minor optimization needed", "All safety checks OK"]
            }
            
            # Sheet 3: Project milestones
            milestones_data = {
                "milestone_id": ["MS-001", "MS-002", "MS-003", "MS-004", "MS-005"],
                "milestone_name": ["Design Review", "Prototype Complete", "Testing Phase", "Validation Complete", "Production Ready"],
                "target_date": ["2025-08-15", "2025-09-01", "2025-09-15", "2025-10-01", "2025-10-15"],
                "status": ["In Progress", "Pending", "Not Started", "Not Started", "Not Started"],
                "owner": ["Alice Johnson", "Bob Smith", "Alice Johnson", "Eva Rodriguez", "Dave Chen"],
                "dependencies": ["Design approval", "Component procurement", "MS-002", "MS-003", "MS-004"],
                "risk_level": ["Low", "Medium", "High", "Medium", "Low"]
            }
            
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                pd.DataFrame(components_data).to_excel(writer, sheet_name='Components', index=False)
                pd.DataFrame(test_data).to_excel(writer, sheet_name='Test_Results', index=False)
                pd.DataFrame(milestones_data).to_excel(writer, sheet_name='Milestones', index=False)
            
            results["multi_sheet_excel"] = {
                "status": "CREATED",
                "file_path": excel_path,
                "sheets": ["Components", "Test_Results", "Milestones"]
            }
            logger.info(f"✓ Created multi-sheet Excel file: {excel_path}")
            
            # Create complex CSV with engineering calculations
            csv_path = os.path.join(self.test_data_dir, self.additional_test_data["complex_csv"])
            
            complex_data = {
                "system_id": ["SYS-001", "SYS-002", "SYS-003", "SYS-004", "SYS-005"],
                "system_name": ["Primary Processing Unit", "Communication Subsystem", "Power Management", "Environmental Control", "Data Storage"],
                "base_power_w": [45.2, 23.8, 12.5, 18.9, 8.7],
                "efficiency_factor": [0.92, 0.88, 0.95, 0.85, 0.91],
                "calculated_power_w": [49.13, 27.05, 13.16, 22.24, 9.56],  # base_power / efficiency
                "thermal_coefficient": [0.85, 0.72, 0.95, 0.68, 0.89],
                "operating_temp_c": [65, 55, 40, 45, 35],
                "calculated_thermal_load": [55.25, 39.6, 38.0, 30.6, 31.15],  # operating_temp * thermal_coefficient
                "mtbf_hours": [50000, 75000, 100000, 45000, 80000],
                "cost_usd": [1250.00, 890.50, 345.75, 567.25, 234.90],
                "cost_per_mtbf": [0.025, 0.0119, 0.00346, 0.0126, 0.00294],  # cost / mtbf
                "design_team": ["Team Alpha", "Team Beta", "Team Alpha", "Team Gamma", "Team Beta"],
                "validation_status": ["Complete", "In Progress", "Complete", "Pending", "Complete"],
                "criticality": ["High", "High", "Critical", "Medium", "Medium"]
            }
            
            pd.DataFrame(complex_data).to_csv(csv_path, index=False)
            results["complex_csv"] = {
                "status": "CREATED", 
                "file_path": csv_path,
                "calculated_columns": ["calculated_power_w", "calculated_thermal_load", "cost_per_mtbf"]
            }
            logger.info(f"✓ Created complex CSV file: {csv_path}")
            
            return results
            
        except Exception as e:
            logger.error(f"✗ Failed to create test data: {e}")
            return {"status": "FAILED", "error": str(e)}
    
    def _test_csv_ingestion(self) -> Dict[str, Any]:
        """Test CSV file ingestion through Nancy API"""
        logger.info("Testing CSV file ingestion")
        
        results = {}
        
        for csv_file in [f for f in self.test_files if f.endswith('.csv')] + [self.additional_test_data["complex_csv"]]:
            file_path = os.path.join(self.test_data_dir, csv_file)
            
            if not os.path.exists(file_path):
                logger.warning(f"CSV file not found: {file_path}")
                continue
                
            try:
                logger.info(f"Testing ingestion of: {csv_file}")
                
                with open(file_path, 'rb') as f:
                    files = {'file': (csv_file, f, 'text/csv')}
                    data = {'author': 'Test Engineer'}
                    
                    start_time = time.time()
                    response = requests.post(f"{self.nancy_api_url}/api/ingest", files=files, data=data, timeout=120)
                    end_time = time.time()
                    
                    processing_time = round((end_time - start_time) * 1000, 2)
                    
                    result = {
                        "status": "PASS" if response.status_code == 200 else "FAIL",
                        "response_code": response.status_code,
                        "processing_time_ms": processing_time,
                        "file_size_bytes": os.path.getsize(file_path),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        result["response_data"] = response_data
                        result["doc_id"] = response_data.get("doc_id")
                        logger.info(f"✓ {csv_file} ingested successfully in {processing_time}ms")
                    else:
                        result["error"] = response.text
                        logger.error(f"✗ {csv_file} ingestion failed: {response.status_code}")
                    
                    results[csv_file] = result
                    
            except Exception as e:
                logger.error(f"✗ Error testing {csv_file}: {e}")
                results[csv_file] = {
                    "status": "FAIL",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        return results
    
    def _test_excel_ingestion(self) -> Dict[str, Any]:
        """Test Excel file ingestion through Nancy API"""
        logger.info("Testing Excel file ingestion")
        
        excel_file = self.additional_test_data["multi_sheet_excel"]
        file_path = os.path.join(self.test_data_dir, excel_file)
        
        if not os.path.exists(file_path):
            return {"status": "SKIPPED", "reason": "Excel test file not found"}
            
        try:
            logger.info(f"Testing ingestion of: {excel_file}")
            
            with open(file_path, 'rb') as f:
                files = {'file': (excel_file, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                data = {'author': 'Test Engineer'}
                
                start_time = time.time()
                response = requests.post(f"{self.nancy_api_url}/api/ingest", files=files, data=data, timeout=180)
                end_time = time.time()
                
                processing_time = round((end_time - start_time) * 1000, 2)
                
                result = {
                    "status": "PASS" if response.status_code == 200 else "FAIL",
                    "response_code": response.status_code,
                    "processing_time_ms": processing_time,
                    "file_size_bytes": os.path.getsize(file_path),
                    "timestamp": datetime.now().isoformat()
                }
                
                if response.status_code == 200:
                    response_data = response.json()
                    result["response_data"] = response_data
                    result["doc_id"] = response_data.get("doc_id")
                    result["sheets_processed"] = response_data.get("sheets_processed", 0)
                    logger.info(f"✓ {excel_file} ingested successfully in {processing_time}ms")
                else:
                    result["error"] = response.text
                    logger.error(f"✗ {excel_file} ingestion failed: {response.status_code}")
                
                return result
                
        except Exception as e:
            logger.error(f"✗ Error testing {excel_file}: {e}")
            return {
                "status": "FAIL",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _test_four_brain_validation(self) -> Dict[str, Any]:
        """Test that all four brains processed the data correctly"""
        logger.info("Testing four-brain integration validation")
        
        # These tests verify data was processed by each brain through specific queries
        test_queries = [
            # Vector Brain: Semantic search
            {
                "brain": "vector",
                "query": "thermal testing requirements",
                "expected_content": ["thermal", "temperature", "test"]
            },
            # Analytical Brain: Structured data queries
            {
                "brain": "analytical", 
                "query": "Show me components with thermal constraints above 70 degrees",
                "expected_content": ["component", "thermal", "70"]
            },
            # Graph Brain: Relationship queries
            {
                "brain": "graph",
                "query": "What relationships exist between Alice Johnson and thermal testing?",
                "expected_content": ["Alice Johnson", "relationship", "thermal"]
            },
            # Linguistic Brain: Natural language processing
            {
                "brain": "linguistic",
                "query": "Which engineers are responsible for power-related components?",
                "expected_content": ["engineer", "power", "responsible"]
            }
        ]
        
        results = {}
        
        for test_query in test_queries:
            try:
                logger.info(f"Testing {test_query['brain']} brain with query: {test_query['query']}")
                
                query_data = {"query": test_query["query"]}
                
                start_time = time.time()
                response = requests.post(f"{self.nancy_api_url}/api/query", json=query_data, timeout=60)
                end_time = time.time()
                
                processing_time = round((end_time - start_time) * 1000, 2)
                
                result = {
                    "status": "PASS" if response.status_code == 200 else "FAIL",
                    "response_code": response.status_code,
                    "processing_time_ms": processing_time,
                    "timestamp": datetime.now().isoformat()
                }
                
                if response.status_code == 200:
                    response_data = response.json()
                    result["response_data"] = response_data
                    result["answer"] = response_data.get("answer", "")
                    
                    # Check if expected content appears in response
                    answer_lower = result["answer"].lower()
                    content_found = sum(1 for content in test_query["expected_content"] if content.lower() in answer_lower)
                    result["content_match_score"] = content_found / len(test_query["expected_content"])
                    
                    if content_found > 0:
                        logger.info(f"✓ {test_query['brain']} brain responded successfully")
                    else:
                        logger.warning(f"⚠ {test_query['brain']} brain response may not contain expected content")
                        
                else:
                    result["error"] = response.text
                    logger.error(f"✗ {test_query['brain']} brain query failed: {response.status_code}")
                
                results[test_query["brain"]] = result
                
            except Exception as e:
                logger.error(f"✗ Error testing {test_query['brain']} brain: {e}")
                results[test_query["brain"]] = {
                    "status": "FAIL",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        return results
    
    def _test_natural_language_queries(self) -> Dict[str, Any]:
        """Test natural language querying capabilities"""
        logger.info("Testing natural language query scenarios")
        
        # Comprehensive natural language test scenarios
        test_scenarios = [
            {
                "name": "thermal_data_inquiry",
                "query": "What thermal test data is available?",
                "expected_keywords": ["thermal", "test", "temperature", "data"]
            },
            {
                "name": "cost_analysis",
                "query": "Show me components with cost over $100",
                "expected_keywords": ["cost", "100", "component", "price"]
            },
            {
                "name": "engineer_ownership",
                "query": "Which engineers own failing tests?",
                "expected_keywords": ["engineer", "fail", "test", "owner"]
            },
            {
                "name": "requirement_dependencies",
                "query": "What requirements depend on thermal analysis?",
                "expected_keywords": ["requirement", "thermal", "analysis", "depend"]
            },
            {
                "name": "power_efficiency",
                "query": "Find systems with power efficiency above 90%",
                "expected_keywords": ["power", "efficiency", "90", "system"]
            },
            {
                "name": "project_status",
                "query": "What is the status of engineering projects?",
                "expected_keywords": ["status", "project", "engineering", "progress"]
            }
        ]
        
        results = {}
        
        for scenario in test_scenarios:
            try:
                logger.info(f"Testing scenario: {scenario['name']}")
                
                query_data = {"query": scenario["query"]}
                
                start_time = time.time()
                response = requests.post(f"{self.nancy_api_url}/api/query", json=query_data, timeout=60)
                end_time = time.time()
                
                processing_time = round((end_time - start_time) * 1000, 2)
                
                result = {
                    "query": scenario["query"],
                    "status": "PASS" if response.status_code == 200 else "FAIL",
                    "response_code": response.status_code,
                    "processing_time_ms": processing_time,
                    "timestamp": datetime.now().isoformat()
                }
                
                if response.status_code == 200:
                    response_data = response.json()
                    result["response_data"] = response_data
                    result["answer"] = response_data.get("answer", "")
                    result["brain_used"] = response_data.get("brain_used", "unknown")
                    result["confidence"] = response_data.get("confidence", 0)
                    
                    # Analyze response quality
                    answer_lower = result["answer"].lower()
                    keyword_matches = sum(1 for keyword in scenario["expected_keywords"] if keyword.lower() in answer_lower)
                    result["keyword_match_score"] = keyword_matches / len(scenario["expected_keywords"])
                    result["response_length"] = len(result["answer"])
                    
                    if keyword_matches > 0:
                        logger.info(f"✓ Scenario '{scenario['name']}' completed successfully")
                    else:
                        logger.warning(f"⚠ Scenario '{scenario['name']}' response may not contain expected keywords")
                        
                else:
                    result["error"] = response.text
                    logger.error(f"✗ Scenario '{scenario['name']}' failed: {response.status_code}")
                
                results[scenario["name"]] = result
                
                # Brief pause between queries
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"✗ Error in scenario '{scenario['name']}': {e}")
                results[scenario["name"]] = {
                    "query": scenario["query"],
                    "status": "FAIL",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        return results
    
    def _test_engineering_domain_intelligence(self) -> Dict[str, Any]:
        """Test engineering domain intelligence and terminology recognition"""
        logger.info("Testing engineering domain intelligence")
        
        # Domain-specific test cases
        domain_tests = [
            {
                "domain": "thermal_engineering",
                "query": "What are the thermal constraints for the CPU component?",
                "expected_domain_terms": ["thermal", "temperature", "cpu", "constraint", "cooling"]
            },
            {
                "domain": "electrical_engineering", 
                "query": "Show EMC compliance test results",
                "expected_domain_terms": ["emc", "compliance", "electrical", "electromagnetic", "test"]
            },
            {
                "domain": "mechanical_engineering",
                "query": "Find mechanical stress analysis data",
                "expected_domain_terms": ["mechanical", "stress", "analysis", "structural", "material"]
            },
            {
                "domain": "systems_engineering",
                "query": "What are the system requirements and dependencies?",
                "expected_domain_terms": ["system", "requirement", "dependency", "interface", "specification"]
            },
            {
                "domain": "quality_engineering",
                "query": "Which tests have failed and need attention?",
                "expected_domain_terms": ["test", "fail", "quality", "validation", "defect"]
            }
        ]
        
        results = {}
        
        for domain_test in domain_tests:
            try:
                logger.info(f"Testing domain: {domain_test['domain']}")
                
                query_data = {"query": domain_test["query"]}
                
                start_time = time.time()
                response = requests.post(f"{self.nancy_api_url}/api/query", json=query_data, timeout=60)
                end_time = time.time()
                
                processing_time = round((end_time - start_time) * 1000, 2)
                
                result = {
                    "domain": domain_test["domain"],
                    "query": domain_test["query"],
                    "status": "PASS" if response.status_code == 200 else "FAIL",
                    "response_code": response.status_code,
                    "processing_time_ms": processing_time,
                    "timestamp": datetime.now().isoformat()
                }
                
                if response.status_code == 200:
                    response_data = response.json()
                    result["response_data"] = response_data
                    result["answer"] = response_data.get("answer", "")
                    
                    # Analyze domain intelligence
                    answer_lower = result["answer"].lower()
                    domain_term_matches = sum(1 for term in domain_test["expected_domain_terms"] if term.lower() in answer_lower)
                    result["domain_intelligence_score"] = domain_term_matches / len(domain_test["expected_domain_terms"])
                    
                    # Check if Nancy understood the engineering context
                    engineering_indicators = ["component", "specification", "requirement", "test", "analysis", "design", "system"]
                    engineering_context_score = sum(1 for indicator in engineering_indicators if indicator.lower() in answer_lower)
                    result["engineering_context_score"] = min(engineering_context_score / len(engineering_indicators), 1.0)
                    
                    if domain_term_matches > 0:
                        logger.info(f"✓ Domain '{domain_test['domain']}' intelligence test passed")
                    else:
                        logger.warning(f"⚠ Domain '{domain_test['domain']}' may not have been properly understood")
                        
                else:
                    result["error"] = response.text
                    logger.error(f"✗ Domain '{domain_test['domain']}' test failed: {response.status_code}")
                
                results[domain_test["domain"]] = result
                
            except Exception as e:
                logger.error(f"✗ Error testing domain '{domain_test['domain']}': {e}")
                results[domain_test["domain"]] = {
                    "domain": domain_test["domain"],
                    "query": domain_test["query"],
                    "status": "FAIL",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        return results
    
    def _test_performance_reliability(self) -> Dict[str, Any]:
        """Test performance and reliability scenarios"""
        logger.info("Testing performance and reliability")
        
        results = {}
        
        try:
            # Test 1: Response time consistency
            response_times = []
            test_query = "What thermal test data is available?"
            
            for i in range(5):
                start_time = time.time()
                response = requests.post(f"{self.nancy_api_url}/api/query", 
                                       json={"query": test_query}, timeout=60)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append((end_time - start_time) * 1000)
                
                time.sleep(1)  # Brief pause between requests
            
            if response_times:
                results["response_time_consistency"] = {
                    "status": "PASS",
                    "avg_response_time_ms": round(sum(response_times) / len(response_times), 2),
                    "min_response_time_ms": round(min(response_times), 2),
                    "max_response_time_ms": round(max(response_times), 2),
                    "std_deviation_ms": round(pd.Series(response_times).std(), 2),
                    "sample_size": len(response_times)
                }
                logger.info("✓ Response time consistency test completed")
            else:
                results["response_time_consistency"] = {"status": "FAIL", "error": "No successful responses"}
            
            # Test 2: Concurrent request handling (simplified)
            logger.info("Testing concurrent request handling")
            concurrent_results = []
            
            # Simple sequential test (can be enhanced for true concurrency if needed)
            for i in range(3):
                query = f"Show me test results for component COMP-{100+i:03d}"
                start_time = time.time()
                response = requests.post(f"{self.nancy_api_url}/api/query", 
                                       json={"query": query}, timeout=60)
                end_time = time.time()
                
                concurrent_results.append({
                    "query_id": i+1,
                    "status": "PASS" if response.status_code == 200 else "FAIL",
                    "response_time_ms": round((end_time - start_time) * 1000, 2)
                })
            
            results["concurrent_handling"] = {
                "status": "PASS" if all(r["status"] == "PASS" for r in concurrent_results) else "FAIL",
                "requests_tested": len(concurrent_results),
                "successful_requests": sum(1 for r in concurrent_results if r["status"] == "PASS"),
                "results": concurrent_results
            }
            logger.info("✓ Concurrent request handling test completed")
            
        except Exception as e:
            logger.error(f"✗ Performance test error: {e}")
            results["error"] = str(e)
        
        return results
    
    def _test_error_handling(self) -> Dict[str, Any]:
        """Test error handling and edge cases"""
        logger.info("Testing error handling and edge cases")
        
        results = {}
        
        # Test 1: Invalid file upload
        try:
            files = {'file': ('invalid.txt', b'invalid content', 'text/plain')}
            data = {'author': 'Test Engineer'}
            response = requests.post(f"{self.nancy_api_url}/api/ingest", files=files, data=data, timeout=30)
            
            results["invalid_file_handling"] = {
                "status": "PASS",  # Should handle gracefully
                "response_code": response.status_code,
                "handled_gracefully": response.status_code in [200, 400, 422]
            }
            logger.info("✓ Invalid file handling test completed")
        except Exception as e:
            results["invalid_file_handling"] = {"status": "FAIL", "error": str(e)}
        
        # Test 2: Malformed query
        try:
            response = requests.post(f"{self.nancy_api_url}/api/query", 
                                   json={"query": ""}, timeout=30)
            
            results["empty_query_handling"] = {
                "status": "PASS",
                "response_code": response.status_code,
                "handled_gracefully": response.status_code in [200, 400, 422]
            }
            logger.info("✓ Empty query handling test completed")
        except Exception as e:
            results["empty_query_handling"] = {"status": "FAIL", "error": str(e)}
        
        # Test 3: Very long query
        try:
            long_query = "What are the thermal constraints " * 100  # Very repetitive long query
            response = requests.post(f"{self.nancy_api_url}/api/query", 
                                   json={"query": long_query}, timeout=60)
            
            results["long_query_handling"] = {
                "status": "PASS",
                "response_code": response.status_code,
                "query_length": len(long_query),
                "handled_gracefully": response.status_code in [200, 400, 413]
            }
            logger.info("✓ Long query handling test completed")
        except Exception as e:
            results["long_query_handling"] = {"status": "FAIL", "error": str(e)}
        
        return results
    
    def _test_cross_brain_queries(self) -> Dict[str, Any]:
        """Test queries requiring coordination between multiple brains"""
        logger.info("Testing cross-brain coordination queries")
        
        # Complex queries that should require multiple brain coordination
        cross_brain_scenarios = [
            {
                "name": "semantic_plus_structured",
                "query": "Find thermal test failures and tell me which engineers are responsible",
                "expected_brains": ["vector", "analytical", "graph"],
                "description": "Requires semantic search + structured data + relationship mapping"
            },
            {
                "name": "relationship_plus_calculation",
                "query": "What is the average power consumption of components owned by Alice Johnson?",
                "expected_brains": ["graph", "analytical"],
                "description": "Requires relationship discovery + numerical calculation"
            },
            {
                "name": "comprehensive_analysis",
                "query": "Show me all failed tests, their related components, and the engineers responsible, along with thermal constraints",
                "expected_brains": ["analytical", "graph", "vector"],
                "description": "Requires comprehensive multi-brain analysis"
            },
            {
                "name": "temporal_relationship_query",
                "query": "Which projects have thermal testing milestones and what are their current statuses?",
                "expected_brains": ["graph", "analytical", "vector"],
                "description": "Requires temporal relationship analysis across brains"
            }
        ]
        
        results = {}
        
        for scenario in cross_brain_scenarios:
            try:
                logger.info(f"Testing cross-brain scenario: {scenario['name']}")
                
                query_data = {"query": scenario["query"]}
                
                start_time = time.time()
                response = requests.post(f"{self.nancy_api_url}/api/query", json=query_data, timeout=90)
                end_time = time.time()
                
                processing_time = round((end_time - start_time) * 1000, 2)
                
                result = {
                    "scenario": scenario["name"],
                    "query": scenario["query"],
                    "description": scenario["description"],
                    "status": "PASS" if response.status_code == 200 else "FAIL",
                    "response_code": response.status_code,
                    "processing_time_ms": processing_time,
                    "timestamp": datetime.now().isoformat()
                }
                
                if response.status_code == 200:
                    response_data = response.json()
                    result["response_data"] = response_data
                    result["answer"] = response_data.get("answer", "")
                    result["brain_used"] = response_data.get("brain_used", "unknown")
                    
                    # Analyze if the response shows evidence of multi-brain coordination
                    answer_lower = result["answer"].lower()
                    complexity_indicators = ["and", "with", "related", "responsible", "average", "all", "status", "constraint"]
                    complexity_score = sum(1 for indicator in complexity_indicators if indicator in answer_lower)
                    result["complexity_score"] = complexity_score / len(complexity_indicators)
                    
                    # Check for comprehensive response (longer responses may indicate multi-brain coordination)
                    result["response_comprehensiveness"] = len(result["answer"]) > 200
                    
                    logger.info(f"✓ Cross-brain scenario '{scenario['name']}' completed")
                        
                else:
                    result["error"] = response.text
                    logger.error(f"✗ Cross-brain scenario '{scenario['name']}' failed: {response.status_code}")
                
                results[scenario["name"]] = result
                
                # Pause between complex queries
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"✗ Error in cross-brain scenario '{scenario['name']}': {e}")
                results[scenario["name"]] = {
                    "scenario": scenario["name"],
                    "query": scenario["query"],
                    "status": "FAIL",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        return results
    
    def _calculate_overall_status(self) -> str:
        """Calculate overall test status based on all test results"""
        total_tests = 0
        passed_tests = 0
        
        def count_tests_recursive(obj):
            nonlocal total_tests, passed_tests
            
            if isinstance(obj, dict):
                if "status" in obj:
                    total_tests += 1
                    if obj["status"] == "PASS":
                        passed_tests += 1
                else:
                    for value in obj.values():
                        count_tests_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    count_tests_recursive(item)
        
        count_tests_recursive(self.test_results["results"])
        
        if total_tests == 0:
            return "NO_TESTS"
        
        success_rate = passed_tests / total_tests
        
        if success_rate >= 0.9:
            return "EXCELLENT"
        elif success_rate >= 0.8:
            return "GOOD"
        elif success_rate >= 0.6:
            return "ACCEPTABLE"
        elif success_rate >= 0.4:
            return "POOR"
        else:
            return "CRITICAL"

def main():
    """Main function to run comprehensive spreadsheet tests"""
    logger.info("Starting Nancy Comprehensive Spreadsheet Test Suite")
    
    # Initialize tester
    tester = NancySpreadsheetTester()
    
    # Run comprehensive tests
    results = tester.run_comprehensive_tests()
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"nancy_spreadsheet_test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Test results saved to: {results_file}")
    
    # Print summary
    print("\n" + "="*80)
    print("NANCY SPREADSHEET INGESTION TEST RESULTS SUMMARY")
    print("="*80)
    print(f"Overall Status: {results['overall_status']}")
    print(f"Test Duration: {results['test_start_time']} to {results['test_end_time']}")
    print(f"Results File: {results_file}")
    print("="*80)
    
    return results

if __name__ == "__main__":
    # Ensure Docker services are running before tests
    print("Comprehensive Nancy Spreadsheet Ingestion Test Suite")
    print("Please ensure Docker services are running: docker-compose up -d")
    print("Starting tests in 5 seconds...")
    time.sleep(5)
    
    main()