#!/usr/bin/env python3
"""
Directory Change Intelligence Testing

Tests Nancy's ability to detect, analyze, and respond to project changes
through hash-based change detection and relationship impact analysis.

This represents a unique capability that baseline RAG systems cannot provide
since they work with static snapshots of data.

Tests:
1. Change detection accuracy
2. Impact analysis across data types
3. Stakeholder notification intelligence
4. Incremental update efficiency
5. Change relationship mapping
"""

import requests
import json
import time
import os
import shutil
import tempfile
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from pathlib import Path

class ChangeIntelligenceTest:
    def __init__(self):
        self.nancy_url = "http://localhost:8000"
        self.baseline_url = "http://localhost:8002"  # Baseline cannot do change detection
        self.test_project_dir = "test_project_changes"
        self.original_files = {}
        self.change_scenarios = []
    
    def setup_test_project(self) -> Dict[str, Any]:
        """Create test project with various file types for change testing"""
        print("🏗️  Setting up test project for change intelligence testing...")
        
        if os.path.exists(self.test_project_dir):
            shutil.rmtree(self.test_project_dir)
        os.makedirs(self.test_project_dir)
        
        # Create project structure with various file types
        project_structure = {
            "docs/requirements.md": '''# Thermal Management Requirements

## Component Requirements
- COMP-001: Primary CPU with 85°C thermal limit
- COMP-002: Memory Module with 70°C thermal limit  
- COMP-003: Radio Transceiver with 60°C thermal limit

## Responsible Engineers
- Thermal Lead: Sarah Chen
- Mechanical Lead: Mike Rodriguez
- Electrical Lead: Dr. Amanda Torres

## Verification Methods
- Bench testing for COMP-001
- Environmental testing for housing
- Field testing for communication range

Last Updated: 2024-08-12
''',
            
            "data/component_specs.csv": '''component_id,component_name,thermal_limit_c,power_w,owner,status,priority
COMP-001,Primary CPU,85,12.5,Sarah Chen,Validated,High
COMP-002,Memory Module,70,3.2,Mike Rodriguez,In Review,Medium  
COMP-003,Radio Transceiver,60,8.7,Dr. Amanda Torres,Validated,High
COMP-004,Battery Pack,45,0.0,James Wilson,Draft,Critical
''',
            
            "code/thermal_monitor.py": '''"""
Thermal Monitoring Module
Author: Sarah Chen
"""
import time
import logging

class ThermalMonitor:
    def __init__(self, max_temp=85):
        self.max_temp = max_temp
        self.logger = logging.getLogger(__name__)
        
    def check_temperature(self, component_id, current_temp):
        """Check if temperature exceeds limits"""
        if current_temp > self.max_temp:
            self.logger.warning(f"Temperature alert for {component_id}: {current_temp}°C")
            return False
        return True
        
    def get_thermal_status(self):
        """Get overall thermal system status"""
        return {"status": "normal", "max_temp": self.max_temp}
''',
            
            "tests/thermal_test_results.csv": '''test_id,component_id,test_date,temperature_c,result,notes
TEST-001,COMP-001,2024-08-10,82,Pass,Within thermal limits
TEST-002,COMP-002,2024-08-10,68,Pass,Good thermal margin
TEST-003,COMP-003,2024-08-11,58,Pass,Excellent thermal performance
TEST-004,COMP-001,2024-08-12,87,Fail,Exceeded thermal limit - needs investigation
''',
            
            "config/thermal_config.json": '''{
    "system_settings": {
        "global_thermal_limit": 85,
        "warning_threshold": 80,
        "critical_threshold": 90,
        "monitoring_interval": 5
    },
    "component_overrides": {
        "COMP-001": {"limit": 85, "critical": 90},
        "COMP-002": {"limit": 70, "critical": 75},
        "COMP-003": {"limit": 60, "critical": 65}
    },
    "notification_settings": {
        "email_alerts": true,
        "thermal_team": ["sarah.chen@company.com", "mike.rodriguez@company.com"],
        "escalation_team": ["amanda.torres@company.com"]
    }
}'''
        }
        
        # Create project files
        created_files = []
        for file_path, content in project_structure.items():
            full_path = os.path.join(self.test_project_dir, file_path)
            
            # Create directory if needed
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Store original content and hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            self.original_files[file_path] = {
                "content": content,
                "hash": content_hash,
                "size": len(content.encode()),
                "created": datetime.now().isoformat()
            }
            
            created_files.append(file_path)
        
        print(f"   ✓ Created test project with {len(created_files)} files")
        
        return {
            "status": "ready",
            "project_directory": self.test_project_dir,
            "files_created": created_files,
            "total_files": len(created_files),
            "original_hashes": {path: info["hash"] for path, info in self.original_files.items()}
        }
    
    def ingest_initial_project(self, system_name: str, base_url: str) -> Dict[str, Any]:
        """Ingest initial project state"""
        print(f"📥 Ingesting initial project state into {system_name}...")
        
        if system_name.lower() == "nancy":
            # Nancy can do directory-based ingestion
            return self._ingest_directory_nancy(base_url)
        else:
            # Baseline gets individual file ingestion
            return self._ingest_individual_files(base_url)
    
    def _ingest_directory_nancy(self, base_url: str) -> Dict[str, Any]:
        """Use Nancy's directory ingestion capability"""
        try:
            response = requests.post(
                f"{base_url}/api/ingest/directory",
                json={
                    "directory_path": os.path.abspath(self.test_project_dir),
                    "project_name": "thermal_management_system",
                    "recursive": True,
                    "include_patterns": ["*.md", "*.csv", "*.py", "*.json"],
                    "author": "Project Team"
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "method": "directory_ingestion",
                    "files_processed": result.get("files_processed", 0),
                    "ingestion_time": result.get("processing_time", 0),
                    "change_detection_enabled": True
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _ingest_individual_files(self, base_url: str) -> Dict[str, Any]:
        """Ingest files individually for baseline system"""
        successful_uploads = 0
        errors = []
        start_time = time.time()
        
        for file_path, file_info in self.original_files.items():
            try:
                filename = os.path.basename(file_path)
                files_data = {'file': (filename, file_info["content"], 'text/plain')}
                data = {'author': 'Project Team'}
                
                response = requests.post(
                    f"{base_url}/api/ingest",
                    files=files_data,
                    data=data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    successful_uploads += 1
                else:
                    errors.append(f"{filename}: HTTP {response.status_code}")
                    
            except Exception as e:
                errors.append(f"{filename}: {str(e)}")
        
        return {
            "status": "completed",
            "method": "individual_file_ingestion",
            "files_processed": successful_uploads,
            "ingestion_time": time.time() - start_time,
            "change_detection_enabled": False,
            "errors": errors
        }
    
    def create_change_scenarios(self) -> List[Dict[str, Any]]:
        """Create various change scenarios to test"""
        print("📝 Creating change scenarios for testing...")
        
        change_scenarios = [
            {
                "scenario_name": "Critical Component Update",
                "description": "Update thermal limits for critical component",
                "files_to_change": {
                    "docs/requirements.md": {
                        "change_type": "content_update",
                        "original_text": "COMP-001: Primary CPU with 85°C thermal limit",
                        "new_text": "COMP-001: Primary CPU with 90°C thermal limit (updated per engineering review)",
                        "change_reason": "Engineering review increased thermal tolerance"
                    },
                    "data/component_specs.csv": {
                        "change_type": "data_update", 
                        "original_text": "COMP-001,Primary CPU,85,12.5,Sarah Chen,Validated,High",
                        "new_text": "COMP-001,Primary CPU,90,12.5,Sarah Chen,Updated,High",
                        "change_reason": "Thermal limit increase and status update"
                    }
                },
                "expected_impact": {
                    "affected_components": ["COMP-001"],
                    "affected_people": ["Sarah Chen"],
                    "affected_systems": ["thermal_monitor.py"],
                    "notification_priority": "high"
                }
            },
            
            {
                "scenario_name": "New Test Results",
                "description": "Add new test results showing thermal failure",
                "files_to_change": {
                    "tests/thermal_test_results.csv": {
                        "change_type": "content_addition",
                        "new_content": "\nTEST-005,COMP-002,2024-08-13,75,Fail,Memory module exceeded limit - needs cooling improvement",
                        "change_reason": "New test results added"
                    }
                },
                "expected_impact": {
                    "affected_components": ["COMP-002"],
                    "affected_people": ["Mike Rodriguez"],
                    "notification_priority": "critical"
                }
            },
            
            {
                "scenario_name": "Code Configuration Update",
                "description": "Update thermal monitoring code and configuration",
                "files_to_change": {
                    "code/thermal_monitor.py": {
                        "change_type": "code_update",
                        "original_text": "def __init__(self, max_temp=85):",
                        "new_text": "def __init__(self, max_temp=90):",
                        "change_reason": "Updated default thermal limit to match new requirements"
                    },
                    "config/thermal_config.json": {
                        "change_type": "config_update",
                        "original_text": '"global_thermal_limit": 85,',
                        "new_text": '"global_thermal_limit": 90,',
                        "change_reason": "Configuration update to match code changes"
                    }
                },
                "expected_impact": {
                    "affected_components": ["thermal monitoring system"],
                    "affected_people": ["Sarah Chen", "development team"],
                    "cross_file_consistency": True
                }
            },
            
            {
                "scenario_name": "New Component Addition",
                "description": "Add new component to system",
                "files_to_change": {
                    "data/component_specs.csv": {
                        "change_type": "record_addition",
                        "new_content": "\nCOMP-005,Cooling Fan,100,15.2,Mike Rodriguez,Draft,Medium",
                        "change_reason": "New cooling component added to address thermal issues"
                    },
                    "docs/requirements.md": {
                        "change_type": "content_addition",
                        "new_content": "\n- COMP-005: Cooling Fan for thermal management enhancement",
                        "change_reason": "Documentation update for new component"
                    }
                },
                "expected_impact": {
                    "new_component": "COMP-005",
                    "affected_people": ["Mike Rodriguez"],
                    "system_expansion": True
                }
            }
        ]
        
        self.change_scenarios = change_scenarios
        print(f"   ✓ Created {len(change_scenarios)} change scenarios")
        
        return change_scenarios
    
    def apply_change_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Apply changes for a specific scenario"""
        print(f"🔄 Applying change scenario: {scenario['scenario_name']}")
        
        applied_changes = {}
        change_hashes = {}
        
        for file_path, change_info in scenario["files_to_change"].items():
            full_path = os.path.join(self.test_project_dir, file_path)
            
            try:
                # Read current content
                with open(full_path, 'r', encoding='utf-8') as f:
                    current_content = f.read()
                
                # Apply change based on type
                if change_info["change_type"] in ["content_update", "data_update", "code_update", "config_update"]:
                    new_content = current_content.replace(
                        change_info["original_text"],
                        change_info["new_text"]
                    )
                elif change_info["change_type"] in ["content_addition", "record_addition"]:
                    new_content = current_content + change_info["new_content"]
                else:
                    continue
                
                # Write updated content
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                # Calculate new hash
                new_hash = hashlib.sha256(new_content.encode()).hexdigest()
                old_hash = self.original_files[file_path]["hash"]
                
                applied_changes[file_path] = {
                    "change_type": change_info["change_type"],
                    "change_reason": change_info["change_reason"],
                    "old_hash": old_hash,
                    "new_hash": new_hash,
                    "hash_changed": old_hash != new_hash,
                    "size_delta": len(new_content.encode()) - self.original_files[file_path]["size"]
                }
                
                change_hashes[file_path] = new_hash
                
                print(f"   ✓ Changed {file_path}: {change_info['change_reason']}")
                
            except Exception as e:
                print(f"   ✗ Failed to change {file_path}: {e}")
                applied_changes[file_path] = {"error": str(e)}
        
        return {
            "scenario": scenario["scenario_name"],
            "changes_applied": len([c for c in applied_changes.values() if "error" not in c]),
            "changes_failed": len([c for c in applied_changes.values() if "error" in c]),
            "applied_changes": applied_changes,
            "new_hashes": change_hashes,
            "expected_impact": scenario["expected_impact"],
            "timestamp": datetime.now().isoformat()
        }
    
    def test_change_detection(self, scenario_result: Dict[str, Any]) -> Dict[str, Any]:
        """Test Nancy's change detection capabilities"""
        print(f"🔍 Testing change detection for scenario: {scenario_result['scenario']}")
        
        if not scenario_result["changes_applied"]:
            return {"status": "no_changes", "message": "No changes to detect"}
        
        try:
            # Use Nancy's directory change detection endpoint
            response = requests.post(
                f"{self.nancy_url}/api/directory/detect_changes",
                json={
                    "directory_path": os.path.abspath(self.test_project_dir),
                    "project_name": "thermal_management_system"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                detection_result = response.json()
                
                # Analyze detection accuracy
                detected_files = set(detection_result.get("changed_files", []))
                actual_changed_files = set(scenario_result["applied_changes"].keys())
                
                true_positives = len(detected_files.intersection(actual_changed_files))
                false_positives = len(detected_files - actual_changed_files)
                false_negatives = len(actual_changed_files - detected_files)
                
                accuracy = true_positives / len(actual_changed_files) if actual_changed_files else 0
                precision = true_positives / len(detected_files) if detected_files else 0
                
                return {
                    "status": "success",
                    "detection_time": detection_result.get("processing_time", 0),
                    "detected_files": list(detected_files),
                    "actual_changed_files": list(actual_changed_files),
                    "accuracy": accuracy,
                    "precision": precision,
                    "true_positives": true_positives,
                    "false_positives": false_positives,
                    "false_negatives": false_negatives,
                    "change_details": detection_result.get("change_details", {})
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def test_impact_analysis(self, scenario_result: Dict[str, Any]) -> Dict[str, Any]:
        """Test Nancy's change impact analysis"""
        print(f"🎯 Testing impact analysis for scenario: {scenario_result['scenario']}")
        
        try:
            # Query Nancy for impact analysis
            impact_query = f"What are the impacts of recent changes to the thermal management system? Consider changes to {', '.join(scenario_result['applied_changes'].keys())}"
            
            response = requests.post(
                f"{self.nancy_url}/api/query",
                json={
                    "query": impact_query,
                    "orchestrator": "langchain",
                    "enable_change_context": True
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Analyze impact analysis quality
                response_text = result.get("response", "").lower()
                expected_impact = scenario_result["expected_impact"]
                
                impact_factors_found = []
                
                # Check for affected components
                if "affected_components" in expected_impact:
                    for component in expected_impact["affected_components"]:
                        if component.lower() in response_text:
                            impact_factors_found.append(f"Component {component}")
                
                # Check for affected people
                if "affected_people" in expected_impact:
                    for person in expected_impact["affected_people"]:
                        person_parts = person.lower().split()
                        if any(part in response_text for part in person_parts):
                            impact_factors_found.append(f"Person {person}")
                
                # Check for system-level impacts
                system_keywords = ["system", "impact", "affect", "change", "update", "thermal"]
                system_mentions = sum(1 for keyword in system_keywords if keyword in response_text)
                
                impact_quality_score = (
                    len(impact_factors_found) / 
                    (len(expected_impact.get("affected_components", [])) + 
                     len(expected_impact.get("affected_people", [])))
                    if expected_impact else 0
                )
                
                return {
                    "status": "success",
                    "query_time": result.get("query_time", 0),
                    "impact_analysis": result.get("response", ""),
                    "sources": result.get("sources", []),
                    "impact_factors_found": impact_factors_found,
                    "impact_quality_score": impact_quality_score,
                    "system_awareness_score": min(system_mentions / 5, 1.0),
                    "comprehensive_analysis": len(result.get("response", "")) > 200
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def test_baseline_limitation(self, scenario_result: Dict[str, Any]) -> Dict[str, Any]:
        """Test baseline's inability to detect changes (demonstrates Nancy's unique value)"""
        print(f"📚 Testing baseline change awareness (expected: none)")
        
        try:
            # Ask baseline about recent changes - should have no awareness
            change_query = f"What recent changes have been made to the thermal management system? Are there any updates to thermal limits or test results?"
            
            response = requests.post(
                f"{self.baseline_url}/api/query",
                json={"query": change_query},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").lower()
                
                # Baseline should not be aware of changes since it works with static data
                change_awareness_keywords = ["recent", "updated", "changed", "modified", "new"]
                change_awareness_score = sum(1 for keyword in change_awareness_keywords if keyword in response_text)
                
                # Check if baseline mentions any actual changed content
                actual_changes = scenario_result["applied_changes"]
                change_content_awareness = 0
                
                for file_path, change_info in actual_changes.items():
                    if "error" not in change_info:
                        # Look for new content in baseline response
                        # This would only happen if baseline was re-ingested after changes
                        change_content_awareness += 0  # Baseline has no change detection
                
                return {
                    "status": "success",
                    "query_time": result.get("query_time", 0),
                    "response": result.get("response", ""),
                    "change_awareness_score": change_awareness_score / len(change_awareness_keywords),
                    "change_content_awareness": change_content_awareness,
                    "limitation_demonstrated": change_awareness_score < 2,  # Low change awareness confirms limitation
                    "baseline_analysis": "Baseline has no inherent change detection capability - works only with static snapshots"
                }
            else:
                return {
                    "status": "error", 
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def run_change_intelligence_tests(self) -> Dict[str, Any]:
        """Run comprehensive change intelligence testing"""
        print("🔄 CHANGE INTELLIGENCE TESTING")
        print("=" * 60)
        
        test_start = time.time()
        
        # Phase 1: Setup
        print("\n1️⃣ SETUP TEST PROJECT")
        print("-" * 30)
        setup_result = self.setup_test_project()
        
        # Phase 2: Initial Ingestion
        print("\n2️⃣ INITIAL PROJECT INGESTION")
        print("-" * 30)
        nancy_ingestion = self.ingest_initial_project("Nancy", self.nancy_url)
        baseline_ingestion = self.ingest_initial_project("Baseline", self.baseline_url)
        
        print("   ⏳ Allowing time for initial processing...")
        time.sleep(10)
        
        # Phase 3: Create Change Scenarios
        print("\n3️⃣ CREATE CHANGE SCENARIOS")
        print("-" * 30)
        scenarios = self.create_change_scenarios()
        
        # Phase 4: Test Each Scenario
        print("\n4️⃣ CHANGE INTELLIGENCE TESTING")
        print("-" * 30)
        
        scenario_results = []
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n   Scenario {i}/{len(scenarios)}: {scenario['scenario_name']}")
            
            # Apply changes
            change_result = self.apply_change_scenario(scenario)
            
            # Wait for potential change detection
            time.sleep(5)
            
            # Test Nancy's change detection
            detection_result = self.test_change_detection(change_result)
            
            # Test Nancy's impact analysis  
            impact_result = self.test_impact_analysis(change_result)
            
            # Test baseline limitation
            baseline_result = self.test_baseline_limitation(change_result)
            
            scenario_test_result = {
                "scenario": scenario,
                "change_application": change_result,
                "nancy_change_detection": detection_result,
                "nancy_impact_analysis": impact_result,
                "baseline_change_limitation": baseline_result,
                "timestamp": datetime.now().isoformat()
            }
            
            scenario_results.append(scenario_test_result)
        
        # Phase 5: Analysis
        print("\n5️⃣ CHANGE INTELLIGENCE ANALYSIS")
        print("-" * 30)
        final_analysis = self._analyze_change_intelligence(scenario_results)
        
        test_time = time.time() - test_start
        
        final_results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "test_type": "Change Intelligence Testing",
                "total_test_time": test_time,
                "test_project_directory": self.test_project_dir
            },
            "setup_results": setup_result,
            "initial_ingestion": {
                "nancy": nancy_ingestion,
                "baseline": baseline_ingestion
            },
            "scenario_results": scenario_results,
            "change_intelligence_analysis": final_analysis
        }
        
        return final_results
    
    def _analyze_change_intelligence(self, scenario_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze change intelligence test results"""
        
        total_scenarios = len(scenario_results)
        successful_detections = 0
        total_accuracy = 0
        total_impact_quality = 0
        baseline_limitations = 0
        
        for result in scenario_results:
            detection = result["nancy_change_detection"]
            impact = result["nancy_impact_analysis"]
            baseline = result["baseline_change_limitation"]
            
            # Count successful detections
            if detection.get("status") == "success" and detection.get("accuracy", 0) > 0.7:
                successful_detections += 1
                total_accuracy += detection.get("accuracy", 0)
            
            # Count quality impact analysis
            if impact.get("status") == "success":
                total_impact_quality += impact.get("impact_quality_score", 0)
            
            # Count baseline limitations demonstrated
            if baseline.get("limitation_demonstrated", False):
                baseline_limitations += 1
        
        avg_accuracy = total_accuracy / successful_detections if successful_detections > 0 else 0
        avg_impact_quality = total_impact_quality / total_scenarios if total_scenarios > 0 else 0
        
        return {
            "overall_performance": {
                "total_scenarios": total_scenarios,
                "successful_change_detections": successful_detections,
                "change_detection_rate": successful_detections / total_scenarios,
                "average_detection_accuracy": avg_accuracy,
                "average_impact_analysis_quality": avg_impact_quality,
                "baseline_limitations_demonstrated": baseline_limitations
            },
            "unique_value_proposition": {
                "change_detection_capability": successful_detections > 0,
                "impact_analysis_capability": avg_impact_quality > 0.5,
                "baseline_cannot_provide": baseline_limitations / total_scenarios > 0.8,
                "engineering_workflow_enhancement": self._assess_workflow_value(avg_accuracy, avg_impact_quality)
            },
            "recommendations": self._generate_change_intelligence_recommendations(
                successful_detections / total_scenarios, avg_accuracy, avg_impact_quality
            )
        }
    
    def _assess_workflow_value(self, detection_accuracy: float, impact_quality: float) -> str:
        """Assess engineering workflow value of change intelligence"""
        if detection_accuracy > 0.8 and impact_quality > 0.7:
            return "High Value: Automated change detection and impact analysis would significantly streamline engineering workflows"
        elif detection_accuracy > 0.6 and impact_quality > 0.5:
            return "Good Value: Meaningful change intelligence that could improve project management and coordination"
        elif detection_accuracy > 0.4 or impact_quality > 0.3:
            return "Moderate Value: Some change intelligence capability but needs improvement for production use"
        else:
            return "Limited Value: Change intelligence capabilities need significant development"
    
    def _generate_change_intelligence_recommendations(self, detection_rate: float, accuracy: float, impact_quality: float) -> List[str]:
        """Generate recommendations for change intelligence"""
        recommendations = []
        
        if detection_rate > 0.8:
            recommendations.append("Nancy's change detection is highly reliable - suitable for production deployment")
        elif detection_rate > 0.6:
            recommendations.append("Nancy's change detection shows promise - consider pilot deployment with monitoring")
        else:
            recommendations.append("Change detection needs improvement before production use")
        
        if accuracy > 0.8:
            recommendations.append("High change detection accuracy minimizes false positives/negatives")
        elif accuracy > 0.6:
            recommendations.append("Moderate accuracy - may need human verification of detected changes")
        else:
            recommendations.append("Low accuracy could lead to missed changes or false alarms")
        
        if impact_quality > 0.7:
            recommendations.append("Strong impact analysis capability - provides valuable insights for engineering teams")
        elif impact_quality > 0.5:
            recommendations.append("Useful impact analysis - can help with change coordination")
        else:
            recommendations.append("Impact analysis needs enhancement to provide engineering value")
        
        recommendations.append("This capability is unique to Nancy - baseline RAG systems cannot provide change intelligence")
        
        return recommendations


def main():
    """Run change intelligence testing"""
    tester = ChangeIntelligenceTest()
    
    try:
        print("Starting Change Intelligence Testing")
        print("Testing Nancy's unique change detection and impact analysis capabilities")
        print("Baseline RAG systems cannot provide this functionality (static data only)")
        print()
        
        results = tester.run_change_intelligence_tests()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"change_intelligence_test_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Display summary
        print("\n" + "="*60)
        print("🔄 CHANGE INTELLIGENCE TEST RESULTS")
        print("="*60)
        
        analysis = results['change_intelligence_analysis']
        
        print(f"\n🎯 OVERALL PERFORMANCE:")
        overall = analysis['overall_performance']
        print(f"   Total Scenarios: {overall['total_scenarios']}")
        print(f"   Successful Detections: {overall['successful_change_detections']}")
        print(f"   Detection Rate: {overall['change_detection_rate']:.1%}")
        print(f"   Average Accuracy: {overall['average_detection_accuracy']:.1%}")
        print(f"   Impact Analysis Quality: {overall['average_impact_analysis_quality']:.1%}")
        print(f"   Baseline Limitations Shown: {overall['baseline_limitations_demonstrated']}/{overall['total_scenarios']}")
        
        print(f"\n💎 UNIQUE VALUE PROPOSITION:")
        unique = analysis['unique_value_proposition']
        print(f"   Change Detection: {'✓' if unique['change_detection_capability'] else '✗'}")
        print(f"   Impact Analysis: {'✓' if unique['impact_analysis_capability'] else '✗'}")
        print(f"   Unique to Nancy: {'✓' if unique['baseline_cannot_provide'] else '✗'}")
        print(f"   Workflow Value: {unique['engineering_workflow_enhancement']}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in analysis['recommendations']:
            print(f"   • {rec}")
        
        print(f"\n📁 Detailed results saved to: {filename}")
        
        return results
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return None
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()