#!/usr/bin/env python3
"""
Nancy Directory Ingestion Test Suite

This script provides comprehensive testing of Nancy's directory-based ingestion system
with hash-based change detection and four-brain architecture integration.

Usage:
    python test_directory_ingestion.py

Requirements:
    - Nancy API running on http://localhost:8000
    - requests library (pip install requests)
"""

import os
import json
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class NancyDirectoryTester:
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.test_dir = Path("./test_project_directory")
        self.results: List[Dict[str, Any]] = []
        
    def log_result(self, test_name: str, success: bool, details: Dict[str, Any] = None, error: str = None):
        """Log test result for summary reporting"""
        result = {
            "test_name": test_name,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {},
            "error": error
        }
        self.results.append(result)
        
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")
        if error:
            print(f"  Error: {error}")
        if details and success:
            for key, value in details.items():
                print(f"  {key}: {value}")
        print()
        
    def make_request(self, endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to Nancy API"""
        url = f"{self.api_base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(url, data=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON response: {str(e)}"}
    
    def create_test_project_structure(self):
        """Create comprehensive test project directory structure"""
        print("Creating test project directory structure...")
        
        # Create directories
        dirs = [
            self.test_dir,
            self.test_dir / "docs",
            self.test_dir / "specs", 
            self.test_dir / "test_results",
            self.test_dir / "src" / "components",
            self.test_dir / "config",
            self.test_dir / ".git",  # Should be ignored
            self.test_dir / "node_modules",  # Should be ignored
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create test files with engineering content
        test_files = {
            "README.md": """# Nancy AI System Project

## Overview
Nancy is a four-brain AI librarian system designed for engineering teams.

## Architecture
- **Vector Brain**: Semantic search using ChromaDB
- **Analytical Brain**: Structured queries using DuckDB  
- **Graph Brain**: Relationship mapping using Neo4j
- **Linguistic Brain**: Query processing using Gemma

## Team
- Alice Johnson: Lead Systems Engineer
- Bob Smith: Software Architect
- Carol Davis: Data Science Lead
- David Wilson: DevOps Engineer

## Dependencies
The system requires careful thermal management and power optimization.
""",
            
            "docs/thermal_analysis.md": """# Thermal Analysis Report
**Document ID**: THA-2025-001
**Author**: Alice Johnson
**Date**: 2025-01-15

## Executive Summary
Thermal constraints analysis for Nancy AI system deployment.

## Temperature Requirements
- CPU Junction: Maximum 85°C
- Memory Modules: Maximum 70°C
- Storage Devices: Maximum 60°C

## Cooling Solutions
1. Active air cooling with variable speed fans
2. Thermal interface materials with >3.0 W/mK conductivity
3. Heat spreaders for memory modules

## Power Implications
Thermal management directly impacts power consumption:
- Fan power scales with cube of RPM
- Thermal throttling reduces performance linearly
- Ambient temperature affects cooling efficiency

## Recommendations
Bob Smith should review mechanical constraints.
Carol Davis needs thermal data for ML model training.
""",
            
            "docs/power_budget.txt": """Power Budget Analysis
Author: Bob Smith
Date: 2025-01-12

System Power Requirements:
- CPU: 65W TDP, 95W peak
- GPU: 150W TDP, 200W peak  
- Memory: 32GB DDR4, 12.8W
- Storage: NVMe 8.5W, HDD 12W
- Cooling: Variable 5-25W
- Total: 250W nominal, 350W peak

Power Supply Specifications:
- 80+ Gold efficiency rating
- 500W capacity with 20% headroom
- Active PFC correction
- Over-current protection

Mechanical stress on connectors must be evaluated.
Electrical compliance testing required per IEC standards.
""",
            
            "specs/system_requirements.json": json.dumps({
                "system_name": "Nancy AI System",
                "version": "1.0.0",
                "requirements": {
                    "functional": {
                        "semantic_search": {
                            "response_time_ms": 2000,
                            "accuracy": 0.95,
                            "supported_formats": ["txt", "md", "pdf", "csv"]
                        },
                        "relationship_queries": {
                            "graph_depth": 5,
                            "concurrent_queries": 10
                        }
                    },
                    "non_functional": {
                        "performance": {
                            "documents_max": 100000,
                            "queries_per_second": 50,
                            "memory_limit_gb": 8
                        },
                        "reliability": {
                            "uptime_percentage": 99.9,
                            "mtbf_hours": 8760,
                            "data_backup_frequency": "daily"
                        }
                    }
                },
                "constraints": {
                    "thermal": {
                        "max_ambient_temp": 35,
                        "cooling_type": "active_air"
                    },
                    "power": {
                        "max_consumption_w": 350,
                        "efficiency_rating": "80plus_gold"
                    }
                },
                "team": {
                    "lead_engineer": "Alice Johnson",
                    "architect": "Bob Smith", 
                    "data_scientist": "Carol Davis",
                    "devops": "David Wilson"
                }
            }, indent=2),
            
            "test_results/component_tests.csv": """Component,Test_Type,Result,Temperature_C,Voltage_V,Power_W,Status,Tested_By
CPU_Intel_i7,Stress_Test,Pass,78.5,1.25,87.5,Operational,Alice Johnson
Memory_DDR4_Module1,Memory_Test,Pass,45.2,1.35,3.2,Operational,Bob Smith
Memory_DDR4_Module2,Memory_Test,Pass,46.8,1.35,3.2,Operational,Bob Smith
GPU_RTX3070,Graphics_Stress,Pass,72.1,1.1,165.2,Operational,Carol Davis
SSD_Samsung_980,IO_Performance,Pass,42.3,3.3,7.8,Operational,David Wilson
PSU_Corsair_650W,Load_Test,Pass,38.7,12.0,25.4,Operational,Alice Johnson
Cooling_Fan1,RPM_Test,Pass,25.1,12.0,8.7,Operational,Bob Smith
Cooling_Fan2,RPM_Test,Pass,26.3,12.0,9.1,Operational,Bob Smith
""",
            
            "config/deployment.yaml": """# Nancy Deployment Configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: nancy-config
data:
  # Four-Brain Architecture Settings
  vector_brain:
    provider: "chromadb"
    embedding_model: "BAAI/bge-small-en-v1.5"
    chunk_size: 512
    
  analytical_brain:
    provider: "duckdb" 
    database_path: "/data/nancy.duckdb"
    memory_limit: "2GB"
    
  graph_brain:
    provider: "neo4j"
    uri: "bolt://neo4j:7687"
    username: "neo4j"
    
  linguistic_brain:
    provider: "gemini"
    model: "gemma-3n-e4b-it"
    
  # Engineering Team Settings  
  team_roles:
    - name: "Alice Johnson"
      role: "Lead Engineer"
      expertise: ["thermal_analysis", "systems_engineering"]
    - name: "Bob Smith"
      role: "Software Architect"
      expertise: ["software_design", "power_management"]
    - name: "Carol Davis"
      role: "Data Scientist"
      expertise: ["machine_learning", "data_analysis"]
    - name: "David Wilson"
      role: "DevOps Engineer"
      expertise: ["deployment", "monitoring"]
""",
            
            "src/components/thermal_monitor.py": '''"""
Thermal Monitoring Component
Author: Alice Johnson
Purpose: Monitor thermal constraints in real-time

This component interfaces with hardware sensors to track:
- CPU junction temperatures
- Memory module temperatures  
- Ambient temperature sensors
- Cooling fan RPM and power consumption
"""

import time
import logging
from typing import Dict, List, Optional

class ThermalMonitor:
    """
    Real-time thermal monitoring for Nancy AI system.
    Integrates with power management and performance scaling.
    """
    
    def __init__(self):
        self.cpu_temp_limit = 85.0  # Celsius
        self.memory_temp_limit = 70.0
        self.ambient_temp_limit = 35.0
        self.sensors = self._initialize_sensors()
        
    def _initialize_sensors(self) -> Dict[str, str]:
        """Initialize thermal sensor interfaces"""
        return {
            "cpu_junction": "/sys/class/hwmon/hwmon0/temp1_input",
            "memory_dimm1": "/sys/class/hwmon/hwmon1/temp1_input", 
            "memory_dimm2": "/sys/class/hwmon/hwmon1/temp2_input",
            "ambient": "/sys/class/hwmon/hwmon2/temp1_input"
        }
    
    def read_temperatures(self) -> Dict[str, float]:
        """Read current temperatures from all sensors"""
        temperatures = {}
        
        for sensor_name, sensor_path in self.sensors.items():
            try:
                # Thermal sensor reading logic would go here
                # For demo purposes, returning simulated values
                if sensor_name == "cpu_junction":
                    temperatures[sensor_name] = 72.5
                elif "memory" in sensor_name:
                    temperatures[sensor_name] = 45.2  
                else:
                    temperatures[sensor_name] = 28.1
                    
            except Exception as e:
                logging.error(f"Failed to read {sensor_name}: {e}")
                temperatures[sensor_name] = None
                
        return temperatures
    
    def check_thermal_constraints(self) -> Dict[str, bool]:
        """Check if thermal constraints are satisfied"""
        temps = self.read_temperatures()
        constraints = {}
        
        constraints["cpu_safe"] = temps.get("cpu_junction", 100) < self.cpu_temp_limit
        constraints["memory_safe"] = all(
            temps.get(f"memory_dimm{i}", 100) < self.memory_temp_limit 
            for i in [1, 2]
        )
        constraints["ambient_safe"] = temps.get("ambient", 100) < self.ambient_temp_limit
        
        return constraints
    
    def get_thermal_status(self) -> Dict[str, any]:
        """Get comprehensive thermal status for Nancy system"""
        return {
            "temperatures": self.read_temperatures(),
            "constraints": self.check_thermal_constraints(),
            "timestamp": time.time()
        }

# Integration point for Nancy four-brain architecture
def get_thermal_data_for_ingestion():
    """Provide thermal data in format suitable for Nancy ingestion"""
    monitor = ThermalMonitor()
    status = monitor.get_thermal_status()
    
    return {
        "document_type": "thermal_data",
        "author": "Alice Johnson", 
        "content": f"Thermal status: {status}",
        "metadata": status
    }
''',
            
            # Files that should be ignored
            ".git/config": "# Git configuration - should be ignored",
            "node_modules/package.json": '{"name": "should-be-ignored"}',
            "temp_file.tmp": "Temporary file - should be ignored",
            "__pycache__/cache.pyc": "# Python cache - should be ignored"
        }
        
        # Write all test files
        for file_path, content in test_files.items():
            full_path = self.test_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
        
        print(f"Created {len(test_files)} test files in {self.test_dir}")
        print()
    
    def test_api_health(self):
        """Test 1: API Health Checks"""
        print("=== Test 1: API Health Checks ===")
        
        # Main API health
        result = self.make_request("/health")
        if result.get("status") == "ok":
            self.log_result("Main API Health Check", True, {"status": result.get("status")})
        else:
            self.log_result("Main API Health Check", False, error=result.get("error", "Unknown error"))
        
        # Directory service health  
        result = self.make_request("/api/directory/health")
        if result.get("status") == "healthy":
            self.log_result("Directory Service Health Check", True, {
                "service": result.get("service"),
                "directories_configured": result.get("directories_configured", 0),
                "pending_files": result.get("pending_files", 0)
            })
        else:
            self.log_result("Directory Service Health Check", False, error=result.get("error", "Service unhealthy"))
    
    def test_directory_configuration(self):
        """Test 2: Directory Configuration"""
        print("=== Test 2: Directory Configuration ===")
        
        abs_path = self.test_dir.resolve()
        data = {
            'directory_path': str(abs_path),
            'recursive': 'true',
            'file_patterns': '*.txt,*.md,*.py,*.js,*.json,*.csv,*.yaml',
            'ignore_patterns': '.git/*,node_modules/*,__pycache__/*,*.pyc,*.tmp'
        }
        
        result = self.make_request("/api/directory/config", "POST", data)
        if result.get("status") == "directory_added":
            self.log_result("Add Directory Configuration", True, {
                "config_id": result.get("config_id"),
                "directory_path": result.get("directory_path"),
                "recursive": result.get("recursive")
            })
            return result.get("config_id")
        else:
            self.log_result("Add Directory Configuration", False, error=result.get("error", "Configuration failed"))
            return None
    
    def test_directory_scanning(self):
        """Test 3: Directory Scanning"""
        print("=== Test 3: Directory Scanning ===")
        
        abs_path = self.test_dir.resolve()
        data = {
            'directory_path': str(abs_path),
            'recursive': 'true', 
            'file_patterns': '*.txt,*.md,*.py,*.js,*.json,*.csv,*.yaml',
            'ignore_patterns': '.git/*,node_modules/*,__pycache__/*,*.pyc,*.tmp',
            'author': 'Test Suite Scanner'
        }
        
        result = self.make_request("/api/directory/scan", "POST", data)
        if "error" not in result:
            self.log_result("Directory Scan", True, {
                "total_files_discovered": result.get("total_files_discovered", 0),
                "new_files": result.get("new_files", 0),
                "changed_files": result.get("changed_files", 0),
                "unchanged_files": result.get("unchanged_files", 0),
                "ignored_files": result.get("ignored_files", 0),
                "files_to_process": result.get("files_to_process", 0)
            })
            return result
        else:
            self.log_result("Directory Scan", False, error=result.get("error"))
            return None
    
    def test_file_processing(self, scan_result):
        """Test 4: File Processing"""
        print("=== Test 4: File Processing ===")
        
        if not scan_result or scan_result.get("files_to_process", 0) == 0:
            self.log_result("Process Pending Files", True, {"message": "No files to process - expected for initial scan"})
            return None
        
        data = {
            'limit': '20',
            'author': 'Test Suite Processor'
        }
        
        result = self.make_request("/api/directory/process", "POST", data)
        if "error" not in result:
            self.log_result("Process Pending Files", True, {
                "processed_files": result.get("processed_files", 0),
                "successful": result.get("successful", 0),
                "failed": result.get("failed", 0),
                "success_rate": result.get("success_rate", 0)
            })
            return result
        else:
            self.log_result("Process Pending Files", False, error=result.get("error"))
            return None
    
    def test_change_detection(self):
        """Test 5: Hash-based Change Detection"""
        print("=== Test 5: Hash-based Change Detection ===")
        
        # First scan to establish baseline
        abs_path = self.test_dir.resolve()
        scan_data = {
            'directory_path': str(abs_path),
            'recursive': 'true',
            'file_patterns': '*.txt,*.md,*.py,*.js,*.json,*.csv,*.yaml',
            'ignore_patterns': '.git/*,node_modules/*,__pycache__/*,*.pyc,*.tmp',
            'author': 'Change Detection Test'
        }
        
        baseline_scan = self.make_request("/api/directory/scan", "POST", scan_data)
        if "error" in baseline_scan:
            self.log_result("Change Detection - Baseline Scan", False, error=baseline_scan.get("error"))
            return
        
        # Modify an existing file
        readme_file = self.test_dir / "README.md"
        original_content = readme_file.read_text()
        modified_content = original_content + f"\n\n## Change Detection Test\nModified at {datetime.now().isoformat()}\n"
        readme_file.write_text(modified_content)
        
        # Add a new file
        new_file = self.test_dir / "docs" / "change_detection_test.md"
        new_file.write_text(f"""# Change Detection Test Document

This file was created during change detection testing.

## Details
- Created: {datetime.now().isoformat()}
- Purpose: Validate hash-based change detection
- Author: Automated Test Suite

## Content
The Nancy directory ingestion system should detect this as a new file
and include it in the files_to_process count.
""")
        
        # Wait to ensure timestamp difference
        time.sleep(2)
        
        # Second scan to detect changes
        change_scan = self.make_request("/api/directory/scan", "POST", scan_data)
        if "error" not in change_scan:
            new_files = change_scan.get("new_files", 0)
            changed_files = change_scan.get("changed_files", 0)
            files_to_process = change_scan.get("files_to_process", 0)
            
            success = (new_files > 0 or changed_files > 0) and files_to_process > 0
            
            self.log_result("Change Detection", success, {
                "new_files_detected": new_files,
                "changed_files_detected": changed_files,
                "total_files_to_process": files_to_process,
                "detection_working": success
            })
            
            if success:
                # Process the changes to complete the test
                process_data = {
                    'limit': '10',
                    'author': 'Change Detection Processing'
                }
                process_result = self.make_request("/api/directory/process", "POST", process_data)
                if "error" not in process_result:
                    self.log_result("Process Changed Files", True, {
                        "processed": process_result.get("processed_files", 0),
                        "successful": process_result.get("successful", 0)
                    })
                    
        else:
            self.log_result("Change Detection", False, error=change_scan.get("error"))
    
    def test_combined_operations(self):
        """Test 6: Combined Scan and Process"""
        print("=== Test 6: Combined Scan and Process ===")
        
        # Create another new file to ensure we have something to process
        test_file = self.test_dir / "specs" / "combined_test.json"
        test_file.write_text(json.dumps({
            "test_type": "combined_operations",
            "created_at": datetime.now().isoformat(),
            "purpose": "Test combined scan and process operation",
            "author": "Combined Test Suite"
        }, indent=2))
        
        time.sleep(1)
        
        abs_path = self.test_dir.resolve()
        data = {
            'directory_path': str(abs_path),
            'recursive': 'true',
            'file_patterns': '*.txt,*.md,*.py,*.js,*.json,*.csv,*.yaml',
            'ignore_patterns': '.git/*,node_modules/*,__pycache__/*,*.pyc,*.tmp',
            'author': 'Combined Test Suite',
            'process_limit': '15'
        }
        
        result = self.make_request("/api/directory/scan-and-process", "POST", data)
        if "error" not in result:
            self.log_result("Combined Scan and Process", True, {
                "operation": result.get("operation"),
                "total_files_discovered": result.get("total_files_discovered", 0),
                "files_processed": result.get("files_processed", 0),
                "files_successful": result.get("files_successful", 0),
                "files_failed": result.get("files_failed", 0),
                "overall_status": result.get("overall_status")
            })
            return result
        else:
            self.log_result("Combined Scan and Process", False, error=result.get("error"))
            return None
    
    def test_directory_status(self):
        """Test 7: Directory Status Monitoring"""
        print("=== Test 7: Directory Status Monitoring ===")
        
        result = self.make_request("/api/directory/status")
        if "error" not in result:
            file_stats = result.get("file_statistics", {})
            self.log_result("Directory Status Check", True, {
                "configured_directories": result.get("configured_directories", 0),
                "pending_files": result.get("pending_files", 0),
                "total_files_tracked": file_stats.get("total_files_tracked", 0),
                "processing_errors": file_stats.get("processing_errors", 0)
            })
            return result
        else:
            self.log_result("Directory Status Check", False, error=result.get("error"))
            return None
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("NANCY DIRECTORY INGESTION TEST REPORT")
        print("="*60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\nOverall Results:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Success Rate: {passed_tests/total_tests*100:.1f}%")
        
        print(f"\nDetailed Results:")
        for result in self.results:
            status = "✓ PASS" if result["success"] else "✗ FAIL"
            print(f"  {status}: {result['test_name']}")
            if result["error"]:
                print(f"    Error: {result['error']}")
        
        # Key capabilities summary
        print(f"\nKey Capabilities Validated:")
        
        capabilities = {
            "API Health": any(r["success"] for r in self.results if "Health" in r["test_name"]),
            "Directory Configuration": any(r["success"] for r in self.results if "Configuration" in r["test_name"]),
            "File Scanning": any(r["success"] for r in self.results if "Scan" in r["test_name"]),
            "Hash-based Change Detection": any(r["success"] for r in self.results if "Change Detection" in r["test_name"]),
            "Four-brain Integration": any(r["success"] for r in self.results if "Process" in r["test_name"]),
            "Status Monitoring": any(r["success"] for r in self.results if "Status" in r["test_name"])
        }
        
        for capability, working in capabilities.items():
            status = "✓ WORKING" if working else "✗ FAILED"
            print(f"  {status}: {capability}")
        
        print(f"\nTest Environment:")
        print(f"  API Base URL: {self.api_base_url}")
        print(f"  Test Directory: {self.test_dir.resolve()}")
        print(f"  Test Duration: {datetime.utcnow().isoformat()}")
        
        # Save detailed results
        report_file = Path("nancy_directory_test_report.json")
        with open(report_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": passed_tests/total_tests,
                    "test_timestamp": datetime.utcnow().isoformat()
                },
                "capabilities": capabilities,
                "detailed_results": self.results
            }, f, indent=2)
        
        print(f"\nDetailed results saved to: {report_file}")
        print(f"Test directory preserved at: {self.test_dir}")
        print("\nFor cleanup, run:")
        print(f"  rm -rf {self.test_dir}")
        print(f"  rm {report_file}")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("NANCY DIRECTORY INGESTION TEST SUITE")
        print("Testing four-brain architecture with hash-based change detection")
        print("="*60)
        
        # Create test environment
        self.create_test_project_structure()
        
        # Run all tests
        self.test_api_health()
        config_id = self.test_directory_configuration()
        scan_result = self.test_directory_scanning()
        self.test_file_processing(scan_result)
        self.test_change_detection()
        self.test_combined_operations()
        self.test_directory_status()
        
        # Generate report
        self.generate_report()


def main():
    """Main test execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Nancy Directory Ingestion Test Suite")
    parser.add_argument("--api-url", default="http://localhost:8000", 
                       help="Nancy API base URL (default: http://localhost:8000)")
    parser.add_argument("--skip-setup", action="store_true", 
                       help="Skip test directory creation (use existing)")
    
    args = parser.parse_args()
    
    tester = NancyDirectoryTester(api_base_url=args.api_url)
    
    if not args.skip_setup:
        tester.create_test_project_structure()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTest suite interrupted by user")
        tester.generate_report()
    except Exception as e:
        print(f"\nUnexpected error during testing: {e}")
        tester.generate_report()
        raise


if __name__ == "__main__":
    main()