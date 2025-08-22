#!/usr/bin/env python3
"""
Comprehensive Enhanced Baseline vs Nancy Four-Brain Architecture Benchmark

This test suite validates the complete value proposition of Nancy's enhanced capabilities:
1. Enhanced baseline with spreadsheet textification vs Nancy's structured intelligence
2. Directory-based ingestion and change detection
3. Codebase analysis with AST parsing and Git integration  
4. Cross-data-type relationship discovery
5. Engineering team value scenarios

Demonstrates that even with an enhanced baseline, Nancy's four-brain architecture
provides transformative value that justifies the "cost of intelligence."
"""

import requests
import time
import json
import os
import glob
import shutil
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Tuple
from pathlib import Path
import csv
import pandas as pd

class EnhancedComprehensiveBenchmark:
    def __init__(self):
        self.nancy_url = "http://localhost:8000"
        self.baseline_url = "http://localhost:8002"
        self.results = []
        self.metrics = {
            "nancy": {
                "llm_calls": 0,
                "embedding_operations": 0,
                "processing_time": 0,
                "errors": 0,
                "cross_brain_queries": 0,
                "structured_queries": 0
            },
            "baseline": {
                "llm_calls": 0,
                "embedding_operations": 0,
                "processing_time": 0,
                "errors": 0,
                "text_searches": 0
            }
        }
        
        # Test data directories
        self.test_data_dir = "benchmark_test_data"
        self.spreadsheet_data_dir = "test_data"
        self.codebase_test_dir = "test_codebase"
        
        # Comprehensive test scenarios
        self.test_scenarios = [
            # SCENARIO 1: Spreadsheet Intelligence Testing
            {
                "category": "Spreadsheet Intelligence",
                "test_type": "structured_query",
                "scenario_description": "Test ability to answer structured data questions",
                "queries": [
                    {
                        "query": "Which components over $10W are owned by thermal engineers and have high priority?",
                        "baseline_capability": "Text search in textified spreadsheet content",
                        "nancy_capability": "Structured query with cross-table relationships",
                        "expected_nancy_advantage": "Precise filtering vs approximate text matching"
                    },
                    {
                        "query": "Show me the cost breakdown of all validated components by subsystem",
                        "baseline_capability": "Text pattern matching for cost mentions",
                        "nancy_capability": "Structured aggregation and grouping",
                        "expected_nancy_advantage": "Accurate calculations vs text approximations"
                    },
                    {
                        "query": "Which engineers work on both high-priority and critical components?",
                        "baseline_capability": "Text search for engineer names and priorities",
                        "nancy_capability": "Graph relationships with multi-criteria analysis",
                        "expected_nancy_advantage": "Relationship discovery vs keyword matching"
                    }
                ]
            },
            
            # SCENARIO 2: Codebase Understanding
            {
                "category": "Codebase Analysis",
                "test_type": "ast_analysis",
                "scenario_description": "Test understanding of code structure and relationships",
                "queries": [
                    {
                        "query": "What functions handle database connections and who authored them?",
                        "baseline_capability": "Text search in code comments and strings",
                        "nancy_capability": "AST parsing with Git author attribution",
                        "expected_nancy_advantage": "Structural understanding vs text matching"
                    },
                    {
                        "query": "Which modules import the thermal_control library and what functions do they call?",
                        "baseline_capability": "Text pattern matching for imports",
                        "nancy_capability": "AST dependency graph with function call analysis",
                        "expected_nancy_advantage": "Complete dependency mapping vs partial text matches"
                    },
                    {
                        "query": "Show me recent changes to authentication code and their impact on other modules",
                        "baseline_capability": "Text search for recent authentication mentions",
                        "nancy_capability": "Git integration with AST impact analysis",
                        "expected_nancy_advantage": "Change impact analysis vs simple text search"
                    }
                ]
            },
            
            # SCENARIO 3: Cross-Data-Type Relationships
            {
                "category": "Cross-Domain Intelligence",
                "test_type": "relationship_discovery",
                "scenario_description": "Test ability to connect information across different data types",
                "queries": [
                    {
                        "query": "Connect thermal test results to design requirements and responsible engineers",
                        "baseline_capability": "Text search across individual files",
                        "nancy_capability": "Graph traversal connecting spreadsheets, docs, and people",
                        "expected_nancy_advantage": "Multi-hop relationship discovery vs isolated text matches"
                    },
                    {
                        "query": "Which code functions implement thermal constraints from the requirements spreadsheet?",
                        "baseline_capability": "Text search for thermal keywords in code",
                        "nancy_capability": "Relationship mapping between requirements and implementations",
                        "expected_nancy_advantage": "Traceability links vs keyword coincidence"
                    },
                    {
                        "query": "Show me all engineering changes this week and their dependencies across docs, code, and data",
                        "baseline_capability": "Text search for recent change mentions",
                        "nancy_capability": "Temporal analysis with cross-domain impact mapping",
                        "expected_nancy_advantage": "Comprehensive change tracking vs fragmented text search"
                    }
                ]
            },
            
            # SCENARIO 4: Directory Change Intelligence
            {
                "category": "Change Intelligence", 
                "test_type": "incremental_update",
                "scenario_description": "Test ability to detect and analyze project changes",
                "queries": [
                    {
                        "query": "What has changed in the project and how does it affect existing requirements?",
                        "baseline_capability": "Static content - no change detection",
                        "nancy_capability": "Hash-based change detection with impact analysis",
                        "expected_nancy_advantage": "Dynamic awareness vs static snapshots"
                    },
                    {
                        "query": "Which engineers should be notified about recent thermal analysis updates?",
                        "baseline_capability": "Text search for engineer names in documents",
                        "nancy_capability": "Change detection with relationship-based notification rules",
                        "expected_nancy_advantage": "Intelligent stakeholder identification vs name matching"
                    }
                ]
            },
            
            # SCENARIO 5: Engineering Team Value Scenarios
            {
                "category": "Engineering Value",
                "test_type": "real_world_scenarios",
                "scenario_description": "Test realistic engineering team workflows",
                "queries": [
                    {
                        "query": "I need to understand thermal constraints for the new component design. Show me requirements, test results, code implementations, and expert contacts.",
                        "baseline_capability": "Multiple separate text searches",
                        "nancy_capability": "Single query with four-brain orchestration",
                        "expected_nancy_advantage": "Integrated workflow vs manual correlation"
                    },
                    {
                        "query": "Create a traceability report connecting requirements to tests to code for thermal management subsystem",
                        "baseline_capability": "Manual document correlation from text searches",
                        "nancy_capability": "Automated traceability via graph relationships",
                        "expected_nancy_advantage": "Complete traceability vs partial correlation"
                    },
                    {
                        "query": "What expertise gaps exist in our thermal management team based on component assignments and code contributions?",
                        "baseline_capability": "Cannot perform - requires structured analysis",
                        "nancy_capability": "Cross-analysis of spreadsheets, code, and git history",
                        "expected_nancy_advantage": "Capability that baseline cannot provide"
                    }
                ]
            }
        ]
    
    def setup_comprehensive_test_data(self) -> Dict[str, Any]:
        """Set up comprehensive test data covering all data types"""
        print("🏗️  Setting up comprehensive test data...")
        
        setup_results = {
            "documents": {"status": "pending", "files": []},
            "spreadsheets": {"status": "pending", "files": []}, 
            "codebase": {"status": "pending", "files": []},
            "mixed_content": {"status": "pending", "files": []}
        }
        
        # 1. Ensure document test data exists
        if os.path.exists(self.test_data_dir):
            doc_files = glob.glob(os.path.join(self.test_data_dir, "*.txt"))
            setup_results["documents"]["files"] = [os.path.basename(f) for f in doc_files]
            setup_results["documents"]["status"] = "ready"
            print(f"   ✓ Documents: {len(doc_files)} files")
        else:
            setup_results["documents"]["status"] = "missing"
            print(f"   ✗ Document directory missing: {self.test_data_dir}")
        
        # 2. Ensure spreadsheet test data exists
        if os.path.exists(self.spreadsheet_data_dir):
            csv_files = glob.glob(os.path.join(self.spreadsheet_data_dir, "*.csv"))
            setup_results["spreadsheets"]["files"] = [os.path.basename(f) for f in csv_files]
            setup_results["spreadsheets"]["status"] = "ready"
            print(f"   ✓ Spreadsheets: {len(csv_files)} files")
        else:
            setup_results["spreadsheets"]["status"] = "missing"
            print(f"   ✗ Spreadsheet directory missing: {self.spreadsheet_data_dir}")
        
        # 3. Create synthetic codebase for testing
        if not os.path.exists(self.codebase_test_dir):
            os.makedirs(self.codebase_test_dir)
        
        # Create test Python files with realistic engineering content
        test_code_files = {
            "thermal_control.py": '''"""
Thermal Control System
Author: Sarah Chen <sarah.chen@company.com>
"""
import database_manager
from sensors import TemperatureSensor
import numpy as np

class ThermalController:
    def __init__(self, max_temp=85.0):
        self.max_temp = max_temp
        self.sensor = TemperatureSensor()
        self.db = database_manager.connect()
        
    def monitor_temperature(self):
        """Monitor thermal constraints per COMP-001 requirements"""
        current_temp = self.sensor.read_temperature()
        if current_temp > self.max_temp:
            self.trigger_cooling()
        return current_temp
        
    def trigger_cooling(self):
        """Emergency cooling activation"""
        self.db.log_event("THERMAL_ALERT", {"temp": self.sensor.read_temperature()})
''',
            "database_manager.py": '''"""
Database Connection Manager
Author: Mike Rodriguez <mike.rodriguez@company.com>
"""
import sqlite3
from typing import Dict, Any

class DatabaseConnection:
    def __init__(self, db_path="telemetry.db"):
        self.db_path = db_path
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        self.connection = sqlite3.connect(self.db_path)
        return self
        
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log system events to database"""
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO events (type, data) VALUES (?, ?)", 
                      (event_type, str(data)))
        self.connection.commit()

def connect():
    """Factory function for database connections"""
    return DatabaseConnection().connect()
''',
            "authentication.py": '''"""
Authentication Module  
Author: Dr. Amanda Torres <amanda.torres@company.com>
Last Modified: Recent security updates
"""
import hashlib
import jwt
import database_manager

class AuthenticationManager:
    def __init__(self):
        self.db = database_manager.connect()
        self.secret_key = "thermal_system_secret"
        
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user credentials"""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        # Check against database
        return self.validate_credentials(username, hashed_password)
        
    def validate_credentials(self, username: str, hashed_password: str) -> bool:
        """Validate user credentials against database"""
        cursor = self.db.connection.cursor()
        result = cursor.execute(
            "SELECT COUNT(*) FROM users WHERE username=? AND password=?",
            (username, hashed_password)
        ).fetchone()
        return result[0] > 0
        
    def generate_token(self, username: str) -> str:
        """Generate JWT token for authenticated user"""
        payload = {"username": username, "role": "engineer"}
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
'''
        }
        
        for filename, content in test_code_files.items():
            file_path = os.path.join(self.codebase_test_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        setup_results["codebase"]["files"] = list(test_code_files.keys())
        setup_results["codebase"]["status"] = "ready"
        print(f"   ✓ Codebase: {len(test_code_files)} files created")
        
        # 4. Create mixed content test files
        mixed_content = {
            "thermal_requirements_analysis.md": '''# Thermal Requirements Analysis

## Component Requirements
Based on component_requirements.csv, the following components have critical thermal constraints:

- COMP-001 (Primary CPU): 85°C max, owned by Sarah Chen
- COMP-002 (Memory Module): 70°C max, owned by Mike Rodriguez  

## Code Implementation
The thermal_control.py module implements these constraints with real-time monitoring.
See thermal_control.ThermalController.monitor_temperature() for implementation details.

## Test Results
Refer to thermal_test_results.csv for validation data.
'''
        }
        
        for filename, content in mixed_content.items():
            file_path = os.path.join(self.test_data_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        setup_results["mixed_content"]["files"] = list(mixed_content.keys())
        setup_results["mixed_content"]["status"] = "ready"
        print(f"   ✓ Mixed content: {len(mixed_content)} files created")
        
        return setup_results
    
    def ingest_comprehensive_data(self, system_name: str, base_url: str) -> Dict[str, Any]:
        """Ingest all data types into specified system"""
        print(f"📥 Comprehensive data ingestion for {system_name}...")
        
        ingestion_results = {
            "system": system_name,
            "total_files": 0,
            "successful_uploads": 0,
            "failed_uploads": 0,
            "ingestion_time": 0,
            "by_type": {
                "documents": {"files": 0, "success": 0, "time": 0},
                "spreadsheets": {"files": 0, "success": 0, "time": 0},
                "codebase": {"files": 0, "success": 0, "time": 0}
            },
            "errors": []
        }
        
        start_time = time.time()
        
        # 1. Ingest documents
        doc_result = self._ingest_directory(base_url, self.test_data_dir, "Benchmark User", "*.txt")
        ingestion_results["by_type"]["documents"] = doc_result
        
        # 2. Ingest spreadsheets  
        csv_result = self._ingest_directory(base_url, self.spreadsheet_data_dir, "Data Manager", "*.csv")
        ingestion_results["by_type"]["spreadsheets"] = csv_result
        
        # 3. Ingest codebase (if Nancy supports directory ingestion)
        if system_name.lower() == "nancy":
            code_result = self._ingest_directory(base_url, self.codebase_test_dir, "Development Team", "*.py") 
            ingestion_results["by_type"]["codebase"] = code_result
        else:
            # Baseline gets individual code files
            code_result = self._ingest_directory(base_url, self.codebase_test_dir, "Development Team", "*.py")
            ingestion_results["by_type"]["codebase"] = code_result
        
        # Calculate totals
        for type_result in ingestion_results["by_type"].values():
            ingestion_results["total_files"] += type_result["files"]
            ingestion_results["successful_uploads"] += type_result["success"]
            ingestion_results["failed_uploads"] += type_result["files"] - type_result["success"]
        
        ingestion_results["ingestion_time"] = time.time() - start_time
        
        print(f"   ✓ {system_name} ingestion: {ingestion_results['successful_uploads']}/{ingestion_results['total_files']} files in {ingestion_results['ingestion_time']:.1f}s")
        
        return ingestion_results
    
    def _ingest_directory(self, base_url: str, directory: str, author: str, pattern: str) -> Dict[str, Any]:
        """Helper to ingest files from a directory"""
        if not os.path.exists(directory):
            return {"files": 0, "success": 0, "time": 0, "errors": []}
        
        files = glob.glob(os.path.join(directory, pattern))
        if not files:
            return {"files": 0, "success": 0, "time": 0, "errors": []}
        
        start_time = time.time()
        successful_uploads = 0
        errors = []
        
        for file_path in files:
            try:
                filename = os.path.basename(file_path)
                
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Upload via API
                files_data = {'file': (filename, content, 'text/plain')}
                data = {'author': author}
                
                response = requests.post(
                    f"{base_url}/api/ingest",
                    files=files_data,
                    data=data,
                    timeout=120
                )
                
                if response.status_code == 200:
                    successful_uploads += 1
                else:
                    errors.append(f"{filename}: HTTP {response.status_code}")
                    
            except Exception as e:
                errors.append(f"{filename}: {str(e)}")
        
        return {
            "files": len(files),
            "success": successful_uploads,
            "time": time.time() - start_time,
            "errors": errors
        }
    
    def run_scenario_comparison(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive comparison for a test scenario"""
        print(f"\n🧪 Testing Scenario: {scenario['category']}")
        print(f"   Description: {scenario['scenario_description']}")
        
        scenario_results = {
            "category": scenario["category"],
            "test_type": scenario["test_type"],
            "description": scenario["scenario_description"],
            "query_results": [],
            "performance_summary": {
                "nancy_avg_time": 0,
                "baseline_avg_time": 0,
                "nancy_success_count": 0,
                "baseline_success_count": 0,
                "nancy_advantage_demonstrated": 0
            }
        }
        
        nancy_times = []
        baseline_times = []
        
        for i, query_test in enumerate(scenario["queries"], 1):
            print(f"\n   Query {i}: {query_test['query'][:60]}...")
            
            # Test Nancy
            print("     🧠 Nancy Four-Brain:", end=" ", flush=True)
            nancy_result = self.query_with_detailed_analysis("Nancy", self.nancy_url, query_test)
            print(f"({nancy_result['query_time']:.1f}s)")
            
            # Test Baseline
            print("     📚 Baseline RAG:", end=" ", flush=True)
            baseline_result = self.query_with_detailed_analysis("Baseline", self.baseline_url, query_test)
            print(f"({baseline_result['query_time']:.1f}s)")
            
            # Analyze advantage
            advantage_analysis = self._analyze_query_advantage(nancy_result, baseline_result, query_test)
            
            query_result = {
                "query": query_test["query"],
                "baseline_capability": query_test["baseline_capability"],
                "nancy_capability": query_test["nancy_capability"],
                "expected_nancy_advantage": query_test["expected_nancy_advantage"],
                "nancy_result": nancy_result,
                "baseline_result": baseline_result,
                "advantage_analysis": advantage_analysis
            }
            
            scenario_results["query_results"].append(query_result)
            
            # Track performance
            if nancy_result["status"] == "success":
                nancy_times.append(nancy_result["query_time"])
                scenario_results["performance_summary"]["nancy_success_count"] += 1
            
            if baseline_result["status"] == "success":
                baseline_times.append(baseline_result["query_time"])
                scenario_results["performance_summary"]["baseline_success_count"] += 1
            
            if advantage_analysis["nancy_advantage_score"] > 0.6:
                scenario_results["performance_summary"]["nancy_advantage_demonstrated"] += 1
        
        # Calculate summary metrics
        if nancy_times:
            scenario_results["performance_summary"]["nancy_avg_time"] = sum(nancy_times) / len(nancy_times)
        if baseline_times:
            scenario_results["performance_summary"]["baseline_avg_time"] = sum(baseline_times) / len(baseline_times)
        
        return scenario_results
    
    def query_with_detailed_analysis(self, system_name: str, base_url: str, query_test: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced query method with detailed capability analysis"""
        start_time = time.time()
        
        try:
            request_data = {"query": query_test["query"]}
            if system_name.lower() == "nancy":
                request_data["orchestrator"] = "langchain"
            
            response = requests.post(
                f"{base_url}/api/query",
                json=request_data,
                timeout=180,
                headers={"Content-Type": "application/json"}
            )
            
            query_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Analyze response quality
                response_analysis = self._analyze_response_quality(
                    result.get("response", ""), 
                    result.get("sources", []),
                    query_test
                )
                
                return {
                    "status": "success",
                    "query_time": query_time,
                    "response": result.get("response", ""),
                    "sources": result.get("sources", []),
                    "response_length": len(result.get("response", "")),
                    "source_count": len(result.get("sources", [])),
                    "analysis": response_analysis,
                    "raw_result": result
                }
            else:
                return {
                    "status": "error",
                    "query_time": query_time,
                    "error": f"HTTP {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return {
                "status": "error",
                "query_time": time.time() - start_time,
                "error": str(e)
            }
    
    def _analyze_response_quality(self, response: str, sources: List[str], query_test: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze response quality for capability comparison"""
        response_lower = response.lower()
        
        # Check for structured data indicators
        structured_indicators = ["component", "requirement", "thermal", "owner", "priority", "status", "cost", "power"]
        structured_score = sum(1 for indicator in structured_indicators if indicator in response_lower) / len(structured_indicators)
        
        # Check for relationship indicators  
        relationship_indicators = ["connect", "relate", "link", "depend", "impact", "affect", "responsible", "author"]
        relationship_score = sum(1 for indicator in relationship_indicators if indicator in response_lower) / len(relationship_indicators)
        
        # Check for technical depth
        technical_indicators = ["function", "module", "implementation", "code", "algorithm", "database", "ast", "git"]
        technical_score = sum(1 for indicator in technical_indicators if indicator in response_lower) / len(technical_indicators)
        
        return {
            "structured_data_score": structured_score,
            "relationship_score": relationship_score,
            "technical_depth_score": technical_score,
            "overall_quality_score": (structured_score + relationship_score + technical_score) / 3,
            "source_diversity": len(set([s.split('.')[0] for s in sources])),
            "response_comprehensiveness": min(len(response) / 200, 1.0)  # Normalize to 0-1
        }
    
    def _analyze_query_advantage(self, nancy_result: Dict[str, Any], baseline_result: Dict[str, Any], query_test: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Nancy's advantage over baseline for this specific query"""
        
        if nancy_result["status"] != "success" or baseline_result["status"] != "success":
            return {
                "nancy_advantage_score": 0.0,
                "advantage_factors": [],
                "analysis": "Cannot compare - one or both queries failed"
            }
        
        nancy_analysis = nancy_result.get("analysis", {})
        baseline_analysis = baseline_result.get("analysis", {})
        
        advantage_factors = []
        advantage_score = 0.0
        
        # Compare quality scores
        nancy_quality = nancy_analysis.get("overall_quality_score", 0)
        baseline_quality = baseline_analysis.get("overall_quality_score", 0)
        
        if nancy_quality > baseline_quality * 1.2:
            advantage_factors.append("Higher overall response quality")
            advantage_score += 0.3
        
        # Compare source diversity
        nancy_sources = nancy_analysis.get("source_diversity", 0)
        baseline_sources = baseline_analysis.get("source_diversity", 0)
        
        if nancy_sources > baseline_sources:
            advantage_factors.append("Better source diversity")
            advantage_score += 0.2
        
        # Compare technical depth
        nancy_technical = nancy_analysis.get("technical_depth_score", 0)
        baseline_technical = baseline_analysis.get("technical_depth_score", 0)
        
        if nancy_technical > baseline_technical * 1.5:
            advantage_factors.append("Superior technical depth")
            advantage_score += 0.3
        
        # Compare response time efficiency
        if nancy_result["query_time"] < baseline_result["query_time"]:
            advantage_factors.append("Faster response time")
            advantage_score += 0.1
        elif nancy_result["query_time"] < baseline_result["query_time"] * 2:
            advantage_factors.append("Reasonable response time for enhanced capabilities")
            advantage_score += 0.05
        
        # Check for unique capabilities
        nancy_response = nancy_result["response"].lower()
        baseline_response = baseline_result["response"].lower()
        
        unique_keywords = ["relationship", "cross-reference", "ast", "git", "structured", "graph"]
        nancy_unique = sum(1 for kw in unique_keywords if kw in nancy_response and kw not in baseline_response)
        
        if nancy_unique > 0:
            advantage_factors.append(f"Demonstrates {nancy_unique} unique advanced capabilities")
            advantage_score += min(nancy_unique * 0.1, 0.3)
        
        return {
            "nancy_advantage_score": min(advantage_score, 1.0),
            "advantage_factors": advantage_factors,
            "nancy_quality_score": nancy_quality,
            "baseline_quality_score": baseline_quality,
            "analysis": f"Nancy demonstrates {len(advantage_factors)} advantage factors with score {advantage_score:.2f}"
        }
    
    def run_comprehensive_enhanced_benchmark(self) -> Dict[str, Any]:
        """Run the complete enhanced baseline vs Nancy benchmark"""
        print("🚀 COMPREHENSIVE ENHANCED BENCHMARK")
        print("   Nancy Four-Brain Architecture vs Enhanced Baseline RAG")
        print("=" * 80)
        
        benchmark_start = time.time()
        
        # Phase 1: Setup
        print("\n1️⃣ COMPREHENSIVE TEST DATA SETUP")
        print("-" * 40)
        setup_result = self.setup_comprehensive_test_data()
        
        # Phase 2: System Health
        print("\n2️⃣ SYSTEM HEALTH VERIFICATION")
        print("-" * 40)
        nancy_health = self._test_system_health("Nancy", self.nancy_url)
        baseline_health = self._test_system_health("Baseline", self.baseline_url)
        
        print(f"   Nancy Four-Brain: {nancy_health['status']}")
        print(f"   Enhanced Baseline: {baseline_health['status']}")
        
        # Phase 3: Comprehensive Ingestion
        print("\n3️⃣ COMPREHENSIVE DATA INGESTION")
        print("-" * 40)
        nancy_ingestion = self.ingest_comprehensive_data("Nancy", self.nancy_url)
        baseline_ingestion = self.ingest_comprehensive_data("Baseline", self.baseline_url)
        
        # Wait for processing
        print("\n   ⏳ Allowing time for comprehensive data processing...")
        time.sleep(15)
        
        # Phase 4: Scenario Testing
        print("\n4️⃣ SCENARIO-BASED TESTING")
        print("-" * 40)
        scenario_results = []
        
        for scenario in self.test_scenarios:
            scenario_result = self.run_scenario_comparison(scenario)
            scenario_results.append(scenario_result)
        
        # Phase 5: Comprehensive Analysis
        print("\n5️⃣ COMPREHENSIVE ANALYSIS")
        print("-" * 40)
        final_analysis = self._generate_comprehensive_analysis(scenario_results)
        
        benchmark_time = time.time() - benchmark_start
        
        # Compile final results
        final_results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "benchmark_type": "Comprehensive Enhanced Baseline vs Nancy",
                "total_benchmark_time": benchmark_time,
                "nancy_url": self.nancy_url,
                "baseline_url": self.baseline_url,
                "test_scenarios": len(self.test_scenarios)
            },
            "setup_results": setup_result,
            "system_health": {
                "nancy": nancy_health,
                "baseline": baseline_health
            },
            "ingestion_results": {
                "nancy": nancy_ingestion,
                "baseline": baseline_ingestion
            },
            "scenario_results": scenario_results,
            "comprehensive_analysis": final_analysis,
            "value_proposition": self._generate_value_proposition(final_analysis)
        }
        
        return final_results
    
    def _test_system_health(self, system_name: str, base_url: str) -> Dict[str, Any]:
        """Test system health"""
        try:
            response = requests.get(f"{base_url}/health", timeout=30)
            if response.status_code == 200:
                return {"status": "healthy", "details": response.json()}
            else:
                return {"status": "unhealthy", "error": response.text}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _generate_comprehensive_analysis(self, scenario_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive analysis across all scenarios"""
        
        total_queries = sum(len(scenario["query_results"]) for scenario in scenario_results)
        nancy_total_success = sum(scenario["performance_summary"]["nancy_success_count"] for scenario in scenario_results)
        baseline_total_success = sum(scenario["performance_summary"]["baseline_success_count"] for scenario in scenario_results)
        nancy_advantages = sum(scenario["performance_summary"]["nancy_advantage_demonstrated"] for scenario in scenario_results)
        
        nancy_times = []
        baseline_times = []
        
        for scenario in scenario_results:
            for query_result in scenario["query_results"]:
                if query_result["nancy_result"]["status"] == "success":
                    nancy_times.append(query_result["nancy_result"]["query_time"])
                if query_result["baseline_result"]["status"] == "success":
                    baseline_times.append(query_result["baseline_result"]["query_time"])
        
        # Calculate capability-specific performance
        capability_analysis = {}
        for scenario in scenario_results:
            scenario_name = scenario["category"]
            scenario_advantages = scenario["performance_summary"]["nancy_advantage_demonstrated"]
            scenario_queries = len(scenario["query_results"])
            
            capability_analysis[scenario_name] = {
                "total_queries": scenario_queries,
                "nancy_advantages": scenario_advantages,
                "advantage_rate": scenario_advantages / scenario_queries if scenario_queries > 0 else 0,
                "nancy_avg_time": scenario["performance_summary"]["nancy_avg_time"],
                "baseline_avg_time": scenario["performance_summary"]["baseline_avg_time"]
            }
        
        return {
            "overall_performance": {
                "total_queries": total_queries,
                "nancy_success_rate": nancy_total_success / total_queries,
                "baseline_success_rate": baseline_total_success / total_queries,
                "nancy_advantage_rate": nancy_advantages / total_queries,
                "nancy_avg_time": sum(nancy_times) / len(nancy_times) if nancy_times else 0,
                "baseline_avg_time": sum(baseline_times) / len(baseline_times) if baseline_times else 0
            },
            "capability_breakdown": capability_analysis,
            "intelligence_cost_analysis": {
                "nancy_avg_time": sum(nancy_times) / len(nancy_times) if nancy_times else 0,
                "baseline_avg_time": sum(baseline_times) / len(baseline_times) if baseline_times else 0,
                "intelligence_time_premium": (sum(nancy_times) / len(nancy_times)) / (sum(baseline_times) / len(baseline_times)) if baseline_times and nancy_times else 1.0,
                "capabilities_gained": nancy_advantages,
                "cost_per_capability": (sum(nancy_times) - sum(baseline_times)) / nancy_advantages if nancy_advantages > 0 and nancy_times and baseline_times else 0
            }
        }
    
    def _generate_value_proposition(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate engineering team value proposition based on results"""
        
        overall = analysis["overall_performance"]
        cost_analysis = analysis["intelligence_cost_analysis"]
        capabilities = analysis["capability_breakdown"]
        
        value_factors = []
        
        # Unique capability analysis
        if overall["nancy_advantage_rate"] > 0.7:
            value_factors.append("Nancy demonstrates clear superiority in 70%+ of test scenarios")
        elif overall["nancy_advantage_rate"] > 0.5:
            value_factors.append("Nancy shows meaningful advantages in majority of scenarios")
        
        # Cost-benefit analysis
        time_premium = cost_analysis["intelligence_time_premium"]
        if time_premium < 2.0:
            value_factors.append(f"Intelligence premium is reasonable ({time_premium:.1f}x baseline time)")
        elif time_premium < 3.0:
            value_factors.append(f"Intelligence premium is moderate ({time_premium:.1f}x baseline time)")
        else:
            value_factors.append(f"Intelligence premium is significant ({time_premium:.1f}x baseline time)")
        
        # Capability-specific value
        high_value_capabilities = []
        for capability_name, capability_data in capabilities.items():
            if capability_data["advantage_rate"] > 0.8:
                high_value_capabilities.append(capability_name)
        
        if high_value_capabilities:
            value_factors.append(f"Exceptional performance in: {', '.join(high_value_capabilities)}")
        
        # Engineering team ROI
        roi_analysis = "Unknown"
        if overall["nancy_advantage_rate"] > 0.6 and time_premium < 3.0:
            roi_analysis = "Positive - Clear engineering value with reasonable cost"
        elif overall["nancy_advantage_rate"] > 0.4:
            roi_analysis = "Mixed - Some value demonstrated, evaluate specific use cases"
        else:
            roi_analysis = "Questionable - Limited advantages shown"
        
        return {
            "value_factors": value_factors,
            "engineering_roi": roi_analysis,
            "recommendation": self._generate_recommendation(overall, cost_analysis),
            "high_value_scenarios": high_value_capabilities
        }
    
    def _generate_recommendation(self, overall: Dict[str, Any], cost_analysis: Dict[str, Any]) -> str:
        """Generate final recommendation for engineering teams"""
        
        advantage_rate = overall["nancy_advantage_rate"]
        time_premium = cost_analysis["intelligence_time_premium"]
        
        if advantage_rate > 0.7 and time_premium < 2.0:
            return "RECOMMEND: Nancy provides significant value with reasonable cost. Deploy for engineering teams."
        elif advantage_rate > 0.6 and time_premium < 3.0:
            return "CONSIDER: Nancy shows clear benefits. Evaluate for high-value engineering workflows."
        elif advantage_rate > 0.5:
            return "PILOT: Nancy has potential. Run targeted pilot with specific engineering use cases."
        else:
            return "DEFER: Limited advantages demonstrated. Further development or different approach needed."


def main():
    """Run the comprehensive enhanced benchmark"""
    benchmark = EnhancedComprehensiveBenchmark()
    
    try:
        print("Starting Comprehensive Enhanced Baseline vs Nancy Benchmark")
        print("This test validates Nancy's four-brain architecture value proposition")
        print("against an enhanced baseline RAG system with spreadsheet capabilities.")
        print()
        
        results = benchmark.run_comprehensive_enhanced_benchmark()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_comprehensive_benchmark_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Display executive summary
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE ENHANCED BENCHMARK RESULTS")
        print("="*80)
        
        analysis = results['comprehensive_analysis']
        value_prop = results['value_proposition']
        
        print(f"\n🏆 OVERALL PERFORMANCE:")
        overall = analysis['overall_performance']
        print(f"   Total Test Queries: {overall['total_queries']}")
        print(f"   Nancy Success Rate: {overall['nancy_success_rate']:.1%}")
        print(f"   Baseline Success Rate: {overall['baseline_success_rate']:.1%}")
        print(f"   Nancy Advantage Rate: {overall['nancy_advantage_rate']:.1%}")
        print(f"   Average Query Time - Nancy: {overall['nancy_avg_time']:.1f}s")
        print(f"   Average Query Time - Baseline: {overall['baseline_avg_time']:.1f}s")
        
        print(f"\n💰 INTELLIGENCE COST ANALYSIS:")
        cost = analysis['intelligence_cost_analysis']
        print(f"   Intelligence Time Premium: {cost['intelligence_time_premium']:.1f}x")
        print(f"   Capabilities Gained: {cost['capabilities_gained']}")
        print(f"   Cost per Capability: {cost['cost_per_capability']:.1f}s")
        
        print(f"\n🎯 CAPABILITY BREAKDOWN:")
        for capability, data in analysis['capability_breakdown'].items():
            print(f"   {capability}: {data['advantage_rate']:.1%} advantage rate ({data['nancy_advantages']}/{data['total_queries']} queries)")
        
        print(f"\n💡 VALUE PROPOSITION:")
        for factor in value_prop['value_factors']:
            print(f"   • {factor}")
        
        print(f"\n📈 ENGINEERING TEAM ROI: {value_prop['engineering_roi']}")
        print(f"\n🔍 RECOMMENDATION: {value_prop['recommendation']}")
        
        print(f"\n📁 Detailed results saved to: {filename}")
        
        return results
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
        return None
    except Exception as e:
        print(f"\n\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()